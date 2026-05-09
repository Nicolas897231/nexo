# Arquitectura inicial

La fase 1 usa monorepo y backend modular monolítico, como indican los documentos del proyecto.

## Decisiones implementadas

- Backend: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2 y Alembic.
- API REST versionada en `/api/v1`.
- Frontend separado reservado en `apps/web`, preparado para Next.js/React.
- Persistencia principal: PostgreSQL/Supabase/Neon mediante `DATABASE_URL`.
- Montos: `Decimal` en Python, `NUMERIC(18,2)` en PostgreSQL y string decimal en JSON.
- Autenticación: JWT access token corto + refresh token rotativo.
- Autorización: ownership estricto por `user_id`.
- Reglas: engine seguro en código, reglas parametrizables en BD.
- Observabilidad: logs JSON con `request_id` y auditoría en tabla `audit_logs`.

## Capas backend

```text
router -> schemas -> service -> repository -> models/db
```

Los routers no consultan SQL directamente ni contienen reglas financieras. Los servicios orquestan casos de uso. Los repositorios aplican filtros por `user_id`.

## Preparación móvil

La app móvil futura consumirá los mismos contratos `/api/v1`, por lo que no se acopla lógica al frontend web.

