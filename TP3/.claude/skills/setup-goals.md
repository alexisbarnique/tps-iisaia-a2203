---
name: setup-goals
description: Crear, listar, actualizar y eliminar objetivos anuales por categoría. Muestra progreso actual (entries registradas vs. target).
---

# Skill: /setup-goals

Gestiona los objetivos anuales del usuario en LifeTracker desde la terminal.

## Qué hace

1. Verifica que el backend esté corriendo en `http://localhost:8000`
2. Obtiene un token JWT (lo pide si no hay uno guardado)
3. Pregunta qué acción realizar: listar, crear, actualizar target o eliminar
4. Llama al endpoint correspondiente de `/api/goals` y muestra el resultado

## Endpoints disponibles

| Acción | Método | Ruta |
|--------|--------|------|
| Listar (con progreso) | GET | `/api/goals` |
| Crear objetivo | POST | `/api/goals` |
| Actualizar target | PUT | `/api/goals/{id}` |
| Eliminar | DELETE | `/api/goals/{id}` |

Todos los endpoints requieren `Authorization: Bearer <token>`.

## Campos para crear un objetivo

- `year` — entero entre 2020 y 2100
- `category` — una de las categorías válidas (book, movie_series, event, city, etc.)
- `target` — entero ≥ 1 (cantidad de entries que querés alcanzar en el año)

Restricción: solo puede existir un objetivo por combinación `(user, year, category)`. Si ya existe, devuelve 409.

## Instrucciones para Claude

Cuando el usuario invoque `/setup-goals`:

1. **Verificar backend**: intentá un `GET /api/goals` sin token. Si da connection error, indicá que hay que levantar el backend con `cd backend && uvicorn app.main:app --reload`.

2. **Obtener token**: pedí email y contraseña, luego hacé `POST /api/auth/login`. Guardá el token para los pasos siguientes.

3. **Preguntar acción**:
   - `listar` → GET `/api/goals`, mostrá cada goal con `category`, `year`, `target`, `current` y `percentage`%
   - `crear` → pedí `year`, `category` y `target`, luego POST `/api/goals`
   - `actualizar` → listá primero los goals, pedí cuál modificar (por número o category/year), pedí nuevo `target`, luego PUT `/api/goals/{id}`
   - `eliminar` → listá primero los goals, pedí cuál eliminar, confirmá antes de DELETE

4. **Mostrar resultado** en forma legible. Para `listar`, formateá así:
   ```
   📚 book 2026 — 3 / 12 (25.0%)
   🎬 movie_series 2026 — 8 / 20 (40.0%)
   ```

5. **Errores comunes**:
   - 409 → ya existe un goal para esa combinación año/categoría; ofrecé actualizar el target
   - 404 → el goal no pertenece al usuario
   - 403 → token inválido o expirado; volvé al paso 2

## Ejemplo de flujo con curl

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Crear objetivo
curl -s -X POST http://localhost:8000/api/goals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"year": 2026, "category": "book", "target": 12}'

# Listar con progreso
curl -s http://localhost:8000/api/goals \
  -H "Authorization: Bearer $TOKEN"
```
