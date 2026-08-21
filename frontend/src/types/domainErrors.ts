export const ErrorCode = {

//GENERALES
  NOT_FOUND: "not_found",
  INVALID_OPERATION: "invalid_operation",
  UNAUTHORIZED: "unauthorized",

//ORDENES
  ORDER_NOT_FOUND: "order_not_found",
  ORDER_ALREADY_CLOSED: "order_already_closed",
  ORDER_ALREADY_CANCELLED: "order_already_cancelled",
  ORDER_ITEMS_NOT_DELIVERED: "order_items_not_delivered",
  ORDER_EMPTY: "order_empty",
  ORDER_HAS_REMAINING_BALANCE: "order_has_remaining_balance",
  INVALID_TRANSITION: "invalid_transition",

//ITEMS
  ITEM_NOT_FOUND: "item_not_found",
  ITEM_NOT_IN_ORDER: "item_not_in_order",
  ITEM_ALREADY_SENT: "item_already_sent",
  NOT_PENDING_ITEMS_TO_SEND: "not_pending_items_to_send",
  ITEM_STATUS_ROLE_FORBIDDEN: "item_status_role_forbidden",
  ITEM_INVALID_TRANSITION: "item_invalid_transition",

//PAYMENTS
  PAYMENT_NOT_FOUND: "payment_not_found",
  PAYMENT_INVALID_METHOD: "payment_invalid_method",
  PAYMENT_EXCEEDS_REMAINING: "payment_exceeds_remaining",

//CASH REGISTER
  CASH_REGISTER_ALREADY_OPEN: "cash_register_already_open",
  CASH_REGISTER_ALREADY_CLOSED: "cash_register_already_closed",
  CASH_REGISTER_NOT_OPEN: "cash_register_not_open",
  CASH_REGISTER_PENDING_ORDERS: "cash_register_pending_orders",
  CASH_REGISTER_INVALID_COUNT: "cash_register_invalid_count",
  CASH_MOVEMENT_NOT_FOUND: "cash_movement_not_found",

//USERS
  USER_NOT_FOUND: "user_not_found",
  USERNAME_ALREADY_EXISTS: "username_already_exists",
  USER_CANNOT_DEACTIVATE_SELF : "user_cannot_deactivate_self",

//AUTH
  INVALID_TOKEN: "invalid_token",
  INVALID_TOKEN_PAYLOAD: "invalid_token_payload",
  USER_INACTIVE: "user_inactive",
  ROLE_MISMATCH: "role_mismatch",

//EMAIL Y BACKUP
  INVALID_BACKUP_CONFIGURATION: "invalid_backup_configuration",
  EMAIL_NOT_CONFIGURED: "email_not_configured",
  SMTP_NOT_CONFIGURED: "smtp_not_configured",
  SMTP_HOST_NOT_CONFIGURED: "smtp_host_not_configured",
  BACKUP_EMAIL_NOT_CONFIGURED: "backup_email_not_configured",
  EMAIL_SEND_FAILURE: "email_send_failure",
  BACKUP_NOT_FOUND: "backup_not_found",
  BACKUP_INVALID_PATH: "backup_invalid_path",
  BACKUP_DATABASE_NOT_FOUND: "backup_database_not_found",
  BACKUP_ENGINE_NOT_SUPPORTED: "backup_engine_not_supported",
  BACKUP_FAILED: "backup_failed",
  /*SMTP_CONNECTION_ERROR: "smtp_connection_error",*/

//TABLES
  TABLE_NOT_FOUND: "table_not_found",
  TABLE_NUMBER_ALREADY_EXISTS: "table_number_already_exists",

//PRODUCTS
  PRODUCT_NOT_FOUND: "product_not_found",
  PRODUCT_ALREADY_EXISTS: "product_already_exists",
  INVALID_PRODUCT_NAME: "invalid_product_name",

//CATEGORIES
  CATEGORY_NOT_FOUND: "category_not_found",
  CATEGORY_ALREADY_EXISTS: "category_already_exists",
  INVALID_CATEGORY_NAME: "invalid_category_name",

//STATIONS
  STATION_NOT_FOUND: "station_not_found",
  STATION_NAME_ALREADY_EXISTS: "station_name_already_exists",
  INVALID_STATION_NAME: "invalid_station_name",

//LAYOUT
  LAYOUT_BACKGROUND_INVALID_FORMAT: "layout_background_invalid_format",
  LAYOUT_BACKGROUND_TOO_LARGE: "layout_background_too_large",

//PERMISSIONS
  PERMISSION_DENIED: "permission_denied",

//REPORTS
  REPORT_INVALID_DATE_RANGE: "report_invalid_date_range",

//SETTINGS
  BACKUP_DESTINATION_REQUIRED: "backup_destination_required",
  BACKUP_WEEKDAY_REQUIRED: "backup_weekday_required",
  BACKUP_MONTHDAY_REQUIRED: "backup_monthday_required"

} as const;

export type ErrorCode = typeof ErrorCode[keyof typeof ErrorCode];