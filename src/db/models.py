from datetime import datetime
from typing import Literal, get_args

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, validates, mapped_column, relationship, backref
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import uuid

from sqlalchemy.types import JSON

AllowedTaskStatus = Literal["todo", "in_progress", "done"]
AllowedRoles = Literal['owner', 'member']
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    memberships = relationship("ProjectMember", back_populates="user", lazy="selectin")
    settings = relationship("UserSettings", lazy="selectin", uselist=False, back_populates="user")

class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"))
    settings: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

    user = relationship("User", back_populates="settings")

class UserInvite(Base):
    __tablename__ = "user_invites"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"))
    project_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("projects.id", ondelete="CASCADE"))
    status: Mapped[Literal["accepted", "denied", "waiting"]] = mapped_column(nullable=True, default='waiting')

    project = relationship("Project")
    user = relationship("User")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    members = relationship("ProjectMember",
                           back_populates="project",
                           lazy="selectin",
                           cascade="all, delete-orphan",
                           passive_deletes=True)
    tasks = relationship("Task",
                         back_populates="project",
                         lazy="selectin",
                         cascade="all, delete-orphan",
                         passive_deletes=True)
    owner = relationship("User", foreign_keys=[owner_id], lazy="joined")

    @property
    def owner_email(self):
        return self.owner.email

class ProjectMember(Base):
    __tablename__ = "project_members"

    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("projects.id"), primary_key=True)
    role: Mapped[str] = mapped_column(default='member', nullable=False)

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="members")

    @validates("role")
    def validate_role(self, key, role):
        allowed = get_args(AllowedRoles)
        if role not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return role
    
    @property
    def name(self):
        return self.user.name # для получения имени пользователя

    @property
    def email(self):
        return self.user.email # для получения почты пользователя

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[AllowedTaskStatus] = mapped_column(default='todo', nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    assignee_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment",
                            back_populates="task",
                            cascade="all, delete-orphan",
                            passive_deletes=True)
    assignee = relationship("User")

    @property
    def assignee_email(self):
        return self.assignee.email

    @property
    def project_owner_email(self) -> str:
        return self.project.owner.email

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False,)
    author_id: Mapped[uuid.UUID] = mapped_column(PGUUID, ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    replied_to: Mapped[uuid.UUID] = mapped_column(ForeignKey("comments.id"), default=None, nullable=True)
    is_reply_deleted: Mapped[bool] = mapped_column(default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    task = relationship("Task", back_populates="comments")
    author = relationship("User")
    replies = relationship(
        "Comment",
        backref=backref("parent", remote_side=[id]),
        lazy="selectin"
    )

    @property
    def author_name(self):
        return self.author.name 
    
    @property
    def author_email(self):
        return self.author.email