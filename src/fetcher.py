import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Generator, List
from dataclasses import dataclass

from api import GitHubAPI
from crud import RepoCRUD

@dataclass
class FetchProgress:
    current_date: datetime
    page: int
    fetched_in_interval: int
    total_fetched: int
    errors: int

class GitHubFetcher:
    def __init__(self, api: GitHubAPI, crud: Optional[RepoCRUD] = None, delay: float = 4.0, batch_size: int = 100):
        self.api = api
        self.crud = crud
        self.delay = delay
        self.batch_size = batch_size
        self.stats = {"fetched":0, "errors":0, "requests":0, "batches": 0}

        self._progress = None

    def fetch_repositories( self, start_date: datetime, end_date: datetime, min_stars: int = 1000, max_repos_per_day: Optional[int] = None, resume_from: Optional[FetchProgress] = None)-> Generator[List[Dict[str, Any]], FetchProgress, None]:
        if resume_from:
            current_date = resume_from.current_date
            page = resume_from.page
        else:
            current_date = start_date
            page = 1

        current_batch = []
        total_in_interval = 0

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            query = f"created:{date_str} stars:>{min_stars}"

            try:
                repos_data = self.api.search_repo(query, page, per_page=100)
                self.stats['requests'] += 1

                if not repos_data:
                    print(f"День {date_str}: нет данных, переходим к следующему")
                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0
                    continue

                for repo_model in repos_data:
                    try:
                        repo_dict = self._fetch_repo_full_data(repo_model.full_name)

                        if repo_dict:
                            current_batch.append(repo_dict)
                            total_in_interval += 1
                            self.stats['fetched'] += 1

                            if len(current_batch) >= self.batch_size:
                                self.stats['batches'] += 1
                                progress = FetchProgress(
                                    current_date=current_date,
                                    page=page,
                                    fetched_in_interval=total_in_interval,
                                    total_fetched=self.stats['fetched'],
                                    errors=self.stats['errors']
                                )
                                yield current_batch, progress
                                current_batch = []

                    except Exception as e:
                        print(f" Ошибка обработки {repo_model.full_name}: {e}")
                        self.stats['errors'] += 1

                    time.sleep(self.delay)

                if len(repos_data) < 100:
                    print(f"День {date_str}: завершен ({total_in_interval} репозиториев)")
                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0
                else:
                    page += 1

                if max_repos_per_day and total_in_interval >= max_repos_per_day:
                    print(f"Достигнут лимит дня ({max_repos_per_day}), переходим к следующему")
                    current_date += timedelta(days=1)
                    page = 1
                    total_in_interval = 0

            except Exception as e:
                print(f"Ошибка для {date_str}: {e}")
                self.stats['errors'] += 1
                time.sleep(self.delay * 5)
                continue

        if current_batch:
            self.stats['batches'] += 1
            progress = FetchProgress(
                current_date=current_date,
                page=page,
                fetched_in_interval=total_in_interval,
                total_fetched=self.stats['fetched'],
                errors=self.stats['errors']
            )
            yield current_batch, progress

        print(f"\n Сбор завершен!")
        print(f"Статистика: {self.stats}")


    def _fetch_repo_full_data(self, full_name:str) -> Optional[Dict[str, Any]]:
        owner, name = full_name.split('/')

        try:
            repo_info = self.api.get_repo(owner, name)
            self.stats['requests'] += 1

            repo_dict = repo_info.model_dump()
            #repo_dict['owner'] = {"login": owner, 'type': 'User'}
            #+++ ВасильевВВ (type заполняется из API)
            repo_dict['owner'] = {"login": owner, 'type': repo_info.owner.type}
            #--- ВасильевВВ (type заполняется из API)

            try:
                repo_dict['readme'] = self.api.get_readme(owner, name)
                self.stats['requests'] += 1
            except Exception:
                repo_dict['readme'] = None


            repo_dict['releases_count'] = self.api.get_releases_count(owner, name)
            self.stats['requests'] += 1

            repo_dict['contributors_count'] = self.api.get_contributors_count(owner, name)
            self.stats['requests'] += 1

            repo_dict['languages_map'] = self.api.get_languages(owner, name)
            self.stats['requests'] += 1

            #+++ ВасильевВВ (добавил отсутствующие поля)
            repo_dict['commits_count'] = self.api.get_commits_count(owner, name)
            self.stats['requests'] += 1

            repo_dict['owner_location'] = self.api.get_owner_location(repo_info.owner)
            self.stats['requests'] += 1
            #--- ВасильевВВ (добавил отсутствующие поля)

            repo_dict['open_issues_count'] = self.api.get_issues_count(owner, name, False)
            repo_dict['closed_issues_count'] = self.api.get_issues_count(owner, name, True)
            self.stats['requests'] += 2

            repo_dict['open_pr_count'] = self.api.get_pr_count(owner, name, False)
            #repo_dict['merged_pr_count'] = self.api.get_pr_count(owner, name, True)
            #+++ ВасильевВВ (перепутано поле)
            repo_dict['closed_pr_count'] = self.api.get_pr_count(owner, name, True)
            #--- ВасильевВВ
            self.stats['requests'] += 2

            repo_dict['subscribers_count'] = getattr(repo_info, 'subscribers_count', 0)
            repo_dict['license_spdx_id'] = getattr(repo_info, 'license_spdx_id', None)

            return repo_dict

        except Exception as e:
            print(f"Не удалось получить {full_name}: {e}")
            self.stats['errors'] += 1
            return None


    def get_stats(self) -> Dict[str, int]:
        return self.stats


    def reset_stats(self):
        self.stats = {'fetched': 0, 'errors': 0, 'requests': 0}
