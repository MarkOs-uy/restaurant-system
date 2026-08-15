from enum import StrEnum

class WSEvent(StrEnum):
    # -------------------------------------------------------------------------
    # Caja
    # -------------------------------------------------------------------------
    CASH_REGISTER_UPDATED = "CASH_REGISTER_UPDATED"
    CASH_MOVEMENT_ADDED = "CASH_MOVEMENT_ADDED"
    CASH_MOVEMENT_DELETED = "CASH_MOVEMENT_DELETED"

    # -------------------------------------------------------------------------
    # Órdenes
    # -------------------------------------------------------------------------
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_STATUS_CHANGED = "ORDER_STATUS_CHANGED"
    ORDER_CLOSED = "ORDER_CLOSED"

    # -------------------------------------------------------------------------
    # Items
    # -------------------------------------------------------------------------
    ITEM_STATUS_CHANGED = "ITEM_STATUS_CHANGED"
    NEW_ITEM = "NEW_ITEM"
    ITEM_READY = "ITEM_READY"

    # -------------------------------------------------------------------------
    # Pagos
    # -------------------------------------------------------------------------
    PAYMENT_ADDED = "PAYMENT_ADDED"
    PAYMENT_DELETED = "PAYMENT_DELETED"

    # -------------------------------------------------------------------------
    # Mesas
    # -------------------------------------------------------------------------
    TABLE_CREATED = "TABLE_CREATED"
    TABLE_UPDATED = "TABLE_UPDATED"
    TABLE_POSITION_UPDATED = "TABLE_POSITION_UPDATED"
    TABLE_ACTIVATED = "TABLE_ACTIVATED"
    TABLE_DEACTIVATED = "TABLE_DEACTIVATED"

    # -------------------------------------------------------------------------
    # Layout
    # -------------------------------------------------------------------------
    LAYOUT_UPDATED = "LAYOUT_UPDATED"