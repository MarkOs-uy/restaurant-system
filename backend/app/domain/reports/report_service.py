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