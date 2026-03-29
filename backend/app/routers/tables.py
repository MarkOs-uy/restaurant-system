from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Table
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.order_item import OrderItem, OrderItemStatus

from app.schemas.table import TableCreate
from app.schemas.order.order_item import AddItemRequest
from app.schemas.table import TableUpdate, TableOut

from app.domain.table.table_service import TableService
from app.domain.table.dependencies import get_table_service

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
        Order.status.in_(["DRAFT", "OPEN", "SENT", "IN_PROGRESS", "READY"])
    ).first()

    
    if not order:
        order = Order(
            table_id=table_id,
            restaurant_id=user.restaurant_id,
            status=OrderStatus.DRAFT
        )

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


@router.get("/", response_model=list[TableOut])
def list_tables(
    active: bool | None = Query(default=True),
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables(user.restaurant_id, active)


@router.get("/status")
def list_tables_status(
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables_status(user.restaurant_id)


@router.patch("/{table_id}/position")
def update_table_position(
    table_id: int,
    x: int,
    y: int,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.update_position(user.restaurant_id, table_id, x, y)


@router.patch("/{table_id}/activate")
def activate_table(
    table_id: int,
    user: User = Depends(get_current_user),
    service: TableService = Depends(get_table_service)
):
    return service.activate_table(user.restaurant_id, table_id)


@router.patch("/{table_id}", response_model=TableOut)
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