from sqlalchemy import Integer, Text, DateTime, String, JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


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
    * size: размер репозитория в килобайтах
    * topics: список топиков репозитория
    * pushed_at: дата последнего push
    * contributors_count: количество контрибьюторов
    """

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    readme: Mapped[str] = mapped_column(Text)
    releases_count: Mapped[int] = mapped_column(Integer)
    subscribers_count: Mapped[int] = mapped_column(Integer)
    stargazers_count: Mapped[int] = mapped_column(Integer)
    forks_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    license_spdx_id: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)
    topics: Mapped[list[str]] = mapped_column(JSON)
    pushed_at: Mapped[datetime] = mapped_column(DateTime)
    contributors_count: Mapped[datetime] = mapped_column(DateTime)
