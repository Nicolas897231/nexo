"""initial phase 1 schema

Revision ID: 20260504_0001
Revises:
Create Date: 2026-05-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260504_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create extension if not exists pgcrypto;
        create extension if not exists citext;

        create table users (
            id uuid primary key default gen_random_uuid(),
            email citext unique not null,
            password_hash text not null,
            email_verified_at timestamptz,
            status varchar(20) not null default 'active'
                check (status in ('active','disabled','pending_verification','deleted')),
            token_version integer not null default 1,
            last_login_at timestamptz,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table user_profiles (
            user_id uuid primary key references users(id) on delete cascade,
            first_name varchar(80),
            last_name varchar(80),
            country_code char(2) not null default 'CO',
            city varchar(100),
            currency_code char(3) not null default 'COP',
            payday smallint check (payday between 1 and 31),
            income_frequency varchar(20)
                check (income_frequency is null or income_frequency in ('monthly','biweekly','weekly','variable'))
        );

        create table user_preferences (
            user_id uuid primary key references users(id) on delete cascade,
            theme_mode varchar(20) not null default 'system'
                check (theme_mode in ('system','light','dark')),
            accent_color varchar(30) not null default 'blue',
            dashboard_layout jsonb not null default '{}'::jsonb,
            notification_settings jsonb not null default '{}'::jsonb
        );

        create table refresh_tokens (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id) on delete cascade,
            token_hash text unique not null,
            family_id uuid not null,
            device_id varchar(120),
            user_agent text,
            ip_address inet,
            expires_at timestamptz not null,
            revoked_at timestamptz,
            created_at timestamptz not null default now()
        );

        create table login_attempts (
            id uuid primary key default gen_random_uuid(),
            email citext not null,
            ip_address inet,
            success boolean not null,
            reason varchar(80) not null,
            created_at timestamptz not null default now()
        );

        create table password_reset_tokens (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id) on delete cascade,
            token_hash text not null,
            expires_at timestamptz not null,
            used_at timestamptz
        );

        create table income_sources (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            name varchar(120) not null,
            source_type varchar(30) not null check (source_type in ('salary','freelance','business','other')),
            expected_amount numeric(18,2) not null check (expected_amount >= 0),
            frequency varchar(20) not null check (frequency in ('monthly','biweekly','weekly','variable')),
            is_active boolean not null default true,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table transaction_categories (
            id uuid primary key default gen_random_uuid(),
            user_id uuid references users(id),
            name varchar(80) not null,
            kind varchar(20) not null check (kind in ('income','expense','saving','debt')),
            parent_id uuid references transaction_categories(id),
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table financial_transactions (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            category_id uuid references transaction_categories(id),
            income_source_id uuid references income_sources(id),
            type varchar(20) not null check (type in ('income','expense','transfer','saving','debt_payment')),
            amount numeric(18,2) not null check (amount >= 0),
            currency_code char(3) not null default 'COP',
            transaction_date date not null,
            description varchar(255),
            is_fixed boolean not null default false,
            recurrence_rule jsonb,
            metadata jsonb,
            idempotency_key varchar(120),
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz,
            constraint uq_transactions_user_idempotency_key unique (user_id, idempotency_key)
        );

        create table debts (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            name varchar(120) not null,
            debt_type varchar(30) not null check (debt_type in ('credit_card','personal_loan','vehicle_loan','other')),
            principal_balance numeric(18,2) not null check (principal_balance >= 0),
            minimum_payment numeric(18,2) not null check (minimum_payment >= 0),
            interest_rate_annual numeric(9,6) check (interest_rate_annual is null or interest_rate_annual >= 0),
            due_day smallint check (due_day between 1 and 31),
            status varchar(20) not null default 'active' check (status in ('active','paid','paused')),
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table financial_snapshots (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            period_month date not null,
            total_income numeric(18,2) not null default 0 check (total_income >= 0),
            fixed_expenses numeric(18,2) not null default 0 check (fixed_expenses >= 0),
            variable_expenses numeric(18,2) not null default 0 check (variable_expenses >= 0),
            debt_payments numeric(18,2) not null default 0 check (debt_payments >= 0),
            savings_amount numeric(18,2) not null default 0 check (savings_amount >= 0),
            available_cashflow numeric(18,2) not null default 0,
            calculated_at timestamptz not null default now(),
            unique (user_id, period_month)
        );

        create table goals (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_type varchar(30) not null check (goal_type in ('saving','live_alone','buy_car','travel')),
            name varchar(120) not null,
            target_amount numeric(18,2) not null check (target_amount >= 0),
            current_amount numeric(18,2) not null default 0 check (current_amount >= 0),
            monthly_contribution numeric(18,2) not null default 0 check (monthly_contribution >= 0),
            target_date date,
            priority smallint not null default 3 check (priority between 1 and 5),
            status varchar(20) not null default 'planning'
                check (status in ('planning','active','paused','completed','not_viable')),
            strategy_id uuid,
            parameters jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table goal_contributions (
            id uuid primary key default gen_random_uuid(),
            goal_id uuid not null references goals(id) on delete cascade,
            user_id uuid not null references users(id),
            amount numeric(18,2) not null check (amount >= 0),
            contribution_date date not null
        );

        create table goal_events (
            id uuid primary key default gen_random_uuid(),
            goal_id uuid not null references goals(id) on delete cascade,
            event_type varchar(40) not null,
            payload jsonb
        );

        create table simulations (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            simulation_type varchar(40) not null check (simulation_type in ('saving','housing','car_financing','travel')),
            input_payload jsonb not null,
            result_payload jsonb not null,
            rule_engine_version varchar(30) not null default 'v1',
            created_at timestamptz not null default now()
        );

        create table car_purchase_scenarios (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            vehicle_reference_id uuid,
            vehicle_value numeric(18,2) not null check (vehicle_value >= 0),
            down_payment numeric(18,2) not null check (down_payment >= 0),
            loan_amount numeric(18,2) not null check (loan_amount >= 0),
            annual_interest_rate numeric(9,6) not null check (annual_interest_rate >= 0),
            term_months integer not null check (term_months > 0),
            monthly_payment numeric(18,2) not null check (monthly_payment >= 0),
            monthly_total_cost numeric(18,2) not null check (monthly_total_cost >= 0),
            insurance_monthly numeric(18,2) not null default 0 check (insurance_monthly >= 0),
            fuel_monthly numeric(18,2) not null default 0 check (fuel_monthly >= 0),
            maintenance_monthly numeric(18,2) not null default 0 check (maintenance_monthly >= 0),
            parking_monthly numeric(18,2) not null default 0 check (parking_monthly >= 0)
        );

        create table housing_scenarios (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            city varchar(100) not null,
            rent_amount numeric(18,2) not null check (rent_amount >= 0),
            utilities_amount numeric(18,2) not null check (utilities_amount >= 0),
            food_amount numeric(18,2) not null check (food_amount >= 0),
            moving_initial_cost numeric(18,2) not null check (moving_initial_cost >= 0),
            emergency_fund_required numeric(18,2) not null check (emergency_fund_required >= 0)
        );

        create table travel_scenarios (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            destination varchar(120) not null,
            travel_date date,
            flights_amount numeric(18,2) not null default 0 check (flights_amount >= 0),
            lodging_amount numeric(18,2) not null default 0 check (lodging_amount >= 0),
            food_amount numeric(18,2) not null default 0 check (food_amount >= 0),
            extras_amount numeric(18,2) not null default 0 check (extras_amount >= 0)
        );

        create table rule_templates (
            id uuid primary key default gen_random_uuid(),
            code varchar(80) unique not null,
            name varchar(120) not null,
            description text,
            allowed_fields jsonb not null default '{}'::jsonb,
            allowed_operators jsonb not null default '{}'::jsonb,
            schema_json jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table rule_definitions (
            id uuid primary key default gen_random_uuid(),
            code varchar(80) unique not null,
            scope varchar(40) not null,
            rule_type varchar(40) not null,
            condition_json jsonb not null,
            action_json jsonb not null,
            severity varchar(20) not null,
            version integer not null default 1,
            is_active boolean not null default true,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table user_rule_definitions (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            template_id uuid references rule_templates(id),
            name varchar(120) not null,
            scope varchar(40) not null,
            condition_json jsonb not null,
            action_json jsonb not null,
            priority integer not null default 100,
            version integer not null default 1,
            is_active boolean not null default true,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create table rule_evaluation_logs (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            rule_code varchar(80) not null,
            input_context_hash varchar(128),
            result_json jsonb not null,
            triggered boolean not null,
            created_at timestamptz not null default now()
        );

        create table audit_logs (
            id uuid primary key default gen_random_uuid(),
            user_id uuid,
            actor_user_id uuid references users(id) on delete set null,
            event_type varchar(80) not null,
            entity_type varchar(80),
            entity_id uuid,
            request_id uuid,
            ip_address inet,
            user_agent text,
            before_state jsonb,
            after_state jsonb,
            created_at timestamptz not null default now()
        );

        create table alerts (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            goal_id uuid references goals(id),
            alert_type varchar(60) not null,
            severity varchar(20) not null check (severity in ('info','warning','danger')),
            message text not null,
            payload jsonb,
            status varchar(20) not null default 'active' check (status in ('active','dismissed','resolved')),
            created_at timestamptz not null default now(),
            resolved_at timestamptz
        );

        create index ix_refresh_tokens_user_family on refresh_tokens(user_id, family_id);
        create index ix_login_attempts_email_created on login_attempts(email, created_at desc);
        create index ix_login_attempts_ip_created on login_attempts(ip_address, created_at desc);
        create index ix_income_sources_user on income_sources(user_id);
        create index ix_transaction_categories_user_kind on transaction_categories(user_id, kind);
        create index ix_financial_transactions_user_date on financial_transactions(user_id, transaction_date desc);
        create index ix_financial_transactions_user_type_date on financial_transactions(user_id, type, transaction_date desc);
        create index ix_debts_user on debts(user_id);
        create index ix_goals_user_status_priority on goals(user_id, status, priority);
        create index ix_goal_contributions_user_goal_date on goal_contributions(user_id, goal_id, contribution_date desc);
        create index ix_simulations_user_created on simulations(user_id, created_at desc);
        create index ix_user_rule_definitions_user_scope_priority on user_rule_definitions(user_id, scope, is_active, priority);
        create index ix_rule_evaluation_logs_user_created on rule_evaluation_logs(user_id, created_at desc);
        create index ix_audit_logs_user_created on audit_logs(user_id, created_at desc);
        create index ix_audit_logs_request_id on audit_logs(request_id);
        create index ix_alerts_user_status on alerts(user_id, status, created_at desc);

        insert into rule_templates (code, name, description, allowed_fields, allowed_operators, schema_json)
        values
        (
            'CATEGORY_PERCENT_LIMIT',
            'Límite por porcentaje',
            'Permite alertar cuando un fact supera un porcentaje definido.',
            '["monthly_available","savings_rate","debt_payment_ratio","housing_cost_ratio","car_total_monthly_ratio"]'::jsonb,
            '["gt","gte","lt","lte","between"]'::jsonb,
            '{"value": "string decimal proporcional, ejemplo 0.300000"}'::jsonb
        ),
        (
            'AMOUNT_LIMIT',
            'Límite por monto',
            'Permite alertar cuando un monto supera un valor definido.',
            '["rent_amount","car_loan_payment","emergency_fund_amount","goal_required_monthly"]'::jsonb,
            '["gt","gte","lt","lte","between"]'::jsonb,
            '{"value": "string decimal"}'::jsonb
        );

        insert into rule_definitions (code, scope, rule_type, condition_json, action_json, severity, version)
        values
        (
            'GEN-002',
            'general',
            'LIQUIDITY',
            '{"fact":"monthly_available","operator":"lte","value":"0.000000"}'::jsonb,
            '{"severity":"WARNING","message":"Tu capacidad mensual disponible no es positiva.","recommendation":"Revisa ingresos y gastos antes de crear metas nuevas."}'::jsonb,
            'WARNING',
            1
        );
        """
    )
    _enable_rls()


def downgrade() -> None:
    op.execute(
        """
        drop table if exists alerts cascade;
        drop table if exists audit_logs cascade;
        drop table if exists rule_evaluation_logs cascade;
        drop table if exists user_rule_definitions cascade;
        drop table if exists rule_definitions cascade;
        drop table if exists rule_templates cascade;
        drop table if exists travel_scenarios cascade;
        drop table if exists housing_scenarios cascade;
        drop table if exists car_purchase_scenarios cascade;
        drop table if exists simulations cascade;
        drop table if exists goal_events cascade;
        drop table if exists goal_contributions cascade;
        drop table if exists goals cascade;
        drop table if exists financial_snapshots cascade;
        drop table if exists debts cascade;
        drop table if exists financial_transactions cascade;
        drop table if exists transaction_categories cascade;
        drop table if exists income_sources cascade;
        drop table if exists password_reset_tokens cascade;
        drop table if exists login_attempts cascade;
        drop table if exists refresh_tokens cascade;
        drop table if exists user_preferences cascade;
        drop table if exists user_profiles cascade;
        drop table if exists users cascade;
        """
    )


def _enable_rls() -> None:
    user_tables = [
        "user_profiles",
        "user_preferences",
        "income_sources",
        "financial_transactions",
        "debts",
        "financial_snapshots",
        "goals",
        "goal_contributions",
        "simulations",
        "car_purchase_scenarios",
        "housing_scenarios",
        "travel_scenarios",
        "user_rule_definitions",
        "rule_evaluation_logs",
        "alerts",
    ]
    for table_name in user_tables:
        user_column = "user_id"
        op.execute(f"alter table {table_name} enable row level security;")
        op.execute(
            f"""
            create policy {table_name}_owner_select on {table_name}
            for select using (
                {user_column} = nullif(current_setting('app.current_user_id', true), '')::uuid
            );
            create policy {table_name}_owner_insert on {table_name}
            for insert with check (
                {user_column} = nullif(current_setting('app.current_user_id', true), '')::uuid
            );
            create policy {table_name}_owner_update on {table_name}
            for update using (
                {user_column} = nullif(current_setting('app.current_user_id', true), '')::uuid
            ) with check (
                {user_column} = nullif(current_setting('app.current_user_id', true), '')::uuid
            );
            create policy {table_name}_owner_delete on {table_name}
            for delete using (
                {user_column} = nullif(current_setting('app.current_user_id', true), '')::uuid
            );
            """
        )

    op.execute("alter table transaction_categories enable row level security;")
    op.execute(
        """
        create policy transaction_categories_read on transaction_categories
        for select using (
            user_id is null or user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy transaction_categories_write on transaction_categories
        for all using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        ) with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        """
    )

    op.execute("alter table audit_logs enable row level security;")
    op.execute(
        """
        create policy audit_logs_owner_read on audit_logs
        for select using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or actor_user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy audit_logs_owner_insert on audit_logs
        for insert with check (
            user_id is null
            or user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
            or actor_user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        """
    )
