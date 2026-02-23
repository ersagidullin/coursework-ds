import requests
from typing import Dict, List, Optional, Any, Generator

class GitHubRepoFetcher:
    """
    Класс для получения данных о репозиториях GitHub через API поиска.
    """
    # Базовый URL для поиска репозиториев
    BASE_URL = "https://api.github.com/search/repositories"

    def __init__(self, api_token: Optional[str] = None):
        """
        Инициализирует загрузчик.

        Args:
            api_token: Опциональный Personal Access Token для GitHub API.
                      Использование токена увеличивает лимиты скорости запросов.
        """
        self.api_token = api_token
        self.session = requests.Session()
        if api_token:
            self.session.headers.update({"Authorization": f"token {api_token}"})
        # Рекомендуется указывать User-Agent
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Внутренний метод для выполнения запроса к API и обработки ответа.

        Args:
            params: Параметры запроса (словарь).

        Returns:
            Словарь с данными ответа от API.

        Raises:
            Exception: Если запрос не удался или API вернул ошибку.
        """
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()  # Выбросит исключение для HTTP ошибок (4xx или 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к GitHub API: {e}")
        except ValueError as e:
            raise Exception(f"Ошибка при разборе JSON ответа: {e}")

    def fetch_repos(
        self,
        query: str = "is:public",
        per_page: int = 30,
        max_pages: Optional[int] = None,
        sort: Optional[str] = None,
        order: str = "desc"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Получает список публичных репозиториев, соответствующих поисковому запросу.
        Поддерживает пагинацию и возвращает результаты по одному (как генератор).

        Args:
            query: Поисковый запрос в формате GitHub. По умолчанию "is:public".
            per_page: Количество результатов на страницу (макс. 100).
            max_pages: Максимальное количество страниц для загрузки (None - все доступные).
            sort: Поле для сортировки (напр., 'stars', 'forks', 'updated').
            order: Порядок сортировки ('desc' или 'asc').

        Yields:
            Словарь с данными одного репозитория (элемент из списка 'items').

        Пример:
            fetcher = GitHubRepoFetcher()
            for repo in fetcher.fetch_repos(query="language:python", sort="stars", per_page=10):
                print(repo['name'], repo['stargazers_count'])
        """
        page = 1
        pages_loaded = 0

        while True:
            if max_pages is not None and pages_loaded >= max_pages:
                break

            # Формируем параметры для текущей страницы
            params = {
                "q": query,
                "per_page": min(per_page, 100),  # API ограничивает 100
                "page": page
            }
            if sort:
                params["sort"] = sort
                params["order"] = order

            print(f"Загрузка страницы {page}...") # Для отладки
            data = self._make_request(params)

            # Обрабатываем элементы на текущей странице
            items = data.get('items', [])
            for repo in items:
                yield repo

            # Проверяем, есть ли еще страницы
            # GitHub API возвращает информацию о ссылках в заголовках, но для простоты
            # будем ориентироваться на количество полученных элементов.
            if len(items) < per_page:
                break # Это была последняя страница

            # Также можно проверить флаг incomplete_results
            if data.get('incomplete_results', False):
                print("Предупреждение: Результаты неполные (возможно, таймаут сервера).")
                # В этом случае лучше остановиться, так как следующие страницы могут быть недоступны.
                break

            page += 1
            pages_loaded += 1

    def fetch_all_repos(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Удобный метод для получения ВСЕХ результатов в виде одного списка.
        Использует тот же генератор `fetch_repos`.

        Args:
            **kwargs: Те же аргументы, что и у `fetch_repos` (кроме max_pages, он здесь игнорируется).

        Returns:
            Список всех словарей с данными репозиториев.
        """
        # Убираем max_pages из kwargs, если он там есть, чтобы загрузить всё
        kwargs.pop('max_pages', None)
        return list(self.fetch_repos(max_pages=None, **kwargs))

