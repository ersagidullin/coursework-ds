from database import Database
from repository_service import RepositoryService
from api import GitHubAPI
from models import Repository
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


class GitHubETL:
    def __init__(self, token: str, database_url: str):
        self.db = Database(database_url)
        self.api = GitHubAPI(token)

    def load_repository(self, owner: str, repo: str) -> None:
        self.db.create_tables()
        session = self.db.get_session()

        try:
            repo_service = RepositoryService(session)
            snapshot = self.api.get_repository_snapshot(owner, repo)
            repository = Repository.from_snapshot(snapshot)
            repo_service.insert_repo(repository)
        finally:
            session.close()


if __name__ == "__main__":
    etl = GitHubETL(token=GITHUB_TOKEN, database_url=DATABASE_URL)
    etl.load_repository("ersagidullin", "coursework-ds")
