"""
Основной модуль.
Содержит процедуры, определяющие логику работы. Вспомогательные процедуры вынесены в другие модули.
"""

from common import get_tokens, get_period
import json
import psycopg2
import sqlalchemy

tokens = []
date_start = ""
date_end = ""

# функция с основной логикой программы (entry point)
def main():
    repositories = list(api_get_repositories())
    #postgresql+psycopg2://postgres:111@localhost:41750/github
    #print(repositories) # для теста

    # Подключение к базе
    try:
        conn = psycopg2.connect("host=localhost port=41750 dbname=postgres user=postgres password=vpiFGdXd")
        cur = conn.cursor()
    except ValueError:
        print("Ошибка соединения с базой данных")

    # +++ код используется при полном соответствии полей json и колонок таблицы
    columns = repositories[10].keys()
    values = [repositories[10][col] for col in columns]
    # --- код используется при полном соответствии полей json и колонок таблицы

    # +++ Только нужные колонки (предварительная фильтрация)
    allowed_columns = {"id", "node_id", "name"}  # множество допустимых колонок
    filtered_data = {k: v for k, v in repositories[10].items() if k in allowed_columns}
    columns = filtered_data.keys()
    values = list(filtered_data.values())
    # --- Только нужные колонки (предварительная фильтрация)

    insert_statement = f"INSERT INTO repositories ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    cur.execute(insert_statement, values)

    conn.commit()
    cur.close()
    conn.close()

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
    iso_str = date_start.isoformat(timespec='seconds').replace('+00:00', 'Z')
    filter = "is:public+created:>" + iso_str
    if len(tokens)>0:
        fetcher = api.GitHubRepoFetcher(tokens[0])
        repositories = fetcher.fetch_repos()
    else:
        fetcher = api.GitHubRepoFetcher()
        repositories = fetcher.fetch_repos()
    return repositories

# запуск основной логики программы
if __name__ == "__main__":
    main()