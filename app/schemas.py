from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ExperimentStatus, Framework, TaskStatus


# ---------- Task ----------

class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.OPEN


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Model ----------

class ModelBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    framework: Framework
    task_id: int


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    framework: Framework | None = None


class ModelRead(ModelBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Experiment ----------

class ExperimentBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    status: ExperimentStatus = ExperimentStatus.RUNNING
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    model_id: int


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    status: ExperimentStatus | None = None
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)


class ExperimentRead(ExperimentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime