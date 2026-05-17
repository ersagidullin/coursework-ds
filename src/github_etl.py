from datetime import datetime
from typing import Optional

from database import Database
from repository_service import RepositoryService
from api import GitHubAPI
from models import Repository
from dotenv import load_dotenv
from fetcher import GitHubFetcher, FetchProgress
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


class GitHubETL:
    def __init__(
        self,
        token: str,
        database_url: str,
        delay: float = 4.0,
        batch_size: int = 100,
        batches_per_send: int = 10,
    ):
        self.db = Database(database_url)
        self.api = GitHubAPI(token)
        self.fetcher = GitHubFetcher(
            api=self.api,
            delay=delay,
            batch_size=batch_size,
            batches_per_send=batches_per_send,
        )

    def _save_batch(
        self,
        repo_service: RepositoryService,
        repos: list[Repository],
    ) -> int:
        if not repos:
            return 0

        try:
            repo_service.insert_many_repos(repos)
            return len(repos)

        except Exception as e:
            print(f"Ошибка массовой вставки батча ({len(repos)}): {e}")
            repo_service.session.rollback()

            saved_count = 0
            for repo in repos:
                try:
                    repo_service.insert_repo(repo)
                    saved_count += 1
                except Exception as repo_error:
                    print(f"Не удалось сохранить {repo.full_name}: {repo_error}")
                    repo_service.session.rollback()

            return saved_count

    def load_repositories(
        self,
        start_date: datetime,
        end_date: datetime,
        min_stars: int = 1000,
        max_repos_per_day: Optional[int] = None,
        resume_from: Optional[FetchProgress] = None,
    ) -> FetchProgress:
        self.db.create_tables()
        session = self.db.get_session()

        last_progress = resume_from or FetchProgress(
            current_date=start_date,
            page=1,
            fetched_in_interval=0,
            total_fetched=0,
            errors=0,
        )

        try:
            repo_service = RepositoryService(session)

            for repos_batch, progress in self.fetcher.fetch_repositories(
                start_date=start_date,
                end_date=end_date,
                min_stars=min_stars,
                max_repos_per_day=max_repos_per_day,
                resume_from=resume_from,
            ):
                saved_count = self._save_batch(repo_service, repos_batch)
                last_progress = progress

                print(
                    f"[ETL] Сохранено: {saved_count} | "
                    f"{progress.current_date.date()} | "
                    f"page={progress.page} | "
                    f"total={progress.total_fetched} | "
                    f"errors={progress.errors}"
                )

            print("[ETL] Загрузка завершена")
            print(f"[ETL] Статистика: {self.fetcher.get_stats()}")

            return last_progress

        finally:
            session.close()

    def get_stats(self) -> dict:
        return self.fetcher.get_stats()

    def reset_stats(self) -> None:
        self.fetcher.reset_stats()


if __name__ == "__main__":
    etl = GitHubETL(
        token=GITHUB_TOKEN,
        database_url=DATABASE_URL,
        delay=4.0,
        batch_size=5,
        batches_per_send=1,
    )

    etl.load_repositories(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        min_stars=1000,
        max_repos_per_day=500,
    )
