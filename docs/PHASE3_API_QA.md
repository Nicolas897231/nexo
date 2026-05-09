# Fase 3 API, Estructura Y QA

## Implementado

- API versionada en `/api/v1` con routers por dominio.
- Separacion `router -> schema -> service/repository -> model` para los dominios nuevos o extendidos.
- Endpoints exactos de Fase 3 para auth, users, financial profile, categories, income sources, movements, debts, strategies, distributions, goals, rules, simulations, dashboard, alerts y audit.
- Compatibilidad con rutas historicas de Fase 1/2, por ejemplo `/finance/transactions`, `/settings/me` y `/simulations/live-alone`.
- Migracion `20260507_0003_phase3_api_contract.py` para distribuciones de usuario, RLS y categorias base.

## Decisiones Tecnicas

- `financial-profile.monthly_income` se materializa como fuente de ingreso principal para no duplicar datos financieros.
- `movements` reutiliza `financial_transactions`; acepta `movement_type` como alias de `type`.
- Estrategias son catalogo backend deterministico; distribuciones personalizadas viven en `user_distributions`.
- Simulaciones se guardan en `simulations` para permitir consulta posterior y conversion a meta.
- Reportes exportables quedan pendientes porque Fase 3 no define contrato concreto.
- Envio real de correo para recuperacion de contrasena queda pendiente; el backend ya genera y guarda token hasheado.

## Seguridad Y Validacion

- Todos los endpoints privados dependen de `get_current_user`.
- No se acepta `user_id` desde el cliente para ownership.
- Montos: string decimal en API, `Decimal` en Python y `NUMERIC` en PostgreSQL.
- Floats monetarios son rechazados.
- Reglas siguen siendo declarativas y validadas con listas blancas de facts, operadores y acciones.
- Auditoria registra cambios relevantes sin contrasenas, tokens ni secretos.
- RLS se mantiene para datos por usuario y se agrega a `user_distributions`.

## Pruebas

Ejecutar unitarias:

```powershell
cd apps/api
pytest -p no:cacheprovider
```

Ejecutar calidad:

```powershell
ruff check app tests migrations
ruff format --check app tests migrations
```

La suite nueva valida que OpenAPI exponga el contrato de Fase 3, que health versionado sea publico, que los montos rechacen floats y que las distribuciones sumen `1.000000`.

## Pendiente

- Pruebas de integracion completas contra PostgreSQL usando `TEST_DATABASE_URL`.
- Adaptador SMTP/transaccional para entregar tokens de recuperacion.
- Reportes exportables y proveedores externos cuando el contrato lo defina.
- Rate limit distribuido con Redis/WAF para produccion multi-instancia.
