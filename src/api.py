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

class RecentPullRequestModel(BaseModel):
    number: int
    title: str
    author: Optional[str] = None
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    is_draft: bool = False
    is_merged: bool = False


class PullRequestStatsModel(BaseModel):
    total_count: int = 0
    open_count: int = 0
    closed_count: int = 0
    merged_count: int = 0
    last_pr_at: Optional[datetime] = None
    prs_30d: int = 0
    prs_90d: int = 0
    unique_requestors_recent: int = 0
    merged_recent: int = 0
    draft_recent: int = 0

class RecentIssueModel(BaseModel):
    number: int
    title: str
    author: Optional[str] = None
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    comments: int = 0
    labels: list[str] = Field(default_factory=list)
    is_pull_request: bool = False


class IssueStatsModel(BaseModel):
    total_count: int = 0
    open_count: int = 0
    closed_count: int = 0
    last_issue_at: Optional[datetime] = None
    issues_30d: int = 0
    issues_90d: int = 0
    unique_authors_recent: int = 0
    closed_recent: int = 0

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
    contributors_count: int = 0
    owner_location: Optional[str] = None
    description: Optional[str] = None
    owner_type: str
    size: int = 0
    has_github_actions: bool = False
    recent_commits: list[dict[str, Any]] = Field(default_factory=list)
    commit_stats: dict[str, Any] = Field(default_factory=dict)
    root_contents: list[dict] = Field(default_factory=list)
    pull_request_stats: dict[str, Any] = Field(default_factory=dict)
    recent_pull_requests: list[dict[str, Any]] = Field(default_factory=list)
    issue_stats: dict[str, Any] = Field(default_factory=dict)
    recent_issues: list[dict[str, Any]] = Field(default_factory=list)


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

    def get_issue_count(self, owner: str, repo: str, state: str = "all") -> int:
        url = f"{self.base_url}/search/issues"
        query = f"repo:{owner}/{repo} type:issue"

        if state in {"open", "closed"}:
            query += f" state:{state}"

        params = {"q": query}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["total_count"]


    def get_recent_issues(self, owner: str, repo: str, limit: int = 30):
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": limit,
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()

        recent_issues = []
        unique_authors = set()
        closed_recent = 0
        issues_30d = 0
        issues_90d = 0
        last_issue_at = None

        now = datetime.utcnow()

        for idx, item in enumerate(data):
            if "pull_request" in item:
                continue

            user_data = item.get("user") or {}
            author = user_data.get("login")

            created_at_str = item.get("created_at")
            updated_at_str = item.get("updated_at")
            closed_at_str = item.get("closed_at")

            if not created_at_str or not updated_at_str:
                continue

            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            closed_at = (
                datetime.fromisoformat(closed_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
                if closed_at_str else None
            )

            if last_issue_at is None:
                last_issue_at = updated_at

            if author:
                unique_authors.add(author)

            if item.get("state") == "closed":
                closed_recent += 1

            delta_days = (now - created_at).days
            if delta_days <= 30:
                issues_30d += 1
            if delta_days <= 90:
                issues_90d += 1

            labels = []
            for label in item.get("labels", []):
                if isinstance(label, dict):
                    name = label.get("name")
                    if name:
                        labels.append(name)

            recent_issues.append(
                {
                    "number": item.get("number"),
                    "title": (item.get("title") or "")[:500],
                    "author": author,
                    "state": item.get("state"),
                    "created_at": created_at.isoformat(),
                    "updated_at": updated_at.isoformat(),
                    "closed_at": closed_at.isoformat() if closed_at else None,
                    "comments": item.get("comments", 0),
                    "labels": labels,
                    "is_pull_request": "pull_request" in item,
                }
            )

            if len(recent_issues) >= limit:
                break

        issue_stats = {
            "total_count": self.get_issue_count(owner, repo, state="all"),
            "open_count": self.get_issue_count(owner, repo, state="open"),
            "closed_count": self.get_issue_count(owner, repo, state="closed"),
            "last_issue_at": last_issue_at.isoformat() if last_issue_at else None,
            "issues_30d": issues_30d,
            "issues_90d": issues_90d,
            "unique_authors_recent": len(unique_authors),
            "closed_recent": closed_recent,
        }

        return recent_issues, issue_stats

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

    def get_root_contents(self, owner: str, repo: str) -> list[dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            return []

        response.raise_for_status()
        data = response.json()

        result = []

        for item in data:
            result.append({
                "name": item.get("name"),
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size", 0)
            })

        return result
    
    def get_pull_request_count(self, owner: str, repo: str, state: str = "all") -> int:
        url = f"{self.base_url}/search/issues"
        query = f"repo:{owner}/{repo} type:pr"

        if state in {"open", "closed"}:
            query += f" state:{state}"

        params = {"q": query}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["total_count"]


    def get_merged_pull_request_count(self, owner: str, repo: str) -> int:
        url = f"{self.base_url}/search/issues"
        params = {"q": f"repo:{owner}/{repo} type:pr is:merged"}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["total_count"]


    def get_recent_pull_requests(self, owner: str, repo: str, limit: int = 30):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": limit,
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()

        recent_pull_requests = []
        unique_requestors = set()
        merged_recent = 0
        draft_recent = 0
        prs_30d = 0
        prs_90d = 0
        last_pr_at = None

        now = datetime.utcnow()

        for idx, item in enumerate(data):
            author_data = item.get("user") or {}
            author = author_data.get("login")

            created_at_str = item.get("created_at")
            updated_at_str = item.get("updated_at")
            closed_at_str = item.get("closed_at")
            merged_at_str = item.get("merged_at")

            if not created_at_str or not updated_at_str:
                continue

            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            closed_at = (
                datetime.fromisoformat(closed_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
                if closed_at_str else None
            )
            merged_at = (
                datetime.fromisoformat(merged_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
                if merged_at_str else None
            )

            if idx == 0:
                last_pr_at = updated_at

            if author:
                unique_requestors.add(author)

            is_draft = item.get("draft", False)
            is_merged = merged_at is not None

            if is_merged:
                merged_recent += 1

            if is_draft:
                draft_recent += 1

            delta_days = (now - created_at).days
            if delta_days <= 30:
                prs_30d += 1
            if delta_days <= 90:
                prs_90d += 1

            recent_pull_requests.append(
                {
                    "number": item.get("number"),
                    "title": (item.get("title") or "")[:500],
                    "author": author,
                    "state": item.get("state"),
                    "created_at": created_at.isoformat(),
                    "updated_at": updated_at.isoformat(),
                    "closed_at": closed_at.isoformat() if closed_at else None,
                    "merged_at": merged_at.isoformat() if merged_at else None,
                    "is_draft": is_draft,
                    "is_merged": is_merged,
                }
            )

        pr_stats = {
            "total_count": self.get_pull_request_count(owner, repo, state="all"),
            "open_count": self.get_pull_request_count(owner, repo, state="open"),
            "closed_count": self.get_pull_request_count(owner, repo, state="closed"),
            "merged_count": self.get_merged_pull_request_count(owner, repo),
            "last_pr_at": last_pr_at.isoformat() if last_pr_at else None,
            "prs_30d": prs_30d,
            "prs_90d": prs_90d,
            "unique_requestors_recent": len(unique_requestors),
            "merged_recent": merged_recent,
            "draft_recent": draft_recent,
        }

        return recent_pull_requests, pr_stats