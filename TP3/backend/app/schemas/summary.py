from pydantic import BaseModel
from typing import Any

class Highlight(BaseModel):
    category: str
    count: int
    items: list[Any]
    countries: int | None = None
    cities: int | None = None
    by_type: dict[str, int] | None = None

class MonthlySummary(BaseModel):
    year: int
    month: int
    highlights: list[Highlight]

class MonthBlock(BaseModel):
    month: int
    highlights: list[Highlight]

class AnnualSummary(BaseModel):
    year: int
    months: list[MonthBlock]
    totals: dict[str, int]
