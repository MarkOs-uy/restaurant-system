from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db

from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.cash_register import CashRegister


from app.schemas.order_item import OrderItemCreate
from app.schemas.order import OrderOut, OrderStatusUpdate, ALLOWED_TRANSITIONS

from app.schemas.payment import PaymentCreate

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/{order_id}/items")
def add_item_to_order(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.status != OrderStatus.CLOSED
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o cerrado")

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.restaurant_id == order.restaurant_id,
        Product.active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no disponible")

    if product.restaurant_id != order.restaurant_id:
        raise HTTPException(
            status_code=403,
            detail="Producto no pertenece al restaurante"
        )

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=item.quantity,
        unit_price=product.price
    )

    db.add(order_item)
    db.commit()
    db.refresh(order_item)

    return {
        "order_id": order.id,
        "item_id": order_item.id,
        "product": product.name,
        "quantity": order_item.quantity
    }

@router.post("/{order_id}/payments")
def add_payment(
    order_id: int,
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status == OrderStatus.CLOSED:
        raise HTTPException(400, "Order already closed")

    total_order = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    total_paid = sum(p.amount for p in order.payments)

    remaining = total_order - total_paid

    if payment.amount > remaining:
        raise HTTPException(400, "Payment exceeds remaining balance")

    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None,
        CashRegister.restaurant_id == order.restaurant_id
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay una caja abierta")

    payment_record = Payment(
        order_id=order.id,
        restaurant_id=order.restaurant_id,
        amount=payment.amount,
        method=payment.method,
        cash_register_id=cash_register.id
    )

    db.add(payment_record)

    new_remaining = remaining - payment.amount

    if new_remaining == 0:
        order.status = OrderStatus.CLOSED
        order.closed_at = func.now()

    db.commit()

    return {"remaining": remaining - payment.amount}


@router.post("/{order_id}/close")
def close_order(order_id: int, db: Session = Depends(get_db)):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    total_order = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    total_paid = sum(p.amount for p in order.payments)

    remaining = total_order - total_paid

    if remaining > 0:
        raise HTTPException(
            400,
            f"Order not fully paid. Remaining: {remaining}"
        )

    if order.status != OrderStatus.CLOSED:
        order.status = OrderStatus.CLOSED
        order.closed_at = func.now()
        db.commit()
        db.refresh(order)

    return {
        "order_id": order.id,
        "status": order.status
    }



@router.post("/{order_id}/force-close")
def force_close_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status == OrderStatus.CLOSED:
        raise HTTPException(400, "Order already closed")

    total_order = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    total_paid = sum(
        payment.amount for payment in order.payments
    )

    remaining = total_order - total_paid

    if remaining > 0:
        raise HTTPException(
            400,
            f"No se puede cerrar. Faltan pagar {remaining}"
        )

    order.status = OrderStatus.CLOSED
    order.closed_at = func.now()

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "status": order.status
    }



@router.get("/{order_id}", response_model=OrderOut)
@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    # 1️⃣ Construimos items
    items = []
    total = 0

    for item in order.items:
        subtotal = item.quantity * item.unit_price
        total += subtotal

        items.append({
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "subtotal": float(subtotal)
        })

    # 2️⃣ Pagos
    payments = []
    total_paid = 0

    for p in order.payments:
        payments.append({
            "id": p.id,
            "amount": float(p.amount),
            "method": p.method.value
        })
        total_paid += p.amount

    remaining = total - total_paid

    # 3️⃣ Return completo
    return {
        "order_id": order.id,
        "table_number": order.table.number,
        "status": order.status.value,
        "items": items,
        "payments": payments,
        "total": float(total),
        "total_paid": float(total_paid),
        "remaining": float(remaining)
    }



@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Orden no encontrada")

    if order.status not in ALLOWED_TRANSITIONS:
        raise HTTPException(400, "La Orden no se puede modificar")

    if data.status not in ALLOWED_TRANSITIONS[order.status]:
        raise HTTPException(400, "Transición de estado inválida")

    order.status = data.status
    db.commit()
    db.refresh(order)

    return {"order_id": order.id, "new_status": order.status}

