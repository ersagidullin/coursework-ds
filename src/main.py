from database import Database
from crud import RepoCRUD
from fetcher import GitHubFetcher, FetchProgress
from api import GitHubAPI
from common import get_tokens, get_period

tokens = []
date_start = ""
date_end = ""

# функция с основной логикой программы (entry point)
def main():
    # создаем базу данных с таблицей
    database_url = "postgresql://postgres:vpiFGdXd@localhost:41750/github"
    database = Database(database_url)
    database.create_tables()


    session = database.get_session()
    crud = RepoCRUD(session)

    token = get_tokens(tokens)
    api = GitHubAPI(token[0])
    period = get_period()
    fetcher = GitHubFetcher(api)
    result = list(fetcher.fetch_repositories(period[0], period[1]))
    for res in result:
        inserted = crud.insert_many_repos(res[0])

# запуск основной логики программы
if __name__ == "__main__":
    main()