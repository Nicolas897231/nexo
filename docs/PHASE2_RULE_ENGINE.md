# Fase 2 - Motor de Reglas

Esta fase implementa el motor determinístico de NexoVía según `finanzas_app_fase2_motor_reglas_detallado_v2.docx`.

## Decisiones implementadas

- El motor vive en código Python.
- Las reglas predefinidas, plantillas y reglas personalizadas viven en PostgreSQL.
- Las reglas son JSON declarativo validado, no código ejecutable.
- Las reglas personalizadas siempre pertenecen a `user_id`.
- Las evaluaciones guardan trazabilidad en `rule_evaluations`, `rule_evaluation_items`, `rule_evaluation_logs` y `audit_logs`.
- Los cálculos financieros están separados en `financial_math.py` y usan `Decimal`.

## Componentes

- `RuleRegistry`: carga reglas globales activas y reglas personalizadas activas del usuario.
- `FactBuilder`: construye facts desde datos persistidos del usuario.
- `RuleEngine`: valida y evalúa condiciones declarativas.
- `RecommendationBuilder`: arma `overall_status`, score, alertas, sugerencias y datos para UI.
- `RuleAuditWriter`: persiste evaluaciones y eventos de auditoría.

## DSL permitido

Condición simple:

```json
{"fact": "savings_rate", "operator": "lt", "value": "0.200000"}
```

Condición compuesta:

```json
{
  "all": [
    {"fact": "housing_cost_ratio", "operator": "lte", "value": "0.350000"},
    {"fact": "emergency_fund_months", "operator": "gte", "value": "3.000000"}
  ]
}
```

Expresión segura:

```json
{
  "left": {"formula": "sum", "fields": ["car_loan_payment", "car_monthly_expenses"]},
  "operator": "gt",
  "right": {"formula": "percent_of", "field": "monthly_net_income", "value": "0.20"}
}
```

## Seguridad

- No se usa `eval`, `exec` ni ejecución dinámica.
- Se rechazan tokens peligrosos como `eval`, `exec`, `import`, `lambda`, `__`, `subprocess`, `os.` y `sys.`.
- Operadores permitidos: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `between`, `in`.
- Fórmulas permitidas: `percent_of`, `sum`, `subtract`, `multiply`, `divide`.
- Facts permitidos definidos en `ALLOWED_FACTS`.
- Acciones permitidas: `WARN`, `FAIL`, `BLOCK`, `INFO`.
- Severidades permitidas: `INFO`, `SUCCESS`, `WARNING`, `CRITICAL`, `BLOCKING`, `HIGH_RISK`.
- Máximo 10 condiciones por grupo y máximo 50 reglas activas por usuario.
- Cada regla personalizada se consulta, edita, pausa o elimina filtrando por `user_id`.
- La migración de Fase 2 habilita RLS para `rule_evaluations`, `rule_evaluation_items` y `rule_change_log`.

## Endpoints

- `POST /api/v1/evaluations/profile`
- `POST /api/v1/evaluations/goals/{goal_id}`
- `GET /api/v1/rule-templates`
- `GET /api/v1/user-rules`
- `POST /api/v1/user-rules`
- `PATCH /api/v1/user-rules/{id}`
- `GET /api/v1/rule-evaluations/{id}`
- `GET /api/v1/rules/predefined`
- `POST /api/v1/rules/custom/validate`
- `POST /api/v1/rules/evaluate`
- `POST /api/v1/simulations/car`
- `POST /api/v1/simulations/live-alone`

## Reglas iniciales

La migración `20260504_0002_phase2_rule_engine.py` agrega plantillas y reglas base:

- General: `GEN-001` a `GEN-006`.
- Ahorro: `SAV-001`, `SAV-002`.
- Vivir solo: `LIVE-002`, `LIVE-005`.
- Carro: `CAR-002`, `CAR_TOTAL_MONTHLY_COST_MAX_RATIO`.
- Viaje: `TRV-004`, `TRV-005`.

## Pendiente

- Completar todas las reglas de Fase 2 que requieren facts todavía no modelados.
- Persistir snapshots de simulaciones si producto lo requiere.
- Agregar pruebas de integración con PostgreSQL real y RLS.
- Conectar frontend visual de constructor de reglas.
