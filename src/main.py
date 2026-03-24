from fetcher import GitHubFetcher, FetchProgress
from api import GitHubAPI
from common import get_tokens, get_period

tokens = []
date_start = ""
date_end = ""

# функция с основной логикой программы (entry point)
def main():
    token = get_tokens(tokens)
    API = GitHubAPI(token)
    period = get_period()
    g = GitHubFetcher.fetch_repositories(period[0], period[1])
    a = 1
# запуск основной логики программы
if __name__ == "__main__":
    main()