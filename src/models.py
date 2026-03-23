from sqlalchemy import Integer, Text, DateTime, String, JSON, BigInteger
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
    * open_issues_count: количество открытых issues
    * closed_issues_count: количество закрытых issues
    * open_pr_count: количество открытых pullrequests
    * closed_pr_count: количество закрытых pullrequests
    * full_name: название репозитория
    * contributors_count: количество контрибьюторов
    * commits_count: количество коммитов
    * owner_location: местоположение владельца
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
    open_issues_count: Mapped[int] = mapped_column(Integer, nullable=False)
    closed_issues_count: Mapped[int] = mapped_column(Integer, nullable=False)
    open_pr_count: Mapped[int] = mapped_column(Integer, nullable=False)
    closed_pr_count: Mapped[int] = mapped_column(Integer, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    contributors_count: Mapped[int] = mapped_column(Integer, nullable=False)
    commits_count: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    @classmethod
    def from_snapshot(cls, snapshot: RepositorySnapshot):
        return cls(**snapshot.model_dump())
