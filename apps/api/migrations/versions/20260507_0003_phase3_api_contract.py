"""phase 3 api contract

Revision ID: 20260507_0003
Revises: 20260504_0002
Create Date: 2026-05-07
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260507_0003"
down_revision: str | None = "20260504_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create table if not exists user_distributions (
            id uuid primary key default gen_random_uuid(),
            user_id uuid not null references users(id),
            name varchar(120) not null,
            strategy_code varchar(40) not null,
            needs_percentage numeric(9,6) not null check (needs_percentage >= 0),
            wants_percentage numeric(9,6) not null check (wants_percentage >= 0),
            savings_percentage numeric(9,6) not null check (savings_percentage >= 0),
            metadata jsonb not null default '{}'::jsonb,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now(),
            deleted_at timestamptz
        );

        create index if not exists ix_user_distributions_user_created
            on user_distributions(user_id, created_at desc);

        alter table user_distributions enable row level security;
        drop policy if exists user_distributions_owner_select on user_distributions;
        drop policy if exists user_distributions_owner_insert on user_distributions;
        drop policy if exists user_distributions_owner_update on user_distributions;
        drop policy if exists user_distributions_owner_delete on user_distributions;

        create policy user_distributions_owner_select on user_distributions
        for select using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy user_distributions_owner_insert on user_distributions
        for insert with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy user_distributions_owner_update on user_distributions
        for update using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        ) with check (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );
        create policy user_distributions_owner_delete on user_distributions
        for delete using (
            user_id = nullif(current_setting('app.current_user_id', true), '')::uuid
        );

        insert into transaction_categories (name, kind)
        values
            ('Salario', 'income'),
            ('Freelance', 'income'),
            ('Vivienda', 'expense'),
            ('Mercado', 'expense'),
            ('Transporte', 'expense'),
            ('Ahorro general', 'saving'),
            ('Pago de deuda', 'debt')
        on conflict do nothing;
        """
    )


def downgrade() -> None:
    op.execute("drop table if exists user_distributions cascade;")
