# Seguridad de NexoVia

## Controles agregados en Fase 3

- Recuperacion y cambio de contrasena usan tokens temporales hasheados; `forgot-password` responde generico para no filtrar si un email existe.
- Al cambiar o resetear contrasena se incrementa `token_version` y se revocan refresh tokens activos.
- Los endpoints documentados de Fase 3 usan `user_id` del token y responden 404 ante recursos ajenos.
- `movements` acepta `movement_type` como alias del campo historico `type`; el monto sigue siendo string decimal y se rechazan floats.
- Las simulaciones se persisten por usuario y solo pueden consultarse o convertirse a meta por su propietario.
- `alerts` y `audit/activity` exponen unicamente registros propios.
- `user_distributions` tiene RLS en la migracion de Fase 3, igual que el resto de datos por usuario.
- Reportes exportables, busquedas externas y email real quedan pendientes hasta contar con contratos/adaptadores seguros.

Este documento registra los controles implementados desde la base inicial. NexoVia maneja información financiera personal, por lo que la seguridad no queda aplazada para fases posteriores.

## Secretos y variables de entorno

- No hay API keys, contraseñas, tokens ni secretos reales en el código.
- `.env` y variantes reales están ignoradas por Git.
- `.env.example` contiene solo nombres de variables y valores de reemplazo.
- Secretos requeridos por el backend:
  - `DATABASE_URL`
  - `JWT_SECRET`
  - credenciales SMTP futuras si se activa email transaccional.

## Autenticación y sesiones

- Login con email y contraseña.
- Contraseñas hasheadas con Argon2id mediante `argon2-cffi`.
- Access token JWT corto, por defecto 15 minutos.
- Refresh token rotativo, por defecto 30 días.
- El refresh token se guarda solo como hash SHA-256, nunca plano.
- `token_version` permite invalidar sesiones al cambiar contraseña o cerrar todos los dispositivos.
- Los errores de login son genéricos para no revelar si un email existe.

## Autorización y aislamiento por usuario

- No hay roles en el MVP; todos los usuarios operan únicamente sobre sus propios datos.
- El backend toma `user_id` del token validado. No acepta `user_id` del cliente para operar recursos propios.
- Repositorios de movimientos, metas y reglas filtran por `user_id`.
- Los accesos a recursos ajenos deben responder 404 para no revelar existencia.

## Row Level Security en PostgreSQL/Supabase

- La migración inicial habilita RLS en tablas con datos de usuario.
- Las políticas usan `current_setting('app.current_user_id', true)` como segunda línea de defensa.
- La aplicación sigue filtrando por `user_id` en queries. RLS no reemplaza autorización en servicios/repositorios.
- Para operaciones autenticadas que dependan de RLS, la sesión DB debe establecer `app.current_user_id` dentro de la transacción.

## Validación de inputs

- Los routers usan schemas Pydantic separados para Create, Update y Read.
- Montos monetarios llegan como string decimal, se convierten a `Decimal` y se cuantizan con `ROUND_HALF_UP`.
- Se rechazan floats en payloads monetarios.
- Se validan enums, longitudes de texto, fechas, UUIDs, emails, contraseñas y rangos.
- Las reglas personalizadas usan JSON declarativo con lista blanca de facts y operadores. No existe `eval`, `exec` ni código dinámico de usuario.

## CORS

- CORS se configura por allowlist en `CORS_ALLOWED_ORIGINS`.
- En local se permiten `http://localhost:3000` y `http://127.0.0.1:3000`.
- En producción está prohibido usar `*`; se deben configurar los dominios reales, por ejemplo `https://nexovia.pages.dev`.
- Se permiten credenciales porque la estrategia final puede usar cookies HttpOnly para refresh tokens.

## Rate limit inicial

- Hay un middleware básico en memoria para `register`, `login` y `refresh`.
- Este control reduce fuerza bruta en local/MVP, pero en producción debe migrar a Redis o un WAF para funcionar correctamente con múltiples instancias.

## Motor de reglas

- Las reglas personalizadas son JSON declarativo, no código.
- El motor rechaza operadores, facts, fórmulas y acciones fuera de listas blancas.
- No se usa `eval`, `exec` ni ejecución dinámica.
- Las reglas personalizadas se filtran siempre por `user_id`.
- La Fase 2 agrega auditoría para creación, edición, activación, pausa, eliminación y evaluación de reglas.
- Detalle completo en [PHASE2_RULE_ENGINE.md](PHASE2_RULE_ENGINE.md).

## Security headers

El middleware agrega:

- `Content-Security-Policy`: reduce impacto de XSS e inyección de contenido.
- `X-Frame-Options: DENY`: evita clickjacking.
- `X-Content-Type-Options: nosniff`: evita MIME sniffing.
- `Referrer-Policy: no-referrer`: evita filtrar URLs sensibles.
- `Permissions-Policy`: desactiva permisos del navegador que la API no necesita.
- `Strict-Transport-Security`: se activa solo fuera de local para exigir HTTPS.

## Logging y auditoría

- Cada request tiene `request_id` propagado por `X-Request-ID` o generado por el backend.
- Los logs son JSON estructurado a stdout.
- Se redactan campos sensibles: `password`, `password_hash`, `access_token`, `refresh_token`, `reset_token`, `authorization`, `cookie`.
- `audit_logs` vive en PostgreSQL y registra eventos funcionales y de seguridad.
- La auditoría guarda estados filtrados; no debe duplicar datos sensibles innecesarios.

## Superficie de ataque

- Endpoints financieros requieren autenticación.
- Errores internos no exponen stack traces al cliente.
- CORS estricto en producción.
- No se exponen modelos SQLAlchemy directamente.
- Las migraciones definen FKs, checks e índices para preservar integridad.
