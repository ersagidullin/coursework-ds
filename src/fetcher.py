import time
from typing import  Optional, Dict, Any
from datetime import datetime

from github_api import GithubApi
from models import Repository
from repo_crud import RepoCRUD

class GitHubFentcher:
    def __init__(self, api: GithubApi, crud: RepoCRUD, delay: float = 1.0):
        self.api = api
        self.crud = crud
        self.delay = delay
        self.stats = {"fetched":0, "errors":0, "requests":0}

    def fetch_repositories(self, query:str, max_repos:Optional[int]=None, per_page:int =100)->Dict[str, int]:
        page =1
        total_fetched = 0
        while True:
            if max_repos and total_fetched >= max_repos:
                break
            try:
                repos_data = self.api.search_repo(query, page, per_page)
                self.stats["requests"] += 1
                if not repos_data:
                    break
                for repo_model in repos_data:
                    if max_repos and total_fetched >= max_repos:
                        break
                    full_name = repo_model.full_name
                    try:
                        repo_dict= self._fetch_repo_full_data(full_name)
                        if repo_dict:
                            saved_repo = self.crud.insert_repo(repo_dict)
                            if saved_repo:
                                total_fetched += 1
                                self.stats["fetched"] += 1

                    except Exception as e:
                        print(f"Ошибка при обработке {full_name}: {e}")
                        self.stats["errors"] += 1

                    time.sleep(self.delay)

                if len(repos_data)<per_page:
                    print("Конец данных")
                    break

                page+=1

            except Exception as e:
                print(f"Ошибка на странице {page} - {e}")
                self.stats["errors"] += 1
                time.sleep(self.delay * 5)
                continue

        print(f"Завершено. Всего обработано: {total_fetched}")
        print(f"Статистика: {self.stats}")
        return self.stats


    def _fetch_repo_full_data(self, full_name:str) -> Optional[Dict[str, Any]]:
        owner, name = full_name.split("/")
        try:
            repo_info = self.api.get_repo(owner, name)
            self.stats["requests"] += 1
        except Exception as e:
            print(f"Не удалось получить данные репозитория {full_name}: {e}")
            return None

        repo_dict = repo_info.model_dump()
        repo_dict['owner'] = {"login": owner, 'type':'User'}

        try:
            repo_dict['readme'] = self.api.get_readme(owner, name)
            self.stats["requests"] += 1

        except Exception :
            repo_dict['readme'] = None


        repo_dict['releases_count'] = self.api.get_releases_count(owner, name, 1,100)
        self.stats["requests"] += 1

        repo_dict['contributors_count'] = self.api.get_contributors_count(owner, name)
        self.stats["requests"] += 1

        repo_dict['languages_map'] = self.api.get_languages(owner, name)
        self.stats["requests"] += 1

        repo_dict['open_issues_count'] = self.api.get_issues_count(owner, name, False)
        repo_dict['closed_issues_count'] = self.api.get_issues_count(owner, name, True)
        self.stats["requests"] += 2

        repo_dict['open_pr_count'] = self.api.get_pr_count(owner, name, False)
        repo_dict['merged_pr_count'] = self.api.get_pr_count(owner, name, True)
        self.stats["requests"] += 2

        repo_dict['subscribers_count'] = getattr(repo_info, 'subscribers_count', 0)

        repo_dict['license_spdx_id'] = getattr(repo_info, 'license_spdx_id', None)

        return repo_dict


    def get_stats(self) -> Dict[str, int]:
        return self.stats


    def reset_stats(self):
        self.stats = {'fetched': 0, 'errors': 0, 'requests': 0}
