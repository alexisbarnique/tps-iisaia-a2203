# Security

- No loggear el contenido del header `Authorization`.
- `.env` siempre al `.gitignore`. Versionamos solo `.env.example`.
- No exponer trazas internas en respuestas de error. `HTTPException` con detail genérico.
