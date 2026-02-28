from sqlalchemy import Integer, Text, DateTime, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    * user_repositories: связи с пользователями
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

    user_repositories: Mapped[list["UserRepository"]] = relationship(
        "UserRepository", back_populates="repository", cascade="all, delete-orphan"
    )


class UserRepository(Base):
    """
    * user_id: id пользователя
    * repository_id: id репозитория
    * user: объект пользователя
    * repository: объект репозитория
    * is_owner: True - владелец; False - contributor
    """

    __tablename__ = "user_repositories"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id"), primary_key=True
    )
    user: Mapped["User"] = relationship("User", back_populates="user_repositories")
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="user_repositories"
    )

    is_owner: Mapped[bool] = mapped_column(Boolean)


class User(Base):
    """
    * user_repositories: связи с репозиториями
    * login: логин
    * location: локация
    * company: компания
    * is_organization: True - организация; False - пользователь
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_repositories: Mapped[list["UserRepository"]] = relationship(
        "UserRepository", back_populates="user", cascade="all, delete-orphan"
    )

    login: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    is_organization: Mapped[bool] = mapped_column(Boolean)
