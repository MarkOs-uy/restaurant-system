from fastapi import APIRouter, Depends, Query

from app.schemas.table import (
    TableCreate,
    TableUpdate,
    TableList,
    TableOut,
    TablePositionUpdate,
    TablePositionOut
)

from app.schemas.order.order_item import AddItemRequest

from app.domain.table.table_service import TableService
from app.domain.table.dependencies import get_table_service
from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User

from app.dependencies.roles import waiter_or_admin, admin_only


router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/")
def create_table(
    table_in: TableCreate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.create_table(user.restaurant_id, table_in)


@router.post("/{table_id}/touch")
def touch_table(
    table_id: int,
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.touch_table(user.restaurant_id, table_id)


@router.post("/{table_id}/add-product")
def add_product_to_table(
    table_id: int,
    payload: AddItemRequest,
    user: User = Depends(waiter_or_admin),
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
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables(user.restaurant_id, active)


@router.get("/status", response_model=list[TableOut])
def list_tables_status(
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables_status(user.restaurant_id)


@router.patch("/{table_id}/position", response_model=TablePositionOut)
def update_position(
    table_id: int,
    data: TablePositionUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_position(user.restaurant_id, table_id, data)


@router.patch("/{table_id}/activate")
def activate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.activate_table(user.restaurant_id, table_id)


@router.patch("/{table_id}", response_model=TableList)
def update_table(
    table_id: int,
    table_in: TableUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_table(user.restaurant_id, table_id, table_in)


@router.delete("/{table_id}")
def deactivate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.deactivate_table(user.restaurant_id, table_id)
