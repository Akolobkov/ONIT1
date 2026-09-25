from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Framework(str, Enum):
    PYTORCH = "pytorch"
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"


class ExperimentStatus(str, Enum):
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.OPEN.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    models: Mapped[list["Model"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    framework: Mapped[str] = mapped_column(String(32))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="models")
    experiments: Mapped[list["Experiment"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default=ExperimentStatus.RUNNING.value)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    model: Mapped["Model"] = relationship(back_populates="experiments")