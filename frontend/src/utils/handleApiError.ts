import { showToast } from "./showToast"

export interface ApiError extends Error {
  code?: string
  context?: any
  status?: number
}

export function handleApiError(error: any) {
  console.error("API ERROR:", error)
  const apiError = error?.response?.data
  const message = mapErrorToMessage({
    code: apiError?.error ?? error?.code,
    message: apiError?.detail ?? error?.message
  })
  showToast(message)
}


function mapErrorToMessage(error: any) {

  switch (error.code) {

    // ORDERS
    case "order_not_found":
      return "La orden no existe"

    case "order_already_closed":
      return "La orden ya fue cerrada"

    case "order_items_not_delivered":
      return "No se puede cerrar la orden: hay items sin entregar"

    case "order_empty":
      return "La orden no tiene productos"

    case "order_has_remaining_balance":
      return "La orden aún tiene saldo pendiente"


    // ORDER ITEMS
    case "item_not_found":
      return "Item no encontrado"

    case "item_already_send":
      return "El item ya fue enviado a cocina"

    case "not_pending_items_to_send":
      return "No hay items pendientes para enviar"


    // PAYMENTS
    case "payment_exceeds_remaining":
      return "El pago excede el saldo restante"

    case "payment_invalid_method":
      return "Método de pago inválido"


    // CASH REGISTER
    case "cash_register_not_open":
      return "No hay una caja abierta"

    case "cash_register_already_open":
      return "Ya existe una caja abierta"

    case "cash_register_pending_orders":
      return "No se puede cerrar la caja: hay órdenes abiertas"


    // TABLES
    case "table_not_found":
      return "Mesa no encontrada"

    case "table_number_already_exists":
      return "Ya existe una mesa con ese número"


    // PRODUCTS
    case "product_not_found":
      return "Producto no encontrado"


    // CATEGORIES
    case "category_not_found":
      return "Categoría no encontrada"


    // USERS
    case "user_not_found":
      return "Usuario no encontrado"


    default:
      return error.message || "Error inesperado"
  }
}
