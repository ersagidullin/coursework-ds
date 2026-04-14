from sqlalchemy import Boolean, Integer, Text, DateTime, String, JSON, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from api import RepositorySnapshot


class Base(DeclarativeBase):
    pass


class Repository(Base):
    """
    * github_id: id репозитория
    * readme: README произвольного размера
    * releases_count: количество релизов
    * subscribers_count: количество отслеживающих (watchers)
    * stargazers_count: количество звезд
    * forks_count: количество форков
    * created_at: дата создания репозитория
    * license_spdx_id: лицензия (SPDX ID)
    * topics: список топиков репозитория
    * pushed_at: дата последнего push
    * languages_map: языки репозитория в %
    * full_name: название репозитория
    * contributors_count: количество контрибьюторов
    * owner_location: местоположение владельца
    * description: описание репозитория
    * owner_type: тип владельца (user или organization)
    * size: размер репозитория в килобайтах
    * has_github_actions: использование gitHub actions
    * recent_commits: список последних коммитов
    * commit_stats: статистика по коммитам
    * root_contents: содержимое корневой директории
    * pull_request_stats: статистика по pull requests
    * recent_pull_requests: последние pull requests
    * issue_stats: статистика по issues
    * recent_issues: последние issues
    """

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    github_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    readme: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    releases_count: Mapped[int] = mapped_column(Integer, nullable=False)
    subscribers_count: Mapped[int] = mapped_column(Integer, nullable=False)
    stargazers_count: Mapped[int] = mapped_column(Integer, nullable=False)
    forks_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    license_spdx_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    pushed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    languages_map: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    contributors_count: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    has_github_actions: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recent_commits: Mapped[list[dict]] = mapped_column(JSON, default=list)
    commit_stats: Mapped[dict] = mapped_column(JSON, default=dict)
    root_contents: Mapped[list[dict]] = mapped_column(JSON, default=list)
    pull_request_stats: Mapped[dict] = mapped_column(JSON, default=dict)
    recent_pull_requests: Mapped[list[dict]] = mapped_column(JSON, default=list)
    issue_stats: Mapped[dict] = mapped_column(JSON, default=dict)
    recent_issues: Mapped[list[dict]] = mapped_column(JSON, default=list)
    
    @classmethod
    def from_snapshot(cls, snapshot: RepositorySnapshot):
        return cls(**snapshot.model_dump())
