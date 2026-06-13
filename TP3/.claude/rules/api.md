---
paths:
  - "backend/**/*.py"
---

# API conventions

Cuando trabajes con código del backend:

- Cada endpoint declara su `response_model` y `status_code` explícito.
- Para endpoints protegidos, inyectar `current_user: User = Depends(get_current_user)` como parámetro
  — no como `dependencies=[]` — porque el handler generalmente necesita el usuario.
- Errores que vuelven al cliente: `HTTPException` con código HTTP correcto (`404` para no encontrado,
  `403` cuando falta el header Authorization, `401` para token inválido o expirado).
