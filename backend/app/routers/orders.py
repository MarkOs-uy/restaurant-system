from decimal import Decimal
from fastapi import APIRouter, Depends, Query

from app.models.user import User

from app.dependencies.roles import waiter_or_admin, waiter_cashier_or_admin, all_staff

from app.schemas.order.order_item import OrderItemCreate
from app.schemas.order.payment import PaymentCreate
from app.schemas.order.order import OrderStatusUpdate

from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service


router = APIRouter(prefix="/orders", tags=["orders"])


# -------------------------
# Agregar item
# -------------------------
@router.post("/{order_id}/items")
def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    user: User = Depends(waiter_or_admin),
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
    user: User = Depends(waiter_or_admin),
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
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.add_payment(order, payment.amount, payment.method)

# -------------------------
# Aplicar descuento
# -------------------------
@router.put("/{order_id}/discount")
def apply_discount(
    order_id: int,
    discount: Decimal = Query(..., ge=0),
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.apply_discount(order, discount)

# -------------------------
# Cerrar orden
# -------------------------
@router.post("/{order_id}/close")
def close_order(
    order_id: int,
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.close_order(order)

# -------------------------
# Obtener ordenes activas
# -------------------------
@router.get("/active")
def get_active_orders(
    user: User = Depends(all_staff),
    service: OrderService = Depends(get_order_service)
):
    return service.serialize_orders(user.restaurant_id)

# -------------------------
# Obtener orden por ID
# -------------------------
@router.get("/{order_id}")
def get_order(
    order_id: int,
    user: User = Depends(all_staff),
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
    user: User = Depends(all_staff),
    service: OrderService = Depends(get_order_service)
):
    order = service.get_order(order_id, user.restaurant_id)
    return service.update_status(order, data.status)

# -------------------------
# Actualizar cantidad de item
# -------------------------
@router.patch("/order-items/{item_id}")
def update_order_item_quantity(
    item_id: int,
    quantity: int,
    service: OrderService = Depends(get_order_service),
    user: User = Depends(waiter_or_admin)
):
    return service.update_item_quantity(
        restaurant_id=user.restaurant_id,
        item_id=item_id,
        quantity=quantity
    )

# -------------------------
# Borrar item de orden
# -------------------------
@router.delete("/{order_id}/items/{item_id}")
def delete_order_item(
    order_id: int,
    item_id: int,
    user: User = Depends(waiter_or_admin),
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
    user: User = Depends(waiter_cashier_or_admin),
    service: OrderService = Depends(get_order_service)
):
    service.cancel_payment(user.restaurant_id, payment_id)
    return {"ok": True}
