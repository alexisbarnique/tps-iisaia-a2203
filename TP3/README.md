# LifeTracker ✦

> *"Juro solemnemente que mis intenciones son guardar cada momento."*

Aplicación web de seguimiento de vida personal. Registrá conciertos, libros, películas, ciudades y lugares — y recibí un resumen anual estilo Spotify Wrapped de todo lo que viviste.

**TP3 — IISAIA | CEIA Bimestre 5**  
**Autora:** Alexis Barniquez

---

## Demo

| Login | Registros | Resumen anual |
|---|---|---|
| ![Login](docs/screenshots/login.png) | ![Registros](docs/screenshots/entries.png) | ![Anual](docs/screenshots/annual.png) |

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Base de datos | PostgreSQL + SQLAlchemy 2.x + Alembic |
| Frontend | Vue.js 3 + Vite + Pinia |
| Auth | JWT (Bearer token, 7 días) |
| Tests | pytest (27 tests) |

---

## Características

### Categorías de registro

| Categoría | Campos extra |
|---|---|
| 🎵 Evento / Concierto | título, fecha, notas |
| 🎬 Película / Serie | saga, parte, temporada, calificación |
| 📚 Libro | saga, parte, calificación |
| 🗺️ Ciudad | país |
| 🏛️ Lugar | tipo (restaurante/café/museo/bar/parque), ciudad, país, calificación |

### Metas anuales

Definí objetivos anuales por categoría (ej. "leer 12 libros este año") y seguí tu progreso automáticamente. El sistema cuenta las entradas registradas y calcula el porcentaje de avance — sin carga manual.

- Una meta por categoría por año
- Progreso en tiempo real basado en tus registros
- Visualización circular en `/goals` y widget compacto en el Dashboard
- Metas completadas se destacan en verde

### Resúmenes

- **Mensual:** elegís año y mes → ves todo lo que registraste ese período
- **Anual (Wrapped):** grid de totales + desglose mes a mes. Nunca muestra lo que *no* hiciste.

### Skill `/add-entry`

Registrá entradas desde la terminal con un flujo interactivo. El token JWT se guarda localmente — solo pedís credenciales la primera vez.

```
cd backend && python3 scripts/add_entry_cli.py
```

---

## Instalación

### Requisitos

- Python 3.11+
- Node.js 18+
- Docker

### 1. Base de datos

```bash
docker run -d --name lifetracker-db \
  -e POSTGRES_DB=lifetracker \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5433:5432 \
  postgres:15

docker exec lifetracker-db psql -U postgres -c "CREATE DATABASE lifetracker_test;"
```

### 2. Backend

```bash
cd backend
cp .env.example .env        # completar SECRET_KEY con algo random
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

La app queda disponible en `http://localhost:5173`.

---

## Variables de entorno

Copiar `backend/.env.example` a `backend/.env`:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/lifetracker
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/lifetracker_test
SECRET_KEY=tu-clave-secreta-aqui
```

---

## Tests

```bash
cd backend
pytest tests/ -v
```

```
tests/test_auth.py        4 passed
tests/test_entries.py     8 passed
tests/test_goals.py       8 passed
tests/test_metadata.py    2 passed
tests/test_summaries.py   5 passed
─────────────────────────────────
27 passed
```

---

## API — Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Crear cuenta |
| POST | `/api/auth/login` | Obtener token JWT |
| GET | `/api/entries` | Listar entradas (filtros: category, year, month) |
| POST | `/api/entries` | Crear entrada |
| PUT | `/api/entries/{id}` | Editar entrada |
| DELETE | `/api/entries/{id}` | Eliminar entrada |
| GET | `/api/summaries/monthly/{year}/{month}` | Resumen mensual |
| GET | `/api/summaries/annual/{year}` | Resumen anual |
| GET | `/api/goals` | Listar metas con progreso actual |
| POST | `/api/goals` | Crear meta anual por categoría |
| PUT | `/api/goals/{id}` | Editar objetivo numérico de una meta |
| DELETE | `/api/goals/{id}` | Eliminar meta |
| GET | `/api/categories` | Lista de categorías |
| GET | `/api/place-types` | Lista de tipos de lugar |

---

## Estructura del proyecto

```
TP3/
├── backend/
│   ├── app/
│   │   ├── models/        # SQLAlchemy: User, Entry, Goal
│   │   ├── schemas/       # Pydantic: validación por categoría, GoalProgress
│   │   ├── routers/       # endpoints: auth, entries, summaries, metadata, goals
│   │   └── auth/          # JWT: hash, token, dependency
│   ├── alembic/           # migraciones
│   ├── scripts/
│   │   └── add_entry_cli.py   # skill /add-entry
│   └── tests/             # 27 tests con TDD
├── frontend/
│   └── src/
│       ├── views/         # Login, Dashboard, Entries, Form, Summaries, Goals, GoalForm
│       ├── components/    # NavBar, EntryCard, SummaryBlock, GoalCard
│       ├── stores/        # Pinia: auth, entries, goals
│       └── api/           # axios con interceptor JWT
├── .claude/
│   ├── settings.json      # permisos de Claude Code
│   └── skills/
│       └── add-entry.md   # skill /add-entry
├── CLAUDE.md
└── rules.md
```

---

## Diseño

Temática Harry Potter — pergamino oscuro, dorado mágico.

```css
--color-bg:      #0d0d1a   /* noche en Hogwarts */
--color-gold:    #c9a84c   /* dorado mágico */
--color-crimson: #7b1f1f   /* burdeos Gryffindor */
--font-display:  'Cinzel', serif
--font-body:     'EB Garamond', serif
```
