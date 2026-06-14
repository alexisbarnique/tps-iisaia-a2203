import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.entry import Entry
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalRead, GoalProgress

router = APIRouter(prefix="/api/goals", tags=["goals"])


def _build_progress(goal: Goal, db: Session) -> GoalProgress:
    current = (
        db.query(func.count(Entry.id))
        .filter(
            Entry.user_id == goal.user_id,
            Entry.category == goal.category,
            extract("year", Entry.date) == goal.year,
        )
        .scalar()
        or 0
    )
    percentage = min(round(current / goal.target * 100, 1), 100.0) if goal.target > 0 else 0.0
    base = GoalRead.model_validate(goal)
    return GoalProgress(**base.model_dump(), current=current, percentage=percentage)


@router.get("", response_model=list[GoalProgress], status_code=200)
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.year.desc(), Goal.category)
        .all()
    )
    return [_build_progress(g, db) for g in goals]


@router.post("", response_model=GoalRead, status_code=201)
def create_goal(
    body: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = Goal(user_id=current_user.id, **body.model_dump())
    db.add(goal)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Goal for this category and year already exists",
        )
    db.refresh(goal)
    return goal


@router.put("/{goal_id}", response_model=GoalRead, status_code=200)
def update_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.target = body.target
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", response_model=None, status_code=204)
def delete_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
