# NexoVia Produccion LAN 10.10.10.0/24

Servidores objetivo:

- API: `10.10.10.240`
- PostgreSQL: `10.10.10.241`
- Web: `10.10.10.242`

La web debe llamar a `/api/v1` en su mismo origen. Next.js reescribe `/api/*` hacia `http://10.10.10.240:8000/api/*`, lo que permite cookies HttpOnly sin guardar tokens en localStorage.

Para HTTP dentro de LAN se usa `SESSION_COOKIE_SECURE=false`. En una salida publica con HTTPS debe cambiarse a `true`.
