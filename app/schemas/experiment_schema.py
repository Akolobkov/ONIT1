from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ExperimentStatus


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