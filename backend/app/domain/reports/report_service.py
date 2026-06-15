from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product


class ReportService:

    def __init__(self, db: Session):
        self.db = db

    def get_sales_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ):
        totals_by_day = self._empty_days(start_date, end_date)

        for order in self._closed_orders_query(restaurant_id, start_date, end_date):
            if not order.closed_at:
                continue

            day = order.closed_at.date().isoformat()
            totals_by_day[day] += self._order_total(order)

        series = [
            {"date": day, "total": self._money(total)}
            for day, total in sorted(totals_by_day.items())
        ]
        non_zero_days = [point for point in series if point["total"] > 0]

        return {
            "series": series,
            "max_day": max(non_zero_days, key=lambda point: point["total"], default=None),
            "min_day": min(non_zero_days, key=lambda point: point["total"], default=None)
        }

    def get_products_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date,
        category_id: int | None = None
    ):
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
            if item["quantity"] > 0
        ]

        top_products = sorted(
            [item for item in period_items if item["quantity"] > 0],
            key=lambda item: (item["quantity"], item["total"], item["name"]),
            reverse=True
        )[:10]
        least_products = sorted(
            period_items,
            key=lambda item: (item["quantity"], item["total"], item["name"])
        )[:10]

        return {
            "today_best_seller": max(
                today_items,
                key=lambda item: (item["quantity"], item["total"]),
                default=None
            ),
            "top_products": top_products,
            "least_products": least_products
        }

    def get_product_evolution_report(
        self,
        restaurant_id: int,
        product_id: int,
        start_date: date,
        end_date: date
    ):
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
                totals_by_day[closed_at.date().isoformat()] += quantity * unit_price

        return {
            "series": [
                {"date": day, "total": self._money(total)}
                for day, total in sorted(totals_by_day.items())
            ]
        }

    def get_sales_orders_report(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ):
        orders = (
            self._closed_orders_query(restaurant_id, start_date, end_date)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.table)
            )
            .order_by(Order.closed_at.desc(), Order.id.desc())
            .all()
        )

        return {
            "orders": [
                self._serialize_sales_order(order)
                for order in orders
                if order.closed_at
            ]
        }

    def _closed_orders_query(
        self,
        restaurant_id: int,
        start_date: date,
        end_date: date
    ):
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

    def _product_rows(
        self,
        restaurant_id: int,
        range_start: datetime,
        range_end: datetime,
        category_id: int | None
    ):
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

    def _summarize_products(
        self,
        restaurant_id: int,
        rows,
        category_id: int | None
    ):
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
            {
                **item,
                "total": self._money(item["total"])
            }
            for item in totals.values()
        ]

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

    def _serialize_sales_order(self, order: Order):
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

        return {
            "order_id": order.id,
            "table_number": order.table.number if order.table else None,
            "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            "items": [
                {
                    "item_id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product.name if item.product else "Producto eliminado",
                    "unit_price": self._money(item.unit_price),
                    "quantity": item.quantity,
                    "line_total": self._money(item.quantity * item.unit_price)
                }
                for item in active_items
            ],
            "subtotal": self._money(subtotal),
            "discount": self._money(discount),
            "total": self._money(max(subtotal - discount, Decimal("0")))
        }

    def _date_bounds(self, start_date: date, end_date: date):
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date + timedelta(days=1), time.min)
        return start, end

    def _empty_days(self, start_date: date, end_date: date) -> dict[str, Decimal]:
        days: dict[str, Decimal] = {}
        current = start_date

        while current <= end_date:
            days[current.isoformat()] = Decimal("0")
            current += timedelta(days=1)

        return days

    def _money(self, value: Decimal | int | float) -> float:
        return float(round(Decimal(value), 2))
