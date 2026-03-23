from sqlalchemy import Column, Integer, String, BigInteger, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)          # GitHub repository ID
    node_id = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    full_name = Column(String(), nullable=False)
    private = Column(Boolean, default=False)
    owner = Column(JSONB)
    html_url = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
    fork = Column(Boolean, default=False)
    url = Column(String(), nullable=False)
    forks_url = Column(String(), nullable=False)
    keys_url = Column(String(), nullable=False)
    collaborators_url = Column(String(), nullable=False)
    teams_url = Column(String(), nullable=False)
    hooks_url = Column(String(), nullable=False)
    issue_events_url = Column(String(), nullable=False)
    events_url = Column(String(), nullable=False)
    assignees_url = Column(String(), nullable=False)
    branches_url = Column(String(), nullable=False)
    tags_url = Column(String(), nullable=False)
    blobs_url = Column(String(), nullable=False)
    git_tags_url = Column(String(), nullable=False)
    git_refs_url = Column(String(), nullable=False)
    trees_url = Column(String(), nullable=False)
    statuses_url = Column(String(), nullable=False)
    languages_url = Column(String(), nullable=False)
    stargazers_url = Column(String(), nullable=False)
    full_name = Column(String(), nullable=False)
    #owner_login = Column(String(255), nullable=False)
    #owner_type = Column(String(50))
    #description = Column(Text)
    #created_at = Column(DateTime(timezone=True))
    #updated_at = Column(DateTime(timezone=True))
    #pushed_at = Column(DateTime(timezone=True))
    #stargazers_count = Column(Integer, default=0)
    #forks_count = Column(Integer, default=0)
    #language = Column(String(100))
    #html_url = Column(Text)
    #is_private = Column(Boolean, default=False)
    #fetched_at = Column(DateTime(timezone=True), server_default=func.now())

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
            node_id=data['node_id'],
            name=data['name'],
            full_name=data['full_name'],
            private=data['private'],
            owner=data['owner'],
            html_url=data['html_url'],
            description=data['description'],
            fork=data['fork'],
            url=data['url'],
            forks_url=data['forks_url'],
            keys_url=data['keys_url'],
            collaborators_url=data['collaborators_url'],
            teams_url=data['teams_url'],
            hooks_url=data['hooks_url'],
            issue_events_url=data['issue_events_url'],
            events_url=data['events_url'],
            assignees_url=data['assignees_url'],
            branches_url=data['branches_url'],
            tags_url=data['tags_url'],
            blobs_url=data['blobs_url'],
            git_tags_url=data['git_tags_url'],
            git_refs_url=data['git_refs_url'],
            trees_url=data['trees_url'],
            statuses_url=data['statuses_url'],
            languages_url=data['languages_url'],
            stargazers_url=data['forks_url'],
            #created_at=data.get('created_at'),
            #updated_at=data.get('updated_at'),
            #pushed_at=data.get('pushed_at'),
            #stargazers_count=data.get('stargazers_count', 0),
            #forks_count=data.get('forks_count', 0),
            #language=data.get('language'),
            #html_url=data.get('html_url'),
            #is_private=data.get('private', False)
        )