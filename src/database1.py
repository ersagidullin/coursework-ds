from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=False)  # echo=True для отладки SQL
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Создаёт все таблицы, определённые в моделях."""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Удаляет все таблицы (осторожно!)."""
        Base.metadata.drop_all(self.engine)

    def get_session(self) -> Session:
        """Возвращает новую сессию."""
        return self.SessionLocal()