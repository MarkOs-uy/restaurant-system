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