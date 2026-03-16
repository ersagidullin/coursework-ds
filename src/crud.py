from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Repository

class RepoCRUD:
    def __init__(self, session: Session):
        self.session = session

    # ---------- CREATE ----------
    def insert_repo(self, repo_data: Dict[str, Any]) -> Repository:
        """
        Добавляет новый репозиторий. Если запись с таким id уже существует,
        можно либо проигнорировать, либо обновить – здесь реализовано
        добавление с проверкой на существование (upsert через merge).
        """
        repo = Repository.from_github_api(repo_data)
        # merge – вставит, если нет, или обновит, если есть (по primary key)
        merged = self.session.merge(repo)
        self.session.commit()
        return merged

    def insert_many_repos(self, repos_list: List[Dict[str, Any]]) -> List[Repository]:
        """
        Массовая вставка нескольких репозиториев.
        Используем bulk_save_objects для эффективности.
        """
        repo_objects = [Repository.from_github_api(data) for data in repos_list]
        # bulk_save_objects не обновляет существующие, только вставляет новые.
        # Для upsert пришлось бы использовать более сложные методы.
        # Здесь для простоты используем merge в цикле, но это медленно.
        # Альтернатива: использовать session.bulk_insert_mappings + обработка конфликтов.
        # Для демонстрации оставим простой вариант:
        inserted = []
        for repo in repo_objects:
            inserted.append(self.session.merge(repo))
        self.session.commit()
        return inserted

    # ---------- READ ----------
    def get_repo(self, repo_id: int) -> Optional[Repository]:
        """Получить репозиторий по ID."""
        return self.session.get(Repository, repo_id)

    def get_all_repos(self, limit: int = 100, offset: int = 0) -> List[Repository]:
        """Получить все репозитории с пагинацией."""
        return self.session.query(Repository).order_by(Repository.id).limit(limit).offset(offset).all()

    def search_repos(self, **filters) -> List[Repository]:
        """
        Поиск с фильтрацией.
        Пример: search_repos(language='python', stargazers_count_min=1000)
        """
        query = self.session.query(Repository)
        conditions = []

        if 'language' in filters:
            conditions.append(Repository.language == filters['language'])
        if 'stargazers_count_min' in filters:
            conditions.append(Repository.stargazers_count >= filters['stargazers_count_min'])
        if 'owner_login' in filters:
            conditions.append(Repository.owner_login == filters['owner_login'])
        if 'created_after' in filters:
            conditions.append(Repository.created_at >= filters['created_after'])

        if conditions:
            query = query.filter(and_(*conditions))

        return query.order_by(Repository.stargazers_count.desc()).limit(100).all()

    # ---------- UPDATE ----------
    def update_repo(self, repo_id: int, update_data: Dict[str, Any]) -> Optional[Repository]:
        """
        Обновляет поля репозитория (кроме id). Возвращает обновлённый объект или None.
        """
        repo = self.session.get(Repository, repo_id)
        if not repo:
            return None

        # Разрешённые для обновления поля
        allowed_fields = {'name', 'description', 'stargazers_count', 'forks_count',
                          'language', 'updated_at', 'pushed_at', 'is_private'}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(repo, field, value)

        self.session.commit()
        return repo

    # ---------- DELETE ----------
    def delete_repo(self, repo_id: int) -> bool:
        """Удаляет репозиторий по ID. Возвращает True, если удаление произошло."""
        repo = self.session.get(Repository, repo_id)
        if repo:
            self.session.delete(repo)
            self.session.commit()
            return True
        return False

    def delete_all_repos(self) -> int:
        """Удаляет все записи из таблицы (осторожно!). Возвращает количество удалённых."""
        count = self.session.query(Repository).delete()
        self.session.commit()
        return count
