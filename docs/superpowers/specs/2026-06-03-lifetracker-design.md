# LifeTracker — Diseño Técnico (TP3 IISAIA)

## Resumen

Aplicación web personal para registrar eventos de vida — conciertos, películas, series, libros, ciudades y lugares visitados — con generación de resúmenes mensuales y anuales estilo "Spotify Wrapped". Multi-usuario con autenticación JWT. Solo muestra lo que fue registrado, nunca lo que faltó.

---

## Stack Tecnológico

| Capa        | Tecnología                    |
|-------------|-------------------------------|
| Backend     | Python 3.11 + FastAPI         |
| Base de datos | PostgreSQL                  |
| ORM / Migraciones | SQLAlchemy + Alembic    |
| Frontend    | Vue.js 3 + Vite               |
| Estado global | Pinia                       |
| Auth        | JWT (Bearer token)            |
| Skill CLI   | `/add-entry` (Claude Code)    |

---

## Arquitectura General

```
┌─────────────────┐         ┌─────────────────┐         ┌──────────────┐
│  Vue.js (Vite)  │ ──HTTP──▶  FastAPI :8000   │ ──ORM──▶  PostgreSQL  │
│     :5173       │ ◀──JSON──  /api/*           │         │             │
└─────────────────┘         └─────────────────┘         └──────────────┘
        │                           │
        │                   JWT auth (Bearer token)
        │
┌─────────────────┐
│  Skill /add-entry│  (Claude Code CLI → FastAPI)
└─────────────────┘
```

**Estructura de carpetas:**

```
TP3/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routers/      # endpoints por dominio
│   │   ├── schemas/      # Pydantic schemas
│   │   └── auth/         # JWT logic
│   ├── alembic/          # migraciones
│   └── scripts/
│       └── add_entry_cli.py
├── frontend/
│   └── src/
│       ├── views/
│       ├── components/
│       └── stores/       # Pinia
├── .claude/
│   ├── settings.json
│   └── skills/
│       └── add-entry.md
├── CLAUDE.md
└── rules.md
```

---

## Modelo de Datos

### Tabla `users`

| Campo      | Tipo      | Restricciones        |
|------------|-----------|----------------------|
| id         | UUID      | PK                   |
| email      | TEXT      | UNIQUE NOT NULL       |
| password   | TEXT      | NOT NULL (bcrypt)     |
| created_at | TIMESTAMP | DEFAULT now()         |

### Tabla `entries`

| Campo         | Tipo      | Aplica a                        | Notas                              |
|---------------|-----------|---------------------------------|------------------------------------|
| id            | UUID      | todas                           | PK                                 |
| user_id       | UUID      | todas                           | FK → users.id                      |
| category      | ENUM      | todas                           | event, movie_series, book, city, place |
| title         | TEXT      | todas                           | NOT NULL                           |
| date          | DATE      | todas                           | NOT NULL — cuándo ocurrió          |
| notes         | TEXT      | todas                           | nullable, comentario libre         |
| created_at    | TIMESTAMP | todas                           | DEFAULT now()                      |
| rating        | INT       | movie_series, book, place       | nullable, 1–5                      |
| saga_name     | TEXT      | movie_series, book              | nullable                           |
| saga_part     | INT       | movie_series, book              | nullable — número de entrega       |
| season_number | INT       | movie_series                    | nullable — solo series             |
| country       | TEXT      | city, place                     | nullable                           |
| city          | TEXT      | place                           | nullable — ciudad donde está       |
| place_type    | ENUM      | place                           | nullable — ver enum abajo          |

### Enums PostgreSQL

```sql
CREATE TYPE category_enum AS ENUM ('event', 'movie_series', 'book', 'city', 'place');

CREATE TYPE place_type_enum AS ENUM ('restaurant', 'cafe', 'museum', 'bar', 'park', 'other');
-- Extensible con: ALTER TYPE place_type_enum ADD VALUE 'theater';
```

Todos los campos específicos por categoría son nullable. La validación de coherencia (ej: `season_number` solo con `movie_series`) se hace en el backend (Pydantic), no en la DB.

---

## API Endpoints (FastAPI)

Todos los endpoints excepto `auth/*` requieren `Authorization: Bearer <token>`. El `user_id` se extrae del token — nunca se pasa como parámetro.

### Auth

| Método | Ruta                  | Descripción        |
|--------|-----------------------|--------------------|
| POST   | /api/auth/register    | Crear cuenta       |
| POST   | /api/auth/login       | Obtener JWT token  |

### Entries

| Método | Ruta                  | Descripción                                    |
|--------|-----------------------|------------------------------------------------|
| GET    | /api/entries          | Listar entradas (filtros: category, year, month)|
| POST   | /api/entries          | Crear entrada                                  |
| GET    | /api/entries/{id}     | Detalle de una entrada                         |
| PUT    | /api/entries/{id}     | Editar entrada                                 |
| DELETE | /api/entries/{id}     | Eliminar entrada                               |

### Summaries

| Método | Ruta                                    | Descripción                     |
|--------|-----------------------------------------|---------------------------------|
| GET    | /api/summaries/monthly/{year}/{month}   | Resumen de un mes               |
| GET    | /api/summaries/annual/{year}            | Resumen anual (wrapped completo)|

### Metadata

| Método | Ruta               | Descripción                          |
|--------|--------------------|--------------------------------------|
| GET    | /api/categories    | Lista de categorías disponibles      |
| GET    | /api/place-types   | Lista de tipos de lugar (para forms) |

### Lógica de Resúmenes

Los resúmenes se calculan on-demand con queries agrupadas. **Nunca muestran categorías con 0 entradas.** Si el período no tiene ninguna entrada registrada, la API responde HTTP 200 con `"highlights": []` — nunca 404.

Ejemplo de resumen mensual (Marzo 2025):
```json
{
  "year": 2025,
  "month": 3,
  "highlights": [
    { "category": "book", "count": 2, "items": ["El nombre del viento", "La sabiduría del lobo"] },
    { "category": "city", "countries": 1, "cities": 1, "items": [{"city": "Mendoza", "country": "Argentina"}] },
    { "category": "movie_series", "count": 2, "items": ["Dune: Parte Dos", "Stranger Things T4"] }
  ]
}
```

---

## Frontend (Vue.js + Vite)

### Rutas

| Ruta                  | Vista              | Descripción                                      |
|-----------------------|--------------------|--------------------------------------------------|
| /login                | LoginView          | Formulario login/registro                        |
| /dashboard            | DashboardView      | Resumen del mes actual + accesos directos        |
| /entries              | EntriesListView    | Lista de entradas con filtros por categoría      |
| /entries/new          | EntryFormView      | Formulario de nueva entrada (campos dinámicos)   |
| /entries/:id/edit     | EntryFormView      | Editar entrada existente                         |
| /summary/monthly      | MonthlySummaryView | Selector de mes → resumen                       |
| /summary/annual       | AnnualSummaryView  | Selector de año → wrapped completo              |

### Estado Global (Pinia)

- **`authStore`** — JWT token, datos del usuario actual, login/logout
- **`entriesStore`** — cache de entradas, filtros activos, CRUD actions

### Formulario Dinámico (`/entries/new`)

Al seleccionar categoría aparecen los campos relevantes:

| Categoría      | Campos visibles                                      |
|----------------|------------------------------------------------------|
| event          | title, date, notes                                   |
| movie_series   | title, date, saga_name, saga_part, season_number, rating, notes |
| book           | title, date, saga_name, saga_part, rating, notes     |
| city           | title (ciudad), country, date, notes                 |
| place          | title, place_type, city, country, date, rating, notes|

---

## Diseño Visual

**Inspiración:** Harry Potter — Hogwarts de noche, pergamino mágico, estética oscura y dorada.

### Paleta de Colores

```css
--color-bg:       #0d0d1a;   /* noche en Hogwarts */
--color-surface:  #1a1a2e;   /* pergamino oscuro */
--color-border:   #3d2b1f;   /* madera antigua */
--color-gold:     #c9a84c;   /* dorado mágico */
--color-crimson:  #7b1f1f;   /* burdeos Gryffindor */
--color-text:     #e8dcc8;   /* pergamino claro */
--color-muted:    #8a7a6a;   /* tinta desvanecida */
```

### Tipografía (Google Fonts CDN)

- **Cinzel** — headings y títulos (estilo inscripción mágica)
- **EB Garamond** — cuerpo de texto (pergamino antiguo)

### Elementos Visuales

- Tarjetas con bordes dorados y esquinas decorativas
- Fondo texturado tipo pergamino oscuro
- Iconos por categoría: 🎵 eventos, 🎬 películas/series, 📚 libros, 🗺️ ciudades, 🏛️ lugares
- Animación suave al revelar el resumen anual (wrapped)
- CSS 100% custom con variables, sin librerías de UI externas

---

## Skill `/add-entry`

**Archivo:** `.claude/skills/add-entry.md`
**Script auxiliar:** `backend/scripts/add_entry_cli.py`

### Flujo Interactivo

```
1. Claude pregunta: ¿Qué querés registrar?
   → event / movie_series / book / city / place

2. Pide campos relevantes uno a uno según categoría

3. Llama a POST /api/entries con JWT local
   (almacenado en ~/.config/lifetracker/token)

4. Confirma: "✓ Agregado: 'El nombre del viento' — Crónica del Asesino de Reyes #1"
```

### Autenticación del CLI

El token JWT se guarda localmente al hacer login desde la web. Si no existe el archivo, el skill solicita email/password para obtenerlo antes de continuar.

---

## Archivos de Configuración

### `CLAUDE.md`

```markdown
# LifeTracker — TP3 IISAIA

Backend: FastAPI + PostgreSQL (puerto 8000)
Frontend: Vue.js + Vite (puerto 5173)
Skill disponible: /add-entry

## Comandos útiles
- Backend: cd backend && uvicorn app.main:app --reload
- Frontend: cd frontend && npm run dev
- Migraciones: alembic upgrade head
- Tests: cd backend && pytest
```

### `rules.md`

```markdown
- No modificar migraciones ya aplicadas — crear nuevas siempre
- JWT secrets solo en variables de entorno (.env), nunca hardcodeados
- Validar category y place_type en Pydantic (backend), no solo en el frontend
- Los resúmenes nunca muestran categorías con 0 entradas en el período
- place_type solo acepta valores del enum; nuevos tipos requieren migración
```

### `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(python3:*)",
      "Bash(uvicorn:*)",
      "Bash(alembic:*)",
      "Bash(npm:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)"
    ]
  }
}
```

---

## Decisiones de Diseño

- **Campos específicos en tabla única** — todos los campos opcionales en `entries` en lugar de tablas separadas por categoría. Simplifica queries y migraciones; la validación de coherencia vive en Pydantic.
- **Resúmenes on-demand** — no se precalculan ni cachean. El volumen de datos personales no justifica complejidad adicional.
- **JWT sin refresh token** — scope académico; token con expiración larga (7 días) es suficiente.
- **place_type como enum extensible** — `ALTER TYPE ... ADD VALUE` en Alembic es una migración de una línea, sin downtime ni pérdida de datos.
- **country en city y place** — permite contar países visitados independientemente del número de ciudades, habilitando el resumen "visitaste X países y Y ciudades".
