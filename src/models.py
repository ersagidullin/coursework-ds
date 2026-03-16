from sqlalchemy import Integer, Text, DateTime, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


class Repository(Base):
    """
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
    * merged_pr_count: количество смерженных pullrequests
    * full_name: название репозитория
    * contributors_count: количество контрибьюторов
    """

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    readme: Mapped[Optional[str]] = mapped_column(Text)
    releases_count: Mapped[int] = mapped_column(Integer)
    subscribers_count: Mapped[int] = mapped_column(Integer)
    stargazers_count: Mapped[int] = mapped_column(Integer)
    forks_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    license_spdx_id: Mapped[Optional[str]] = mapped_column(String)
    topics: Mapped[list[str]] = mapped_column(JSON)
    pushed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    languages_map: Mapped[dict[str, float]] = mapped_column(JSON)
    open_issues_count: Mapped[int] = mapped_column(Integer)
    closed_issues_count: Mapped[int] = mapped_column(Integer)
    open_pr_count: Mapped[int] = mapped_column(Integer)
    merged_pr_count: Mapped[int] = mapped_column(Integer)
    full_name: Mapped[str] = mapped_column(String)
    contributors_count: Mapped[int] = mapped_column(Integer)
