# Testing

- Todo endpoint público necesita al menos un test de happy path y uno de error esperado.
- Tests usan `TestClient` de FastAPI con los fixtures `setup_db` (session-scoped, limpia la DB) y `db`
  (transaction rollback por test) definidos en `conftest.py`.
- Nombres: `test_<funcion>_<situacion>` — `test_create_goal_ok`, `test_get_entry_not_found`.
- No mockear la base de datos — los tests corren contra `lifetracker_test` (PostgreSQL real).
