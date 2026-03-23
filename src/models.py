from sqlalchemy import Integer, Text, DateTime, String, JSON, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional


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
    def from_github_api(cls, data: dict) -> "Repository":
        return cls(
            github_id=data["github_id"],
            readme=data.get("readme"),
            releases_count=data.get("releases_count", 0),
            subscribers_count=data.get("subscribers_count", 0),
            stargazers_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            created_at=data["created_at"],
            license_spdx_id=data.get("license_spdx_id"),
            topics=data.get("topics", []),
            pushed_at=data.get("pushed_at"),
            languages_map=data.get("languages_map", {}),
            open_issues_count=data.get("open_issues_count", 0),
            closed_issues_count=data.get("closed_issues_count", 0),
            open_pr_count=data.get("open_pr_count", 0),
            closed_pr_count=data.get("closed_pr_count", 0),
            full_name=data["full_name"],
            contributors_count=data.get("contributors_count", 0),
            commits_count=data.get("commits_count", 0),
            owner_location=data.get("owner_location"),
        )
