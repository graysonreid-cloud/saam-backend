import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, DateTime, JSON,
    ForeignKey, Integer, Float
)
from sqlalchemy.orm import relationship

from db.base import Base


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

    # Relationships
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
# JiraLink (SAAM request → Jira issue)
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

    # Optional direct external IDs (legacy fields)
    external_id_jira = Column(String, unique=True, index=True, nullable=True)
    external_id_teams = Column(String, unique=True, index=True, nullable=True)

    # Flexible identity mappings
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

    behaviour_records = relationship("MemberBehaviour", back_populates="team_member")


# -------------------------------------------------------------------
# TeamMemberExternalIdentity (multi‑source identity mapping)
# -------------------------------------------------------------------

class TeamMemberExternalIdentity(Base):
    __tablename__ = "team_member_external_identities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    team_member_id = Column(String, ForeignKey("team_members.id"), nullable=False)
    source = Column(String, nullable=False)          # e.g., "jira", "teams", "slack"
    external_id = Column(String, nullable=False, index=True)

    team_member = relationship("TeamMember", back_populates="external_identities")


# -------------------------------------------------------------------
# MemberBehaviour (per‑member behavioural metrics)
# -------------------------------------------------------------------

class MemberBehaviour(Base):
    __tablename__ = "member_behaviour"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    request_id = Column(String, nullable=False)
    team_member_id = Column(String, ForeignKey("team_members.id"), nullable=True)

    # Raw behavioural metrics
    actions = Column(Integer, nullable=False)
    responses = Column(Integer, nullable=False)
    issues = Column(Integer, nullable=False)
    avg_blocker_age = Column(Float, nullable=False)
    interaction_load = Column(Float, nullable=False)

    # Normalised metrics
    participation_norm = Column(Float, nullable=False)
    blocker_norm = Column(Float, nullable=False)
    interaction_norm = Column(Float, nullable=False)

    triggered_rules = Column(JSON, nullable=True)

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    team_member = relationship("TeamMember", back_populates="behaviour_records")


# -------------------------------------------------------------------
# JiraUser (canonical Jira identity)
# -------------------------------------------------------------------

class JiraUser(Base):
    __tablename__ = "jira_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    # Link to canonical TeamMember
    team_member_id = Column(String, ForeignKey("team_members.id"), nullable=True)
    team_member = relationship("TeamMember")

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)


# -------------------------------------------------------------------
# JiraIssue (persistent issue state)
# -------------------------------------------------------------------

class JiraIssue(Base):
    __tablename__ = "jira_issues"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_key = Column(String, unique=True, index=True, nullable=False)

    summary = Column(String, nullable=True)
    status = Column(String, nullable=True)
    issue_type = Column(String, nullable=True)
    priority = Column(String, nullable=True)

    reporter_id = Column(String, ForeignKey("jira_users.id"), nullable=True)
    assignee_id = Column(String, ForeignKey("jira_users.id"), nullable=True)

    reporter = relationship("JiraUser", foreign_keys=[reporter_id])
    assignee = relationship("JiraUser", foreign_keys=[assignee_id])

    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    events = relationship("JiraEvent", back_populates="issue", cascade="all, delete-orphan")


# -------------------------------------------------------------------
# JiraEvent (every webhook event)
# -------------------------------------------------------------------

class JiraEvent(Base):
    __tablename__ = "jira_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("jira_issues.id"), nullable=False)

    event_type = Column(String, nullable=False)       # e.g., "issue_updated", "comment_created"
    raw_payload = Column(JSON, nullable=False)

    triggered_by_id = Column(String, ForeignKey("jira_users.id"), nullable=True)
    triggered_by = relationship("JiraUser")

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    issue = relationship("JiraIssue", back_populates="events")


# -------------------------------------------------------------------
# TeamMemberInteraction (behavioural signals per event)
# -------------------------------------------------------------------

class TeamMemberInteraction(Base):
    __tablename__ = "team_member_interactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    team_member_id = Column(String, ForeignKey("team_members.id"), nullable=False)
    jira_event_id = Column(String, ForeignKey("jira_events.id"), nullable=False)

    # Behavioural signal classification
    signal_type = Column(String, nullable=False)      # e.g., "comment", "status_change", "assignment"
    weight = Column(Float, nullable=False)            # numeric signal strength

    # FIXED: cannot use reserved name "metadata"
    event_metadata = Column(JSON, nullable=True)

    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    team_member = relationship("TeamMember")
    jira_event = relationship("JiraEvent")
