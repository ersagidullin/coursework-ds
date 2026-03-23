from database import Database
from crud import RepoCRUD
from api import GitHubAPI
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


class GitHubETL:
    def __init__(self, token: str, database_url: str):
        self.db = Database(database_url)
        self.api = GitHubAPI(token)
        self.session = None
        self.repo_crud = None

    def main(self):
        self.db.create_tables()
        self.session = self.db.get_session()
        self.repo_crud = RepoCRUD(self.session)

        owner = "psf"
        repo = "requests"

        repo_model = self.api.get_repo(owner, repo)
        readme = self.api.get_readme(owner, repo)
        releases_count = self.api.get_releases_count(owner, repo)
        contributors_count = self.api.get_contributors_count(owner, repo)
        languages_map = self.api.get_languages(owner, repo)

        open_issues_count = self.api.get_issues_count(owner, repo, is_closed=False)
        closed_issues_count = self.api.get_issues_count(owner, repo, is_closed=True)

        open_pr_count = self.api.get_pr_count(owner, repo, is_closed=False)
        closed_pr_count = self.api.get_pr_count(owner, repo, is_closed=True)

        commits_count = self.api.get_commits_count(owner, repo)
        owner_location = self.api.get_owner_location(repo_model.owner)

        repo_data = {
            "github_id": repo_model.github_id,
            "readme": readme,
            "releases_count": releases_count,
            "subscribers_count": repo_model.stargazers_count,
            "stargazers_count": repo_model.stargazers_count,
            "forks_count": repo_model.forks_count,
            "created_at": repo_model.created_at,
            "license_spdx_id": None,
            "topics": repo_model.topics,
            "pushed_at": repo_model.pushed_at,
            "languages_map": languages_map,
            "open_issues_count": open_issues_count,
            "closed_issues_count": closed_issues_count,
            "open_pr_count": open_pr_count,
            "closed_pr_count": closed_pr_count,
            "full_name": repo_model.full_name,
            "contributors_count": contributors_count,
            "commits_count": commits_count,
            "owner_location": owner_location,
        }

        self.repo_crud.insert_repo(repo_data)
        self.session.close()


if __name__ == "__main__":
    etl = GitHubETL(token=GITHUB_TOKEN, database_url=DATABASE_URL)
    etl.main()
