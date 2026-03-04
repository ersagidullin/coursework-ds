"""
Основной модуль.
Содержит процедуры, определяющие логику работы. Вспомогательные процедуры вынесены в другие модули.
"""

from common import get_tokens, get_period

tokens = []
date_start = ""
date_end = ""

# функция с основной логикой программы (entry point)
def main():
    repositories = api_get_repositories()
    print(repositories)

# получение репозиториев через API
def api_get_repositories():
    import api
    #from api import GitHubRepoFetcher
    global tokens
    tokens = get_tokens(tokens)
    period = get_period()
    if period[2]:
        print("Загрузка отменена пользователем.")
        return
    global date_start, date_end
    date_start = period[0]
    date_end = period[1]
    if len(tokens)>0:
        fetcher = api.GitHubRepoFetcher(tokens[0])
        repositories = fetcher.fetch_all_repos()
    else:
        fetcher = api.GitHubRepoFetcher()
        repositories = fetcher.fetch_all_repos()
    return repositories

# запуск основной логики программы
if __name__ == "__main__":
    main()
