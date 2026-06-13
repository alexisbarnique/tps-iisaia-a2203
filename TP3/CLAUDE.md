# LifeTracker — TP3 IISAIA

Aplicación web de seguimiento de vida personal. Multi-usuario con JWT auth.

## Stack

- **Backend:** Python 3.11 + FastAPI, puerto 8000
- **Frontend:** Vue.js 3 + Vite, puerto 5173
- **Base de datos:** PostgreSQL en puerto 5433 (docker: `lifetracker-db`)
- **ORM:** SQLAlchemy 2.x + Alembic

## Comandos

```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Migraciones
cd backend && alembic upgrade head

# Tests
cd backend && pytest tests/ -v

# Base de datos (primera vez)
docker run -d --name lifetracker-db \
  -e POSTGRES_DB=lifetracker -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres -p 5433:5432 postgres:15
docker exec lifetracker-db psql -U postgres -c "CREATE DATABASE lifetracker_test;"
```

## Folder Map

### Backend

| Path | Responsabilidad |
|------|----------------|
| `backend/app/main.py` | Entry point FastAPI — CORS + registro de routers |
| `backend/app/config.py` | Settings via pydantic-settings (lee `.env`) |
| `backend/app/database.py` | Engine SQLAlchemy, `SessionLocal`, `Base`, `get_db` |
| `backend/app/routers/auth.py` | `POST /api/auth/register` y `/login` |
| `backend/app/routers/entries.py` | CRUD entradas (`GET`, `POST`, `PUT`, `DELETE /api/entries`) |
| `backend/app/routers/summaries.py` | Resúmenes mensual y anual (`/api/summaries/...`) |
| `backend/app/routers/metadata.py` | Listas de categorías y place types (sin auth) |
| `backend/app/models/user.py` | Modelo SQLAlchemy `User` |
| `backend/app/models/entry.py` | Modelo SQLAlchemy `Entry` + enums `CategoryEnum`, `PlaceTypeEnum` |
| `backend/app/schemas/auth.py` | Pydantic `RegisterRequest`, `LoginRequest`, `TokenResponse` |
| `backend/app/schemas/entry.py` | Pydantic `EntryCreate`, `EntryRead` + validación cruzada por categoría |
| `backend/app/schemas/summary.py` | Pydantic `MonthlySummary`, `AnnualSummary`, `Highlight` |
| `backend/app/auth/jwt.py` | Encode/decode JWT + hash/verify password (bcrypt) |
| `backend/app/auth/deps.py` | Dependency `get_current_user` — extrae `user_id` del token |
| `backend/alembic/versions/` | Migraciones — nunca editar las aplicadas, solo crear nuevas |
| `backend/scripts/add_entry_cli.py` | CLI interactivo del skill `/add-entry` |
| `backend/tests/` | Tests pytest (`conftest.py` + `test_*.py`) |

### Frontend

| Path | Responsabilidad |
|------|----------------|
| `frontend/src/main.js` | Bootstrap de Vue + Pinia + Router |
| `frontend/src/App.vue` | Root component — `<NavBar>` + `<RouterView>` |
| `frontend/src/api/client.js` | Instancia Axios — interceptor JWT en request, redirect `/login` en 401 |
| `frontend/src/router/index.js` | Rutas + guard global (redirige a `/login` si no autenticado) |
| `frontend/src/stores/auth.js` | Pinia — token en `localStorage`, `login`, `register`, `logout` |
| `frontend/src/stores/entries.js` | Pinia — CRUD entradas, caché local |
| `frontend/src/views/LoginView.vue` | Login y registro |
| `frontend/src/views/DashboardView.vue` | Resumen del mes actual |
| `frontend/src/views/EntriesListView.vue` | Lista de entradas con filtros por categoría/fecha |
| `frontend/src/views/EntryFormView.vue` | Formulario crear/editar entrada (ruta compartida) |
| `frontend/src/views/MonthlySummaryView.vue` | Resumen mensual por elección de mes/año |
| `frontend/src/views/AnnualSummaryView.vue` | Wrapped anual — totales + desglose mes a mes |
| `frontend/src/components/NavBar.vue` | Barra de navegación sticky |
| `frontend/src/components/EntryCard.vue` | Tarjeta de entrada con acciones editar/eliminar |
| `frontend/src/components/SummaryBlock.vue` | Bloque de highlight por categoría (usado en dashboard y resúmenes) |

## Workflow

- Cambios en modelos → crear migración con `alembic revision --autogenerate -m "descripción"` y aplicar con `alembic upgrade head`. Nunca editar migraciones ya aplicadas.
- Antes de un PR, correr `cd backend && pytest tests/ -v` y verificar que pasan los 19 tests.
- Cambios en endpoints → asegurar que cada uno declare `response_model` y `status_code` explícitos.

## Skill disponible

`/add-entry` — registra una nueva entrada desde la terminal (requiere backend corriendo)

## Variables de entorno

Copiar `backend/.env.example` a `backend/.env` y completar:
- `DATABASE_URL` — PostgreSQL connection string (puerto 5433)
- `TEST_DATABASE_URL` — base de datos para tests
- `SECRET_KEY` — clave secreta para JWT (generá una random)
