from fastapi import APIRouter
from app.models.entry import CategoryEnum, PlaceTypeEnum

router = APIRouter(prefix="/api", tags=["metadata"])

@router.get("/categories")
def get_categories():
    return [{"value": c.value, "label": c.value.replace("_", " ").title()} for c in CategoryEnum]

@router.get("/place-types")
def get_place_types():
    return [{"value": p.value, "label": p.value.title()} for p in PlaceTypeEnum]
