import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Generator, List
from dataclasses import dataclass

from models import Repository
from api import GitHubAPI, RepositorySnapshot


@dataclass
class FetchProgress:
    current_date: datetime
    page: int
    fetched_in_interval: int
    total_fetched: int
    errors: int


class GitHubFetcher:
    def __init__(
        self,
        api: GitHubAPI,
        delay: float = 4.0,
        batch_size: int = 100,
        batches_per_send: int = 10,
    ):
        self.api = api
        self.delay = delay
        self.batch_size = batch_size
        self.batches_per_send = batches_per_send
        self.stats = {
            "fetched": 0,
            "errors": 0,
            "requests": 0,
            "batches": 0,
            "big_batches": 0,
        }

        self._progress = None

    def _flush_buffer(
        self,
        buffer: List[List[Repository]],
        current_batch: List[Repository],
        current_date: datetime,
        page: int,
        total_in_interval: int,
    ) -> Generator[Tuple[List[Repository], FetchProgress], None, None]:

        if current_batch:
            buffer.append(current_batch)

        if not buffer:
            return

        big_batch = []
        for batch in buffer:
            big_batch.extend(batch)

        self.stats["big_batches"] += 1
        progress = FetchProgress(
            current_date=current_date,
            page=page,
            fetched_in_interval=total_in_interval,
            total_fetched=self.stats["fetched"],
            errors=self.stats["errors"],
        )

        yield big_batch, progress

    def fetch_repositories(
        self,
        start_date: datetime,
        end_date: datetime,
        min_stars: int = 1000,
        max_repos_per_day: Optional[int] = None,
        resume_from: Optional[FetchProgress] = None,
    ) -> Generator[Tuple[List[Repository], FetchProgress], None, None]:

        if resume_from:
            current_date = resume_from.current_date
            page = resume_from.page
            print(f" Возобновляем с {current_date.date()}, страница {page}")
        else:
            current_date = start_date
            page = 1

        buffer = []
        current_batch = []
        total_in_interval = 0

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            query = f"created:{date_str} stars:>{min_stars}"

            try:
                repos_data = self.api.search_repo(query, page, per_page=100)
                self.stats["requests"] += 1
                print(f"Получено {len(repos_data)} репозиториев")

                if not repos_data:
                    print(f"Нет данных, переходим к следующему дню")

                    for result in self._flush_buffer(
                        buffer, current_batch, current_date, page, total_in_interval
                    ):
                        yield result
                    buffer = []
                    current_batch = []

                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0
                    continue

                for repo_model in repos_data:
                    try:
                        repo_obj = self._fetch_repo_full_data(repo_model.full_name)

                        if repo_obj:
                            current_batch.append(repo_obj)
                            total_in_interval += 1
                            self.stats["fetched"] += 1

                            if len(current_batch) >= self.batch_size:
                                self.stats["batches"] += 1
                                buffer.append(current_batch)
                                current_batch = []

                                if len(buffer) >= self.batches_per_send:
                                    for result in self._flush_buffer(
                                        buffer,
                                        current_batch,
                                        current_date,
                                        page,
                                        total_in_interval,
                                    ):
                                        yield result
                                    buffer = []
                                    current_batch = []

                    except Exception as e:
                        print(f" Ошибка обработки {repo_model.full_name}: {e}")
                        self.stats["errors"] += 1

                    time.sleep(self.delay)

                if len(repos_data) < 100:
                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0
                else:
                    page += 1

                if max_repos_per_day and total_in_interval >= max_repos_per_day:
                    print(
                        f"Достигнут лимит дня ({max_repos_per_day}), переходим к следующему"
                    )

                    for result in self._flush_buffer(
                        buffer, current_batch, current_date, page, total_in_interval
                    ):
                        yield result
                    buffer = []
                    current_batch = []

                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0

            except Exception as e:
                print(f"Ошибка для {date_str}: {e}")
                self.stats["errors"] += 1
                time.sleep(self.delay * 5)
                continue

        for result in self._flush_buffer(
            buffer, current_batch, current_date, page, total_in_interval
        ):
            yield result

    def _fetch_repo_full_data(self, full_name: str) -> Optional[Repository]:
        owner, name = full_name.split("/")

        try:
            repo_info = self.api.get_repo(owner, name)
            self.stats["requests"] += 1

            try:
                readme = self.api.get_readme(owner, name)
                self.stats["requests"] += 1
            except Exception:
                readme = None

            releases_count = self.api.get_releases_count(owner, name)
            self.stats["requests"] += 1

            contributors_count = self.api.get_contributors_count(owner, name)
            self.stats["requests"] += 1

            languages_map = self.api.get_languages(owner, name)
            self.stats["requests"] += 1

            open_issues_count = self.api.get_issues_count(owner, name, False)
            closed_issues_count = self.api.get_issues_count(owner, name, True)
            self.stats["requests"] += 2

            open_pr_count = self.api.get_pr_count(owner, name, False)
            closed_pr_count = self.api.get_pr_count(owner, name, True)
            self.stats["requests"] += 2

            commits_count = self.api.get_commits_count(owner, name)
            self.stats["requests"] += 1

            owner_location = self.api.get_owner_location(repo_info.owner)
            self.stats["requests"] += 1

            snapshot = RepositorySnapshot(
                github_id=repo_info.github_id,
                full_name=repo_info.full_name,
                readme=readme,
                releases_count=releases_count,
                subscribers_count=repo_info.subscribers_count or 0,
                stargazers_count=repo_info.stargazers_count,
                forks_count=repo_info.forks_count,
                created_at=repo_info.created_at,
                license_spdx_id=(
                    repo_info.license.spdx_id if repo_info.license else None
                ),
                topics=repo_info.topics or [],
                pushed_at=repo_info.pushed_at,
                languages_map=languages_map,
                open_issues_count=open_issues_count,
                closed_issues_count=closed_issues_count,
                open_pr_count=open_pr_count,
                closed_pr_count=closed_pr_count,
                contributors_count=contributors_count,
                commits_count=commits_count,
                owner_location=owner_location,
                description=repo_info.description,
                owner_type=repo_info.owner.type,
                size=repo_info.size,
            )

            return Repository.from_snapshot(snapshot)

        except Exception as e:
            print(f"Не удалось получить {full_name}: {e}")
            self.stats["errors"] += 1
            return None

    def get_stats(self) -> Dict[str, int]:
        return self.stats

    def reset_stats(self):
        self.stats = {"fetched": 0, "errors": 0, "requests": 0, "batches": 0}
