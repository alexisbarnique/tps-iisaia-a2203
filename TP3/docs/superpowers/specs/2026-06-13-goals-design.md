# Goals / Metas — Design Spec

**Date:** 2026-06-13  
**Status:** Approved  
**Scope:** Feature 1 of LifeTracker TP3

---

## Summary

Users can set annual numeric goals tied to a category (e.g., "read 12 books this year"). Progress is computed automatically by counting matching entries — no manual input required. Goals appear on a dedicated `/goals` page and as a compact widget on the Dashboard.

---

## Decisions Made

| Question | Decision |
|----------|----------|
| Time period | Annual only (per year) |
| Progress tracking | Automatic — count of entries matching category + year |
| Where goals appear | Dedicated `/goals` page + compact section on Dashboard |
| Goal card style | Circular SVG progress indicator with count (X / Y) |
| Dashboard widget style | Compact chips below monthly summary; hidden if no goals |
| Architecture | Category-linked goals (one per user/year/category) |

---

## Data Model

**Table: `goals`**

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, default uuid4 |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE, NOT NULL |
| `year` | INTEGER | NOT NULL |
| `category` | CategoryEnum | NOT NULL |
| `target` | INTEGER | NOT NULL, ≥ 1 |
| `created_at` | TIMESTAMPTZ | server default now() |

**Unique constraint:** `(user_id, year, category)` — one goal per category per year per user.

Progress is **not stored** — it is computed at query time via a COUNT subquery on `entries` filtered by `user_id`, `year`, and `category`.

No changes to the `entries` table or `enums.py`.

---

## Pydantic Schemas

```python
# GoalCreate — request body for POST
class GoalCreate(BaseModel):
    year: int  # ge=2020, le=2100
    category: CategoryEnum
    target: int  # ge=1

# GoalUpdate — request body for PUT (year and category are immutable)
class GoalUpdate(BaseModel):
    target: int  # ge=1

# GoalRead — base response (no progress)
class GoalRead(BaseModel):
    id: UUID
    user_id: UUID
    year: int
    category: CategoryEnum
    target: int
    created_at: datetime
    model_config = {"from_attributes": True}

# GoalProgress — response for list endpoint (includes computed fields)
class GoalProgress(GoalRead):
    current: int       # count of matching entries
    percentage: float  # min(current / target * 100, 100.0)
```

---

## API Endpoints

All endpoints require JWT auth (`Authorization: Bearer <token>`).

| Method | Path | Request | Response | Status |
|--------|------|---------|----------|--------|
| GET | `/api/goals` | — | `list[GoalProgress]` | 200 |
| POST | `/api/goals` | `GoalCreate` | `GoalRead` | 201 |
| PUT | `/api/goals/{id}` | `GoalUpdate` | `GoalRead` | 200 |
| DELETE | `/api/goals/{id}` | — | — | 204 |

**Error cases:**
- `POST` with duplicate `(year, category)` for same user → `409 Conflict`
- `PUT`/`DELETE` on another user's goal → `404 Not Found` (no ownership leak)
- Missing/invalid token → `403`/`401` (handled by existing `get_current_user` dependency)

**Progress computation:** `GET /api/goals` uses a single SQLAlchemy query with a correlated subquery (no N+1). The Dashboard calls the same endpoint and filters to `year == current_year` on the frontend.

---

## Frontend

### New Files

| File | Responsibility |
|------|----------------|
| `src/stores/goals.js` | Pinia store — CRUD + local cache with `current`/`percentage` |
| `src/views/GoalsView.vue` | Goals list with GoalCard components + "Nueva meta" button |
| `src/views/GoalFormView.vue` | Create/edit form — category selector, year, target input |
| `src/components/GoalCard.vue` | Card with SVG circular progress, `X / Y` count, category label |

### New Routes

```
/goals            → GoalsView      (authenticated)
/goals/new        → GoalFormView   (authenticated)
/goals/:id/edit   → GoalFormView   (authenticated, shared route)
```

### Modified Files

- **`NavBar.vue`** — add "Metas" link between Entradas and Resúmenes
- **`DashboardView.vue`** — add "🎯 Metas {year}" section below monthly summary:
  - Renders compact chips (mini circle SVG + `X/Y` label) for each goal of the current year
  - Completed goals (100%) render with green accent color
  - Section is hidden (`v-if`) when user has no goals for the current year

---

## Visual Design

**GoalCard** (on `/goals` page):
- Circular SVG progress ring (58px), rotated -90° so progress starts at top
- Track color: `#222`, fill color: `#7c6bff`, completed fill: `#27c97a`
- Shows: category emoji + label, goal description ("Leer 12 libros este año"), `X / Y` count
- Edit and delete actions

**Dashboard widget chip:**
- Mini circular SVG (32px) + `X/Y` text inline
- Row of chips, wraps on small screens
- "Ver todas las metas" link at bottom of section

---

## Testing

File: `backend/tests/test_goals.py`

| Test | Scenario |
|------|----------|
| `test_create_goal_ok` | POST creates goal, returns 201 with all fields |
| `test_list_goals_returns_progress` | GET returns correct `current` and `percentage` based on existing entries |
| `test_update_goal_ok` | PUT updates target, returns 200 |
| `test_delete_goal_ok` | DELETE returns 204; goal absent from subsequent GET |
| `test_create_goal_duplicate_returns_409` | Same user/year/category → 409 |
| `test_update_goal_other_user_returns_404` | Cannot edit another user's goal |
| `test_delete_goal_other_user_returns_404` | Cannot delete another user's goal |
| `test_create_goal_unauthenticated_returns_403` | No token → 403 |

All tests use the `setup_db` + `db` fixtures from `conftest.py` against `lifetracker_test` (real PostgreSQL, no mocks).

---

## Out of Scope

- Monthly goals (annual only)
- Manual progress override
- Goals linked to subcategory filters (e.g., specific saga)
- Notifications when a goal is reached (separate feature)
- Goal history across years (the list shows all years; no archiving)
