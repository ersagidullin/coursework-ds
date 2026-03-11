from sqlalchemy import Column, Integer, String, BigInteger, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(BigInteger, primary_key=True)          # GitHub repository ID
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    owner_login = Column(String(255), nullable=False)
    owner_type = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    pushed_at = Column(DateTime(timezone=True))
    stargazers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    language = Column(String(100))
    html_url = Column(Text)
    is_private = Column(Boolean, default=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Repository(id={self.id}, full_name='{self.full_name}')>"

    @classmethod
    def from_github_api(cls, data: dict):
        """
        Создаёт экземпляр Repository из сырых данных, полученных от GitHub API.
        """
        owner = data.get('owner', {})
        return cls(
            id=data['id'],
            name=data['name'],
            full_name=data['full_name'],
            owner_login=owner.get('login'),
            owner_type=owner.get('type'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            pushed_at=data.get('pushed_at'),
            stargazers_count=data.get('stargazers_count', 0),
            forks_count=data.get('forks_count', 0),
            language=data.get('language'),
            html_url=data.get('html_url'),
            is_private=data.get('private', False)
        )