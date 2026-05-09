# Despliegue MVP

Según la fase 5, el MVP público beta puede iniciar con costo mensual cero:

- Frontend: Cloudflare Pages Free.
- Backend: Render Free Web Service.
- Base de datos: Supabase Free PostgreSQL o Neon Free.
- SSL: automático en Cloudflare/Render.
- Logs: stdout JSON de Render y agregador futuro.

## Render backend

Start command recomendado:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:$PORT
```

Healthcheck:

```text
GET /health
```

## Variables de producción

- `ENVIRONMENT=production`
- `DATABASE_URL`
- `JWT_SECRET`
- `CORS_ALLOWED_ORIGINS=https://nexovia.pages.dev`
- `FRONTEND_PUBLIC_URL=https://nexovia.pages.dev`
- `BACKEND_PUBLIC_URL=https://nexovia-api.onrender.com`

No usar filesystem local para datos de usuario en Render Free. Cualquier archivo futuro debe ir a almacenamiento gestionado.

