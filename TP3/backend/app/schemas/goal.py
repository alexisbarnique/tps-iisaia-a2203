import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.enums import CategoryEnum


class GoalCreate(BaseModel):
    year: int = Field(ge=2020, le=2100)
    category: CategoryEnum
    target: int = Field(ge=1)


class GoalUpdate(BaseModel):
    target: int = Field(ge=1)


class GoalRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    year: int
    category: CategoryEnum
    target: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GoalProgress(GoalRead):
    current: int
    percentage: float
