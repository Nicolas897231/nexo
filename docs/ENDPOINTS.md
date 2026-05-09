# Endpoints Fase 3

Todos los endpoints de negocio viven bajo `/api/v1`. `GET /health`, `GET /api/v1/health`, `/docs` y `/openapi.json` son publicos; el resto requiere autenticacion salvo endpoints de auth publicos.

## Auth

- `POST /api/v1/auth/register`: crea usuario, perfil y preferencias por defecto.
- `POST /api/v1/auth/login`: autentica y emite access/refresh token.
- `POST /api/v1/auth/refresh`: rota refresh token.
- `POST /api/v1/auth/logout`: revoca refresh token.
- `POST /api/v1/auth/forgot-password`: solicita recuperacion con respuesta generica.
- `POST /api/v1/auth/reset-password`: cambia contrasena con token temporal.
- `POST /api/v1/auth/change-password`: cambia contrasena autenticado y revoca sesiones.
- `GET /api/v1/auth/me`: identidad minima autenticada.

## Usuario

- `GET/PATCH /api/v1/users/me`: perfil propio.
- `GET/PATCH /api/v1/users/me/preferences`: preferencias propias.
- `GET/PATCH /api/v1/settings/me`: alias historico de preferencias.
- `GET /api/v1/users/me/security-settings`: configuracion de seguridad visible.
- `GET /api/v1/users/me/activity`: actividad propia basada en auditoria.

## Finanzas

- `GET/PUT/PATCH /api/v1/financial-profile`: perfil financiero propio.
- `GET /api/v1/financial-profile/health-score`: puntaje financiero mensual.
- `POST /api/v1/financial-profile/recalculate`: recalcula snapshot mensual.
- `GET/POST /api/v1/categories`: categorias globales y propias.
- `PATCH/DELETE /api/v1/categories/{category_id}`: modifica categoria propia.
- `GET/POST /api/v1/income-sources`: fuentes de ingreso propias.
- `PATCH/DELETE /api/v1/income-sources/{source_id}`: modifica fuente propia.
- `GET/POST /api/v1/movements`: movimientos por contrato Fase 3.
- `GET/PATCH/DELETE /api/v1/movements/{movement_id}`: movimiento propio.
- `GET /api/v1/movements/summary/monthly`: resumen mensual.
- `GET/POST /api/v1/finance/transactions`: alias historico de movimientos.
- `GET /api/v1/finance/snapshot`: resumen mensual historico.

## Deudas, Estrategias Y Metas

- `GET/POST /api/v1/debts`: deudas propias.
- `PATCH /api/v1/debts/{debt_id}`: edita deuda propia.
- `POST /api/v1/debts/{debt_id}/payments`: registra pago y movimiento.
- `GET /api/v1/debts/strategy`: orden de pago recomendado tipo avalancha.
- `GET /api/v1/strategies`: estrategias predeterminadas.
- `GET /api/v1/strategies/{strategy_id}`: detalle de estrategia.
- `POST /api/v1/strategies/preview`: vista previa por ingreso mensual.
- `POST /api/v1/distributions`: guarda distribucion propia.
- `GET /api/v1/distributions/current`: ultima distribucion activa.
- `PATCH /api/v1/distributions/{distribution_id}`: edita distribucion propia.
- `GET/POST /api/v1/goals`: metas propias.
- `GET/PATCH/DELETE /api/v1/goals/{goal_id}`: meta propia.
- `POST /api/v1/goals/{goal_id}/contributions`: registra aporte.
- `GET /api/v1/goals/{goal_id}/timeline`: timeline de aportes.

## Reglas Y Simulaciones

- `GET /api/v1/rules/templates`: plantillas aprobadas.
- `GET /api/v1/rules/predefined`: reglas globales activas versionadas.
- `GET /api/v1/rules/custom`: reglas personalizadas del usuario.
- `POST /api/v1/rules/custom/validate`: valida regla declarativa.
- `POST /api/v1/rules/custom`: crea regla personalizada.
- `PATCH/DELETE /api/v1/rules/custom/{rule_id}`: modifica regla propia.
- `POST /api/v1/rules/evaluate`: evaluacion segura del motor.
- `GET /api/v1/decision-engine/recommendations`: recomendaciones generales.
- `POST /api/v1/evaluations/profile`: evalua perfil financiero.
- `POST /api/v1/evaluations/goals/{goal_id}`: evalua meta propia.
- `POST /api/v1/simulations/savings`: simula ahorro.
- `POST /api/v1/simulations/living-alone`: simula vivir solo.
- `POST /api/v1/simulations/live-alone`: alias historico.
- `POST /api/v1/simulations/car`: simula compra de carro.
- `POST /api/v1/simulations/travel`: simula viaje.
- `GET /api/v1/simulations/{simulation_id}`: consulta simulacion propia.
- `POST /api/v1/simulations/{simulation_id}/convert-to-goal`: crea meta desde simulacion.

## Dashboard, Alertas Y Auditoria

- `GET /api/v1/dashboard/summary`: resumen mensual de ingresos, egresos, metas y alertas.
- `GET /api/v1/dashboard/cashflow`: serie mensual por fecha y tipo.
- `GET /api/v1/alerts`: alertas activas propias.
- `PATCH /api/v1/alerts/{alert_id}/read`: marca alerta propia como leida.
- `GET /api/v1/audit/activity`: auditoria propia paginada.

## Pendientes Deliberados

- Reportes exportables quedan para fase posterior porque el contrato de Fase 3 no define rutas concretas.
- Busquedas externas reales y envio transaccional de email quedan detras de adaptadores futuros.
