import requests
import base64
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class OwnerModel(BaseModel):
    login: str
    type: str


class LicenseModel(BaseModel):
    spdx_id: Optional[str] = None


class RepositoryModel(BaseModel):
    github_id: int = Field(alias="id")
    full_name: str
    subscribers_count: Optional[int] = None
    stargazers_count: int
    forks_count: int
    created_at: datetime
    pushed_at: Optional[datetime] = None
    topics: list[str] = []
    owner: OwnerModel
    license: Optional[LicenseModel] = None

    model_config = ConfigDict(extra="ignore")


def decode_readme(content: str):
    decoded = base64.b64decode(content)
    return decoded.decode("utf-8", errors="replace")


class GitHubAPI:
    def __init__(self, token: str):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Research/1.0",
            "Authorization": f"Bearer {token}",
        }

    def _get_count_from_link(self, url, params=None):
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        link = response.headers.get("Link", "")

        if 'rel="last"' in link:
            import re

            match = re.search(r'page=(\d+)>; rel="last"', link)
            if match:
                return int(match.group(1))

        return len(response.json())

    def search_repo(self, query: str, page: int, per_page: int):
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "page": page, "per_page": per_page}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [RepositoryModel.model_validate(repo) for repo in data["items"]]

    def get_repo(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return RepositoryModel.model_validate(response.json())

    def get_readme(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        content = data.get("content", "")
        return decode_readme(content)

    def get_releases_count(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        return self._get_count_from_link(url, {"per_page": 1})

    def get_contributors_count(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        return self._get_count_from_link(url, {"per_page": 1, "anon": "true"})

    def get_languages(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        total = sum(data.values())
        if total == 0:
            return {}

        return {
            language: round(bytes_count / total * 100, 2)
            for language, bytes_count in data.items()
        }

    def get_issues_count(self, owner: str, repo: str, is_closed: bool):
        state = "closed" if is_closed else "open"

        url = f"{self.base_url}/search/issues"
        params = {"q": f"repo:{owner}/{repo} type:issue state:{state}"}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()["total_count"]

    def get_pr_count(self, owner: str, repo: str, is_closed: bool):
        state = "closed" if is_closed else "open"

        url = f"{self.base_url}/search/issues"
        params = {"q": f"repo:{owner}/{repo} type:pr state:{state}"}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()["total_count"]

    def get_commits_count(self, owner: str, repo: str):
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        return self._get_count_from_link(url, {"per_page": 1})

    def get_owner_location(self, owner: OwnerModel):
        if owner.type == "User":
            url = f"{self.base_url}/users/{owner.login}"
        elif owner.type == "Organization":
            url = f"{self.base_url}/orgs/{owner.login}"
        else:
            return None

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("location")
