"""
Endpoints para la gestión de órdenes.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.roles import waiter_or_admin, waiter_cashier_or_admin, all_staff

from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User

from app.schemas.order.order_item import OrderItemCreate
from app.schemas.order.payment import (
    PaymentCreate,
    PaymentOut
)
from app.schemas.order.order import (
    OrderStatusUpdate,
    OrderDetail,
    OrderResponse
)

router = APIRouter(prefix="/orders", tags=["orders"])

# -------------------------
# Agregar item
# -------------------------
@router.post(
    "/{order_id}/items",
    response_model=OrderDetail,
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
    response_model=OrderDetail,
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
    response_model=OrderDetail,
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
    response_model=OrderDetail,
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
    response_model=OrderDetail,
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