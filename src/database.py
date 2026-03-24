from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            echo=True,
            future=True,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.SessionLocal()
