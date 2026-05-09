"""phase 2 rule engine

Revision ID: 20260504_0002
Revises: 20260504_0001
Create Date: 2026-05-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260504_0002"
down_revision: str | None = "20260504_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        alter table rule_definitions add column if not exists name varchar(120) not null default '';
        alter table rule_definitions add column if not exists description text;
        alter table rule_definitions add column if not exists priority integer not null default 100;

        create table if not exists rule_evaluations (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            request_id uuid,
            scope varchar(40) not null,
            status varchar(40) not null,
            score integer not null check (score between 0 and 100),
            facts_snapshot jsonb not null default '{}'::jsonb,
            response_json jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now()
        );

        create table if not exists rule_evaluation_items (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            evaluation_id uuid not null references rule_evaluations(id) on delete cascade,
            rule_id uuid,
            rule_code varchar(80) not null,
            rule_version integer not null,
            status varchar(20) not null,
            severity varchar(20) not null,
            facts_snapshot jsonb not null default '{}'::jsonb,
            output_message text
        );

        create table if not exists rule_change_log (
            id uuid primary key default gen_random_uuid(),
            rule_id uuid not null references user_rule_definitions(id),
            changed_by_user_id uuid not null references users(id),
            before_json jsonb,
            after_json jsonb,
            created_at timestamptz not null default now()
        );

        create index if not exists ix_rule_evaluations_user_created
            on rule_evaluations(user_id, created_at desc);
        create index if not exists ix_rule_evaluations_request_id
            on rule_evaluations(request_id);
        create index if not exists ix_rule_evaluation_items_eval
            on rule_evaluation_items(evaluation_id);
        create index if not exists ix_rule_change_log_rule_created
            on rule_change_log(rule_id, created_at desc);
        create index if not exists ix_rule_change_log_user_created
            on rule_change_log(changed_by_user_id, created_at desc);

        alter table rule_evaluations enable row level security;
        alter table rule_evaluation_items enable row level security;
        alter table rule_change_log enable row level security;

        drop policy if exists rule_evaluations_owner_select on rule_evaluations;
        drop policy if exists rule_evaluations_owner_insert on rule_evaluations;
        drop policy if exists rule_evaluation_items_owner_select on rule_evaluation_items;
        drop policy if exists rule_evaluation_items_owner_insert on rule_evaluation_items;
        drop policy if exists rule_change_log_owner_read on rule_change_log;
        drop policy if exists rule_change_log_owner_insert on rule_change_log;

        create policy rule_evaluations_owner_select on rule_evaluations
        for select using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy rule_evaluations_owner_insert on rule_evaluations
        for insert with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy rule_evaluation_items_owner_select on rule_evaluation_items
        for select using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy rule_evaluation_items_owner_insert on rule_evaluation_items
        for insert with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy rule_change_log_owner_read on rule_change_log
        for select using (
            changed_by_user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy rule_change_log_owner_insert on rule_change_log
        for insert with check (
            changed_by_user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );

        insert into rule_templates (code, name, description, allowed_fields, allowed_operators, schema_json)
        values
        (
            'MINIMUM_GOAL',
            'Meta mínima',
            'Permite exigir una meta o ahorro mínimo.',
            '["savings_rate","goal_progress_ratio","goal_required_monthly"]'::jsonb,
            '["gt","gte","lt","lte"]'::jsonb,
            '{"value":"string decimal"}'::jsonb
        ),
        (
            'DECISION_BLOCK',
            'Bloqueo de decisión',
            'Permite pausar una recomendación cuando falta una condición previa.',
            '["emergency_fund_months","monthly_available","remaining_after_goals"]'::jsonb,
            '["gt","gte","lt","lte"]'::jsonb,
            '{"status":"BLOCK","severity":"BLOCKING"}'::jsonb
        ),
        (
            'DEADLINE_ALERT',
            'Alerta de vencimiento',
            'Permite alertar cuando una meta no avanza al ritmo esperado.',
            '["goal_progress_ratio","goal_required_monthly"]'::jsonb,
            '["gt","gte","lt","lte","between"]'::jsonb,
            '{"value":"string decimal"}'::jsonb
        )
        on conflict (code) do nothing;
        """
    )
    _upsert_global_rules()


def downgrade() -> None:
    op.execute(
        """
        drop table if exists rule_change_log cascade;
        drop table if exists rule_evaluation_items cascade;
        drop table if exists rule_evaluations cascade;
        alter table rule_definitions drop column if exists priority;
        alter table rule_definitions drop column if exists description;
        alter table rule_definitions drop column if exists name;
        """
    )


def _upsert_global_rules() -> None:
    rules = [
        (
            "GEN-001",
            "Datos mínimos completos",
            "general",
            "CORE",
            10,
            '{"fact":"monthly_net_income","operator":"lte","value":"0.000000"}',
            '{"status":"BLOCK","severity":"BLOCKING","message":"Debes registrar tu ingreso mensual antes de simular.","recommendation":"Completa tu perfil financiero."}',
            "BLOCKING",
        ),
        (
            "GEN-002",
            "Capacidad mensual positiva",
            "general",
            "LIQUIDITY",
            20,
            '{"fact":"monthly_available","operator":"lte","value":"0.000000"}',
            '{"status":"WARN","severity":"WARNING","message":"Tu capacidad mensual disponible no es positiva.","recommendation":"Revisa ingresos y gastos antes de crear metas nuevas."}',
            "WARNING",
        ),
        (
            "GEN-003",
            "Ahorro saludable base",
            "general",
            "SAVINGS",
            30,
            '{"fact":"savings_rate","operator":"lt","value":"0.200000"}',
            '{"status":"WARN","severity":"WARNING","message":"Tu ahorro mensual está por debajo del 20% saludable.","recommendation":"Ajusta gastos o define un ahorro mínimo."}',
            "WARNING",
        ),
        (
            "GEN-004",
            "Deuda controlada",
            "general",
            "DEBT",
            40,
            '{"fact":"debt_payment_ratio","operator":"gt","value":"0.350000"}',
            '{"status":"FAIL","severity":"CRITICAL","message":"Tus pagos de deuda superan el 35% de tu ingreso.","recommendation":"Prioriza reducción de deuda antes de asumir metas nuevas."}',
            "CRITICAL",
        ),
        (
            "GEN-005",
            "Fondo de emergencia mínimo",
            "general",
            "EMERGENCY_FUND",
            50,
            '{"fact":"emergency_fund_months","operator":"lt","value":"3.000000"}',
            '{"status":"WARN","severity":"WARNING","message":"Tu fondo de emergencia está por debajo de 3 meses.","recommendation":"Fortalece tu fondo antes de metas aspiracionales."}',
            "WARNING",
        ),
        (
            "GEN-006",
            "No comprometer liquidez",
            "general",
            "LIQUIDITY",
            60,
            '{"left":{"fact":"remaining_after_goals"},"operator":"lt","right":{"fact":"minimum_liquidity_buffer"}}',
            '{"status":"BLOCK","severity":"BLOCKING","message":"El plan compromete tu margen mínimo de liquidez.","recommendation":"Reduce aportes a metas o aumenta el plazo."}',
            "BLOCKING",
        ),
        (
            "SAV-001",
            "Monto objetivo mayor a cero",
            "saving",
            "GOAL_VALIDATION",
            110,
            '{"fact":"target_amount","operator":"lte","value":"0.000000"}',
            '{"status":"BLOCK","severity":"BLOCKING","message":"La meta de ahorro debe tener un monto objetivo mayor a cero."}',
            "BLOCKING",
        ),
        (
            "SAV-002",
            "Aporte viable",
            "saving",
            "GOAL_VALIDATION",
            120,
            '{"left":{"fact":"monthly_contribution"},"operator":"gt","right":{"fact":"monthly_available"}}',
            '{"status":"WARN","severity":"WARNING","message":"El aporte mensual supera tu disponible.","recommendation":"Reduce el aporte o amplía el plazo."}',
            "WARNING",
        ),
        (
            "LIVE-002",
            "Máximo tolerable de vivienda",
            "housing",
            "LIMIT",
            210,
            '{"fact":"housing_cost_ratio","operator":"gt","value":"0.350000"}',
            '{"status":"FAIL","severity":"HIGH_RISK","message":"El costo total de vivienda supera el 35% de tu ingreso.","recommendation":"Busca un arriendo menor o aplaza la mudanza."}',
            "HIGH_RISK",
        ),
        (
            "LIVE-005",
            "Fondo de emergencia previo",
            "housing",
            "SAFETY",
            220,
            '{"fact":"emergency_fund_months","operator":"lt","value":"3.000000"}',
            '{"status":"WARN","severity":"WARNING","message":"No tienes aún 3 meses de fondo de emergencia para vivir solo.","recommendation":"Crea una meta de fondo antes de mudarte."}',
            "WARNING",
        ),
        (
            "CAR-002",
            "Cuota máxima tolerable del carro",
            "car",
            "LIMIT",
            310,
            '{"fact":"car_loan_payment_ratio","operator":"gt","value":"0.150000"}',
            '{"status":"WARN","severity":"CRITICAL","message":"La cuota del carro supera el límite saludable para tu ingreso.","developer_message":"car_loan_payment_ratio > 0.15","suggestions":["Aumentar cuota inicial","Buscar un carro de menor valor","Revisar plazo y tasa"]}',
            "CRITICAL",
        ),
        (
            "CAR_TOTAL_MONTHLY_COST_MAX_RATIO",
            "Costo mensual total del carro",
            "car",
            "LIMIT",
            320,
            '{"left":{"formula":"sum","fields":["car_loan_payment","car_monthly_expenses"]},"operator":"gt","right":{"formula":"percent_of","field":"monthly_net_income","value":"0.20"}}',
            '{"status":"FAIL","severity":"HIGH_RISK","message":"El costo mensual total del carro supera el 20% de tu ingreso.","recommendation":"Reduce el valor del carro, aumenta la cuota inicial o revisa si la meta debe aplazarse."}',
            "HIGH_RISK",
        ),
        (
            "TRV-004",
            "Viaje viable",
            "travel",
            "GOAL_VALIDATION",
            410,
            '{"left":{"fact":"goal_required_monthly"},"operator":"gt","right":{"fact":"monthly_available"}}',
            '{"status":"WARN","severity":"WARNING","message":"El aporte mensual requerido para el viaje supera tu disponible.","recommendation":"Cambia la fecha, baja el presupuesto o aumenta el ahorro."}',
            "WARNING",
        ),
        (
            "TRV-005",
            "No desplazar obligaciones",
            "travel",
            "SAFETY",
            420,
            '{"fact":"remaining_after_goals","operator":"lt","value":"0.000000"}',
            '{"status":"BLOCK","severity":"BLOCKING","message":"El viaje desplaza obligaciones financieras básicas.","recommendation":"Cambia fecha, baja presupuesto o reduce aporte mensual."}',
            "BLOCKING",
        ),
    ]
    for code, name, scope, rule_type, priority, condition, action, severity in rules:
        op.execute(
            f"""
            insert into rule_definitions
                (code, name, scope, rule_type, priority, condition_json, action_json, severity, version, is_active)
            values
                ('{code}', '{name}', '{scope}', '{rule_type}', {priority},
                 '{condition}'::jsonb, '{action}'::jsonb, '{severity}', 1, true)
            on conflict (code) do update set
                name = excluded.name,
                scope = excluded.scope,
                rule_type = excluded.rule_type,
                priority = excluded.priority,
                condition_json = excluded.condition_json,
                action_json = excluded.action_json,
                severity = excluded.severity,
                version = rule_definitions.version + 1,
                is_active = true;
            """
        )
