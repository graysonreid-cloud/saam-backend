import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base, engine


# -------------------------------------------------------------------
# Request (raw webhook event)
# -------------------------------------------------------------------

class Request(Base):
    __tablename__ = "requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)

    action_logs = relationship("ActionLog", back_populates="request", cascade="all, delete-orphan")
    response_logs = relationship("ResponseLog", back_populates="request", cascade="all, delete-orphan")
    lifecycle_events = relationship("RequestLifecycle", back_populates="request", cascade="all, delete-orphan")
    jira_links = relationship("JiraLink", back_populates="request", cascade="all, delete-orphan")


# -------------------------------------------------------------------
# ActionLog (internal SAAM actions)
# -------------------------------------------------------------------

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("requests.id"), nullable=False)
    action_type = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    request = relationship("Request", back_populates="action_logs")


# -------------------------------------------------------------------
# ResponseLog (outgoing messages)
# -------------------------------------------------------------------

class ResponseLog(Base):
    __tablename__ = "response_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("requests.id"), nullable=False)
    response_type = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    request = relationship("Request", back_populates="response_logs")


# -------------------------------------------------------------------
# RequestLifecycle (pipeline stages)
# -------------------------------------------------------------------

class RequestLifecycle(Base):
    __tablename__ = "request_lifecycle"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("requests.id"), nullable=False)
    stage = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    request = relationship("Request", back_populates="lifecycle_events")


# -------------------------------------------------------------------
# JiraLink (link SAAM request → Jira issue)
# -------------------------------------------------------------------

class JiraLink(Base):
    __tablename__ = "jira_links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("requests.id"), nullable=False)
    issue_key = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    request = relationship("Request", back_populates="jira_links")


# -------------------------------------------------------------------
# TeamMember (canonical identity model)
# -------------------------------------------------------------------

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    external_id_jira = Column(String, unique=True, index=True, nullable=True)
    external_id_teams = Column(String, unique=True, index=True, nullable=True)

    external_identities = relationship(
        "TeamMemberExternalIdentity",
        back_populates="team_member",
        cascade="all, delete-orphan"
    )

    display_name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    role = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


class TeamMemberExternalIdentity(Base):
    __tablename__ = "team_member_external_identities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    team_member_id = Column(String, ForeignKey("team_members.id"), nullable=False)
    source = Column(String, nullable=False)  # "jira", "teams", "git", etc.
    external_id = Column(String, nullable=False, index=True)

    team_member = relationship("TeamMember", back_populates="external_identities")


# -------------------------------------------------------------------
# Create all tables
# -------------------------------------------------------------------

def init_db():
    Base.metadata.create_all(bind=engine)
