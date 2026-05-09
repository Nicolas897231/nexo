# Estado fase 1

## Listo

- Monorepo base.
- Backend FastAPI modular.
- Configuración por variables de entorno.
- Security headers.
- CORS por allowlist.
- Middleware de `request_id`.
- Logging JSON con redacción de campos sensibles.
- Manejo uniforme de errores.
- Modelos y migración inicial PostgreSQL con RLS.
- Endpoints iniciales de auth, usuarios, settings, finanzas, metas y reglas.
- Motor de reglas inicial sin ejecución de código arbitrario.
- Helpers de dinero con `Decimal`.
- Pruebas unitarias iniciales.

## Pendiente

- Frontend Next.js real en `apps/web`.
- CI/CD completo con secret scan, dependency scan y lint gates.
- Rate limit persistente con Redis.
- Recuperación de contraseña por email.
- MFA/TOTP futuro.
- Motor de reglas completo de fase 2.
- Simuladores completos de ahorro, vivir solo, carro y viaje.
- Workers async para recálculos pesados.
- Colección Bruno/Insomnia y pruebas Schemathesis/ZAP/k6.

## Nota sobre fuentes adjuntas

En la carpeta revisada `C:\Users\Nicolas\OneDrive - SENA\Escritorio\Nexo` estaban disponibles los documentos `.docx` y `metafinanzas_mockups_pantallas.zip`. No encontré `finanzas_app_fase3_codigo_ejemplo.zip`, por lo que esta fase se basó en los documentos disponibles y no en código de ejemplo externo.

## Verificación ejecutada

Desde `apps/api`:

- `pytest -p no:cacheprovider`: pruebas pasan.
- `ruff check app tests migrations`: sin errores.
- `ruff format --check app tests migrations`: formato correcto.
- `python -m compileall app tests migrations`: compilación de sintaxis correcta.
- `python -c "from app.main import create_app; app=create_app(); print(app.title)"`: app importable.
