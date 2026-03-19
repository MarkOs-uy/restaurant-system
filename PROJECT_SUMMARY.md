# 📊 Project Summary
Generated: 2026-03-18 15:16:07.810475

## 📁 Estructura del proyecto

```
- ./
  - analyze_project.py
  - backend/
    - alembic/
      - env.py
      - versions/
        - 50f5f9de1220_add_table_shape.py
        - 530c9b9f2a9f_initial_schema.py
        - 9607a137eec7_add_password_to_user.py
        - b30663f913d9_add_cash_register_audit_fields.py
        - fa7705341950_add_table_coordinates.py
    - app/
      - main.py
      - seed.py
      - seed_products.py
      - seed_restaurant.py
      - seed_stations.py
      - seed_users.py
      - core/
        - dependencies.py
        - security.py
      - db/
        - base.py
        - base_class.py
        - session.py
        - tenant.py
      - dependencies/
        - auth.py
      - domain/
        - order_item_service.py
        - order_item_transitions.py
        - order_service.py
        - order_transitions.py
      - models/
        - cash_register.py
        - category.py
        - order.py
        - order_item.py
        - payment.py
        - product.py
        - production_station.py
        - restaurant.py
        - table.py
        - user.py
        - __init__.py
      - routers/
        - auth.py
        - cash_register.py
        - category.py
        - kitchen.py
        - orders.py
        - order_items.py
        - products.py
        - stations.py
        - tables.py
        - users.py
        - ws_kitchen.py
        - ws_waiter.py
      - schemas/
        - auth.py
        - base.py
        - cash_register.py
        - category.py
        - product.py
        - table.py
        - user.py
        - waiter.py
        - order/
          - kitchen.py
          - order.py
          - order_item.py
          - payment.py
      - websocket/
        - manager.py
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

print("MODELOS REGISTRADOS:")
print(Base.metadata.tables.keys())

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
    op.drop_column('tables', 'shape')
    op.drop_column('tables', 'capacity')
    op.drop_column('tables', 'y')
    op.drop_column('tables', 'x')
    # ### end Alembic commands ###

```

---

### .\backend\app\main.py

**Funciones (1):**
- root

**Clases (0):**

**Imports (22):**
- fastapi.FastAPI
- fastapi.Depends
- sqlalchemy.orm.Session
- sqlalchemy.text
- app.db.base.Base
- app.db.session.engine
- contextlib.asynccontextmanager
- app.db.session.SessionLocal
- app.seed.seed_tables
- app.models
- app.routers.tables
- app.routers.orders
- app.routers.products
- app.routers.cash_register
- app.routers.category
- app.routers.order_items
- app.routers.stations
- app.routers.auth
- app.routers.users
- app.routers.ws_kitchen
- app.routers.kitchen.router
- fastapi.middleware.cors.CORSMiddleware

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine

from contextlib import asynccontextmanager
from app.db.session import SessionLocal
from app.seed import seed_tables

from app import models

from app.routers import tables, orders, products, cash_register, category, order_items, stations, auth, users, ws_kitchen
from app.routers.kitchen import router as kitchen_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Backend arrancando...")
    yield
    print("Backend apagándose...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # luego lo restringimos
    #allow_origins=["http://localhost:5173","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen_router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws_kitchen.router)
@app.get("/")
def root():
    return {"status": "running"}

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
        seed_tables(db)
        seed_stations(db)
        seed_products(db)
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

    restaurant = Restaurant(
        name="Sistema Demo"
    )

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

    print("Creando usuarios iniciales...")

    pass_hash = get_password_hash("1234")

    users = [
        User(name="admin", role="ADMIN", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="waiter", role="WAITER", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="kitchen", role="KITCHEN", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="cashier", role="CASHIER", password_hash = pass_hash, restaurant_id=restaurant.id),
    ]

    db.add_all(users)
    db.commit()

    print("Estaciones creadas.")

```

---

### .\backend\app\core\dependencies.py

**Funciones (1):**
- get_current_restaurant

**Clases (0):**

**Imports (6):**
- fastapi.Depends
- fastapi.HTTPException
- fastapi.Header
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.restaurant.Restaurant

```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.restaurant import Restaurant


def get_current_restaurant(
    x_restaurant_id: int = Header(None),
    db: Session = Depends(get_db)
):
    """
    Temporal: identifica restaurante por header.
    En producción esto vendrá del JWT.
    """

    if not x_restaurant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Restaurant-Id header required"
        )

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == x_restaurant_id,
        Restaurant.active == True
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return restaurant

```

---

### .\backend\app\core\security.py

**Funciones (4):**
- get_password_hash
- verify_password
- create_access_token
- decode_access_token

**Clases (0):**

**Imports (5):**
- datetime.datetime
- datetime.timedelta
- jose.JWTError
- jose.jwt
- passlib.context.CryptContext

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔐 Hash password
def get_password_hash(password: str):
    return pwd_context.hash(password)


# 🔎 Verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# 🎟 Create JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔓 Decode JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

```

---

### .\backend\app\db\base.py

**Funciones (0):**

**Clases (0):**

**Imports (8):**
- app.db.base_class.Base
- app.models.table.Table
- app.models.restaurant.Restaurant
- app.models.product.Product
- app.models.payment.Payment
- app.models.order.Order
- app.models.order_item.OrderItem
- app.models.cash_register.CashRegister

```python
from app.db.base_class import Base

from app.models.table import Table
from app.models.restaurant import Restaurant
from app.models.product import Product
from app.models.payment import Payment
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cash_register import CashRegister



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
        raise HTTPException(401, "Invalid token")

    user_id = payload.get("sub")

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(401, "User not found")

    return user

```

---

### .\backend\app\domain\order_item_service.py

**Funciones (1):**
- change_item_status

**Clases (1):**
- OrderItemDomainError

**Imports (6):**
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.user.User
- app.models.user.UserRole
- app.models.order.OrderStatus
- app.domain.order_item_transitions.can_transition

```python
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus
from app.domain.order_item_transitions import can_transition


class OrderItemDomainError(Exception):
    pass


def change_item_status(item: OrderItem, new_status: OrderItemStatus, user: User):

    if item.order.status == OrderStatus.CLOSED:
        raise OrderItemDomainError("Cannot modify items of closed order")

    # 🔐 reglas por rol
    if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Only kitchen can start items")

    if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Only kitchen can mark ready")

    if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
        raise OrderItemDomainError("Only waiter can deliver")

    if not can_transition(item.status, new_status):
        raise OrderItemDomainError(
            f"Invalid transition from {item.status.value} to {new_status.value}"
        )

    item.status = new_status
```

---

### .\backend\app\domain\order_item_transitions.py

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

### .\backend\app\domain\order_service.py

**Funciones (9):**
- __init__
- calculate_totals
- send_to_kitchen
- close_order
- add_payment
- get_active_orders
- get_order
- update_status
- add_item

**Clases (2):**
- OrderDomainError
- OrderService

**Imports (10):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- sqlalchemy.func
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItemStatus
- app.models.payment.Payment
- app.models.user.User
- app.models.order_item.OrderItem
- app.domain.order_transitions.is_valid_order_transition

```python
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItemStatus
from app.models.payment import Payment
from app.models.user import User
from app.models.order_item import OrderItem


from app.domain.order_transitions import is_valid_order_transition


class OrderDomainError(Exception):
    pass


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Cálculos
    # -------------------------

    def calculate_totals(self, order: Order):
        total = sum(
            item.quantity * item.unit_price
            for item in order.items
        )

        total_paid = sum(
            payment.amount
            for payment in order.payments
        )

        remaining = total - total_paid

        return (
            float(total),
            float(total_paid),
            float(remaining)
        )
    
    # -------------------------
    # Enviar a cocina
    # -------------------------

    def send_to_kitchen(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order is closed")

        pending_items = [
            item for item in order.items
            if item.status == OrderItemStatus.PENDING
        ]

        if not pending_items:
            raise OrderDomainError("No pending items to send")

        for item in pending_items:
            item.status = OrderItemStatus.SENT

        if order.status == OrderStatus.OPEN:
            order.status = OrderStatus.SENT

        return pending_items

    # -------------------------
    # Cerrar orden
    # -------------------------

    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        total, total_paid, remaining = self.calculate_totals(order)

        if remaining > 0:
            raise OrderDomainError(
                f"Order not fully paid. Remaining: {remaining}"
            )

        not_delivered = [
            item for item in order.items
            if item.status != OrderItemStatus.DELIVERED
        ]

        if not_delivered:
            raise OrderDomainError(
                "All items must be DELIVERED before closing order"
            )

        order.status = OrderStatus.CLOSED
        order.closed_at = func.now()

    # -------------------------
    # Registrar pago
    # -------------------------

    def add_payment(self, order: Order, amount, method, cash_register):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        total, total_paid, remaining = self.calculate_totals(order)

        if amount > remaining:
            raise OrderDomainError(
                "Payment exceeds remaining balance"
            )

        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=amount,
            method=method,
            cash_register_id=cash_register.id
        )

        self.db.add(payment)


    def get_active_orders(self, restaurant_id: int):
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status != OrderStatus.CLOSED
            )
            .all()
        )


    def get_order(self, order_id: int, restaurant_id: int):

        order = (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )

        if not order:
            raise OrderDomainError("Order not found")

        return order


    def update_status(self, order: Order, new_status: OrderStatus):

        if not is_valid_order_transition(order.status, new_status):
            raise OrderDomainError("Invalid status transition")

        order.status = new_status


    def add_item(self, order, product, quantity: int):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Cannot add items to a closed order")

        if quantity <= 0:
            raise OrderDomainError("Quantity must be greater than zero")

        existing_item = self.db.query(OrderItem).filter(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product.id,
            OrderItem.status == OrderItemStatus.PENDING
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            return existing_item

        new_item = OrderItem(
            restaurant_id=order.restaurant_id,
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
            status=OrderItemStatus.PENDING
        )

        self.db.add(new_item)
        return new_item
```

---

### .\backend\app\domain\order_transitions.py

**Funciones (1):**
- is_valid_order_transition

**Clases (0):**

**Imports (1):**
- app.models.order.OrderStatus

```python
# app/domain/order_transitions.py

from app.models.order import OrderStatus

ORDER_ALLOWED_TRANSITIONS = {
    OrderStatus.OPEN: [
        OrderStatus.SENT,
        OrderStatus.CANCELLED
    ],
    OrderStatus.SENT: [
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED
    ],
    OrderStatus.IN_PROGRESS: [
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.READY: [
        OrderStatus.CLOSED
    ],
    OrderStatus.CLOSED: [],
    OrderStatus.CANCELLED: []
}


def is_valid_order_transition(
    current_status: OrderStatus,
    new_status: OrderStatus
) -> bool:
    """
    Valida si una transición de estado de orden es permitida.
    """

    allowed = ORDER_ALLOWED_TRANSITIONS.get(current_status, [])

    return new_status in allowed
```

---

### .\backend\app\models\cash_register.py

**Funciones (0):**

**Clases (1):**
- CashRegister

**Imports (9):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.DateTime
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Boolean
- sqlalchemy.sql.func
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True)
    
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    is_open = Column(Boolean, default=True, nullable=False)
    opened_by_id = Column(Integer, ForeignKey("users.id"))
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    opening_amount = Column(Numeric(10,2), nullable=False)
    closing_amount = Column(Numeric(10,2), nullable=True)

    restaurant = relationship("Restaurant", back_populates="cash_registers")
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

### .\backend\app\models\order.py

**Funciones (0):**

**Clases (2):**
- OrderStatus
- Order

**Imports (12):**
- enum
- uuid
- sqlalchemy.Column
- sqlalchemy.Integer
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
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum, Index
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class OrderStatus(str, enum.Enum):
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

    shape = Column(String, default="round")

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

**Imports (10):**
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
- app.core.security.create_access_token
- app.dependencies.auth.get_current_user
- app.schemas.user.UserOut
- passlib.context.CryptContext

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user

from app.schemas.user import UserOut

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not pwd_context.verify(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
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

**Funciones (3):**
- open_cash_register
- close_cash_register
- current_cash_register

**Clases (0):**

**Imports (15):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- sqlalchemy.func
- decimal.Decimal
- app.models.payment.Payment
- app.models.cash_register.CashRegister
- app.models.user.User
- app.db.session.get_db
- app.dependencies.auth.get_current_user
- app.schemas.cash_register.CashRegisterOpen
- app.schemas.cash_register.CashRegisterOut
- app.schemas.cash_register.CashRegisterSummary
- app.schemas.cash_register.CashRegisterCloseOut

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.models.payment import Payment
from app.models.cash_register import CashRegister
from app.models.user import User

from app.db.session import get_db

from app.dependencies.auth import get_current_user

from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterOut,
    CashRegisterSummary,
    CashRegisterCloseOut
)

router = APIRouter(
    prefix="/cash-register",
    tags=["cash-register"]
)

@router.post("/open", response_model=CashRegisterOut)
def open_cash_register(
    data: CashRegisterOpen,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing = db.query(CashRegister).filter(
        CashRegister.is_open == True,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if existing:
        raise HTTPException(400, "Ya hay una caja abierta")

    register = CashRegister(
        restaurant_id=user.restaurant_id,
        opening_amount=data.opening_amount,
        opened_by_id=user.id,
        is_open=True
    )

    db.add(register)
    db.commit()
    db.refresh(register)

    return register


@router.post("/close", response_model=CashRegisterCloseOut)
def close_cash_register(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cash_register = db.query(CashRegister).filter(
        CashRegister.is_open == True,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    total = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    cash_register.closing_amount = total
    cash_register.closed_at = func.now()
    cash_register.is_open = False
    cash_register.closed_by_id = user.id

    db.commit()

    return {
        "message": "Caja cerrada",
        "total_vendido": float(total)
    }


@router.get("/current", response_model=CashRegisterSummary | None)
def current_cash_register(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cash_register = db.query(CashRegister).filter(
        CashRegister.is_open == True,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if not cash_register:
        return None
    
    total_sales = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    orders_count = db.query(func.count(Payment.id)).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    average_ticket = (
        total_sales / orders_count
        if orders_count
        else Decimal("0")
    )

    rows = db.query(
        Payment.method,
        func.sum(Payment.amount)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).group_by(
        Payment.method
    ).all()

    by_method = {
        method.value: amount
        for method, amount in rows
    }

    return {
        "cash_register_id": cash_register.id,
        "opened_at": cash_register.opened_at,
        "total_sales": float(total_sales),
        "orders_count": orders_count,
        "average_ticket": float(average_ticket),
        "by_method": {
            method.value: float(amount)
            for method, amount in rows
        }
    }
```

---

### .\backend\app\routers\category.py

**Funciones (5):**
- list_categories
- create_category
- update_category
- delete_category
- list_categories_with_products

**Clases (0):**

**Imports (11):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.db.session.get_db
- app.models.category.Category
- app.models.product.Product
- app.models.restaurant.Restaurant
- app.models.user.User
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.restaurant import Restaurant
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/")
def list_categories(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Category).filter(
        Category.restaurant_id == user.restaurant_id
    ).order_by(Category.name).all()


@router.post("/")
def create_category(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = Category(
        name=data["name"],
        restaurant_id=user.restaurant_id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.patch("/{category_id}")
def update_category(
    category_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.restaurant_id == user.restaurant_id
    ).first()

    if not category:
        raise HTTPException(404, "Category not found")

    category.name = data["name"]

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.restaurant_id == user.restaurant_id
    ).first()

    if not category:
        raise HTTPException(404, "Category not found")

    db.delete(category)
    db.commit()

    return {"ok": True}

@router.get("/with-products")
def list_categories_with_products(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = (
        db.query(Category)
        .options(joinedload(Category.products))
        .filter(Category.restaurant_id == user.restaurant_id)
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
            if p.active and p.restaurant_id == user.restaurant_id
        ]

        result.append({
            "id": category.id,
            "name": category.name,
            "products": active_products
        })

    return result

```

---

### .\backend\app\routers\kitchen.py

**Funciones (2):**
- get_station_items
- update_item_status

**Clases (0):**

**Imports (16):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.user.User
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.order.Order
- app.dependencies.auth.get_current_user
- app.schemas.order.order_item.OrderItemStatusUpdate
- app.schemas.order.order_item.OrderItemOut
- app.schemas.order.kitchen.KitchenItemOut
- app.domain.order_item_service.change_item_status
- app.domain.order_item_service.OrderItemDomainError

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order
from app.dependencies.auth import get_current_user

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemOut
)
from app.schemas.order.kitchen import KitchenItemOut

from app.domain.order_item_service import (
    change_item_status,
    OrderItemDomainError
)

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

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


@router.patch("/{item_id}/status", response_model=OrderItemOut)
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    try:
        change_item_status(item, data.status, user)
    except OrderItemDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()
    db.refresh(item)

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

### .\backend\app\routers\orders.py

**Funciones (8):**
- add_item_to_order
- add_payment
- close_order
- delete_order_item
- get_active_orders
- get_order
- update_order_status
- update_item_quantity

**Clases (0):**

**Imports (22):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- collections.defaultdict
- app.db.session.get_db
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.product.Product
- app.models.user.User
- app.models.cash_register.CashRegister
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.dependencies.auth.get_current_user
- app.schemas.order.order.OrderOut
- app.schemas.order.order_item.OrderItemCreate
- app.schemas.order.payment.PaymentCreate
- app.schemas.order.order.WaiterOrderOut
- app.schemas.order.order.OrderStatusUpdate
- app.websocket.manager.manager
- app.domain.order_service.OrderService
- app.domain.order_service.OrderDomainError

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.models.cash_register import CashRegister
from app.models.order_item import OrderItem, OrderItemStatus
from app.dependencies.auth import get_current_user

from app.schemas.order.order import OrderOut
from app.schemas.order.order_item import OrderItemCreate
from app.schemas.order.payment import PaymentCreate
from app.schemas.order.order import WaiterOrderOut
from app.schemas.order.order import OrderStatusUpdate

from app.websocket.manager import manager

from app.domain.order_service import (
    OrderService,
    OrderDomainError
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/{order_id}/items")
def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == user.restaurant_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.restaurant_id == user.restaurant_id,
        Product.active == True
    ).first()

    if not product:
        raise HTTPException(404, "Producto no disponible")

    service = OrderService(db)
    print(dir(service))
    try:
        new_item = service.add_item(order, product, item.quantity)
        db.commit()
        db.refresh(new_item)
        return new_item
    except OrderDomainError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))

@router.post("/{order_id}/send-to-kitchen")
async def send_to_kitchen(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == user.restaurant_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    service = OrderService(db)

    try:
        sent_items = service.send_to_kitchen(order)
    except OrderDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()

    # agrupar items por estación
    stations = defaultdict(list)

    for item in sent_items:
        stations[item.product.station_id].append(item)

    # enviar evento websocket por estación
    for station_id, items in stations.items():

        try:
            await manager.send_to_station(
                restaurant_id=user.restaurant_id,
                station_id=station_id,
                message={
                    "type": "NEW_ITEMS",
                    "order_id": order.id,
                    "table": order.table.number,
                    "items": [
                        {
                            "product": i.product.name,
                            "quantity": i.quantity,
                            "item_id": i.id
                        }
                        for i in items
                    ]
                }
            )

        except Exception as e:
            print("WebSocket error:", e)

    return {"message": "Items enviados"}

@router.post("/{order_id}/payments")
def add_payment(
    order_id: int,
    payment: PaymentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == user.restaurant_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    cash_register = db.query(CashRegister).filter(
        CashRegister.restaurant_id == user.restaurant_id,
        CashRegister.closed_at == None
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    service = OrderService(db)

    try:
        service.add_payment(
            order,
            payment.amount,
            payment.method,
            cash_register
        )
    except OrderDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()

    return {"message": "Pago registrado"}

@router.post("/{order_id}/close")
def close_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == user.restaurant_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    service = OrderService(db)

    try:
        service.close_order(order)
    except OrderDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "status": order.status
    }

@router.delete("/order-items/{item_id}")
def delete_order_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    print("ITEM ID:", item_id)
    print("USER RESTAURANT:", user.restaurant_id)

    item = db.query(OrderItem).filter(
        OrderItem.id == item_id
    ).first()

    print("ITEM FOUND:", item)

    if item:
        print("ITEM RESTAURANT:", item.restaurant_id)

    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    if item.status != OrderItemStatus.PENDING:
        raise HTTPException(400, "Item already sent to kitchen")

    db.delete(item)
    db.commit()

    return {"message": "Item eliminado"}


@router.get("/active", response_model=list[WaiterOrderOut])
def get_active_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = OrderService(db)
    orders = service.get_active_orders(user.restaurant_id)

    result = []

    for order in orders:
        total, total_paid, remaining = service.calculate_totals(order)

        result.append({
            "id": order.id,
            "table_id": order.table_id,
            "table_number": order.table.number,
            "status": order.status,
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
            "total_paid": total_paid,
            "remaining": remaining
        })

    return result


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = OrderService(db)

    try:
        order = service.get_order(order_id, user.restaurant_id)
    except OrderDomainError as e:
        raise HTTPException(404, str(e))

    total, total_paid, remaining = service.calculate_totals(order)

    return {
        "id": order.id,
        "table_id": order.table_id,
        "table_number": order.table.number,
        "status": order.status,
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
        "payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "method": p.method
            }
            for p in order.payments
        ],
        "total": total,
        "total_paid": total_paid,
        "remaining": remaining
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == user.restaurant_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    service = OrderService(db)

    try:
        service.update_status(order, data.status)
    except OrderDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "new_status": order.status
    }

@router.patch("/order-items/{item_id}")
def update_item_quantity(
    item_id: int,
    quantity: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    if item.status != OrderItemStatus.PENDING:
        raise HTTPException(400, "Item already sent to kitchen")

    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity

    db.commit()

    return {"ok": True}
```

---

### .\backend\app\routers\order_items.py

**Funciones (0):**

**Clases (0):**

**Imports (12):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.user.User
- app.models.user.UserRole
- app.schemas.order.order_item.OrderItemStatusUpdate
- app.dependencies.auth.get_current_user
- app.websocket.manager.manager

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.schemas.order.order_item import OrderItemStatusUpdate
from app.dependencies.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter(prefix="/order-items", tags=["order-items"])

ALLOWED_ITEM_TRANSITIONS = {
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


@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    # 🔐 CONTROL POR ROL

    if data.status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
        raise HTTPException(403, "Only kitchen can start items")

    if data.status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
        raise HTTPException(403, "Only kitchen can mark ready")

    if data.status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
        raise HTTPException(403, "Only waiter can deliver")


    if data.status not in ALLOWED_ITEM_TRANSITIONS[item.status]:
        raise HTTPException(
            400,
            f"Invalid transition from {item.status} to {data.status}"
        )

    item.status = data.status
    db.commit()
    db.refresh(item)

        # avisar a mozos si el item está listo
    if item.status == OrderItemStatus.READY:

        await manager.send_to_waiters(
            restaurant_id=user.restaurant_id,
            message={
                "type": "ITEM_READY",
                "table": item.order.table.number,
                "product": item.product.name,
                "quantity": item.quantity,
                "order_id": item.order.id,
                "item_id": item.id
            }
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

**Imports (11):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.db.session.get_db
- app.models.product.Product
- app.models.restaurant.Restaurant
- app.models.user.User
- app.schemas.product.ProductCreate
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.product import Product
from app.models.restaurant import Restaurant
from app.models.user import User

from app.schemas.product import ProductCreate

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
def create_product(
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        price=product.price,
        restaurant_id=user.restaurant_id,
        category_id=product.category_id,
        station_id=product.station_id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@router.get("/")
def list_products(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.station)
    ).filter(
        Product.restaurant_id == user.restaurant_id
    ).all()

@router.patch("/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.restaurant_id == user.restaurant_id
    ).first()

    if not db_product:
        raise HTTPException(404, "Product not found")

    db_product.name = product.name
    db_product.price = product.price
    db_product.category_id = product.category_id
    db_product.station_id = product.station_id

    db.commit()
    db.refresh(db_product)

    return db_product

@router.patch("/{product_id}/toggle")
def toggle_product(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.restaurant_id == user.restaurant_id
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    product.active = not product.active

    db.commit()
    db.refresh(product)

    return product
```

---

### .\backend\app\routers\stations.py

**Funciones (6):**
- list_stations
- create_station
- update_station
- toggle_station
- get_station_items
- list_active_stations

**Clases (0):**

**Imports (13):**
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


from app.schemas.order.kitchen import KitchenItemOut

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/")
def list_stations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(ProductionStation).filter(
        ProductionStation.restaurant_id == user.restaurant_id
    ).order_by(ProductionStation.name).all()


@router.post("/")
def create_station(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = ProductionStation(
        name=data["name"],
        restaurant_id=user.restaurant_id,
        active=True
    )

    db.add(station)
    db.commit()
    db.refresh(station)

    return station


@router.patch("/{station_id}")
def update_station(
    station_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = db.query(ProductionStation).filter(
        ProductionStation.id == station_id,
        ProductionStation.restaurant_id == user.restaurant_id
    ).first()

    if not station:
        raise HTTPException(404, "Station not found")

    station.name = data["name"]

    db.commit()
    db.refresh(station)

    return station


@router.patch("/{station_id}/toggle")
def toggle_station(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = db.query(ProductionStation).filter(
        ProductionStation.id == station_id,
        ProductionStation.restaurant_id == user.restaurant_id
    ).first()

    if not station:
        raise HTTPException(404, "Station not found")

    station.active = not station.active

    db.commit()
    db.refresh(station)

    return station

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

@router.get("/active")
def list_active_stations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    stations = db.query(ProductionStation).filter(
        ProductionStation.restaurant_id == user.restaurant_id,
        ProductionStation.active == True
    ).order_by(ProductionStation.name).all()

    return stations
```

---

### .\backend\app\routers\tables.py

**Funciones (7):**
- touch_table
- add_product_to_table
- list_tables
- create_table
- update_table
- update_table_position
- delete_table

**Clases (0):**

**Imports (16):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.db.session.get_db
- app.models.Table
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.product.Product
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.schemas.table.TableCreate
- app.schemas.order.order_item.AddItemRequest
- app.models.user.User
- app.dependencies.auth.get_current_user

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Table
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.order_item import OrderItem, OrderItemStatus

from app.schemas.table import TableCreate
from app.schemas.order.order_item import AddItemRequest

from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/tables", tags=["tables"])

'''
@router.post("/{table_id}/touch")
def touch_table(
    table_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id,
        Table.active == True
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # 🔴 MODIFICADO → ahora también excluye CANCELLED
    order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.restaurant_id == user.restaurant_id,
        Order.status.notin_([
            OrderStatus.CLOSED,
            OrderStatus.CANCELLED
        ])
    ).first()

    # si no existe → crearlo
    if not order:
        order = Order(
            table_id=table_id,
            restaurant_id=table.restaurant_id,
            status=OrderStatus.OPEN  # 🟢 AGREGADO explícito
        )
        db.add(order)
        db.commit()
        db.refresh(order)

    return {
        "order_id": order.id,
        "table_number": table.number,
        "status": order.status
    }
'''
@router.post("/{table_id}/touch")
def touch_table(
    table_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id,
        Table.active == True
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.restaurant_id == user.restaurant_id,
        Order.status.notin_([
            OrderStatus.CLOSED,
            OrderStatus.CANCELLED
        ])
    ).first()

    return {
        "table_id": table_id,
        "table_number": table.number,
        "order_id": order.id if order else None
    }

@router.post("/{table_id}/add-product")
def add_product_to_table(
    table_id: int,
    payload: AddItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id
    ).first()

    if not table:
        raise HTTPException(404, "Table not found")

    order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.restaurant_id == user.restaurant_id,
        Order.status.notin_([
            OrderStatus.CLOSED,
            OrderStatus.CANCELLED
        ])
    ).first()

    if not order:
        order = Order(
            table_id=table_id,
            restaurant_id=user.restaurant_id,
            status=OrderStatus.OPEN
        )
        db.add(order)
        db.flush()

    product = db.query(Product).filter(
        Product.id == payload.product_id,
        Product.restaurant_id == user.restaurant_id
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    item = OrderItem(
        restaurant_id=user.restaurant_id,
        order_id=order.id,
        product_id=product.id,
        quantity=payload.quantity,
        unit_price=product.price,
        status=OrderItemStatus.PENDING
    )

    db.add(item)
    db.commit()

    return {"order_id": order.id}

# 🔥 ESTE ES EL ENDPOINT IMPORTANTE
@router.get("/")
def list_tables(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    tables = (
        db.query(Table)
        .options(joinedload(Table.orders))
        .filter(
            Table.active == True,
            Table.restaurant_id == user.restaurant_id
        )
        .order_by(Table.number)
        .all()
    )
    result = []

    for table in tables:

        # buscar orden activa
        active_order = next(
            (
                order for order in table.orders
                if order.status not in [
                    OrderStatus.CLOSED,
                    OrderStatus.CANCELLED
                ]
            ),
            None
        )

        if active_order:
            result.append({
                "id": table.id,
                "number": table.number,
                "x": table.x,
                "y": table.y,
                "shape": table.shape,
                "status": "ocupada",
                "order_id": active_order.id,
                "order_status": active_order.status.value
            })
        else:
            result.append({
                "id": table.id,
                "number": table.number,
                "x": table.x,
                "y": table.y,
                "shape": table.shape,
                "status": "libre",
                "order_id": None,
                "order_status": None
            })

    return result

@router.post("/")
def create_table(
    table_in: TableCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    table = Table(
        restaurant_id=user.restaurant_id,
        number=table_in.number,
        x=table_in.x,
        y=table_in.y,
        capacity=table_in.capacity,
        shape=table_in.shape
    )

    db.add(table)
    db.commit()
    db.refresh(table)

    return table

@router.patch("/{table_id}")
def update_table(
    table_id: int,
    table_in: TableCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.number = table_in.number
    table.capacity = table_in.capacity
    table.shape = table_in.shape

    db.commit()

    return {"success": True}

@router.patch("/{table_id}/position")
def update_table_position(
    table_id: int,
    x: int,
    y: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.x = x
    table.y = y

    db.commit()

    return {"success": True}

@router.delete("/{table_id}")
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.restaurant_id == user.restaurant_id
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table.active = False

    db.commit()

    return {"success": True}
```

---

### .\backend\app\routers\users.py

**Funciones (4):**
- list_users
- create_user
- update_user
- toggle_user

**Clases (0):**

**Imports (9):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- sqlalchemy.orm.Session
- passlib.context.CryptContext
- app.db.session.get_db
- app.models.user.User
- app.dependencies.auth.get_current_user
- app.schemas.user.UserOut

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_model=list[UserOut])
def list_users(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(User).filter(
        User.restaurant_id == user.restaurant_id
    ).all()


@router.post("/")
def create_user(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    hashed = pwd_context.hash(data["password"])

    new_user = User(
        username=data["username"],
        password_hash=hashed,
        role=data["role"],
        restaurant_id=user.restaurant_id,
        active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    target = db.query(User).filter(
        User.id == user_id,
        User.restaurant_id == user.restaurant_id
    ).first()

    if not target:
        raise HTTPException(404, "User not found")

    target.username = data["username"]
    target.role = data["role"]

    if data.get("password"):
        target.password_hash = pwd_context.hash(data["password"])

    db.commit()
    db.refresh(target)

    return target


@router.patch("/{user_id}/toggle")
def toggle_user(
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    target = db.query(User).filter(
        User.id == user_id,
        User.restaurant_id == user.restaurant_id
    ).first()

    if not target:
        raise HTTPException(404, "User not found")

    target.active = not target.active

    db.commit()
    db.refresh(target)

    return target
```

---

### .\backend\app\routers\ws_kitchen.py

**Funciones (0):**

**Clases (0):**

**Imports (4):**
- fastapi.APIRouter
- fastapi.WebSocket
- fastapi.WebSocketDisconnect
- app.websocket.manager.manager

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/kitchen/{restaurant_id}/{station_id}")
async def kitchen_ws(websocket: WebSocket, restaurant_id: int, station_id: int):

    await manager.connect(websocket, restaurant_id, station_id)

    try:
        while True:

            message = await websocket.receive()

            # si el cliente se desconecta
            if message["type"] == "websocket.disconnect":
                break

            # si llega texto (no lo usamos, pero lo aceptamos)
            if message["type"] == "websocket.receive":
                pass

    except WebSocketDisconnect:
        pass

    finally:

        manager.disconnect(websocket, restaurant_id, station_id)

        print(
            "Kitchen clients:",
            len(manager.connections[restaurant_id][station_id])
        )
```

---

### .\backend\app\routers\ws_waiter.py

**Funciones (0):**

**Clases (0):**

**Imports (4):**
- fastapi.APIRouter
- fastapi.WebSocket
- fastapi.WebSocketDisconnect
- app.websocket.manager.manager

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/waiter/{restaurant_id}")
async def waiter_ws(websocket: WebSocket, restaurant_id: int):

    await manager.connect_waiter(websocket, restaurant_id)

    try:
        while True:
            await websocket.receive()

    except WebSocketDisconnect:
        manager.disconnect_waiter(websocket, restaurant_id)
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
    updated_at: datetime
```

---

### .\backend\app\schemas\cash_register.py

**Funciones (0):**

**Clases (4):**
- CashRegisterOpen
- CashRegisterOut
- CashRegisterSummary
- CashRegisterCloseOut

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
    total_sales: float
    orders_count: int
    average_ticket: float
    by_method: dict[str, float]

class CashRegisterCloseOut(BaseSchema):
    message: str
    total_vendido: Decimal
```

---

### .\backend\app\schemas\category.py

**Funciones (0):**

**Clases (1):**
- CategoryOut

**Imports (3):**
- typing.List
- base.BaseSchema
- product.ProductOut

```python
from typing import List
from .base import BaseSchema
from .product import ProductOut

class CategoryOut(BaseSchema):
    id: int
    name: str
    products: list[ProductOut]
```

---

### .\backend\app\schemas\product.py

**Funciones (0):**

**Clases (2):**
- ProductCreate
- ProductOut

**Imports (2):**
- decimal.Decimal
- base.BaseSchema

```python
from decimal import Decimal
from .base import BaseSchema

class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int


class ProductOut(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int

```

---

### .\backend\app\schemas\table.py

**Funciones (0):**

**Clases (2):**
- TableOut
- TableCreate

**Imports (2):**
- app.models.order.OrderStatus
- base.BaseSchema

```python
from app.models.order import OrderStatus
from .base import BaseSchema

class TableOut(BaseSchema):
    id: int
    number: int

    x: int
    y: int
    shape: str

    status: str
    order_id: int | None
    order_status: OrderStatus | None

class TableCreate(BaseSchema):
    number: int
    x: int = 0
    y: int = 0
    capacity: int = 4
    shape: str = "round"
```

---

### .\backend\app\schemas\user.py

**Funciones (0):**

**Clases (1):**
- UserOut

**Imports (2):**
- base.BaseSchema
- app.models.user.UserRole

```python
from .base import BaseSchema
from app.models.user import UserRole

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

**Imports (3):**
- pydantic.BaseModel
- typing.List
- decimal.Decimal

```python
# schemas/waiter.py

from pydantic import BaseModel
from typing import List
from decimal import Decimal

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
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    total: float
    total_paid: float
    remaining: float


class WaiterOrderOut(BaseSchema):
    id: int
    table_id: int
    table_number: int
    status: OrderStatus
    items: list[OrderItemOut]
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

### .\backend\app\websocket\manager.py

**Funciones (3):**
- __init__
- disconnect
- disconnect_waiter

**Clases (1):**
- ConnectionManager

**Imports (2):**
- fastapi.WebSocket
- collections.defaultdict

```python
from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:

    def __init__(self):

        # restaurant -> station -> kitchen connections
        self.connections = defaultdict(lambda: defaultdict(list))

        # restaurant -> waiter connections
        self.waiters = defaultdict(list)


    # =========================
    # KITCHEN
    # =========================

    async def connect(self, websocket: WebSocket, restaurant_id: int, station_id: int):

        await websocket.accept()

        self.connections[restaurant_id][station_id].append(websocket)

        print(f"WS kitchen connected r={restaurant_id} s={station_id}")


    def disconnect(self, websocket: WebSocket, restaurant_id: int, station_id: int):

        if websocket in self.connections[restaurant_id][station_id]:
            self.connections[restaurant_id][station_id].remove(websocket)

        print(f"WS kitchen disconnected r={restaurant_id} s={station_id}")


    async def send_to_station(self, restaurant_id: int, station_id: int, message: dict):

        dead = []

        for connection in self.connections[restaurant_id][station_id]:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.connections[restaurant_id][station_id].remove(conn)

        print(
            f"Kitchen broadcast to {len(self.connections[restaurant_id][station_id])} clients"
        )


    # =========================
    # WAITERS
    # =========================

    async def connect_waiter(self, websocket: WebSocket, restaurant_id: int):

        await websocket.accept()

        self.waiters[restaurant_id].append(websocket)

        print(f"WS waiter connected r={restaurant_id}")


    def disconnect_waiter(self, websocket: WebSocket, restaurant_id: int):

        if websocket in self.waiters[restaurant_id]:
            self.waiters[restaurant_id].remove(websocket)

        print(f"WS waiter disconnected r={restaurant_id}")


    async def send_to_waiters(self, restaurant_id: int, message: dict):

        dead = []

        for connection in self.waiters[restaurant_id]:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.waiters[restaurant_id].remove(conn)

        print(
            f"Waiter broadcast to {len(self.waiters[restaurant_id])} clients"
        )


manager = ConnectionManager()
```

---

