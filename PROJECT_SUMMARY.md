# 📊 Project Summary
Generated: 2026-08-24 14:24:08.296872

## 📁 Estructura del proyecto

```
- ./
  - analyze_project.py
  - .agents/
  - .devcontainer/
  - .github/
    - workflows/
  - backend/
    - .pytest_cache/
      - v/
        - cache/
    - alembic/
      - env.py
      - versions/
        - f186e0156a8f_initial_schema.py
    - app/
      - main.py
      - restore_pending.py
      - seed.py
      - core/
        - config.py
        - redis.py
        - security.py
        - serialization.py
      - db/
        - base_class.py
        - session.py
        - tenant.py
      - dependencies/
        - auth.py
        - permissions.py
        - roles.py
      - domain/
        - backup/
          - backup_service.py
          - dependencies.py
          - restore_executor.py
          - schedule_utils.py
        - cash_register/
          - cash_movement_service.py
          - cash_register_service.py
          - dependencies.py
        - category/
          - category_service.py
          - dependencies.py
        - errors/
          - base.py
          - error_codes.py
        - events/
          - websocket.py
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
        - reports/
          - dependencies.py
          - report_service.py
        - settings/
          - dependencies.py
          - settings_service.py
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
      - infraestructure/
        - restart/
          - restart_manager.py
      - models/
        - cash_movement.py
        - cash_register.py
        - category.py
        - enums.py
        - event_outbox.py
        - order.py
        - order_item.py
        - payment.py
        - product.py
        - production_station.py
        - restaurant.py
        - restaurant_layout.py
        - system_settings.py
        - table.py
        - user.py
        - __init__.py
      - routers/
        - auth.py
        - backups.py
        - cash_register.py
        - category.py
        - kitchen.py
        - layout.py
        - orders.py
        - order_items.py
        - products.py
        - reports.py
        - stations.py
        - system_settings.py
        - tables.py
        - users.py
      - scheduler/
        - backup_jobs.py
        - scheduler.py
      - schemas/
        - auth.py
        - backup.py
        - base.py
        - cash_register.py
        - category.py
        - layout.py
        - product.py
        - reports.py
        - station.py
        - system_settings.py
        - table.py
        - user.py
        - order/
          - kitchen.py
          - order.py
          - order_item.py
          - payment.py
      - services/
        - event_cleanup.py
        - event_service.py
        - event_worker.py
      - utils/
        - money.py
      - websocket/
        - manager.py
        - ws.py
    - backups/
      - restaurant_1/
        - automatic/
    - docs/
    - tests/
      - conftest.py
      - __init__.py
      - unit/
        - factories.py
        - test_auth_and_permissions.py
        - test_backup_service.py
        - test_cash_register_service.py
        - test_order_service.py
        - test_security.py
        - __init__.py
    - uploads/
      - layouts/
        - 1/
  - backups/
    - daily/
    - last/
    - manual/
    - monthly/
    - restaurant_1/
      - before_restore/
      - daily/
      - manual/
    - weekly/
  - frontend/
    - dist/
      - assets/
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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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

### .\backend\alembic\versions\f186e0156a8f_initial_schema.py

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

Revision ID: f186e0156a8f
Revises: 
Create Date: 2026-08-24 16:20:53.715467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f186e0156a8f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('restaurants',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('plan', sa.String(), nullable=False),
    sa.Column('external_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restaurants_external_id'), 'restaurants', ['external_id'], unique=True)
    op.create_table('categories',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('restaurant_id', 'name', name='uq_category_name_per_restaurant')
    )
    op.create_table('event_outbox',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=False),
    sa.Column('target', sa.String(), nullable=False),
    sa.Column('target_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('retries', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_error', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_event_outbox_cleanup', 'event_outbox', ['status', 'processed_at'], unique=False)
    op.create_index('idx_event_outbox_failed_cleanup', 'event_outbox', ['status', 'retries', 'created_at'], unique=False)
    op.create_index('ix_event_outbox_created', 'event_outbox', ['created_at'], unique=False)
    op.create_index('ix_event_outbox_event_type', 'event_outbox', ['event_type'], unique=False)
    op.create_index('ix_event_outbox_restaurant', 'event_outbox', ['restaurant_id'], unique=False)
    op.create_index('ix_event_outbox_status', 'event_outbox', ['status'], unique=False)
    op.create_table('production_stations',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('restaurant_id', 'name', name='uq_station_name_per_restaurant')
    )
    op.create_table('restaurant_layout',
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('grid_size', sa.Integer(), nullable=False),
    sa.Column('snap_to_grid', sa.Boolean(), nullable=False),
    sa.Column('background_image', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('restaurant_id')
    )
    op.create_table('system_settings',
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('smtp_host', sa.String(), nullable=True),
    sa.Column('smtp_port', sa.Integer(), nullable=False),
    sa.Column('smtp_user', sa.String(), nullable=True),
    sa.Column('smtp_password', sa.String(), nullable=True),
    sa.Column('smtp_from', sa.String(), nullable=True),
    sa.Column('smtp_use_tls', sa.Boolean(), nullable=False),
    sa.Column('backup_email', sa.String(), nullable=True),
    sa.Column('backup_frequency', sa.Enum('manual', 'daily', 'weekly', 'monthly', name='backupfrequency', native_enum=False, length=20), nullable=False),
    sa.Column('backup_retention_daily', sa.Integer(), nullable=False),
    sa.Column('backup_retention_weekly', sa.Integer(), nullable=False),
    sa.Column('backup_retention_monthly', sa.Integer(), nullable=False),
    sa.Column('backup_time', sa.Time(), nullable=False),
    sa.Column('backup_weekday', sa.Integer(), nullable=True),
    sa.Column('backup_monthday', sa.Integer(), nullable=True),
    sa.Column('backup_enabled', sa.Boolean(), nullable=False),
    sa.Column('last_automatic_backup_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('next_automatic_backup_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_backup_result', sa.String(), nullable=True),
    sa.Column('backup_keep_local', sa.Boolean(), nullable=False),
    sa.Column('backup_send_email', sa.Boolean(), nullable=False),
    sa.Column('backup_timezone', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('restaurant_id')
    )
    op.create_table('tables',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('x', sa.Integer(), nullable=False),
    sa.Column('y', sa.Integer(), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('shape', sa.String(), nullable=False),
    sa.Column('external_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('restaurant_id', 'external_id', name='uq_table_external_per_restaurant'),
    sa.UniqueConstraint('restaurant_id', 'number', name='uq_table_number_per_restaurant')
    )
    op.create_index('ix_table_restaurant_active', 'tables', ['restaurant_id', 'active'], unique=False)
    op.create_index(op.f('ix_tables_restaurant_id'), 'tables', ['restaurant_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'WAITER', 'KITCHEN', 'CASHIER', name='userrole'), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('restaurant_id', 'username', name='uq_user_username_per_restaurant')
    )
    op.create_index(op.f('ix_users_restaurant_id'), 'users', ['restaurant_id'], unique=False)
    op.create_table('cash_registers',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('is_open', sa.Boolean(), nullable=False),
    sa.Column('opened_by_id', sa.Integer(), nullable=False),
    sa.Column('closed_by_id', sa.Integer(), nullable=True),
    sa.Column('opened_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('opening_amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('closing_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('expected_cash', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('counted_cash', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('difference', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_sales', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('payments_snapshot', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['opened_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cash_registers_restaurant_id'), 'cash_registers', ['restaurant_id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('table_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'OPEN', 'SENT', 'IN_PROGRESS', 'READY', 'CLOSED', 'CANCELLED', name='orderstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('discount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancelled_by_id', sa.Integer(), nullable=True),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['cancelled_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_external_id'), 'orders', ['external_id'], unique=True)
    op.create_index(op.f('ix_orders_restaurant_id'), 'orders', ['restaurant_id'], unique=False)
    op.create_index('ix_orders_restaurant_status', 'orders', ['restaurant_id', 'status'], unique=False)
    op.create_table('products',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('station_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.ForeignKeyConstraint(['station_id'], ['production_stations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('restaurant_id', 'name', name='uq_product_name_per_restaurant')
    )
    op.create_index(op.f('ix_products_restaurant_id'), 'products', ['restaurant_id'], unique=False)
    op.create_table('cash_movements',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('cash_register_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('cash_in', 'cash_out', name='cashmovementtype', native_enum=False, length=20), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['cash_register_id'], ['cash_registers.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cash_movements_register', 'cash_movements', ['cash_register_id'], unique=False)
    op.create_index('ix_cash_movements_register_type', 'cash_movements', ['cash_register_id', 'type'], unique=False)
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SENT', 'IN_PROGRESS', 'READY', 'DELIVERED', 'CANCELLED', name='orderitemstatus'), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancelled_by_id', sa.Integer(), nullable=True),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['cancelled_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_items_order_status', 'order_items', ['order_id', 'status'], unique=False)
    op.create_index(op.f('ix_order_items_restaurant_id'), 'order_items', ['restaurant_id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
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
    op.drop_index('ix_order_items_order_status', table_name='order_items')
    op.drop_table('order_items')
    op.drop_index('ix_cash_movements_register_type', table_name='cash_movements')
    op.drop_index('ix_cash_movements_register', table_name='cash_movements')
    op.drop_table('cash_movements')
    op.drop_index(op.f('ix_products_restaurant_id'), table_name='products')
    op.drop_table('products')
    op.drop_index('ix_orders_restaurant_status', table_name='orders')
    op.drop_index(op.f('ix_orders_restaurant_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_external_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_cash_registers_restaurant_id'), table_name='cash_registers')
    op.drop_table('cash_registers')
    op.drop_index(op.f('ix_users_restaurant_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tables_restaurant_id'), table_name='tables')
    op.drop_index('ix_table_restaurant_active', table_name='tables')
    op.drop_table('tables')
    op.drop_table('system_settings')
    op.drop_table('restaurant_layout')
    op.drop_table('production_stations')
    op.drop_index('ix_event_outbox_status', table_name='event_outbox')
    op.drop_index('ix_event_outbox_restaurant', table_name='event_outbox')
    op.drop_index('ix_event_outbox_event_type', table_name='event_outbox')
    op.drop_index('ix_event_outbox_created', table_name='event_outbox')
    op.drop_index('idx_event_outbox_failed_cleanup', table_name='event_outbox')
    op.drop_index('idx_event_outbox_cleanup', table_name='event_outbox')
    op.drop_table('event_outbox')
    op.drop_table('categories')
    op.drop_index(op.f('ix_restaurants_external_id'), table_name='restaurants')
    op.drop_table('restaurants')

    # --------------------------------------------------
    # Eliminar ENUM nativos de PostgreSQL.
    #
    # Al eliminar las tablas PostgreSQL no elimina
    # automáticamente los tipos ENUM asociados.
    # --------------------------------------------------
    op.execute(
        "DROP TYPE IF EXISTS paymentmethod"
    )

    op.execute(
        "DROP TYPE IF EXISTS orderitemstatus"
    )

    op.execute(
        "DROP TYPE IF EXISTS orderstatus"
    )

    op.execute(
        "DROP TYPE IF EXISTS userrole"
    )
    # ### end Alembic commands ###

```

---

### .\backend\app\main.py

**Funciones (5):**
- lifespan
- root
- health
- domain_error_handler
- unexpected_error_handler

**Clases (0):**

**Imports (33):**
- collections.abc.AsyncGenerator
- contextlib.asynccontextmanager
- fastapi.FastAPI
- fastapi.Request
- fastapi.responses.JSONResponse
- fastapi.middleware.cors.CORSMiddleware
- fastapi.staticfiles.StaticFiles
- asyncio
- logging
- pathlib.Path
- app.models
- app.services.event_worker.EventWorker
- app.services.event_cleanup.EventCleanup
- app.events.redis_listener.redis_event_listener
- app.scheduler.scheduler.scheduler
- app.scheduler.backup_jobs.register_jobs
- app.routers.tables
- app.routers.orders
- app.routers.products
- app.routers.cash_register
- app.routers.category
- app.routers.order_items
- app.routers.layout
- app.routers.system_settings
- app.routers.stations
- app.routers.auth
- app.routers.users
- app.routers.kitchen
- app.routers.reports
- app.routers.backups
- app.domain.errors.base.DomainError
- app.websocket.ws
- app.core.config.CORS_ORIGINS

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import asyncio
import logging
from pathlib import Path

from app import models
from app.services.event_worker import EventWorker
from app.services.event_cleanup import EventCleanup
from app.events.redis_listener import redis_event_listener

from app.scheduler.scheduler import scheduler
from app.scheduler.backup_jobs import register_jobs

# routers
from app.routers import tables, orders, products, cash_register, category, order_items
from app.routers import layout, system_settings, stations, auth, users, kitchen, reports, backups

from app.domain.errors.base import DomainError
from app.websocket import ws
from app.core.config import CORS_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("app.main")

# --------------------------------------------------------------------------------------
# Configuración del ciclo de vida de la aplicación.
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Backend arrancando...")

    # Event worker
    worker = EventWorker()
    worker_task = asyncio.create_task(worker.run())
    logger.info("Event worker iniciado")

    # Redis listener
    redis_task = asyncio.create_task(redis_event_listener())
    logger.info("Redis listener iniciado")

    # Event cleanup
    cleanup = EventCleanup(interval_seconds=3600)
    cleanup_task = asyncio.create_task(cleanup.run())
    logger.info("Event cleanup iniciado")

    # Scheduler
    logger.info("Iniciando scheduler...")
    register_jobs()
    scheduler.start()
    logger.info("Scheduler iniciado")

    try:
        yield
    finally:
        logger.info("Backend apagándose...")

        # Detener scheduler
        scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")

        redis_task.cancel()
        worker_task.cancel()
        cleanup_task.cancel()

        await asyncio.gather(
            redis_task,
            worker_task,
            cleanup_task,
            return_exceptions=True,
        )
        logger.info("Redis listener detenido")
        logger.info("Event worker detenido")
        logger.info("Event cleanup detenido")

# --------------------------------------------------------------------------------------
# Aplicación FastAPI.
# --------------------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# --------------------------------------------------------------------------------------
# Configuración de archivos estáticos.
# --------------------------------------------------------------------------------------
uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# --------------------------------------------------------------------------------------
# Configuración CORS.
# --------------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# Registro de routers.
# --------------------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(backups.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen.router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws.router)
app.include_router(layout.router, prefix="/api")
app.include_router(system_settings.router, prefix="/api")

# --------------------------------------------------------------------------------------
# Endpoints del sistema.
# --------------------------------------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    return {"status": "running"}


@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "restaurant-pos",
        "version": "1.0.0"
    }

# --------------------------------------------------------------------------------------
# Manejadores globales de excepciones.
# --------------------------------------------------------------------------------------
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logger.warning("%s: %s", exc.code, exc.message,)
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "detail": exc.message,
            "context": exc.context
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
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

### .\backend\app\restore_pending.py

**Funciones (0):**

**Clases (0):**

**Imports (2):**
- pathlib.Path
- app.domain.backup.restore_executor.RestoreExecutor

```python
from pathlib import Path

from app.domain.backup.restore_executor import RestoreExecutor


# --------------------------------------------------------------------------------------
# Archivo utilizado para indicar que existe una restauración pendiente.
# --------------------------------------------------------------------------------------
PENDING = Path("/backups/restore.pending")


# --------------------------------------------------------------------------------------
# Si existe un archivo de restauración pendiente, ejecutar el restore antes de iniciar
# la aplicación y eliminar el archivo de control.
# --------------------------------------------------------------------------------------
if PENDING.exists():
    backup = Path(PENDING.read_text().strip())

    print(
        f"restore_pending. Restaurando base de datos desde backup: {backup}"
    )

    RestoreExecutor.restore(backup)

    PENDING.unlink()
```

---

### .\backend\app\seed.py

**Funciones (3):**
- seed_restaurant
- seed_admin
- run

**Clases (0):**

**Imports (8):**
- logging
- os
- sqlalchemy.orm.Session
- app.core.security.get_password_hash
- app.db.session.SessionLocal
- app.models.restaurant.Restaurant
- app.models.user.User
- app.models.user.UserRole

```python
import logging
import os

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole

logger = logging.getLogger("app.seed")


# --------------------------------------------------------------------------------------
# Crea el restaurante por defecto si aún no existe.
# --------------------------------------------------------------------------------------
def seed_restaurant(db: Session) -> Restaurant:
    restaurant = db.query(Restaurant).first()
    if restaurant:
        logger.info("Default restaurant already exists.")
        return restaurant
    logger.info("Creating default restaurant.")
    restaurant = Restaurant(
        name="Resto Demo"
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

# --------------------------------------------------------------------------------------
# Crea el usuario administrador por defecto si aún no existe.
# --------------------------------------------------------------------------------------
def seed_admin(db: Session, restaurant: Restaurant,) -> None:
    admin = (
        db.query(User)
        .filter(
            User.restaurant_id == restaurant.id,
            User.username == "admin",
        )
        .first()
    )
    if admin:
        logger.info("Admin user already exists.")
        return
    admin_password = os.getenv("ADMIN_SEED_PASSWORD")
    if not admin_password:
        raise RuntimeError(
            "ADMIN_SEED_PASSWORD must be configured."
        )
    logger.info("Creating admin user.")
    db.add(
        User(
            username="admin",
            role=UserRole.ADMIN,
            password_hash=get_password_hash(admin_password),
            restaurant_id=restaurant.id,
            active=True,
        )
    )
    db.commit()
    logger.info("Admin user created successfully.")

# --------------------------------------------------------------------------------------
# Ejecuta el proceso completo de inicialización de datos.
# --------------------------------------------------------------------------------------
def run() -> None:
    db: Session = SessionLocal()
    try:
        restaurant = seed_restaurant(db)
        seed_admin(db, restaurant,)
    finally:

        db.close()

# --------------------------------------------------------------------------------------
# Punto de entrada del proceso de inicialización.
# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    run()
```

---

### .\backend\app\core\config.py

**Funciones (3):**
- _get_csv_env
- _get_int_env
- _get_required_env

**Clases (0):**

**Imports (2):**
- os
- dotenv.load_dotenv

```python
import os

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno separada por comas como lista de strings.
# --------------------------------------------------------------------------------------
def _get_csv_env(
    name: str,
    default: str
) -> list[str]:
    value = os.getenv(name, default)
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno como entero.
# --------------------------------------------------------------------------------------
def _get_int_env(
    name: str,
    default: int
) -> int:
    return int(
        os.getenv(name, str(default))
    )

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno obligatoria.
# Lanza RuntimeError si no está definida.
# --------------------------------------------------------------------------------------
def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} no está configurada. Defínela en el archivo .env"
        )
    return value


SECRET_KEY = _get_required_env("SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

DATABASE_URL = _get_required_env("DATABASE_URL")

ACCESS_TOKEN_EXPIRE_MINUTES = _get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES",60)

CORS_ORIGINS = _get_csv_env("CORS_ORIGINS","")

if not CORS_ORIGINS:
    raise RuntimeError(
        "CORS_ORIGINS debe configurarse explícitamente"
    )

```

---

### .\backend\app\core\redis.py

**Funciones (0):**

**Clases (0):**

**Imports (2):**
- os
- redis.asyncio

```python
import os

import redis.asyncio as redis

redis_client: redis.Redis = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_keepalive=True,
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

**Imports (10):**
- datetime.datetime
- datetime.timedelta
- datetime.timezone
- uuid.uuid4
- jose.JWTError
- jose.jwt
- passlib.context.CryptContext
- app.core.config.ACCESS_TOKEN_EXPIRE_MINUTES
- app.core.config.ALGORITHM
- app.core.config.SECRET_KEY

```python
"""
Funciones de seguridad del sistema.

Responsabilidades:
- Generar hashes BCrypt.
- Verificar contraseñas.
- Crear tokens JWT.
- Validar y decodificar tokens JWT.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)

# --------------------------------------------------------------------------------------
# Contexto utilizado para el hash y verificación de contraseñas
# --------------------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------------------------------------------------------------------
# Genera el hash BCrypt de una contraseña
# --------------------------------------------------------------------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --------------------------------------------------------------------------------------
# Verifica una contraseña contra su hash BCrypt
# --------------------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --------------------------------------------------------------------------------------
# Crea un JWT firmado con la información suministrada
# --------------------------------------------------------------------------------------
def create_access_token(data: dict[str, object]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        "jti": str(uuid4()) # Identificador único del token
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# --------------------------------------------------------------------------------------
# Decodifica un JWT y devuelve su payload si es válido
# --------------------------------------------------------------------------------------
def decode_access_token(token: str) -> dict[str, object] | None:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        return None
```

---

### .\backend\app\core\serialization.py

**Funciones (2):**
- decimal_to_float
- decimal_dict_to_float

**Clases (0):**

**Imports (2):**
- decimal.Decimal
- typing.Any

```python
from decimal import Decimal
from typing import Any


# --------------------------------------------------------------------------------------
# Convierte un Decimal a float. Si el valor no es Decimal, lo devuelve sin cambios.
# --------------------------------------------------------------------------------------
def decimal_to_float(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


# --------------------------------------------------------------------------------------
# Convierte todos los valores Decimal de un diccionario a float.
# --------------------------------------------------------------------------------------
def decimal_dict_to_float(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: decimal_to_float(value)
        for key, value in data.items()
    }
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
- collections.abc.Generator
- sqlalchemy.create_engine
- sqlalchemy.orm.Session
- sqlalchemy.orm.sessionmaker
- app.core.config.DATABASE_URL

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

# --------------------------------------------------------------------------------------
# Motor principal de SQLAlchemy
# --------------------------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# --------------------------------------------------------------------------------------
# Fábrica de sesiones de base de datos
# --------------------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------------------------------------------------------------
# Dependency de FastAPI que proporciona una sesión de base de datos.
# La sesión se cierra automáticamente al finalizar la petición.
# --------------------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
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

**Funciones (2):**
- authenticate_token
- get_current_user

**Clases (0):**

**Imports (9):**
- fastapi.Depends
- fastapi.security.OAuth2PasswordBearer
- sqlalchemy.orm.Session
- app.core.security.decode_access_token
- app.db.session.get_db
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.user.User
- app.models.user.UserRole

```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token

from app.db.session import get_db

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.user import (
    User,
    UserRole
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ---------------------------------------------------------------------------------------------
# Autentica un token y devuelve el usuario correspondiente.
# Lanza DomainError si el token es inválido, el usuario no existe o no puede autenticarse.
# ---------------------------------------------------------------------------------------------
def authenticate_token(
    db: Session,
    token: str
) -> User:

    payload = decode_access_token(token)

    if not payload:
        raise DomainError(
            "Invalid token",
            ErrorCode.INVALID_TOKEN
        )

    try:
        user_id = int(payload["sub"])
        restaurant_id = int(payload["restaurant_id"])
        role = UserRole(payload["role"])

    except (KeyError, TypeError, ValueError):
        raise DomainError(
            "Invalid token payload",
            ErrorCode.INVALID_TOKEN_PAYLOAD
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        )
        .first()
    )

    if not user:
        raise DomainError(
            "User not found",
            ErrorCode.USER_NOT_FOUND
        )

    if not user.active:
        raise DomainError(
            "Inactive user",
            ErrorCode.USER_INACTIVE
        )

    if user.role != role:
        raise DomainError(
            "Role mismatch",
            ErrorCode.ROLE_MISMATCH
        )

    return user


# ---------------------------------------------------------------------------------------------
# Obtiene el usuario autenticado a partir del token de acceso.
# Lanza DomainError si el token es inválido o el usuario no puede autenticarse.
# ---------------------------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    return authenticate_token(
        db=db,
        token=token
    )
```

---

### .\backend\app\dependencies\permissions.py

**Funciones (2):**
- require_roles
- role_checker

**Clases (0):**

**Imports (6):**
- fastapi.Depends
- app.dependencies.auth.get_current_user
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.user.User
- app.models.user.UserRole

```python
from fastapi import Depends

from app.dependencies.auth import get_current_user

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.user import User, UserRole

# --------------------------------------------------------------------------------------
# Crea una dependencia que restringe el acceso a uno o más roles.
#
# Uso:
#   admin_only = require_roles(UserRole.ADMIN)
#   admin_or_cashier = require_roles(UserRole.ADMIN, UserRole.CASHIER)
# --------------------------------------------------------------------------------------
def require_roles(*roles: UserRole):

    # ----------------------------------------------------------------------------------
    # Verifica que el usuario autenticado tenga alguno de los roles permitidos.
    # ----------------------------------------------------------------------------------
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise DomainError(
                "Permission denied",
                ErrorCode.PERMISSION_DENIED,
                context={
                    "required_roles": [role.value for role in roles],
                    "user_role": user.role.value
                }
            )
        return user
    return role_checker
```

---

### .\backend\app\dependencies\roles.py

**Funciones (0):**

**Clases (0):**

**Imports (2):**
- app.dependencies.permissions.require_roles
- app.models.user.UserRole

```python
from app.dependencies.permissions import require_roles

from app.models.user import UserRole

# --------------------------------------------------------------------------------------
# Dependencias reutilizables para autorización basada en roles.
# --------------------------------------------------------------------------------------

admin_only = require_roles(UserRole.ADMIN)

waiter_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER
)

cashier_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.CASHIER
)

kitchen_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.KITCHEN
)

waiter_cashier_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.CASHIER
)

waiter_kitchen_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.KITCHEN
)

all_staff = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.CASHIER,
    UserRole.KITCHEN
)
```

---

### .\backend\app\domain\backup\backup_service.py

**Funciones (29):**
- __init__
- _get_settings
- _create_backup
- _backup_before_restore
- _cleanup_before_restore
- _backup_info
- _find_backup
- _build_backup_path
- _backup_database
- _backup_sqlite
- _backup_postgres
- _send_backup_email
- _email_enabled
- _resolve_backup_dir
- _latest_backup_file
- _restaurant_backup_directory
- _apply_retention_policy
- _calculate_next_run
- _create_restore_pending
- status
- create_backup
- create_automatic_backup
- create_and_email_backup
- download_backup
- list_backups
- delete_backup
- restore_backup
- run_pending_backups
- run_scheduled_backup

**Clases (1):**
- BackupService

**Imports (28):**
- os
- shutil
- smtplib
- socket
- subprocess
- logging
- datetime.datetime
- datetime.timedelta
- datetime.timezone
- datetime.time
- calendar
- zoneinfo.ZoneInfo
- email.message.EmailMessage
- pathlib.Path
- urllib.parse.unquote
- urllib.parse.urlparse
- fastapi.responses.FileResponse
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.db.session.DATABASE_URL
- app.infraestructure.restart.restart_manager.RestartManager
- app.models.system_settings.SystemSettings
- app.schemas.backup.BackupStatusOut
- app.schemas.backup.BackupInfoOut
- app.schemas.backup.BackupFileOut
- app.schemas.backup.BackupEmailOut
- app.schemas.backup.BackupDeleteOut
- app.schemas.backup.BackupRestoreOut

```python
import os
import shutil
import smtplib
import socket
import subprocess
import logging
from datetime import (
    datetime,
    timedelta,
    timezone,
    time
)
import calendar
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastapi.responses import FileResponse

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.db.session import DATABASE_URL

from app.infraestructure.restart.restart_manager import RestartManager

from app.models.system_settings import SystemSettings

from app.schemas.backup import (
    BackupStatusOut,
    BackupInfoOut,
    BackupFileOut,
    BackupEmailOut,
    BackupDeleteOut,
    BackupRestoreOut
)

BEFORE_RESTORE_MAX = 10
logger = logging.getLogger("app.domain.backup")

class BackupService:

    """
    Servicio encargado de la lógica de negocio relacionada con los backups.

    Responsabilidades:
    - Gestionar la lógica de negocio de los backups.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db) -> None:
        self.db = db
        self.backup_dir = self._resolve_backup_dir()

#-------------------------------------------------------------------
# DEVOLVER CONFIGURACIÓN DEL RESTAURANTE
#-------------------------------------------------------------------
    def _get_settings(self,restaurant_id: int) -> SystemSettings | None:
        return (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.restaurant_id
                == restaurant_id
            )
            .first()
        )

#-------------------------------------------------------------------
# CREAR BACKUP (MANUAL, AUTOMÁTICO O ANTES DE RESTAURAR)
#-------------------------------------------------------------------
    def _create_backup(
        self,
        restaurant_id: int,
        backup_type: str
    ):
        backup_path = self._build_backup_path(
            restaurant_id,
            backup_type,
            datetime.now(timezone.utc)
        )
        self._backup_database(
            backup_path
        )
        return self._backup_info(
            backup_path
        )

#-------------------------------------------------------------------
# CREAR BACKUP ANTES DE RESTAURAR
#-------------------------------------------------------------------
    def _backup_before_restore(self, restaurant_id) -> BackupInfoOut:
        self._create_backup(
            restaurant_id,
            "before_restore"
        )
        self._cleanup_before_restore(restaurant_id)

#-------------------------------------------------------------------
# MANTENER SOLO LOS ÚLTIMOS BACKUPS ANTES DE RESTAURAR
#-------------------------------------------------------------------
    def _cleanup_before_restore(self, restaurant_id: int):
        directory = (
            self._restaurant_backup_directory(restaurant_id)
            / "before_restore"
        )

        if not directory.exists():
            return

        backups = sorted(
            (
                path
                for path in directory.iterdir()
                if path.is_file()
            ),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for backup in backups[BEFORE_RESTORE_MAX:]:
            backup.unlink()

#-------------------------------------------------------------------
# DEVOLVER INFORMACIÓN DEL BACKUP
#-------------------------------------------------------------------
    def _backup_info(self, backup_path: Path):
        stat = backup_path.stat()

        return {
            "last_backup_at": datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc
            ),
            "last_backup_file": str(
                backup_path.relative_to(self.backup_dir)
            ),
            "last_backup_size": stat.st_size,
            "type": backup_path.parent.name
        }

#-------------------------------------------------------------------
# DEVOLVER EL PATH DEL BACKUP SI EXISTE, O LANZAR ERROR SI NO EXISTE
#-------------------------------------------------------------------
    def _find_backup(
        self,
        restaurant_id: int,
        filename: str
    ) -> Path:
        restaurant_dir = self._restaurant_backup_directory(
            restaurant_id
        )
        path = (restaurant_dir / filename).resolve()
        if not path.exists() or not path.is_file():
            raise DomainError(
                "Backup not found",
                ErrorCode.BACKUP_NOT_FOUND,
                context={"filename": filename})
        # Evita que intenten acceder fuera del directorio
        if restaurant_dir.resolve() not in path.parents:
            raise DomainError(
                "Invalid backup path",
                ErrorCode.BACKUP_INVALID_PATH,
                context={"filename": filename}
            )
        return path

#-------------------------------------------------------------------
# CONSTRUIR EL PATH DEL BACKUP
#-------------------------------------------------------------------
    def _build_backup_path(
        self,
        restaurant_id: int,
        backup_type: str,
        created_at: datetime,
    ):
        suffix = (
            ".sqlite3"
            if DATABASE_URL.startswith("sqlite")
            else ".dump"
        )
        directory = self._restaurant_backup_directory(restaurant_id)
        return (
            directory /
            f"backup-{created_at:%Y%m%d-%H%M%S}{suffix}"
        )

#-------------------------------------------------------------------
# BACKUP BASE DE DATOS DE ACUERDO AL MOTOR DE BASE DE DATOS
#-------------------------------------------------------------------
    def _backup_database(self, backup_path: Path):
        if DATABASE_URL.startswith("sqlite"):
            self._backup_sqlite(backup_path)

        elif DATABASE_URL.startswith("postgresql"):
            self._backup_postgres(backup_path)

        else:
            raise DomainError(
                "Not supported database engine for backup",
                ErrorCode.BACKUP_ENGINE_NOT_SUPPORTED
            )

#-------------------------------------------------------------------
# BACKUP EN SQLITE
#-------------------------------------------------------------------
    def _backup_sqlite(self, backup_path: Path):
        parsed = urlparse(DATABASE_URL)
        database_path = unquote(parsed.path)
        if os.name == "nt" and database_path.startswith("/"):
            database_path = database_path[1:]
        source = Path(database_path)
        if not source.exists():
            raise DomainError(
                "Database file not found for backup",
                ErrorCode.BACKUP_DATABASE_NOT_FOUND
            )
        shutil.copy2(source, backup_path)

#-------------------------------------------------------------------
# BACKUP EN POSTGRES
#-------------------------------------------------------------------
    def _backup_postgres(self, backup_path: Path):
        parsed = urlparse(
            DATABASE_URL.replace(
                "postgresql+psycopg2://",
                "postgresql://"
            )
        )
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password
        command = [
            "pg_dump",
            "-h", parsed.hostname,
            "-p", str(parsed.port or 5432),
            "-U", parsed.username,
            "-d", parsed.path.lstrip("/"),

            "--format=custom",
            "--clean",
            "--if-exists",
            "--no-owner",
            
            "--file", str(backup_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            detail = result.stderr.strip() or "No se pudo ejecutar pg_dump"
            raise DomainError(
                "Error creating backup with pg_dump",
                ErrorCode.BACKUP_FAILED,
                context={"detail": detail}
            )

#-------------------------------------------------------------------
# ENVIAR BACKUP POR EMAIL
#-------------------------------------------------------------------
    def _send_backup_email(self, recipient_email: str, backup_path: Path, created_at: str, restaurant_id: int):
        settings = self._get_settings(
            restaurant_id
        )
        if not settings:
            raise DomainError(
                code=ErrorCode.SMTP_NOT_CONFIGURED,
                detail="SMTP does not configured for this restaurant"
            )
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port or 587
        smtp_user = settings.smtp_user or ""
        smtp_password = settings.smtp_password or ""
        smtp_from = (
            settings.smtp_from
            or smtp_user
        )
        smtp_use_tls = settings.smtp_use_tls
        message = EmailMessage()
        message["Subject"] = "Backup del sistema restaurant"
        message["From"] = smtp_from
        message["To"] = recipient_email
        message.set_content(
            f"Adjunto backup generado el {created_at}.\n\n"
            "Este correo fue generado automaticamente por el sistema."
        )
        message.add_attachment(
            backup_path.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=backup_path.name
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            if smtp_use_tls:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            if smtp_user:
                smtp.login(smtp_user, smtp_password)
            smtp.send_message(message)

#-------------------------------------------------------------------
# DEVOLVER TRUE o FALSE SI EL EMAIL ESTA CONFIGURADO PARA ESTE RESTAURANTE
#-------------------------------------------------------------------
    def _email_enabled(self, restaurant_id: int):
        settings = self._get_settings(restaurant_id)
        if not settings:
            return False
        return bool(
            settings.smtp_host
            and (
                settings.smtp_from
                or settings.smtp_user
            )
        )

#-------------------------------------------------------------------
# DEVOLVER EL DIRECTORIO DE BACKUPS
#-------------------------------------------------------------------
    def _resolve_backup_dir(self):
        configured_dir = os.getenv("BACKUP_DIR")
        if configured_dir:
            return Path(configured_dir)
        mounted_dir = Path("/backups")
        if mounted_dir.exists():
            return mounted_dir
        return Path("backups")

#-------------------------------------------------------------------
# OBTENER ÚLTIMO BACKUP
#-------------------------------------------------------------------
    def _latest_backup_file(self, restaurant_id: int):
        restaurant_dir = self._restaurant_backup_directory(restaurant_id)
        if not restaurant_dir.exists():
            return None
        candidates = [
            path
            for path in restaurant_dir.rglob("*")
            if path.is_file()
            and path.stat().st_size > 0
        ]
        if not candidates:
            return None
        latest = max(candidates, key=lambda path: path.stat().st_mtime)
        stats = latest.stat()

        return {
            "name": str(latest.relative_to(self.backup_dir)),
            "modified_at": datetime.fromtimestamp(stats.st_mtime,tz=timezone.utc).isoformat(),
            "size": stats.st_size,
            "type": latest.parent.name
        }

#-------------------------------------------------------------------
# Devolver el directorio de backups del restaurante
#-------------------------------------------------------------------    
    def _restaurant_backup_directory(
        self,
        restaurant_id: int
    ) -> Path:
        directory = (
            self.backup_dir /
            f"restaurant_{restaurant_id}"
        )
        directory.mkdir(
            parents=True,
            exist_ok=True
        )
        return directory

#-------------------------------------------------------------------
# APLICAR POLÍTICA DE RETENCIÓN
#-------------------------------------------------------------------
    def _apply_retention_policy(self, settings: SystemSettings):
        restaurant_dir = (
            self.backup_dir /
            f"restaurant_{settings.restaurant_id}"
        )

        if not restaurant_dir.exists():
            return

        now = datetime.now(timezone.utc)

        retention = {
            "daily": settings.backup_retention_daily,
            "weekly": settings.backup_retention_weekly,
            "monthly": settings.backup_retention_monthly,
        }

        for backup_type, days in retention.items():

            if not days:
                continue

            directory = restaurant_dir / backup_type

            if not directory.exists():
                continue

            limit = now - timedelta(days=days)

            for backup in directory.rglob("*"):

                if not backup.is_file():
                    continue

                modified = datetime.fromtimestamp(
                    backup.stat().st_mtime,
                    tz=timezone.utc
                )

                if modified < limit:
                    backup.unlink()

#-------------------------------------------------------------------
# CALCULAR PRÓXIMO BACKUP PROGRAMADO
#-------------------------------------------------------------------
    def _calculate_next_run(
        self,
        settings: SystemSettings
    ):
        tz = ZoneInfo(settings.backup_timezone)
        now = datetime.now(tz)
        backup_time = settings.backup_time or time(3, 0)
        candidate = now.replace(
            hour=backup_time.hour,
            minute=backup_time.minute,
            second=0,
            microsecond=0
        )
        frequency = settings.backup_frequency.value
        if frequency == "daily":
            if candidate <= now:
                candidate += timedelta(days=1)
            return candidate
        if frequency == "weekly":
            weekday = settings.backup_weekday or 0
            days = weekday - candidate.weekday()
            if days < 0:
                days += 7
            candidate += timedelta(days=days)
            if candidate <= now:
                candidate += timedelta(days=7)
            return candidate
        if frequency == "monthly":
            monthday = settings.backup_monthday or 1
            year = now.year
            month = now.month
            last_day = calendar.monthrange(year, month)[1]
            day = min(monthday, last_day)
            candidate = candidate.replace(day=day)
            if candidate <= now:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                last_day = calendar.monthrange(year, month)[1]
                day = min(monthday, last_day)
                candidate = candidate.replace(
                    year=year,
                    month=month,
                    day=day
                )
            return candidate.astimezone(timezone.utc)
        return None

#-------------------------------------------------------------------------------
# Crear archivo restore.pending para indicar que se debe restaurar un backup
#-------------------------------------------------------------------------------
    def _create_restore_pending(self, backup: Path):
        pending = Path(os.getenv("BACKUP_DIR", "/backups")) / "restore.pending"
        pending.write_text(str(backup), encoding="utf-8")

#-------------------------------------------------------------------
# DEVOLVER EL ESTADO DEL BACKUP
#-------------------------------------------------------------------
    def status(self, restaurant_id: int) -> BackupStatusOut:
        settings = self._get_settings(restaurant_id)
        self.backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        latest = self._latest_backup_file(restaurant_id)
        return BackupStatusOut(
            last_backup_at=latest["modified_at"] if latest else None,
            last_backup_file=latest["name"] if latest else None,
            last_backup_size=latest["size"] if latest else None,
            last_backup_source=latest["type"] if latest else None,
            email_enabled=self._email_enabled(restaurant_id),
            email_from=settings.smtp_from if settings else None,
            last_automatic_backup_at=settings.last_automatic_backup_at
            if settings and settings.last_automatic_backup_at
            else None,
            next_automatic_backup_at=settings.next_automatic_backup_at
                if settings and settings.next_automatic_backup_at
                else None,
            last_backup_result=settings.last_backup_result
                if settings else None
        )

#-------------------------------------------------------------------
# CREAR BACKUP
#-------------------------------------------------------------------
    def create_backup(self, restaurant_id) -> BackupInfoOut:
        return self._create_backup(
            restaurant_id,
            "manual"
        )

#-------------------------------------------------------------------
# CREAR BACKUP AUTOMÁTICO
#-------------------------------------------------------------------
    def create_automatic_backup(self, restaurant_id, frequency) -> BackupInfoOut:
        return self._create_backup(
            restaurant_id,
            frequency
        )

#-------------------------------------------------------------------
# CREAR BACKUP Y ENVIAR POR EMAIL
#-------------------------------------------------------------------
    def create_and_email_backup(self, recipient_email: str, restaurant_id: int) -> BackupEmailOut:
        if not self._email_enabled(restaurant_id):
            raise DomainError(
                code=ErrorCode.SMTP_NOT_CONFIGURED,
                detail="SMTP is not configured for this restaurant"
            )
        backup = self.create_backup(restaurant_id)
        backup_path = self.backup_dir / backup.last_backup_file
        try:
            self._send_backup_email(
                recipient_email=recipient_email,
                backup_path=backup_path,
                created_at=backup.last_backup_at,
                restaurant_id=restaurant_id
            )

        except (
            smtplib.SMTPException,
            ConnectionError,
            TimeoutError,
            socket.timeout,
            OSError
        ) as ex:
            raise DomainError(
                "Error sending backup email",
                ErrorCode.EMAIL_SEND_FAILURE,
                context={
                    "recipient": recipient_email,
                    "detail": str(ex)
                }
            ) from ex

        return BackupEmailOut(
            **backup.model_dump(),
            sent_to=recipient_email
        )

#-------------------------------------------------------------------
# DESCARGAR BACKUP
#-------------------------------------------------------------------
    def download_backup(self, restaurant_id: int, filename: str ):
        path = self._find_backup(
            restaurant_id,
            filename
        )
        return FileResponse(
            path=path,
            filename=path.name,
            media_type="application/octet-stream"
        )

#-------------------------------------------------------------------
# LISTAR BACKUPS
#-------------------------------------------------------------------
    def list_backups(self, restaurant_id: int) -> list[BackupFileOut]:
        directory = self._restaurant_backup_directory(
            restaurant_id
        )
        files = [
            path
            for path in directory.rglob("*")
            if path.is_file()
        ]
        files.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return [
            BackupFileOut(
                filename=str(path.relative_to(directory)),
                created_at=datetime.fromtimestamp(
                    path.stat().st_mtime,
                    tz=timezone.utc
                ),
                size=path.stat().st_size,
                type=(
                    "manual"
                    if path.parent == directory
                    else path.parent.name
                )
            )
            for path in files
        ]

#-------------------------------------------------------------------
# ELIMINAR BACKUP
#-------------------------------------------------------------------    
    def delete_backup(self, restaurant_id: int, filename: str) -> BackupDeleteOut:
        path = self._find_backup(
            restaurant_id,
            filename
        )
        path.unlink()
        return BackupDeleteOut(success=True)

#-------------------------------------------------------------------
# RESTORE BACKUP
#-------------------------------------------------------------------
    def restore_backup(self, restaurant_id: int, filename: str) -> BackupRestoreOut:
        print(">>> 1")

        backup = self._find_backup(
            restaurant_id,
            filename
        )
        self._backup_before_restore(restaurant_id)
        self._create_restore_pending(backup)
        RestartManager.request_restart()
        return BackupRestoreOut(
            success=True,
            restart_required=True
        )

#-------------------------------------------------------------------
# CORRER BACKUPS PENDIENTES
#-------------------------------------------------------------------
    def run_pending_backups(self):
        now = datetime.now(timezone.utc)
        restaurants = (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.backup_enabled.is_(True),
                SystemSettings.next_automatic_backup_at <= now
            )
            .all()
        )
        for settings in restaurants:
            try:
                self.run_scheduled_backup(
                    settings.restaurant_id
                )
            except Exception:
                logger.exception(
                    f"Error running scheduled backup for restaurant {settings.restaurant_id}"
                )
                self.db.rollback()

#-------------------------------------------------------------------
# CORRER BACKUP PROGRAMADO
#-------------------------------------------------------------------
    def run_scheduled_backup(self, restaurant_id: int):
        settings = self._get_settings(restaurant_id)
        try:
            backup = self.create_automatic_backup(
                restaurant_id,
                settings.backup_frequency.value
            )

            self._apply_retention_policy(settings)
            
            if settings.backup_send_email and settings.backup_email:
                backup_path = (
                    self.backup_dir /
                    backup["last_backup_file"]
                )
                self._send_backup_email(
                    settings.backup_email,
                    backup_path,
                    backup["last_backup_at"],
                    restaurant_id
                )
            settings.last_backup_result = "OK"
        except Exception as ex:
            logger.exception(
                f"Error running scheduled backup for restaurant {settings.restaurant_id}"
            )
            settings.last_backup_result = str(ex)
        settings.last_automatic_backup_at = datetime.now(timezone.utc)
        settings.next_automatic_backup_at = self._calculate_next_run(settings)
        self.db.commit()
```

---

### .\backend\app\domain\backup\dependencies.py

**Funciones (1):**
- get_backup_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- backup_service.BackupService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .backup_service import BackupService


def get_backup_service(
    db: Session = Depends(get_db)
) -> BackupService:
    return BackupService(db)
```

---

### .\backend\app\domain\backup\restore_executor.py

**Funciones (3):**
- restore
- _restore_sqlite
- _restore_postgres

**Clases (1):**
- RestoreExecutor

**Imports (7):**
- os
- shutil
- subprocess
- pathlib.Path
- urllib.parse.unquote
- urllib.parse.urlparse
- app.db.session.DATABASE_URL

```python
import os
import shutil
import subprocess
from pathlib import Path

from urllib.parse import unquote, urlparse

from app.db.session import DATABASE_URL

class RestoreExecutor:

#--------------------------------------------------------------------------------------
# RESTAURA LA BASE DE DATOS DE ACUERDO AL MOTOR DE BASE DE DATOS
#--------------------------------------------------------------------------------------
    @staticmethod
    def restore(backup: Path) -> None:
        if DATABASE_URL.startswith("sqlite"):
            RestoreExecutor._restore_sqlite(backup)
        elif DATABASE_URL.startswith("postgresql"):
            RestoreExecutor._restore_postgres(backup)
        else:
            raise RuntimeError(
                f"Unsupported database engine: {DATABASE_URL}"
            )

#-------------------------------------------------------------------
# RESTORE SQLITE
#-------------------------------------------------------------------
    @staticmethod
    def _restore_sqlite(backup: Path) -> None:
        parsed = urlparse(DATABASE_URL)
        database_path = unquote(parsed.path)
        if os.name == "nt" and database_path.startswith("/"):
            database_path = database_path[1:]
        destination = Path(database_path)
        shutil.copy2(backup, destination)

#-------------------------------------------------------------------
# RESTORE POSTGRES
#-------------------------------------------------------------------
    @staticmethod
    def _restore_postgres(backup: Path) -> None:
        parsed = urlparse(
            DATABASE_URL.replace(
                "postgresql+psycopg2://",
                "postgresql://"
            )
        )
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password
        command = [
            "pg_restore",
            "-h", parsed.hostname,
            "-p", str(parsed.port or 5432),
            "-U", parsed.username,
            "-d", parsed.path.lstrip("/"),
            "--clean",
            "--if-exists",
            "--no-owner",
            "--exit-on-error",
            "--verbose",
            str(backup)
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
            )
```

---

### .\backend\app\domain\backup\schedule_utils.py

**Funciones (2):**
- _resolve_timezone
- calculate_next_backup

**Clases (0):**

**Imports (10):**
- calendar
- datetime.datetime
- datetime.time
- datetime.timedelta
- datetime.timezone
- datetime.tzinfo
- zoneinfo.ZoneInfo
- zoneinfo.ZoneInfoNotFoundError
- app.models.system_settings.SystemSettings
- app.models.enums.BackupFrequency

```python
import calendar

from datetime import datetime, time, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.models.system_settings import SystemSettings
from app.models.enums import BackupFrequency

#----------------------------------------------------------------------------------
# Resuelve la zona horaria a partir del nombre de la zona horaria.
# Si la zona horaria no es válida, se devuelve UTC.
#----------------------------------------------------------------------------------
def _resolve_timezone(timezone_name: str) -> tzinfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        if timezone_name == "America/Montevideo":
            return timezone(timedelta(hours=-3))
        return timezone.utc

#------------------------------------------------------------------------------------------
# Devuelve el próximo instante programado en UTC según la configuración del restaurante.
#------------------------------------------------------------------------------------------
def calculate_next_backup(
    settings: SystemSettings,
    reference: datetime | None = None,
) -> datetime | None:
    if reference is None:
        reference = datetime.now(timezone.utc)

    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)

    tz = _resolve_timezone(settings.backup_timezone or "UTC")
    now = reference.astimezone(tz)
    backup_time = settings.backup_time or time(3, 0)

    candidate = now.replace(
        hour=backup_time.hour,
        minute=backup_time.minute,
        second=0,
        microsecond=0
    )

    frequency = settings.backup_frequency

    if frequency == BackupFrequency.DAILY:
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.astimezone(timezone.utc)

    if frequency == BackupFrequency.WEEKLY:
        weekday = settings.backup_weekday or 0
        days = weekday - candidate.weekday()
        days = (weekday - candidate.weekday()) % 7
        candidate += timedelta(days=days)
        if candidate <= now:
            candidate += timedelta(days=7)
        return candidate.astimezone(timezone.utc)

    if frequency == BackupFrequency.MONTHLY:
        monthday = settings.backup_monthday or 1
        year = now.year
        month = now.month
        last_day = calendar.monthrange(year, month)[1]
        day = min(monthday, last_day)
        candidate = candidate.replace(day=day)
        if candidate <= now:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
            last_day = calendar.monthrange(year, month)[1]
            day = min(monthday, last_day)
            candidate = candidate.replace(
                year=year,
                month=month,
                day=day
            )
        return candidate.astimezone(timezone.utc)

    return None
```

---

### .\backend\app\domain\cash_register\cash_movement_service.py

**Funciones (4):**
- __init__
- _get_cash_movement
- create_cash_movement
- delete_cash_movement

**Clases (1):**
- CashMovementService

**Imports (11):**
- sqlalchemy.orm.Session
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.events.websocket.WSEvent
- app.services.event_service.EventService
- app.utils.money.money
- app.models.cash_movement.CashMovement
- app.models.cash_register.CashRegister
- app.models.user.UserRole
- app.schemas.cash_register.CashMovementCreate

```python
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.events.websocket import WSEvent
from app.services.event_service import EventService

from app.utils.money import money

from app.models.cash_movement import CashMovement
from app.models.cash_register import CashRegister
from app.models.user import UserRole
from app.schemas.cash_register import CashMovementCreate


class CashMovementService:

    """
    Servicio encargado de la lógica de negocio relacionada con los movimientos de la caja registradora.

    Responsabilidades:
    - Gestionar la lógica de negocio de los movimientos de la caja registradora.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # --------------------------------------------------------
    # Obtener movimiento de caja
    # --------------------------------------------------------
    def _get_cash_movement(
        self,
        restaurant_id: int,
        movement_id: int
    ) -> CashMovement:
        movement = (
            self.db.query(CashMovement)
            .join(
                CashRegister,
                CashMovement.cash_register_id == CashRegister.id
            )
            .filter(
                CashMovement.id == movement_id,
                CashRegister.restaurant_id == restaurant_id
            )
            .first()
        )
        if not movement:
            raise DomainError(
                "Movement not found",
                ErrorCode.CASH_MOVEMENT_NOT_FOUND
            )
        return movement

    # -------------------------
    # Crear movimiento de caja
    # -------------------------
    def create_cash_movement(
        self,
        restaurant_id: int,
        user_id: int,
        data: CashMovementCreate
    ) -> CashMovement:
        cash_register = CashRegisterService(self.db).get_open_cash_register(
            restaurant_id,
            for_update=True
        )
        movement = CashMovement(
            cash_register_id=cash_register.id,
            user_id=user_id,
            type=data.type,
            amount=data.amount,
            reason=data.reason
        )
        self.db.add(movement)
        self.db.flush()
        self.db.refresh(movement)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.CASH_MOVEMENT_ADDED,
            payload={
                "movement": {
                    "id": movement.id,
                    "type": movement.type.value,
                    "amount": money(movement.amount),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat()
                }
            },
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        return movement

    # ---------------------------------------------------------
    # Eliminar movimiento de caja
    # ---------------------------------------------------------
    def delete_cash_movement(
        self,
        restaurant_id: int,
        movement_id: int
    ) -> None:
        movement = self._get_cash_movement(restaurant_id, movement_id)
        amount = movement.amount
        movement_type = movement.type
        payload={
            "movement_id": movement_id,
            "amount": money(amount),
            "movement_type": movement_type.value
        }
        self.db.delete(movement)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.CASH_MOVEMENT_DELETED,
            payload=payload,
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
```

---

### .\backend\app\domain\cash_register\cash_register_service.py

**Funciones (9):**
- __init__
- _calculate_sales
- _calculate_payment_breakdown
- _calculate_cash_movements
- open_cash_register
- get_open_cash_register
- close_cash_register
- get_current_cash_register
- get_dashboard

**Clases (1):**
- CashRegisterService

**Imports (19):**
- logging
- decimal.Decimal
- sqlalchemy.orm.Session
- sqlalchemy.func
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.core.serialization.decimal_dict_to_float
- app.utils.money.money
- app.models.cash_register.CashRegister
- app.models.payment.Payment
- app.models.cash_movement.CashMovement
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.payment.PaymentMethod
- app.models.cash_movement.CashMovementType
- app.schemas.cash_register.CashRegisterClose
- app.schemas.cash_register.CashRegisterCloseOut
- app.schemas.cash_register.CashRegisterSummary
- app.schemas.cash_register.CashRegisterDashboard

```python
import logging

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.core.serialization import decimal_dict_to_float

from app.utils.money import money

from app.models.cash_register import CashRegister
from app.models.payment import Payment
from app.models.cash_movement import CashMovement
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType

from app.schemas.cash_register import (
    CashRegisterClose,
    CashRegisterCloseOut,
    CashRegisterSummary,
    CashRegisterDashboard
)

logger = logging.getLogger("app.domain.cash_register")

class CashRegisterService:

    """
    Servicio encargado de la lógica de negocio relacionada con la caja registradora.

    Responsabilidades:
    - Gestionar la lógica de negocio de la caja registradora.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------
    # Método de cálculo de ventas realizadas por caja registradora
    # --------------------------------------------------------------------------------
    def _calculate_sales(self, cash_register_id: int) -> tuple[
        Decimal,
        int,
        int,
        Decimal
    ]:
        total_sales = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        transactions_count = self.db.query(
            func.count(Payment.id)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        orders_count = self.db.query(
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

    # --------------------------------------------------------------------------------
    # Sumar pagos por método de pago
    # --------------------------------------------------------------------------------
    def _calculate_payment_breakdown(self, cash_register_id: int) -> dict[str, Decimal]:
        breakdown = {
            method.value: Decimal("0")
            for method in PaymentMethod
        }
        rows = self.db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).group_by(
            Payment.method
        ).all()
        for method, total in rows:
            breakdown[method.value] = total or Decimal("0")
        return breakdown

    # --------------------------------------------------------------------------------
    # Calcular movimientos de caja agrupados por entradas y salidas
    # --------------------------------------------------------------------------------
    def _calculate_cash_movements(self, cash_register_id: int) -> tuple[Decimal, Decimal]:
        rows = self.db.query(
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

    # --------------------------------------------------------------------------------
    # Abrir Caja
    # --------------------------------------------------------------------------------
    def open_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        opening_amount: Decimal
    ) -> CashRegister:
        if opening_amount < Decimal("0"):
            raise DomainError(
                "opening amount must be greater than or equal to zero",
                ErrorCode.INVALID_OPERATION,
                context={"opening_amount": money(opening_amount)}
            )
        existing = self.db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()
        if existing:
            raise DomainError(
                "Cash register already open", 
                ErrorCode.CASH_REGISTER_ALREADY_OPEN
                )
        logger.info("Caja abierta r=%s user=%s amount=%s", restaurant_id, user_id, opening_amount)
        cash_register = CashRegister(
            restaurant_id=restaurant_id,
            opened_by_id=user_id,
            opening_amount=opening_amount,
            is_open=True
        )
        self.db.add(cash_register)
        self.db.commit()
        self.db.refresh(cash_register)
        return cash_register

    # --------------------------------------------------------------------------------
    # Obtener una caja registradora abierta o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def get_open_cash_register(
        self,
        restaurant_id: int,
        for_update: bool = False
    ) -> CashRegister:
        query = self.db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        )
        if for_update:
            query = query.with_for_update()
        cash_register = query.first()
        if not cash_register:
            raise DomainError(
                "cash register not open",
                ErrorCode.CASH_REGISTER_NOT_OPEN
            )
        return cash_register
    
    # --------------------------------------------------------------------------------
    # Cerrar caja
    # --------------------------------------------------------------------------------
    def close_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        data: CashRegisterClose
    ) -> CashRegisterCloseOut:
        if data.counted_cash < Decimal("0"):
            raise DomainError(
                "counted cash must be greater than or equal to zero",
                ErrorCode.CASH_REGISTER_INVALID_COUNT,
                context={"counted_cash": money(data.counted_cash)}
            )
        cash_register = self.get_open_cash_register(
            restaurant_id,
            for_update=True
        )
        open_orders = self.db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            Order.status.notin_([OrderStatus.CLOSED, OrderStatus.CANCELLED, OrderStatus.DRAFT])
        ).count()
        if open_orders > 0:
            raise DomainError(
                "cannot close cash register: there are open orders",
                ErrorCode.CASH_REGISTER_PENDING_ORDERS
            )
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        payment_breakdown = self._calculate_payment_breakdown(
            cash_register.id
        )
        cash_sales = payment_breakdown.get(
            PaymentMethod.CASH.value,
            Decimal("0")
        )
        cash_in, cash_out = self._calculate_cash_movements(
            cash_register.id
        )
        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )
        closing_amount = (
            cash_register.opening_amount
            + total_sales
            + cash_in
            - cash_out
        )

        difference = data.counted_cash - expected_cash

        cash_register.closed_at = func.now()
        cash_register.closed_by_id = user_id
        cash_register.is_open = False
        cash_register.total_sales = total_sales
        cash_register.closing_amount = closing_amount
        cash_register.expected_cash = expected_cash
        cash_register.counted_cash = data.counted_cash
        cash_register.difference = difference
        cash_register.payments_snapshot = decimal_dict_to_float(payment_breakdown)
        logger.info("Caja cerrada r=%s user=%s difference=%s", restaurant_id, user_id, difference)
        self.db.commit()
        return CashRegisterCloseOut(
            message="Caja cerrada",
            opening_amount=cash_register.opening_amount,
            closing_amount=cash_register.closing_amount,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=payment_breakdown,
            cash_in=cash_in,
            cash_out=cash_out,
            expected_cash=expected_cash,
            counted_cash=data.counted_cash,
            difference=difference
        )

    # --------------------------------------------------------------------------------
    # Devolver caja registradora actual
    # --------------------------------------------------------------------------------
    def get_current_cash_register(self, restaurant_id: int) -> CashRegisterSummary:
        cash_register = self.get_open_cash_register(restaurant_id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            cash_register.id
        )
        return CashRegisterSummary(
            cash_register_id=cash_register.id,
            opened_at=cash_register.opened_at,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=by_method
        )

    # --------------------------------------------------------------------------------
    # Devolver dashboard
    # --------------------------------------------------------------------------------
    def get_dashboard(self, restaurant_id: int) -> CashRegisterDashboard:
        cash_register = self.get_open_cash_register(restaurant_id)
        logger.debug("get_dashboard cash_register_id=%s", cash_register.id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            cash_register.id
        )
        cash_in, cash_out = self._calculate_cash_movements(
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
        movements = self.db.query(CashMovement).filter(
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
        logger.debug(
            "get_dashboard r=%s opening=%s sales=%s orders=%s",
            cash_register.restaurant_id,
            cash_register.opening_amount,
            total_sales,
            orders_count
        )
        return CashRegisterDashboard(
            cash_register_id=cash_register.id,
            opened_at=cash_register.opened_at,
            opening_amount=cash_register.opening_amount,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=by_method,
            cash_movements=movements_list,
            expected_cash=expected_cash
        )
```

---

### .\backend\app\domain\cash_register\dependencies.py

**Funciones (2):**
- get_cash_register_service
- get_cash_movement_service

**Clases (0):**

**Imports (5):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.cash_register.cash_movement_service.CashMovementService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService

def get_cash_register_service(
    db: Session = Depends(get_db)
) -> CashRegisterService:
    return CashRegisterService(db)


def get_cash_movement_service(
    db: Session = Depends(get_db)
) -> CashMovementService:
    return CashMovementService(db)
```

---

### .\backend\app\domain\category\category_service.py

**Funciones (8):**
- __init__
- _get_category
- _category_name_exists
- list_categories
- create_category
- update_category
- toggle_category
- list_categories_with_products

**Clases (1):**
- CategoryService

**Imports (10):**
- logging
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.category.Category
- app.schemas.category.CategoryCreate
- app.schemas.category.CategoryUpdate
- app.schemas.category.CategoryWithProducts
- app.schemas.category.ProductRef

```python
import logging

from sqlalchemy.orm import Session, joinedload

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.category import Category

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryWithProducts
)
from app.schemas.category import ProductRef

logger = logging.getLogger("app.domain.category")

class CategoryService:

    """
    Servicio encargado de la lógica de negocio relacionada con las categorías.

    Responsabilidades:
    - Gestionar el CRUD de categorías.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------
    # Obtener una categoría del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == restaurant_id
            )
            .first()
        )
        if not category:
            raise DomainError(
                "Category not found",
                ErrorCode.CATEGORY_NOT_FOUND
            )
        return category

    # --------------------------------------------------------------------------------
    # Encontrar categoría por nombre
    # --------------------------------------------------------------------------------
    def _category_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(Category)
            .filter(
                Category.restaurant_id == restaurant_id,
                Category.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)
        return query.first() is not None
    
    # -------------------------
    # Listar categorías
    # -------------------------
    def list_categories(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[Category]:
        query = (
            self.db.query(Category)
            .filter(Category.restaurant_id == restaurant_id)
        )
        if active is not None:
            query = query.filter(Category.active == active)
        return query.order_by(Category.name).all()

    # -------------------------
    # Crear categoría
    # -------------------------
    def create_category(
        self,
        restaurant_id: int,
        data: CategoryCreate
    ) -> Category:
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Category name cannot be empty",
                ErrorCode.INVALID_CATEGORY_NAME
            )
        existing = self._category_name_exists(restaurant_id, name)
        if existing:
            raise DomainError(
                "Category already exists",
                ErrorCode.CATEGORY_ALREADY_EXISTS
            )
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
    def update_category(
        self,
        restaurant_id: int,
        category_id: int,
        data: CategoryUpdate
    ) -> Category:
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Category name cannot be empty",
                ErrorCode.INVALID_CATEGORY_NAME
            )
        existing = self._category_name_exists(restaurant_id, name, exclude_id=category_id)
        if existing:
            raise DomainError(
                "Category already exists",
                ErrorCode.CATEGORY_ALREADY_EXISTS
            )
        category = self._get_category(restaurant_id, category_id)
        category.name = name
        self.db.commit()
        self.db.refresh(category)
        return category

    # --------------------------------------------
    # Activar o desactivar categoría
    # --------------------------------------------
    def toggle_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = self._get_category(restaurant_id, category_id)
        category.active = not category.active
        self.db.commit()
        self.db.refresh(category)
        logger.info(
            "Categoría alternada r=%s category_id=%s active=%s",
            restaurant_id,
            category.id,
            category.active
        )
        return category

    # --------------------------------------------
    # Listar categorías con productos activos
    # --------------------------------------------
    def list_categories_with_products(
        self,
        restaurant_id: int
    ) -> list[CategoryWithProducts]:
        categories = (
            self.db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.restaurant_id == restaurant_id)
            .filter(Category.active.is_(True))
            .order_by(Category.name)
            .all()
        )
        return [
            CategoryWithProducts(
                id=c.id,
                name=c.name,
                active=c.active,
                products=[
                    ProductRef(
                        id=p.id,
                        name=p.name,
                        price=p.price
                    )
                    for p in c.products
                    if p.active
                ]
            )
            for c in categories
        ]
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

### .\backend\app\domain\errors\base.py

**Funciones (1):**
- __init__

**Clases (1):**
- DomainError

**Imports (1):**
- typing.Any

```python
from typing import Any

class DomainError(Exception):

    message: str
    code: str
    context: dict[str, Any]

    def __init__(
        self,
        message: str,
        code: str = "domain_error",
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)
```

---

### .\backend\app\domain\errors\error_codes.py

**Funciones (0):**

**Clases (1):**
- ErrorCode

**Imports (1):**
- enum.Enum

```python
from enum import Enum

class ErrorCode(str, Enum):

    # GENERALES
    NOT_FOUND = "not_found"
    INVALID_OPERATION = "invalid_operation"
    UNAUTHORIZED = "unauthorized"

    # ORDERS
    ORDER_NOT_FOUND = "order_not_found"
    ORDER_ALREADY_CLOSED = "order_already_closed"
    ORDER_ALREADY_CANCELLED = "order_already_cancelled"
    ORDER_ITEMS_NOT_DELIVERED = "order_items_not_delivered"
    ORDER_EMPTY = "order_empty"
    ORDER_HAS_REMAINING_BALANCE = "order_has_remaining_balance"
    INVALID_TRANSITION = "invalid_transition"

    # ORDER ITEMS
    ITEM_NOT_FOUND = "item_not_found"
    ITEM_NOT_IN_ORDER = "item_not_in_order"
    ITEM_ALREADY_SENT = "item_already_sent"
    NOT_PENDING_ITEMS_TO_SEND = "not_pending_items_to_send"
    ITEM_STATUS_ROLE_FORBIDDEN = "item_status_role_forbidden"
    ITEM_INVALID_TRANSITION = "item_invalid_transition"

    # TABLES
    TABLE_NOT_FOUND = "table_not_found"
    TABLE_NUMBER_ALREADY_EXISTS = "table_number_already_exists"

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
    PRODUCT_ALREADY_EXISTS = "product_already_exists"
    INVALID_PRODUCT_NAME = "invalid_product_name"

    # USERS
    USER_NOT_FOUND = "user_not_found"
    USERNAME_ALREADY_EXISTS = "username_already_exists"
    USER_CANNOT_DEACTIVATE_SELF = "user_cannot_deactivate_self"

    # CATEGORIES
    CATEGORY_NOT_FOUND = "category_not_found"
    CATEGORY_ALREADY_EXISTS = "category_already_exists"
    INVALID_CATEGORY_NAME = "invalid_category_name"

    # STATIONS
    STATION_NOT_FOUND = "station_not_found"
    STATION_NAME_ALREADY_EXISTS = "station_name_already_exists"
    INVALID_STATION_NAME = "invalid_station_name"

    # LAYOUT
    LAYOUT_BACKGROUND_INVALID_FORMAT = "layout_background_invalid_format"
    LAYOUT_BACKGROUND_TOO_LARGE = "layout_background_too_large"

    # PERMISSIONS
    PERMISSION_DENIED = "permission_denied"

    # EMAIL Y BACKUP
    INVALID_BACKUP_CONFIGURATION = "invalid_backup_configuration"
    EMAIL_NOT_CONFIGURED = "email_not_configured"
    SMTP_NOT_CONFIGURED = "smtp_not_configured"
    SMTP_HOST_NOT_CONFIGURED = "smtp_host_not_configured"
    BACKUP_EMAIL_NOT_CONFIGURED = "backup_email_not_configured"
    EMAIL_SEND_FAILURE = "email_send_failure"
    BACKUP_NOT_FOUND = "backup_not_found"
    BACKUP_INVALID_PATH = "backup_invalid_path"
    BACKUP_DATABASE_NOT_FOUND = "backup_database_not_found"
    BACKUP_ENGINE_NOT_SUPPORTED = "backup_engine_not_supported"
    BACKUP_FAILED = "backup_failed"

    # REPORTS
    REPORT_INVALID_DATE_RANGE = "report_invalid_date_range"

    #SETTINGS
    BACKUP_DESTINATION_REQUIRED = "backup_destination_required"
    BACKUP_WEEKDAY_REQUIRED = "backup_weekday_required"
    BACKUP_MONTHDAY_REQUIRED = "backup_monthday_required"

    # AUTH
    INVALID_TOKEN = "invalid_token"
    INVALID_TOKEN_PAYLOAD = "invalid_token_payload"
    USER_INACTIVE = "user_inactive"
    ROLE_MISMATCH = "role_mismatch"
```

---

### .\backend\app\domain\events\websocket.py

**Funciones (0):**

**Clases (1):**
- WSEvent

**Imports (1):**
- enum.StrEnum

```python
from enum import StrEnum

class WSEvent(StrEnum):
    # -------------------------------------------------------------------------
    # Caja
    # -------------------------------------------------------------------------
    CASH_REGISTER_UPDATED = "CASH_REGISTER_UPDATED"
    CASH_MOVEMENT_ADDED = "CASH_MOVEMENT_ADDED"
    CASH_MOVEMENT_DELETED = "CASH_MOVEMENT_DELETED"

    # -------------------------------------------------------------------------
    # Órdenes
    # -------------------------------------------------------------------------
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_STATUS_CHANGED = "ORDER_STATUS_CHANGED"
    ORDER_CLOSED = "ORDER_CLOSED"

    # -------------------------------------------------------------------------
    # Items
    # -------------------------------------------------------------------------
    ITEM_STATUS_CHANGED = "ITEM_STATUS_CHANGED"
    NEW_ITEM = "NEW_ITEM"
    ITEM_READY = "ITEM_READY"

    # -------------------------------------------------------------------------
    # Pagos
    # -------------------------------------------------------------------------
    PAYMENT_ADDED = "PAYMENT_ADDED"
    PAYMENT_DELETED = "PAYMENT_DELETED"

    # -------------------------------------------------------------------------
    # Mesas
    # -------------------------------------------------------------------------
    TABLE_CREATED = "TABLE_CREATED"
    TABLE_UPDATED = "TABLE_UPDATED"
    TABLE_POSITION_UPDATED = "TABLE_POSITION_UPDATED"
    TABLE_ACTIVATED = "TABLE_ACTIVATED"
    TABLE_DEACTIVATED = "TABLE_DEACTIVATED"

    # -------------------------------------------------------------------------
    # Layout
    # -------------------------------------------------------------------------
    LAYOUT_UPDATED = "LAYOUT_UPDATED"
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

**Funciones (2):**
- __init__
- get_station_items

**Clases (1):**
- KitchenService

**Imports (7):**
- sqlalchemy.orm.Session
- app.models.user.User
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.order.Order
- app.schemas.order.kitchen.KitchenItemOut

```python
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order

from app.schemas.order.kitchen import KitchenItemOut

class KitchenService:
    """
    Servicio encargado de la lógica de negocio relacionada con la cocina.

    Responsabilidades:
    - Devolver items a pedido
    - Acceder a la base de datos mediante SQLAlchemy.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------------------------
    # Obtener los items de una estación, filtrando por estado y restaurante
    # -------------------------------------------------------------------------
    def get_station_items(
        self,
        station_id: int,
        user: User
    ) -> list[KitchenItemOut]:
        items = (
            self.db.query(OrderItem)
            .join(OrderItem.product)
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
            .order_by(Order.created_at, OrderItem.id)
            .all()
        )
        return [
            KitchenItemOut(
                item_id=item.id,
                product_name=item.product.name,
                quantity=item.quantity,
                status=item.status,
                table_number=item.order.table.number,
                order_id=item.order.id,
                notes=item.notes
            )
            for item in items
        ]
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

**Funciones (6):**
- __init__
- _validate_background_image
- _save_background_image
- get_layout
- update_layout
- update_background_image

**Clases (1):**
- LayoutService

**Imports (11):**
- logging
- pathlib.Path
- uuid.uuid4
- fastapi.UploadFile
- sqlalchemy.orm.Session
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.domain.events.websocket.WSEvent
- app.services.event_service.EventService
- app.models.restaurant_layout.RestaurantLayout
- app.schemas.layout.LayoutUpdate

```python
import logging

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.models.restaurant_layout import RestaurantLayout

from app.schemas.layout import LayoutUpdate

logger = logging.getLogger("app.domain.layout")

class LayoutService:

    """
    Servicio encargado de la lógica de negocio relacionada con el diseño del restaurante.

    Responsabilidades:
    - Gestionar la lógica de negocio del diseño del restaurante.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # --------------------------------------------------------------------------------------
    # Validar imagen de fondo
    # --------------------------------------------------------------------------------------
    async def _validate_background_image(
        self,
        file: UploadFile
    ) -> tuple[bytes, str]:
        allowed_types = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }
        extension = allowed_types.get(file.content_type or "")
        if not extension:
            raise DomainError(
                "Invalid image format. Allowed formats: JPEG, PNG, WEBP, GIF.",
                ErrorCode.LAYOUT_BACKGROUND_INVALID_FORMAT
            )
        content = await file.read()
        max_size = 8 * 1024 * 1024
        if len(content) > max_size:
            raise DomainError(
                "The image cannot exceed 8 MB.",
                ErrorCode.LAYOUT_BACKGROUND_TOO_LARGE
            )
        return content, extension

    # --------------------------------------------------------------------------------------
    # Guardar imagen de fondo
    # --------------------------------------------------------------------------------------
    def _save_background_image(
        self,
        restaurant_id: int,
        content: bytes,
        extension: str
    ) -> str:
        upload_root = (
            Path(__file__).resolve().parents[3]
            / "uploads"
            / "layouts"
        )
        restaurant_dir = upload_root / str(restaurant_id)
        restaurant_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        filename = f"{uuid4().hex}{extension}"
        destination = restaurant_dir / filename
        try:
            destination.write_bytes(content)
        except OSError:
            logger.exception(
                "No se pudo guardar la imagen de fondo del layout. "
                "restaurant_id=%s",
                restaurant_id
            )
            raise
        return f"/uploads/layouts/{restaurant_id}/{filename}"

    # --------------------------------------------------------------------------------------
    # Devuelve el diseño del restaurante, si no existe lo crea con valores por defecto
    # --------------------------------------------------------------------------------------
    def get_layout(self, restaurant_id: int) -> RestaurantLayout:
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

    # --------------------------------------------------------------------------------------
    # Actualiza el diseño del restaurante
    # --------------------------------------------------------------------------------------
    def update_layout(self, restaurant_id: int, data: LayoutUpdate) -> RestaurantLayout:
        logger.info("Layout actualizado r=%s", restaurant_id)
        layout = self.get_layout(restaurant_id)
        layout.width = data.width
        layout.height = data.height
        layout.grid_size = data.grid_size
        layout.snap_to_grid = data.snap_to_grid
        if data.background_image is not None:
            layout.background_image = data.background_image
        self.db.refresh(layout)
        self.events.emit(
                restaurant_id=restaurant_id,
                event_type=WSEvent.LAYOUT_UPDATED,
                payload={"restaurant_id": restaurant_id}
            )
        self.db.commit()
        return layout

    # --------------------------------------------------------------------------------------
    # Actualiza la imagen de fondo del diseño del restaurante
    # --------------------------------------------------------------------------------------
    async def update_background_image(
        self,
        restaurant_id: int,
        file: UploadFile
    ) -> RestaurantLayout:
        logger.info(
            "Background del layout actualizado r=%s",
            restaurant_id
        )
        content, extension = await self._validate_background_image(file)
        background_image = self._save_background_image(
            restaurant_id,
            content,
            extension
        )
        layout = self.get_layout(restaurant_id)
        layout.background_image = background_image
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.LAYOUT_UPDATED,
            payload={
                "restaurant_id": restaurant_id
            }
        )
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

**Funciones (20):**
- __init__
- _get_active_orders
- _get_active_order
- _calculate_totals
- _calculate_order_status
- _set_status
- get_order
- to_order_response
- to_order_response_list
- apply_discount
- add_item
- add_product_to_order
- update_status
- send_to_kitchen
- add_payment
- delete_payment
- close_order
- cancel_order
- delete_order_item
- update_item_quantity

**Clases (1):**
- OrderService

**Imports (29):**
- logging
- decimal.Decimal
- decimal.ROUND_HALF_UP
- datetime.datetime
- datetime.timezone
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- sqlalchemy.func
- app.domain.order.order_transitions.is_valid_order_transition
- app.domain.order.constants.ACTIVE_ORDER_STATUSES
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.domain.events.websocket.WSEvent
- app.services.event_service.EventService
- app.utils.money.money
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.models.user.UserRole
- app.models.payment.Payment
- app.models.table.Table
- app.schemas.order.order.OrderResponse
- app.schemas.order.order_item.OrderItemCreate
- app.schemas.order.order_item.OrderItemOut
- app.schemas.order.payment.PaymentCreate
- app.schemas.order.payment.PaymentOut
- app.domain.cash_register.cash_register_service.CashRegisterService

```python
import logging

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.domain.order.order_transitions import is_valid_order_transition
from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.utils.money import money

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.user import UserRole
from app.models.payment import Payment
from app.models.table import Table

from app.schemas.order.order import OrderResponse
from app.schemas.order.order_item import (
    OrderItemCreate,
    OrderItemOut
)
from app.schemas.order.payment import (
    PaymentCreate,
    PaymentOut
)

logger = logging.getLogger("app.domain.order")

class OrderService:

    """
    Servicio encargado de la lógica de negocio relacionada con las ordenes.

    Responsabilidades:
    - Gestionar el ciclo de vida de las órdenes.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # -------------------------
    # Obtener ordenes activas
    # -------------------------
    def _get_active_orders(self, restaurant_id: int) -> list[Order]:
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

    # -------------------------
    # Obtener orden activa por mesa
    # -------------------------
    def _get_active_order(self, restaurant_id: int, table_id: int) -> Order:
        return (
            self.db.query(Order)
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.table_id == table_id,
                Order.status.in_(ACTIVE_ORDER_STATUSES)
            )
            .first()
        )

    # -------------------------
    # Calcular totales de la orden
    # -------------------------
    def _calculate_totals(self, order: Order) -> tuple[Decimal, Decimal, Decimal, Decimal]: 
        active_items = [
            item
            for item in order.items
            if item.status != OrderItemStatus.CANCELLED
        ]
        subtotal = sum((item.quantity * item.unit_price for item in active_items), Decimal("0"))
        discount = order.discount or Decimal("0")
        total = max(subtotal - discount, Decimal("0"))
        total_paid = sum((payment.amount for payment in order.payments), Decimal("0"))
        remaining = total - total_paid
        return subtotal, total, total_paid, remaining

    # -------------------------
    # Calcular estado de la orden basado en estados de los items
    # -------------------------
    def _calculate_order_status(self, order: Order) -> OrderStatus:
        active_items = [
            i for i in order.items
            if i.status != OrderItemStatus.CANCELLED
        ]
        if not active_items:
            if order.status not in (
                OrderStatus.CLOSED,
                OrderStatus.CANCELLED
            ):
                return OrderStatus.CANCELLED
            return order.status
        statuses = [i.status for i in active_items]
        if any(s == OrderItemStatus.IN_PROGRESS for s in statuses):
            return OrderStatus.IN_PROGRESS
        if any(s == OrderItemStatus.SENT for s in statuses):
            return OrderStatus.SENT
        if any(s == OrderItemStatus.PENDING for s in statuses):
            return OrderStatus.OPEN
        if all(
            s in (OrderItemStatus.READY, OrderItemStatus.DELIVERED)
            for s in statuses
        ):
            return OrderStatus.READY
        return order.status

    # -------------------------
    # Cambiar estado de la orden si es diferente al actual
    # -------------------------
    def _set_status(self, order: Order, new_status: OrderStatus) -> bool:
        if order.status == new_status:
            return False
        if not is_valid_order_transition(order.status, new_status):
            raise DomainError(
                "Invalid order status transition",
                ErrorCode.INVALID_TRANSITION,
                context={
                    "from": order.status.value,
                    "to": new_status.value,
                    "order_id": order.id
                }
            )
        order.status = new_status
        return True

    # -------------------------
    # Obtener orden por id
    # -------------------------
    def get_order(self, order_id: int, restaurant_id: int) -> Order:
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
            raise DomainError(
                "Orden no encontrada",
                ErrorCode.ORDER_NOT_FOUND
            )
        return order

    # -------------------------------------------------------------------------------------------------
    # Devolver orden con items, pagos, subtotal, descuento, totales y remanentes
    # -------------------------------------------------------------------------------------------------
    def to_order_response(
        self,
        order: Order
    ) -> OrderResponse:
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        return OrderResponse(
            id=order.id,
            table_id=order.table_id,
            table_number=order.table.number,
            status=order.status,
            created_at=order.created_at,
            items=[
                OrderItemOut(
                    id=item.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=money(item.unit_price),
                    subtotal=money(item.quantity * item.unit_price),
                    status=item.status,
                    notes=item.notes
                )
                for item in order.items
            ],
            payments=[
                PaymentOut(
                    id=payment.id,
                    amount=money(payment.amount),
                    method=payment.method
                )
                for payment in order.payments
            ],
            subtotal=money(subtotal),
            discount=money(order.discount or 0),
            total=money(total),
            total_paid=money(total_paid),
            remaining=money(remaining)
        )

    # -------------------------------------------------------------------------------------------------
    # Devolver lista de órdenes activas con items, pagos, subtotal, descuento, totales y remanentes
    # -------------------------------------------------------------------------------------------------
    def to_order_response_list(
        self,
        restaurant_id: int
    ) -> list[OrderResponse]:
        orders = self._get_active_orders(restaurant_id)
        return [
            self.to_order_response(order)
            for order in orders
        ]

    # -------------------------
    # Aplicar descuento a la orden
    # -------------------------
    def apply_discount(self, order: Order, discount: Decimal) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot apply discount to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "Cannot apply discount to cancelled order",
                ErrorCode.INVALID_OPERATION
            )
        discount = discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal, _, total_paid, _ = self._calculate_totals(order)
        if discount > subtotal:
            raise DomainError(
                "Discount cannot exceed order subtotal",
                ErrorCode.INVALID_OPERATION,
                context={
                    "discount": money(discount),
                    "subtotal": money(subtotal)
                }
            )
        new_total = subtotal - discount
        if new_total < total_paid:
            raise DomainError(
                "Discount would make paid amount exceed order total",
                ErrorCode.INVALID_OPERATION,
                context={
                    "discount": money(discount),
                    "new_total": money(new_total),
                    "total_paid": money(total_paid)
                }
            )
        logger.info("Descuento aplicado order_id=%s discount=%s", order.id, discount)
        order.discount = discount
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Crear / agregar items
    # -------------------------
    def add_item(self, order: Order, data: OrderItemCreate) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot add items to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "Cannot add items to cancelled order",
                ErrorCode.ORDER_ALREADY_CANCELLED
            )
        if data.quantity <= 0:
            raise DomainError(
                "Quantity must be greater than zero",
                ErrorCode.INVALID_OPERATION
            )
        product = (
            self.db.query(Product)
            .filter(
                Product.id == data.product_id,
                Product.restaurant_id == order.restaurant_id,
                Product.active
            )
            .first()
        )
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": data.product_id}
            )
        
        previous_status = order.status
        notes = (data.notes.strip() if data.notes else None)

        existing_item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id,
                OrderItem.product_id == product.id,
                OrderItem.status == OrderItemStatus.PENDING,
                OrderItem.notes == notes
            )
            .first()
        )
        if existing_item:
            existing_item.quantity += data.quantity
            item = existing_item
        else:
            item = OrderItem(
                restaurant_id=order.restaurant_id,
                order_id=order.id,
                product_id=product.id,
                quantity=data.quantity,
                unit_price=product.price,
                status=OrderItemStatus.PENDING,
                notes=data.notes
            )
            self.db.add(item)        
        self.db.flush()
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        # =========================
        # 🔔 EVENTOS
        # =========================
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.NEW_ITEM,
            payload={"order_id": order.id},
            target="station",
            target_id=str(product.station_id)
        )
        if order.status != previous_status:
            for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={"order_id": order.id, "status": order.status.value},
                    target="role",
                    target_id=role.value
                )
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            logger.debug("ORDER_UPDATED emit order_id=%s", order.id)
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Agregar producto a la mesa (crear orden si no existe)
    # -------------------------
    def add_product_to_order(self, restaurant_id: int, table_id: int, data: OrderItemCreate):
        table = self.db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table:
            raise DomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND
            )
        order = self._get_active_order(restaurant_id, table_id)
        if not order:
            order = Order(table_id=table_id, restaurant_id=restaurant_id, status=OrderStatus.OPEN)
            self.db.add(order)
            self.db.flush()
        item = self.add_item(order, data)
        return {"order_id": order.id}

    # -------------------------
    # Actualizar estado de la orden
    # -------------------------
    def update_status(self, order: Order, new_status: OrderStatus) -> OrderResponse:
        if order.status == new_status:
            return self.to_order_response(order)
        previous_status = order.status
        if self._set_status(order, new_status):
            logger.info(
                "Estado de orden actualizado order_id=%s from=%s to=%s",
                order.id, previous_status.value, new_status.value
            )
            for role in [UserRole.ADMIN, UserRole.WAITER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={"order_id": order.id, "status": new_status.value},
                    target="role",
                    target_id=role.value
                )
            self.db.commit()
            self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Enviar a cocina
    # -------------------------
    def send_to_kitchen(self, order: Order) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError("Order is closed", ErrorCode.ORDER_ALREADY_CLOSED)
        
        if order.status == OrderStatus.CANCELLED:
            raise DomainError("Order is cancelled", ErrorCode.ORDER_ALREADY_CANCELLED)
        pending_items = [
            item
            for item in order.items
            if item.status == OrderItemStatus.PENDING
        ]
        if not pending_items:
            raise DomainError(
                "No pending items to send",
                ErrorCode.NO_PENDING_ITEMS_TO_SEND
            )
        previous_status = order.status

        # --------------------------------------------------
        # Actualizar ítems pendientes
        # --------------------------------------------------
        for item in pending_items:
            item.status = OrderItemStatus.SENT

        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)

        logger.info(
            "Orden enviada a cocina order_id=%s r=%s",
            order.id,
            order.restaurant_id
        )

        # --------------------------------------------------
        # Notificar a las estaciones involucradas
        # --------------------------------------------------
        station_ids = {
            item.product.station_id
            for item in pending_items
        }

        for station_id in station_ids:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={
                    "order_id": order.id
                },
                target="station",
                target_id=str(station_id)
            )

        # --------------------------------------------------
        # Notificar cambio de estado de la orden
        # --------------------------------------------------
        if order.status != previous_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER
            ]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )
        # --------------------------------------------------
        # Un único commit:
        #
        # - cambios de la orden
        # - cambios de los ítems
        # - eventos EventOutbox
        #
        # quedan en la misma transacción.
        # --------------------------------------------------
        self.db.commit()
        self.db.refresh(order)

        return self.to_order_response(order)

    # -------------------------
    # Agregar pago
    # -------------------------
    def add_payment(self, order: Order, data: PaymentCreate) -> Payment:
        from app.domain.cash_register.cash_register_service import CashRegisterService
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Order already closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "Order already cancelled",
                ErrorCode.ORDER_ALREADY_CANCELLED
            )
        cash_service = CashRegisterService(self.db)
        cash_register = cash_service.get_open_cash_register(order.restaurant_id)
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        if data.amount > remaining:
            raise DomainError(
                "Payment exceeds remaining balance",
                ErrorCode.PAYMENT_EXCEEDS_REMAINING,
                context={
                    "amount": money(data.amount),
                    "remaining": money(remaining)
                }
            )
        logger.info("Pago agregado order_id=%s amount=%s method=%s", order.id, data.amount, data.method)
        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=data.amount,
            method=data.method,
            cash_register_id=cash_register.id
        )
        self.db.add(payment)
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.PAYMENT_ADDED,
                payload={"order_id": order.id, "amount": money(data.amount), "method": data.method},
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.CASH_REGISTER_UPDATED,
            payload={"order_id": order.id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # -------------------------
    # Borrar pago
    # -------------------------
    def delete_payment(self, restaurant_id: int, payment_id: int):
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.restaurant_id == restaurant_id
            )
            .first()
        )

        if not payment:
            raise DomainError("Pago no encontrado", ErrorCode.PAYMENT_NOT_FOUND)

        if payment.order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot delete payment from closed order",
                ErrorCode.INVALID_OPERATION
            )
        if payment.order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "Cannot delete payment from cancelled order",
                ErrorCode.INVALID_OPERATION
            )        
        logger.info("Pago eliminado order_id=%s amount=%s method=%s", payment.order_id, payment.amount, payment.method)
        order_id = payment.order_id
        amount = payment.amount
        method = payment.method
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=restaurant_id,
                event_type=WSEvent.PAYMENT_DELETED,
                payload={
                    "order_id": order_id,
                    "amount": money(amount),
                    "method": method
                },
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.CASH_REGISTER_UPDATED,
            payload={"order_id": order_id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.delete(payment)
        self.db.commit()
        return {"deleted": payment_id}

    # -------------------------
    # Cerrar orden
    # -------------------------
    def close_order(self, order: Order) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError("La orden ya está cerrada", ErrorCode.ORDER_ALREADY_CLOSED)
        if order.status == OrderStatus.CANCELLED:
            raise DomainError("La orden está cancelada", ErrorCode.ORDER_ALREADY_CANCELLED)
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        if remaining > 0:
            raise DomainError(
                f"La orden no está paga. Saldo: {remaining:.2f}",
                ErrorCode.ORDER_HAS_REMAINING_BALANCE,
                context={"remaining": money(remaining)}
            )
        active_items = [
            item
            for item in order.items
            if item.status != OrderItemStatus.CANCELLED
        ]

        if not active_items:
            raise DomainError(
                "La orden no tiene items activos",
                ErrorCode.ORDER_EMPTY
            )
        not_delivered = [
            i for i in order.items
            if i.status not in [OrderItemStatus.DELIVERED, OrderItemStatus.CANCELLED]
        ]
        if not_delivered:
            raise DomainError(
                "No se puede cerrar la orden. Hay items no entregados",
                ErrorCode.ORDER_ITEMS_NOT_DELIVERED,
                context={"items": [i.id for i in not_delivered]}
            )
        logger.info("Orden cerrada order_id=%s r=%s total=%s", order.id, order.restaurant_id, total)
        self._set_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()
        # Emitir evento
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_CLOSED,
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.CASH_REGISTER_UPDATED,
            payload={"order_id": order.id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Cancelar orden
    # -------------------------
    def cancel_order(self, order: Order, user_id: int, reason: str) -> OrderResponse:
        reason = reason.strip()
        if not reason:
            raise DomainError(
                "Debe indicar un motivo para cancelar la orden",
                ErrorCode.INVALID_OPERATION,
                context={
                    "order_id": order.id
                }
            )

        # --------------------------------------------------
        # Estados finales
        # --------------------------------------------------
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "No se puede cancelar una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={
                    "order_id": order.id
                }
            )

        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "La orden ya está cancelada",
                ErrorCode.ORDER_ALREADY_CANCELLED,
                context={
                    "order_id": order.id
                }
            )

        # --------------------------------------------------
        # No permitimos cancelar una orden que ya tenga
        # items entregados.
        #
        # Una devolución posterior a la entrega deberá
        # modelarse como otra operación.
        # --------------------------------------------------
        delivered_items = [
            item
            for item in order.items
            if item.status == OrderItemStatus.DELIVERED
        ]

        if delivered_items:
            raise DomainError(
                (
                    "No se puede cancelar la orden porque "
                    "contiene items entregados"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "order_id": order.id,
                    "items": [
                        item.id
                        for item in delivered_items
                    ]
                }
            )

        # --------------------------------------------------
        # Validación financiera
        #
        # La cancelación completa deja el total en cero.
        # Por lo tanto no puede haber pagos registrados.
        # --------------------------------------------------
        _, _, total_paid, _ = (
            self._calculate_totals(order)
        )

        if total_paid > Decimal("0"):
            raise DomainError(
                (
                    "No se puede cancelar la orden mientras "
                    "tenga pagos registrados"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "order_id": order.id,
                    "total_paid": money(total_paid)
                }
            )

        cancelled_at = datetime.now(timezone.utc)

        # --------------------------------------------------
        # Cancelar todos los items activos.
        #
        # En una cancelación completa preservamos también
        # los PENDING porque forman parte del historial
        # de la orden cancelada.
        # --------------------------------------------------
        items_to_cancel = [
            item
            for item in order.items
            if item.status != OrderItemStatus.CANCELLED
        ]

        affected_station_ids = set()

        for item in items_to_cancel:

            item.status = OrderItemStatus.CANCELLED

            item.cancelled_at = cancelled_at
            item.cancelled_by_id = user_id
            item.cancellation_reason = reason

            if item.product.station_id is not None:
                affected_station_ids.add(
                    item.product.station_id
                )

        # --------------------------------------------------
        # Cancelar orden
        # --------------------------------------------------
        previous_status = order.status

        self._set_status(
            order,
            OrderStatus.CANCELLED
        )

        order.cancelled_at = cancelled_at
        order.cancelled_by_id = user_id
        order.cancellation_reason = reason

        logger.info(
            (
                "Orden cancelada "
                "order_id=%s user_id=%s reason=%s"
            ),
            order.id,
            user_id,
            reason
        )

        # ==================================================
        # EVENTOS
        # ==================================================

        # --------------------------------------------------
        # Cocina
        #
        # Un único ORDER_UPDATED por estación es suficiente
        # para que cada estación vuelva a obtener su estado.
        # --------------------------------------------------
        for station_id in affected_station_ids:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={
                    "order_id": order.id
                },
                target="station",
                target_id=str(station_id)
            )

        # --------------------------------------------------
        # Salón / administración / caja
        # --------------------------------------------------
        for role in [
            UserRole.ADMIN,
            UserRole.WAITER,
            UserRole.CASHIER
        ]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_STATUS_CHANGED,
                payload={
                    "order_id": order.id,
                    "status": order.status.value
                },
                target="role",
                target_id=role.value
            )

            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={
                    "order_id": order.id
                },
                target="role",
                target_id=role.value
            )

        # --------------------------------------------------
        # Un único commit:
        #
        # - cancelación de items
        # - cancelación de orden
        # - datos de auditoría
        # - eventos Outbox
        # todo dentro de la misma transacción.
        # --------------------------------------------------
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Eliminar item de la orden
    # -------------------------
    def delete_order_item(
        self,
        restaurant_id: int,
        order_id: int,
        item_id: int,
    ) -> OrderResponse:
        item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.id == item_id,
                OrderItem.restaurant_id == restaurant_id
            )
            .first()
        )
        if not item:
            raise DomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"item": item_id}
            )
        if item.order_id != order_id:
            raise DomainError(
                "Item no pertenece a la orden",
                ErrorCode.ITEM_NOT_IN_ORDER,
                context={
                    "item": item_id,
                    "order_id": order_id
                }
            )       
        if item.status != OrderItemStatus.PENDING:
            raise DomainError(
                "El item ya fue enviado a la cocina",
                ErrorCode.ITEM_ALREADY_SENT,
                context={"item": item.id}
            )

        order = item.order
        previous_status = order.status

        self.db.delete(item)
        self.db.flush()
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        logger.info("Item eliminado order_id=%s item_id=%s", order_id, item_id)

        # 🔔 EVENTO
        if order.status != previous_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER,
                UserRole.CASHIER
            ]:
                self.events.emit(
                    restaurant_id=restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )


        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={"order_id": order_id},
                target="role",
                target_id=role.value
            )
            
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)
        
    # -------------------------
    # Actualizar cantidad por item de la orden
    # -------------------------
    def update_item_quantity(
        self,
        restaurant_id: int,
        item_id: int,
        quantity: int
    ) -> OrderResponse:
        item = (
            self.db.query(OrderItem)
            .join(Order)
            .filter(
                OrderItem.id == item_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )
        if not item:
            raise DomainError("order item not found", ErrorCode.ITEM_NOT_FOUND)
        order = item.order
        if item.status != OrderItemStatus.PENDING:
            raise DomainError(
                "cannot modify item already sent to kitchen",
                ErrorCode.ITEM_ALREADY_SENT
            )
        if quantity <= 0:
            return self.delete_order_item(
                restaurant_id,
                item.order_id,
                item.id
            )
        item.quantity = quantity
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)
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
        OrderStatus.CLOSED,
        OrderStatus.CANCELLED
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

**Funciones (5):**
- __init__
- _get_item
- _process_status_transition
- update_status
- cancel_item

**Clases (1):**
- OrderItemService

**Imports (18):**
- logging
- datetime.datetime
- datetime.timezone
- decimal.Decimal
- sqlalchemy.orm.Session
- app.domain.order.order_service.OrderService
- app.domain.order_item.order_item_transitions.can_transition
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.domain.events.websocket.WSEvent
- app.services.event_service.EventService
- app.utils.money.money
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.user.User
- app.models.user.UserRole
- app.models.order.OrderStatus
- app.schemas.order.order.OrderResponse

```python
import logging

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.utils.money import money

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

from app.schemas.order.order import OrderResponse

logger = logging.getLogger("app.domain.order_item")

class OrderItemService:

    """
    Servicio encargado de la lógica de negocio relacionada con los items de las ordenes.

    Responsabilidades:
    - Gestionar el ciclo de vida de las items.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # -------------------------
    # Obtener item
    # -------------------------
    def _get_item(self, item_id: int, restaurant_id: int) -> OrderItem:
        item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.id == item_id,
                OrderItem.restaurant_id == restaurant_id
            )
            .first()
        )
        if not item:
            raise DomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"item_id": item_id})
        return item

    # -----------------------------------------------------------------------------
    # Procesar transición de estado del item y recalcular estado de la orden
    # -----------------------------------------------------------------------------
    def _process_status_transition(
        self,
        item: OrderItem,
        new_status: OrderItemStatus,
        user: User,
        order_service: OrderService
    ) -> OrderStatus:

        order = item.order

        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "No se pueden modificar items en una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={"order_id": order.id}
            )

        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "No se pueden modificar items en una orden cancelada",
                ErrorCode.ORDER_ALREADY_CANCELLED,
                context={"order_id": order.id}
            )

        if (
            new_status == OrderItemStatus.IN_PROGRESS
            and user.role != UserRole.KITCHEN
        ):
            raise DomainError(
                "Sólo COCINA puede comenzar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if (
            new_status == OrderItemStatus.READY
            and user.role != UserRole.KITCHEN
        ):
            raise DomainError(
                "Sólo COCINA puede marcar items como listos",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if (
            new_status == OrderItemStatus.DELIVERED
            and user.role != UserRole.WAITER
        ):
            raise DomainError(
                "Sólo MOZO puede entregar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "WAITER"}
            )

        if (
            new_status == OrderItemStatus.CANCELLED
            and user.role not in (
                UserRole.WAITER,
                UserRole.ADMIN
            )
        ):
            raise DomainError(
                "Sólo MOZO o ADMIN puede cancelar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={
                    "required_roles": [
                        UserRole.WAITER.value,
                        UserRole.ADMIN.value
                    ]
                }
            )

        if not can_transition(
            item.status,
            new_status
        ):
            raise DomainError(
                (
                    f"Transición inválida desde "
                    f"{item.status.value} a {new_status.value}"
                ),
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "from": item.status.value,
                    "to": new_status.value
                }
            )
        item.status = new_status
        previous_status = order.status
        new_order_status = (order_service._calculate_order_status(order))
        order_service._set_status(order, new_order_status)
        return previous_status

    # -------------------------
    # Actualizar estado
    # -------------------------
    def update_status(
        self,
        item_id: int,
        new_status: OrderItemStatus,
        user: User
    ) -> OrderItem:

        if new_status == OrderItemStatus.CANCELLED:
            raise DomainError(
                "La cancelación de items debe realizarse mediante la operación específica de cancelación",
                ErrorCode.INVALID_OPERATION
            )

        item = self._get_item(
            item_id,
            user.restaurant_id
        )

        order = item.order

        order_service = OrderService(
            self.db
        )

        previous_status = (
            self._process_status_transition(
                item,
                new_status,
                user,
                order_service
            )
        )

        # ==================================================
        # EVENTOS
        # ==================================================

        payload = {
            "order_id": order.id,
            "item_id": item.id,
            "status": new_status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # --------------------------------------------------
        # Cocina
        # --------------------------------------------------
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.ITEM_STATUS_CHANGED,
            payload=payload,
            target="station",
            target_id=str(
                item.product.station_id
            )
        )

        # --------------------------------------------------
        # Salón / administración
        # --------------------------------------------------
        for role in [
            UserRole.ADMIN,
            UserRole.WAITER
        ]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_STATUS_CHANGED,
                payload=payload,
                target="role",
                target_id=role.value
            )

        # --------------------------------------------------
        # Ítem listo
        # --------------------------------------------------
        if new_status == OrderItemStatus.READY:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_READY,
                payload={
                    "order_id": order.id,
                    "table": order.table.number,
                    "product": item.product.name,
                    "quantity": item.quantity
                },
                target="role",
                target_id=UserRole.WAITER.value
            )

        # --------------------------------------------------
        # Cambio de estado general de la orden
        # --------------------------------------------------
        if order.status != previous_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER
            ]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )

        # --------------------------------------------------
        # Commit atómico:
        #
        # cambio del dominio + eventos Outbox.
        # --------------------------------------------------
        self.db.commit()
        self.db.refresh(item)
        return item

    # -------------------------
    # Cancelar item
    # -------------------------
    def cancel_item(
        self,
        item_id: int,
        reason: str,
        user: User
    ) -> OrderResponse:

        item = self._get_item(
            item_id,
            user.restaurant_id
        )

        order = item.order

        reason = reason.strip()

        if not reason:
            raise DomainError(
                "Debe indicar un motivo para cancelar el item",
                ErrorCode.INVALID_OPERATION,
                context={"item_id": item.id}
            )

        # --------------------------------------------------
        # La tabla de transiciones sigue siendo la fuente
        # de verdad respecto a qué estados pueden cancelarse.
        #
        # PENDING no admite CANCELLED: debe eliminarse.
        # DELIVERED y CANCELLED son estados finales.
        # --------------------------------------------------
        if not can_transition(
            item.status,
            OrderItemStatus.CANCELLED
        ):
            raise DomainError(
                (
                    f"No se puede cancelar un item "
                    f"en estado {item.status.value}"
                ),
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "item_id": item.id,
                    "from": item.status.value,
                    "to": OrderItemStatus.CANCELLED.value
                }
            )

        order_service = OrderService(self.db)

        # --------------------------------------------------
        # Validación financiera
        #
        # Cancelar el item reduce el subtotal y, por tanto,
        # puede dejar inválido un descuento existente o hacer
        # que lo ya pagado supere el nuevo total.
        # --------------------------------------------------
        subtotal, _, total_paid, _ = (
            order_service._calculate_totals(order)
        )

        item_amount = (
            item.quantity * item.unit_price
        )

        new_subtotal = (
            subtotal - item_amount
        )

        discount = (
            order.discount or Decimal("0")
        )

        if discount > new_subtotal:
            raise DomainError(
                (
                    "No se puede cancelar el item porque "
                    "el descuento de la orden superaría "
                    "el nuevo subtotal"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "item_id": item.id,
                    "new_subtotal": money(new_subtotal),
                    "discount": money(discount)
                }
            )

        new_total = max(
            new_subtotal - discount,
            Decimal("0")
        )

        if total_paid > new_total:
            raise DomainError(
                (
                    "No se puede cancelar el item porque "
                    "el monto pagado superaría el nuevo total"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "item_id": item.id,
                    "new_total": money(new_total),
                    "total_paid": money(total_paid)
                }
            )

        # --------------------------------------------------
        # Transición de estado.
        #
        # Acá se validan también:
        # - estado de la orden
        # - rol del usuario
        # - transición del item
        # - nuevo estado general de la orden
        # --------------------------------------------------
        previous_order_status = (
            self._process_status_transition(
                item=item,
                new_status=OrderItemStatus.CANCELLED,
                user=user,
                order_service=order_service
            )
        )

        # --------------------------------------------------
        # Auditoría del item
        # --------------------------------------------------
        cancelled_at = datetime.now(
            timezone.utc
        )

        item.cancelled_at = cancelled_at
        item.cancelled_by_id = user.id
        item.cancellation_reason = reason

        # --------------------------------------------------
        # Si era el último item activo,
        # _calculate_order_status() habrá cancelado también
        # la orden. Registramos su auditoría.
        # --------------------------------------------------
        if (
            previous_order_status != OrderStatus.CANCELLED
            and order.status == OrderStatus.CANCELLED
        ):
            order.cancelled_at = cancelled_at
            order.cancelled_by_id = user.id
            order.cancellation_reason = reason

        logger.info(
            (
                "Item cancelado "
                "order_id=%s item_id=%s "
                "user_id=%s reason=%s"
            ),
            order.id,
            item.id,
            user.id,
            reason
        )

        # ==================================================
        # EVENTOS
        # ==================================================

        payload = {
            "order_id": order.id,
            "item_id": item.id,
            "status": item.status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # --------------------------------------------------
        # Cocina
        # --------------------------------------------------
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.ITEM_STATUS_CHANGED,
            payload=payload,
            target="station",
            target_id=str(
                item.product.station_id
            )
        )

        # --------------------------------------------------
        # Salón / administración / caja
        #
        # Caja también debe enterarse porque la cancelación
        # modifica subtotal, total y saldo de la orden.
        # --------------------------------------------------
        for role in [
            UserRole.ADMIN,
            UserRole.WAITER,
            UserRole.CASHIER
        ]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_STATUS_CHANGED,
                payload=payload,
                target="role",
                target_id=role.value
            )

            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={
                    "order_id": order.id
                },
                target="role",
                target_id=role.value
            )

        # --------------------------------------------------
        # Si cambió también el estado general de la orden.
        #
        # Por ejemplo:
        # READY → CANCELLED
        # al cancelar el último item activo.
        # --------------------------------------------------
        if order.status != previous_order_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER,
                UserRole.CASHIER
            ]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )

        # --------------------------------------------------
        # Un único commit:
        #
        # - cancelación del item
        # - posible cancelación de la orden
        # - auditoría
        # - eventos Outbox
        #
        # todo queda dentro de la misma transacción.
        # --------------------------------------------------
        self.db.commit()

        self.db.refresh(item)
        self.db.refresh(order)

        return order_service.to_order_response(
            order
        )
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
        OrderItemStatus.SENT
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
        OrderItemStatus.DELIVERED,
        OrderItemStatus.CANCELLED
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

**Funciones (9):**
- __init__
- _get_product
- _product_name_exists
- _get_active_category
- _get_active_station
- create_product
- list_products
- update_product
- toggle_product

**Clases (1):**
- ProductService

**Imports (9):**
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.models.product.Product
- app.models.category.Category
- app.models.production_station.ProductionStation
- app.schemas.product.ProductCreate
- app.schemas.product.ProductUpdate
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode

```python
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.category import Category
from app.models.production_station import ProductionStation
from app.schemas.product import (
    ProductCreate, 
    ProductUpdate
)

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode


class ProductService:

    """
    Servicio encargado de la lógica de negocio relacionada con los productos.

    Responsabilidades:
    - Gestionar el CRUD de productos.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------
    # Obtener producto
    # -------------------------
    def _get_product(self, product_id: int, restaurant_id: int) -> Product:
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.restaurant_id == restaurant_id
        ).first()
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.PRODUCT_NOT_FOUND,
                context={"product_id": product_id})
        return product

    # --------------------------------------------------------------------------------
    # Encontrar producto por nombre
    # --------------------------------------------------------------------------------
    def _product_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(Product)
            .filter(
                Product.restaurant_id == restaurant_id,
                Product.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        return query.first() is not None

    # --------------------------------------------------------------------------------
    # Obtener una categoría activa del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_active_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == restaurant_id,
                Category.active.is_(True)
            )
            .first()
        )

        if not category:
            raise DomainError(
                "Category not found or inactive",
                ErrorCode.CATEGORY_NOT_FOUND,
                context={"category_id": category_id}
            )

        return category


    # --------------------------------------------------------------------------------
    # Obtener una estación activa del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_active_station(
        self,
        restaurant_id: int,
        station_id: int
    ) -> ProductionStation:
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.active.is_(True)
            )
            .first()
        )

        if not station:
            raise DomainError(
                "Station not found or inactive",
                ErrorCode.STATION_NOT_FOUND,
                context={"station_id": station_id}
            )

        return station

    # -------------------------
    # Crear producto
    # -------------------------
    def create_product(
        self,
        restaurant_id: int,
        data: ProductCreate
    ) -> Product:

        name = data.name.strip()

        if not name:
            raise DomainError(
                "Product name cannot be empty",
                ErrorCode.INVALID_PRODUCT_NAME
            )

        if self._product_name_exists(
            restaurant_id,
            name
        ):
            raise DomainError(
                "Product already exists",
                ErrorCode.PRODUCT_ALREADY_EXISTS
            )

        self._get_active_category(
            restaurant_id,
            data.category_id
        )

        self._get_active_station(
            restaurant_id,
            data.station_id
        )

        product = Product(
            name=name,
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
    def list_products(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[Product]:

        query = (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.station)
            )
            .filter(
                Product.restaurant_id == restaurant_id
            )
        )

        if active is not None:
            query = query.filter(
                Product.active == active
            )

        return (
            query
            .order_by(Product.name)
            .all()
        )

    # -------------------------
    # Actualizar producto
    # -------------------------
    def update_product(
        self,
        product_id: int,
        restaurant_id: int,
        data: ProductUpdate
    ) -> Product:

        product = self._get_product(
            product_id,
            restaurant_id
        )

        if data.name is not None:
            name = data.name.strip()

            if not name:
                raise DomainError(
                    "Product name cannot be empty",
                    ErrorCode.INVALID_PRODUCT_NAME
                )

            existing = self._product_name_exists(
                restaurant_id,
                name,
                exclude_id=product.id
            )

            if existing:
                raise DomainError(
                    "Product already exists",
                    ErrorCode.PRODUCT_ALREADY_EXISTS
                )

            data.name = name

        if data.category_id is not None:
            self._get_active_category(
                restaurant_id,
                data.category_id
            )

        if data.station_id is not None:
            self._get_active_station(
                restaurant_id,
                data.station_id
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        return product

    # -------------------------------------
    # Cambiar producto - Activo/Inactivo
    # -------------------------------------
    def toggle_product(self, product_id: int, restaurant_id: int) -> Product:
        product = self._get_product(product_id, restaurant_id)
        product.active = not product.active
        self.db.commit()
        self.db.refresh(product)
        return product
```

---

### .\backend\app\domain\reports\dependencies.py

**Funciones (1):**
- get_report_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- report_service.ReportService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .report_service import ReportService


def get_report_service(
    db: Session = Depends(get_db)
) -> ReportService:
    return ReportService(db)

```

---

### .\backend\app\domain\reports\report_service.py

**Funciones (14):**
- __init__
- _closed_orders_query
- _product_rows
- _summarize_products
- _order_total
- _serialize_sales_order
- _group_sales_order_items
- _date_bounds
- _empty_days
- _validate_date_range
- get_sales_report
- get_products_report
- get_product_evolution_report
- get_sales_orders_report

**Clases (1):**
- ReportService

**Imports (24):**
- datetime.date
- datetime.datetime
- datetime.time
- datetime.timedelta
- decimal.Decimal
- sqlalchemy.orm.Query
- sqlalchemy.orm.Session
- sqlalchemy.orm.joinedload
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus
- app.models.product.Product
- app.schemas.reports.SalesOrderOut
- app.schemas.reports.SalesOrderItemOut
- app.schemas.reports.SalesOrdersReportOut
- app.schemas.reports.ProductEvolutionReportOut
- app.schemas.reports.ProductEvolutionPoint
- app.schemas.reports.ProductsReportOut
- app.schemas.reports.ProductSummaryOut
- app.schemas.reports.SalesReportOut
- app.schemas.reports.SalesPointOut

```python
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Query
from sqlalchemy.orm import Session, joinedload

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product

from app.schemas.reports import (
    SalesOrderOut,
    SalesOrderItemOut,
    SalesOrdersReportOut,
    ProductEvolutionReportOut,
    ProductEvolutionPoint,
    ProductsReportOut,
    ProductSummaryOut,
    SalesReportOut,
    SalesPointOut
)

class ReportService:

    """
    Servicio encargado de la lógica de negocio relacionada con los reportes.

    Responsabilidades:
    - Gestionar la lógica de negocio de los reportes.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session):
        self.db = db

    # --------------------------------------------------------------------------------------
    # Devuelve una consulta de órdenes cerradas para un restaurante en un rango de fechas
    # --------------------------------------------------------------------------------------
    def _closed_orders_query(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ) -> Query:
        start, end = self._date_bounds(start_date, end_date)
        return (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.CLOSED,
                Order.closed_at >= start,
                Order.closed_at < end
            )
        )
    
    # ---------------------------------------------------------------------------------------------------------------------------------
    # Devuelve una consulta de los productos vendidos para un restaurante en un rango de fechas, opcionalmente filtrando por categoría
    # ---------------------------------------------------------------------------------------------------------------------------------
    def _product_rows(
        self,
        restaurant_id: int,
        range_start: datetime,
        range_end: datetime,
        category_id: int | None
    ) -> list[tuple[int, str, int | None, int, Decimal]]:
        query = (
            self.db.query(
                Product.id,
                Product.name,
                Product.category_id,
                OrderItem.quantity,
                OrderItem.unit_price
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.CLOSED,
                Order.closed_at >= range_start,
                Order.closed_at < range_end,
                OrderItem.status != OrderItemStatus.CANCELLED
            )
        )
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        return query.all()

    # --------------------------------------------------------------------------------------
    # Devuelve el total vendido de un producto
    # --------------------------------------------------------------------------------------
    def _summarize_products(
        self,
        restaurant_id: int,
        rows: list[tuple[int, str, int | None, int, Decimal]],
        category_id: int | None
    ) -> list[ProductSummaryOut]:
        totals: dict[int, dict] = {}
        products_query = self.db.query(Product).filter(Product.restaurant_id == restaurant_id)
        if category_id is not None:
            products_query = products_query.filter(Product.category_id == category_id)
        for product in products_query.all():
            totals[product.id] = {
                "product_id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "quantity": 0,
                "total": Decimal("0")
            }
        for product_id, name, product_category_id, quantity, unit_price in rows:
            if product_id not in totals:
                totals[product_id] = {
                    "product_id": product_id,
                    "name": name,
                    "category_id": product_category_id,
                    "quantity": 0,
                    "total": Decimal("0")
                }
            totals[product_id]["quantity"] += quantity
            totals[product_id]["total"] += quantity * unit_price
        return [
            ProductSummaryOut(
                product_id=item["product_id"],
                name=item["name"],
                category_id=item["category_id"],
                quantity=item["quantity"],
                total=item["total"]
            )
            for item in totals.values()
        ]

    # --------------------------------------------------------------------------------------
    # Devuelve el total de un pedido
    # --------------------------------------------------------------------------------------
    def _order_total(self, order: Order) -> Decimal:
        subtotal = sum(
            (
                item.quantity * item.unit_price
                for item in order.items
                if item.status != OrderItemStatus.CANCELLED
            ),
            Decimal("0")
        )
        return max(subtotal - (order.discount or Decimal("0")), Decimal("0"))

    # --------------------------------------------------------------------------------------
    # Devuelve una representación serializada de un pedido cerrado para el reporte de ventas
    # --------------------------------------------------------------------------------------
    def _serialize_sales_order(self, order: Order) -> SalesOrderOut:
        active_items = [
            item
            for item in order.items
            if item.status != OrderItemStatus.CANCELLED
        ]
        subtotal = sum(
            (item.quantity * item.unit_price for item in active_items),
            Decimal("0")
        )
        discount = order.discount or Decimal("0")
        return SalesOrderOut(
            order_id=order.id,
            table_number=order.table.number if order.table else None,
            closed_at=order.closed_at,
            items=self._group_sales_order_items(active_items),
            subtotal=subtotal,
            discount=discount,
            total=max(subtotal - discount, Decimal("0"))
        )

    # --------------------------------------------------------------------------------------
    # Agrupa los productos para el reporte de ventas
    # --------------------------------------------------------------------------------------
    def _group_sales_order_items(self, items: list[OrderItem]) -> list[SalesOrderItemOut]:
        grouped: dict[tuple[int, Decimal], SalesOrderItemOut] = {}
        for item in items:
            key = (
                item.product_id,
                item.unit_price
            )

            if key in grouped:
                grouped_item = grouped[key]

                grouped_item.quantity += item.quantity
                grouped_item.line_total += (
                    item.quantity *
                    item.unit_price
                )
            else:
                grouped[key] = SalesOrderItemOut(
                    item_id=item.id,
                    product_id=item.product_id,
                    product_name=(
                        item.product.name
                        if item.product
                        else "Producto eliminado"
                    ),
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=(
                        item.quantity *
                        item.unit_price
                    )
                )

        return sorted(
            grouped.values(),
            key=lambda item:
                item.product_name.lower()
        )

    # --------------------------------------------------------------------------------------
    # Devuelve el rango de fechas como datetime para consultas
    # --------------------------------------------------------------------------------------
    def _date_bounds(self, start_date: date, end_date: date) -> tuple[datetime, datetime]:
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date + timedelta(days=1), time.min)
        return start, end

    # ------------------------------------------------------------------------------------------
    # Devuelve un diccionario con días vacíos entre start_date y end_date, inicializados en 0
    # ------------------------------------------------------------------------------------------
    def _empty_days(self, start_date: date, end_date: date) -> dict[date, Decimal]:
        days: dict[date, Decimal] = {}
        current = start_date
        while current <= end_date:
            days[current] = Decimal("0")
            current += timedelta(days=1)
        return days

    # --------------------------------------------------------------------------------
    # Valida que el rango de fechas sea correcto (start_date <= end_date)
    # --------------------------------------------------------------------------------
    def _validate_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> None:
        if start_date > end_date:
            raise DomainError(
                "start date must be before or equal to end date",
                ErrorCode.REPORT_INVALID_DATE_RANGE,
                context={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )

    # --------------------------------------------------------------------------------
    # Obtener reporte de ventas
    # --------------------------------------------------------------------------------
    def get_sales_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ) -> SalesReportOut:
        self._validate_date_range(start_date, end_date)
        totals_by_day = self._empty_days(start_date, end_date)
        for order in self._closed_orders_query(restaurant_id, start_date, end_date):
            if not order.closed_at:
                continue
            day = order.closed_at.date()
            totals_by_day[day] += self._order_total(order)
        series = [
            SalesPointOut(
                date=day,
                total=total
            )
            for day, total in sorted(totals_by_day.items())
        ]
        non_zero_days = [
            point
            for point in series
            if point.total > 0
        ]
        return SalesReportOut(
            series=series,
            max_day=max(
                non_zero_days,
                key=lambda point: point.total,
                default=None
            ),
            min_day=min(
                non_zero_days,
                key=lambda point: point.total,
                default=None
            )
        )

    # --------------------------------------------------------------------------------
    # Obtener reporte de productos
    # --------------------------------------------------------------------------------
    def get_products_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date,
        category_id: int | None = None
    ) -> ProductsReportOut:
        self._validate_date_range(start_date, end_date)
        start_today = datetime.combine(date.today(), time.min)
        end_today = datetime.combine(date.today() + timedelta(days=1), time.min)
        start, end = self._date_bounds(start_date, end_date)
        period_items = self._summarize_products(
            restaurant_id=restaurant_id,
            rows=self._product_rows(restaurant_id, start, end, category_id),
            category_id=category_id
        )
        today_items = [
            item
            for item in self._summarize_products(
                restaurant_id=restaurant_id,
                rows=self._product_rows(restaurant_id, start_today, end_today, category_id),
                category_id=category_id
            )
            if item.quantity > 0
        ]
        top_products = sorted(
            [item for item in period_items if item.quantity > 0],
            key=lambda item: (item.quantity, item.total, item.name),
            reverse=True
        )[:10]
        least_products = sorted(
            period_items,
            key=lambda item: (item.quantity, item.total, item.name)
        )[:10]
        return ProductsReportOut(
            today_best_seller=max(
                today_items,
                key=lambda item: (item.quantity, item.total),
                default=None
            ),
            top_products=top_products,
            least_products=least_products
        )

    # --------------------------------------------------------------------------------
    # Obtener reporte de evolución de un producto
    # --------------------------------------------------------------------------------
    def get_product_evolution_report(
        self,
        restaurant_id: int,
        product_id: int,
        start_date: date,
        end_date: date
    ) -> ProductEvolutionReportOut:
        self._validate_date_range(start_date, end_date)
        totals_by_day = self._empty_days(start_date, end_date)
        start, end = self._date_bounds(start_date, end_date)
        rows = (
            self.db.query(Order.closed_at, OrderItem.quantity, OrderItem.unit_price)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.CLOSED,
                Order.closed_at >= start,
                Order.closed_at < end,
                OrderItem.product_id == product_id,
                OrderItem.status != OrderItemStatus.CANCELLED
            )
            .all()
        )
        for closed_at, quantity, unit_price in rows:
            if closed_at:
                totals_by_day[closed_at.date()] += quantity * unit_price
        return ProductEvolutionReportOut(
            series=[
                ProductEvolutionPoint(
                    date=day,
                    total=total
                )
                for day, total in sorted(totals_by_day.items())
            ]
        )

    # --------------------------------------------------------------------------------
    # Obtener reporte de órdenes de venta
    # --------------------------------------------------------------------------------
    def get_sales_orders_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ) -> SalesOrdersReportOut:
        self._validate_date_range(start_date, end_date)
        orders = (
            self._closed_orders_query(restaurant_id, start_date, end_date)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.table)
            )
            .order_by(Order.closed_at.desc(), Order.id.desc())
            .all()
        )
        return SalesOrdersReportOut(
            orders=[
                self._serialize_sales_order(order)
                for order in orders
                if order.closed_at
            ]
        )
```

---

### .\backend\app\domain\settings\dependencies.py

**Funciones (1):**
- get_settings_service

**Clases (0):**

**Imports (4):**
- fastapi.Depends
- sqlalchemy.orm.Session
- app.db.session.get_db
- settings_service.SettingsService

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .settings_service import SettingsService


def get_settings_service(
    db: Session = Depends(get_db)
) -> SettingsService:
    return SettingsService(db)
```

---

### .\backend\app\domain\settings\settings_service.py

**Funciones (5):**
- __init__
- get_settings
- to_response
- update_settings
- send_test_email

**Clases (1):**
- SettingsService

**Imports (10):**
- smtplib
- email.message.EmailMessage
- sqlalchemy.orm.Session
- app.domain.backup.schedule_utils.calculate_next_backup
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.enums.BackupFrequency
- app.models.system_settings.SystemSettings
- app.schemas.system_settings.SettingsUpdateRequest
- app.schemas.system_settings.SettingsResponse

```python
import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import Session

from app.domain.backup.schedule_utils import calculate_next_backup
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.enums import BackupFrequency
from app.models.system_settings import SystemSettings

from app.schemas.system_settings import (
    SettingsUpdateRequest,
    SettingsResponse
)

class SettingsService:

    def __init__(self, db: Session) -> None:
        self.db = db

    '''
    Servicio encargado de la lógica de negocio relacionada con la configuración del sistema.

    Responsabilidades:
    - Gestionar la lógica de negocio de la configuración del sistema.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    '''

    # --------------------------------------------------------------------------------------
    # Obtener configuración del sistema para un restaurante
    # --------------------------------------------------------------------------------------
    def get_settings(
        self,
        restaurant_id: int
    ) -> SystemSettings:
        settings = (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.restaurant_id == restaurant_id
            )
            .first()
        )
        if not settings:
            settings = SystemSettings(
                restaurant_id=restaurant_id,
                smtp_use_tls=True,
                backup_timezone="America/Montevideo"
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    # --------------------------------------------------------------------------------------
    # Serializar configuración del sistema para respuesta de API
    # --------------------------------------------------------------------------------------
    def to_response(
        self,
        settings: SystemSettings
    ) -> SettingsResponse:

        return SettingsResponse(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_from=settings.smtp_from,
            smtp_use_tls=settings.smtp_use_tls,

            smtp_password_configured=bool(settings.smtp_password),

            backup_email=settings.backup_email,
            backup_enabled=settings.backup_enabled,
            backup_frequency=settings.backup_frequency,

            backup_time=settings.backup_time,
            backup_weekday=settings.backup_weekday,
            backup_monthday=settings.backup_monthday,

            backup_retention_daily=settings.backup_retention_daily,
            backup_retention_weekly=settings.backup_retention_weekly,
            backup_retention_monthly=settings.backup_retention_monthly,

            backup_keep_local=settings.backup_keep_local,
            backup_send_email=settings.backup_send_email,
            backup_timezone=settings.backup_timezone,

            last_automatic_backup_at=settings.last_automatic_backup_at,
            next_automatic_backup_at=settings.next_automatic_backup_at,
            last_backup_result=settings.last_backup_result,
        )

    # --------------------------------------------------------------------------------------
    # Actualizar configuración del sistema para un restaurante
    # --------------------------------------------------------------------------------------
    def update_settings(
        self,
        restaurant_id: int,
        data: SettingsUpdateRequest
    ) -> SystemSettings:
        settings = self.get_settings(restaurant_id)
        if (
            data.backup_enabled
            and not data.backup_keep_local
            and not data.backup_send_email
        ):
            raise DomainError(
                "Debe conservar el backup localmente o enviarlo por correo.",
                ErrorCode.BACKUP_DESTINATION_REQUIRED
            )
        if (
            data.backup_frequency == BackupFrequency.WEEKLY
            and data.backup_weekday is None
        ):
            raise DomainError(
                "Debe indicar el dia de la semana.",
                ErrorCode.BACKUP_WEEKDAY_REQUIRED
            )
        if (
            data.backup_frequency == BackupFrequency.MONTHLY
            and data.backup_monthday is None
        ):
            raise DomainError(
                "Debe indicar el dia del mes.",
                ErrorCode.BACKUP_MONTHDAY_REQUIRED
            )
        if data.backup_send_email:
            if not data.smtp_host:
                raise DomainError(
                    "SMTP Host no configurado",
                    ErrorCode.SMTP_HOST_NOT_CONFIGURED
                )
            if not data.backup_email:
                raise DomainError(
                    "Correo de backup no configurado",
                    ErrorCode.BACKUP_EMAIL_NOT_CONFIGURED
                )
        settings.smtp_host = data.smtp_host
        settings.smtp_port = data.smtp_port
        settings.smtp_user = data.smtp_user
        settings.smtp_from = data.smtp_from
        settings.smtp_use_tls = data.smtp_use_tls

        settings.backup_email = data.backup_email
        settings.backup_enabled = data.backup_enabled
        settings.backup_frequency = data.backup_frequency
        settings.backup_time = data.backup_time
        settings.backup_weekday = data.backup_weekday
        settings.backup_monthday = data.backup_monthday
        settings.backup_retention_daily = data.backup_retention_daily
        settings.backup_retention_weekly = data.backup_retention_weekly
        settings.backup_retention_monthly = data.backup_retention_monthly
        settings.backup_keep_local = data.backup_keep_local
        settings.backup_send_email = data.backup_send_email
        settings.backup_timezone = data.backup_timezone
        settings.next_automatic_backup_at = (
            calculate_next_backup(settings)
            if settings.backup_enabled
            else None
        )
        if data.smtp_password:
            settings.smtp_password = data.smtp_password
        self.db.commit()
        self.db.refresh(settings)
        return settings

    # --------------------------------------------------------------------------------------
    # Enviar correo de prueba para verificar configuración SMTP
    # --------------------------------------------------------------------------------------
    def send_test_email(
        self,
        restaurant_id: int
    ):
        settings = self.get_settings(restaurant_id)
        if not settings.smtp_host:
            raise DomainError(
                "SMTP Host no configurado",
                ErrorCode.SMTP_HOST_NOT_CONFIGURED
            )
        if not settings.backup_email:
            raise DomainError(
                "Correo de backup no configurado",
                ErrorCode.BACKUP_EMAIL_NOT_CONFIGURED
            )
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port or 587
        smtp_user = settings.smtp_user or ""
        smtp_password = settings.smtp_password or ""
        smtp_from = settings.smtp_from or smtp_user
        smtp_use_tls = settings.smtp_use_tls

        message = EmailMessage()

        message["Subject"] = "Prueba de correo"
        message["From"] = smtp_from
        message["To"] = settings.backup_email

        message.set_content(
            "La configuracion SMTP del sistema funciona correctamente."
        )
        try:
            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=30
            ) as smtp:
                if smtp_use_tls:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                if smtp_user:
                    smtp.login(
                        smtp_user,
                        smtp_password
                    )
                smtp.send_message(message)
        except (
            smtplib.SMTPException,
            TimeoutError,
            ConnectionError,
            OSError
        ) as ex:
            raise DomainError(
                "No fue posible enviar el correo de prueba.",
                ErrorCode.EMAIL_SEND_FAILURE,
                context={"detail": str(ex)}
            ) from ex
        return {
            "success": True,
            "sent_to": settings.backup_email
        }
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

**Funciones (8):**
- __init__
- _station_name_exists
- _get_station
- get_station
- create_station
- list_stations
- update_station
- toggle_station

**Clases (1):**
- StationService

**Imports (6):**
- sqlalchemy.orm.Session
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.models.production_station.ProductionStation
- app.schemas.station.StationCreate
- app.schemas.station.StationUpdate

```python
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.production_station import ProductionStation

from app.schemas.station import (
    StationCreate,
    StationUpdate
)

class StationService:

    """
    Servicio encargado de la lógica de negocio relacionada con las estaciones.

    Responsabilidades:
    - Gestionar el CRUD de estaciones.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------
    # Comprobar si el nombre de la estación ya existe
    # -------------------------------------------------------
    def _station_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(
                ProductionStation.id != exclude_id
            )
        return query.first() is not None

    # ---------------------------------------
    # Obtener estación - método privado
    # ---------------------------------------
    def _get_station(self, restaurant_id: int, station_id: int) -> ProductionStation:
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id
            )
            .first()
        )
        if not station:
            raise DomainError(
                "Station not found",
                code=ErrorCode.STATION_NOT_FOUND
            )
        return station

    # -------------------------
    # Obtener estación
    # -------------------------
    def get_station(
        self,
        restaurant_id: int,
        station_id: int
    ):
        return self._get_station(
            restaurant_id,
            station_id
        )

    # -------------------------
    # Crear estación
    # ------------------------- 
    def create_station(self, restaurant_id: int, data: StationCreate) -> ProductionStation:
        name=data.name.strip()
        if not name:
            raise DomainError(
                "Station name cannot be empty",
                ErrorCode.INVALID_STATION_NAME
            )

        if self._station_name_exists(restaurant_id, name):
            raise DomainError(
                "Station name already exists",
                ErrorCode.STATION_NAME_ALREADY_EXISTS,
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
    def list_stations(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[ProductionStation]:

        query = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id
            )
        )

        if active is not None:
            query = query.filter(
                ProductionStation.active == active
            )

        return (
            query
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Actualizar estación
    # -------------------------
    def update_station(self, restaurant_id: int, station_id: int, data: StationUpdate) -> ProductionStation:
        station = self._get_station(restaurant_id, station_id)
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Station name cannot be empty",
                ErrorCode.INVALID_STATION_NAME
            )
        if self._station_name_exists(
            restaurant_id,
            name,
            exclude_id=station_id
        ):
            raise DomainError(
                "Station name already exists",
                ErrorCode.STATION_NAME_ALREADY_EXISTS,
                context={"name": name}
            )
        station.name = name
        self.db.commit()
        self.db.refresh(station)
        return station

    # -----------------------------
    # Activar/desactivar estación
    # -----------------------------
    def toggle_station(self, restaurant_id: int, station_id: int) -> ProductionStation:
        station = self._get_station(restaurant_id, station_id)
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

**Funciones (11):**
- __init__
- _exists_table_by_number
- _get_table
- list_tables
- list_tables_status
- create_table
- update_table
- update_position
- deactivate_table
- activate_table
- touch_table

**Clases (1):**
- TableService

**Imports (15):**
- sqlalchemy.orm.Session
- sqlalchemy.func
- app.domain.order.constants.ACTIVE_ORDER_STATUSES
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.domain.events.websocket.WSEvent
- app.services.event_service.EventService
- app.models.Table
- app.models.order.Order
- app.schemas.table.TablePositionUpdate
- app.schemas.table.TableStatusResponse
- app.schemas.table.TableCreate
- app.schemas.table.TableUpdate
- app.schemas.table.TableTouchResponse
- logging

```python
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.models import Table
from app.models.order import Order

from app.schemas.table import (
    TablePositionUpdate,
    TableStatusResponse,
    TableCreate,
    TableUpdate,
    TableTouchResponse
)

import logging

logger = logging.getLogger("app.domain.table")

class TableService:

    """
    Servicio encargado de la lógica de negocio relacionada con las mesas.

    Responsabilidades:
    - Gestionar el CRUD de las mesas.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    def _exists_table_by_number(
        self,
        restaurant_id: int,
        number: int,
        exclude_id: int | None = None,
    ) -> Table | None:
        query = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id,
            Table.number == number
        )
        if exclude_id is not None:
            query = query.filter(Table.id != exclude_id)
        return query.first()

    # -------------------------
    # Devolver mesa
    # -------------------------        
    def _get_table(self, restaurant_id: int, table_id: int, active_only: bool = False) -> Table:
        query = self.db.query(Table).filter(
            Table.id == table_id,
            Table.restaurant_id == restaurant_id
        )
        if active_only:
            query = query.filter(Table.active.is_(True))
        table = query.first()
        if not table:
            raise DomainError(
                "Table not found",
                code=ErrorCode.TABLE_NOT_FOUND,
                context={"table_id": table_id}
            )
        return table

    # -------------------------
    # Listar mesas
    # -------------------------
    def list_tables(self, restaurant_id: int, active: bool | None = True) -> list[Table]:
        query = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id
        )
        if active is not None:
            query = query.filter(Table.active == active)
        return query.order_by(Table.number).all()

    # ----------------------------
    # Listar status de las mesas
    # ----------------------------
    def list_tables_status(self, restaurant_id: int) -> list[TableStatusResponse]:
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
            TableStatusResponse(
                id=row.id,
                number=row.number,
                x=row.x,
                y=row.y,
                capacity=row.capacity,
                shape=row.shape,
                active=row.active,
                order_id=row.order_id,
                order_status=row.order_status,
            )
            for row in rows
        ]

    # -------------------------
    # Crear mesa
    # -------------------------
    def create_table(self, restaurant_id, data: TableCreate) -> Table:
        new_number = data.number
        if new_number is None:
            max_number = self.db.query(func.max(Table.number)).filter(
                Table.restaurant_id == restaurant_id
            ).scalar()
            new_number = (max_number or 0) + 1
        if new_number <= 0:
            raise DomainError(
                "Table number must be greater than zero",
                code=ErrorCode.INVALID_OPERATION,
                context={"number": new_number}
            )
        existing = self._exists_table_by_number(restaurant_id, new_number)
        if existing:
            raise DomainError(
                "Table number already exists",
                code=ErrorCode.TABLE_NUMBER_ALREADY_EXISTS,
                context={
                    "number": new_number,
                    "active": existing.active
                }
            )
        logger.info("Mesa creada r=%s number=%s", restaurant_id, new_number)
        table = Table(
            restaurant_id=restaurant_id,
            number=new_number,
            x=data.x,
            y=data.y,
            capacity=data.capacity,
            shape=data.shape
        )
        self.db.add(table)
        self.db.flush()
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.TABLE_CREATED,
            payload={"table_id": table.id}
        )
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Actualizar mesa
    # -------------------------
    def update_table(self, restaurant_id, table_id, data: TableUpdate) -> Table:
        table = self._get_table(restaurant_id, table_id)
        update_data = data.model_dump(exclude_unset=True)
        new_number = update_data.get("number")
        if new_number is not None:
            if new_number <= 0:
                raise DomainError(
                    "Table number must be greater than zero",
                    code=ErrorCode.INVALID_OPERATION,
                    context={"number": new_number}
                )
            existing = self._exists_table_by_number(restaurant_id, new_number, exclude_id=table_id)
            if existing:
                raise DomainError(
                    "Table number already exists",
                    code=ErrorCode.TABLE_NUMBER_ALREADY_EXISTS,
                    context={
                        "number": new_number,
                        "active": existing.active
                    }
                )

        for field, value in update_data.items():
            setattr(table, field, value)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.TABLE_UPDATED,
            payload={"table_id": table.id}
        )
        self.db.commit()
        self.db.refresh(table)
        return table

    # --------------------------------
    # Actualizar posición de la mesa
    # --------------------------------
    def update_position(
        self,
        restaurant_id: int,
        table_id: int,
        data: TablePositionUpdate
    ) -> Table:
        table = self._get_table(restaurant_id, table_id, active_only=True)
        table.x = data.x
        table.y = data.y
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.TABLE_POSITION_UPDATED,
            payload={
                "table_id": table.id,
                "x": table.x,
                "y": table.y
            }
        )
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Desactivar mesa
    # -------------------------
    def deactivate_table(self, restaurant_id, table_id) -> None:
        table = self._get_table(restaurant_id, table_id, active_only=True)
        logger.info("Mesa desactivada r=%s table_id=%s", restaurant_id, table_id)
        table.active = False
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.TABLE_DEACTIVATED,
            payload={"table_id": table.id}
        )
        self.db.commit()

    # -------------------------
    # Activar mesa
    # -------------------------
    def activate_table(self, restaurant_id, table_id) -> None:
        table = self._get_table(restaurant_id, table_id)
        logger.info("Mesa activada r=%s table_id=%s", restaurant_id, table_id)
        table.active = True
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.TABLE_ACTIVATED,
            payload={"table_id": table.id}
        )
        self.db.commit()  

    # -------------------------
    # Tocar mesa
    # -------------------------
    def touch_table(self, restaurant_id: int, table_id: int) -> TableTouchResponse:
        table = self._get_table(restaurant_id, table_id, active_only=True)
        order = self.db.query(Order).filter(
            Order.table_id == table_id,
            Order.restaurant_id == restaurant_id,
            Order.status.in_(ACTIVE_ORDER_STATUSES)
        ).first()
        return TableTouchResponse(
            table_id=table.id,
            table_number=table.number,
            order_id=order.id if order else None
        )
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

**Funciones (7):**
- __init__
- _username_exists
- get_user
- list_users
- create_user
- update_user
- toggle_user

**Clases (1):**
- UserService

**Imports (8):**
- logging
- sqlalchemy.orm.Session
- app.domain.errors.base.DomainError
- app.domain.errors.error_codes.ErrorCode
- app.core.security.get_password_hash
- app.models.user.User
- app.schemas.user.UserCreate
- app.schemas.user.UserUpdate

```python
import logging
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.core.security import get_password_hash

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger("app.domain.user")

class UserService:

    def __init__(self, db: Session) -> None:
        self.db = db

    # -----------------------------------------------------------------
    # Verificar si un nombre de usuario ya existe en el restaurante
    # -----------------------------------------------------------------
    def _username_exists(
        self,
        restaurant_id: int,
        username: str,
        exclude_user_id: int | None = None
    ) -> bool:
        query = self.db.query(User).filter(
            User.restaurant_id == restaurant_id,
            User.username == username
        )
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    # -------------------------
    # Obtener usuario
    # -------------------------
    def get_user(self, user_id: int, restaurant_id: int) -> User:
        user = self.db.query(User).filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        ).first()
        if not user:
            raise DomainError(
                "User not found",
                ErrorCode.USER_NOT_FOUND
            )
        return user

    # -------------------------
    # Listar usuarios
    # -------------------------
    def list_users(self, restaurant_id: int) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.restaurant_id == restaurant_id)
            .order_by(User.username)
            .all()
        )

    # -------------------------
    # Crear usuario
    # -------------------------
    def create_user(self, restaurant_id: int, data: UserCreate) -> User:
        existing = self._username_exists(restaurant_id, data.username)
        if existing:
            raise DomainError(
                "User exists",
                ErrorCode.USERNAME_ALREADY_EXISTS,
                context={"username": data.username}
            )
        hashed = get_password_hash(data.password.get_secret_value())
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
        logger.info(
            "Usuario creado r=%s username=%s role=%s",
            restaurant_id,
            user.username,
            user.role
        )
        return user

    # -------------------------
    # Actualizar usuario
    # -------------------------
    def update_user(self, user_id: int, restaurant_id: int, data: UserUpdate) -> User:
        user = self.get_user(user_id, restaurant_id)
        if data.username is not None:
            existing = self._username_exists(restaurant_id, data.username, exclude_user_id=user_id)
            if existing:
                raise DomainError(
                    "User exists",
                    ErrorCode.USERNAME_ALREADY_EXISTS,
                    context={"username": data.username}
                )
            user.username = data.username
        if data.role is not None:
            user.role = data.role
        if data.password is not None:
            user.password_hash = get_password_hash(data.password.get_secret_value())
        self.db.commit()
        self.db.refresh(user)
        logger.info(
            "Usuario actualizado r=%s id=%s",
            restaurant_id,
            user.id
        )
        return user

    # --------------------------------------
    # Activar / Desactivar usuario
    # --------------------------------------
    def toggle_user(self, target_user_id: int, current_user_id: int, restaurant_id: int) -> User:
        if target_user_id == current_user_id:
            raise DomainError(
                "You cannot deactivate your own account.",
                ErrorCode.USER_CANNOT_DEACTIVATE_SELF
            )
        user = self.get_user(target_user_id, restaurant_id)
        user.active = not user.active
        self.db.commit()
        self.db.refresh(user)
        logger.info(
            "Usuario %s id=%s",
            "activado" if user.active else "desactivado",
            restaurant_id,
            user.id
        )
        return user
```

---

### .\backend\app\events\redis_listener.py

**Funciones (2):**
- _process_event
- redis_event_listener

**Clases (0):**

**Imports (8):**
- asyncio
- json
- logging
- typing.Any
- app.core.redis.redis_client
- app.websocket.manager.manager
- app.services.event_worker.INSTANCE_ID
- app.models.user.UserRole

```python
import asyncio
import json
import logging

from typing import Any

from app.core.redis import redis_client
from app.websocket.manager import manager
from app.services.event_worker import INSTANCE_ID
from app.models.user import UserRole

logger = logging.getLogger("app.redis_listener")

CHANNEL = "restaurant_events"

# --------------------------------------------------------------------------------------
# Procesa un evento recibido desde Redis y lo distribuye mediante WebSocket.
# --------------------------------------------------------------------------------------
async def _process_event(data: dict[str, Any]) -> None:
    try:

        # ignorar eventos propios
        if data.get("origin") == INSTANCE_ID:
            return

        restaurant_id = data.get("restaurant_id")
        target = data.get("target")
        target_id = data.get("target_id")
        event_type = data.get("event_type")
        payload = data.get("payload") or {}

        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                logger.warning("Invalid JSON payload: %s", payload)
                return
        if not restaurant_id or not event_type:
            logger.warning("Invalid event received: %s", data)
            return
        if not isinstance(payload, dict):
            logger.warning("Invalid payload type: %s", type(payload))
            return
        message = {
            "type": event_type,
            "payload": payload
        }
        logger.debug(
            "Dispatch WS event: r=%s target=%s type=%s payload=%s",
            restaurant_id,
            target,
            event_type,
            payload
        )
        if target == "broadcast":
            await manager.broadcast(
                restaurant_id,
                message
            )
        elif target == "role":
            await manager.send_to_role(
                restaurant_id,
                UserRole(target_id),
                message
            )
        elif target == "station":
            station_payload = {
                **payload,
                "station_id": int(target_id)
            }
            await manager.send_to_role(
                restaurant_id,
                UserRole.KITCHEN,
                {
                    "type": event_type,
                    "payload": station_payload
                }
            )
        else:
            logger.warning(
                "Unknown event target: %s",
                target
            )
    except Exception:
        logger.exception("Error processing redis event: %s", data)

# --------------------------------------------------------------------------------------
# Escucha permanentemente el canal Redis y despacha los eventos recibidos.
# Reconecta automáticamente ante cualquier fallo.
# --------------------------------------------------------------------------------------
async def redis_event_listener() -> None:

    while True:
        pubsub = None
        try:
            logger.info("Starting Redis listener")
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(CHANNEL)
            logger.info("Subscribed to %s", CHANNEL)
            async for message in pubsub.listen():
                try:
                    if message["type"] != "message":
                        continue
                    raw = message["data"]
                    if not raw:
                        continue
                    # Redis puede devolver bytes dependiendo de la configuración del cliente.
                    if isinstance(raw, bytes):
                        raw = raw.decode()

                    data = json.loads(raw)

                    # procesar evento sin bloquear listener
                    asyncio.create_task(_process_event(data))

                except Exception:
                    logger.exception("Error reading redis message")

        except asyncio.CancelledError:

            logger.info("Redis listener cancelled")
            break

        except Exception:
            logger.exception("Redis listener crashed. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)
        finally:
            if pubsub:
                try:
                    await pubsub.unsubscribe(CHANNEL)
                    await pubsub.close()
                except Exception:
                    logger.exception("Error closing Redis pubsub")
            logger.info("Redis listener stopped")

```

---

### .\backend\app\infraestructure\restart\restart_manager.py

**Funciones (2):**
- request_restart
- _restart

**Clases (1):**
- RestartManager

**Imports (3):**
- os
- threading
- time

```python
import os
import threading
import time


class RestartManager:
    """
    Gestiona el reinicio controlado del proceso de la aplicación.

    Se utiliza principalmente después de solicitar la restauración de un backup,
    permitiendo que la respuesta HTTP sea enviada antes de finalizar el proceso.
    """

    _requested: bool = False
    _lock = threading.Lock()

    # --------------------------------------------------------------------------------------
    # Solicita el reinicio de la aplicación.
    # Si ya existe una solicitud pendiente, no hace nada.
    # --------------------------------------------------------------------------------------
    @classmethod
    def request_restart(cls) -> None:

        with cls._lock:

            if cls._requested:
                return

            cls._requested = True

        threading.Thread(
            target=cls._restart,
            daemon=True,
        ).start()

    # --------------------------------------------------------------------------------------
    # Espera unos segundos para permitir que la respuesta HTTP llegue al cliente
    # y luego finaliza el proceso. Docker o el supervisor correspondiente se
    # encargará de iniciarlo nuevamente.
    # --------------------------------------------------------------------------------------
    @staticmethod
    def _restart() -> None:

        time.sleep(3)

        os._exit(0)
```

---

### .\backend\app\models\cash_movement.py

**Funciones (0):**

**Clases (2):**
- CashMovementType
- CashMovement

**Imports (13):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.DateTime
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Enum
- sqlalchemy.String
- sqlalchemy.Identity
- sqlalchemy.Index
- sqlalchemy.sql.func
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Numeric,
    ForeignKey,
    Enum,
    String,
    Identity,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashMovementType(str, enum.Enum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class CashMovement(Base):
    __tablename__ = "cash_movements"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

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
        Enum(
            CashMovementType,
            values_callable=lambda enum: [
                item.value
                for item in enum
            ],
            native_enum=False,
            length=20
        ),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    reason = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index(
            "ix_cash_movements_register",
            "cash_register_id"
        ),
        Index(
            "ix_cash_movements_register_type",
            "cash_register_id",
            "type"
        ),
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

**Imports (11):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.DateTime
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Boolean
- sqlalchemy.JSON
- sqlalchemy.Identity
- sqlalchemy.sql.func
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Numeric,
    ForeignKey,
    Boolean,
    JSON,
    Identity
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

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
        ForeignKey("users.id"),
        nullable=False
    )

    closed_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    opened_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    opening_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    closing_amount = Column(
        Numeric(10, 2),
        nullable=True
    )

    expected_cash = Column(
        Numeric(10, 2),
        nullable=True
    )

    counted_cash = Column(
        Numeric(10, 2),
        nullable=True
    )

    difference = Column(
        Numeric(10, 2),
        nullable=True
    )

    total_sales = Column(
        Numeric(10, 2),
        nullable=True
    )

    payments_snapshot = Column(
        JSON,
        nullable=True
    )

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

**Imports (9):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.String
- sqlalchemy.UniqueConstraint
- sqlalchemy.Identity
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
from sqlalchemy import (
    Column,
    Integer,
    Boolean, 
    ForeignKey, 
    String, 
    UniqueConstraint, 
    Identity
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, Identity(), primary_key=True)

    name = Column(String, nullable=False)

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "name",
            name="uq_category_name_per_restaurant"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="categories"
    )

    products = relationship(
        "Product",
        back_populates="category"
    )
```

---

### .\backend\app\models\enums.py

**Funciones (0):**

**Clases (2):**
- BackupFrequency
- TableShape

**Imports (1):**
- enum.Enum

```python
from enum import Enum


class BackupFrequency(str, Enum):
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TableShape(str, Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    RECTANGLE_HORIZONTAL = "rectangle-horizontal"
    RECTANGLE_VERTICAL = "rectangle-vertical"
```

---

### .\backend\app\models\event_outbox.py

**Funciones (0):**

**Clases (1):**
- EventOutbox

**Imports (11):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.DateTime
- sqlalchemy.JSON
- sqlalchemy.ForeignKey
- sqlalchemy.Identity
- sqlalchemy.Index
- sqlalchemy.func
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Identity,
    Index,
    func
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class EventOutbox(Base):
    __tablename__ = "event_outbox"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    payload = Column(
        JSON,
        nullable=False
    )

    target = Column(
        String,
        nullable=False
    )

    target_id = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    retries = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_error = Column(
        String,
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_event_outbox_restaurant",
            "restaurant_id"
        ),
        Index(
            "ix_event_outbox_event_type",
            "event_type"
        ),
        Index(
            "ix_event_outbox_status",
            "status"
        ),
        Index(
            "ix_event_outbox_created",
            "created_at"
        ),
        Index(
            "idx_event_outbox_cleanup",
            "status",
            "processed_at"
        ),
        Index(
            "idx_event_outbox_failed_cleanup",
            "status",
            "retries",
            "created_at"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="event_outbox"
    )
```

---

### .\backend\app\models\order.py

**Funciones (0):**

**Clases (2):**
- OrderStatus
- Order

**Imports (15):**
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
- sqlalchemy.Identity
- sqlalchemy.Text
- sqlalchemy.sql.func
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
import enum
import uuid
from sqlalchemy import (
    Column, 
    Integer, 
    Numeric, 
    ForeignKey, 
    String, 
    DateTime, 
    Enum, 
    Index, 
    Identity,
    Text
)
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

    id = Column(Integer, Identity(), primary_key=True)
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

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    discount = Column(Numeric(10, 2), nullable=False, default=0)

    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    cancelled_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    cancellation_reason = Column(
        Text,
        nullable=True
    )
    
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

**Imports (13):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.ForeignKey
- sqlalchemy.Numeric
- sqlalchemy.String
- sqlalchemy.Enum
- sqlalchemy.Identity
- sqlalchemy.Index
- sqlalchemy.DateTime
- sqlalchemy.Text
- sqlalchemy.orm.relationship
- enum
- app.db.base_class.Base

```python
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    Enum,
    Identity,
    Index,
    DateTime,
    Text
)
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

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

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

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        Enum(OrderItemStatus),
        default=OrderItemStatus.PENDING,
        nullable=False
    )

    notes = Column(
        String,
        nullable=True
    )

    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    cancelled_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    cancellation_reason = Column(
        Text,
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_order_items_order_status",
            "order_id",
            "status"
        ),
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")

    restaurant = relationship(
        "Restaurant",
        back_populates="order_items"
    )
```

---

### .\backend\app\models\payment.py

**Funciones (0):**

**Clases (2):**
- PaymentMethod
- Payment

**Imports (9):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Enum
- sqlalchemy.Numeric
- sqlalchemy.ForeignKey
- sqlalchemy.Identity
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum

from sqlalchemy import (
    Column,
    Integer,
    Enum,
    Numeric,
    ForeignKey,
    Identity
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

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

    method = Column(
        Enum(PaymentMethod),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="payments"
    )

    cash_register = relationship(
        "CashRegister"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="payments"
    )
```

---

### .\backend\app\models\product.py

**Funciones (0):**

**Clases (1):**
- Product

**Imports (10):**
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Numeric
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.UniqueConstraint
- sqlalchemy.Identity
- app.db.base_class.Base
- sqlalchemy.orm.relationship

```python
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint, Identity
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, Identity(), primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    station_id = Column(
        Integer,
        ForeignKey("production_stations.id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )
    
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

**Imports (9):**
- sqlalchemy.orm.relationship
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.UniqueConstraint
- sqlalchemy.Identity
- app.db.base_class.Base

```python
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    ForeignKey, 
    UniqueConstraint, 
    Identity
)
from app.db.base_class import Base

class ProductionStation(Base):
    __tablename__ = "production_stations"

    id = Column(Integer, Identity(), primary_key=True)
    restaurant_id = Column(ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

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

**Imports (11):**
- uuid
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.DateTime
- sqlalchemy.Boolean
- sqlalchemy.Identity
- sqlalchemy.orm.relationship
- datetime.datetime
- datetime.timezone
- app.db.base_class.Base

```python
import uuid

from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime, 
    Boolean, 
    Identity
)
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from app.db.base_class import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, Identity(), primary_key=True)

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
    tables = relationship(
        "Table",
        back_populates="restaurant",
        cascade="all, delete"
    )

    products = relationship(
        "Product",
        back_populates="restaurant",
        cascade="all, delete"
    )

    payments = relationship(
        "Payment",
        back_populates="restaurant",
        cascade="all, delete"
    )

    orders = relationship(
        "Order",
        back_populates="restaurant",
        cascade="all, delete"
    )

    cash_registers = relationship(
        "CashRegister",
        back_populates="restaurant",
        cascade="all, delete"
    )

    stations = relationship(
        "ProductionStation",
        back_populates="restaurant",
        cascade="all, delete"
    )

    categories = relationship(
        "Category",
        back_populates="restaurant",
        cascade="all, delete"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="restaurant",
        cascade="all, delete"
    )

    users = relationship(
        "User",
        back_populates="restaurant"
    )

    event_outbox = relationship(
        "EventOutbox",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    settings = relationship(
        "SystemSettings",
        back_populates="restaurant",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
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
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey
)

from app.db.base_class import Base


class RestaurantLayout(Base):
    __tablename__ = "restaurant_layout"

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        primary_key=True
    )

    width = Column(
        Integer,
        nullable=False,
        default=900
    )

    height = Column(
        Integer,
        nullable=False,
        default=500
    )

    grid_size = Column(
        Integer,
        nullable=False,
        default=40
    )

    snap_to_grid = Column(
        Boolean,
        nullable=False,
        default=True
    )

    background_image = Column(
        String,
        nullable=True
    )
```

---

### .\backend\app\models\system_settings.py

**Funciones (0):**

**Clases (1):**
- SystemSettings

**Imports (12):**
- datetime.time
- sqlalchemy.Column
- sqlalchemy.DateTime
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.Time
- sqlalchemy.Enum
- sqlalchemy.orm.relationship
- app.models.enums.BackupFrequency
- app.db.base_class.Base

```python
# app/models/system_settings.py

from datetime import time

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Time,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship

from app.models.enums import BackupFrequency

from app.db.base_class import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        primary_key=True
    )

    # SMTP
    smtp_host = Column(
        String,
        nullable=True
    )

    smtp_port = Column(
        Integer,
        nullable=False,
        default=587
    )

    smtp_user = Column(
        String,
        nullable=True
    )

    smtp_password = Column(
        String,
        nullable=True
    )

    smtp_from = Column(
        String,
        nullable=True
    )

    smtp_use_tls = Column(
        Boolean,
        nullable=False,
        default=True
    )


    # Backups
    backup_email = Column(
        String,
        nullable=True
    )

    backup_frequency = Column(
        SqlEnum(
            BackupFrequency,
            values_callable=lambda enum: [
                item.value
                for item in enum
            ],
            native_enum=False,
            length=20
        ),
        nullable=False,
        default=BackupFrequency.MANUAL
    )

    backup_retention_daily = Column(
        Integer,
        nullable=False,
        default=30
    )

    backup_retention_weekly = Column(
        Integer,
        nullable=False,
        default=84
    )

    backup_retention_monthly = Column(
        Integer,
        nullable=False,
        default=365
    )

    backup_time = Column(
        Time,
        nullable=False,
        default=time(hour=3, minute=0)
    )

    backup_weekday = Column(
        Integer,
        nullable=True
    )

    backup_monthday = Column(
        Integer,
        nullable=True
    )

    backup_enabled = Column(
        Boolean,
        nullable=False,
        default=False
    )

    last_automatic_backup_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    next_automatic_backup_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_backup_result = Column(
        String,
        nullable=True
    )

    backup_keep_local = Column(
        Boolean,
        nullable=False,
        default=True
    )

    backup_send_email = Column(
        Boolean,
        nullable=False,
        default=False
    )

    backup_timezone = Column(
        String,
        nullable=False,
        default="America/Montevideo"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="settings"
    )
```

---

### .\backend\app\models\table.py

**Funciones (0):**

**Clases (1):**
- Table

**Imports (12):**
- uuid
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.Boolean
- sqlalchemy.ForeignKey
- sqlalchemy.String
- sqlalchemy.UniqueConstraint
- sqlalchemy.Index
- sqlalchemy.Identity
- sqlalchemy.orm.relationship
- app.db.base_class.Base
- app.models.enums.TableShape

```python
import uuid

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    Index,
    Identity
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from app.models.enums import TableShape


class Table(Base):
    __tablename__ = "tables"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    number = Column(
        Integer,
        nullable=False
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    x = Column(
        Integer,
        nullable=False,
        default=0
    )

    y = Column(
        Integer,
        nullable=False,
        default=0
    )

    capacity = Column(
        Integer,
        nullable=False,
        default=4
    )

    shape = Column(
        String,
        nullable=False,
        default=TableShape.CIRCLE.value
    )

    external_id = Column(
        String,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

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

**Imports (11):**
- enum
- sqlalchemy.Column
- sqlalchemy.Integer
- sqlalchemy.String
- sqlalchemy.Enum
- sqlalchemy.ForeignKey
- sqlalchemy.Boolean
- sqlalchemy.Identity
- sqlalchemy.UniqueConstraint
- sqlalchemy.orm.relationship
- app.db.base_class.Base

```python
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Boolean,
    Identity,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    WAITER = "WAITER"
    KITCHEN = "KITCHEN"
    CASHIER = "CASHIER"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    username = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "username",
            name="uq_user_username_per_restaurant"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="users"
    )
```

---

### .\backend\app\models\__init__.py

**Funciones (0):**

**Clases (0):**

**Imports (15):**
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
- restaurant_layout.RestaurantLayout
- cash_movement.CashMovement
- event_outbox.EventOutbox
- system_settings.SystemSettings
- enums.BackupFrequency

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
from .restaurant_layout import RestaurantLayout
from .cash_movement import CashMovement
from .event_outbox import EventOutbox
from .system_settings import SystemSettings
from .enums import BackupFrequency

```

---

### .\backend\app\routers\auth.py

**Funciones (2):**
- login
- get_me

**Clases (0):**

**Imports (14):**
- logging
- fastapi.APIRouter
- fastapi.Depends
- fastapi.HTTPException
- fastapi.status
- fastapi.security.OAuth2PasswordRequestForm
- sqlalchemy.orm.Session
- app.db.session.get_db
- app.dependencies.auth.get_current_user
- app.core.security.create_access_token
- app.core.security.verify_password
- app.models.user.User
- app.schemas.auth.TokenResponse
- app.schemas.user.UserOut

```python
"""
Endpoints para la gestión de la autenticación de usuarios.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""
import logging

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.dependencies.auth import get_current_user
from app.core.security import (
    create_access_token, 
    verify_password
)

from app.models.user import User

from app.schemas.auth import TokenResponse
from app.schemas.user import UserOut

logger = logging.getLogger("app.routers.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

# ----------------------------------------------------------------------------------------------------
# Autenticar usuario
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve un JWT."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning("Login fallido username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    logger.info("Login exitoso user=%s r=%s", user.id, user.restaurant_id)
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value,
        "restaurant_id": user.restaurant_id
    })
    return TokenResponse(access_token=token, token_type="bearer")

# ----------------------------------------------------------------------------------------------------
# Obtener datos del usuario autenticado
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Usuario autenticado",
    description="Devuelve la información del usuario autenticado."
)
def get_me(user: User = Depends(get_current_user)):
    return user
```

---

### .\backend\app\routers\backups.py

**Funciones (7):**
- create_backup
- create_and_email_backup
- restore_backup
- backup_status
- list_backups
- download_backup
- delete_backup

**Clases (0):**

**Imports (8):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.admin_only
- app.domain.backup.backup_service.BackupService
- app.domain.backup.dependencies.get_backup_service
- app.models.user.User
- app.schemas.backup.BackupEmailRequest

```python
"""
Endpoints para la gestión de backups.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import admin_only

from app.domain.backup.backup_service import BackupService
from app.domain.backup.dependencies import get_backup_service

from app.models.user import User

from app.schemas.backup import BackupEmailRequest

router = APIRouter(prefix="/backups", tags=["backups"])

# ----------------------------------------------------------------------------------------------------
# Crear un backup
# ----------------------------------------------------------------------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crea un backup",
    description="Crea un backup manual."
)
def create_backup(
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.create_backup(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Crea un backup y lo envía por correo electrónico
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/email",
    status_code=status.HTTP_201_CREATED,
    summary="Crear backup y enviar por e-mail",
    description="Crea un backup y lo envía por e-mail al e-mail configurado."
)
def create_and_email_backup(
    data: BackupEmailRequest,
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.create_and_email_backup(data.email, user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Restaura un backup
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/restore/{filename:path}",
    status_code=status.HTTP_201_CREATED,
    summary="Restaurar un backup existente",
    description="Restaura un backup existente a partir del archivo seleccionado."
)
def restore_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.restore_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )

# ----------------------------------------------------------------------------------------------------
# Obtiene el status de un backup
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Obtener el status del backup",
    description="Obtiene el status del backup seleccionado."
)
def backup_status(
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.status(
        user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Obtiene un listado de los backups
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    summary="Listado de backups",
    description="Obtiene un listado de todos los backups del restaurant autenticado."
)
def list_backups(
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.list_backups(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Descarga un backup a un dispositivo de almacenamiento
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/download/{filename:path}",
    status_code=status.HTTP_200_OK,
    summary="Descargar backup",
    description="Descarga un backup a un dispositivo de almacenamiento."
)
def download_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.download_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )

# ----------------------------------------------------------------------------------------------------
# Elimina un backup
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/{filename:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un backup",
    description="Elimina el backup seleccionado."
)
def delete_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    service.delete_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )
```

---

### .\backend\app\routers\cash_register.py

**Funciones (6):**
- open_cash_register
- close_cash_register
- create_cash_movement
- current_cash_register
- get_cash_register_dashboard
- delete_cash_movement

**Clases (0):**

**Imports (17):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.cashier_or_admin
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.cash_register.cash_movement_service.CashMovementService
- app.domain.cash_register.dependencies.get_cash_register_service
- app.domain.cash_register.dependencies.get_cash_movement_service
- app.models.user.User
- app.schemas.cash_register.CashRegisterOpen
- app.schemas.cash_register.CashRegisterResponse
- app.schemas.cash_register.CashRegisterSummary
- app.schemas.cash_register.CashRegisterCloseOut
- app.schemas.cash_register.CashMovementCreate
- app.schemas.cash_register.CashMovementOut
- app.schemas.cash_register.CashRegisterClose
- app.schemas.cash_register.CashRegisterDashboard

```python
"""
Endpoints para la gestión de la caja registradora.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import cashier_or_admin

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService
from app.domain.cash_register.dependencies import (
    get_cash_register_service,
    get_cash_movement_service
)

from app.models.user import User

from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterResponse,
    CashRegisterSummary,
    CashRegisterCloseOut,
    CashMovementCreate,
    CashMovementOut,
    CashRegisterClose,
    CashRegisterDashboard
)

router = APIRouter(prefix="/cash-register", tags=["cash-register"])

# ----------------------------------------------------------------------------------------------------
# Abrir caja registradora
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/open",
    response_model=CashRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Abre caja registradora",
    description="Abre una caja registradora con un monto inicial en el restaurant autenticado."
    )

def open_cash_register(
    data: CashRegisterOpen,
    user: User = Depends(cashier_or_admin),
    service: CashRegisterService = Depends(get_cash_register_service),
):
    return service.open_cash_register(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        opening_amount=data.opening_amount
    )

# ----------------------------------------------------------------------------------------------------
# Cerrar caja registradora
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/close",
    response_model=CashRegisterCloseOut,
    status_code=status.HTTP_200_OK,
    summary="Cierra una caja registradora",
    description="Cierra la caja registradora del restaurant autenticado."
)
def close_cash_register(
    data: CashRegisterClose,
    user: User = Depends(cashier_or_admin),
    service: CashRegisterService = Depends(get_cash_register_service)   
):
    return service.close_cash_register(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Agregar un movimiento de caja
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/movements",
    response_model=CashMovementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agrega un movimiento de caja",
    description="Agrega un movimiento de caja para el restaurant autenticado."
)
def create_cash_movement(
    data: CashMovementCreate,
    user: User = Depends(cashier_or_admin),
    service: CashMovementService = Depends(get_cash_movement_service)
):
    return service.create_cash_movement(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Devuelve un resumen de la caja actual
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/current",
    response_model=CashRegisterSummary | None,
    status_code=status.HTTP_200_OK,
    summary="Resumen de la caja actual",
    description="Obtener un resumen de la caja actual del restaurant autenticado."
)
def current_cash_register(
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(cashier_or_admin)
):
    return service.get_current_cash_register(
        restaurant_id=user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Devuelve un resumen para el dashboard de la página del cajero
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/dashboard",
    response_model=CashRegisterDashboard | None,
    status_code=status.HTTP_200_OK,
    summary="Obtener dashboard",
    description="Obtener resumen de la caja actual para el dashboard de la página del cajero del restaurant autenticado."
)
def get_cash_register_dashboard(
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(cashier_or_admin)
):
    return service.get_dashboard(
        restaurant_id=user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Eliminar un movimiento de caja
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/movements/{movement_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un movimiento de caja",
    description="Elimina un movimientod de caja para el restaurant autenticado."
)
def delete_cash_movement(
    movement_id: int,
    user: User = Depends(cashier_or_admin),
    service: CashMovementService = Depends(get_cash_movement_service),
):
    return service.delete_cash_movement(
        restaurant_id=user.restaurant_id,
        movement_id=movement_id
    )
```

---

### .\backend\app\routers\category.py

**Funciones (5):**
- create_category
- list_categories
- list_categories_with_products
- update_category
- toggle_category

**Clases (0):**

**Imports (13):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.Query
- app.dependencies.roles.admin_only
- app.dependencies.roles.waiter_or_admin
- app.domain.category.category_service.CategoryService
- app.domain.category.dependencies.get_category_service
- app.models.user.User
- app.schemas.category.CategoryCreate
- app.schemas.category.CategoryResponse
- app.schemas.category.CategoryUpdate
- app.schemas.category.CategoryWithProducts

```python
"""
Endpoints para la gestión de categorías.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    admin_only, 
    waiter_or_admin
)

from app.domain.category.category_service import CategoryService
from app.domain.category.dependencies import get_category_service

from app.models.user import User

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithProducts,
)

router = APIRouter(prefix="/categories", tags=["categories"])

# ----------------------------------------------------------------------------------------------------
# Crear categoría
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría para el restaurante autenticado."
)
def create_category(
    data: CategoryCreate,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar categorías
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Devuelve la lista de categorías del restaurante autenticado."
)
def list_categories(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar categorías con productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/with-products",
    response_model=list[CategoryWithProducts],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías con productos",
    description="Devuelve la lista de categorías del restaurante autenticado junto con sus productos."
)
def list_categories_with_products(
    user: User = Depends(waiter_or_admin),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories_with_products(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar categoría
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría",
    description="Actualiza una categoría del restaurante."
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service)
):
    return service.update_category(user.restaurant_id, category_id, data)

# ----------------------------------------------------------------------------------------------------
# Activar o desactivar categoría
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{category_id}/toggle",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar categoría",
    description="Activa o desactiva una categoría del restaurante."
)
def toggle_category(
    category_id: int,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service)
):
    return service.toggle_category(user.restaurant_id, category_id)
```

---

### .\backend\app\routers\kitchen.py

**Funciones (1):**
- get_station_items

**Clases (0):**

**Imports (8):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.kitchen_or_admin
- app.domain.kitchen.dependencies.get_kitchen_service
- app.domain.kitchen.kitchen_service.KitchenService
- app.models.user.User
- app.schemas.order.kitchen.KitchenItemOut

```python
"""
Endpoints para la gestión de la cocina.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import kitchen_or_admin

from app.domain.kitchen.dependencies import get_kitchen_service
from app.domain.kitchen.kitchen_service import KitchenService

from app.models.user import User

from app.schemas.order.kitchen import KitchenItemOut

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

# ----------------------------------------------------------------------------------------------------
# Obtener items por estación
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/stations/{station_id}/items",
    response_model=list[KitchenItemOut],
    status_code=status.HTTP_200_OK,
    summary="Devolver items por estación",
    description="Devuelve la lista de items por estación del restaurante autenticado."
)
def get_station_items(
    station_id: int,
    user: User = Depends(kitchen_or_admin),
    service: KitchenService = Depends(get_kitchen_service)
):
    return service.get_station_items(
        station_id=station_id,
        user=user
    )
```

---

### .\backend\app\routers\layout.py

**Funciones (3):**
- upload_background
- get_layout
- update_layout

**Clases (0):**

**Imports (12):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.File
- fastapi.UploadFile
- app.dependencies.roles.waiter_or_admin
- app.dependencies.roles.admin_only
- app.domain.layout.dependencies.get_layout_service
- app.domain.layout.layout_service.LayoutService
- app.models.user.User
- app.schemas.layout.LayoutOut
- app.schemas.layout.LayoutUpdate

```python
"""
Endpoints para la gestión de la layout del restaurant.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    File,
    UploadFile
)

from app.dependencies.roles import (
    waiter_or_admin, 
    admin_only
)

from app.domain.layout.dependencies import get_layout_service
from app.domain.layout.layout_service import LayoutService

from app.models.user import User

from app.schemas.layout import(
    LayoutOut,
    LayoutUpdate
)

router = APIRouter(prefix="/layout", tags=["layout"])

# ----------------------------------------------------------------------------------------------------
# Subir imagen de fondo
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/background",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Aplicar background",
    description="Aplica un background al diseño del restaurant a partir de una imagen cargada desde disco."
)
async def upload_background(
    file: UploadFile = File(..., description="Carga el archivo seleccionado."),
    user: User = Depends(admin_only),
    service: LayoutService = Depends(get_layout_service)
):
    return await service.update_background_image(user.restaurant_id, file)

# ----------------------------------------------------------------------------------------------------
# Obtener el diseño del restaurant
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener diseño del restaurant",
    description="Obtiene el diseño del restaurant: tamaño, background, grid y snap_to_grid."
)
def get_layout(
    user: User = Depends(waiter_or_admin),
    service: LayoutService = Depends(get_layout_service)
):
    return service.get_layout(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar el diseño del restaurant
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar diseño del restaurant",
    description="Actualiza el diseño del restaurant: tamaño, background, grid y snap_to_grid."
)
def update_layout(
    data: LayoutUpdate,
    user: User = Depends(admin_only),
    service: LayoutService = Depends(get_layout_service)
):
    return service.update_layout(user.restaurant_id, data)
```

---

### .\backend\app\routers\orders.py

**Funciones (11):**
- add_item_to_order
- send_to_kitchen
- add_payment
- close_order
- apply_discount
- get_active_orders
- get_order
- update_order_item_quantity
- cancel_order
- delete_order_item
- delete_payment

**Clases (0):**

**Imports (16):**
- decimal.Decimal
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.Query
- app.dependencies.roles.waiter_or_admin
- app.dependencies.roles.waiter_cashier_or_admin
- app.dependencies.roles.all_staff
- app.domain.order.order_service.OrderService
- app.domain.order.dependencies.get_order_service
- app.models.user.User
- app.schemas.order.order_item.OrderItemCreate
- app.schemas.order.payment.PaymentCreate
- app.schemas.order.payment.PaymentOut
- app.schemas.order.order.OrderResponse
- app.schemas.order.order.OrderCancel

```python
"""
Endpoints para la gestión de órdenes.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from decimal import Decimal
from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    waiter_or_admin, 
    waiter_cashier_or_admin, 
    all_staff
)

from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User

from app.schemas.order.order_item import OrderItemCreate
from app.schemas.order.payment import (
    PaymentCreate,
    PaymentOut
)
from app.schemas.order.order import (
    OrderResponse,
    OrderCancel
)

router = APIRouter(prefix="/orders", tags=["orders"])

# -------------------------
# Agregar item
# -------------------------
@router.post(
    "/{order_id}/items",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar item a orden",
    description="Agrega un item a la orden especificada."
)
def add_item_to_order(
    order_id: int,
    data: OrderItemCreate,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.add_item(order, data)

# -------------------------
# Enviar a cocina
# -------------------------
@router.post(
    "/{order_id}/send-to-kitchen",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Enviar orden a cocina",
    description="Envía la orden especificada a la cocina."
)
def send_to_kitchen(
    order_id: int,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.send_to_kitchen(order)

# -------------------------
# Agregar pago
# -------------------------
@router.post(
    "/{order_id}/payments",
    response_model=PaymentOut,
    status_code=status.HTTP_200_OK,
    summary="Agregar pago a orden",
    description="Agrega un pago a la orden especificada."
)
def add_payment(
    order_id: int,
    data: PaymentCreate,
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.add_payment(order, data)

# -------------------------
# Cerrar orden
# -------------------------
@router.post(
    "/{order_id}/close",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar orden",
    description="Cierra la orden especificada."
)
def close_order(
    order_id: int,
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.close_order(order)

# -------------------------
# Aplicar descuento
# -------------------------
@router.put(
    "/{order_id}/discount",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Aplicar descuento a orden",
    description="Aplica un descuento a la orden especificada."
)
def apply_discount(
    order_id: int,
    discount: Decimal = Query(..., ge=0),
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.apply_discount(order, discount)

# -------------------------
# Obtener ordenes activas
# -------------------------
@router.get(
    "/active",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener ordenes activas",
    description="Obtiene todas las órdenes activas del restaurante."
)
def get_active_orders(
    user: User = Depends(all_staff),
    service: OrderService = Depends(get_order_service)
):
    return service.to_order_response_list(user.restaurant_id)

# -------------------------
# Obtener orden por ID
# -------------------------
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener orden por ID",
    description="Obtiene la orden especificada por su ID."
)
def get_order(
    order_id: int,
    user: User = Depends(all_staff),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.to_order_response(order)

# -------------------------
# Actualizar cantidad de item
# -------------------------
@router.patch(
    "/order-items/{item_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar cantidad de item",
    description="Actualiza la cantidad del item especificado en la orden."
)
def update_order_item_quantity(
    item_id: int,
    quantity: int = Query(..., ge=1),
    service: OrderService = Depends(get_order_service),
    user: User = Depends(waiter_or_admin)
):
    return service.update_item_quantity(user.restaurant_id, item_id, quantity)

# -------------------------
# Cancelar orden
# -------------------------
@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancelar orden",
    description=(
        "Cancela una orden y conserva "
        "su información para auditoría."
    )
)
def cancel_order(
    order_id: int,
    data: OrderCancel,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(
        get_order_service
    )
):
    order = service.get_order(order_id, user.restaurant_id)

    return service.cancel_order(
        order=order,
        user_id=user.id,
        reason=data.reason
    )

# -------------------------
# Borrar item de orden
# -------------------------
@router.delete(
    "/{order_id}/items/{item_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Borrar item de orden",
    description="Borra el item especificado de la orden."
)
def delete_order_item(
    order_id: int,
    item_id: int,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(get_order_service)
):
    return service.delete_order_item(user.restaurant_id, order_id, item_id)

# -------------------------
# Borrar Pago
# -------------------------
@router.delete(
    "/payments/{payment_id}",
    status_code=status.HTTP_200_OK,
    summary="Borrar pago",
    description="Borra el pago especificado."
)
def delete_payment(
    payment_id: int,
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    service.delete_payment(user.restaurant_id, payment_id)
```

---

### .\backend\app\routers\order_items.py

**Funciones (2):**
- update_item_status
- cancel_order_item

**Clases (0):**

**Imports (11):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.waiter_kitchen_or_admin
- app.dependencies.roles.waiter_or_admin
- app.domain.order_item.order_item_service.OrderItemService
- app.domain.order_item.dependencies.get_order_item_service
- app.models.user.User
- app.schemas.order.order_item.OrderItemStatusUpdate
- app.schemas.order.order_item.OrderItemCancel
- app.schemas.order.order.OrderResponse

```python
"""
Endpoints para la gestión de los items de una orden.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import (
    waiter_kitchen_or_admin, 
    waiter_or_admin
)

from app.domain.order_item.order_item_service import OrderItemService
from app.domain.order_item.dependencies import get_order_item_service

from app.models.user import User

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemCancel
)

from app.schemas.order.order import OrderResponse


router = APIRouter(prefix="/order-items", tags=["order-items"])

# ----------------------------------------------------------------------------------------------------
# Cambiar estado de item
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{item_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar estado de item",
    description="Actualiza el estado del item especificado."
)
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(waiter_kitchen_or_admin),
    service: OrderItemService = Depends(get_order_item_service),
):
    service.update_status(
        item_id=item_id,
        new_status=data.status,
        user=user,
    )

# -------------------------
# Cancelar item
# -------------------------
@router.patch(
    "/{item_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancelar item",
    description=(
        "Cancela un item que ya fue enviado a cocina "
        "y conserva su registro histórico."
    )
)
def cancel_order_item(
    item_id: int,
    data: OrderItemCancel,
    user: User = Depends(waiter_or_admin),
    service: OrderItemService = Depends(
        get_order_item_service
    )
):
    return service.cancel_item(
        item_id=item_id,
        reason=data.reason,
        user=user
    )
```

---

### .\backend\app\routers\products.py

**Funciones (4):**
- create_product
- list_products
- update_product
- toggle_product

**Clases (0):**

**Imports (12):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.Query
- app.dependencies.roles.admin_only
- app.dependencies.roles.waiter_or_admin
- app.domain.product.dependencies.get_product_service
- app.domain.product.product_service.ProductService
- app.models.user.User
- app.schemas.product.ProductCreate
- app.schemas.product.ProductResponse
- app.schemas.product.ProductUpdate

```python
"""
Endpoints para la gestión de productos.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import(
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    admin_only, 
    waiter_or_admin
)

from app.domain.product.dependencies import get_product_service
from app.domain.product.product_service import ProductService

from app.models.user import User

from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])

# ----------------------------------------------------------------------------------------------------
# Crear producto
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crea un nuevo producto para el restaurante autenticado."
)
def create_product(
    product: ProductCreate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(user.restaurant_id, product)

# ----------------------------------------------------------------------------------------------------
# Listar productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Devuelve la lista de productos del restaurante autenticado."
)
def list_products(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: ProductService = Depends(get_product_service)
):
    return service.list_products(
        user.restaurant_id,
        active
    )

# ----------------------------------------------------------------------------------------------------
# Actualizar producto
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualiza un producto del restaurante autenticado."
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.update_product(product_id, user.restaurant_id, product)

# ----------------------------------------------------------------------------------------------------
# Alternar estado del producto (Activo/Inactivo)
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{product_id}/toggle",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar estado del producto",
    description="Alterna el estado de un producto (Activo/Inactivo) del restaurante autenticado."
)
def toggle_product(
    product_id: int,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.toggle_product(product_id, user.restaurant_id)
```

---

### .\backend\app\routers\reports.py

**Funciones (4):**
- sales_report
- sales_orders_report
- products_report
- product_evolution_report

**Clases (0):**

**Imports (13):**
- datetime.date
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.Query
- app.dependencies.roles.admin_only
- app.domain.reports.dependencies.get_report_service
- app.domain.reports.report_service.ReportService
- app.models.user.User
- app.schemas.reports.ProductEvolutionReportOut
- app.schemas.reports.SalesOrdersReportOut
- app.schemas.reports.ProductsReportOut
- app.schemas.reports.SalesReportOut

```python
"""
Endpoints para la gestión de reportes.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""
from datetime import date

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import admin_only

from app.domain.reports.dependencies import get_report_service
from app.domain.reports.report_service import ReportService

from app.models.user import User

from app.schemas.reports import (
    ProductEvolutionReportOut,
    SalesOrdersReportOut,
    ProductsReportOut,
    SalesReportOut
)

router = APIRouter(prefix="/reports", tags=["reports"])

# ----------------------------------------------------------------------------------------------------
# Reporte de Ventas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/sales",
    response_model=SalesReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de ventas",
    description="Reporte conteniendo la evolución de las ventas en un período determinado.")
def sales_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de ventas por orden
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/sales/orders",
    response_model=SalesOrdersReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de ventas por orden",
    description="Reporte con listado de ventas realizadas en un período determinado."
)
def sales_orders_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_orders_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de productos más y menos vendidos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/products",
    response_model=ProductsReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de productos más y menos vendidos",
    description="Reporte conteniendo el top 10 de los productos más y menos vendidos en un período determinado."
)
def products_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    category_id: int | None = Query(None, description="Filtrar por categoría."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_products_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de evolución de productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/products/{product_id}/evolution",
    response_model=ProductEvolutionReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de evolución de las ventas de un producto",
    description="Reporte conteniendo la evolución de las ventas de un producto seleccionado en un período determinado."
)
def product_evolution_report(
    product_id: int,
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_product_evolution_report(
        restaurant_id=user.restaurant_id,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )
```

---

### .\backend\app\routers\stations.py

**Funciones (6):**
- create_station
- list_stations
- list_active_stations
- get_station
- update_station
- toggle_station

**Clases (0):**

**Imports (12):**
- fastapi.APIRouter
- fastapi.status
- fastapi.Depends
- fastapi.Query
- app.dependencies.roles.admin_only
- app.dependencies.roles.kitchen_or_admin
- app.domain.stations.dependencies.get_station_service
- app.domain.stations.station_service.StationService
- app.models.user.User
- app.schemas.station.StationCreate
- app.schemas.station.StationResponse
- app.schemas.station.StationUpdate

```python
"""
Endpoints para la gestión de estaciones.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter,
    status, 
    Depends, 
    Query
)

from app.dependencies.roles import (
    admin_only, 
    kitchen_or_admin
)

from app.domain.stations.dependencies import get_station_service
from app.domain.stations.station_service import StationService

from app.models.user import User

from app.schemas.station import (
    StationCreate,
    StationResponse,
    StationUpdate,
)

router = APIRouter(prefix="/stations", tags=["stations"])

# ----------------------------------------------------------------------------------------------------
# Crear estación
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear estación",
    description="Crea una nueva estación para el restaurante autenticado."
)
def create_station(
    data: StationCreate,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.create_station(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar estaciones
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estaciones",
    description="Devuelve la lista de estaciones del restaurante autenticado."
)
def list_stations(
    active: bool | None = Query(default=True),
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar estaciones activas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/active",
    response_model=list[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estaciones activas",
    description="Devuelve la lista de estaciones activas del restaurante autenticado."
)
def list_active_stations(
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Obtener estación
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estación",
    description="Devuelve una estación específica del restaurante autenticado."
)
def get_station(
    station_id: int,
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.get_station(user.restaurant_id, station_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar estación
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estación",
    description="Actualiza la información de una estación específica del restaurante autenticado."
)
def update_station(
    station_id: int,
    data: StationUpdate,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.update_station(user.restaurant_id, station_id, data)

# ----------------------------------------------------------------------------------------------------
# Alternar estado de estación
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{station_id}/toggle",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar estado de estación",
    description="Alterna el estado de una estación específica del restaurante autenticado."
)
def toggle_station(
    station_id: int,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.toggle_station(user.restaurant_id, station_id)
```

---

### .\backend\app\routers\system_settings.py

**Funciones (3):**
- test_email
- get_settings
- update_settings

**Clases (0):**

**Imports (10):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.admin_only
- app.domain.settings.dependencies.get_settings_service
- app.domain.settings.settings_service.SettingsService
- app.models.user.User
- app.schemas.system_settings.SettingsUpdateRequest
- app.schemas.system_settings.SettingsResponse
- app.schemas.system_settings.EmailTestResponse

```python
"""
Endpoints para la gestión de la configuración del sistema.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import admin_only

from app.domain.settings.dependencies import get_settings_service

from app.domain.settings.settings_service import SettingsService

from app.models.user import User

from app.schemas.system_settings import (
    SettingsUpdateRequest,
    SettingsResponse,
    EmailTestResponse
)

router = APIRouter(prefix="/settings", tags=["settings"])

# ----------------------------------------------------------------------------------------------------
# Testear correo electrónico configurado
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/test-email",
    response_model=EmailTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Testear el e-mail",
    description="Testea el correo electrónico configurado enviando un correo de prueba.")
def test_email(
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    return service.send_test_email(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Obtener settings del sistema
# ----------------------------------------------------------------------------------------------------
@router.get(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener settings",
    description="Obtiene las settings del sistema."
)
def get_settings(
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    settings = service.get_settings(user.restaurant_id)
    return service.to_response(settings)

# ----------------------------------------------------------------------------------------------------
# Actualizar settings del sistema
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar settings",
    description="Actualiza settings del sistema.")
def update_settings(
    data: SettingsUpdateRequest,
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    settings = service.update_settings(user.restaurant_id, data)
    return service.to_response(settings)
```

---

### .\backend\app\routers\tables.py

**Funciones (9):**
- create_table
- touch_table
- add_product_to_order
- list_tables
- list_tables_status
- update_position
- activate_table
- update_table
- deactivate_table

**Clases (0):**

**Imports (20):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- fastapi.Query
- app.dependencies.roles.waiter_or_admin
- app.dependencies.roles.admin_only
- app.domain.table.table_service.TableService
- app.domain.table.dependencies.get_table_service
- app.domain.order.order_service.OrderService
- app.domain.order.dependencies.get_order_service
- app.models.user.User
- app.schemas.table.TableCreate
- app.schemas.table.TableResponse
- app.schemas.table.TableUpdate
- app.schemas.table.TableList
- app.schemas.table.TableStatusResponse
- app.schemas.table.TablePositionUpdate
- app.schemas.table.TablePositionOut
- app.schemas.table.TableTouchResponse
- app.schemas.order.order_item.OrderItemCreate

```python
"""
Endpoints para la gestión de mesas.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    waiter_or_admin, 
    admin_only
)

from app.domain.table.table_service import TableService
from app.domain.table.dependencies import get_table_service
from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User

from app.schemas.table import (
    TableCreate,
    TableResponse,
    TableUpdate,
    TableList,
    TableStatusResponse,
    TablePositionUpdate,
    TablePositionOut,
    TableTouchResponse
)

from app.schemas.order.order_item import OrderItemCreate

router = APIRouter(prefix="/tables", tags=["tables"])

# ----------------------------------------------------------------------------------------------------
# Crear mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear mesa",
    description="Crea una nueva mesa para el restaurante autenticado."
)
def create_table(
    data: TableCreate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.create_table(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Tocar mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/{table_id}/touch",
    response_model=TableTouchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tocar mesa",
    description="Accede a una mesa para realizar operaciones."
)
def touch_table(
    table_id: int,
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.touch_table(user.restaurant_id, table_id)

# ----------------------------------------------------------------------------------------------------
# Agregar producto a la orden de la mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/{table_id}/add-product",
    status_code=status.HTTP_200_OK,
    summary="Agregar producto a la orden",
    description="Agrega un producto a la orden abierta de una mesa."
)
def add_product_to_order(
    table_id: int,
    data: OrderItemCreate,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(get_order_service)
):
    return service.add_product_to_order(
        restaurant_id=user.restaurant_id,
        table_id=table_id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Listar mesas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[TableList],
    status_code=status.HTTP_200_OK,
    summary="Listar mesas",
    description="Lista todas las mesas del restaurante autenticado."
)
def list_tables(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar estado de las mesas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/status",
    response_model=list[TableStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estado de las mesas",
    description="Lista el estado de todas las mesas del restaurante autenticado."
)
def list_tables_status(
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables_status(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Modificar posición de la mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}/position",
    response_model=TablePositionOut,
    status_code=status.HTTP_200_OK,
    summary="Modificar posición de la mesa",
    description="Modifica la posición de una mesa específica del restaurante autenticado."
)
def update_position(
    table_id: int,
    data: TablePositionUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_position(user.restaurant_id, table_id, data)

# ----------------------------------------------------------------------------------------------------
# Activar mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}/activate",
    status_code=status.HTTP_200_OK,
    summary="Activar mesa",
    description="Activa una mesa específica del restaurante autenticado."
)
def activate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.activate_table(user.restaurant_id, table_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar mesa",
    description="Actualiza la información de una mesa específica del restaurante autenticado."
)
def update_table(
    table_id: int,
    data: TableUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_table(user.restaurant_id, table_id, data)

# ----------------------------------------------------------------------------------------------------
# Desactivar mesa
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar mesa",
    description="Desactiva una mesa específica del restaurante autenticado."
)
def deactivate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.deactivate_table(user.restaurant_id, table_id)
```

---

### .\backend\app\routers\users.py

**Funciones (4):**
- create_user
- list_users
- update_user
- toggle_user

**Clases (0):**

**Imports (10):**
- fastapi.APIRouter
- fastapi.Depends
- fastapi.status
- app.dependencies.roles.admin_only
- app.domain.user.user_service.UserService
- app.domain.user.dependencies.get_user_service
- app.models.user.User
- app.schemas.user.UserCreate
- app.schemas.user.UserUpdate
- app.schemas.user.UserOut

```python
"""
Endpoints para la gestión de los usuarios del sistema.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import admin_only

from app.domain.user.user_service import UserService
from app.domain.user.dependencies import get_user_service

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserOut
)

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------------------------------------------------------------------------------------
# Crear usuario
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un usuario en el sistema."
)
def create_user(
    data: UserCreate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar usuarios del sistema
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Lista los usuarios del sistema."
)
def list_users(
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.list_users(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualiza un usuario
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description="Actualiza un usuario del sistema."
)
def update_user(
    user_id: int,
    data: UserUpdate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user_id, user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Activa/Desactiva un usuario
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{user_id}/toggle",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Activar/Desactivar usuario",
    description="Activa o desactiva a un usuario del sistema."
)
def toggle_user(
    user_id: int,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.toggle_user(user_id, user.id, user.restaurant_id)
```

---

### .\backend\app\scheduler\backup_jobs.py

**Funciones (2):**
- register_jobs
- scheduled_backup_job

**Clases (0):**

**Imports (4):**
- sqlalchemy.orm.Session
- app.db.session.SessionLocal
- app.domain.backup.backup_service.BackupService
- app.scheduler.scheduler.scheduler

```python
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain.backup.backup_service import BackupService
from app.scheduler.scheduler import scheduler


# --------------------------------------------------------------------------------------
# Registra las tareas programadas relacionadas con los backups.
# --------------------------------------------------------------------------------------
def register_jobs() -> None:
    scheduler.add_job(
        scheduled_backup_job,
        trigger="interval",
        minutes=1,
        id="backup_scheduler",
        replace_existing=True,
    )


# --------------------------------------------------------------------------------------
# Ejecuta la comprobación de backups pendientes.
# Crea una sesión independiente de base de datos para el scheduler.
# --------------------------------------------------------------------------------------
def scheduled_backup_job() -> None:

    db: Session = SessionLocal()

    try:
        BackupService(db).run_pending_backups()

    finally:
        db.close()
```

---

### .\backend\app\scheduler\scheduler.py

**Funciones (0):**

**Clases (0):**

**Imports (1):**
- apscheduler.schedulers.background.BackgroundScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler

# --------------------------------------------------------------------------------------
# Scheduler global utilizado para registrar y ejecutar tareas programadas.
# Todas las fechas se manejan internamente en UTC.
# --------------------------------------------------------------------------------------
scheduler: BackgroundScheduler = BackgroundScheduler(
    timezone="UTC"
)
```

---

### .\backend\app\schemas\auth.py

**Funciones (0):**

**Clases (1):**
- TokenResponse

**Imports (1):**
- pydantic.BaseModel

```python
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

```

---

### .\backend\app\schemas\backup.py

**Funciones (0):**

**Clases (7):**
- BackupEmailRequest
- BackupInfoOut
- BackupFileOut
- BackupStatusOut
- BackupEmailOut
- BackupDeleteOut
- BackupRestoreOut

**Imports (3):**
- datetime.datetime
- base.BaseSchema
- pydantic.EmailStr

```python
from datetime import datetime

from .base import BaseSchema
from pydantic import EmailStr


# -------------------------------------------------------------------
# Request
# -------------------------------------------------------------------
class BackupEmailRequest(BaseSchema):
    email: EmailStr

# -------------------------------------------------------------------
# Reusable
# -------------------------------------------------------------------
class BackupInfoOut(BaseSchema):
    last_backup_at: datetime
    last_backup_file: str
    last_backup_size: int
    type: str


class BackupFileOut(BaseSchema):
    filename: str
    created_at: datetime
    size: int
    type: str

# -------------------------------------------------------------------
# Status
# -------------------------------------------------------------------
class BackupStatusOut(BaseSchema):
    last_backup_at: datetime | None
    last_backup_file: str | None
    last_backup_size: int | None
    last_backup_source: str | None

    email_enabled: bool
    email_from: str | None

    last_automatic_backup_at: datetime | None
    next_automatic_backup_at: datetime | None

    last_backup_result: str | None

# -------------------------------------------------------------------
# Responses
# -------------------------------------------------------------------
class BackupEmailOut(BackupInfoOut):
    sent_to: EmailStr


class BackupDeleteOut(BaseSchema):
    success: bool


class BackupRestoreOut(BaseSchema):
    success: bool
    restart_required: bool
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
- CashRegisterResponse
- CashRegisterSummary
- CashRegisterCloseOut
- CashRegisterClose
- CashMovementCreate
- CashMovementOut
- CashRegisterDashboard

**Imports (5):**
- datetime.datetime
- decimal.Decimal
- pydantic.Field
- base.BaseSchema
- app.models.cash_movement.CashMovementType

```python
from datetime import datetime
from decimal import Decimal
from pydantic import Field
from .base import BaseSchema
from app.models.cash_movement import CashMovementType


class CashRegisterOpen(BaseSchema):
    opening_amount: Decimal = Field(ge=Decimal("0"))


class CashRegisterResponse(BaseSchema):
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

class CashRegisterCloseOut(BaseSchema):
    message: str
    total_sales: Decimal
    transactions_count: int
    by_method: dict[str, Decimal]
    opening_amount: Decimal
    closing_amount: Decimal
    cash_in: Decimal
    cash_out: Decimal
    expected_cash: Decimal
    counted_cash: Decimal
    difference: Decimal


class CashRegisterClose(BaseSchema):
    counted_cash: Decimal = Field(ge=Decimal("0"))


class CashMovementCreate(BaseSchema):
    type: CashMovementType
    amount: Decimal = Field(gt=Decimal("0"))
    reason: str


class CashMovementOut(BaseSchema):
    id: int
    type: CashMovementType
    amount: Decimal
    reason: str | None
    created_at: datetime


class CashRegisterDashboard(BaseSchema):
    cash_register_id: int
    opened_at: datetime
    opening_amount: Decimal
    total_sales: Decimal
    orders_count: int
    transactions_count: int
    average_ticket: Decimal
    by_method: dict[str, Decimal]
    cash_movements: list[CashMovementOut]
    expected_cash: Decimal
```

---

### .\backend\app\schemas\category.py

**Funciones (0):**

**Clases (6):**
- ProductRef
- CategoryCreate
- CategoryUpdate
- CategoryRef
- CategoryResponse
- CategoryWithProducts

**Imports (3):**
- decimal.Decimal
- pydantic.Field
- base.BaseSchema

```python
from decimal import Decimal
from pydantic import Field
from .base import BaseSchema

class ProductRef(BaseSchema):
    id: int
    name: str
    price: Decimal

class CategoryCreate(BaseSchema):
    name: str

class CategoryUpdate(BaseSchema):
    name: str

class CategoryRef(BaseSchema):
    id: int
    name: str

class CategoryResponse(CategoryRef):
    active: bool

class CategoryWithProducts(CategoryResponse):
    products: list[ProductRef] = Field(default_factory=list)
```

---

### .\backend\app\schemas\layout.py

**Funciones (0):**

**Clases (2):**
- LayoutOut
- LayoutUpdate

**Imports (2):**
- pydantic.Field
- base.BaseSchema

```python
from pydantic import Field

from .base import BaseSchema

class LayoutOut(BaseSchema):
    restaurant_id: int
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool
    background_image: str | None = None


class LayoutUpdate(BaseSchema):
    width: int | None = None
    height: int | None = None
    grid_size: int | None = None
    snap_to_grid: bool | None = None
    background_image: str | None = None
```

---

### .\backend\app\schemas\product.py

**Funciones (0):**

**Clases (3):**
- ProductCreate
- ProductUpdate
- ProductResponse

**Imports (4):**
- decimal.Decimal
- base.BaseSchema
- category.CategoryRef
- station.StationRef

```python
from decimal import Decimal
from .base import BaseSchema
from .category import CategoryRef
from .station import StationRef

class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int

class ProductUpdate(BaseSchema):
    name: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    station_id: int | None = None

class ProductResponse(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int
    active: bool
    category: CategoryRef
    station: StationRef
```

---

### .\backend\app\schemas\reports.py

**Funciones (0):**

**Clases (9):**
- SalesOrderItemOut
- SalesOrderOut
- SalesOrdersReportOut
- ProductEvolutionPoint
- ProductEvolutionReportOut
- ProductSummaryOut
- ProductsReportOut
- SalesPointOut
- SalesReportOut

**Imports (5):**
- decimal.Decimal
- datetime.datetime
- datetime.date
- base.BaseSchema
- order.order_item.OrderItemOut

```python
from decimal import Decimal
from datetime import datetime, date
from .base import BaseSchema
from .order.order_item import OrderItemOut

class SalesOrderItemOut(BaseSchema):
    item_id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal

class SalesOrderOut(BaseSchema):
    order_id: int
    table_number: int | None
    closed_at: datetime | None
    items: list[SalesOrderItemOut]
    subtotal: Decimal
    discount: Decimal
    total: Decimal

class SalesOrdersReportOut(BaseSchema):
    orders: list[SalesOrderOut]

class ProductEvolutionPoint(BaseSchema):
    date: date
    total: Decimal

class ProductEvolutionReportOut(BaseSchema):
    series: list[ProductEvolutionPoint]

class ProductSummaryOut(BaseSchema):
    product_id: int
    name: str
    category_id: int
    quantity: int
    total: Decimal

class ProductsReportOut(BaseSchema):
    today_best_seller: ProductSummaryOut | None
    top_products: list[ProductSummaryOut]
    least_products: list[ProductSummaryOut]

class SalesPointOut(BaseSchema):
    date: date
    total: Decimal

class SalesReportOut(BaseSchema):
    series: list[SalesPointOut]
    max_day: SalesPointOut | None
    min_day: SalesPointOut | None
```

---

### .\backend\app\schemas\station.py

**Funciones (0):**

**Clases (4):**
- StationCreate
- StationUpdate
- StationRef
- StationResponse

**Imports (1):**
- base.BaseSchema

```python
from .base import BaseSchema

class StationCreate(BaseSchema):
    name: str

class StationUpdate(BaseSchema):
    name: str

class StationRef(BaseSchema):
    id: int
    name: str

class StationResponse(BaseSchema):
    id: int
    name: str
    active: bool
```

---

### .\backend\app\schemas\system_settings.py

**Funciones (0):**

**Clases (3):**
- SettingsUpdateRequest
- SettingsResponse
- EmailTestResponse

**Imports (6):**
- pydantic.Field
- pydantic.EmailStr
- base.BaseSchema
- datetime.datetime
- datetime.time
- app.models.enums.BackupFrequency

```python
from pydantic import Field, EmailStr

from .base import BaseSchema
from datetime import datetime, time
from app.models.enums import BackupFrequency

class SettingsUpdateRequest(BaseSchema):
    smtp_host: str | None = None
    smtp_port: int | None = Field(ge=1, le=65535)
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: EmailStr | None = None
    smtp_use_tls: bool = True

    backup_email: EmailStr | None = None

    backup_enabled: bool = False
    backup_frequency: BackupFrequency = BackupFrequency.MANUAL

    backup_time: time | None = None
    backup_weekday: int | None = Field(default=None, ge=0, le=6)
    backup_monthday: int | None = Field(default=None, ge=1, le=31)

    backup_retention_daily: int = Field(default=30, ge=1)
    backup_retention_weekly: int = Field(default=12, ge=1)
    backup_retention_monthly: int = Field(default=24, ge=1)
    backup_keep_local: bool = True
    backup_send_email: bool = True

    backup_timezone: str = "America/Montevideo"


class SettingsResponse(BaseSchema):

    smtp_host: str | None
    smtp_port: int | None
    smtp_user: str | None

    smtp_from: EmailStr | None
    smtp_use_tls: bool

    smtp_password_configured: bool

    backup_email: EmailStr | None

    backup_enabled: bool
    backup_frequency: BackupFrequency

    backup_time: time | None
    backup_weekday: int | None
    backup_monthday: int | None

    backup_retention_daily: int
    backup_retention_weekly: int
    backup_retention_monthly: int

    backup_keep_local: bool
    backup_send_email: bool

    backup_timezone: str

    last_automatic_backup_at: datetime | None
    next_automatic_backup_at: datetime | None
    last_backup_result: str | None

class EmailTestResponse(BaseSchema):
    success: bool
    sent_to: str
```

---

### .\backend\app\schemas\table.py

**Funciones (0):**

**Clases (8):**
- TableCreate
- TableResponse
- TableUpdate
- TableStatusResponse
- TableList
- TablePositionUpdate
- TablePositionOut
- TableTouchResponse

**Imports (3):**
- app.models.order.OrderStatus
- base.BaseSchema
- app.models.enums.TableShape

```python
from app.models.order import OrderStatus
from .base import BaseSchema
from app.models.enums import TableShape

class TableCreate(BaseSchema):
    number: int | None = None
    x: int = 0
    y: int = 0
    capacity: int = 4
    shape: TableShape = TableShape.CIRCLE

class TableResponse(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: TableShape
    active: bool

class TableUpdate(BaseSchema):
    number: int | None = None
    capacity: int | None = None
    shape: TableShape | None = None
    active: bool | None = None

class TableStatusResponse(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: TableShape
    active: bool
    order_id: int | None
    order_status: OrderStatus | None

class TableList(BaseSchema):
    id: int
    number: int
    capacity: int
    shape: TableShape
    active: bool

class TablePositionUpdate(BaseSchema):
    x: int
    y: int

class TablePositionOut(BaseSchema):
    id: int
    x: int
    y: int

class TableTouchResponse(BaseSchema):
    table_id: int
    table_number: int
    order_id: int | None
```

---

### .\backend\app\schemas\user.py

**Funciones (4):**
- validate_username
- validate_password
- validate_username
- validate_password

**Clases (3):**
- UserCreate
- UserUpdate
- UserOut

**Imports (6):**
- re
- pydantic.SecretStr
- pydantic.ConfigDict
- pydantic.field_validator
- base.BaseSchema
- app.models.user.UserRole

```python
import re

from pydantic import SecretStr, ConfigDict, field_validator

from .base import BaseSchema
from app.models.user import UserRole

USERNAME_RE = re.compile(r"^[a-z0-9_.-]+$")

class UserCreate(BaseSchema):
    username: str
    password: SecretStr
    role: UserRole

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.lower()
        if not USERNAME_RE.fullmatch(value):
            raise ValueError(
                "Username may only contain lowercase letters, numbers, '.', '-' and '_'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()
        if len(password) < 4:
            raise ValueError("Password must contain at least 4 characters.")
        return value


class UserUpdate(BaseSchema):
    username: str | None = None
    password: SecretStr | None = None
    role: UserRole | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if not USERNAME_RE.fullmatch(value):
            raise ValueError(
                "Username may only contain lowercase letters, numbers, '.', '-' and '_'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        password = value.get_secret_value()
        if len(password) < 4:
            raise ValueError("Password must contain at least 4 characters.")
        return value

class UserOut(BaseSchema):
    id: int
    username: str
    role: UserRole
    active: bool
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
    notes: str | None = None
```

---

### .\backend\app\schemas\order\order.py

**Funciones (0):**

**Clases (3):**
- OrderResponse
- OrderStatusUpdate
- OrderCancel

**Imports (7):**
- decimal.Decimal
- pydantic.Field
- app.models.order.OrderStatus
- datetime.datetime
- base.BaseSchema
- order_item.OrderItemOut
- payment.PaymentOut

```python
from decimal import Decimal
from pydantic import Field
from app.models.order import OrderStatus
from datetime import datetime
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderResponse(BaseSchema):
    id: int
    table_id: int
    table_number: int
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    total_paid: Decimal
    remaining: Decimal

class OrderStatusUpdate(BaseSchema):
    status: OrderStatus

class OrderCancel(BaseSchema):
    reason: str = Field(
        min_length=1,
        max_length=500
    )
```

---

### .\backend\app\schemas\order\order_item.py

**Funciones (0):**

**Clases (4):**
- OrderItemCreate
- OrderItemStatusUpdate
- OrderItemOut
- OrderItemCancel

**Imports (4):**
- decimal.Decimal
- app.models.order_item.OrderItemStatus
- base.BaseSchema
- pydantic.Field

```python
from decimal import Decimal
from app.models.order_item import OrderItemStatus
from ..base import BaseSchema
from pydantic import Field

class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int
    notes: str | None = None


class OrderItemStatusUpdate(BaseSchema):
    status: OrderItemStatus


class OrderItemOut(BaseSchema):
    id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    status: OrderItemStatus
    notes: str | None = None

class OrderItemCancel(BaseSchema):
    reason: str = Field(
        min_length=1,
        max_length=500
    )
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

### .\backend\app\services\event_cleanup.py

**Funciones (3):**
- __init__
- run
- cleanup

**Clases (1):**
- EventCleanup

**Imports (9):**
- asyncio
- logging
- sqlalchemy.and_
- sqlalchemy.orm.Session
- datetime.datetime
- datetime.timedelta
- datetime.timezone
- app.db.session.SessionLocal
- app.models.event_outbox.EventOutbox

```python
import asyncio
import logging

from sqlalchemy import and_
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.event_outbox import EventOutbox

logger = logging.getLogger("app.event_cleanup")

# --------------------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------------------
PROCESSED_RETENTION_DAYS = 3
FAILED_RETENTION_DAYS = 7
FAILED_MAX_RETRIES = 10

# --------------------------------------------------------------------------------------
# Servicio encargado de eliminar eventos antiguos del EventOutbox.
# --------------------------------------------------------------------------------------
class EventCleanup:

    """
    Elimina periódicamente eventos antiguos del EventOutbox para evitar
    el crecimiento indefinido de la tabla.
    """
    
    def __init__(self, interval_seconds=3600) ->None:
        self.interval = interval_seconds

# --------------------------------------------------------------------------------------
# Ejecuta el proceso de limpieza periódicamente.
# --------------------------------------------------------------------------------------
    async def run(self) -> None:
        logger.info("Event cleanup job started")
        while True:
            try:
                await asyncio.sleep(self.interval)
                self.cleanup()
            except asyncio.CancelledError:
                logger.info("Event cleanup stopped")
                raise
            except Exception:
                logger.exception("Cleanup job failed")

# --------------------------------------------------------------------------------------
# Elimina eventos procesados y fallidos que ya no deben conservarse.
# --------------------------------------------------------------------------------------
    def cleanup(self) -> None:
        db: Session = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            processed_cutoff = now - timedelta(days=PROCESSED_RETENTION_DAYS)
            failed_cutoff = now - timedelta(days=FAILED_RETENTION_DAYS)
            # Eliminar eventos procesados antiguos.
            processed_deleted = (
                db.query(EventOutbox)
                .filter(
                    and_(
                        EventOutbox.status == "processed",
                        EventOutbox.processed_at < processed_cutoff
                    )
                )
                .delete(synchronize_session=False)
            )
            # Eliminar eventos fallidos que ya no volverán a reintentarse.
            failed_deleted = (
                db.query(EventOutbox)
                .filter(
                    and_(
                        EventOutbox.status == "failed",
                        EventOutbox.retries >= FAILED_MAX_RETRIES,
                        EventOutbox.created_at < failed_cutoff
                    )
                )
                .delete(synchronize_session=False)
            )
            db.commit()
            total = processed_deleted + failed_deleted
            if not total:
                return

            logger.info(
                "event_cleanup_completed processed=%s failed=%s total=%s",
                processed_deleted,
                failed_deleted,
                total,
            )
        except Exception:
            db.rollback()
            logger.exception("event_cleanup_failed")
        finally:
            db.close()
```

---

### .\backend\app\services\event_service.py

**Funciones (2):**
- __init__
- emit

**Clases (1):**
- EventService

**Imports (3):**
- typing.Any
- sqlalchemy.orm.Session
- app.models.event_outbox.EventOutbox

```python
from typing import Any

from sqlalchemy.orm import Session

from app.models.event_outbox import EventOutbox


class EventService:
    """
    Servicio encargado de registrar eventos en la tabla EventOutbox.

    Los eventos son procesados posteriormente por el EventWorker,
    que los publica en Redis y actualiza su estado.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------------
    # Registra un evento pendiente para ser procesado por el EventWorker.
    # --------------------------------------------------------------------------------------
    def emit(
        self,
        restaurant_id: int,
        event_type: str,
        payload: dict[str, Any],
        target: str = "broadcast",
        target_id: str | None = None,
    ) -> None:

        event = EventOutbox(
            restaurant_id=restaurant_id,
            event_type=event_type,
            payload=payload,
            target=target,
            target_id=target_id,
            status="pending",
            retries=0,
        )

        self.db.add(event)
```

---

### .\backend\app\services\event_worker.py

**Funciones (3):**
- run
- _process_batch
- _deliver_event

**Clases (1):**
- EventWorker

**Imports (14):**
- asyncio
- json
- logging
- uuid
- datetime.datetime
- datetime.timezone
- typing.Any
- sqlalchemy.select
- sqlalchemy.orm.Session
- app.db.session.SessionLocal
- app.websocket.manager.manager
- app.core.redis.redis_client
- app.models.user.UserRole
- app.models.event_outbox.EventOutbox

```python
import asyncio
import json
import logging
import uuid

from datetime import datetime, timezone

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.websocket.manager import manager
from app.core.redis import redis_client

from app.models.user import UserRole
from app.models.event_outbox import EventOutbox


INSTANCE_ID = str(uuid.uuid4())

logger = logging.getLogger("app.event_worker")

# --------------------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------------------
POLL_INTERVAL = 0.5
BATCH_SIZE = 50

MAX_RETRIES = 6
BASE_RETRY_DELAY = 2

EVENT_TTL_HOURS = 48 # Utilizada por la tarea periódica que elimina eventos antiguos.


class EventWorker:
    """
    Procesa los eventos pendientes almacenados en la tabla EventOutbox.

    Su responsabilidad es:

    - entregar eventos a los clientes WebSocket locales;
    - replicarlos mediante Redis para otras instancias;
    - gestionar reintentos automáticos;
    - marcar los eventos como procesados o fallidos.
    """

# --------------------------------------------------------------------------------------
# Inicia el ciclo principal del EventWorker.
# --------------------------------------------------------------------------------------
    async def run(self) -> None:
        logger.info("EventWorker started")
        while True:
            try:
                await self._process_batch()
            except Exception:
                logger.exception("EventWorker loop error")
            await asyncio.sleep(POLL_INTERVAL)

# --------------------------------------------------------------------------------------
# Procesa un lote de eventos pendientes.
# --------------------------------------------------------------------------------------
    async def _process_batch(self) -> None:
        db: Session = SessionLocal()
        try:
            stmt = (
                select(EventOutbox)
                .where(EventOutbox.status == "pending")
                .order_by(EventOutbox.id)
                .limit(BATCH_SIZE)
                .with_for_update(skip_locked=True)
            )
            events = db.execute(stmt).scalars().all()
            if not events:
                return None
            for event in events:
                try:
                    await self._deliver_event(event)
                    event.status = "processed"
                    event.processed_at = datetime.now(timezone.utc)
                except Exception as e:
                    event.retries += 1
                    event.last_error = str(e)
                    if event.retries >= MAX_RETRIES:
                        event.status = "failed"
                        logger.error(
                            "Event failed permanently id=%s type=%s",
                            event.id,
                            event.event_type
                        )
                    else:
                        delay = BASE_RETRY_DELAY ** event.retries
                        logger.warning(
                            "Event retry id=%s attempt=%s delay=%ss",
                            event.id,
                            event.retries,
                            delay
                        )
                        await asyncio.sleep(delay)
                db.commit()
        finally:
            db.close()

# --------------------------------------------------------------------------------------
# Entrega un evento mediante WebSocket y lo replica en Redis.
# --------------------------------------------------------------------------------------
    async def _deliver_event(self, event: EventOutbox,) -> None:
        payload = event.payload or {}
        message = {
            "type": event.event_type,
            "payload": payload
        }
        # ---- websocket delivery ----
        if event.target == "broadcast":
            await manager.broadcast(
                event.restaurant_id,
                message
            )
        elif event.target == "role":
            await manager.send_to_role(
                event.restaurant_id,
                UserRole(event.target_id),
                message
            )
        elif event.target == "station":
            station_payload = {
                **payload,
                "station_id": int(event.target_id)
            }
            await manager.send_to_role(
                event.restaurant_id,
                UserRole.KITCHEN,
                {
                    "type": event.event_type,
                    "payload": station_payload
                }
            )

        # ---- redis replication ----

        await redis_client.publish(
            "restaurant_events",
            json.dumps({
                "origin": INSTANCE_ID,
                "restaurant_id": event.restaurant_id,
                "event_type": event.event_type,
                "payload": payload,
                "target": event.target,
                "target_id": event.target_id
            })
        )

```

---

### .\backend\app\utils\money.py

**Funciones (2):**
- to_decimal
- money

**Clases (0):**

**Imports (3):**
- decimal.Decimal
- decimal.ROUND_HALF_UP
- typing.Any

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

TWOPLACES = Decimal("0.01")


# --------------------------------------------------------------------------------------
# Convierte un valor a Decimal de forma segura.
# --------------------------------------------------------------------------------------
def to_decimal(value: Any) -> Decimal:
    """
    Convierte cualquier valor numérico compatible a Decimal.
    """
    return Decimal(str(value))


# --------------------------------------------------------------------------------------
# Devuelve un valor monetario con dos decimales utilizando ROUND_HALF_UP.
# --------------------------------------------------------------------------------------
def money(value: Any) -> str:
    """
    Convierte un valor numérico a su representación monetaria.
    """

    if value is None:
        value = Decimal("0")

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return str(
        value.quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )
    )
```

---

### .\backend\app\websocket\manager.py

**Funciones (6):**
- __init__
- connect
- disconnect
- send_to_role
- broadcast
- _safe_send

**Clases (1):**
- ConnectionManager

**Imports (6):**
- logging
- fastapi.WebSocket
- collections.defaultdict
- typing.Any
- app.models.user.User
- app.models.user.UserRole

```python
import logging

from fastapi import WebSocket
from collections import defaultdict
from typing import Any

from app.models.user import User, UserRole


logger = logging.getLogger("app.websocket.manager")

MAX_CONNECTIONS_PER_USER = 3


class ConnectionManager:
    """
    Administra las conexiones WebSocket activas.

    Mantiene índices por restaurante, rol y usuario para facilitar
    el envío eficiente de mensajes.
    """

    def __init__(self) -> None:
        # websocket_id -> connection
        self._ws_index: dict[int, dict[str, Any]] = {}

        # restaurant -> connections
        self._by_restaurant: defaultdict[int, set[int]] = defaultdict(set)

        # restaurant -> role -> connections
        self._by_role: defaultdict[int, defaultdict[UserRole, set[int]]] = \
            defaultdict(lambda: defaultdict(set))

        # user -> connection_count
        self._user_connections: defaultdict[int, int] = defaultdict(int)

# --------------------------------------------------------------------------------------
# Acepta una nueva conexión WebSocket autenticada.
# --------------------------------------------------------------------------------------
    async def connect(self, websocket: WebSocket, user: User,) -> bool:

        if self._user_connections[user.id] >= MAX_CONNECTIONS_PER_USER:
            logger.warning(
                "WS rejected user=%s reason=max_connections",
                user.id
            )
            await websocket.close(code=1008)
            return False

        await websocket.accept()

        conn = {
            "ws": websocket,
            "user": user
        }

        ws_id = id(websocket)

        self._ws_index[ws_id] = conn
        self._by_restaurant[user.restaurant_id].add(ws_id)
        self._by_role[user.restaurant_id][user.role].add(ws_id)

        self._user_connections[user.id] += 1

        logger.info(
            "WS connected r=%s user=%s role=%s",
            user.restaurant_id,
            user.id,
            user.role
        )

        return True

# --------------------------------------------------------------------------------------
# Elimina una conexión WebSocket.
# --------------------------------------------------------------------------------------
    def disconnect(self, websocket: WebSocket):

        ws_id = id(websocket)

        conn = self._ws_index.pop(ws_id, None)

        if not conn:
            return

        user = conn["user"]
        restaurant_id = user.restaurant_id

        self._by_restaurant[restaurant_id].discard(ws_id)

        self._by_role[restaurant_id][user.role].discard(ws_id)

        self._user_connections[user.id] -= 1

        if self._user_connections[user.id] <= 0:
            del self._user_connections[user.id]

        logger.info(
            "WS disconnected r=%s user=%s",
            restaurant_id,
            user.id
        )

# --------------------------------------------------------------------------------------
# Envía un mensaje a todos los usuarios de un rol.
# --------------------------------------------------------------------------------------
    async def send_to_role(
        self,
        restaurant_id: int,
        role: UserRole,
        message: dict
    ):

        targets = list(self._by_role[restaurant_id].get(role, []))

        if not targets:
            logger.warning(
                "WS role send: no targets restaurant=%s role=%s message=%s",
                restaurant_id,
                role,
                message["type"]
            )
            return

        logger.debug("WS role send: r=%s role=%s connections=%s", restaurant_id, role, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

# --------------------------------------------------------------------------------------
# Envía un mensaje a todos los usuarios.
# --------------------------------------------------------------------------------------
    async def broadcast(
        self,
        restaurant_id: int,
        message: dict
    ):
        targets = list(self._by_restaurant.get(restaurant_id, []))
        logger.debug("WS broadcast: r=%s connections=%s", restaurant_id, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

# --------------------------------------------------------------------------------------
# Envía un mensaje
# --------------------------------------------------------------------------------------
    async def _safe_send(self, ws_id: int, message: dict):
        conn = self._ws_index.get(ws_id)
        if not conn:
            return
        ws = conn["ws"]
        try:
            logger.info("WS send: ws_id=%s type=%s", ws_id, message["type"])
            await ws.send_json(message)
        except Exception:
            logger.exception("WS send failed ws_id=%s", ws_id,)
            self.disconnect(ws)


manager = ConnectionManager()

```

---

### .\backend\app\websocket\ws.py

**Funciones (1):**
- websocket_endpoint

**Clases (0):**

**Imports (8):**
- fastapi.APIRouter
- fastapi.WebSocket
- fastapi.WebSocketDisconnect
- sqlalchemy.orm.Session
- app.db.session.SessionLocal
- app.domain.errors.base.DomainError
- app.dependencies.auth.authenticate_token
- app.websocket.manager.manager

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain.errors.base import DomainError
from app.dependencies.auth import authenticate_token
from app.websocket.manager import manager

router = APIRouter()


# --------------------------------------------------------------------------------------
# Establece una conexión WebSocket autenticada mediante un token JWT.
# --------------------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    db: Session = SessionLocal()

    try:

        try:
            auth_user = authenticate_token(db, token)
        except DomainError:
            await websocket.close(code=1008)
            return

        connected = await manager.connect(
            websocket,
            auth_user,
        )

        if not connected:
            return

        try:
            # Mantener la conexión abierta mientras el cliente permanezca conectado.
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            manager.disconnect(websocket)

    finally:
        db.close()
```

---

### .\backend\tests\conftest.py

**Funciones (6):**
- db
- restaurant
- user
- table
- product
- order

**Clases (0):**

**Imports (16):**
- pytest
- decimal.Decimal
- sqlalchemy.create_engine
- sqlalchemy.orm.sessionmaker
- app.db.base_class.Base
- app.models.restaurant.Restaurant
- app.models.user.User
- app.models.user.UserRole
- app.models.table.Table
- app.models.category.Category
- app.models.production_station.ProductionStation
- app.models.product.Product
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus

```python
"""
conftest.py

Fixtures compartidas para toda la suite de tests.
pytest descubre este archivo automáticamente (no hace falta importarlo).

Ubicación esperada: backend/tests/conftest.py
"""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base

from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.models.table import Table
from app.models.category import Category
from app.models.production_station import ProductionStation
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus


@pytest.fixture
def db():
    """
    Sesión de base de datos aislada por test.

    SQLite in-memory: no toca Postgres, no requiere el contenedor `db`
    levantado, y se descarta automáticamente al terminar el test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def restaurant(db):
    """
    Restaurante base para asociar a las entidades de cada test.
    Ajustar los campos si Restaurant exige más columnas obligatorias.
    """
    r = Restaurant(name="Restaurante de Prueba")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def user(db, restaurant):
    """
    Usuario base (cajero) para operaciones que requieren user_id.
    """
    u = User(
        restaurant_id=restaurant.id,
        username="cajero_test",
        role=UserRole.CASHIER,
        password_hash="x",  # placeholder, no se testea login en estos tests
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def table(db, restaurant):
    """
    Mesa base -- Order.table_id es obligatorio, así que toda orden
    de prueba necesita una mesa asociada.
    """
    t = Table(
        restaurant_id=restaurant.id,
        number=1,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@pytest.fixture
def product(db, restaurant):
    """
    Producto base para armar OrderItems. Encadena Category y
    ProductionStation porque Product los exige como FK obligatoria,
    aunque la lógica de order_service no los use directamente.
    """
    category = Category(restaurant_id=restaurant.id, name="Categoría Test")
    station = ProductionStation(restaurant_id=restaurant.id, name="Estación Test")
    db.add_all([category, station])
    db.commit()
    db.refresh(category)
    db.refresh(station)

    p = Product(
        restaurant_id=restaurant.id,
        name="Producto Test",
        price=Decimal("100.00"),
        station_id=station.id,
        category_id=category.id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def order(db, restaurant, table):
    """
    Orden vacía (sin items) en estado OPEN, lista para que cada test
    le agregue los items/pagos que necesite.
    """
    o = Order(
        restaurant_id=restaurant.id,
        table_id=table.id,
        status=OrderStatus.OPEN,
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return o
```

---

### .\backend\tests\__init__.py

**Funciones (0):**

**Clases (0):**

**Imports (0):**

```python

```

---

### .\backend\tests\unit\factories.py

**Funciones (4):**
- crear_pago
- crear_movimiento_caja
- crear_orden
- crear_item

**Clases (0):**

**Imports (9):**
- decimal.Decimal
- app.models.payment.Payment
- app.models.payment.PaymentMethod
- app.models.cash_movement.CashMovement
- app.models.cash_movement.CashMovementType
- app.models.order.Order
- app.models.order.OrderStatus
- app.models.order_item.OrderItem
- app.models.order_item.OrderItemStatus

```python
"""
tests/unit/factories.py

Funciones helper para crear datos de prueba rápido, sin repetir
boilerplate de SQLAlchemy en cada test.

Estas NO son fixtures de pytest -- son funciones normales que se
llaman a mano dentro de cada test, pasándoles la sesión `db`.
"""

from decimal import Decimal

from app.models.payment import Payment, PaymentMethod
from app.models.cash_movement import CashMovement, CashMovementType
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus


def crear_pago(
    db,
    restaurant_id: int,
    cash_register_id: int,
    order_id: int,
    amount: Decimal,
    method: PaymentMethod = PaymentMethod.CASH,
) -> Payment:
    pago = Payment(
        restaurant_id=restaurant_id,
        cash_register_id=cash_register_id,
        order_id=order_id,
        amount=amount,
        method=method,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def crear_movimiento_caja(
    db,
    cash_register_id: int,
    user_id: int,
    amount: Decimal,
    tipo: CashMovementType,
    reason: str = "ajuste de prueba",
) -> CashMovement:
    mov = CashMovement(
        cash_register_id=cash_register_id,
        user_id=user_id,
        amount=amount,
        type=tipo,
        reason=reason,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def crear_orden(
    db,
    restaurant_id: int,
    table_id: int,
    status: OrderStatus = OrderStatus.CLOSED,
) -> Order:
    """
    Por defecto crea la orden ya CLOSED, porque la mayoría de los
    tests de caja no necesitan una orden abierta -- solo necesitan
    que exista una orden a la que asociar pagos.
    """
    orden = Order(
        restaurant_id=restaurant_id,
        table_id=table_id,
        status=status,
    )
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden


def crear_item(
    db,
    restaurant_id: int,
    order_id: int,
    product_id: int,
    quantity: int = 1,
    unit_price: Decimal = Decimal("100.00"),
    status: OrderItemStatus = OrderItemStatus.PENDING,
) -> OrderItem:
    item = OrderItem(
        restaurant_id=restaurant_id,
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        status=status,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

---

### .\backend\tests\unit\test_auth_and_permissions.py

**Funciones (9):**
- test_authenticate_token_rechaza_token_invalido
- test_authenticate_token_rechaza_payload_incompleto
- test_authenticate_token_rechaza_usuario_inexistente
- test_authenticate_token_rechaza_usuario_inactivo
- test_authenticate_token_rechaza_rol_desactualizado
- test_authenticate_token_rechaza_restaurant_id_cruzado
- test_authenticate_token_devuelve_el_usuario_con_token_valido
- test_require_roles_permite_rol_incluido
- test_require_roles_rechaza_rol_no_incluido

**Clases (0):**

**Imports (6):**
- pytest
- app.core.security.create_access_token
- app.dependencies.auth.authenticate_token
- app.dependencies.permissions.require_roles
- app.domain.errors.base.DomainError
- app.models.user.UserRole

```python
"""
tests/unit/test_auth_and_permissions.py

Fase 3 (P1) del plan de testing: authenticate_token (dependencies/auth.py)
y require_roles (dependencies/permissions.py).

Estos tests protegen el activo más crítico de un sistema multi-tenant:
que un usuario nunca pueda autenticarse "cruzado" contra otro restaurante.

Correr con: docker compose exec backend pytest tests/unit/test_auth_and_permissions.py -v
"""

import pytest
from app.core.security import create_access_token
from app.dependencies.auth import authenticate_token
from app.dependencies.permissions import require_roles
from app.domain.errors.base import DomainError
from app.models.user import UserRole


# --------------------------------------------------------------------------------
# authenticate_token
# --------------------------------------------------------------------------------

def test_authenticate_token_rechaza_token_invalido(db):
    with pytest.raises(DomainError):
        authenticate_token(db=db, token="esto-no-es-un-token")


def test_authenticate_token_rechaza_payload_incompleto(db):
    """
    Token válido y bien firmado, pero le falta 'restaurant_id' --
    debe rechazarse en vez de reventar con un KeyError sin controlar.
    """
    token = create_access_token({"sub": "1", "role": "ADMIN"})

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_usuario_inexistente(db, restaurant):
    token = create_access_token({
        "sub": "99999",  # no existe en la DB
        "restaurant_id": str(restaurant.id),
        "role": "ADMIN",
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_usuario_inactivo(db, restaurant, user):
    user.active = False
    db.commit()

    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": user.role.value,
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_rol_desactualizado(db, restaurant, user):
    """
    El token dice CASHIER (el rol que tenía al loguearse), pero en DB
    ahora el usuario es ADMIN (alguien le cambió el rol después). Debe
    rechazarse -- fuerza a repetir login en vez de operar con un rol
    que ya no es el real.
    """
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": "CASHIER",  # rol viejo, embebido en el token
    })
    user.role = UserRole.ADMIN  # el rol real cambió en DB
    db.commit()

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_restaurant_id_cruzado(db, restaurant, user):
    """
    CRÍTICO -- aislamiento multi-tenant.

    El token tiene el user_id correcto pero un restaurant_id de OTRO
    restaurante. La query de authenticate_token filtra por
    (User.id == user_id AND User.restaurant_id == restaurant_id), así
    que este intento de "cruzar" tenants debe fallar como si el
    usuario no existiera -- nunca debe devolver el User real.
    """
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": "999999",  # restaurante que no es el suyo
        "role": user.role.value,
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_devuelve_el_usuario_con_token_valido(db, restaurant, user):
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": user.role.value,
    })

    resultado = authenticate_token(db=db, token=token)

    assert resultado.id == user.id
    assert resultado.restaurant_id == restaurant.id


# --------------------------------------------------------------------------------
# require_roles / role_checker
# --------------------------------------------------------------------------------

def test_require_roles_permite_rol_incluido(user):
    """
    role_checker es la función interna que devuelve require_roles().
    Se puede llamar directo pasándole el User -- FastAPI normalmente
    lo resuelve vía Depends(get_current_user), pero para testear la
    lógica de permisos no hace falta levantar ese mecanismo.
    """
    checker = require_roles(UserRole.CASHIER, UserRole.ADMIN)

    resultado = checker(user=user)

    assert resultado is user


def test_require_roles_rechaza_rol_no_incluido(user):
    checker = require_roles(UserRole.ADMIN)  # user (fixture) es CASHIER

    with pytest.raises(DomainError):
        checker(user=user)

```

---

### .\backend\tests\unit\test_backup_service.py

**Funciones (14):**
- _settings
- test_calculate_next_run_daily_hora_futura_es_hoy
- test_calculate_next_run_daily_hora_pasada_es_manana
- test_calculate_next_run_monthly_clampea_dia_31_en_febrero
- test_calculate_next_run_weekly_cae_en_el_weekday_configurado
- test_apply_retention_policy_borra_backups_viejos_conserva_nuevos
- test_apply_retention_policy_sin_directorio_no_falla
- test_apply_retention_policy_dias_en_cero_no_borra_nada
- test_resolve_backup_dir_respeta_env_var
- test_restaurant_backup_directory_crea_carpeta_si_no_existe
- test_backup_postgres_lanza_domain_error_si_pg_dump_falla
- test_backup_postgres_no_lanza_error_si_pg_dump_ok
- fake_run
- fake_run

**Clases (0):**

**Imports (10):**
- os
- subprocess
- datetime.datetime
- datetime.time
- datetime.timezone
- pytest
- app.domain.backup.backup_service.BackupService
- app.domain.errors.base.DomainError
- app.models.system_settings.SystemSettings
- app.models.enums.BackupFrequency

```python
"""
tests/unit/test_backup_service.py

Fase 4 (P1) del plan de testing: backup/restore.

No testeamos pg_dump/pg_restore en sí (eso lo garantiza Postgres) --
testeamos la lógica alrededor: cálculo de próxima corrida, política
de retención, resolución de directorios, y el manejo de errores de
subprocess (mockeado, sin ejecutar pg_dump de verdad).

IMPORTANTE: BackupService(db) llama a _resolve_backup_dir() en su
__init__, que en este contenedor puede resolver a /backups (el
volumen real montado, ver BACKUP_DIR en docker-compose.yml). Por eso
en casi todos los tests pisamos service.backup_dir = tmp_path
INMEDIATAMENTE después de instanciar, para no escribir jamás sobre
el directorio real de backups del restaurante.

Correr con: docker compose exec backend pytest tests/unit/test_backup_service.py -v
"""

import os
import subprocess
from datetime import datetime, time, timezone

import pytest
from app.domain.backup.backup_service import BackupService
from app.domain.errors.base import DomainError
from app.models.system_settings import SystemSettings
from app.models.enums import BackupFrequency


def _settings(**overrides) -> SystemSettings:
    """
    SystemSettings como objeto Python plano, SIN guardar en DB --
    _calculate_next_run y _apply_retention_policy solo leen atributos,
    no hacen falta persistidos.
    """
    defaults = dict(
        restaurant_id=1,
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(3, 0),
        backup_weekday=0,
        backup_monthday=1,
        backup_timezone="America/Montevideo",
        backup_retention_daily=30,
        backup_retention_weekly=84,
        backup_retention_monthly=365,
    )
    defaults.update(overrides)
    return SystemSettings(**defaults)


# --------------------------------------------------------------------------------
# _calculate_next_run -- función pura, sin filesystem ni DB
# --------------------------------------------------------------------------------

def test_calculate_next_run_daily_hora_futura_es_hoy(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(23, 59),
    )

    resultado = service._calculate_next_run(settings)

    ahora = datetime.now(resultado.tzinfo)
    assert resultado.date() == ahora.date()
    assert resultado.hour == 23 and resultado.minute == 59


def test_calculate_next_run_daily_hora_pasada_es_manana(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(0, 1),
    )

    resultado = service._calculate_next_run(settings)

    ahora = datetime.now(resultado.tzinfo)
    # Salvo que corras el test a las 00:00-00:01 exactas, debe caer mañana
    assert resultado.date() > ahora.date() or resultado > ahora


def test_calculate_next_run_monthly_clampea_dia_31_en_febrero(db):
    """
    Caso límite real: backup_monthday=31 pero el próximo mes es
    febrero (28 o 29 días) -- no debe reventar, debe usar el último
    día disponible del mes.
    """
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.MONTHLY,
        backup_monthday=31,
        backup_time=time(0, 0),
    )

    resultado = service._calculate_next_run(settings)

    # Nunca debe caer en un día que no existe (ej: 31 de febrero)
    assert 1 <= resultado.day <= 31


def test_calculate_next_run_weekly_cae_en_el_weekday_configurado(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.WEEKLY,
        backup_weekday=2,  # miércoles (Monday=0)
        backup_time=time(23, 59),
    )

    resultado = service._calculate_next_run(settings)

    assert resultado.weekday() == 2


# --------------------------------------------------------------------------------
# _apply_retention_policy -- filesystem real, pero en tmp_path (pytest lo limpia solo)
# --------------------------------------------------------------------------------

def test_apply_retention_policy_borra_backups_viejos_conserva_nuevos(db, tmp_path):
    service = BackupService(db)
    service.backup_dir = tmp_path  # nunca tocar /backups real

    settings = _settings(restaurant_id=1, backup_retention_daily=7)
    daily_dir = tmp_path / "restaurant_1" / "daily"
    daily_dir.mkdir(parents=True)

    viejo = daily_dir / "backup-viejo.dump"
    nuevo = daily_dir / "backup-nuevo.dump"
    viejo.write_bytes(b"x")
    nuevo.write_bytes(b"x")

    ahora = datetime.now(timezone.utc).timestamp()
    diez_dias = 10 * 24 * 60 * 60
    un_dia = 24 * 60 * 60
    os.utime(viejo, (ahora - diez_dias, ahora - diez_dias))  # más viejo que retention=7 días
    os.utime(nuevo, (ahora - un_dia, ahora - un_dia))         # dentro de retention

    service._apply_retention_policy(settings)

    assert not viejo.exists()
    assert nuevo.exists()


def test_apply_retention_policy_sin_directorio_no_falla(db, tmp_path):
    """
    Si todavía no existe restaurant_X/ (nunca se hizo un backup),
    no debe romper -- debe salir en silencio.
    """
    service = BackupService(db)
    service.backup_dir = tmp_path
    settings = _settings(restaurant_id=999)

    service._apply_retention_policy(settings)  # no debe lanzar excepción


def test_apply_retention_policy_dias_en_cero_no_borra_nada(db, tmp_path):
    """
    retention=0/None para un tipo de backup significa "conservar para
    siempre" (el código hace `if not days: continue`) -- confirmamos
    que esa interpretación es la que efectivamente corre.
    """
    service = BackupService(db)
    service.backup_dir = tmp_path
    settings = _settings(restaurant_id=1, backup_retention_daily=0)

    daily_dir = tmp_path / "restaurant_1" / "daily"
    daily_dir.mkdir(parents=True)
    viejo = daily_dir / "backup-viejo.dump"
    viejo.write_bytes(b"x")
    ahora = datetime.now(timezone.utc).timestamp()
    cien_dias = 100 * 24 * 60 * 60
    os.utime(viejo, (ahora - cien_dias, ahora - cien_dias))

    service._apply_retention_policy(settings)

    assert viejo.exists()


# --------------------------------------------------------------------------------
# _resolve_backup_dir
# --------------------------------------------------------------------------------

def test_resolve_backup_dir_respeta_env_var(db, tmp_path, monkeypatch):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))

    service = BackupService(db)

    assert service.backup_dir == tmp_path


# --------------------------------------------------------------------------------
# _restaurant_backup_directory -- crea el directorio si no existe
# --------------------------------------------------------------------------------

def test_restaurant_backup_directory_crea_carpeta_si_no_existe(db, tmp_path):
    service = BackupService(db)
    service.backup_dir = tmp_path

    resultado = service._restaurant_backup_directory(restaurant_id=5)

    assert resultado.exists()
    assert resultado == tmp_path / "restaurant_5"


# --------------------------------------------------------------------------------
# _backup_postgres -- subprocess mockeado, nunca corre pg_dump de verdad
# --------------------------------------------------------------------------------

def test_backup_postgres_lanza_domain_error_si_pg_dump_falla(db, tmp_path, monkeypatch):
    service = BackupService(db)

    def fake_run(command, capture_output, text, env):
        return subprocess.CompletedProcess(
            args=command, returncode=1, stdout="", stderr="conexión rechazada"
        )

    monkeypatch.setattr(
        "app.domain.backup.backup_service.subprocess.run", fake_run
    )

    with pytest.raises(DomainError):
        service._backup_postgres(tmp_path / "backup.dump")


def test_backup_postgres_no_lanza_error_si_pg_dump_ok(db, tmp_path, monkeypatch):
    service = BackupService(db)

    def fake_run(command, capture_output, text, env):
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "app.domain.backup.backup_service.subprocess.run", fake_run
    )

    service._backup_postgres(tmp_path / "backup.dump")  # no debe lanzar

```

---

### .\backend\tests\unit\test_cash_register_service.py

**Funciones (8):**
- test_open_cash_register_rejects_negative_amount
- test_open_cash_register_rejects_second_open
- test_close_cash_register_expected_cash_solo_cuenta_efectivo
- test_close_cash_register_difference_negativa_no_bloquea_cierre
- test_close_cash_register_bloquea_si_hay_ordenes_abiertas
- test_close_cash_register_rejects_negative_counted_cash
- test_close_cash_register_considera_movimientos_de_caja
- test_average_ticket_es_cero_sin_ordenes

**Clases (0):**

**Imports (12):**
- decimal.Decimal
- pytest
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.errors.base.DomainError
- app.models.payment.PaymentMethod
- app.models.cash_movement.CashMovementType
- app.models.order.OrderStatus
- app.schemas.cash_register.CashRegisterClose
- factories.crear_pago
- factories.crear_movimiento_caja
- factories.crear_orden
- pydantic.ValidationError

```python
"""
tests/unit/test_cash_register_service.py

Fase 1 (P0) del plan de testing: dinero y estado de caja.
Correr con: docker compose exec backend pytest tests/unit/test_cash_register_service.py -v
"""

from decimal import Decimal

import pytest
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.errors.base import DomainError
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType
from app.models.order import OrderStatus
from app.schemas.cash_register import CashRegisterClose

from .factories import crear_pago, crear_movimiento_caja, crear_orden


# --------------------------------------------------------------------------------
# open_cash_register
# --------------------------------------------------------------------------------

def test_open_cash_register_rejects_negative_amount(db, restaurant, user):
    service = CashRegisterService(db)

    with pytest.raises(DomainError):
        service.open_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            opening_amount=Decimal("-1"),
        )


def test_open_cash_register_rejects_second_open(db, restaurant, user):
    service = CashRegisterService(db)
    service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )

    with pytest.raises(DomainError):
        service.open_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            opening_amount=Decimal("500"),
        )


# --------------------------------------------------------------------------------
# close_cash_register -- el corazón de la Fase 1
# --------------------------------------------------------------------------------

def test_close_cash_register_expected_cash_solo_cuenta_efectivo(db, restaurant, user, table):
    """
    Caso real que probaste a mano: abrís con $1000, un pago en efectivo
    de $500 y uno con tarjeta de $300. El expected_cash debe ser 1500,
    no 1800 -- la tarjeta no suma al efectivo esperado en caja.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    orden = crear_orden(db, restaurant_id=restaurant.id, table_id=table.id)

    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("500"), method=PaymentMethod.CASH)
    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("300"), method=PaymentMethod.CARD)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1500")),
    )

    assert resultado.expected_cash == Decimal("1500")
    assert resultado.difference == Decimal("0")
    assert resultado.total_sales == Decimal("800")  # 500 + 300, esto sí suma todo


def test_close_cash_register_difference_negativa_no_bloquea_cierre(db, restaurant, user, table):
    """
    Si el cajero cuenta menos plata de la esperada, el sistema debe
    reportar la diferencia pero NO impedir el cierre -- eso lo decide
    un supervisor después, no el sistema.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    orden = crear_orden(db, restaurant_id=restaurant.id, table_id=table.id)
    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("500"), method=PaymentMethod.CASH)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1400")),  # faltan $100
    )

    assert resultado.expected_cash == Decimal("1500")
    assert resultado.difference == Decimal("-100")


def test_close_cash_register_bloquea_si_hay_ordenes_abiertas(db, restaurant, user, table):
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    crear_orden(db, restaurant_id=restaurant.id, table_id=table.id, status=OrderStatus.IN_PROGRESS)

    with pytest.raises(DomainError):
        service.close_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            data=CashRegisterClose(counted_cash=Decimal("1000")),
        )


def test_close_cash_register_rejects_negative_counted_cash(db, restaurant, user):
    """
    OJO: counted_cash ya tiene Field(ge=Decimal("0")) en el schema
    Pydantic (CashRegisterClose), así que el rechazo pasa ACÁ -- al
    construir el objeto -- y nunca llega a pisar el service.

    El chequeo `if data.counted_cash < 0: raise DomainError` que
    tiene close_cash_register es código muerto: Pydantic ya garantiza
    que ese valor nunca puede ser negativo. No es un bug, pero es
    duplicación -- vale la pena limpiarlo en algún refactor.
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CashRegisterClose(counted_cash=Decimal("-50"))


def test_close_cash_register_considera_movimientos_de_caja(db, restaurant, user):
    """
    Un cash_in (ej: cambio que trae el dueño) y un cash_out (ej: pago
    a un proveedor) deben afectar expected_cash en la dirección correcta.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    crear_movimiento_caja(db, cash_register_id=caja.id, user_id=user.id,
                           amount=Decimal("200"), tipo=CashMovementType.CASH_IN)
    crear_movimiento_caja(db, cash_register_id=caja.id, user_id=user.id,
                           amount=Decimal("50"), tipo=CashMovementType.CASH_OUT)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1150")),
    )

    # 1000 (apertura) + 0 (ventas cash) + 200 (in) - 50 (out) = 1150
    assert resultado.expected_cash == Decimal("1150")
    assert resultado.difference == Decimal("0")


# --------------------------------------------------------------------------------
# average_ticket -- caso límite de división por cero
# --------------------------------------------------------------------------------

def test_average_ticket_es_cero_sin_ordenes(db, restaurant, user):
    """
    Deja escrito en piedra que _calculate_sales no explota si todavía
    no hubo ninguna venta -- por si alguien "optimiza" el código después.
    """
    service = CashRegisterService(db)
    service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )

    resumen = service.get_current_cash_register(restaurant_id=restaurant.id)

    assert resumen.average_ticket == Decimal("0")
    assert resumen.orders_count == 0
```

---

### .\backend\tests\unit\test_order_service.py

**Funciones (17):**
- test_calculate_totals_suma_items_correctamente
- test_calculate_totals_aplica_descuento_al_total
- test_apply_discount_rechaza_descuento_mayor_al_subtotal
- test_apply_discount_rechaza_si_deja_pagos_excedidos
- test_apply_discount_rechaza_en_orden_cerrada
- test_status_todos_cancelados_orden_open_pasa_a_cancelled
- test_status_item_in_progress_domina_sobre_pending
- test_status_todos_ready_o_delivered_es_ready
- test_close_order_rechaza_con_saldo_pendiente
- test_close_order_rechaza_orden_sin_items
- test_close_order_rechaza_items_no_entregados
- test_close_order_ok_con_items_cancelados_y_delivered_mixtos
- test_calculate_totals_excluye_items_cancelados
- test_add_payment_rechaza_si_excede_saldo_restante
- test_add_payment_requiere_caja_abierta
- test_add_payment_rechaza_en_orden_cerrada
- test_delete_payment_bloqueado_en_orden_cerrada

**Clases (0):**

**Imports (10):**
- decimal.Decimal
- pytest
- app.domain.order.order_service.OrderService
- app.domain.cash_register.cash_register_service.CashRegisterService
- app.domain.errors.base.DomainError
- app.models.order.OrderStatus
- app.models.order_item.OrderItemStatus
- app.schemas.order.payment.PaymentCreate
- app.models.payment.PaymentMethod
- factories.crear_item

```python
"""
tests/unit/test_order_service.py

Fase 2 (P0) del plan de testing: totales, transiciones de estado
y flujo de pagos de órdenes.

Correr con: docker compose exec backend pytest tests/unit/test_order_service.py -v
"""

from decimal import Decimal

import pytest
from app.domain.order.order_service import OrderService
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.errors.base import DomainError
from app.models.order import OrderStatus
from app.models.order_item import OrderItemStatus
from app.schemas.order.payment import PaymentCreate
from app.models.payment import PaymentMethod

from .factories import crear_item


# --------------------------------------------------------------------------------
# _calculate_totals
# --------------------------------------------------------------------------------

def test_calculate_totals_suma_items_correctamente(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=2, unit_price=Decimal("100.00"))
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("50.00"))
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("250.00")  # 2*100 + 1*50
    assert total == Decimal("250.00")     # sin descuento
    assert total_paid == Decimal("0")
    assert remaining == Decimal("250.00")


def test_calculate_totals_aplica_descuento_al_total(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    order.discount = Decimal("20.00")
    db.commit()
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("100.00")
    assert total == Decimal("80.00")
    assert remaining == Decimal("80.00")


# --------------------------------------------------------------------------------
# apply_discount
# --------------------------------------------------------------------------------

def test_apply_discount_rechaza_descuento_mayor_al_subtotal(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("150.00"))


def test_apply_discount_rechaza_si_deja_pagos_excedidos(db, restaurant, user, order, product):
    """
    Caso real: ya se pagó $80 sobre un total de $100. Si después
    intentan aplicar un descuento de $30, el nuevo total ($70) quedaría
    por debajo de lo ya pagado -- eso no puede pasar.
    """
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("80.00"), method=PaymentMethod.CASH))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("30.00"))


def test_apply_discount_rechaza_en_orden_cerrada(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)
    order.status = OrderStatus.CLOSED
    db.commit()

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("10.00"))


# --------------------------------------------------------------------------------
# _calculate_order_status -- la matriz de estados
# --------------------------------------------------------------------------------

def test_status_todos_cancelados_orden_open_pasa_a_cancelled(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.CANCELLED)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.CANCELLED


def test_status_item_in_progress_domina_sobre_pending(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.IN_PROGRESS)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.PENDING)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.IN_PROGRESS


def test_status_todos_ready_o_delivered_es_ready(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.READY)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.DELIVERED)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.READY


# --------------------------------------------------------------------------------
# close_order -- los tres guardas
# --------------------------------------------------------------------------------

def test_close_order_rechaza_con_saldo_pendiente(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_rechaza_orden_sin_items(db, restaurant, order):
    service = OrderService(db)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_rechaza_items_no_entregados(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.READY)  # READY, no DELIVERED
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_ok_con_items_cancelados_y_delivered_mixtos(db, restaurant, user, order, product):
    """
    Un item CANCELLED no cuenta ni para el estado (ya lo cubre
    _calculate_order_status) ni para el total a pagar (fix aplicado
    en _calculate_totals) -- la orden cierra pagando solo el item
    DELIVERED ($100), sin el cancelado ($50).
    """
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("50.00"),
               status=OrderItemStatus.CANCELLED)
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)
    # crear_item es un atajo de test que no dispara _set_status como lo
    # haría el flujo real (add_item -> send_to_kitchen -> deliver_item).
    # Simulamos acá el estado al que naturalmente habría llegado la orden.
    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)

    resultado = service.close_order(order)

    assert resultado.status == OrderStatus.CLOSED


def test_calculate_totals_excluye_items_cancelados(db, restaurant, order, product):
    """
    Regresión del fix: _calculate_totals debe excluir items CANCELLED
    del subtotal, igual que ya hace report_service._order_total y
    _calculate_order_status. Antes del fix este test daba 150.00.
    """
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("50.00"),
               status=OrderItemStatus.CANCELLED)
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("100.00")
    assert total == Decimal("100.00")


# --------------------------------------------------------------------------------
# add_payment / delete_payment
# --------------------------------------------------------------------------------

def test_add_payment_rechaza_si_excede_saldo_restante(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("150.00"), method=PaymentMethod.CASH))


def test_add_payment_requiere_caja_abierta(db, restaurant, order, product):
    """
    Sin caja abierta, add_payment debe fallar -- es el acoplamiento
    real entre OrderService y CashRegisterService.
    """
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("50.00"), method=PaymentMethod.CASH))


def test_add_payment_rechaza_en_orden_cerrada(db, restaurant, order):
    service = OrderService(db)
    order.status = OrderStatus.CLOSED
    db.commit()

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("10.00"), method=PaymentMethod.CASH))


def test_delete_payment_bloqueado_en_orden_cerrada(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)
    pago = service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)
    # Mismo motivo que en el test anterior: simulamos el estado READY
    # al que se llegaría vía el flujo real antes de cerrar.
    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)
    service.close_order(order)

    with pytest.raises(DomainError):
        service.delete_payment(restaurant.id, pago.id)

```

---

### .\backend\tests\unit\test_security.py

**Funciones (7):**
- test_password_hash_verifica_correctamente
- test_password_hash_rechaza_password_incorrecto
- test_password_hash_nunca_es_igual_al_texto_plano
- test_create_access_token_incluye_los_claims_esperados
- test_decode_access_token_con_token_invalido_devuelve_none
- test_decode_access_token_con_firma_incorrecta_devuelve_none
- test_decode_access_token_expirado_devuelve_none

**Clases (0):**

**Imports (11):**
- datetime.datetime
- datetime.timedelta
- datetime.timezone
- jose.jwt
- pytest
- app.core.security.get_password_hash
- app.core.security.verify_password
- app.core.security.create_access_token
- app.core.security.decode_access_token
- app.core.config.SECRET_KEY
- app.core.config.ALGORITHM

```python
"""
tests/unit/test_security.py

Fase 3 (P1) del plan de testing: funciones puras de app/core/security.py.
No necesitan `db` -- son funciones sin estado, ideales para arrancar rápido.

Correr con: docker compose exec backend pytest tests/unit/test_security.py -v
"""

from datetime import datetime, timedelta, timezone

from jose import jwt as jose_jwt
import pytest

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.config import SECRET_KEY, ALGORITHM


# --------------------------------------------------------------------------------
# Hashing de contraseñas
# --------------------------------------------------------------------------------

def test_password_hash_verifica_correctamente():
    hash_ = get_password_hash("mi_password_segura")

    assert verify_password("mi_password_segura", hash_) is True


def test_password_hash_rechaza_password_incorrecto():
    hash_ = get_password_hash("mi_password_segura")

    assert verify_password("password_equivocado", hash_) is False


def test_password_hash_nunca_es_igual_al_texto_plano():
    """
    Chequeo básico pero importante: confirma que efectivamente se
    está hasheando y no guardando en texto plano por error.
    """
    hash_ = get_password_hash("mi_password_segura")

    assert hash_ != "mi_password_segura"


# --------------------------------------------------------------------------------
# create_access_token / decode_access_token
# --------------------------------------------------------------------------------

def test_create_access_token_incluye_los_claims_esperados():
    token = create_access_token({
        "sub": "1",
        "restaurant_id": "1",
        "role": "ADMIN",
    })

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["restaurant_id"] == "1"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_decode_access_token_con_token_invalido_devuelve_none():
    assert decode_access_token("esto-no-es-un-jwt-valido") is None


def test_decode_access_token_con_firma_incorrecta_devuelve_none():
    """
    Un token firmado con OTRA clave secreta -- simula un token
    falsificado o de otro entorno -- debe ser rechazado.
    """
    token_falso = jose_jwt.encode(
        {"sub": "1", "restaurant_id": "1", "role": "ADMIN",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "clave-secreta-incorrecta",
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token_falso) is None


def test_decode_access_token_expirado_devuelve_none():
    """
    Construye a mano un token ya vencido (exp en el pasado) para
    confirmar que decode_access_token lo rechaza en vez de aceptarlo.
    """
    token_vencido = jose_jwt.encode(
        {
            "sub": "1",
            "restaurant_id": "1",
            "role": "ADMIN",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token_vencido) is None

```

---

### .\backend\tests\unit\__init__.py

**Funciones (0):**

**Clases (0):**

**Imports (0):**

```python

```

---

### .\scripts\announce_service.py

**Funciones (4):**
- get_local_ip
- create_service
- main
- shutdown

**Clases (0):**

**Imports (7):**
- os
- signal
- socket
- sys
- time
- zeroconf.ServiceInfo
- zeroconf.Zeroconf

```python
#!/usr/bin/env python3
"""
POS Zeroconf announcer.

Publishes the POS services on the local network so phones/tablets can discover
the server. The hostname itself (pos.local by default) is provided by Avahi on
the Linux host; this script publishes service metadata and ports.
"""

import os
import signal
import socket
import sys
import time

from zeroconf import ServiceInfo, Zeroconf


HOSTNAME = os.getenv("POS_HOSTNAME", "pos.local").rstrip(".")
FRONTEND_PORT = int(os.getenv("POS_FRONTEND_PORT", "5173"))
BACKEND_PORT = int(os.getenv("POS_BACKEND_PORT", "8000"))
SERVICE_NAME = os.getenv("POS_SERVICE_NAME", "restaurant-pos")


def get_local_ip() -> str:
    """Return the LAN IP without requiring the destination to be reachable."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)


def create_service(service_type: str, name: str, port: int, ip: str) -> ServiceInfo:
    return ServiceInfo(
        service_type,
        f"{name}.{service_type}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            "version": "1.0",
            "hostname": HOSTNAME,
            "service": name,
        },
        server=f"{HOSTNAME}.",
    )


def main() -> None:
    ip = get_local_ip()

    print("POS Zeroconf announcer")
    print("IP detectada:", ip)
    print("Hostname:", f"{HOSTNAME}.")

    zeroconf = Zeroconf()

    services = [
        create_service(
            "_pos._tcp.local.",
            SERVICE_NAME,
            FRONTEND_PORT,
            ip,
        ),
        create_service(
            "_http._tcp.local.",
            f"{SERVICE_NAME}-web",
            FRONTEND_PORT,
            ip,
        ),
        create_service(
            "_ws._tcp.local.",
            f"{SERVICE_NAME}-ws",
            BACKEND_PORT,
            ip,
        ),
    ]

    for service in services:
        zeroconf.register_service(service)
        print("Servicio publicado:", service.name, "puerto:", service.port)

    print("\nPOS disponible en:")
    print(f"http://{HOSTNAME}:{FRONTEND_PORT}")
    print(f"http://{ip}:{FRONTEND_PORT}")

    def shutdown(_sig, _frame) -> None:
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

