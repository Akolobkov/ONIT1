from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Framework

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
