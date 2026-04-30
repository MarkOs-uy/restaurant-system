# 📊 Project Summary
Generated: 2026-04-23 11:18:20.221299

## 📁 Estructura del proyecto

```
- ./
  - analyze_project.py
  - backend/
    - alembic/
      - env.py
      - versions/
        - 0d21e3868b2f_add_draft_status_to_orderstatus.py
        - 50f5f9de1220_add_table_shape.py
        - 530c9b9f2a9f_initial_schema.py
        - 5aa86605f254_add_discount_to_orders.py
        - 6ba12f28852f_cambios_en_cashregister.py
        - 7b0b567ffe9e_add_discount_to_orders.py
        - 7fd07db91f0d_refactor_restaurant_layout_structure.py
        - 900c4d6546a2_creando_tabla_de_eventos.py
        - 9607a137eec7_add_password_to_user.py
        - a4b707b32039_restaurant_layout.py
        - b30663f913d9_add_cash_register_audit_fields.py
        - e2398672eb07_agregar_índice_a_tabla_de_eventos_por_.py
        - fa7705341950_add_table_coordinates.py
    - app/
      - main.py
      - seed.py
      - seed_products.py
      - seed_restaurant.py
      - seed_stations.py
      - seed_users.py
      - core/
        - redis.py
        - security.py
      - db/
        - base_class.py
        - session.py
        - tenant.py
      - dependencies/
        - auth.py
      - domain/
        - errors.py
        - error_codes.py
        - cash_register/
          - cash_movement_service.py
          - cash_register_service.py
          - dependencies.py
        - category/
          - category_service.py
          - dependencies.py
        - kitchen/
          - dependencies.py
          - kitchen_service.py
        - layout/
          - dependencies.py
          - layout_service.py
        - order/
          - constants.py
          - dependencies.py
          - order_service.py
          - order_transitions.py
        - order_item/
          - dependencies.py
          - order_item_service.py
          - order_item_transitions.py
        - product/
          - dependencies.py
          - product_service.py
        - stations/
          - dependencies.py
          - station_service.py
        - table/
          - dependencies.py
          - table_service.py
        - user/
          - dependencies.py
          - user_service.py
      - events/
        - redis_listener.py
      - models/
        - cash_movement.py
        - cash_register.py
        - category.py
        - domain_event.py
        - order.py
        - order_item.py
        - payment.py
        - product.py
        - production_station.py
        - restaurant.py
        - restaurant_layout.py
        - table.py
        - user.py
        - __init__.py
      - routers/
        - auth.py
        - cash_register.py
        - category.py
        - kitchen.py
        - layout.py
        - orders.py
        - order_items.py
        - products.py
        - stations.py
        - tables.py
        - users.py
      - schemas/
        - auth.py
        - base.py
        - cash_register.py
        - category.py
        - layout.py
        - product.py
        - station.py
        - table.py
        - user.py
        - waiter.py
        - order/
          - kitchen.py
          - order.py
          - order_item.py
          - payment.py
      - services/
        - event_service.py
      - websocket/
        - manager.py
        - ws.py
  - backups/
    - daily/
    - last/
    - monthly/
    - weekly/
  - frontend/
    - public/
    - src/
      - assets/
      - components/
      - pages/
      - services/
      - types/
      - utils/
  - scripts/
    - announce_service.py
```

## 📄 Archivos analizados

### .\analyze_project.py

**Funciones (3):**
- analyze_file
- build_tree
- main

**Clases (0):**

**Imports (3):**
- os
- ast
- datetime.datetime

```python
import os
import ast
from datetime import datetime

EXCLUDE_DIRS = {"venv", "__pycache__", ".git", ".idea", ".vscode", "node_modules"}
OUTPUT_FILE = "PROJECT_SUMMARY.md"
INCLUDE_CODE = True  # Cambia a True si quieres incluir el código completo

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except:
            return None

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for n in node.names:
                imports.append(f"{module}.{n.name}")

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }

def build_tree(root):
    tree = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        level = root_dir.replace(root, "").count(os.sep)
        indent = "  " * level
        tree.append(f"{indent}- {os.path.basename(root_dir)}/")

        subindent = "  " * (level + 1)
        for f in files:
            if f.endswith(".py"):
                tree.append(f"{subindent}- {f}")
    return "\n".join(tree)

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"# 📊 Project Summary\n")
        out.write(f"Generated: {datetime.now()}\n\n")

        out.write("## 📁 Estructura del proyecto\n\n")
        out.write("```\n")
        out.write(build_tree("."))
        out.write("\n```\n\n")

        out.write("## 📄 Archivos analizados\n\n")

        for root_dir, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root_dir, file)
                    analysis = analyze_file(path)

                    if not analysis:
                        continue

                    out.write(f"### {path}\n\n")

                    out.write(f"**Funciones ({len(analysis['functions'])}):**\n")
                    for fn in analysis["functions"]:
                        out.write(f"- {fn}\n")

                    out.write(f"\n**Clases ({len(analysis['classes'])}):**\n")
                    for cl in analysis["classes"]:
                        out.write(f"- {cl}\n")

                    out.write(f"\n**Imports ({len(analysis['imports'])}):**\n")
                    for im in analysis["imports"]:
                        out.write(f"- {im}\n")

                    if INCLUDE_CODE:
                        with open(path, "r", encoding="utf-8") as f:
                            out.write("\n```python\n")
                            out.write(f.read())
                            out.write("\n```\n")

                    out.write("\n---\n\n")

    print(f"✅ Archivo generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
```

---

### .\backend\alembic\env.py

**Funciones (2):**
- run_migrations_offline
- run_migrations_online

**Clases (0):**

**Imports (8):**
- logging.config.fileConfig
- sqlalchemy.engine_from_config
- sqlalchemy.pool
- alembic.context
- app.db.base_class.Base
- app.models
- dotenv.load_dotenv
- os

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.db.base_class import Base
from app import models

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

---

### .\backend\alembic\versions\0d21e3868b2f_add_draft_status_to_orderstatus.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add draft status to orderstatus

Revision ID: 0d21e3868b2f
Revises: 5aa86605f254
Create Date: 2026-03-22 15:34:58.319184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d21e3868b2f'
down_revision: Union[str, Sequence[str], None] = '5aa86605f254'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE 'DRAFT'")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

```

---

### .\backend\alembic\versions\50f5f9de1220_add_table_shape.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add table shape

Revision ID: 50f5f9de1220
Revises: fa7705341950
Create Date: 2026-03-15 02:51:03.395475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50f5f9de1220'
down_revision: Union[str, Sequence[str], None] = 'fa7705341950'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tables', sa.Column('shape', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tables', 'shape')
    # ### end Alembic commands ###

```

---

### .\backend\alembic\versions\530c9b9f2a9f_initial_schema.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""initial schema

Revision ID: 530c9b9f2a9f
Revises: 
Create Date: 2026-02-22 21:55:21.520913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '530c9b9f2a9f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('restaurants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('plan', sa.String(), nullable=False),
    sa.Column('external_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restaurants_external_id'), 'restaurants', ['external_id'], unique=True)
    op.create_index(op.f('ix_restaurants_id'), 'restaurants', ['id'], unique=False)
    op.create_table('cash_registers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('opening_amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('closing_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cash_registers_id'), 'cash_registers', ['id'], unique=False)
    op.create_index(op.f('ix_cash_registers_restaurant_id'), 'cash_registers', ['restaurant_id'], unique=False)
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('production_stations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_tables_external_id'), 'tables', ['external_id'], unique=True)
    op.create_index(op.f('ix_tables_id'), 'tables', ['id'], unique=False)
    op.create_index(op.f('ix_tables_restaurant_id'), 'tables', ['restaurant_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'WAITER', 'KITCHEN', 'CASHIER', name='userrole'), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('table_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('OPEN', 'SENT', 'IN_PROGRESS', 'READY', 'CLOSED', 'CANCELLED', name='orderstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_external_id'), 'orders', ['external_id'], unique=True)
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_restaurant_id'), 'orders', ['restaurant_id'], unique=False)
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('station_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.ForeignKeyConstraint(['station_id'], ['production_stations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_restaurant_id'), 'products', ['restaurant_id'], unique=False)
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SENT', 'IN_PROGRESS', 'READY', 'DELIVERED', 'CANCELLED', name='orderitemstatus'), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_restaurant_id'), 'order_items', ['restaurant_id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('method', sa.Enum('CASH', 'CARD', 'TRANSFER', 'OTHER', name='paymentmethod'), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('cash_register_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cash_register_id'], ['cash_registers.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_restaurant_id'), 'payments', ['restaurant_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payments_restaurant_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_order_items_restaurant_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_products_restaurant_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_orders_restaurant_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_external_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_table('users')
    op.drop_index(op.f('ix_tables_restaurant_id'), table_name='tables')
    op.drop_index(op.f('ix_tables_id'), table_name='tables')
    op.drop_index(op.f('ix_tables_external_id'), table_name='tables')
    op.drop_table('tables')
    op.drop_table('production_stations')
    op.drop_table('categories')
    op.drop_index(op.f('ix_cash_registers_restaurant_id'), table_name='cash_registers')
    op.drop_index(op.f('ix_cash_registers_id'), table_name='cash_registers')
    op.drop_table('cash_registers')
    op.drop_index(op.f('ix_restaurants_id'), table_name='restaurants')
    op.drop_index(op.f('ix_restaurants_external_id'), table_name='restaurants')
    op.drop_table('restaurants')
    # ### end Alembic commands ###

```

---

### .\backend\alembic\versions\5aa86605f254_add_discount_to_orders.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add discount to orders

Revision ID: 5aa86605f254
Revises: 7b0b567ffe9e
Create Date: 2026-03-18 18:02:40.042295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5aa86605f254'
down_revision: Union[str, Sequence[str], None] = '7b0b567ffe9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'orders',
        sa.Column('discount', sa.Numeric(10, 2), nullable=False, server_default="0")
    )
    
    op.alter_column('orders', 'discount', server_default=None)


def downgrade() -> None:
    op.drop_column('orders', 'discount')

```

---

### .\backend\alembic\versions\6ba12f28852f_cambios_en_cashregister.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""cambios en cashregister

Revision ID: 6ba12f28852f
Revises: 7fd07db91f0d
Create Date: 2026-03-31 03:06:33.845028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ba12f28852f'
down_revision: Union[str, Sequence[str], None] = '7fd07db91f0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cash_registers",
        sa.Column("expected_cash", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("counted_cash", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("difference", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("total_sales", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("payments_snapshot", sa.JSON(), nullable=True)
    )

    op.create_table(
        "cash_movements",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "cash_register_id",
            sa.Integer(),
            sa.ForeignKey("cash_registers.id"),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "type",
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            "amount",
            sa.Numeric(10,2),
            nullable=False
        ),

        sa.Column(
            "reason",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        )
    )

    op.create_index(
        "ix_cash_movements_register",
        "cash_movements",
        ["cash_register_id"]
    )

    op.create_index(
        "ix_cash_movements_register_type",
        "cash_movements",
        ["cash_register_id", "type"]
    )


def downgrade() -> None:
    op.drop_index("ix_cash_movements_register_type", table_name="cash_movements")
    op.drop_index("ix_cash_movements_register", table_name="cash_movements")

    op.drop_table("cash_movements")

    op.drop_column("cash_registers", "payments_snapshot")
    op.drop_column("cash_registers", "total_sales")
    op.drop_column("cash_registers", "difference")
    op.drop_column("cash_registers", "counted_cash")
    op.drop_column("cash_registers", "expected_cash")
```

---

### .\backend\alembic\versions\7b0b567ffe9e_add_discount_to_orders.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add discount to orders

Revision ID: 7b0b567ffe9e
Revises: 50f5f9de1220
Create Date: 2026-03-18 18:02:00.580785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b0b567ffe9e'
down_revision: Union[str, Sequence[str], None] = '50f5f9de1220'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

```

---

### .\backend\alembic\versions\7fd07db91f0d_refactor_restaurant_layout_structure.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""refactor restaurant_layout structure

Revision ID: 7fd07db91f0d
Revises: a4b707b32039
Create Date: 2026-03-30 02:44:25.946302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fd07db91f0d'
down_revision: Union[str, Sequence[str], None] = 'a4b707b32039'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # eliminar PK actual
    op.drop_constraint(
        "restaurant_layout_pkey",
        "restaurant_layout",
        type_="primary"
    )

    # eliminar columna id
    op.drop_column("restaurant_layout", "id")

    # convertir restaurant_id en PK
    op.create_primary_key(
        "restaurant_layout_pkey",
        "restaurant_layout",
        ["restaurant_id"]
    )

    # nuevos campos
    op.add_column(
        "restaurant_layout",
        sa.Column("grid_size", sa.Integer(), server_default="40")
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("snap_to_grid", sa.Boolean(), server_default="true")
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("background_image", sa.String(), nullable=True)
    )


def downgrade():

    op.drop_column("restaurant_layout", "background_image")
    op.drop_column("restaurant_layout", "snap_to_grid")
    op.drop_column("restaurant_layout", "grid_size")

    op.drop_constraint(
        "restaurant_layout_pkey",
        "restaurant_layout",
        type_="primary"
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("id", sa.Integer(), primary_key=True)
    )

    op.create_primary_key(
        "restaurant_layout_pkey",
        "restaurant_layout",
        ["id"]
    )
```

---

### .\backend\alembic\versions\900c4d6546a2_creando_tabla_de_eventos.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""creando tabla de eventos

Revision ID: 900c4d6546a2
Revises: 0d21e3868b2f
Create Date: 2026-03-26 17:33:05.954838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '900c4d6546a2'
down_revision: Union[str, Sequence[str], None] = '0d21e3868b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "domain_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("domain_events")

```

---

### .\backend\alembic\versions\9607a137eec7_add_password_to_user.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add password to user

Revision ID: 9607a137eec7
Revises: 530c9b9f2a9f
Create Date: 2026-02-24 02:31:41.038535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9607a137eec7'
down_revision: Union[str, Sequence[str], None] = '530c9b9f2a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

```

---

### .\backend\alembic\versions\a4b707b32039_restaurant_layout.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""restaurant layout

Revision ID: a4b707b32039
Revises: e2398672eb07
Create Date: 2026-03-30 02:10:53.189414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b707b32039'
down_revision: Union[str, Sequence[str], None] = 'e2398672eb07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('idx_domain_events_restaurant'), table_name='domain_events')
    op.create_index(op.f('ix_domain_events_id'), 'domain_events', ['id'], unique=False)
    op.create_index(op.f('ix_domain_events_restaurant_id'), 'domain_events', ['restaurant_id'], unique=False)
    op.create_foreign_key(
    "fk_domain_events_restaurant",
    "domain_events",
    "restaurants",
    ["restaurant_id"],
    ["id"]
)
    op.create_table(
        "restaurant_layout",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id"), nullable=False, unique=True),
        sa.Column("width", sa.Integer(), nullable=False, server_default="900"),
        sa.Column("height", sa.Integer(), nullable=False, server_default="500"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_domain_events_restaurant", "domain_events", type_="foreignkey")
    op.drop_index(op.f('ix_domain_events_restaurant_id'), table_name='domain_events')
    op.drop_index(op.f('ix_domain_events_id'), table_name='domain_events')
    op.create_index(op.f('idx_domain_events_restaurant'), 'domain_events', ['restaurant_id'], unique=False)
    op.drop_table("restaurant_layout")

```

---

### .\backend\alembic\versions\b30663f913d9_add_cash_register_audit_fields.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add cash_register audit fields

Revision ID: b30663f913d9
Revises: 9607a137eec7
Create Date: 2026-03-01 21:47:58.915981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b30663f913d9'
down_revision: Union[str, Sequence[str], None] = '9607a137eec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cash_registers', sa.Column('is_open', sa.Boolean(), nullable=False))
    op.add_column('cash_registers', sa.Column('opened_by_id', sa.Integer(), nullable=True))
    op.add_column('cash_registers', sa.Column('closed_by_id', sa.Integer(), nullable=True))
    op.drop_index(op.f('ix_cash_registers_id'), table_name='cash_registers')
    op.create_foreign_key(None, 'cash_registers', 'users', ['opened_by_id'], ['id'])
    op.create_foreign_key(None, 'cash_registers', 'users', ['closed_by_id'], ['id'])
    op.create_unique_constraint('uq_category_name_per_restaurant', 'categories', ['restaurant_id', 'name'])
    op.create_index('ix_orders_restaurant_status', 'orders', ['restaurant_id', 'status'], unique=False)
    op.create_unique_constraint('uq_station_name_per_restaurant', 'production_stations', ['restaurant_id', 'name'])
    op.create_unique_constraint('uq_product_name_per_restaurant', 'products', ['restaurant_id', 'name'])
    op.alter_column('tables', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('tables', 'external_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index(op.f('ix_tables_external_id'), table_name='tables')
    op.drop_constraint(op.f('tables_number_key'), 'tables', type_='unique')
    op.create_index('ix_table_restaurant_active', 'tables', ['restaurant_id', 'active'], unique=False)
    op.create_unique_constraint('uq_table_external_per_restaurant', 'tables', ['restaurant_id', 'external_id'])
    op.create_unique_constraint('uq_table_number_per_restaurant', 'tables', ['restaurant_id', 'number'])
    op.drop_constraint(op.f('tables_restaurant_id_fkey'), 'tables', type_='foreignkey')
    op.create_foreign_key(None, 'tables', 'restaurants', ['restaurant_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tables', type_='foreignkey')
    op.create_foreign_key(op.f('tables_restaurant_id_fkey'), 'tables', 'restaurants', ['restaurant_id'], ['id'])
    op.drop_constraint('uq_table_number_per_restaurant', 'tables', type_='unique')
    op.drop_constraint('uq_table_external_per_restaurant', 'tables', type_='unique')
    op.drop_index('ix_table_restaurant_active', table_name='tables')
    op.create_unique_constraint(op.f('tables_number_key'), 'tables', ['number'], postgresql_nulls_not_distinct=False)
    op.create_index(op.f('ix_tables_external_id'), 'tables', ['external_id'], unique=True)
    op.alter_column('tables', 'external_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('tables', 'active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_constraint('uq_product_name_per_restaurant', 'products', type_='unique')
    op.drop_constraint('uq_station_name_per_restaurant', 'production_stations', type_='unique')
    op.drop_index('ix_orders_restaurant_status', table_name='orders')
    op.drop_constraint('uq_category_name_per_restaurant', 'categories', type_='unique')
    op.drop_constraint(None, 'cash_registers', type_='foreignkey')
    op.drop_constraint(None, 'cash_registers', type_='foreignkey')
    op.create_index(op.f('ix_cash_registers_id'), 'cash_registers', ['id'], unique=False)
    op.drop_column('cash_registers', 'closed_by_id')
    op.drop_column('cash_registers', 'opened_by_id')
    op.drop_column('cash_registers', 'is_open')
    # ### end Alembic commands ###

```

---

### .\backend\alembic\versions\e2398672eb07_agregar_índice_a_tabla_de_eventos_por_.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""agregar índice a tabla de eventos por restaurant_id

Revision ID: e2398672eb07
Revises: 900c4d6546a2
Create Date: 2026-03-26 17:46:46.648977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2398672eb07'
down_revision: Union[str, Sequence[str], None] = '900c4d6546a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_domain_events_restaurant",
        "domain_events",
        ["restaurant_id"]
    )



def downgrade() -> None:
    op.drop_index(
        "idx_domain_events_restaurant",
        table_name="domain_events"
    )

```

---

### .\backend\alembic\versions\fa7705341950_add_table_coordinates.py

**Funciones (2):**
- upgrade
- downgrade

**Clases (0):**

**Imports (4):**
- typing.Sequence
- typing.Union
- alembic.op
- sqlalchemy

```python
"""add table coordinates

Revision ID: fa7705341950
Revises: b30663f913d9
Create Date: 2026-03-15 02:39:50.294892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa7705341950'
down_revision: Union[str, Sequence[str], None] = 'b30663f913d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "tables",
        sa.Column("x", sa.Integer(), nullable=False, server_default="0")
    )

    op.add_column(
        "tables",
        sa.Column("y", sa.Integer(), nullable=False, server_default="0")
    )

    op.add_column(
        "tables",
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="4")
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tables', 'capacity')
    op.drop_column('tables', 'y')
    op.drop_column('tables', 'x')
    # ### end Alembic commands ###

```

---

### .\backend\app\main.py

**Funciones (2):**
- root
- health

**Clases (0):**

**Imports (23):**
- fastapi.FastAPI
- fastapi.Request
- fastapi.responses.JSONResponse
- contextlib.asynccontextmanager
- asyncio
- logging
- app.models
- app.events.redis_listener.redis_event_listener
- app.services.event_service.event_service
- app.routers.tables
- app.routers.orders
- app.routers.products
- app.routers.cash_register
- app.routers.category
- app.routers.order_items
- app.routers.stations
- app.routers.auth
- app.routers.users
- app.routers.kitchen
- app.routers.layout
- app.domain.errors.DomainError
- app.websocket.ws
- fastapi.middleware.cors.CORSMiddleware

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging

from app import models
from app.events.redis_listener import redis_event_listener

from app.services.event_service import event_service

# routers
from app.routers import tables, orders, products, cash_register, category, order_items, stations, auth, users, kitchen
from app.routers import layout


from app.domain.errors import DomainError
from app.websocket import ws

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Backend arrancando...")

    # 🔥 REGISTRAR EVENT LOOP PARA EVENT SERVICE
    event_service.loop = asyncio.get_running_loop()

    print("EventService loop registrado")

    # Redis listener
    redis_task = asyncio.create_task(redis_event_listener())

    yield

    print("Backend apagándose...")

    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen.router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws.router)
app.include_router(layout.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "restaurant-pos",
        "version": "1.0.0"
    }

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("app")

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):

    logger.warning(f"{exc.code}: {exc.message}")

    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "detail": exc.message,
            "context": exc.context
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):

    logger.exception("Unexpected server error")

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "detail": "Error interno del servidor"
        }
    )
```

---

### .\backend\app\seed.py

**Funciones (2):**
- seed_tables
- run

**Clases (0):**

**Imports (7):**
- sqlalchemy.orm.Session
- app.db.session.SessionLocal
- app.models.table.Table
- app.seed_restaurant.seed_restaurant
- app.seed_products.seed_products
- app.seed_stations.seed_stations
- app.seed_users.seed_users

```python
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.table import Table
from app.seed_restaurant import seed_restaurant
from app.seed_products import seed_products
from app.seed_stations import seed_stations
from app.seed_users import seed_users


def seed_tables(db: Session):

    restaurant = seed_restaurant(db)

    if db.query(Table).first():
        print("Seed ya ejecutado. No se crean mesas.")
        return

    print("Creando mesas iniciales...")

    tables = [
        Table(number=i, restaurant_id=restaurant.id)
        for i in range(1, 21)
    ]

    db.add_all(tables)
    db.commit()

    print("Mesas creadas.")

def run():
    db = SessionLocal()
    try:
        #seed_tables(db)
        #seed_stations(db)
        #seed_products(db)
        seed_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()

```

---

### .\backend\app\seed_products.py

**Funciones (1):**
- seed_products

**Clases (0):**

**Imports (4):**
- sqlalchemy.orm.Session
- app.models.product.Product
- app.models.category.Category
- app.seed_restaurant.seed_restaurant

```python
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.category import Category
from app.seed_restaurant import seed_restaurant


def seed_products(db: Session):

    restaurant = seed_restaurant(db)

    existing_products = db.query(Product).count()
    if existing_products > 0:
        print("Seed productos ya ejecutado.")
        return

    print("Creando categorías iniciales...")

    # Crear categorías
    bebidas = Category(name="Bebidas", restaurant_id=restaurant.id)
    cocina = Category(name="Cocina", restaurant_id=restaurant.id)

    db.add_all([bebidas, cocina])
    db.commit()

    db.refresh(bebidas)
    db.refresh(cocina)

    print("Creando productos iniciales...")

    products = [
        # BEBIDAS → estación 2 (barra)
        Product(
            name="Coca Cola",
            price=120,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),
        Product(
            name="Agua",
            price=90,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),
        Product(
            name="Cerveza",
            price=180,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),

        # COCINA → estación 1
        Product(
            name="Hamburguesa",
            price=450,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
        Product(
            name="Pizza Muzza",
            price=520,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
        Product(
            name="Papas Fritas",
            price=250,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
    ]

    db.add_all(products)
    db.commit()

    print("Productos creados con categorías.")

```

---

### .\backend\app\seed_restaurant.py

**Funciones (1):**
- seed_restaurant

**Clases (0):**

**Imports (2):**
- sqlalchemy.orm.Session
- app.models.restaurant.Restaurant

```python
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant


def seed_restaurant(db: Session):

    restaurant = db.query(Restaurant).first()

    if restaurant:
        print("Restaurant ya existe.")
        return restaurant

    print("Creando restaurant default...")
    restaurant = Restaurant(name="Resto Demo")

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant

```

---

### .\backend\app\seed_stations.py

**Funciones (1):**
- seed_stations

**Clases (0):**

**Imports (3):**
- sqlalchemy.orm.Session
- app.models.production_station.ProductionStation
- app.seed_restaurant.seed_restaurant

```python
from sqlalchemy.orm import Session
from app.models.production_station import ProductionStation
from app.seed_restaurant import seed_restaurant

def seed_stations(db: Session):

    restaurant = seed_restaurant(db)

    existing_stations = db.query(ProductionStation).count()

    if existing_stations > 0:
        print("Seed estaciones ya ejecutado.")
        return

    print("Creando estaciones iniciales...")

    products = [
        ProductionStation(name="Cocina", restaurant_id=restaurant.id),
        ProductionStation(name="Barra", restaurant_id=restaurant.id),
    ]

    db.add_all(products)
    db.commit()

    print("Estaciones creadas.")

```

---

### .\backend\app\seed_users.py

**Funciones (1):**
- seed_users

**Clases (0):**

**Imports (4):**
- sqlalchemy.orm.Session
- app.models.user.User
- app.seed_restaurant.seed_restaurant
- app.core.security.get_password_hash

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.seed_restaurant import seed_restaurant
from app.core.security import get_password_hash

def seed_users(db: Session):

    restaurant = seed_restaurant(db)

    existing_users = db.query(User).count()

    if existing_users > 0:
        print("Seed usuarios ya ejecutado.")
        return

    print("Creando usuario admin...")

    pass_hash = get_password_hash("1234")

    users = [
        User(username="admin", role="ADMIN", password_hash = pass_hash, restaurant_id=restaurant.id)
        #User(username="waiter", role="WAITER", password_hash = pass_hash, restaurant_id=restaurant.id),
        #User(username="kitchen", role="KITCHEN", password_hash = pass_hash, restaurant_id=restaurant.id),
        #User(username="cashier", role="CASHIER", password_hash = pass_hash, restaurant_id=restaurant.id),
    ]

    db.add_all(users)
    db.commit()

    print("Usuario Admin creado.")

```

---

### .\backend\app\core\redis.py

**Funciones (0):**

**Clases (0):**

**Imports (2):**
- redis.asyncio
- os

```python
import redis.asyncio as redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
    socket_keepalive=True
)
```

---

### .\backend\app\core\security.py

**Funciones (4):**
- get_password_hash
- verify_password
- create_access_token
- decode_access_token

**Clases (0):**

**Imports (6):**
- datetime.datetime
- datetime.timedelta
- datetime.timezone
- jose.JWTError
- jose.jwt
- passlib.context.CryptContext

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# 🔐 Hash password
def get_password_hash(password: str):
    return pwd_context.hash(password)


# 🔎 Verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# 🎟 Create JWT
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# 🔓 Decode JWT
def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None
```

---

### .\backend\app\db\base_class.py

**Funciones (0):**

**Clases (0):**

**Imports (1):**
- sqlalchemy.orm.declarative_base

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

---

### .\backend\app\db\session.py

**Funciones (1):**
- get_db

**Clases (0):**

**Imports (5):**
- sqlalchemy.create_engine
- sqlalchemy.orm.sessionmaker
- sqlalchemy.orm.declarative_base
- dotenv.load_dotenv
- os

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

---

### .\backend\app\db\tenant.py

**Funciones (1):**
- tenant_query

**Clases (0):**

**Imports (2):**
- sqlalchemy.orm.Session
- app.models.user.User

```python
from sqlalchemy.orm import Session
from app.models.user import User

def tenant_query(db: Session, model, user: User):
    return db.query(model).filter(model.restaurant_id == user.restaurant_id)
```

---

### .\backend\app\dependencies\auth.py

**Funciones (1):**
- get_current_user

**Clases (0):**

**Imports (7):**
- fastapi.Depends
- fastapi.HTTPException
- fastapi.security.OAuth2PasswordBearer
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.user.User
- app.core.security.decode_access_token

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(401, "Token inválido")

    user_id = payload.get("sub")

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(401, "No se encuentra este usuario")
    
    if not user.active:
        raise HTTPException(401, "Usuario inactivo")

    return user

```

---

### .\backend\app\domain\errors.py

**Funciones (1):**
- __init__

**Clases (10):**
- DomainError
- CashRegisterDomainError
- PaymentDomainError
- OrderDomainError
- OrderItemDomainError
- ProductDomainError
- TableDomainError
- UserDomainError
- CategoryDomainError
- StationDomainError

**Imports (0):**

```python
class DomainError(Exception):

    def __init__(self, message: str, code: str = "domain_error", context: dict | None = None):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)


class CashRegisterDomainError(DomainError):
    pass


class PaymentDomainError(DomainError):
    pass


class OrderDomainError(DomainError):
    pass


class OrderItemDomainError(DomainError):
    pass


class ProductDomainError(DomainError):
    pass


class TableDomainError(DomainError):
    pass


class UserDomainError(DomainError):
    pass


class CategoryDomainError(DomainError):
    pass


class StationDomainError(DomainError):
    pass
```

---

### .\backend\app\domain\error_codes.py

**Funciones (0):**

**Clases (1):**
- ErrorCode

**Imports (0):**

```python
class ErrorCode:

    # GENERALES
    NOT_FOUND = "not_found"
    INVALID_OPERATION = "invalid_operation"
    UNAUTHORIZED = "unauthorized"

    # ORDERS
    ORDER_NOT_FOUND = "order_not_found"
    ORDER_ALREADY_CLOSED = "order_already_closed"
    ORDER_ITEMS_NOT_DELIVERED = "order_items_not_delivered"
    ORDER_EMPTY = "order_empty"
    ORDER_HAS_REMAINING_BALANCE = "order_has_remaining_balance"
    INVALID_TRANSITION = "invalid_transition"

    # ORDER ITEMS
    ITEM_NOT_FOUND = "item_not_found"
    ITEM_NOT_IN_ORDER = "item_not_in_order"
    ITEM_ALREADY_SEND = "item_already_send"
    NOT_PENDING_ITEMS_TO_SEND = "not_pending_items_to_send"
    ITEM_STATUS_ROLE_FORBIDDEN = "item_status_role_forbidden"
    ITEM_INVALID_TRANSITION = "item_invalid_transition"

    # TABLES
    TABLE_NOT_FOUND = "table_not_found"

    # PAYMENTS
    PAYMENT_NOT_FOUND = "payment_not_found"
    PAYMENT_INVALID_METHOD = "payment_invalid_method"
    PAYMENT_EXCEEDS_REMAINING = "payment_exceeds_remaining"

    # CASH REGISTER
    CASH_REGISTER_ALREADY_OPEN = "cash_register_already_open"
    CASH_REGISTER_ALREADY_CLOSED = "cash_register_already_closed"
    CASH_REGISTER_NOT_OPEN = "cash_register_not_open"
    CASH_REGISTER_PENDING_ORDERS = "cash_register_pending_orders"
    CASH_REGISTER_INVALID_COUNT = "cash_register_invalid_count"
    CASH_MOVEMENT_NOT_FOUND = "cash_movement_not_found"


    # PRODUCTS
    PRODUCT_NOT_FOUND = "product_not_found"

    # USERS
    USER_NOT_FOUND = "user_not_found"
    USERNAME_ALREADY_EXISTS = "username_already_exists"

    # CATEGORIES
    CATEGORY_NOT_FOUND = "category_not_found"

    # STATIONS
    STATION_NOT_FOUND = "station_not_found"
    STATION_NAME_ALREADY_EXISTS = "station_name_already_exists"
```

---

### .\backend\app\domain\cash_register\cash_movement_service.py

**Funciones (2):**
- create_cash_movement
- delete_cash_movement

**Clases (1):**
- CashMovementService

**Imports (6):**
- app.models.cash_movement.CashMovement
- app.models.cash_register.CashRegister
- app.domain.errors.CashRegisterDomainError
- app.domain.error_codes.ErrorCode
- app.models.user.UserRole
- app.services.event_service.event_service

```python
from app.models.cash_movement import CashMovement
from app.models.cash_register import CashRegister
from app.domain.errors import CashRegisterDomainError
from app.domain.error_codes import ErrorCode
from app.models.user import UserRole
from app.services.event_service import event_service


class CashMovementService:

    def create_cash_movement(
        self,
        db,
        restaurant_id,
        user_id,
        movement_type,
        amount,
        reason
    ):

        cash_register = (
            db.query(CashRegister)
            .filter(
                CashRegister.restaurant_id == restaurant_id,
                CashRegister.is_open == True
            )
            .with_for_update()
            .first()
        )

        if not cash_register:
            raise CashRegisterDomainError(
                "cash register not open",
                ErrorCode.CASH_REGISTER_NOT_OPEN
            )

        movement = CashMovement(
            cash_register_id=cash_register.id,
            user_id=user_id,
            type=movement_type,
            amount=amount,
            reason=reason
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {
                "type": "CASH_MOVEMENT_ADDED",
                "movement": {
                    "id": movement.id,
                    "type": movement.type,
                    "amount": float(movement.amount),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat()
                }
            }
        )

        return movement


    def delete_cash_movement(
        self,
        db,
        restaurant_id,
        movement_id
    ):

        movement = db.query(CashMovement).join(
            CashRegister,
            CashMovement.cash_register_id == CashRegister.id
        ).filter(
            CashMovement.id == movement_id,
            CashRegister.restaurant_id == restaurant_id
        ).first()

        if not movement:
            raise CashRegisterDomainError(
                "Movement not found",
                ErrorCode.CASH_MOVEMENT_NOT_FOUND
            )

        amount = movement.amount
        movement_type = movement.type

        db.delete(movement)
        db.commit()

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {
                "type": "CASH_MOVEMENT_DELETED",
                "movement_id": movement_id,
                "amount": float(amount),
                "movement_type": movement_type
            }
        )

        return {"ok": True}
```

---

### .\backend\app\domain\cash_register\cash_register_service.py

**Funciones (9):**
- _get_open_cash_register
- _calculate_sales
- _calculate_payment_breakdown
- _calculate_cash_movements
- open_cash_register
- close_cash_register
- get_current_cash_register
- require_open_cash_register
- get_dashboard

**Clases (1):**
- CashRegisterService

**Imports (12):**
- decimal.Decimal
- sqlalchemy.orm.Session
- sqlalchemy.func
- app.models.cash_register.CashRegister
- app.models.payment.Payment
- app.models.cash_movement.CashMovement
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.payment.PaymentMethod
- app.models.cash_movement.CashMovementType
- app.domain.errors.CashRegisterDomainError
- app.domain.error_codes.ErrorCode

```python
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.cash_register import CashRegister
from app.models.payment import Payment
from app.models.cash_movement import CashMovement
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType

from app.domain.errors import CashRegisterDomainError
from app.domain.error_codes import ErrorCode


class CashRegisterService:

    def _get_open_cash_register(
        self,
        db: Session,
        restaurant_id: int,
        for_update: bool = False
    ):

        query = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        )

        if for_update:
            query = query.with_for_update()

        cash_register = query.first()

        if not cash_register:
            raise CashRegisterDomainError(
                "cash register not open",
                ErrorCode.CASH_REGISTER_NOT_OPEN
            )

        return cash_register


    def _calculate_sales(self, db: Session, cash_register_id: int):
        total_sales = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        transactions_count = db.query(
            func.count(Payment.id)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        orders_count = db.query(
            func.count(func.distinct(Payment.order_id))
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        average_ticket = (
            total_sales / orders_count
            if orders_count
            else Decimal("0")
        )
        return total_sales, transactions_count, orders_count, average_ticket


    def _calculate_payment_breakdown(self, db: Session, cash_register_id: int):
        rows = db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).group_by(
            Payment.method
        ).all()
        return {
            method.value: total or Decimal("0")
            for method, total in rows
        }


    def _calculate_cash_movements(self, db: Session, cash_register_id: int):
        rows = db.query(
            CashMovement.type,
            func.sum(CashMovement.amount)
        ).filter(
            CashMovement.cash_register_id == cash_register_id
        ).group_by(
            CashMovement.type
        ).all()
        cash_in = Decimal("0")
        cash_out = Decimal("0")
        for mtype, total in rows:
            if mtype == CashMovementType.CASH_IN:
                cash_in += total or Decimal("0")
            elif mtype == CashMovementType.CASH_OUT:
                cash_out += total or Decimal("0")
        return cash_in, cash_out


    def open_cash_register(
        self,
        db: Session,
        restaurant_id: int,
        user_id: int,
        opening_amount: Decimal
    ):
        existing = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()
        if existing:
            raise CashRegisterDomainError(
                "Cash register already open", 
                ErrorCode.CASH_REGISTER_ALREADY_OPEN
                )
        cash_register = CashRegister(
            restaurant_id=restaurant_id,
            opened_by_id=user_id,
            opening_amount=opening_amount,
            is_open=True
        )
        db.add(cash_register)
        db.commit()
        db.refresh(cash_register)
        return cash_register


    def close_cash_register(
        self,
        db: Session,
        restaurant_id: int,
        user_id: int,
        counted_cash: Decimal
    ):

        cash_register = self._get_open_cash_register(
            db,
            restaurant_id,
            for_update=True
        )

        open_orders = db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            Order.status.notin_([OrderStatus.CLOSED, OrderStatus.CANCELLED])
        ).count()

        if open_orders > 0:
            raise CashRegisterDomainError(
                "cannot close cash register: there are open orders",
                ErrorCode.CASH_REGISTER_PENDING_ORDERS
            )

        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            db,
            cash_register.id
        )

        payment_breakdown = self._calculate_payment_breakdown(
            db,
            cash_register.id
        )

        cash_sales = payment_breakdown.get(
            PaymentMethod.CASH.value,
            Decimal("0")
        )

        cash_in, cash_out = self._calculate_cash_movements(
            db,
            cash_register.id
        )

        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )

        difference = counted_cash - expected_cash

        cash_register.closed_at = func.now()
        cash_register.closed_by_id = user_id
        cash_register.is_open = False
        cash_register.total_sales = total_sales
        cash_register.expected_cash = expected_cash
        cash_register.counted_cash = counted_cash
        cash_register.difference = difference
        cash_register.payments_snapshot = payment_breakdown

        db.commit()

        return {
            "message": "Caja cerrada",
            "opening_amount": cash_register.opening_amount,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": payment_breakdown,
            "cash_in": cash_in,
            "cash_out": cash_out,
            "expected_cash": expected_cash,
            "counted_cash": counted_cash,
            "difference": difference
        }


    def get_current_cash_register(self, db: Session, restaurant_id: int):
        cash_register = self._get_open_cash_register(db, restaurant_id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            db,
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            db,
            cash_register.id
        )
        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": by_method
        }


    def require_open_cash_register(self, db: Session, restaurant_id: int):
        return self._get_open_cash_register(db, restaurant_id)


    def get_dashboard(self, db: Session, restaurant_id: int):

        cash_register = self._get_open_cash_register(db, restaurant_id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            db,
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            db,
            cash_register.id
        )
        cash_in, cash_out = self._calculate_cash_movements(
            db,
            cash_register.id
        )
        cash_sales = by_method.get(
            PaymentMethod.CASH.value,
            Decimal("0")
        )
        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )
        movements = db.query(CashMovement).filter(
            CashMovement.cash_register_id == cash_register.id
        ).order_by(
            CashMovement.created_at.desc()
        ).all()
        movements_list = [
            {
                "id": m.id,
                "type": m.type,
                "amount": m.amount,
                "reason": m.reason,
                "created_at": m.created_at
            }
            for m in movements
        ]
        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "opening_amount": cash_register.opening_amount,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": by_method,
            "cash_movements": movements_list,
            "expected_cash": expected_cash
        }
```

---

### .\backend\app\domain\cash_register\dependencies.py

**Funciones (2):**
- get_cash_register_service
- get_cash_movement_service

**Clases (0):**

**Imports (2):**
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.cash_register.cash_movement_service.CashMovementService

```python
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService


def get_cash_register_service():
    return CashRegisterService()

def get_cash_movement_service():
    return CashMovementService()
```

---

### .\backend\app\domain\category\category_service.py

**Funciones (7):**
- __init__
- _get_category
- list_categories
- create_category
- update_category
- delete_category
- list_categories_with_products

**Clases (1):**
- CategoryService

**Imports (5):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.models.category.Category
- app.domain.errors.CategoryDomainError
- app.domain.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.domain.errors import CategoryDomainError
from app.domain.error_codes import ErrorCode

class CategoryService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Devolver una categoría, lanzar error si no existe o no pertenece al restaurante
    # -------------------------

    def _get_category(self, restaurant_id: int, category_id: int):
        category = (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == restaurant_id
            )
            .first()
        )
        if not category:
            raise CategoryDomainError(
                "Category not found",
                ErrorCode.CATEGORY_NOT_FOUND
            )
        return category

    # -------------------------
    # Listar categorías
    # -------------------------

    def list_categories(self, restaurant_id: int):
        return (
            self.db.query(Category)
            .filter(Category.restaurant_id == restaurant_id)
            .order_by(Category.name)
            .all()
        )

    # -------------------------
    # Crear categoría
    # -------------------------

    def create_category(self, restaurant_id: int, name: str):
        category = Category(
            name=name,
            restaurant_id=restaurant_id
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    # -------------------------
    # Actualizar categoría
    # -------------------------

    def update_category(self, restaurant_id: int, category_id: int, name: str):
        category = self._get_category(restaurant_id, category_id)
        category.name = name
        self.db.commit()
        self.db.refresh(category)
        return category

    # -------------------------
    # Eliminar categoría
    # -------------------------

    def delete_category(self, restaurant_id: int, category_id: int):
        category = self._get_category(restaurant_id, category_id)
        self.db.delete(category)
        self.db.commit()
        return True

    # -------------------------
    # Listar categorías con productos activos
    # -------------------------

    def list_categories_with_products(self, restaurant_id: int):
        categories = (
            self.db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.restaurant_id == restaurant_id)
            .order_by(Category.name)
            .all()
        )
        result = []
        for category in categories:
            active_products = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price
                }
                for p in category.products
                if p.active
            ]
            result.append({
                "id": category.id,
                "name": category.name,
                "products": active_products
            })
        return result
```

---

### .\backend\app\domain\category\dependencies.py

**Funciones (1):**
- get_category_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- category_service.CategoryService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .category_service import CategoryService


def get_category_service(
    db: Session = Depends(get_db)
) -> CategoryService:
    return CategoryService(db)
```

---

### .\backend\app\domain\kitchen\dependencies.py

**Funciones (1):**
- get_kitchen_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.domain.kitchen.kitchen_service.KitchenService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.kitchen.kitchen_service import KitchenService


def get_kitchen_service(
    db: Session = Depends(get_db)
) -> KitchenService:
    return KitchenService(db)
```

---

### .\backend\app\domain\kitchen\kitchen_service.py

**Funciones (3):**
- __init__
- get_station_items
- update_item_status

**Clases (1):**
- KitchenService

**Imports (8):**
- sqlalchemy.orm.Session
- app.models.user.User
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.order.Order
- app.schemas.order.kitchen.KitchenItemOut
- app.domain.order_item.order_item_service.OrderItemService

```python
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order

from app.schemas.order.kitchen import KitchenItemOut

from app.domain.order_item.order_item_service import OrderItemService


class KitchenService:

    def __init__(self, db: Session):
        self.db = db
        self.item_service = OrderItemService(db)

    # -------------------------
    # Obtener los items de una estación, filtrando por estado y restaurante
    # -------------------------

    def get_station_items(
        self,
        station_id: int,
        user: User
    ) -> list[KitchenItemOut]:
        items = (
            self.db.query(OrderItem)
            .join(OrderItem.product)
            .join(Product.station)
            .join(OrderItem.order)
            .join(Order.table)
            .filter(
                Product.station_id == station_id,
                OrderItem.restaurant_id == user.restaurant_id,
                OrderItem.status.in_([
                    OrderItemStatus.SENT,
                    OrderItemStatus.IN_PROGRESS
                ])
            )
            .all()
        )

        result = []

        for item in items:
            result.append(
                KitchenItemOut(
                    item_id=item.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    status=item.status,
                    table_number=item.order.table.number,
                    order_id=item.order.id
                )
            )

        return result

    # -------------------------
    # Actualizar el estado de un item, validando que el usuario tenga permisos para hacerlo
    # -------------------------

    def update_item_status(
        self,
        item_id: int,
        status: OrderItemStatus,
        user: User
    ):
        return OrderItemService.update_status(
            item_id=item_id,
            new_status=status,
            user=user
        )
```

---

### .\backend\app\domain\layout\dependencies.py

**Funciones (1):**
- get_layout_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- layout_service.LayoutService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .layout_service import LayoutService


def get_layout_service(db: Session = Depends(get_db)):
    return LayoutService(db)
```

---

### .\backend\app\domain\layout\layout_service.py

**Funciones (3):**
- __init__
- get_layout
- update_layout

**Clases (1):**
- LayoutService

**Imports (3):**
- sqlalchemy.orm.Session
- app.models.restaurant_layout.RestaurantLayout
- app.schemas.layout.LayoutUpdate

```python
from sqlalchemy.orm import Session
from app.models.restaurant_layout import RestaurantLayout
from app.schemas.layout import LayoutUpdate


class LayoutService:

    def __init__(self, db: Session):
        self.db = db


    def get_layout(self, restaurant_id: int):

        layout = (
            self.db.query(RestaurantLayout)
            .filter(RestaurantLayout.restaurant_id == restaurant_id)
            .first()
        )

        if not layout:

            layout = RestaurantLayout(
                restaurant_id=restaurant_id,
                width=900,
                height=750,
                grid_size=40,
                snap_to_grid=True
            )

            self.db.add(layout)
            self.db.commit()
            self.db.refresh(layout)

        return layout


    def update_layout(self, restaurant_id: int, data: LayoutUpdate):

        layout = self.get_layout(restaurant_id)

        layout.width = data.width
        layout.height = data.height
        layout.grid_size = data.grid_size
        layout.snap_to_grid = data.snap_to_grid

        self.db.commit()
        self.db.refresh(layout)

        return layout
```

---

### .\backend\app\domain\order\constants.py

**Funciones (0):**

**Clases (0):**

**Imports (1):**
- app.models.order.OrderStatus

```python
from app.models.order import OrderStatus

ACTIVE_ORDER_STATUSES = [
    OrderStatus.DRAFT,
    OrderStatus.OPEN,
    OrderStatus.SENT,
    OrderStatus.IN_PROGRESS,
    OrderStatus.READY
]
```

---

### .\backend\app\domain\order\dependencies.py

**Funciones (1):**
- get_order_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- order_service.OrderService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .order_service import OrderService

def get_order_service(
    db: Session = Depends(get_db)
) -> OrderService:

    return OrderService(db)
```

---

### .\backend\app\domain\order\order_service.py

**Funciones (16):**
- __init__
- get_order
- get_active_orders
- get_active_order
- serialize_order
- serialize_orders
- calculate_totals
- add_item
- add_product_to_table
- update_status
- recalculate_order_status
- send_to_kitchen
- add_payment
- cancel_payment
- close_order
- delete_order_item

**Clases (1):**
- OrderService

**Imports (18):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- sqlalchemy.func
- decimal.Decimal
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.user.UserRole
- app.models.payment.Payment
- app.models.table.Table
- app.services.event_service.event_service
- app.domain.order.order_transitions.is_valid_order_transition
- app.domain.order.constants.ACTIVE_ORDER_STATUSES
- app.domain.errors.OrderDomainError
- app.domain.error_codes.ErrorCode
- app.domain.cash_register.cash_register_service.CashRegisterService

```python
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.user import UserRole
from app.models.payment import Payment
from app.models.table import Table

from app.services.event_service import event_service
from app.domain.order.order_transitions import is_valid_order_transition
from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors import OrderDomainError
from app.domain.error_codes import ErrorCode


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Getters
    # -------------------------

    def get_order(self, order_id: int, restaurant_id: int):
        order = (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(Order.id == order_id, Order.restaurant_id == restaurant_id)
            .first()
        )
        if not order:
            raise OrderDomainError(
                "Orden no encontrada",
                ErrorCode.ORDER_NOT_FOUND
            )

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        return order


    def get_active_orders(self, restaurant_id: int):
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(Order.restaurant_id == restaurant_id,
                    Order.status.in_(ACTIVE_ORDER_STATUSES))
            .all()
        )


    def get_active_order(self, restaurant_id: int, table_id: int):
        return (
            self.db.query(Order)
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.table_id == table_id,
                Order.status.in_(ACTIVE_ORDER_STATUSES)
            )
            .first()
        )


    def serialize_order(self, order: Order):
        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        return {
            "id": order.id,
            "table_id": order.table_id,
            "table_number": order.table.number,
            "status": order.status.value,
            "created_at": order.created_at,
            "items": [
                {
                    "id": item.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "subtotal": float(item.quantity * item.unit_price),
                    "status": item.status.value
                }
                for item in order.items
            ],
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "method": p.method
                }
                for p in order.payments
            ],
            "total": float(total),
            "subtotal": float(subtotal),
            "discount": float(order.discount or 0),
            "total_paid": float(total_paid),
            "remaining": float(remaining)
        }


    def serialize_orders(self, restaurant_id: int):
        orders = self.get_active_orders(restaurant_id)

        result = []

        for order in orders:
            subtotal, total, total_paid, remaining = self.calculate_totals(order)

            result.append({
                "id": order.id,
                "table_id": order.table_id,
                "table_number": order.table.number,
                "status": order.status,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.quantity * item.unit_price,
                        "status": item.status
                    }
                    for item in order.items
                ],
                "total": total,
                "subtotal": subtotal,
                "discount": float(order.discount or 0),
                "total_paid": total_paid,
                "remaining": remaining
            })

        return result



    # -------------------------
    # Totales
    # -------------------------

    def calculate_totals(self, order: Order):
        subtotal = sum((item.quantity * item.unit_price for item in order.items), Decimal("0"))
        discount = order.discount or Decimal("0")
        total = max(subtotal - discount, Decimal("0"))
        total_paid = sum(payment.amount for payment in order.payments)
        remaining = total - total_paid
        return subtotal, total, total_paid, remaining

    # -------------------------
    # Crear / agregar items
    # -------------------------

    def add_item(self, order: Order, product_id: int, quantity: int) -> OrderItem:
        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Cannot add items to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if quantity <= 0:
            raise OrderDomainError(
                "Quantity must be greater than zero",
                ErrorCode.INVALID_OPERATION
            )

        # Buscar producto en la base
        product = (
            self.db.query(Product)
            .filter(
                Product.id == product_id,
                Product.restaurant_id == order.restaurant_id,
                Product.active
            )
            .first()
        )
        if not product:
            raise OrderDomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
            )

        existing_item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id,
                OrderItem.product_id == product.id,
                OrderItem.status == OrderItemStatus.PENDING
            )
            .first()
        )

        if existing_item:
            existing_item.quantity += quantity
            item = existing_item
        else:
            item = OrderItem(
                restaurant_id=order.restaurant_id,
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                status=OrderItemStatus.PENDING
            )
            self.db.add(item)
        
        self.db.commit()
        self.db.refresh(item)

        previous_status = order.status
        self.db.refresh(order)  # Trae la lista de items actualizada
        self.recalculate_order_status(order)

        # =========================
        # 🔔 EVENTOS
        # =========================
        event_service.emit_to_station(
            order.restaurant_id,
            product.station_id,
            {"type": "NEW_ITEM", "order_id": order.id}
        )

        if order.status != previous_status:
            for role in [UserRole.WAITER, UserRole.CASHIER]:
                event_service.emit_to_role(
                    order.restaurant_id,
                    role,
                    {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": order.status.value}
                )

        for role in [UserRole.WAITER, UserRole.CASHIER]:
            print("EVENT emit_to_role en ADD ITEM ORDER_UPDATED")
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "ORDER_UPDATED", "order_id": order.id}
            )

        return item


    def add_product_to_table(self, restaurant_id: int, table_id: int, product_id: int, quantity: int):
        table = self.db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table:
            raise OrderDomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND
            )

        order = self.get_active_order(restaurant_id, table_id)
        if not order:
            order = Order(table_id=table_id, restaurant_id=restaurant_id, status=OrderStatus.OPEN)
            self.db.add(order)
            self.db.flush()

        product = self.db.query(Product).filter(Product.id == product_id, Product.restaurant_id == restaurant_id, Product.active).first()
        if not product:
            raise OrderDomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
            )

        item = self.add_item(order, product.id, quantity)
        return {"order_id": order.id, "item_id": item.id}


    # -------------------------
    # Estados
    # -------------------------

    def update_status(self, order: Order, new_status: OrderStatus):
        if order.status == new_status:
            return order

        if not is_valid_order_transition(order.status, new_status):
            raise OrderDomainError(
                "Invalid order status transition",
                ErrorCode.INVALID_TRANSITION,
                context={
                    "from": order.status.value,
                    "to": new_status.value,
                    "order_id": order.id
                }
            )

        previous_status = order.status
        order.status = new_status

        self.db.commit()
        self.db.refresh(order)

        # Emit events solo si cambio
        if previous_status != new_status:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": new_status.value}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            {"type": "ORDER_UPDATED", "order_id": order.id}
        )
        return order


    def recalculate_order_status(self, order: Order):
        active_items = [
            i for i in order.items
            if i.status != OrderItemStatus.CANCELLED
        ]

        if not active_items:
            # Si todos los ítems fueron cancelados y la orden
            # todavía no fue enviada a cocina, se cancela automáticamente.
            # En estados posteriores (SENT, IN_PROGRESS, etc.) esto
            # no puede ocurrir porque siempre hay ítems activos.
            if order.status in [OrderStatus.DRAFT, OrderStatus.OPEN]:
                self.update_status(order, OrderStatus.CANCELLED)
            return

        statuses = [i.status for i in active_items]

        if any(s == OrderItemStatus.IN_PROGRESS for s in statuses):
            self.update_status(order, OrderStatus.IN_PROGRESS)
        elif any(s == OrderItemStatus.SENT for s in statuses):
            self.update_status(order, OrderStatus.SENT)
        elif any(s == OrderItemStatus.PENDING for s in statuses):
            self.update_status(order, OrderStatus.OPEN)
        elif all(s in [OrderItemStatus.READY, OrderItemStatus.DELIVERED] for s in statuses):
            self.update_status(order, OrderStatus.READY)

    # -------------------------
    # Enviar a cocina
    # -------------------------

    def send_to_kitchen(self, order: Order):
        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Order is closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        pending_items = [i for i in order.items if i.status == OrderItemStatus.PENDING]
        if not pending_items:
            raise OrderDomainError(
                "No pending items to send",
                ErrorCode.NO_PENDING_ITEMS_TO_SEND
            )

        previous_status = order.status
        for item in pending_items:
            item.status = OrderItemStatus.SENT

        self.recalculate_order_status(order)
        self.db.commit()

        # Agrupar por estación y emitir
        station_ids = {i.product.station_id for i in pending_items}
        for station_id in station_ids:
            event_service.emit_to_station(
                order.restaurant_id,
                station_id,
                {"type": "ORDER_UPDATED", "order_id": order.id}
            )

        if order.status != previous_status:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": order.status.value}
            )

        # 🔹 Convertir a JSON serializable
        result = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "status": item.status.value,
                "subtotal": float(item.quantity * item.unit_price)
            }
            for item in pending_items
        ]

        return result

    # -------------------------
    # Pagos
    # -------------------------

    def add_payment(self, order: Order, amount: Decimal, method: str):
        from app.domain.cash_register.cash_register_service import CashRegisterService

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Order already closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        cash_service = CashRegisterService()
        cash_register = cash_service.require_open_cash_register(self.db, order.restaurant_id)

        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        if amount > remaining:
            raise OrderDomainError(
                "Payment exceeds remaining balance",
                ErrorCode.PAYMENT_EXCEEDS_REMAINING,
                context={
                    "amount": float(amount),
                    "remaining": float(remaining)
                }
            )

        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=amount,
            method=method,
            cash_register_id=cash_register.id
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        # Emitir eventos
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "PAYMENT_ADDED", "order_id": order.id, "amount": float(amount), "method": method}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )
        return payment


    def cancel_payment(self, restaurant_id: int, payment_id: int):
        print("Id: ",payment_id)
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.restaurant_id == restaurant_id
            )
            .first()
        )

        if not payment:
            raise OrderDomainError(
                "Pago no encontrado",
                ErrorCode.PAYMENT_NOT_FOUND
                )

        if payment.order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Cannot cancel payment from closed order",
                ErrorCode.INVALID_OPERATION
            )

        order_id = payment.order_id
        amount = payment.amount
        method = payment.method

        self.db.delete(payment)
        self.db.commit()

        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                restaurant_id,
                role,
                {
                    "type": "PAYMENT_DELETED",
                    "order_id": order_id,
                    "amount": float(amount),
                    "method": method                   
                }
            )

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )

        return {"deleted": payment_id}

    # -------------------------
    # Cerrar orden
    # -------------------------

    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "La orden ya está cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        if remaining > 0:
            raise OrderDomainError(
                f"La orden no está paga. Saldo: {remaining:.2f}",
                ErrorCode.ORDER_HAS_REMAINING_BALANCE,
                context={"remaining": float(remaining)}
            )

        if not order.items:
            raise OrderDomainError(
                "La orden no tiene items",
                ErrorCode.ORDER_EMPTY
            )

        not_delivered = [i for i in order.items if i.status != OrderItemStatus.DELIVERED]

        if not_delivered:
            raise OrderDomainError(
                "No se puede cerrar la orden. Hay items no entregados",
                ErrorCode.ORDER_ITEMS_NOT_DELIVERED,
                context={"items": [i.id for i in not_delivered]}
            )

        self.update_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()
        self.db.commit()

        # Emitir evento
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "ORDER_CLOSED", "order_id": order.id}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )

        return order

    # -------------------------
    # Eliminar item de la orden
    # -------------------------

    def delete_order_item(
        self,
        restaurant_id: int,
        order_id: int,
        item_id: int,
    ):

        item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.id == item_id,
                OrderItem.restaurant_id == restaurant_id
            )
            .first()
        )

        if not item:
            raise OrderDomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"item": item_id}
            )

        if item.order_id != order_id:
            raise OrderDomainError(
                "Item no pertenece a la orden",
                ErrorCode.ITEM_NOT_IN_ORDER,
                context={
                    "item": item_id,
                    "order_id": order_id
                }
            )
        
        if item.status != OrderItemStatus.PENDING:
            raise OrderDomainError(
                "El item ya fue enviado a la cocina",
                ErrorCode.ITEM_ALREADY_SENT,
                context={"item": item.id}
            )

        order = (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )

        self.db.delete(item)
        self.db.commit()

        self.recalculate_order_status(order)

        # 🔔 EVENTO
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                restaurant_id,
                role,
                {"type": "ORDER_UPDATED", "order_id": order_id}
            )

        return {"message": "Item eliminado"}

```

---

### .\backend\app\domain\order\order_transitions.py

**Funciones (1):**
- is_valid_order_transition

**Clases (0):**

**Imports (1):**
- app.models.order.OrderStatus

```python
# app/domain/order_transitions.py

from app.models.order import OrderStatus

ORDER_ALLOWED_TRANSITIONS = {
    OrderStatus.DRAFT: [
        OrderStatus.OPEN,
        OrderStatus.CANCELLED
    ],
    OrderStatus.OPEN: [
        OrderStatus.SENT,
        OrderStatus.CANCELLED
    ],
    OrderStatus.SENT: [
        OrderStatus.IN_PROGRESS,
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.IN_PROGRESS: [
        OrderStatus.SENT,
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.READY: [
        OrderStatus.OPEN,
        OrderStatus.SENT,
        OrderStatus.CLOSED
    ],
    OrderStatus.CLOSED: [],
    OrderStatus.CANCELLED: []
}


def is_valid_order_transition(
    current_status: OrderStatus,
    new_status: OrderStatus
) -> bool:
    allowed = ORDER_ALLOWED_TRANSITIONS.get(current_status, [])
    return new_status in allowed
```

---

### .\backend\app\domain\order_item\dependencies.py

**Funciones (1):**
- get_order_item_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- order_item_service.OrderItemService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .order_item_service import OrderItemService


def get_order_item_service(
    db: Session = Depends(get_db)
) -> OrderItemService:

    return OrderItemService(db)
```

---

### .\backend\app\domain\order_item\order_item_service.py

**Funciones (4):**
- __init__
- get_item
- update_status
- change_item_status

**Clases (1):**
- OrderItemService

**Imports (12):**
- fastapi.HTTPException
- sqlalchemy.orm.Session
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.user.User
- app.models.user.UserRole
- app.models.order.OrderStatus
- app.domain.order.order_service.OrderService
- app.domain.order_item.order_item_transitions.can_transition
- app.domain.errors.OrderItemDomainError
- app.domain.error_codes.ErrorCode
- app.services.event_service.event_service

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors import OrderItemDomainError
from app.domain.error_codes import ErrorCode

from app.services.event_service import event_service



class OrderItemService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener item
    # -------------------------
    
    def get_item(self, item_id: int, restaurant_id: int):

        item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.id == item_id,
                OrderItem.restaurant_id == restaurant_id
            )
            .first()
        )

        if not item:
            raise OrderItemDomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"Item:": item_id })

        return item

    # -------------------------
    # Actualizar estado
    # -------------------------

    def update_status(
        self,
        item_id: int,
        new_status: OrderItemStatus,
        user: User
    ):
        item = self.get_item(item_id, user.restaurant_id)
        order_service = OrderService(self.db)
        previous_status = self.change_item_status(
            item,
            new_status,
            user,
            order_service
        )
        self.db.commit()
        self.db.refresh(item)
        order = item.order

        # =========================
        # EVENTOS
        # =========================

        payload = {
            "type": "ITEM_STATUS_CHANGED",
            "order_id": order.id,
            "item_id": item.id,
            "status": new_status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # cocina
        event_service.emit_to_station(
            order.restaurant_id,
            item.product.station_id,
            payload
        )

        # mozos
        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            payload
        )

        # evento especial READY
        if new_status == OrderItemStatus.READY:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {
                    "type": "ITEM_READY",
                    "order_id": order.id,
                    "table": order.table.number,
                    "product": item.product.name,
                    "quantity": item.quantity
                }
            )

        # cambio de estado de orden
        if order.status != previous_status:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {
                    "type": "ORDER_STATUS_CHANGED",
                    "order_id": order.id,
                    "status": order.status.value
                }
            )
        return item
    
    # -------------------------
    # Cambiar estado
    # -------------------------

    def change_item_status(
        self,
        item: OrderItem,
        new_status: OrderItemStatus,
        user: User,
        order_service: OrderService
    ):
        order = item.order
        if order.status == OrderStatus.CLOSED:
            raise OrderItemDomainError(
                "No se pueden modificar items en una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={"order_id": order.id}
            )

        # reglas por rol
        if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
            raise OrderItemDomainError(
                "Sólo COCINA puede comenzar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
            raise OrderItemDomainError(
                "Sólo COCINA puede marcar items como listos",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
            raise OrderItemDomainError(
                "Sólo MOZO puede entregar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "WAITER"}
            )

        if not can_transition(item.status, new_status):
            raise OrderItemDomainError(
                f"Transición inválida desde {item.status.value} a {new_status.value}",
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "from": item.status.value,
                    "to": new_status.value
                }
            )
        item.status = new_status
        previous_status = order.status
        order_service.recalculate_order_status(order)
        return previous_status

```

---

### .\backend\app\domain\order_item\order_item_transitions.py

**Funciones (2):**
- can_transition
- allowed_transitions

**Clases (0):**

**Imports (1):**
- app.models.order_item.OrderItemStatus

```python
from app.models.order_item import OrderItemStatus


_ALLOWED_TRANSITIONS = {
    OrderItemStatus.PENDING: [
        OrderItemStatus.SENT,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.SENT: [
        OrderItemStatus.IN_PROGRESS,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.IN_PROGRESS: [
        OrderItemStatus.READY,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.READY: [
        OrderItemStatus.DELIVERED
    ],
    OrderItemStatus.DELIVERED: [],
    OrderItemStatus.CANCELLED: []
}


def can_transition(current: OrderItemStatus, new: OrderItemStatus) -> bool:
    return new in _ALLOWED_TRANSITIONS.get(current, [])


def allowed_transitions(status: OrderItemStatus) -> list[OrderItemStatus]:
    return _ALLOWED_TRANSITIONS.get(status, [])
```

---

### .\backend\app\domain\product\dependencies.py

**Funciones (1):**
- get_product_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- product_service.ProductService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .product_service import ProductService


def get_product_service(
    db: Session = Depends(get_db)
) -> ProductService:
    return ProductService(db)
```

---

### .\backend\app\domain\product\product_service.py

**Funciones (6):**
- __init__
- get_product
- create_product
- list_products
- update_product
- toggle_product

**Clases (1):**
- ProductService

**Imports (7):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.models.product.Product
- app.schemas.product.ProductCreate
- app.schemas.product.ProductUpdate
- app.domain.errors.ProductDomainError
- app.domain.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

from app.domain.errors import ProductDomainError
from app.domain.error_codes import ErrorCode


class ProductService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener producto
    # -------------------------

    def get_product(self, product_id: int, restaurant_id: int):
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.restaurant_id == restaurant_id
        ).first()
        if not product:
            raise ProductDomainError(
                "Product not found",
                ErrorCode.PRODUCT_NOT_FOUND,
                context={"product_id": product_id})
        return product

    # -------------------------
    # Crear producto
    # -------------------------

    def create_product(self, restaurant_id: int, data: ProductCreate):
        product = Product(
            name=data.name,
            price=data.price,
            category_id=data.category_id,
            station_id=data.station_id,
            restaurant_id=restaurant_id
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    # -------------------------
    # Listar productos
    # -------------------------

    def list_products(self, restaurant_id: int):
        return (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.station)
            )
            .filter(Product.restaurant_id == restaurant_id)
            .all()
        )

    # -------------------------
    # Actualizar producto
    # -------------------------

    def update_product(self, product_id: int, restaurant_id: int, data: ProductUpdate):
        product = self.get_product(product_id, restaurant_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    # -------------------------
    # Cambiar producto - Activo/Inactivo
    # -------------------------

    def toggle_product(self, product_id: int, restaurant_id: int):
        product = self.get_product(product_id, restaurant_id)
        product.active = not product.active
        self.db.commit()
        self.db.refresh(product)
        return product
```

---

### .\backend\app\domain\stations\dependencies.py

**Funciones (1):**
- get_station_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- station_service.StationService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .station_service import StationService


def get_station_service(
    db: Session = Depends(get_db)
) -> StationService:
    return StationService(db)
```

---

### .\backend\app\domain\stations\station_service.py

**Funciones (7):**
- __init__
- create_station
- list_stations
- list_active_stations
- get_station
- update_station
- toggle_station

**Clases (1):**
- StationService

**Imports (5):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.models.production_station.ProductionStation
- app.domain.errors.StationDomainError
- app.domain.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session, joinedload
from app.models.production_station import ProductionStation
from app.domain.errors import StationDomainError
from app.domain.error_codes import ErrorCode


class StationService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Crear estación
    # ------------------------- 

    def create_station(self, restaurant_id: int, name: str):
        existing = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name
            )
            .first()
        )
        if existing:
            raise StationDomainError(
                "Station name already exists",
                code=ErrorCode.STATION_NAME_ALREADY_EXISTS,
                context={"name": name}
            )
        station = ProductionStation(
            name=name,
            restaurant_id=restaurant_id,
            active=True
        )
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station
    
    # -------------------------
    # Listar estaciones
    # -------------------------

    def list_stations(self, restaurant_id: int):
        return (
            self.db.query(ProductionStation)
            .filter(ProductionStation.restaurant_id == restaurant_id)
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Listar estaciones activas
    # -------------------------

    def list_active_stations(self, restaurant_id: int):
        return (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.active == True
            )
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Obtener estación
    # -------------------------

    def get_station(self, restaurant_id: int, station_id: int):
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id
            )
            .first()
        )
        if not station:
            raise StationDomainError(
                "Station not found",
                code=ErrorCode.STATION_NOT_FOUND
            )
        return station

    # -------------------------
    # Actualizar estación
    # -------------------------

    def update_station(self, restaurant_id: int, station_id: int, name: str):
        station = self.get_station(restaurant_id, station_id)
        existing = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name,
                ProductionStation.id != station_id
            )
            .first()
        )
        if existing:
            raise StationDomainError(
                "Station name already exists",
                code=ErrorCode.STATION_NAME_ALREADY_EXISTS
            )
        station.name = name
        self.db.commit()
        self.db.refresh(station)
        return station

    # -------------------------
    # Activar/desactivar estación
    # -------------------------

    def toggle_station(self, restaurant_id: int, station_id: int):
        station = self.get_station(restaurant_id, station_id)
        station.active = not station.active
        self.db.commit()
        self.db.refresh(station)
        return station
```

---

### .\backend\app\domain\table\dependencies.py

**Funciones (1):**
- get_table_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- table_service.TableService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .table_service import TableService


def get_table_service(db: Session = Depends(get_db)):
    return TableService(db)
```

---

### .\backend\app\domain\table\table_service.py

**Funciones (10):**
- __init__
- list_tables
- list_tables_status
- _get_table
- create_table
- update_table
- update_position
- deactivate_table
- activate_table
- touch_table

**Clases (1):**
- TableService

**Imports (9):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- sqlalchemy.func
- app.models.Table
- app.models.order.Order
- app.schemas.table.TablePositionUpdate
- app.domain.order.constants.ACTIVE_ORDER_STATUSES
- app.domain.errors.TableDomainError
- app.domain.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Table
from app.models.order import Order
from app.schemas.table import TablePositionUpdate

from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors import TableDomainError
from app.domain.error_codes import ErrorCode


class TableService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Listar mesas
    # -------------------------

    def list_tables(self, restaurant_id: int, active: bool | None = True):
        query = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id
        )

        if active is not None:
            query = query.filter(Table.active == active)
        return query.order_by(Table.number).all()


    # -------------------------
    # Listar status de las mesas
    # -------------------------

    def list_tables_status(self, restaurant_id: int):

        active_order_subquery = (
            self.db.query(
                Order.table_id,
                func.max(Order.id).label("order_id")
            )
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status.in_(ACTIVE_ORDER_STATUSES)
            )
            .group_by(Order.table_id)
            .subquery()
        )
        rows = (
            self.db.query(
                Table.id,
                Table.number,
                Table.x,
                Table.y,
                Table.capacity,
                Table.shape,
                Table.active,
                Order.id.label("order_id"),
                Order.status.label("order_status")
            )
            .outerjoin(
                active_order_subquery,
                Table.id == active_order_subquery.c.table_id
            )
            .outerjoin(
                Order,
                Order.id == active_order_subquery.c.order_id
            )
            .filter(
                Table.restaurant_id == restaurant_id,
                Table.active.is_(True)
            )
            .order_by(Table.number)
            .all()
        )
        return [
            {
                "id": row.id,
                "number": row.number,
                "x": row.x,
                "y": row.y,
                "capacity": row.capacity,
                "shape": row.shape,
                "active": row.active,
                "status": "ocupada" if row.order_id else "libre",
                "order_id": row.order_id,
                "order_status": row.order_status
            }
            for row in rows
        ]

    # -------------------------
    # Devolver mesa
    # -------------------------        

    def _get_table(self, restaurant_id: int, table_id: int, active_only=False) -> Table:
        query = self.db.query(Table).filter(
            Table.id == table_id,
            Table.restaurant_id == restaurant_id
        )
        if active_only:
            query = query.filter(Table.active.is_(True))
        table = query.first()
        if not table:
            raise TableDomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND,
                context={"table_id": table_id})
        return table

    # -------------------------
    # Crear mesa
    # -------------------------

    def create_table(self, restaurant_id, table_in):
        max_number = self.db.query(func.max(Table.number)).filter(
            Table.restaurant_id == restaurant_id
        ).scalar()
        new_number = (max_number or 0) + 1
        table = Table(
            restaurant_id=restaurant_id,
            number=new_number,
            x=table_in.x,
            y=table_in.y,
            capacity=table_in.capacity,
            shape=table_in.shape
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Actualizar mesa
    # -------------------------

    def update_table(self, restaurant_id, table_id, table_in):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        update_data = table_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(table, field, value)
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Actualizar posición de la mesa
    # -------------------------

    def update_position(
        self,
        restaurant_id: int,
        table_id: int,
        data: TablePositionUpdate
    ) -> None:
        table = self._get_table(restaurant_id, table_id, active_only=True)

        table.x = data.x
        table.y = data.y

        self.db.commit()

    # -------------------------
    # Desactivar mesa
    # -------------------------

    def deactivate_table(self, restaurant_id, table_id):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        table.active = False
        self.db.commit()
        return {"message": "Table deactivated"}

    # -------------------------
    # Activar mesa
    # -------------------------

    def activate_table(self, restaurant_id, table_id):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        table.active = True
        self.db.commit()
        return {"message": "Table activated"}    
    
    # -------------------------
    # Tocar mesa
    # -------------------------

    def touch_table(self, restaurant_id: int, table_id: int):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        if not table:
            raise TableDomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND,
                context={"table_id": table_id})
        order = self.db.query(Order).filter(
            Order.table_id == table_id,
            Order.restaurant_id == restaurant_id,
            Order.status.in_(ACTIVE_ORDER_STATUSES)
        ).first()
        return {
            "table_id": table.id,
            "table_number": table.number,
            "order_id": order.id if order else None
        }
```

---

### .\backend\app\domain\user\dependencies.py

**Funciones (1):**
- get_user_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- user_service.UserService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .user_service import UserService


def get_user_service(
    db: Session = Depends(get_db)
) -> UserService:

    return UserService(db)
```

---

### .\backend\app\domain\user\user_service.py

**Funciones (6):**
- __init__
- get_user
- list_users
- create_user
- update_user
- toggle_user

**Clases (1):**
- UserService

**Imports (7):**
- sqlalchemy.orm.Session
- app.models.user.User
- app.schemas.user.UserCreate
- app.schemas.user.UserUpdate
- app.core.security.get_password_hash
- app.domain.errors.UserDomainError
- app.domain.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

from app.domain.errors import UserDomainError
from app.domain.error_codes import ErrorCode


class UserService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener usuario
    # -------------------------

    def get_user(self, user_id: int, restaurant_id: int):

        user = self.db.query(User).filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        ).first()

        if not user:
            raise UserDomainError(
                "User not found",
                ErrorCode.USER_NOT_FOUND
            )

        return user


    # -------------------------
    # Listar usuarios
    # -------------------------

    def list_users(self, restaurant_id: int):

        return (
            self.db.query(User)
            .filter(User.restaurant_id == restaurant_id)
            .order_by(User.username)
            .all()
        )


    # -------------------------
    # Crear usuario
    # -------------------------

    def create_user(self, restaurant_id: int, data: UserCreate):

        existing = self.db.query(User).filter(
            User.restaurant_id == restaurant_id,
            User.username == data.username
        ).first()

        if existing:
            raise UserDomainError(
                "User exists",
                ErrorCode.USERNAME_ALREADY_EXISTS,
                context={"username": data.username}
            )

        hashed = get_password_hash(data.password)

        user = User(
            username=data.username,
            password_hash=hashed,
            role=data.role,
            restaurant_id=restaurant_id,
            active=True
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user


    # -------------------------
    # Actualizar usuario
    # -------------------------

    def update_user(self, user_id: int, restaurant_id: int, data: UserUpdate):

        user = self.get_user(user_id, restaurant_id)

        if data.username is not None:

            existing = self.db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.username == data.username,
                User.id != user_id
            ).first()

            if existing:
                raise UserDomainError(
                    "User exists",
                    ErrorCode.USERNAME_ALREADY_EXISTS,
                    context={"username": data.username}
                )

            user.username = data.username

        if data.role is not None:
            user.role = data.role

        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        self.db.commit()
        self.db.refresh(user)

        return user


    # -------------------------
    # Activar / Desactivar usuario
    # -------------------------

    def toggle_user(self, user_id: int, restaurant_id: int):

        user = self.get_user(user_id, restaurant_id)

        user.active = not user.active

        self.db.commit()
        self.db.refresh(user)

        return user
```

---

### .\backend\app\events\redis_listener.py

**Funciones (0):**

**Clases (0):**

**Imports (5):**
- asyncio
- json
- app.core.redis.redis_client
- app.websocket.manager.manager
- app.services.event_service.INSTANCE_ID

```python
import asyncio
import json

from app.core.redis import redis_client
from app.websocket.manager import manager
from app.services.event_service import INSTANCE_ID


async def redis_event_listener():

    pubsub = redis_client.pubsub()

    await pubsub.subscribe("restaurant_events")

    print("Redis listener started")

    try:
        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            # ignorar eventos de esta misma instancia
            if data.get("origin") == INSTANCE_ID:
                continue

            restaurant_id = data.get("restaurant_id")
            target = data.get("target")
            target_id = data.get("target_id")

            if target == "broadcast":
                await manager.broadcast(restaurant_id, data["payload"])

            elif target == "role":
                await manager.send_to_role(restaurant_id, target_id, data["payload"])

            elif target == "station":
                await manager.send_to_station(restaurant_id, target_id, data["payload"])

    except asyncio.CancelledError:
        print("Redis listener stopped")

    finally:
        await pubsub.unsubscribe("restaurant_events")
        await pubsub.close()
```

---

### .\backend\app\models\cash_movement.py

**Funciones (0):**

**Clases (2):**
- CashMovementType
- CashMovement

**Imports (11):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.DateTime
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Enum
- sqlalchemy.String
- sqlalchemy.sql.func
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum

from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Enum, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashMovementType(str, enum.Enum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class CashMovement(Base):

    __tablename__ = "cash_movements"

    id = Column(Integer, primary_key=True)

    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        Enum(CashMovementType),
        nullable=False
    )

    amount = Column(Numeric(10,2))

    reason = Column(String(255))

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    cash_register = relationship(
        "CashRegister",
        back_populates="movements"
    )
```

---

### .\backend\app\models\cash_register.py

**Funciones (0):**

**Clases (1):**
- CashRegister

**Imports (10):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.DateTime
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Boolean
- sqlalchemy.JSON
- sqlalchemy.sql.func
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashRegister(Base):

    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    is_open = Column(
        Boolean,
        default=True,
        nullable=False
    )

    opened_by_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    closed_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    opened_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    opening_amount = Column(
        Numeric(10,2),
        nullable=False
    )

    expected_cash = Column(
        Numeric(10,2),
        nullable=True
    )

    counted_cash = Column(
        Numeric(10,2),
        nullable=True
    )

    difference = Column(
        Numeric(10,2),
        nullable=True
    )

    total_sales = Column(
        Numeric(10,2),
        nullable=True
    )

    payments_snapshot = Column(JSON)

    # -------------------------
    # RELATIONSHIPS
    # -------------------------

    restaurant = relationship(
        "Restaurant",
        back_populates="cash_registers"
    )

    movements = relationship(
        "CashMovement",
        back_populates="cash_register",
        cascade="all, delete-orphan"
    )
```

---

### .\backend\app\models\category.py

**Funciones (0):**

**Clases (1):**
- Category

**Imports (8):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.String
- sqlalchemy.UniqueConstraint
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
from sqlalchemy import Column, Integer, Boolean, ForeignKey, String, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_category_name_per_restaurant"),
    )
    restaurant = relationship("Restaurant", back_populates="categories")
    products = relationship("Product", back_populates="category")


```

---

### .\backend\app\models\domain_event.py

**Funciones (0):**

**Clases (1):**
- DomainEvent

**Imports (9):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.JSON
- sqlalchemy.DateTime
- sqlalchemy.func
- sqlalchemy.ForeignKey
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
from sqlalchemy import Column, Integer, String, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DomainEvent(Base):

    __tablename__ = "domain_events"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    event_type = Column(String, nullable=False)

    payload = Column(JSON)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="domain_events"
    )
```

---

### .\backend\app\models\order.py

**Funciones (0):**

**Clases (2):**
- OrderStatus
- Order

**Imports (13):**
- enum
- uuid
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.String
- sqlalchemy.DateTime
- sqlalchemy.Enum
- sqlalchemy.Index
- sqlalchemy.sql.func
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
import enum
import uuid
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String, DateTime, Enum, Index
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    SENT = "SENT"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.OPEN,
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    discount = Column(Numeric(10, 2), nullable=False, default=0)
    external_id = Column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )    
    __table_args__ = (
        Index("ix_orders_restaurant_status", "restaurant_id", "status"),
    )
    table = relationship("Table", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

```

---

### .\backend\app\models\order_item.py

**Funciones (0):**

**Clases (2):**
- OrderItemStatus
- OrderItem

**Imports (9):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.ForeignKey
- sqlalchemy.Numeric
- sqlalchemy.String
- sqlalchemy.Enum
- sqlalchemy.orm.relationship
- enum
- app.db.base_class.Base

```python
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class OrderItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    # 🔥 MULTI-TENANT
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)

    unit_price = Column(Numeric(10, 2), nullable=False)

    status = Column(
        Enum(OrderItemStatus),
        default=OrderItemStatus.PENDING,
        nullable=False
    )

    notes = Column(String, nullable=True)

    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    restaurant = relationship("Restaurant", back_populates="order_items")

```

---

### .\backend\app\models\payment.py

**Funciones (0):**

**Clases (2):**
- PaymentMethod
- Payment

**Imports (8):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Enum
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum
from sqlalchemy import Column, Integer, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )
    order = relationship("Order", back_populates="payments")
    cash_register = relationship("CashRegister")
    restaurant = relationship("Restaurant", back_populates="payments")




```

---

### .\backend\app\models\product.py

**Funciones (0):**

**Clases (1):**
- Product

**Imports (9):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Numeric
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.UniqueConstraint
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)
    station_id = Column(ForeignKey("production_stations.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_product_name_per_restaurant"),
    )

    category = relationship("Category", back_populates="products")
    station = relationship("ProductionStation", back_populates="products")
    restaurant = relationship("Restaurant", back_populates="products")


```

---

### .\backend\app\models\production_station.py

**Funciones (0):**

**Clases (1):**
- ProductionStation

**Imports (8):**
- app.db.base_class.Base
- sqlalchemy.orm.relationship
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.UniqueConstraint

```python
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint

class ProductionStation(Base):
    __tablename__ = "production_stations"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_station_name_per_restaurant"),
    )
    restaurant = relationship("Restaurant", back_populates="stations")
    products = relationship("Product", back_populates="station")

```

---

### .\backend\app\models\restaurant.py

**Funciones (0):**

**Clases (1):**
- Restaurant

**Imports (10):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.DateTime
- sqlalchemy.Boolean
- sqlalchemy.orm.relationship
- datetime.datetime
- datetime.timezone
- uuid
- app.db.base_class.Base

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    active = Column(Boolean, default=True, nullable=False)

    plan = Column(String, default="basic", nullable=False)

    external_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # Relaciones
    tables = relationship("Table", back_populates="restaurant", cascade="all, delete")
    products = relationship("Product", back_populates="restaurant", cascade="all, delete")
    payments = relationship("Payment", back_populates="restaurant", cascade="all, delete")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete")
    cash_registers = relationship("CashRegister", back_populates="restaurant", cascade="all, delete")
    stations = relationship("ProductionStation", back_populates="restaurant", cascade="all, delete")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete")
    order_items = relationship("OrderItem", back_populates="restaurant", cascade="all, delete")
    users = relationship("User", back_populates="restaurant")
    domain_events = relationship("DomainEvent", back_populates="restaurant")



```

---

### .\backend\app\models\restaurant_layout.py

**Funciones (0):**

**Clases (1):**
- RestaurantLayout

**Imports (6):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Boolean
- sqlalchemy.String
- sqlalchemy.ForeignKey
- app.db.base_class.Base

```python
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from app.db.base_class import Base


class RestaurantLayout(Base):

    __tablename__ = "restaurant_layout"

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        primary_key=True
    )

    width = Column(Integer, default=900)
    height = Column(Integer, default=500)

    grid_size = Column(Integer, default=40)
    snap_to_grid = Column(Boolean, default=True)

    background_image = Column(String, nullable=True)
```

---

### .\backend\app\models\table.py

**Funciones (0):**

**Clases (1):**
- Table

**Imports (10):**
- uuid
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.String
- sqlalchemy.UniqueConstraint
- sqlalchemy.Index
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import uuid
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    number = Column(Integer, nullable=False)

    active = Column(Boolean, default=True, nullable=False)

    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)

    capacity = Column(Integer, default=4, nullable=False)

    shape = Column(String, default="Circular")

    external_id = Column(
        String,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )

    # 🔐 Multi-tenant constraints correctas
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "number",
            name="uq_table_number_per_restaurant"
        ),
        UniqueConstraint(
            "restaurant_id",
            "external_id",
            name="uq_table_external_per_restaurant"
        ),
        Index(
            "ix_table_restaurant_active",
            "restaurant_id",
            "active"
        ),
    )

    # Relaciones
    orders = relationship(
        "Order",
        back_populates="table"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="tables"
    )
```

---

### .\backend\app\models\user.py

**Funciones (0):**

**Clases (2):**
- UserRole
- User

**Imports (9):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Enum
- sqlalchemy.ForeignKey
- sqlalchemy.Boolean
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    WAITER = "WAITER"
    KITCHEN = "KITCHEN"
    CASHIER = "CASHIER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    username = Column(String, nullable=False)

    role = Column(Enum(UserRole), nullable=False)

    password_hash = Column(String, nullable=False)

    active = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="users")

```

---

### .\backend\app\models\__init__.py

**Funciones (0):**

**Clases (0):**

**Imports (13):**
- table.Table
- order.Order
- product.Product
- order_item.OrderItem
- payment.Payment
- cash_register.CashRegister
- restaurant.Restaurant
- production_station.ProductionStation
- category.Category
- user.User
- domain_event.DomainEvent
- restaurant_layout.RestaurantLayout
- cash_movement.CashMovement

```python
from .table import Table
from .order import Order
from .product import Product
from .order_item import OrderItem
from .payment import Payment
from .cash_register import CashRegister
from .restaurant import Restaurant
from .production_station import ProductionStation
from .category import Category
from .user import User
from .domain_event import DomainEvent
from .restaurant_layout import RestaurantLayout
from .cash_movement import CashMovement

```

---

### .\backend\app\routers\auth.py

**Funciones (2):**
- login
- get_me

**Clases (0):**

**Imports (13):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- fastapi.status
- sqlalchemy.orm.Session
- fastapi.security.OAuth2PasswordRequestForm
- app.db.session.get_db
- app.models.user.User
- app.schemas.auth.TokenResponse
- app.schemas.user.UserOut
- app.core.security.create_access_token
- app.core.security.verify_password
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserOut
from app.core.security import create_access_token, verify_password
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value,
        "restaurant_id": user.restaurant_id
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserOut)
def get_me(
    user: User = Depends(get_current_user)
):
    return user
```

---

### .\backend\app\routers\cash_register.py

**Funciones (6):**
- open_cash_register
- close_cash_register
- create_cash_movement
- delete_cash_movement
- current_cash_register
- get_cash_register_dashboard

**Clases (0):**

**Imports (18):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.user.User
- app.dependencies.auth.get_current_user
- app.domain.errors.CashRegisterDomainError
- app.schemas.cash_register.CashRegisterOpen
- app.schemas.cash_register.CashRegisterSummary
- app.schemas.cash_register.CashRegisterCloseOut
- app.schemas.cash_register.CashMovementCreate
- app.schemas.cash_register.CashRegisterClose
- app.schemas.cash_register.CashRegisterDashboard
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.cash_register.cash_movement_service.CashMovementService
- app.domain.cash_register.dependencies.get_cash_register_service
- app.domain.cash_register.dependencies.get_cash_movement_service

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.domain.errors import CashRegisterDomainError

from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterSummary,
    CashRegisterCloseOut,
    CashMovementCreate,
    CashRegisterClose,
    CashRegisterDashboard
)

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService
from app.domain.cash_register.dependencies import (
    get_cash_register_service,
    get_cash_movement_service
)

router = APIRouter(
    prefix="/cash-register",
    tags=["cash-register"]
)


@router.post("/open")
def open_cash_register(
    data: CashRegisterOpen,
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.open_cash_register(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            opening_amount=data.opening_amount
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/close", response_model=CashRegisterCloseOut)
def close_cash_register(
    payload: CashRegisterClose,
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.close_cash_register(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            counted_cash=payload.counted_cash
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movements")
def create_cash_movement(
    payload: CashMovementCreate,
    db: Session = Depends(get_db),
    service: CashMovementService = Depends(get_cash_movement_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.create_cash_movement(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            movement_type=payload.type,
            amount=payload.amount,
            reason=payload.reason
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/movements/{movement_id}")
def delete_cash_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    service: CashMovementService = Depends(get_cash_movement_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.delete_cash_movement(
            db=db,
            restaurant_id=user.restaurant_id,
            movement_id=movement_id
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/current", response_model=CashRegisterSummary | None)
def current_cash_register(
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    return service.get_current_cash_register(
        db=db,
        restaurant_id=user.restaurant_id
    )


@router.get("/dashboard", response_model=CashRegisterDashboard | None)
def get_cash_register_dashboard(
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    return service.get_dashboard(
        db=db,
        restaurant_id=user.restaurant_id
    )
```

---

### .\backend\app\routers\category.py

**Funciones (5):**
- create_category
- list_categories
- list_categories_with_products
- update_category
- delete_category

**Clases (0):**

**Imports (9):**
- fastapi.APIRouter
- fastapi.Depends
- app.dependencies.auth.get_current_user
- app.models.user.User
- app.schemas.category.CategoryResponse
- app.schemas.category.CategoryCreate
- app.schemas.category.CategoryWithProducts
- app.domain.category.category_service.CategoryService
- app.domain.category.dependencies.get_category_service

```python
from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.category import CategoryResponse, CategoryCreate, CategoryWithProducts
from app.domain.category.category_service import CategoryService
from app.domain.category.dependencies import get_category_service


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.create_category(user.restaurant_id, data.name)


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories(user.restaurant_id)


@router.get("/with-products", response_model=list[CategoryWithProducts])
def list_categories_with_products(
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories_with_products(user.restaurant_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryCreate,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.update_category(user.restaurant_id, category_id, data.name)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    service.delete_category(user.restaurant_id, category_id)
    return {"ok": True}



```

---

### .\backend\app\routers\kitchen.py

**Funciones (2):**
- get_station_items
- update_item_status

**Clases (0):**

**Imports (9):**
- fastapi.APIRouter
- fastapi.Depends
- app.models.user.User
- app.dependencies.auth.get_current_user
- app.schemas.order.order_item.OrderItemStatusUpdate
- app.schemas.order.order_item.OrderItemOut
- app.schemas.order.kitchen.KitchenItemOut
- app.domain.kitchen.dependencies.get_kitchen_service
- app.domain.kitchen.kitchen_service.KitchenService

```python
from fastapi import APIRouter, Depends

from app.models.user import User
from app.dependencies.auth import get_current_user

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemOut
)

from app.schemas.order.kitchen import KitchenItemOut

from app.domain.kitchen.dependencies import get_kitchen_service
from app.domain.kitchen.kitchen_service import KitchenService


router = APIRouter(
    prefix="/kitchen",
    tags=["kitchen"]
)

# -----------------------------------------------------

@router.get(
    "/stations/{station_id}/items",
    response_model=list[KitchenItemOut]
)
def get_station_items(
    station_id: int,
    user: User = Depends(get_current_user),
    service: KitchenService = Depends(get_kitchen_service)
):
    return service.get_station_items(
        station_id=station_id,
        user=user
    )

# -----------------------------------------------------

@router.patch(
    "/{item_id}/status",
    response_model=OrderItemOut
)
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    service: KitchenService = Depends(get_kitchen_service)
):
    item = service.update_item_status(
        item_id=item_id,
        status=data.status,
        user=user
    )
    return OrderItemOut(
        id=item.id,
        product_name=item.product.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=item.quantity * item.unit_price,
        status=item.status
    )
```

---

### .\backend\app\routers\layout.py

**Funciones (2):**
- get_layout
- update_layout

**Clases (0):**

**Imports (8):**
- fastapi.APIRouter
- fastapi.Depends
- app.schemas.layout.LayoutOut
- app.schemas.layout.LayoutUpdate
- app.dependencies.auth.get_current_user
- app.domain.layout.dependencies.get_layout_service
- app.domain.layout.layout_service.LayoutService
- app.models.user.User

```python
from fastapi import APIRouter, Depends

from app.schemas.layout import LayoutOut, LayoutUpdate
from app.dependencies.auth import get_current_user
from app.domain.layout.dependencies import get_layout_service
from app.domain.layout.layout_service import LayoutService
from app.models.user import User

router = APIRouter(prefix="/layout", tags=["layout"])


@router.get("/", response_model=LayoutOut)
def get_layout(
    user: User = Depends(get_current_user),
    service: LayoutService = Depends(get_layout_service)
):
    return service.get_layout(user.restaurant_id)


@router.patch("/", response_model=LayoutUpdate)
def update_layout(
    data: LayoutUpdate,
    user: User = Depends(get_current_user),
    service: LayoutService = Depends(get_layout_service)
):
    return service.update_layout(
        user.restaurant_id,
        data
    )
```

---

### .\backend\app\routers\orders.py

**Funciones (10):**
- get_order_service
- add_item_to_order
- send_to_kitchen
- add_payment
- close_order
- get_active_orders
- get_order
- update_order_status
- delete_order_item
- cancel_payment

**Clases (0):**

**Imports (12):**
- fastapi.APIRouter
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.user.User
- app.models.payment.Payment
- app.dependencies.auth.get_current_user
- app.schemas.order.order_item.OrderItemCreate
- app.schemas.order.payment.PaymentCreate
- app.schemas.order.order.OrderStatusUpdate
- app.domain.order.order_service.OrderService
- app.domain.order.order_service.OrderDomainError

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.payment import Payment
from app.dependencies.auth import get_current_user
from app.schemas.order.order_item import OrderItemCreate
from app.schemas.order.payment import PaymentCreate
from app.schemas.order.order import OrderStatusUpdate

from app.domain.order.order_service import OrderService, OrderDomainError

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service(db: Session = Depends(get_db)):
    return OrderService(db)

# -------------------------
# Agregar item
# -------------------------
@router.post("/{order_id}/items")
def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.add_item(order, item.product_id, item.quantity)

# -------------------------
# Enviar a cocina
# -------------------------
@router.post("/{order_id}/send-to-kitchen")
def send_to_kitchen(
    order_id: int,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.send_to_kitchen(order)

# -------------------------
# Agregar pago
# -------------------------
@router.post("/{order_id}/payments")
def add_payment(
    order_id: int,
    payment: PaymentCreate,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.add_payment(order, payment.amount, payment.method)

# -------------------------
# Cerrar orden
# -------------------------
@router.post("/{order_id}/close")
def close_order(
    order_id: int,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.close_order(order)

# -------------------------
# Obtener ordenes activas
# -------------------------
@router.get("/active")
def get_active_orders(
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.serialize_orders(user.restaurant_id)

# -------------------------
# Obtener orden por ID
# -------------------------
@router.get("/{order_id}")
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.serialize_order(order)

# -------------------------
# Actualizar estado
# -------------------------
@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.update_status(order, data.status)

# -------------------------
# Borrar item de orden
# -------------------------
@router.delete("/{order_id}/items/{item_id}")
def delete_order_item(
    order_id: int,
    item_id: int,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    service.delete_order_item(user.restaurant_id, order_id, item_id)
    return {"ok": True}

# -------------------------
# Borrar Pago
# -------------------------
@router.delete("/payments/{payment_id}")
def cancel_payment(
    payment_id: int,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    service.cancel_payment(user.restaurant_id, payment_id)
    return {"ok": True}
```

---

### .\backend\app\routers\order_items.py

**Funciones (0):**

**Clases (0):**

**Imports (9):**
- fastapi.APIRouter
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.user.User
- app.models.user.UserRole
- app.dependencies.auth.get_current_user
- app.schemas.order.order_item.OrderItemStatusUpdate
- app.domain.order_item.order_item_service.OrderItemService

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.dependencies.auth import get_current_user

from app.schemas.order.order_item import OrderItemStatusUpdate

from app.domain.order_item.order_item_service import OrderItemService

router = APIRouter(
    prefix="/order-items",
    tags=["order-items"]
)

@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = OrderItemService(db)

    item = service.update_status(
        item_id=item_id,
        new_status=data.status,
        user=user
    )

    return {
        "item_id": item.id,
        "new_status": item.status
    }
```

---

### .\backend\app\routers\products.py

**Funciones (4):**
- create_product
- list_products
- update_product
- toggle_product

**Clases (0):**

**Imports (8):**
- fastapi.APIRouter
- fastapi.Depends
- app.models.user.User
- app.schemas.product.ProductCreate
- app.schemas.product.ProductUpdate
- app.dependencies.auth.get_current_user
- app.domain.product.product_service.ProductService
- app.domain.product.dependencies.get_product_service

```python
from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate

from app.dependencies.auth import get_current_user

from app.domain.product.product_service import ProductService
from app.domain.product.dependencies import get_product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/")
def create_product(
    product: ProductCreate,
    user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(
        user.restaurant_id,
        product
    )


@router.get("/")
def list_products(
    user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):

    return service.list_products(user.restaurant_id)


@router.patch("/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):

    return service.update_product(
        product_id,
        user.restaurant_id,
        product
    )


@router.patch("/{product_id}/toggle")
def toggle_product(
    product_id: int,
    user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):

    return service.toggle_product(
        product_id,
        user.restaurant_id
    )
```

---

### .\backend\app\routers\stations.py

**Funciones (7):**
- create_station
- list_stations
- list_active_stations
- get_station
- update_station
- toggle_station
- get_station_items

**Clases (0):**

**Imports (18):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.production_station.ProductionStation
- app.models.user.User
- app.models.order.Order
- app.domain.stations.dependencies.get_station_service
- app.domain.stations.station_service.StationService
- app.schemas.station.StationCreate
- app.schemas.station.StationOut
- app.schemas.station.StationUpdate
- app.schemas.order.kitchen.KitchenItemOut
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.production_station import ProductionStation
from app.models.user import User
from app.models.order import Order

from app.domain.stations.dependencies import get_station_service
from app.domain.stations.station_service import StationService

from app.schemas.station import StationCreate, StationOut, StationUpdate
from app.schemas.order.kitchen import KitchenItemOut

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/stations", tags=["stations"])


@router.post("/", response_model=StationOut)
def create_station(
    data: StationCreate,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.create_station(
        user.restaurant_id,
        data.name
    )


@router.get("/", response_model=list[StationOut])
def list_stations(
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id)


@router.get("/active", response_model=list[StationOut])
def list_active_stations(
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.list_active_stations(user.restaurant_id)


@router.get("/{station_id}", response_model=StationOut)
def get_station(
    station_id: int,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.get_station(user.restaurant_id, station_id)


@router.patch("/{station_id}")
def update_station(
    station_id: int,
    data: StationUpdate,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.update_station(
        user.restaurant_id,
        station_id,
        data.name
    )


@router.patch("/{station_id}/toggle")
def toggle_station(
    station_id: int,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.toggle_station(
        user.restaurant_id,
        station_id
    )


@router.get("/stations/{station_id}/items", response_model=list[KitchenItemOut])
def get_station_items(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(OrderItem)
        .join(OrderItem.product)
        .join(Product.station)
        .join(OrderItem.order)
        .join(Order.table)
        .filter(
            Product.station_id == station_id,
            OrderItem.restaurant_id == user.restaurant_id,
            OrderItem.status.in_([
                OrderItemStatus.SENT,
                OrderItemStatus.IN_PROGRESS
            ])
        )
        .all()
    )

    result = []

    for item in items:
        result.append({
            "item_id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "status": item.status,
            "table_number": item.order.table.number,
            "order_id": item.order.id
        })

    return result


```

---

### .\backend\app\routers\tables.py

**Funciones (9):**
- create_table
- touch_table
- add_product_to_table
- list_tables
- list_tables_status
- update_position
- activate_table
- update_table
- deactivate_table

**Clases (0):**

**Imports (15):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.Query
- app.schemas.table.TableCreate
- app.schemas.table.TableUpdate
- app.schemas.table.TableList
- app.schemas.table.TableOut
- app.schemas.table.TablePositionUpdate
- app.schemas.order.order_item.AddItemRequest
- app.domain.table.table_service.TableService
- app.domain.table.dependencies.get_table_service
- app.domain.order.order_service.OrderService
- app.domain.order.dependencies.get_order_service
- app.models.user.User
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, Query

from app.schemas.table import (
    TableCreate,
    TableUpdate,
    TableList,
    TableOut,
    TablePositionUpdate
)

from app.schemas.order.order_item import AddItemRequest

from app.domain.table.table_service import TableService
from app.domain.table.dependencies import get_table_service

from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/")
def create_table(
    table_in: TableCreate,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.create_table(user.restaurant_id, table_in)


@router.post("/{table_id}/touch")
def touch_table(
    table_id: int,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.touch_table(user.restaurant_id, table_id)


@router.post("/{table_id}/add-product")
def add_product_to_table(
    table_id: int,
    payload: AddItemRequest,
    user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.add_product_to_table(
        restaurant_id=user.restaurant_id,
        table_id=table_id,
        product_id=payload.product_id,
        quantity=payload.quantity
    )


@router.get("/", response_model=list[TableList])
def list_tables(
    active: bool | None = Query(default=True),
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables(user.restaurant_id, active)


@router.get("/status", response_model=list[TableOut])
def list_tables_status(
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables_status(user.restaurant_id)


@router.patch("/{table_id}/position", status_code=204)
def update_position(
    table_id: int,
    data: TablePositionUpdate,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    service.update_position(user.restaurant_id, table_id, data)


@router.patch("/{table_id}/activate")
def activate_table(
    table_id: int,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.activate_table(user.restaurant_id, table_id)


@router.patch("/{table_id}", response_model=TableList)
def update_table(
    table_id: int,
    table_in: TableUpdate,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.update_table(user.restaurant_id, table_id, table_in)


@router.delete("/{table_id}")
def deactivate_table(
    table_id: int,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.deactivate_table(user.restaurant_id, table_id)
```

---

### .\backend\app\routers\users.py

**Funciones (4):**
- list_users
- create_user
- update_user
- toggle_user

**Clases (0):**

**Imports (11):**
- fastapi.APIRouter
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.dependencies.auth.get_current_user
- app.models.user.User
- app.schemas.user.UserCreate
- app.schemas.user.UserUpdate
- app.schemas.user.UserOut
- app.domain.user.user_service.UserService
- app.domain.user.dependencies.get_user_service

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut

from app.domain.user.user_service import UserService
from app.domain.user.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):

    return service.list_users(user.restaurant_id)


@router.post("/", response_model=UserOut)
def create_user(
    data: UserCreate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):

    return service.create_user(user.restaurant_id, data)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):

    return service.update_user(user_id, user.restaurant_id, data)


@router.patch("/{user_id}/toggle", response_model=UserOut)
def toggle_user(
    user_id: int,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):

    return service.toggle_user(user_id, user.restaurant_id)
```

---

### .\backend\app\schemas\auth.py

**Funciones (0):**

**Clases (2):**
- LoginRequest
- TokenResponse

**Imports (1):**
- pydantic.BaseModel

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

```

---

### .\backend\app\schemas\base.py

**Funciones (0):**

**Clases (3):**
- BaseSchema
- TimestampSchema
- Config

**Imports (2):**
- pydantic.BaseModel
- datetime.datetime

```python
from pydantic import BaseModel
from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # reemplaza orm_mode en Pydantic v2


class TimestampSchema(BaseSchema):
    created_at: datetime
```

---

### .\backend\app\schemas\cash_register.py

**Funciones (0):**

**Clases (8):**
- CashRegisterOpen
- CashRegisterOut
- CashRegisterSummary
- PaymentBreakdown
- CashRegisterCloseOut
- CashRegisterClose
- CashMovementCreate
- CashRegisterDashboard

**Imports (3):**
- datetime.datetime
- decimal.Decimal
- base.BaseSchema

```python
from datetime import datetime
from decimal import Decimal
from .base import BaseSchema


class CashRegisterOpen(BaseSchema):
    opening_amount: Decimal


class CashRegisterOut(BaseSchema):
    id: int
    restaurant_id: int
    opening_amount: Decimal
    closing_amount: Decimal | None
    opened_at: datetime
    closed_at: datetime | None
    is_open: bool
    opened_by_id: int
    closed_by_id: int | None

class CashRegisterSummary(BaseSchema):
    cash_register_id: int
    opened_at: datetime
    total_sales: Decimal
    orders_count: int
    average_ticket: Decimal
    by_method: dict[str, Decimal]

class PaymentBreakdown(BaseSchema):
    method: str
    total: Decimal


class CashRegisterCloseOut(BaseSchema):
    message: str
    total_sales: Decimal
    transactions_count: int
    by_method: list[PaymentBreakdown]
    opening_amount: Decimal
    expected_cash: Decimal
    counted_cash: Decimal
    difference: Decimal


class CashRegisterClose(BaseSchema):
    counted_cash: Decimal


class CashMovementCreate(BaseSchema):
    type: str
    amount: Decimal
    reason: str


class CashRegisterDashboard(BaseSchema):

    cash_register_id: int
    opened_at: datetime

    opening_amount: Decimal

    total_sales: Decimal
    orders_count: int
    average_ticket: Decimal

    by_method: dict[str, Decimal]

    cash_movements: list[dict]

    expected_cash: Decimal
```

---

### .\backend\app\schemas\category.py

**Funciones (0):**

**Clases (5):**
- CategoryBase
- CategoryCreate
- CategoryUpdate
- CategoryResponse
- CategoryWithProducts

**Imports (4):**
- typing.List
- base.BaseSchema
- product.ProductMenu
- decimal.Decimal

```python
from typing import List
from .base import BaseSchema
from .product import ProductMenu
from decimal import Decimal

class CategoryBase(BaseSchema):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: str


class CategoryResponse(CategoryBase):
    id: int


class CategoryWithProducts(CategoryResponse):
    products: List[ProductMenu] = []
```

---

### .\backend\app\schemas\layout.py

**Funciones (0):**

**Clases (2):**
- LayoutOut
- LayoutUpdate

**Imports (1):**
- base.BaseSchema

```python
from .base import BaseSchema

class LayoutOut(BaseSchema):
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool


class LayoutUpdate(BaseSchema):
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool
```

---

### .\backend\app\schemas\product.py

**Funciones (0):**

**Clases (4):**
- ProductCreate
- ProductUpdate
- ProductOut
- ProductMenu

**Imports (3):**
- decimal.Decimal
- typing.Optional
- base.BaseSchema

```python
from decimal import Decimal
from typing import Optional
from .base import BaseSchema


class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int


class ProductUpdate(BaseSchema):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    station_id: Optional[int] = None


class ProductOut(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int
    active: bool


class ProductMenu(BaseSchema):
    id: int
    name: str
    price: Decimal
```

---

### .\backend\app\schemas\station.py

**Funciones (0):**

**Clases (3):**
- StationCreate
- StationUpdate
- StationOut

**Imports (3):**
- decimal.Decimal
- typing.Optional
- base.BaseSchema

```python
from decimal import Decimal
from typing import Optional
from .base import BaseSchema

class StationCreate(BaseSchema):
    name: str

class StationUpdate(BaseSchema):
    name: str

class StationOut(BaseSchema):
    id: int
    name: str
    active: bool
```

---

### .\backend\app\schemas\table.py

**Funciones (0):**

**Clases (6):**
- TableStatus
- TableOut
- TableCreate
- TableUpdate
- TableList
- TablePositionUpdate

**Imports (4):**
- app.models.order.OrderStatus
- base.BaseSchema
- typing.Optional
- enum.Enum

```python
from app.models.order import OrderStatus
from .base import BaseSchema
from typing import Optional
from enum import Enum

class TableStatus(str, Enum):
    FREE = "libre"
    OCCUPIED = "ocupada"

class TableOut(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: str
    active: bool
    status: TableStatus
    order_id: int | None
    order_status: OrderStatus | None

class TableCreate(BaseSchema):
    x: int = 0
    y: int = 0
    capacity: int = 4
    shape: str = "Circular"

class TableUpdate(BaseSchema):
    number: Optional[int] = None
    capacity: Optional[int] = None
    shape: Optional[str] = None
    active: Optional[bool] = None


class TableList(BaseSchema):
    id: int
    number: int
    capacity: int
    shape: str
    active: bool

class TablePositionUpdate(BaseSchema):
    x: int
    y: int
```

---

### .\backend\app\schemas\user.py

**Funciones (0):**

**Clases (3):**
- UserCreate
- UserUpdate
- UserOut

**Imports (3):**
- typing.Optional
- base.BaseSchema
- app.models.user.UserRole

```python
from typing import Optional
from .base import BaseSchema
from app.models.user import UserRole


class UserCreate(BaseSchema):
    username: str
    password: str
    role: UserRole


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserOut(BaseSchema):
    id: int
    username: str
    role: UserRole
    active: bool
```

---

### .\backend\app\schemas\waiter.py

**Funciones (0):**

**Clases (1):**
- WaiterItemOut

**Imports (1):**
- pydantic.BaseModel

```python
# schemas/waiter.py

from pydantic import BaseModel

class WaiterItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    status: str

```

---

### .\backend\app\schemas\order\kitchen.py

**Funciones (0):**

**Clases (1):**
- KitchenItemOut

**Imports (2):**
- app.models.order_item.OrderItemStatus
- base.BaseSchema

```python
from app.models.order_item import OrderItemStatus
from ..base import BaseSchema

class KitchenItemOut(BaseSchema):
    item_id: int
    product_name: str
    quantity: int
    status: OrderItemStatus
    table_number: int
    order_id: int
```

---

### .\backend\app\schemas\order\order.py

**Funciones (0):**

**Clases (3):**
- OrderOut
- WaiterOrderOut
- OrderStatusUpdate

**Imports (5):**
- decimal.Decimal
- app.models.order.OrderStatus
- base.BaseSchema
- order_item.OrderItemOut
- payment.PaymentOut

```python
from decimal import Decimal
from app.models.order import OrderStatus
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderOut(BaseSchema):
    id: int
    table_number: int
    status: OrderStatus
    created_at: str
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    subtotal: float
    discount: float
    total: float
    total_paid: float
    remaining: float


class WaiterOrderOut(BaseSchema):
    id: int
    table_id: int
    table_number: int
    status: OrderStatus
    created_at: str
    items: list[OrderItemOut]
    subtotal: float
    discount: float
    total: float
    total_paid: float
    remaining: float


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus
```

---

### .\backend\app\schemas\order\order_item.py

**Funciones (0):**

**Clases (4):**
- OrderItemCreate
- OrderItemStatusUpdate
- OrderItemOut
- AddItemRequest

**Imports (2):**
- app.models.order_item.OrderItemStatus
- base.BaseSchema

```python
from app.models.order_item import OrderItemStatus
from ..base import BaseSchema

class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int


class OrderItemStatusUpdate(BaseSchema):
    status: OrderItemStatus


class OrderItemOut(BaseSchema):
    id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    status: OrderItemStatus

class AddItemRequest(BaseSchema):
    product_id: int
    quantity: int = 1
```

---

### .\backend\app\schemas\order\payment.py

**Funciones (0):**

**Clases (2):**
- PaymentCreate
- PaymentOut

**Imports (3):**
- decimal.Decimal
- app.models.payment.PaymentMethod
- base.BaseSchema

```python
from decimal import Decimal
from app.models.payment import PaymentMethod
from ..base import BaseSchema

class PaymentCreate(BaseSchema):
    method: PaymentMethod
    amount: Decimal


class PaymentOut(BaseSchema):
    id: int
    amount: Decimal
    method: PaymentMethod
```

---

### .\backend\app\services\event_service.py

**Funciones (8):**
- _log_task_error
- __init__
- emit_to_role
- emit_to_station
- broadcast
- _persist_event
- _dispatch
- _create_task

**Clases (1):**
- EventService

**Imports (10):**
- asyncio
- json
- logging
- uuid
- sqlalchemy.orm.Session
- app.websocket.manager.manager
- app.models.user.UserRole
- app.models.domain_event.DomainEvent
- app.db.session.SessionLocal
- app.core.redis.redis_client

```python
# backend/app/domain/event_service.py

import asyncio
import json
import logging
import uuid
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.models.user import UserRole
from app.models.domain_event import DomainEvent
from app.db.session import SessionLocal
from app.core.redis import redis_client

logger = logging.getLogger(__name__)
INSTANCE_ID = str(uuid.uuid4())

class EventService:

    # =========================
    # API PÚBLICA
    # =========================

    def __init__(self):
        self.loop = None


    def emit_to_role(self, restaurant_id: int, role: UserRole, message: dict):
        print("EVENT emit_to_role", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "role",
            "target_id": role.value if hasattr(role, "value") else role,
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.send_to_role, restaurant_id, role, message)

    def emit_to_station(self, restaurant_id: int, station_id: int, message: dict):
        print("EVENT emit_to_station", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "station",
            "target_id": station_id,
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.send_to_station, restaurant_id, station_id, message)

    def broadcast(self, restaurant_id: int, message: dict):
        print("EVENT broadcast", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "broadcast",
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.broadcast, restaurant_id, message)

    # =========================
    # PERSISTENCIA
    # =========================

    def _persist_event(self, restaurant_id: int, event: dict):
        db = SessionLocal()
        try:
            event = DomainEvent(
                restaurant_id=restaurant_id,
                event_type=event.get("type"),
                payload=event
            )
            db.add(event)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error("Error persistiendo evento: %s", e)
        finally:
            db.close()

    # =========================
    # DESPACHO
    # =========================

    def _dispatch(self, func, *args):
        """
        Agenda las coroutines en el loop de FastAPI.
        Guarda referencia a cada tarea para evitar garbage collection
        y registra errores en el callback.
        """
        logger.info("emit event type=%s", args[-1].get("type"))
        try:
            loop = self.loop
            if not loop:
                logger.error("Event loop not initialized")
                return
        except RuntimeError:
            # Nunca debería ocurrir en FastAPI, pero por seguridad:
            logger.error("_dispatch llamado fuera de un loop async. Evento descartado.")
            return

        event = args[-1]

        self._create_task(loop, func(*args))
        self._create_task(loop, self._publish_redis(event))


    def _create_task(self, loop: asyncio.AbstractEventLoop, coro):
        """
        Crea la tarea guardando referencia y registrando errores.
        """
        task = loop.create_task(coro)

        # Guardar referencia evita que el GC la elimine antes de completar
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        task.add_done_callback(_log_task_error)

    # =========================
    # REDIS
    # =========================

    async def _publish_redis(self, message: dict):
        try:
            await redis_client.publish(
                "restaurant_events",
                json.dumps(message)
            )
        except Exception as e:
            logger.error("Error publicando en Redis: %s", e)


# Set global para mantener referencias a tareas en vuelo
# Evita que el GC las elimine antes de que completen
_background_tasks: set[asyncio.Task] = set()


def _log_task_error(task: asyncio.Task):
    """Callback que registra excepciones de tareas background."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "Error en tarea background [%s]: %s",
            task.get_name(),
            exc,
            exc_info=exc
        )


event_service = EventService()
```

---

### .\backend\app\websocket\manager.py

**Funciones (2):**
- __init__
- disconnect

**Clases (1):**
- ConnectionManager

**Imports (3):**
- fastapi.WebSocket
- collections.defaultdict
- app.models.user.UserRole

```python
from fastapi import WebSocket
from collections import defaultdict
from app.models.user import UserRole


class ConnectionManager:

    def __init__(self):
        # restaurant_id -> list of connections
        self.connections = defaultdict(list)
        self._ws_index = {}

    async def connect(self, websocket, user, station_id=None):
        await websocket.accept()
        conn = {"ws": websocket, "user": user, "station_id": station_id}
        self.connections[user.restaurant_id].append(conn)
        self._ws_index[id(websocket)] = user.restaurant_id
        print(f"WS connected r={user.restaurant_id} role={user.role}")


    def disconnect(self, websocket):
        restaurant_id = self._ws_index.pop(id(websocket), None)
        if restaurant_id:
            self.connections[restaurant_id] = [
                c for c in self.connections[restaurant_id]
                if c["ws"] != websocket
            ]
        print("WS disconnected")

    # =========================
    # ENVÍOS
    # =========================

    async def send_to_role(self, restaurant_id: int, role: UserRole, message: dict):

        for c in self.connections[restaurant_id]:
            if c["user"].role == role:
                await self._safe_send(c["ws"], message)

    async def send_to_station(self, restaurant_id: int, station_id: int, message: dict):

        for c in self.connections[restaurant_id]:
            if c["station_id"] == station_id:
                await self._safe_send(c["ws"], message)

    async def broadcast(self, restaurant_id: int, message: dict):

        for c in self.connections[restaurant_id]:
            await self._safe_send(c["ws"], message)

    async def _safe_send(self, ws: WebSocket, message: dict):
        try:
            await ws.send_json(message)
        except Exception as e:
            print("WS send failed", e)


manager = ConnectionManager()
```

---

### .\backend\app\websocket\ws.py

**Funciones (1):**
- __init__

**Clases (1):**
- WSUser

**Imports (5):**
- fastapi.APIRouter
- fastapi.WebSocket
- fastapi.WebSocketDisconnect
- app.websocket.manager.manager
- app.core.security.decode_access_token

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.core.security import decode_access_token

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    payload = decode_access_token(token)

    if not payload:
        await websocket.close(code=1008)
        return

    # 🔥 ARMAR USER FAKE (simple y suficiente)
    class WSUser:
        def __init__(self, payload):
            self.id = payload.get("sub")
            self.role = payload.get("role")
            self.restaurant_id = payload.get("restaurant_id")

    user = WSUser(payload)

    station_id = websocket.query_params.get("station_id")

    await manager.connect(
        websocket,
        user,
        int(station_id) if station_id else None
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

### .\scripts\announce_service.py

**Funciones (4):**
- get_local_ip
- create_service
- main
- shutdown

**Clases (0):**

**Imports (6):**
- socket
- time
- signal
- sys
- zeroconf.Zeroconf
- zeroconf.ServiceInfo

```python
#!/usr/bin/env python3
"""
POS Zeroconf announcer
Anuncia los servicios del POS en la red local.

Servicios publicados:
- _pos._tcp.local  → descubrimiento del POS
- _http._tcp.local → acceso web
- _ws._tcp.local   → websocket
"""

import socket
import time
import signal
import sys
from zeroconf import Zeroconf, ServiceInfo


def get_local_ip():
    """Obtiene la IP local de la máquina"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def create_service(service_type, name, port, ip):
    return ServiceInfo(
        service_type,
        f"{name}.{service_type}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            "version": "1.0",
            "service": name
        },
        server="pos.local."
    )


def main():

    ip = get_local_ip()

    print("POS Zeroconf announcer")
    print("IP detectada:", ip)

    zeroconf = Zeroconf()

    services = [

        create_service(
            "_pos._tcp.local.",
            "restaurant-pos",
            80,
            ip
        ),

        create_service(
            "_http._tcp.local.",
            "restaurant-pos-web",
            80,
            ip
        ),

        create_service(
            "_ws._tcp.local.",
            "restaurant-pos-ws",
            8000,
            ip
        )

    ]

    for service in services:
        zeroconf.register_service(service)
        print("Servicio publicado:", service.name)

    print("\nPOS disponible en:")
    print(f"http://pos.local")
    print(f"http://{ip}")

    print("\nCtrl+C para detener")

    def shutdown(sig, frame):
        print("\nCerrando Zeroconf...")
        for service in services:
            zeroconf.unregister_service(service)
        zeroconf.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
```

---

