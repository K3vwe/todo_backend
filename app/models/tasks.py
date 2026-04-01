import uuid
from .users import User
from datetime import datetime, date, time
from sqlalchemy import (
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from sqlalchemy.orm import validates
from app.models.enum import TaskStatus, TaskPriority

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        ENUM(TaskPriority, name="task_priority", create_type=False,),
        nullable=False,
        server_default=TaskPriority.MEDIUM.value,
    )

    status: Mapped[TaskStatus] = mapped_column(
        ENUM(TaskStatus, name="task_status", create_type=False,),
        nullable=False,
        server_default=TaskStatus.PENDING.value,
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )

    due_time: Mapped[time] = mapped_column(
        Time,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[User] = relationship("User", back_populates="tasks")

    @validates("started_at", "completed_at")
    def auto_status(self, key, value):
        """
        Status auto-derived from timestamps:
        - completed_at set → COMPLETE
        - started_at set → IN_PROGRESS (if not complete)
        - else → PENDING
        """
        if key == "completed_at" and value is not None:
            self.status = TaskStatus.COMPLETED
        elif key == "started_at" and value is not None and not self.completed_at:
            self.status = TaskStatus.IN_PROGRESS
        elif not self.started_at and not self.completed_at:
            self.status = TaskStatus.PENDING
        return value