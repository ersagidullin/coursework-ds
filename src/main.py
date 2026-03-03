from api import GitHubRepoFetcher
import common

tokens = []
date_start = ""
date_end = ""

# функция с основной логикой программы (entry point)
def main():
    api_get_repositories()

# получение репозиториев через API
def api_get_repositories():
    global tokens
    tokens = common.get_tokens(tokens)
    loc_date_start = ""
    loc_date_end = ""
    common.get_period(loc_date_start, loc_date_end)
    a=1

# запуск основной логики программы
if __name__ == "__main__":
    main()
