from datetime import datetime
from typing import Literal, get_args

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, validates, mapped_column, relationship

AllowedTaskStatus = Literal["todo", "in_progress", "done"]
AllowedRoles = Literal['owner', 'member']
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    memberships = relationship("ProjectMember", back_populates="user", lazy="selectin")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    members = relationship("ProjectMember", back_populates="project", lazy="selectin")
    tasks = relationship("Task", back_populates="project", lazy="selectin")

class ProjectMember(Base):
    __tablename__ = "project_members"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    role: Mapped[str] = mapped_column(default='member', nullable=False)

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="members")

    @validates("role")
    def validate_role(self, key, role):
        allowed = get_args(AllowedRoles)
        if role not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return role

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[AllowedTaskStatus] = mapped_column(default='todo', nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment", back_populates="task")

    @validates("status")
    def validate_status(self, key, status):
        allowed = get_args(AllowedTaskStatus)
        if status not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return status

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    project = relationship("Project", back_populates="comments")
