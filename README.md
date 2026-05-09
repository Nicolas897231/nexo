# NexoVia

NexoVia es una aplicación web de finanzas personales orientada a metas. Esta base inicial sigue los documentos del proyecto: arquitectura modular con FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, seguridad desde el inicio, montos con `Decimal`/`NUMERIC` y frontend web separado.

## Estructura

```text
apps/
  api/        Backend FastAPI modular.
  web/        Reserva para Next.js/React.
docs/         Decisiones, seguridad, endpoints y pendientes.
infra/        Docker y despliegue del MVP.
packages/     Contratos compartidos futuros.
```

## Ejecutar backend local

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item ..\..\.env.example .env
# Edita .env con secretos locales fuertes y DATABASE_URL real.
alembic upgrade head
uvicorn app.main:app --reload
```

Endpoints útiles:

- `GET /health`
- `GET /docs`
- `GET /openapi.json`
- API versionada en `/api/v1`

## Pruebas

```powershell
cd apps/api
pytest -p no:cacheprovider
ruff check app tests migrations
ruff format --check app tests migrations
```

## Seguridad

Las medidas iniciales están documentadas en [docs/SECURITY.md](docs/SECURITY.md): variables de entorno, CORS por allowlist, headers HTTP, JWT, refresh tokens hasheados, ownership por `user_id`, RLS PostgreSQL, validación de inputs, logging sin secretos y auditoría.

El motor de reglas de Fase 2 está documentado en [docs/PHASE2_RULE_ENGINE.md](docs/PHASE2_RULE_ENGINE.md).

La API MVP de Fase 3, endpoints, QA y decisiones quedan documentados en [docs/PHASE3_API_QA.md](docs/PHASE3_API_QA.md) y [docs/ENDPOINTS.md](docs/ENDPOINTS.md).

La base frontend de Fase 4 queda documentada en [docs/PHASE4_FRONTEND_UX_UI.md](docs/PHASE4_FRONTEND_UX_UI.md).

El despliegue LAN en los servidores `10.10.10.240`, `10.10.10.241` y `10.10.10.242` queda documentado en [docs/PRODUCTION_LAN_DEPLOYMENT.md](docs/PRODUCTION_LAN_DEPLOYMENT.md).

## Fuente documental usada

La base se construyó usando como fuente principal:

- `finanzas_app_fase1_arquitectura_bd_seguridad_v2.docx`
- `finanzas_app_fase2_motor_reglas_detallado_v2.docx`
- `finanzas_app_fase3_api_estructura_codigo_qa.docx`
- `metafinanzas_fase4_pantallas_completas_especificacion.docx`
- `nexovia_fase5_publicacion_ssl_dominio_monetizacion_hosting.docx`

`MetaFinanzas` se interpreta como nombre histórico. El producto final y los identificadores nuevos usan `NexoVia`/`NexoVía`.
