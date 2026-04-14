import requests
import base64
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
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
    topics: list[str] = Field(default_factory=list)
    owner: OwnerModel
    license: Optional[LicenseModel] = None
    description: Optional[str] = None
    size: int = 0

    model_config = ConfigDict(extra="ignore")


class RecentCommitModel(BaseModel):
    sha: str
    author: Optional[str] = None
    date: datetime
    message: str
    is_merge: bool


class CommitStatsModel(BaseModel):
    total_count: int = 0
    last_commit_at: Optional[datetime] = None
    commits_30d: int = 0
    commits_90d: int = 0
    unique_authors_recent: int = 0
    merge_commits_recent: int = 0


class RepositorySnapshot(BaseModel):
    github_id: int
    full_name: str
    readme: Optional[str] = None
    releases_count: int = 0
    subscribers_count: int = 0
    stargazers_count: int = 0
    forks_count: int = 0
    created_at: datetime
    license_spdx_id: Optional[str] = None
    topics: list[str] = Field(default_factory=list)
    pushed_at: Optional[datetime] = None
    languages_map: dict[str, float] = Field(default_factory=dict)
    open_issues_count: int = 0
    closed_issues_count: int = 0
    open_pr_count: int = 0
    closed_pr_count: int = 0
    contributors_count: int = 0
    owner_location: Optional[str] = None
    description: Optional[str] = None
    owner_type: str
    size: int = 0
    has_github_actions: bool = False
    recent_commits: list[dict[str, Any]] = Field(default_factory=list)
    commit_stats: dict[str, Any] = Field(default_factory=dict)


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

    def has_github_actions(self, owner: str, repo: str) -> bool:
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return data.get("total_count", 0) > 0

    def get_recent_commits(self, owner: str, repo: str, limit: int = 30):
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        response = requests.get(url, headers=self.headers, params={"per_page": limit})
        response.raise_for_status()

        data = response.json()
        recent_commits = []

        unique_authors = set()
        merge_commits_recent = 0
        commits_30d = 0
        commits_90d = 0
        last_commit_at = None

        now = datetime.utcnow()

        for idx, item in enumerate(data):
            commit_data = item.get("commit", {})
            author_data = item.get("author")
            commit_author_data = commit_data.get("author", {})

            sha = item.get("sha", "")
            message_full = commit_data.get("message", "") or ""
            message = message_full.splitlines()[0][:500]
            author = (
                author_data.get("login")
                if isinstance(author_data, dict)
                else commit_author_data.get("name")
            )

            date_str = commit_author_data.get("date")
            if not date_str:
                continue

            commit_date = datetime.fromisoformat(
                date_str.replace("Z", "+00:00")
            ).replace(tzinfo=None)
            is_merge = message.startswith("Merge ") or message.startswith("Merged ")

            if idx == 0:
                last_commit_at = commit_date

            if author:
                unique_authors.add(author)

            if is_merge:
                merge_commits_recent += 1

            delta_days = (now - commit_date).days
            if delta_days <= 30:
                commits_30d += 1
            if delta_days <= 90:
                commits_90d += 1

            recent_commits.append(
                {
                    "sha": sha[:7],
                    "author": author,
                    "date": commit_date.isoformat(),
                    "message": message,
                    "is_merge": is_merge,
                }
            )

        commit_stats = {
            "total_count": self.get_commits_count(owner, repo),
            "last_commit_at": last_commit_at.isoformat() if last_commit_at else None,
            "commits_30d": commits_30d,
            "commits_90d": commits_90d,
            "unique_authors_recent": len(unique_authors),
            "merge_commits_recent": merge_commits_recent,
        }

        return recent_commits, commit_stats
