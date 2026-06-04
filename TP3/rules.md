# Reglas del proyecto LifeTracker

- No modificar migraciones ya aplicadas — crear nuevas con `alembic revision --autogenerate`
- JWT secrets solo en `.env`, nunca hardcodeados en código
- Validar coherencia de campos por categoría en Pydantic (backend), no solo en frontend
- Los resúmenes nunca muestran categorías con 0 entradas — el endpoint devuelve `[]` para períodos vacíos
- `place_type` solo acepta valores del enum; nuevos tipos requieren una migración `ALTER TYPE place_type_enum ADD VALUE '...'`
- Cada endpoint protegido extrae `user_id` del JWT — nunca del request body
- El frontend guarda el token JWT en `localStorage` bajo la clave `token`
