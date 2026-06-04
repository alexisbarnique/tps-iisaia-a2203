from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.database import get_db
from app.models.entry import Entry
from app.models.user import User
from app.schemas.summary import MonthlySummary, AnnualSummary, Highlight, MonthBlock
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/summaries", tags=["summaries"])

def build_highlight(category: str, entries: list) -> Highlight:
    if category == "city":
        countries = list(set(e.country for e in entries if e.country))
        items = [{"city": e.title, "country": e.country} for e in entries]
        return Highlight(category=category, count=len(entries), items=items,
                         countries=len(countries), cities=len(entries))
    if category == "place":
        by_type: dict[str, int] = {}
        for e in entries:
            pt = e.place_type.value if e.place_type else "other"
            by_type[pt] = by_type.get(pt, 0) + 1
        items = [{"title": e.title, "place_type": e.place_type.value if e.place_type else None, "city": e.city} for e in entries]
        return Highlight(category=category, count=len(entries), items=items, by_type=by_type)
    # event, movie_series, book
    items = []
    for e in entries:
        item: dict = {"title": e.title}
        if e.saga_name:
            item["saga_name"] = e.saga_name
            item["saga_part"] = e.saga_part
        if e.season_number:
            item["season_number"] = e.season_number
        if e.rating:
            item["rating"] = e.rating
        items.append(item)
    return Highlight(category=category, count=len(entries), items=items)

def group_by_category(entries: list) -> dict[str, list]:
    groups: dict[str, list] = {}
    for e in entries:
        cat = e.category.value
        groups.setdefault(cat, []).append(e)
    return groups

@router.get("/monthly/{year}/{month}", response_model=MonthlySummary)
def monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        extract("year", Entry.date) == year,
        extract("month", Entry.date) == month,
    ).all()
    if not entries:
        return MonthlySummary(year=year, month=month, highlights=[])
    groups = group_by_category(entries)
    highlights = [build_highlight(cat, ents) for cat, ents in groups.items()]
    return MonthlySummary(year=year, month=month, highlights=highlights)

@router.get("/annual/{year}", response_model=AnnualSummary)
def annual_summary(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        extract("year", Entry.date) == year,
    ).all()
    if not entries:
        return AnnualSummary(year=year, months=[], totals={})

    by_month: dict[int, list] = {}
    for e in entries:
        by_month.setdefault(e.date.month, []).append(e)

    months = []
    for month in sorted(by_month.keys()):
        groups = group_by_category(by_month[month])
        highlights = [build_highlight(cat, ents) for cat, ents in groups.items()]
        months.append(MonthBlock(month=month, highlights=highlights))

    totals: dict[str, int] = {}
    for e in entries:
        cat = e.category.value
        totals[cat] = totals.get(cat, 0) + 1
    city_entries = [e for e in entries if e.category.value == "city"]
    if city_entries:
        totals["city_countries"] = len(set(e.country for e in city_entries if e.country))

    return AnnualSummary(year=year, months=months, totals=totals)
