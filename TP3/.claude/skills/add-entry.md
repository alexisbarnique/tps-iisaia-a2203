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
