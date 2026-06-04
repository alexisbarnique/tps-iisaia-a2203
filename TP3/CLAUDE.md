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

## Skill disponible

`/add-entry` — registra una nueva entrada desde la terminal (requiere backend corriendo)

## Variables de entorno

Copiar `backend/.env.example` a `backend/.env` y completar:
- `DATABASE_URL` — PostgreSQL connection string (puerto 5433)
- `TEST_DATABASE_URL` — base de datos para tests
- `SECRET_KEY` — clave secreta para JWT (generá una random)
