from database import Database
from crud import RepoCRUD
from fetcher import GitHubFetcher, FetchProgress
from api import GitHubAPI
import os
from dotenv import load_dotenv
from datetime import datetime

#tokens = []
#date_start = ""
#date_end = ""

# функция с основной логикой программы (entry point)
def main():
    # создаем базу данных с таблицей
    database_url = "postgresql://postgres:vpiFGdXd@localhost:41750/github"
    database = Database(database_url)
    database.create_tables()

    session = database.get_session()
    crud = RepoCRUD(session)

    #token = get_tokens(tokens)
    load_dotenv()
    token = os.getenv("token")
    date_str = os.getenv('date_start')
    if date_str:
        date_start = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        print("Переменная date_str не найдена")
    date_str = os.getenv('date_end')
    if date_str:
        date_end = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        print("Переменная date_str не найдена")

    api = GitHubAPI(token)
    fetcher = GitHubFetcher(api)
    result = list(fetcher.fetch_repositories(date_start, date_end))
    for res in result:
        inserted = crud.insert_many_repos(res[0])

# запуск основной логики программы
if __name__ == "__main__":
    main()