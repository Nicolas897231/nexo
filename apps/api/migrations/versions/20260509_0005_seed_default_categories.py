"""Seed default transaction categories

Revision ID: 20260509_0005
Revises: 20260509_0004
Create Date: 2026-05-09 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260509_0005"
down_revision: str | None = "20260509_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        with parents as (
            insert into transaction_categories (user_id, name, kind)
            values
                (null, 'Ingresos', 'income'),
                (null, 'Alimentacion', 'expense'),
                (null, 'Vivienda', 'expense'),
                (null, 'Transporte', 'expense'),
                (null, 'Servicios', 'expense'),
                (null, 'Salud', 'expense'),
                (null, 'Educacion', 'expense'),
                (null, 'Ocio', 'expense'),
                (null, 'Ahorro', 'saving'),
                (null, 'Deudas', 'debt')
            returning id, name
        )
        insert into transaction_categories (user_id, name, kind, parent_id)
        select null, child.name, child.kind, parents.id
        from parents
        join (
            values
                ('Ingresos', 'Salario', 'income'),
                ('Ingresos', 'Freelance', 'income'),
                ('Ingresos', 'Negocio', 'income'),
                ('Ingresos', 'Bonos', 'income'),
                ('Alimentacion', 'Supermercado', 'expense'),
                ('Alimentacion', 'Restaurantes', 'expense'),
                ('Alimentacion', 'Mercado', 'expense'),
                ('Vivienda', 'Arriendo', 'expense'),
                ('Vivienda', 'Administracion', 'expense'),
                ('Vivienda', 'Mantenimiento hogar', 'expense'),
                ('Transporte', 'Transporte publico', 'expense'),
                ('Transporte', 'Gasolina', 'expense'),
                ('Transporte', 'Parqueadero', 'expense'),
                ('Transporte', 'Apps de movilidad', 'expense'),
                ('Servicios', 'Internet y celular', 'expense'),
                ('Servicios', 'Agua, luz y gas', 'expense'),
                ('Servicios', 'Suscripciones', 'expense'),
                ('Salud', 'Medicamentos', 'expense'),
                ('Salud', 'Citas medicas', 'expense'),
                ('Educacion', 'Cursos', 'expense'),
                ('Educacion', 'Libros', 'expense'),
                ('Ocio', 'Entretenimiento', 'expense'),
                ('Ocio', 'Viajes', 'expense'),
                ('Ahorro', 'Fondo de emergencia', 'saving'),
                ('Ahorro', 'Meta personal', 'saving'),
                ('Deudas', 'Tarjeta de credito', 'debt'),
                ('Deudas', 'Credito vehiculo', 'debt'),
                ('Deudas', 'Prestamo personal', 'debt')
        ) as child(parent_name, name, kind) on child.parent_name = parents.name;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        delete from transaction_categories
        where user_id is null
          and name in (
            'Ingresos','Alimentacion','Vivienda','Transporte','Servicios','Salud','Educacion','Ocio','Ahorro','Deudas',
            'Salario','Freelance','Negocio','Bonos','Supermercado','Restaurantes','Mercado','Arriendo','Administracion',
            'Mantenimiento hogar','Transporte publico','Gasolina','Parqueadero','Apps de movilidad','Internet y celular',
            'Agua, luz y gas','Suscripciones','Medicamentos','Citas medicas','Cursos','Libros','Entretenimiento','Viajes',
            'Fondo de emergencia','Meta personal','Tarjeta de credito','Credito vehiculo','Prestamo personal'
          );
        """
    )
