# LifeTracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build LifeTracker — a full-stack personal life tracking web app with FastAPI backend, Vue.js 3 frontend, PostgreSQL persistence, JWT auth, and a `/add-entry` Claude Code skill.

**Architecture:** Decoupled — Vite dev server (port 5173) for Vue.js, FastAPI (port 8000) as REST API, PostgreSQL for persistence. JWT tokens (7-day expiry, no refresh). All summaries computed on-demand. Harry Potter dark aesthetic via CSS custom properties.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, psycopg2-binary, python-jose[cryptography], passlib[bcrypt], python-dotenv, pytest, httpx; Vue.js 3, Vite, Pinia, Vue Router 4, axios

---

## File Map

```
TP3/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app + CORS + routers
│   │   ├── config.py                # Settings from env vars
│   │   ├── database.py              # SQLAlchemy engine + session + Base
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User model
│   │   │   └── entry.py             # Entry model + CategoryEnum + PlaceTypeEnum
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # LoginRequest, RegisterRequest, TokenResponse
│   │   │   ├── entry.py             # EntryCreate, EntryUpdate, EntryRead
│   │   │   └── summary.py           # MonthlySummary, AnnualSummary response shapes
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py               # hash/verify password, create/decode token
│   │   │   └── deps.py              # get_current_user FastAPI dependency
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py              # POST /api/auth/register, /login
│   │       ├── entries.py           # CRUD /api/entries
│   │       ├── summaries.py         # GET /api/summaries/monthly, /annual
│   │       └── metadata.py          # GET /api/categories, /place-types
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── add_entry_cli.py         # /add-entry CLI tool
│   ├── tests/
│   │   ├── conftest.py              # TestClient, DB session fixture
│   │   ├── test_auth.py
│   │   ├── test_entries.py
│   │   ├── test_summaries.py
│   │   └── test_metadata.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js
│       ├── api/client.js            # axios instance + JWT interceptor
│       ├── stores/
│       │   ├── auth.js              # Pinia: token, login, register, logout
│       │   └── entries.js           # Pinia: entries cache + CRUD
│       ├── assets/main.css          # HP theme: CSS variables, fonts, base
│       ├── components/
│       │   ├── NavBar.vue
│       │   ├── EntryCard.vue
│       │   └── SummaryBlock.vue
│       └── views/
│           ├── LoginView.vue
│           ├── DashboardView.vue
│           ├── EntriesListView.vue
│           ├── EntryFormView.vue
│           ├── MonthlySummaryView.vue
│           └── AnnualSummaryView.vue
├── .claude/
│   ├── settings.json
│   └── skills/
│       └── add-entry.md
├── CLAUDE.md
└── rules.md
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `TP3/backend/requirements.txt`
- Create: `TP3/backend/.env.example`
- Create: `TP3/backend/app/__init__.py`
- Create: `TP3/backend/app/config.py`
- Create: `TP3/backend/app/database.py`
- Create: `TP3/backend/app/main.py`

- [ ] **Step 1: Create the TP3/backend directory structure**

```bash
mkdir -p TP3/backend/app/models TP3/backend/app/schemas \
         TP3/backend/app/auth TP3/backend/app/routers \
         TP3/backend/tests TP3/backend/scripts
touch TP3/backend/app/__init__.py \
      TP3/backend/app/models/__init__.py \
      TP3/backend/app/schemas/__init__.py \
      TP3/backend/app/auth/__init__.py \
      TP3/backend/app/routers/__init__.py \
      TP3/backend/tests/__init__.py
```

- [ ] **Step 2: Write requirements.txt**

`TP3/backend/requirements.txt`:
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pydantic[email]==2.7.1
pydantic-settings==2.2.1
pytest==8.2.0
httpx==0.27.0
```

- [ ] **Step 3: Write .env.example**

`TP3/backend/.env.example`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lifetracker
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lifetracker_test
SECRET_KEY=change-this-to-a-random-secret-key
```

Copy to `.env` and fill in real values:
```bash
cp TP3/backend/.env.example TP3/backend/.env
```

- [ ] **Step 4: Write config.py**

`TP3/backend/app/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ""
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

Note: add `pydantic-settings==2.2.1` to requirements.txt.

- [ ] **Step 5: Write database.py**

`TP3/backend/app/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 6: Write main.py (initial, no routers yet)**

`TP3/backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: Start PostgreSQL and verify it runs**

```bash
docker run -d --name lifetracker-db \
  -e POSTGRES_DB=lifetracker \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# also create test database
docker exec lifetracker-db psql -U postgres -c "CREATE DATABASE lifetracker_test;"
```

- [ ] **Step 8: Install dependencies and verify the app starts**

```bash
cd TP3/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Expected: `Application startup complete.`
Visit `http://localhost:8000/api/health` → `{"status":"ok"}`

- [ ] **Step 9: Commit**

```bash
git add TP3/backend/
git commit -m "feat: TP3 backend scaffolding"
```

---

## Task 2: Database Models

**Files:**
- Create: `TP3/backend/app/models/user.py`
- Create: `TP3/backend/app/models/entry.py`

- [ ] **Step 1: Write user.py**

`TP3/backend/app/models/user.py`:
```python
import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: Write entry.py**

`TP3/backend/app/models/entry.py`:
```python
import uuid
import enum
from sqlalchemy import String, Integer, Date, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class CategoryEnum(enum.Enum):
    event = "event"
    movie_series = "movie_series"
    book = "book"
    city = "city"
    place = "place"

class PlaceTypeEnum(enum.Enum):
    restaurant = "restaurant"
    cafe = "cafe"
    museum = "museum"
    bar = "bar"
    park = "park"
    other = "other"

class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[CategoryEnum] = mapped_column(Enum(CategoryEnum), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    date = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    # movie_series, book, place
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # movie_series, book
    saga_name: Mapped[str | None] = mapped_column(String, nullable=True)
    saga_part: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # movie_series only
    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # city, place
    country: Mapped[str | None] = mapped_column(String, nullable=True)

    # place only
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    place_type: Mapped[PlaceTypeEnum | None] = mapped_column(Enum(PlaceTypeEnum), nullable=True)
```

- [ ] **Step 3: Update models/__init__.py to export both models**

`TP3/backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.entry import Entry, CategoryEnum, PlaceTypeEnum
```

- [ ] **Step 4: Commit**

```bash
git add TP3/backend/app/models/
git commit -m "feat: SQLAlchemy models for User and Entry"
```

---

## Task 3: Alembic Setup + Initial Migration

**Files:**
- Create: `TP3/backend/alembic.ini`
- Modify: `TP3/backend/alembic/env.py`
- Create: `TP3/backend/alembic/versions/001_initial.py` (generated)

- [ ] **Step 1: Initialize Alembic**

```bash
cd TP3/backend
alembic init alembic
```

- [ ] **Step 2: Update alembic/env.py to use app models and DATABASE_URL**

`TP3/backend/alembic/env.py` (replace the entire file):
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.database import Base
import app.models  # noqa: F401 — registers all models with Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 3: Generate initial migration**

```bash
cd TP3/backend
alembic revision --autogenerate -m "initial"
```

Expected: creates `alembic/versions/xxxx_initial.py`

- [ ] **Step 4: Apply migration**

```bash
alembic upgrade head
```

Expected output ends with: `Running upgrade  -> xxxx, initial`

- [ ] **Step 5: Verify tables exist**

```bash
docker exec lifetracker-db psql -U postgres -d lifetracker -c "\dt"
```

Expected: tables `users`, `entries`, `alembic_version`

- [ ] **Step 6: Commit**

```bash
git add TP3/backend/alembic/
git commit -m "feat: Alembic migrations setup with initial schema"
```

---

## Task 4: JWT Auth Utilities

**Files:**
- Create: `TP3/backend/app/auth/jwt.py`
- Create: `TP3/backend/app/auth/deps.py`
- Create: `TP3/backend/app/schemas/auth.py`

- [ ] **Step 1: Write jwt.py**

`TP3/backend/app/auth/jwt.py`:
```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.secret_key, algorithm="HS256")

def decode_access_token(token: str) -> str:
    """Returns user_id (str) or raises JWTError."""
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return payload["sub"]
```

- [ ] **Step 2: Write deps.py**

`TP3/backend/app/auth/deps.py`:
```python
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from app.auth.jwt import decode_access_token
from app.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 3: Write schemas/auth.py**

`TP3/backend/app/schemas/auth.py`:
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- [ ] **Step 4: Commit**

```bash
git add TP3/backend/app/auth/ TP3/backend/app/schemas/auth.py
git commit -m "feat: JWT auth utilities and Pydantic auth schemas"
```

---

## Task 5: Auth Router + Tests

**Files:**
- Create: `TP3/backend/app/routers/auth.py`
- Modify: `TP3/backend/app/main.py`
- Create: `TP3/backend/tests/conftest.py`
- Create: `TP3/backend/tests/test_auth.py`

- [ ] **Step 1: Write the failing tests**

`TP3/backend/tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import settings

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)   # clean slate (handles re-runs)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    app.dependency_overrides[get_db] = lambda: session
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()

@pytest.fixture()
def client(db):
    return TestClient(app)
```

`TP3/backend/tests/test_auth.py`:
```python
def test_register_creates_user(client):
    res = client.post("/api/auth/register", json={"email": "test@example.com", "password": "secret"})
    assert res.status_code == 201
    assert res.json()["email"] == "test@example.com"

def test_register_duplicate_email_fails(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "secret"})
    res = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "secret"})
    assert res.status_code == 409

def test_login_returns_token(client):
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "secret"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"

def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "correct"})
    res = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert res.status_code == 401
```

- [ ] **Step 2: Run tests — expect ImportError or 404 (router not wired)**

```bash
cd TP3/backend
pytest tests/test_auth.py -v
```

Expected: FAIL (router doesn't exist yet)

- [ ] **Step 3: Write routers/auth.py**

`TP3/backend/app/routers/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.auth.jwt import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = User(email=req.email, password=hash_password(req.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"email": user.email, "id": str(user.id)}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(str(user.id)))
```

- [ ] **Step 4: Register the router in main.py**

`TP3/backend/app/main.py` (replace full file):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
pytest tests/test_auth.py -v
```

Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add TP3/backend/app/routers/auth.py TP3/backend/app/main.py TP3/backend/tests/
git commit -m "feat: auth endpoints with register and login + tests"
```

---

## Task 6: Entry Schemas

**Files:**
- Create: `TP3/backend/app/schemas/entry.py`

- [ ] **Step 1: Write entry schemas with category validation**

`TP3/backend/app/schemas/entry.py`:
```python
import uuid
from pydantic import BaseModel, model_validator, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

class CategoryEnum(str, Enum):
    event = "event"
    movie_series = "movie_series"
    book = "book"
    city = "city"
    place = "place"

class PlaceTypeEnum(str, Enum):
    restaurant = "restaurant"
    cafe = "cafe"
    museum = "museum"
    bar = "bar"
    park = "park"
    other = "other"

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
```

- [ ] **Step 2: Commit**

```bash
git add TP3/backend/app/schemas/entry.py
git commit -m "feat: Entry Pydantic schemas with category validation"
```

---

## Task 7: Entries Router + Tests

**Files:**
- Create: `TP3/backend/app/routers/entries.py`
- Modify: `TP3/backend/app/main.py`
- Create: `TP3/backend/tests/test_entries.py`

- [ ] **Step 1: Write failing tests**

`TP3/backend/tests/test_entries.py`:
```python
import pytest

@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/register", json={"email": "entries@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "entries@example.com", "password": "secret"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_event_entry(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "event", "title": "Coldplay", "date": "2025-03-15"
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["title"] == "Coldplay"

def test_create_book_with_saga(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "book", "title": "El nombre del viento",
        "date": "2025-03-10", "saga_name": "Crónica del Asesino de Reyes", "saga_part": 1, "rating": 5
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["saga_name"] == "Crónica del Asesino de Reyes"

def test_create_city_entry(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "city", "title": "París", "date": "2025-07-01", "country": "Francia"
    }, headers=auth_headers)
    assert res.status_code == 201

def test_invalid_category_field_rejected(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "event", "title": "Concert", "date": "2025-01-01", "rating": 5
    }, headers=auth_headers)
    assert res.status_code == 422

def test_list_entries_returns_only_own(client, auth_headers):
    client.post("/api/entries", json={"category": "event", "title": "Show", "date": "2025-01-01"}, headers=auth_headers)
    res = client.get("/api/entries", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

def test_delete_entry(client, auth_headers):
    res = client.post("/api/entries", json={"category": "event", "title": "ToDelete", "date": "2025-01-01"}, headers=auth_headers)
    entry_id = res.json()["id"]
    del_res = client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_update_entry(client, auth_headers):
    res = client.post("/api/entries", json={"category": "event", "title": "Original", "date": "2025-01-01"}, headers=auth_headers)
    entry_id = res.json()["id"]
    put_res = client.put(f"/api/entries/{entry_id}", json={
        "category": "event", "title": "Updated", "date": "2025-01-01"
    }, headers=auth_headers)
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Updated"

def test_unauthenticated_request_rejected(client):
    res = client.get("/api/entries")
    assert res.status_code == 403
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/test_entries.py -v
```

Expected: FAIL (router not registered)

- [ ] **Step 3: Write routers/entries.py**

`TP3/backend/app/routers/entries.py`:
```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.entry import Entry, CategoryEnum
from app.models.user import User
from app.schemas.entry import EntryCreate, EntryRead
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/entries", tags=["entries"])

@router.get("", response_model=list[EntryRead])
def list_entries(
    category: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Entry).filter(Entry.user_id == current_user.id)
    if category:
        q = q.filter(Entry.category == CategoryEnum[category])
    if year:
        from sqlalchemy import extract
        q = q.filter(extract("year", Entry.date) == year)
    if month:
        from sqlalchemy import extract
        q = q.filter(extract("month", Entry.date) == month)
    return q.order_by(Entry.date.desc()).all()

@router.post("", response_model=EntryRead, status_code=201)
def create_entry(
    body: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = Entry(user_id=current_user.id, **body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/{entry_id}", response_model=EntryRead)
def get_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=EntryRead)
def update_entry(
    entry_id: uuid.UUID,
    body: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    for field, value in body.model_dump().items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
```

- [ ] **Step 4: Add router to main.py**

`TP3/backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
pytest tests/test_entries.py -v
```

Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
git add TP3/backend/app/routers/entries.py TP3/backend/app/main.py TP3/backend/tests/test_entries.py
git commit -m "feat: entries CRUD endpoints + tests"
```

---

## Task 8: Summary Router + Tests

**Files:**
- Create: `TP3/backend/app/schemas/summary.py`
- Create: `TP3/backend/app/routers/summaries.py`
- Modify: `TP3/backend/app/main.py`
- Create: `TP3/backend/tests/test_summaries.py`

- [ ] **Step 1: Write summary schemas**

`TP3/backend/app/schemas/summary.py`:
```python
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
```

- [ ] **Step 2: Write failing tests**

`TP3/backend/tests/test_summaries.py`:
```python
import pytest

@pytest.fixture()
def auth_headers_with_data(client):
    client.post("/api/auth/register", json={"email": "summary@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "summary@example.com", "password": "secret"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # seed entries in March 2025
    client.post("/api/entries", json={"category": "book", "title": "Dune", "date": "2025-03-05"}, headers=headers)
    client.post("/api/entries", json={"category": "book", "title": "1984", "date": "2025-03-20"}, headers=headers)
    client.post("/api/entries", json={"category": "city", "title": "Madrid", "date": "2025-03-10", "country": "España"}, headers=headers)
    client.post("/api/entries", json={"category": "city", "title": "Barcelona", "date": "2025-03-12", "country": "España"}, headers=headers)
    return headers

def test_monthly_summary_returns_only_categories_with_entries(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2025/3", headers=auth_headers_with_data)
    assert res.status_code == 200
    data = res.json()
    assert data["year"] == 2025
    assert data["month"] == 3
    categories = [h["category"] for h in data["highlights"]]
    assert "book" in categories
    assert "city" in categories
    assert "event" not in categories  # no events registered

def test_monthly_summary_empty_period_returns_empty_highlights(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2024/1", headers=auth_headers_with_data)
    assert res.status_code == 200
    assert res.json()["highlights"] == []

def test_monthly_city_summary_counts_countries(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2025/3", headers=auth_headers_with_data)
    city_highlight = next(h for h in res.json()["highlights"] if h["category"] == "city")
    assert city_highlight["countries"] == 1
    assert city_highlight["cities"] == 2

def test_annual_summary_groups_by_month(client, auth_headers_with_data):
    res = client.get("/api/summaries/annual/2025", headers=auth_headers_with_data)
    assert res.status_code == 200
    data = res.json()
    assert data["year"] == 2025
    assert len(data["months"]) >= 1
    assert data["months"][0]["month"] == 3

def test_annual_totals_count_all_entries(client, auth_headers_with_data):
    res = client.get("/api/summaries/annual/2025", headers=auth_headers_with_data)
    totals = res.json()["totals"]
    assert totals.get("book") == 2
    assert totals.get("city") == 2
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
pytest tests/test_summaries.py -v
```

- [ ] **Step 4: Write routers/summaries.py**

`TP3/backend/app/routers/summaries.py`:
```python
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
```

- [ ] **Step 5: Add router to main.py**

`TP3/backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries, summaries

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(summaries.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Run tests — expect PASS**

```bash
pytest tests/test_summaries.py -v
```

Expected: 5 passed

- [ ] **Step 7: Commit**

```bash
git add TP3/backend/app/routers/summaries.py TP3/backend/app/schemas/summary.py \
        TP3/backend/app/main.py TP3/backend/tests/test_summaries.py
git commit -m "feat: summary endpoints (monthly + annual) + tests"
```

---

## Task 9: Metadata Router + Tests

**Files:**
- Create: `TP3/backend/app/routers/metadata.py`
- Modify: `TP3/backend/app/main.py`
- Create: `TP3/backend/tests/test_metadata.py`

- [ ] **Step 1: Write failing tests**

`TP3/backend/tests/test_metadata.py`:
```python
def test_categories_returns_all_five(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    values = [c["value"] for c in res.json()]
    assert set(values) == {"event", "movie_series", "book", "city", "place"}

def test_place_types_returns_six(client):
    res = client.get("/api/place-types")
    assert res.status_code == 200
    values = [p["value"] for p in res.json()]
    assert set(values) == {"restaurant", "cafe", "museum", "bar", "park", "other"}
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/test_metadata.py -v
```

- [ ] **Step 3: Write routers/metadata.py**

`TP3/backend/app/routers/metadata.py`:
```python
from fastapi import APIRouter
from app.models.entry import CategoryEnum, PlaceTypeEnum

router = APIRouter(prefix="/api", tags=["metadata"])

@router.get("/categories")
def get_categories():
    return [{"value": c.value, "label": c.value.replace("_", " ").title()} for c in CategoryEnum]

@router.get("/place-types")
def get_place_types():
    return [{"value": p.value, "label": p.value.title()} for p in PlaceTypeEnum]
```

- [ ] **Step 4: Add router to main.py**

`TP3/backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries, summaries, metadata

app = FastAPI(title="LifeTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(summaries.router)
app.include_router(metadata.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run all tests — expect PASS**

```bash
pytest tests/ -v
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add TP3/backend/app/routers/metadata.py TP3/backend/app/main.py TP3/backend/tests/test_metadata.py
git commit -m "feat: metadata endpoints + full test suite passing"
```

---

## Task 10: Frontend Scaffold

**Files:**
- Create: `TP3/frontend/` (via Vite)
- Create: `TP3/frontend/src/main.js`
- Create: `TP3/frontend/src/App.vue`
- Create: `TP3/frontend/src/router/index.js`
- Create: `TP3/frontend/src/api/client.js`
- Create: `TP3/frontend/src/stores/auth.js`
- Create: `TP3/frontend/src/stores/entries.js`

- [ ] **Step 1: Scaffold Vue project**

```bash
cd TP3
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install vue-router@4 pinia axios
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p TP3/frontend/src/views TP3/frontend/src/components \
         TP3/frontend/src/stores TP3/frontend/src/api \
         TP3/frontend/src/router
```

- [ ] **Step 3: Write src/api/client.js**

`TP3/frontend/src/api/client.js`:
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 4: Write src/stores/auth.js**

`TP3/frontend/src/stores/auth.js`:
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    await router.push('/dashboard')
  }

  async function register(email, password) {
    await api.post('/auth/register', { email, password })
    await login(email, password)
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, isAuthenticated, login, register, logout }
})
```

- [ ] **Step 5: Write src/stores/entries.js**

`TP3/frontend/src/stores/entries.js`:
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useEntriesStore = defineStore('entries', () => {
  const entries = ref([])

  async function fetchEntries(filters = {}) {
    const res = await api.get('/entries', { params: filters })
    entries.value = res.data
    return res.data
  }

  async function createEntry(data) {
    const res = await api.post('/entries', data)
    entries.value.unshift(res.data)
    return res.data
  }

  async function updateEntry(id, data) {
    const res = await api.put(`/entries/${id}`, data)
    const idx = entries.value.findIndex(e => e.id === id)
    if (idx !== -1) entries.value[idx] = res.data
    return res.data
  }

  async function deleteEntry(id) {
    await api.delete(`/entries/${id}`)
    entries.value = entries.value.filter(e => e.id !== id)
  }

  return { entries, fetchEntries, createEntry, updateEntry, deleteEntry }
})
```

- [ ] **Step 6: Write src/router/index.js**

`TP3/frontend/src/router/index.js`:
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/dashboard', component: () => import('@/views/DashboardView.vue') },
  { path: '/entries', component: () => import('@/views/EntriesListView.vue') },
  { path: '/entries/new', component: () => import('@/views/EntryFormView.vue') },
  { path: '/entries/:id/edit', component: () => import('@/views/EntryFormView.vue') },
  { path: '/summary/monthly', component: () => import('@/views/MonthlySummaryView.vue') },
  { path: '/summary/annual', component: () => import('@/views/AnnualSummaryView.vue') },
  { path: '/', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
})

export default router
```

- [ ] **Step 7: Write src/main.js**

`TP3/frontend/src/main.js`:
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 8: Write src/App.vue**

`TP3/frontend/src/App.vue`:
```vue
<template>
  <div id="app">
    <NavBar v-if="auth.isAuthenticated" />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'
const auth = useAuthStore()
</script>
```

- [ ] **Step 9: Start frontend and verify it loads**

```bash
cd TP3/frontend && npm run dev
```

Visit `http://localhost:5173` — should redirect to `/login` (page will be empty until LoginView is created, that's fine).

- [ ] **Step 10: Commit**

```bash
git add TP3/frontend/
git commit -m "feat: Vue.js frontend scaffold with Pinia, Router, and API client"
```

---

## Task 11: Harry Potter Theme CSS + NavBar

**Files:**
- Create: `TP3/frontend/src/assets/main.css`
- Create: `TP3/frontend/src/components/NavBar.vue`

- [ ] **Step 1: Write main.css**

`TP3/frontend/src/assets/main.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

:root {
  --color-bg: #0d0d1a;
  --color-surface: #1a1a2e;
  --color-surface-raised: #22223a;
  --color-border: #3d2b1f;
  --color-gold: #c9a84c;
  --color-gold-dim: #8a6f2e;
  --color-crimson: #7b1f1f;
  --color-text: #e8dcc8;
  --color-muted: #8a7a6a;
  --font-display: 'Cinzel', serif;
  --font-body: 'EB Garamond', serif;
  --radius: 8px;
  --transition: 0.2s ease;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 1.05rem;
  line-height: 1.6;
  min-height: 100vh;
}

h1, h2, h3 {
  font-family: var(--font-display);
  color: var(--color-gold);
  letter-spacing: 0.05em;
}

a { color: var(--color-gold); text-decoration: none; }
a:hover { color: var(--color-text); }

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.25rem;
  position: relative;
}

.card::before, .card::after {
  content: '✦';
  position: absolute;
  color: var(--color-gold-dim);
  font-size: 0.75rem;
}
.card::before { top: 6px; left: 8px; }
.card::after { bottom: 6px; right: 8px; }

.btn {
  font-family: var(--font-display);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  padding: 0.55rem 1.4rem;
  border-radius: var(--radius);
  border: 1px solid var(--color-gold);
  background: transparent;
  color: var(--color-gold);
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}
.btn:hover { background: var(--color-gold); color: var(--color-bg); }
.btn-primary { background: var(--color-gold); color: var(--color-bg); }
.btn-primary:hover { background: var(--color-gold-dim); }
.btn-danger { border-color: var(--color-crimson); color: var(--color-crimson); }
.btn-danger:hover { background: var(--color-crimson); color: var(--color-text); }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1rem; }
.form-group label { font-family: var(--font-display); font-size: 0.8rem; letter-spacing: 0.06em; color: var(--color-muted); }
.form-group input,
.form-group select,
.form-group textarea {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
  width: 100%;
  transition: border-color var(--transition);
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-gold);
}
.form-group select option { background: var(--color-surface); }

.main-content { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }

.page-title {
  font-family: var(--font-display);
  font-size: 1.8rem;
  color: var(--color-gold);
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.category-icon { font-size: 1.2rem; margin-right: 0.4rem; }

.error-msg { color: #e05555; font-size: 0.9rem; margin-top: 0.5rem; }
.success-msg { color: #5ec46e; font-size: 0.9rem; margin-top: 0.5rem; }
```

- [ ] **Step 2: Write NavBar.vue**

`TP3/frontend/src/components/NavBar.vue`:
```vue
<template>
  <nav class="navbar">
    <span class="navbar-brand">✦ LifeTracker ✦</span>
    <div class="navbar-links">
      <RouterLink to="/dashboard">Inicio</RouterLink>
      <RouterLink to="/entries">Registros</RouterLink>
      <RouterLink to="/entries/new">+ Agregar</RouterLink>
      <RouterLink to="/summary/monthly">Mensual</RouterLink>
      <RouterLink to="/summary/annual">Anual</RouterLink>
      <button class="btn btn-danger" style="font-size:0.75rem; padding:0.35rem 0.8rem;" @click="auth.logout()">Salir</button>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.navbar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-brand {
  font-family: var(--font-display);
  color: var(--color-gold);
  font-size: 1.1rem;
  letter-spacing: 0.15em;
}
.navbar-links { display: flex; align-items: center; gap: 1.5rem; }
.navbar-links a { font-family: var(--font-display); font-size: 0.8rem; letter-spacing: 0.06em; color: var(--color-muted); transition: color 0.2s; }
.navbar-links a:hover, .navbar-links a.router-link-active { color: var(--color-gold); }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add TP3/frontend/src/assets/main.css TP3/frontend/src/components/NavBar.vue
git commit -m "feat: Harry Potter dark theme CSS + NavBar component"
```

---

## Task 12: Login / Register View

**Files:**
- Create: `TP3/frontend/src/views/LoginView.vue`

- [ ] **Step 1: Write LoginView.vue**

`TP3/frontend/src/views/LoginView.vue`:
```vue
<template>
  <div class="login-page">
    <div class="login-card card">
      <h1>✦ LifeTracker ✦</h1>
      <p class="subtitle">Guardián de tus memorias</p>

      <div class="tab-row">
        <button :class="['tab', { active: mode === 'login' }]" @click="mode = 'login'">Ingresar</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="mode = 'register'">Registrarse</button>
      </div>

      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Correo electrónico</label>
          <input v-model="email" type="email" required placeholder="tu@email.com" />
        </div>
        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="password" type="password" required placeholder="••••••••" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary" style="width:100%">
          {{ mode === 'login' ? 'Ingresar' : 'Crear cuenta' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const mode = ref('login')
const email = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    if (mode.value === 'login') {
      await auth.login(email.value, password.value)
    } else {
      await auth.register(email.value, password.value)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al procesar la solicitud'
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  text-align: center;
}
.login-card h1 { margin-bottom: 0.25rem; }
.subtitle { color: var(--color-muted); font-style: italic; margin-bottom: 1.5rem; }
.tab-row { display: flex; gap: 0; margin-bottom: 1.5rem; border: 1px solid var(--color-border); border-radius: var(--radius); overflow: hidden; }
.tab { flex: 1; padding: 0.5rem; background: transparent; border: none; color: var(--color-muted); font-family: var(--font-display); font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
.tab.active { background: var(--color-gold); color: var(--color-bg); }
form { text-align: left; }
</style>
```

- [ ] **Step 2: Verify login works end-to-end**

With backend running (`uvicorn app.main:app --reload`) and frontend running (`npm run dev`):
1. Visit `http://localhost:5173/login`
2. Register a new account
3. Should redirect to `/dashboard` (blank page for now, that's fine)

- [ ] **Step 3: Commit**

```bash
git add TP3/frontend/src/views/LoginView.vue
git commit -m "feat: login/register view"
```

---

## Task 13: Entry Form View (Dynamic Fields)

**Files:**
- Create: `TP3/frontend/src/views/EntryFormView.vue`

- [ ] **Step 1: Write EntryFormView.vue**

`TP3/frontend/src/views/EntryFormView.vue`:
```vue
<template>
  <div>
    <h1 class="page-title">{{ isEditing ? 'Editar registro' : 'Nuevo registro' }}</h1>
    <div class="card" style="max-width:600px">
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Categoría</label>
          <select v-model="form.category" required @change="resetCategoryFields">
            <option value="">— elegir —</option>
            <option value="event">🎵 Evento / Concierto</option>
            <option value="movie_series">🎬 Película / Serie</option>
            <option value="book">📚 Libro</option>
            <option value="city">🗺️ Ciudad</option>
            <option value="place">🏛️ Lugar (restaurante, museo…)</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ titleLabel }}</label>
          <input v-model="form.title" type="text" required :placeholder="titlePlaceholder" />
        </div>

        <div class="form-group">
          <label>Fecha</label>
          <input v-model="form.date" type="date" required />
        </div>

        <!-- movie_series fields -->
        <template v-if="form.category === 'movie_series'">
          <div class="form-group">
            <label>Saga (opcional)</label>
            <input v-model="form.saga_name" type="text" placeholder="ej: Harry Potter, MCU" />
          </div>
          <div v-if="form.saga_name" class="form-group">
            <label>Número de entrega en la saga</label>
            <input v-model.number="form.saga_part" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Temporada (solo series)</label>
            <input v-model.number="form.season_number" type="number" min="1" placeholder="ej: 4" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <!-- book fields -->
        <template v-if="form.category === 'book'">
          <div class="form-group">
            <label>Saga (opcional)</label>
            <input v-model="form.saga_name" type="text" placeholder="ej: El señor de los anillos" />
          </div>
          <div v-if="form.saga_name" class="form-group">
            <label>Número de entrega en la saga</label>
            <input v-model.number="form.saga_part" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <!-- city fields -->
        <template v-if="form.category === 'city'">
          <div class="form-group">
            <label>País</label>
            <input v-model="form.country" type="text" placeholder="ej: Francia" />
          </div>
        </template>

        <!-- place fields -->
        <template v-if="form.category === 'place'">
          <div class="form-group">
            <label>Tipo de lugar</label>
            <select v-model="form.place_type" required>
              <option value="">— elegir —</option>
              <option value="restaurant">Restaurante</option>
              <option value="cafe">Café</option>
              <option value="museum">Museo</option>
              <option value="bar">Bar</option>
              <option value="park">Parque</option>
              <option value="other">Otro</option>
            </select>
          </div>
          <div class="form-group">
            <label>Ciudad (opcional)</label>
            <input v-model="form.city" type="text" placeholder="ej: París" />
          </div>
          <div class="form-group">
            <label>País (opcional)</label>
            <input v-model="form.country" type="text" placeholder="ej: Francia" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <div class="form-group">
          <label>Notas (opcional)</label>
          <textarea v-model="form.notes" rows="3" placeholder="Comentarios libres…" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
        <div style="display:flex; gap:1rem; margin-top:0.5rem">
          <button type="submit" class="btn btn-primary">{{ isEditing ? 'Guardar cambios' : 'Registrar' }}</button>
          <RouterLink to="/entries" class="btn">Cancelar</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEntriesStore } from '@/stores/entries'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()
const store = useEntriesStore()

const isEditing = computed(() => !!route.params.id)
const error = ref('')

const form = ref({
  category: '', title: '', date: '', notes: null,
  rating: null, saga_name: null, saga_part: null,
  season_number: null, country: null, city: null, place_type: null,
})

const titleLabel = computed(() => {
  const labels = { city: 'Ciudad', place: 'Nombre del lugar', event: 'Nombre del evento', movie_series: 'Título', book: 'Título' }
  return labels[form.value.category] || 'Título'
})
const titlePlaceholder = computed(() => {
  const ph = { city: 'ej: Venecia', place: 'ej: Musée d\'Orsay', event: 'ej: Coldplay World Tour', movie_series: 'ej: Dune: Parte Dos', book: 'ej: El nombre del viento' }
  return ph[form.value.category] || ''
})

function resetCategoryFields() {
  Object.assign(form.value, { saga_name: null, saga_part: null, season_number: null, country: null, city: null, place_type: null, rating: null })
}

onMounted(async () => {
  if (isEditing.value) {
    const res = await api.get(`/entries/${route.params.id}`)
    Object.assign(form.value, res.data)
    form.value.date = res.data.date
  }
})

async function submit() {
  error.value = ''
  const payload = Object.fromEntries(Object.entries(form.value).filter(([, v]) => v !== null && v !== ''))
  try {
    if (isEditing.value) {
      await store.updateEntry(route.params.id, payload)
    } else {
      await store.createEntry(payload)
    }
    router.push('/entries')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al guardar'
  }
}
</script>
```

- [ ] **Step 2: Test the form manually**

With backend + frontend running:
1. Go to `/entries/new`
2. Select "Libro" — saga, saga_part, rating fields appear
3. Select "Ciudad" — only país field appears
4. Fill and submit — should appear in `/entries` (blank for now)

- [ ] **Step 3: Commit**

```bash
git add TP3/frontend/src/views/EntryFormView.vue
git commit -m "feat: dynamic entry form with category-specific fields"
```

---

## Task 14: Entry Card + Entries List View

**Files:**
- Create: `TP3/frontend/src/components/EntryCard.vue`
- Create: `TP3/frontend/src/views/EntriesListView.vue`

- [ ] **Step 1: Write EntryCard.vue**

`TP3/frontend/src/components/EntryCard.vue`:
```vue
<template>
  <div class="card entry-card">
    <div class="entry-header">
      <span class="category-icon">{{ icon }}</span>
      <strong>{{ entry.title }}</strong>
      <span class="entry-date">{{ formatDate(entry.date) }}</span>
    </div>
    <div class="entry-meta">
      <span v-if="entry.saga_name">📖 {{ entry.saga_name }} #{{ entry.saga_part }}</span>
      <span v-if="entry.season_number">Temporada {{ entry.season_number }}</span>
      <span v-if="entry.country">{{ entry.city ? `${entry.city}, ` : '' }}{{ entry.country }}</span>
      <span v-if="entry.place_type">{{ entry.place_type }}</span>
      <span v-if="entry.rating">{{ '★'.repeat(entry.rating) }}{{ '☆'.repeat(5 - entry.rating) }}</span>
    </div>
    <p v-if="entry.notes" class="entry-notes">{{ entry.notes }}</p>
    <div class="entry-actions">
      <RouterLink :to="`/entries/${entry.id}/edit`" class="btn" style="font-size:0.75rem; padding:0.3rem 0.7rem">Editar</RouterLink>
      <button class="btn btn-danger" style="font-size:0.75rem; padding:0.3rem 0.7rem" @click="$emit('delete', entry.id)">Eliminar</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ entry: Object })
defineEmits(['delete'])

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }
const icon = icons[props.entry.category] || '•'

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' })
}
</script>

<style scoped>
.entry-card { margin-bottom: 1rem; }
.entry-header { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.4rem; }
.entry-date { margin-left: auto; font-size: 0.85rem; color: var(--color-muted); }
.entry-meta { display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.88rem; color: var(--color-muted); margin-bottom: 0.4rem; }
.entry-notes { font-style: italic; color: var(--color-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }
.entry-actions { display: flex; gap: 0.5rem; }
</style>
```

- [ ] **Step 2: Write EntriesListView.vue**

`TP3/frontend/src/views/EntriesListView.vue`:
```vue
<template>
  <div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem">
      <h1 class="page-title" style="margin-bottom:0">Mis registros</h1>
      <RouterLink to="/entries/new" class="btn btn-primary">+ Agregar</RouterLink>
    </div>

    <div class="filter-row">
      <select v-model="filterCategory" @change="load">
        <option value="">Todas las categorías</option>
        <option value="event">🎵 Eventos</option>
        <option value="movie_series">🎬 Películas/Series</option>
        <option value="book">📚 Libros</option>
        <option value="city">🗺️ Ciudades</option>
        <option value="place">🏛️ Lugares</option>
      </select>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="entries.length === 0" class="muted-text">No hay registros todavía.</div>
    <EntryCard
      v-for="entry in entries"
      :key="entry.id"
      :entry="entry"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEntriesStore } from '@/stores/entries'
import EntryCard from '@/components/EntryCard.vue'

const store = useEntriesStore()
const entries = ref([])
const filterCategory = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  const filters = filterCategory.value ? { category: filterCategory.value } : {}
  entries.value = await store.fetchEntries(filters)
  loading.value = false
}

async function handleDelete(id) {
  if (!confirm('¿Eliminar este registro?')) return
  await store.deleteEntry(id)
  entries.value = entries.value.filter(e => e.id !== id)
}

onMounted(load)
</script>

<style scoped>
.filter-row { margin-bottom: 1.5rem; }
.filter-row select { background: var(--color-surface); border: 1px solid var(--color-border); color: var(--color-text); font-family: var(--font-body); padding: 0.4rem 0.75rem; border-radius: var(--radius); }
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
</style>
```

- [ ] **Step 3: Test end-to-end**

With backend + frontend running:
1. Add 2–3 entries via `/entries/new`
2. Go to `/entries` — cards should appear
3. Filter by category — list updates
4. Edit an entry — changes save
5. Delete an entry — it disappears

- [ ] **Step 4: Commit**

```bash
git add TP3/frontend/src/views/EntriesListView.vue TP3/frontend/src/components/EntryCard.vue
git commit -m "feat: entries list view + EntryCard component"
```

---

## Task 15: Dashboard View

**Files:**
- Create: `TP3/frontend/src/components/SummaryBlock.vue`
- Create: `TP3/frontend/src/views/DashboardView.vue`

- [ ] **Step 1: Write SummaryBlock.vue**

`TP3/frontend/src/components/SummaryBlock.vue`:
```vue
<template>
  <div class="summary-block card">
    <div class="summary-header">
      <span class="category-icon">{{ icon }}</span>
      <span class="summary-title">{{ categoryLabel }}</span>
      <span class="summary-count">{{ highlight.count }}</span>
    </div>

    <div v-if="highlight.category === 'city'" class="summary-detail">
      <span>{{ highlight.countries }} {{ highlight.countries === 1 ? 'país' : 'países' }}, {{ highlight.cities }} {{ highlight.cities === 1 ? 'ciudad' : 'ciudades' }}</span>
      <div class="item-list">
        <span v-for="item in highlight.items" :key="item.city" class="item-chip">
          {{ item.city }}<span v-if="item.country">, {{ item.country }}</span>
        </span>
      </div>
    </div>

    <div v-else-if="highlight.category === 'place'" class="summary-detail">
      <div class="by-type">
        <span v-for="(count, type) in highlight.by_type" :key="type" class="item-chip">{{ count }} {{ type }}</span>
      </div>
    </div>

    <div v-else class="summary-detail">
      <div class="item-list">
        <span v-for="item in highlight.items" :key="item.title" class="item-chip">
          {{ item.title }}<span v-if="item.saga_name"> ({{ item.saga_name }})</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ highlight: Object })
const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }
const labels = { event: 'Eventos', movie_series: 'Películas y series', book: 'Libros', city: 'Ciudades', place: 'Lugares' }
const icon = icons[props.highlight.category] || '•'
const categoryLabel = labels[props.highlight.category] || props.highlight.category
</script>

<style scoped>
.summary-block { margin-bottom: 1rem; }
.summary-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem; }
.summary-title { font-family: var(--font-display); font-size: 0.9rem; color: var(--color-gold); }
.summary-count { margin-left: auto; font-family: var(--font-display); font-size: 1.4rem; color: var(--color-gold); }
.summary-detail { color: var(--color-muted); font-size: 0.9rem; }
.item-list, .by-type { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
.item-chip { background: var(--color-surface-raised); border: 1px solid var(--color-border); border-radius: 999px; padding: 0.2rem 0.7rem; font-size: 0.82rem; color: var(--color-text); }
</style>
```

- [ ] **Step 2: Write DashboardView.vue**

`TP3/frontend/src/views/DashboardView.vue`:
```vue
<template>
  <div>
    <h1 class="page-title">✦ Tu mundo este mes ✦</h1>
    <p class="period-label">{{ monthName }} {{ currentYear }}</p>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="highlights.length === 0" class="muted-text empty-state">
      <p>Aún no hay registros este mes.</p>
      <RouterLink to="/entries/new" class="btn btn-primary" style="margin-top:1rem">Agregar el primero</RouterLink>
    </div>
    <div v-else>
      <SummaryBlock v-for="h in highlights" :key="h.category" :highlight="h" />
    </div>

    <div class="quick-links">
      <RouterLink to="/entries/new" class="btn btn-primary">+ Agregar registro</RouterLink>
      <RouterLink to="/summary/monthly" class="btn">Ver historial mensual</RouterLink>
      <RouterLink to="/summary/annual" class="btn">Ver año completo</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const currentMonth = today.getMonth() + 1
const monthName = today.toLocaleDateString('es-AR', { month: 'long' })

const highlights = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get(`/summaries/monthly/${currentYear}/${currentMonth}`)
    highlights.value = res.data.highlights
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.period-label { color: var(--color-muted); font-style: italic; margin-bottom: 1.5rem; text-transform: capitalize; }
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
.empty-state { display: flex; flex-direction: column; align-items: center; }
.quick-links { display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add TP3/frontend/src/components/SummaryBlock.vue TP3/frontend/src/views/DashboardView.vue
git commit -m "feat: dashboard + SummaryBlock component"
```

---

## Task 16: Monthly and Annual Summary Views

**Files:**
- Create: `TP3/frontend/src/views/MonthlySummaryView.vue`
- Create: `TP3/frontend/src/views/AnnualSummaryView.vue`

- [ ] **Step 1: Write MonthlySummaryView.vue**

`TP3/frontend/src/views/MonthlySummaryView.vue`:
```vue
<template>
  <div>
    <h1 class="page-title">Resumen mensual</h1>
    <div class="picker card" style="max-width:300px; margin-bottom:1.5rem">
      <div class="form-group">
        <label>Año</label>
        <input v-model.number="year" type="number" :min="2020" :max="currentYear" />
      </div>
      <div class="form-group">
        <label>Mes</label>
        <select v-model.number="month">
          <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
        </select>
      </div>
      <button class="btn btn-primary" style="width:100%" @click="load">Ver resumen</button>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="loaded && highlights.length === 0" class="muted-text">Sin registros en este período.</div>
    <template v-else-if="loaded">
      <h2 style="margin-bottom:1rem; text-transform:capitalize">{{ monthName(month) }} {{ year }}</h2>
      <SummaryBlock v-for="h in highlights" :key="h.category" :highlight="h" />
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const year = ref(currentYear)
const month = ref(today.getMonth() + 1)
const highlights = ref([])
const loading = ref(false)
const loaded = ref(false)

function monthName(m) {
  return new Date(2000, m - 1, 1).toLocaleDateString('es-AR', { month: 'long' })
}

async function load() {
  loading.value = true
  loaded.value = false
  try {
    const res = await api.get(`/summaries/monthly/${year.value}/${month.value}`)
    highlights.value = res.data.highlights
    loaded.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
</style>
```

- [ ] **Step 2: Write AnnualSummaryView.vue**

`TP3/frontend/src/views/AnnualSummaryView.vue`:
```vue
<template>
  <div>
    <h1 class="page-title">✦ Tu año en resumen ✦</h1>
    <div class="picker card" style="max-width:200px; margin-bottom:1.5rem">
      <div class="form-group">
        <label>Año</label>
        <input v-model.number="year" type="number" :min="2020" :max="currentYear" />
      </div>
      <button class="btn btn-primary" style="width:100%" @click="load">Ver año</button>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="loaded && summary.months.length === 0" class="muted-text">Sin registros en {{ year }}.</div>

    <template v-else-if="loaded">
      <!-- Annual totals -->
      <div class="totals-banner card" style="margin-bottom:2rem">
        <h2>{{ year }} — totales</h2>
        <div class="totals-grid">
          <div v-for="(count, cat) in displayTotals" :key="cat" class="total-item">
            <span class="total-icon">{{ catIcon(cat) }}</span>
            <span class="total-count">{{ count }}</span>
            <span class="total-label">{{ catLabel(cat) }}</span>
          </div>
        </div>
      </div>

      <!-- Month by month -->
      <div v-for="block in summary.months" :key="block.month" class="month-section">
        <h3 class="month-heading">{{ monthName(block.month) }}</h3>
        <SummaryBlock v-for="h in block.highlights" :key="h.category" :highlight="h" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const year = ref(currentYear)
const summary = ref({ months: [], totals: {} })
const loading = ref(false)
const loaded = ref(false)

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️', city_countries: '🌍' }
const labels = { event: 'eventos', movie_series: 'películas/series', book: 'libros', city: 'ciudades', place: 'lugares', city_countries: 'países' }

const displayTotals = computed(() => {
  const t = summary.value.totals
  return Object.fromEntries(Object.entries(t).filter(([, v]) => v > 0))
})

function catIcon(cat) { return icons[cat] || '•' }
function catLabel(cat) { return labels[cat] || cat }
function monthName(m) { return new Date(2000, m - 1, 1).toLocaleDateString('es-AR', { month: 'long' }) }

async function load() {
  loading.value = true
  loaded.value = false
  try {
    const res = await api.get(`/summaries/annual/${year.value}`)
    summary.value = res.data
    loaded.value = true
  } finally {
    loading.value = false
  }
}
</script>

<script>
import { computed } from 'vue'
</script>

<style scoped>
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
.totals-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 1rem; }
.total-item { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; }
.total-icon { font-size: 1.5rem; }
.total-count { font-family: var(--font-display); font-size: 2rem; color: var(--color-gold); }
.total-label { font-size: 0.8rem; color: var(--color-muted); }
.month-section { margin-bottom: 2rem; }
.month-heading { font-family: var(--font-display); color: var(--color-gold); font-size: 1rem; text-transform: capitalize; margin-bottom: 0.75rem; padding-bottom: 0.3rem; border-bottom: 1px solid var(--color-border); }
</style>
```

**Fix before committing:** the `<script setup>` block in `AnnualSummaryView.vue` above has a stray `<script>` block at the end. Replace the entire script section with a single `<script setup>` that imports both `ref` and `computed`:

```vue
<script setup>
import { ref, computed } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const year = ref(currentYear)
const summary = ref({ months: [], totals: {} })
const loading = ref(false)
const loaded = ref(false)

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️', city_countries: '🌍' }
const labels = { event: 'eventos', movie_series: 'películas/series', book: 'libros', city: 'ciudades', place: 'lugares', city_countries: 'países' }

const displayTotals = computed(() => {
  const t = summary.value.totals
  return Object.fromEntries(Object.entries(t).filter(([, v]) => v > 0))
})

function catIcon(cat) { return icons[cat] || '•' }
function catLabel(cat) { return labels[cat] || cat }
function monthName(m) { return new Date(2000, m - 1, 1).toLocaleDateString('es-AR', { month: 'long' }) }

async function load() {
  loading.value = true
  loaded.value = false
  try {
    const res = await api.get(`/summaries/annual/${year.value}`)
    summary.value = res.data
    loaded.value = true
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add TP3/frontend/src/views/MonthlySummaryView.vue TP3/frontend/src/views/AnnualSummaryView.vue
git commit -m "feat: monthly and annual summary views"
```

---

## Task 17: `/add-entry` CLI Script + Skill File

**Files:**
- Create: `TP3/backend/scripts/add_entry_cli.py`
- Create: `TP3/.claude/skills/add-entry.md`

- [ ] **Step 1: Write add_entry_cli.py**

`TP3/backend/scripts/add_entry_cli.py`:
```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import httpx

BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = Path.home() / ".config" / "lifetracker" / "token"

def get_token():
    return TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else None

def save_token(token):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token)

def authenticate():
    print("No hay sesión guardada. Iniciá sesión:")
    email = input("Email: ").strip()
    password = input("Contraseña: ").strip()
    res = httpx.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"Error: {res.json().get('detail', 'credenciales inválidas')}")
        sys.exit(1)
    token = res.json()["access_token"]
    save_token(token)
    print("✓ Sesión iniciada")
    return token

def prompt_entry():
    print("\n¿Qué querés registrar?")
    print("  1. Evento / Concierto")
    print("  2. Película / Serie")
    print("  3. Libro")
    print("  4. Ciudad")
    print("  5. Lugar (restaurante, museo…)")
    choice = input("\nOpción (1-5): ").strip()
    categories = {"1": "event", "2": "movie_series", "3": "book", "4": "city", "5": "place"}
    if choice not in categories:
        print("Opción inválida"); sys.exit(1)
    category = categories[choice]

    title = input("Nombre/Título: ").strip()
    date = input("Fecha (YYYY-MM-DD): ").strip()
    notes = input("Notas (Enter para saltar): ").strip() or None

    entry = {"category": category, "title": title, "date": date}
    if notes:
        entry["notes"] = notes

    if category == "movie_series":
        saga = input("Saga (Enter para saltar): ").strip()
        if saga:
            entry["saga_name"] = saga
            part = input("Número de entrega: ").strip()
            if part.isdigit():
                entry["saga_part"] = int(part)
        season = input("Temporada (Enter para saltar): ").strip()
        if season.isdigit():
            entry["season_number"] = int(season)
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    elif category == "book":
        saga = input("Saga (Enter para saltar): ").strip()
        if saga:
            entry["saga_name"] = saga
            part = input("Número de entrega: ").strip()
            if part.isdigit():
                entry["saga_part"] = int(part)
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    elif category == "city":
        country = input("País (Enter para saltar): ").strip()
        if country:
            entry["country"] = country

    elif category == "place":
        print("Tipo: restaurant / cafe / museum / bar / park / other")
        place_type = input("Tipo: ").strip()
        if place_type:
            entry["place_type"] = place_type
        city = input("Ciudad (Enter para saltar): ").strip()
        if city:
            entry["city"] = city
        country = input("País (Enter para saltar): ").strip()
        if country:
            entry["country"] = country
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    return entry

def post_entry(entry, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = httpx.post(f"{BASE_URL}/entries", json=entry, headers=headers)
    return res

def main():
    token = get_token() or authenticate()
    entry = prompt_entry()
    res = post_entry(entry, token)

    if res.status_code == 401:
        print("Sesión expirada, reautenticando…")
        token = authenticate()
        res = post_entry(entry, token)

    if res.status_code == 201:
        data = res.json()
        saga_info = f" — {data['saga_name']} #{data['saga_part']}" if data.get("saga_name") else ""
        print(f"\n✓ Registrado: '{data['title']}' [{data['category']}]{saga_info}")
    else:
        print(f"Error {res.status_code}: {res.json()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Install httpx in backend**

Add to `requirements.txt` (already included). If not installed:
```bash
pip install httpx
```

- [ ] **Step 3: Test the script manually**

With backend running:
```bash
cd TP3/backend
python3 scripts/add_entry_cli.py
```

Expected flow: prompts for category, fields, then prints `✓ Registrado: ...`

- [ ] **Step 4: Create .claude directory and write the skill file**

```bash
mkdir -p TP3/.claude/skills
```

`TP3/.claude/skills/add-entry.md`:
```markdown
# Skill: /add-entry

Registra una nueva entrada en LifeTracker desde la terminal mediante un flujo interactivo.

## Qué hace

Ejecuta el script `backend/scripts/add_entry_cli.py` que:
1. Verifica el token JWT guardado en `~/.config/lifetracker/token`
2. Si no hay token, solicita email y contraseña
3. Pregunta qué tipo de entrada registrar
4. Solicita los campos relevantes según el tipo
5. Llama a `POST /api/entries` y confirma el registro

## Instrucciones

Ejecutá el siguiente comando desde el directorio `TP3/`:

```bash
cd backend && python3 scripts/add_entry_cli.py
```

El backend debe estar corriendo en `http://localhost:8000`.
Si no está corriendo, primero ejecutá: `uvicorn app.main:app --reload`
```

- [ ] **Step 5: Commit**

```bash
git add TP3/backend/scripts/add_entry_cli.py TP3/.claude/
git commit -m "feat: /add-entry CLI skill"
```

---

## Task 18: Configuration Files

**Files:**
- Create: `TP3/CLAUDE.md`
- Create: `TP3/rules.md`
- Create: `TP3/.claude/settings.json`

- [ ] **Step 1: Write CLAUDE.md**

`TP3/CLAUDE.md`:
```markdown
# LifeTracker — TP3 IISAIA

Aplicación web de seguimiento de vida personal. Multi-usuario con JWT auth.

## Stack

- **Backend:** Python 3.11 + FastAPI, puerto 8000
- **Frontend:** Vue.js 3 + Vite, puerto 5173
- **Base de datos:** PostgreSQL (docker: `lifetracker-db`)
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
  -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
docker exec lifetracker-db psql -U postgres -c "CREATE DATABASE lifetracker_test;"
```

## Skill disponible

`/add-entry` — registra una nueva entrada desde la terminal (requiere backend corriendo)

## Variables de entorno

Copiar `backend/.env.example` a `backend/.env` y completar:
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — clave secreta para JWT (generá una random)
```

- [ ] **Step 2: Write rules.md**

`TP3/rules.md`:
```markdown
# Reglas del proyecto LifeTracker

- No modificar migraciones ya aplicadas — crear nuevas con `alembic revision --autogenerate`
- JWT secrets solo en `.env`, nunca hardcodeados en código
- Validar coherencia de campos por categoría en Pydantic (backend), no solo en frontend
- Los resúmenes nunca muestran categorías con 0 entradas — el endpoint devuelve `[]` para períodos vacíos
- `place_type` solo acepta valores del enum; nuevos tipos requieren una migración `ALTER TYPE place_type_enum ADD VALUE '...'`
- Cada endpoint protegido extrae `user_id` del JWT — nunca del request body
- El frontend guarda el token JWT en `localStorage` bajo la clave `token`
```

- [ ] **Step 3: Write .claude/settings.json**

`TP3/.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(python3:*)",
      "Bash(uvicorn:*)",
      "Bash(alembic:*)",
      "Bash(npm:*)",
      "Bash(pytest:*)",
      "Bash(pip:*)",
      "Bash(docker:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)"
    ]
  }
}
```

- [ ] **Step 4: Commit**

```bash
git add TP3/CLAUDE.md TP3/rules.md TP3/.claude/settings.json
git commit -m "feat: CLAUDE.md, rules.md, and .claude/settings.json"
```

---

## Final Verification

- [ ] **Run the full backend test suite**

```bash
cd TP3/backend && pytest tests/ -v
```

Expected: all tests pass (auth, entries, summaries, metadata)

- [ ] **Smoke-test the full app**

With backend and frontend both running:
1. Register a new user
2. Add one entry of each category (event, movie_series, book, city, place)
3. Go to Dashboard — current month summary shows up
4. Go to Monthly Summary — select current month, all categories appear
5. Go to Annual Summary — totals grid and month breakdown appear
6. Run `/add-entry` skill — entry created via CLI shows up in the web app

- [ ] **Final commit**

```bash
git add .
git commit -m "feat: TP3 LifeTracker complete"
```
