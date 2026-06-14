# Defensa TP3 — Resumen de la sesión de desarrollo asistido por IA

**Fecha:** 2026-06-13  
**Proyecto:** LifeTracker — Feature: Metas Anuales  
**Alumna:** Alexis Barniquez

---

## Contexto

Se agregó la funcionalidad **Metas Anuales** a LifeTracker, una feature completa de backend + frontend que permite a usuarios definir objetivos por categoría (ej. "leer 12 libros este año") y seguir su progreso automáticamente a partir de los registros existentes.

---

## Pipeline de desarrollo asistido por IA

El trabajo siguió el pipeline completo de **Superpowers**, usando un skill por etapa:

### 1. Brainstorming (`superpowers:brainstorming`)

El skill guió una sesión de preguntas iterativas (una por vez) para definir el diseño antes de escribir una sola línea de código. Las decisiones clave se tomaron mediante opciones A/B/C:

- Período: anual únicamente
- Progreso: automático (conteo de entradas, sin input manual)
- UI: página `/goals` dedicada + widget compacto en el Dashboard
- Arquitectura: una meta por usuario/año/categoría

Se usó el **Visual Companion** para mostrar mockups en el browser durante la etapa de diseño visual (cards con circular progress, chips del dashboard).

Al final, el skill generó el design doc en `docs/superpowers/specs/2026-06-13-goals-design.md` y lo commiteó.

---

### 2. Writing Plans (`superpowers:writing-plans`)

A partir del spec aprobado, el skill creó un plan de implementación detallado en `docs/superpowers/plans/2026-06-13-goals.md` con:

- 7 tareas descompuestas en pasos de 2-5 minutos
- Código exacto (no pseudocódigo) para cada paso
- TDD: primero el test fallando, luego la implementación
- Comandos exactos para correr los tests en cada paso

---

### 3. Subagent-Driven Development (`superpowers:subagent-driven-development`)

El skill ejecutó el plan despachando **subagentes independientes** por tarea, con revisión en dos etapas:

```
Por cada tarea:
  → Subagente implementador  (contexto limpio, sigue TDD)
  → Subagente spec-reviewer  (¿el código cumple el spec?)
  → Subagente code-quality-reviewer  (¿está bien escrito?)
  → Loop de corrección hasta aprobación
```

Esto permitió detectar y corregir problemas en caliente:

- Migration que intentaba re-crear un tipo PostgreSQL ya existente (`categoryenum`)
- Store de Pinia que guardaba `GoalRead` (sin `current`/`percentage`) en lugar de `GoalProgress`
- Línea de 101 caracteres violando la regla de estilo del proyecto
- División por cero en el cálculo de porcentaje

---

### 4. Verify (`verify`)

Skill de verificación runtime: arrancó el backend y frontend, navegó por las rutas reales en el browser (`/goals`, `/goals/new`, `/goals/:id/edit`), y probó casos borde (meta duplicada → 409, editar meta ajena → 404).

---

### 5. Finishing a Development Branch (`superpowers:finishing-a-development-branch`)

Verificó que los 27 tests pasen, ofreció las opciones de cierre (merge / PR / keep / discard) y gestionó el push al repositorio.

---

## Lo que se construyó

### Backend (Python/FastAPI)

- Modelo `Goal` con constraint único `(user_id, year, category)`
- Migración Alembic que reutiliza el tipo PostgreSQL compartido (`create_type=False`)
- 4 endpoints REST con auth JWT: GET (con progreso), POST, PUT, DELETE
- Progreso calculado en query time — no almacenado en DB
- 8 tests nuevos (TDD) → 27 tests en total

### Frontend (Vue 3/Pinia)

- Store `goals.js` con refresh automático post-mutación para mantener `GoalProgress` en caché
- `GoalCard.vue` con SVG circular progress (ring de 64px, verde al 100%)
- `GoalsView.vue` y `GoalFormView.vue` (ruta compartida create/edit)
- Widget en Dashboard: chips compactos con mini-ring + X/Y, oculto si no hay metas
- Link "Metas" en NavBar

---

## Principios de la cursada aplicados

| Principio | Cómo se vio hoy |
|---|---|
| **Diseño antes de código** | El skill de brainstorming bloqueó la implementación hasta que el spec estuvo aprobado |
| **TDD** | Cada tarea empezó con tests fallando; la implementación llegó después |
| **Subagentes con contexto limpio** | Cada subagente recibió exactamente el contexto necesario — sin historia de la sesión |
| **Revisión en dos etapas** | Spec compliance primero, code quality después — en ese orden |
| **YAGNI** | Sin features extra: no metas mensuales, no override manual, no notificaciones |
| **Commits frecuentes** | Un commit por tarea completada, mensajes descriptivos |
| **Skills como flujo de trabajo** | Todo el pipeline (brainstorm → plan → implement → verify → finish) coordinado por skills, sin improvisación |
