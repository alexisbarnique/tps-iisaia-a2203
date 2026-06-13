from fastapi import APIRouter

from app.enums import CategoryEnum, PlaceTypeEnum

router = APIRouter(prefix="/api", tags=["metadata"])


@router.get("/categories", response_model=list[dict], status_code=200)
def get_categories():
    return [{"value": c.value, "label": c.value.replace("_", " ").title()} for c in CategoryEnum]


@router.get("/place-types", response_model=list[dict], status_code=200)
def get_place_types():
    return [{"value": p.value, "label": p.value.title()} for p in PlaceTypeEnum]
