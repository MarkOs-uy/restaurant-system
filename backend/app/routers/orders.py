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