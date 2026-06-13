import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.enums import CategoryEnum, PlaceTypeEnum


class EntryCreate(BaseModel):
    category: CategoryEnum
    title: str
    date: date
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    saga_name: Optional[str] = None
    saga_part: Optional[int] = None
    season_number: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    place_type: Optional[PlaceTypeEnum] = None

    @model_validator(mode="after")
    def validate_category_fields(self):
        cat = self.category
        if self.rating is not None and cat == CategoryEnum.event:
            raise ValueError("rating not allowed for event entries")
        if self.season_number is not None and cat != CategoryEnum.movie_series:
            raise ValueError("season_number only allowed for movie_series entries")
        if self.place_type is not None and cat != CategoryEnum.place:
            raise ValueError("place_type only allowed for place entries")
        if self.saga_name is not None and cat not in (CategoryEnum.movie_series, CategoryEnum.book):
            raise ValueError("saga_name only allowed for movie_series or book entries")
        if cat == CategoryEnum.city and not self.country:
            raise ValueError("country is required for city entries")
        if self.city is not None and cat != CategoryEnum.place:
            raise ValueError("city field only allowed for place entries")
        return self


class EntryUpdate(EntryCreate):
    pass


class EntryRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: CategoryEnum
    title: str
    date: date
    notes: Optional[str]
    created_at: datetime
    rating: Optional[int]
    saga_name: Optional[str]
    saga_part: Optional[int]
    season_number: Optional[int]
    country: Optional[str]
    city: Optional[str]
    place_type: Optional[PlaceTypeEnum]

    model_config = {"from_attributes": True}
