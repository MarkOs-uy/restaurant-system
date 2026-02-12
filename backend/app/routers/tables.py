from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Table, Order
from app.models.order import Order, OrderStatus

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/{table_id}/touch")
def touch_table(table_id: int, db: Session = Depends(get_db)):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.active == True
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # buscar pedido abierto
    order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.status != OrderStatus.CLOSED
    ).first()

    # si no existe → crearlo
    if not order:
        order = Order(
            table_id=table_id,
            #status="abierto"
        )
        db.add(order)
        db.commit()
        db.refresh(order)

    return {
        "order_id": order.id,
        "table_number": table.number,
        "status": order.status
    }
