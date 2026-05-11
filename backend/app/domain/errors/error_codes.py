from enum import Enum

class ErrorCode(str, Enum):

    # GENERALES
    NOT_FOUND = "not_found"
    INVALID_OPERATION = "invalid_operation"
    UNAUTHORIZED = "unauthorized"

    # ORDERS
    ORDER_NOT_FOUND = "order_not_found"
    ORDER_ALREADY_CLOSED = "order_already_closed"
    ORDER_ITEMS_NOT_DELIVERED = "order_items_not_delivered"
    ORDER_EMPTY = "order_empty"
    ORDER_HAS_REMAINING_BALANCE = "order_has_remaining_balance"
    INVALID_TRANSITION = "invalid_transition"

    # ORDER ITEMS
    ITEM_NOT_FOUND = "item_not_found"
    ITEM_NOT_IN_ORDER = "item_not_in_order"
    ITEM_ALREADY_SEND = "item_already_send"
    NOT_PENDING_ITEMS_TO_SEND = "not_pending_items_to_send"
    ITEM_STATUS_ROLE_FORBIDDEN = "item_status_role_forbidden"
    ITEM_INVALID_TRANSITION = "item_invalid_transition"

    # TABLES
    TABLE_NOT_FOUND = "table_not_found"
    TABLE_NUMBER_ALREADY_EXISTS = "table_number_already_exists"

    # PAYMENTS
    PAYMENT_NOT_FOUND = "payment_not_found"
    PAYMENT_INVALID_METHOD = "payment_invalid_method"
    PAYMENT_EXCEEDS_REMAINING = "payment_exceeds_remaining"

    # CASH REGISTER
    CASH_REGISTER_ALREADY_OPEN = "cash_register_already_open"
    CASH_REGISTER_ALREADY_CLOSED = "cash_register_already_closed"
    CASH_REGISTER_NOT_OPEN = "cash_register_not_open"
    CASH_REGISTER_PENDING_ORDERS = "cash_register_pending_orders"
    CASH_REGISTER_INVALID_COUNT = "cash_register_invalid_count"
    CASH_MOVEMENT_NOT_FOUND = "cash_movement_not_found"


    # PRODUCTS
    PRODUCT_NOT_FOUND = "product_not_found"

    # USERS
    USER_NOT_FOUND = "user_not_found"
    USERNAME_ALREADY_EXISTS = "username_already_exists"

    # CATEGORIES
    CATEGORY_NOT_FOUND = "category_not_found"

    # STATIONS
    STATION_NOT_FOUND = "station_not_found"
    STATION_NAME_ALREADY_EXISTS = "station_name_already_exists"

    # PERMISSIONS
    PERMISSION_DENIED = "Permission_denied"
