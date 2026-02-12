from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
        Order.status == OrderStatus.OPEN
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o cerrado")

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no disponible")

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

@router.post("/{order_id}/close")
def close_order(
    order_id: int,
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != OrderStatus.READY:
        raise HTTPException(400, "Order not ready to be closed")

    total = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None
    ).first()

    if not cash_register:
        raise HTTPException(
            status_code=400,
            detail="No hay una caja abierta"
        )
    
    payment_record = Payment(
        order_id=order.id,
        method=payment.method,
        total=total,
        cash_register_id=cash_register.id
    )

    db.add(payment_record)
    order.status = OrderStatus.CLOSED

    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "status": order.status,
        "total": total,
        "payment_method": payment.method
    }

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    items = [
        {
            "product_name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price
        }
        for item in order.items
    ]
    
    total = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    return {
        "order_id": order.id,
        "table_number": order.table.number,
        "status": order.status,
        "items": items,
        "total": total
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
