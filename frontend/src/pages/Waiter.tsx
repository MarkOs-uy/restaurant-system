import { useEffect, useReducer } from "react"
import { apiFetch } from "../api"
import { OrderItemStatus } from "../types/orderItemStatus"
import { wsService } from "../services/wsService"
import { OrderStatus } from "../types/orderStatus"
import { WSEvent } from "../types/webSocketEvents"

import type { WSEventParsed } from "../ws"
import type { Order } from "../types/order"

const bell = new Audio("/bell.mp3")

const playSound = () => {
  bell.currentTime = 0
  bell.play().catch(() => {})
}

/**
 * Devuelve el color visual correspondiente al estado
 * de un item de una orden.
 */
const statusColor = (status: OrderItemStatus) => {
    switch (status) {
        case OrderItemStatus.PENDING:
            return "#999"
        case OrderItemStatus.SENT:
            return "orange"
        case OrderItemStatus.READY:
            return "dodgerblue"
        case OrderItemStatus.DELIVERED:
            return "green"
        case OrderItemStatus.IN_PROGRESS:
            return "purple"
        case OrderItemStatus.CANCELLED:
            return "red"
        default:
            return "black"
    }
}

/**
 * Determina si un valor recibido en tiempo de ejecución
 * es un objeto con propiedades accesibles.
 *
 * Se utiliza como primera validación de los payloads
 * recibidos por WebSocket antes de acceder a sus campos.
 */
function isObject(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null
  )
}

/**
 * Verifica si un valor corresponde a uno de los estados
 * válidos de una orden.
 */
function isOrderStatus(
  value: unknown
): value is OrderStatus {
  return Object.values(OrderStatus).includes(
    value as OrderStatus
  )
}

/**
 * Verifica si un valor corresponde a uno de los estados
 * válidos de un item de una orden.
 */
function isOrderItemStatus(
  value: unknown
): value is OrderItemStatus {
  return Object.values(OrderItemStatus).includes(
    value as OrderItemStatus
  )
}

/**
 * Valida el payload recibido para ITEM_STATUS_CHANGED.
 *
 * Además de comprobar la existencia de las propiedades,
 * verifica que sus tipos sean compatibles con el modelo
 * utilizado por el frontend.
 */
function isItemStatusChangedPayload(
  value: unknown
): value is {
  order_id: number
  item_id: number
  status: OrderItemStatus
} {
  if (!isObject(value)) return false

  return (
    typeof value.order_id === "number" &&
    typeof value.item_id === "number" &&
    isOrderItemStatus(value.status)
  )
}

/**
 * Valida el payload recibido para ORDER_STATUS_CHANGED.
 */
function isOrderStatusChangedPayload(
  value: unknown
): value is {
  order_id: number
  status: OrderStatus
} {
  if (!isObject(value)) return false

  return (
    typeof value.order_id === "number" &&
    isOrderStatus(value.status)
  )
}

/**
 * Valida el payload recibido para ORDER_CLOSED.
 */
function isOrderClosedPayload(
  value: unknown
): value is {
  order_id: number
} {
  if (!isObject(value)) return false

  return typeof value.order_id === "number"
}

/**
 * Calcula cuántos minutos han transcurrido desde
 * la creación de una orden.
 *
 * Si la fecha es inexistente o inválida, devuelve 0.
 */
function orderWaitingMinutes(created_at?: string) {
  if (!created_at) return 0

  const normalized = created_at.replace(" -", "-")
  const created = new Date(normalized)

  if (isNaN(created.getTime())) return 0

  const diff = Date.now() - created.getTime()

  return Math.floor(diff / 60000)
}

/**
 * Determina el color utilizado para indicar visualmente
 * cuánto tiempo lleva esperando una orden.
 */
const waitingColor = (minutes: number) => {
  if (minutes >= 15) return "red"
  if (minutes >= 10) return "orange"

  return "#666"
}

/**
 * Indica si una orden contiene al menos un item
 * que ya está listo para ser entregado al cliente.
 */
const hasReadyItems = (order: Order) =>
  order.items.some(
    item => item.status === OrderItemStatus.READY
  )

/**
 * Indica si una orden todavía contiene items que
 * no fueron entregados.
 */
const hasActiveItems = (order: Order) =>
  order.items.some(
    item => item.status !== OrderItemStatus.DELIVERED
  )

/* =========================
ACCIONES DEL REDUCER
========================= */

type OrdersAction =
  | {
  type: "SET_ORDERS"
  orders: Order[]
  }
  | {
  type: "ITEM_STATUS_CHANGED"
  order_id: number
  item_id: number
  status: OrderItemStatus
  }
  | {
  type: "ORDER_STATUS_CHANGED"
  order_id: number
  status: OrderStatus
  }
  | {
  type: "ORDER_CLOSED"
  order_id: number
  }

/**
 * Actualiza el estado local de las órdenes a partir
 * de acciones provenientes del fetch inicial o de
 * eventos WebSocket.
 *
 * El reducer no realiza llamadas HTTP ni efectos secundarios.
 * Su única responsabilidad es transformar el estado actual
 * en un nuevo estado.
 */
function ordersReducer(
  state: Order[],
  action: OrdersAction
): Order[] {
  switch (action.type) {

    case "SET_ORDERS":
      return action.orders

    case "ITEM_STATUS_CHANGED":
      return state.map(order => {

        if (order.id !== action.order_id) {
          return order
        }

        return {
          ...order,
          items: order.items.map(item =>
            item.id === action.item_id
              ? {
                  ...item,
                  status: action.status
                }
              : item
          )
        }
      })

    case "ORDER_STATUS_CHANGED":
      return state.map(order =>
        order.id === action.order_id
          ? {
              ...order,
              status: action.status
            }
          : order
      )

    case "ORDER_CLOSED":
      return state.filter(
        order => order.id !== action.order_id
      )

    default:
      return state
  }
}

/* =========================
   COMPONENT
========================= */
export default function Waiter() {

  const [orders, dispatch] = useReducer(ordersReducer, [])

  /**
   * Obtiene las órdenes activas del restaurante y reemplaza
   * el estado local con la información actualizada.
   *
   * Se utiliza tanto durante la carga inicial de la pantalla
   * como en respuesta a eventos WebSocket que indican que
   * la información de una orden pudo haber cambiado.
   */
  const fetchOrders = async () => {
    const data = await apiFetch<Order[]>("/orders/active")
    dispatch({
      type: "SET_ORDERS",
      orders: data
    })
  }

  /**
   * Suscribe la pantalla a los eventos WebSocket relevantes
   * para el estado de las órdenes del mozo.
   *
   * Algunos eventos pueden actualizar el estado local directamente,
   * mientras que otros provocan una nueva consulta al backend para
   * obtener la representación completa y actualizada de las órdenes.
   */
  useEffect(() => {

    fetchOrders()

    const handler = ({ type, data }: WSEventParsed) => {

      console.log("WS EVENT:", type, data)

      switch (type) {

        case WSEvent.NEW_ITEM:
        case WSEvent.ORDER_UPDATED:
          fetchOrders()
          break

        case WSEvent.ITEM_READY:
          playSound()
          fetchOrders()
          break

        case WSEvent.ITEM_STATUS_CHANGED:
          if (!isItemStatusChangedPayload(data)) {
            console.warn(
              "Payload inválido para ITEM_STATUS_CHANGED",
              data
            )
            return
          }
          //fetchOrders()
          dispatch({
            type: "ITEM_STATUS_CHANGED",
            order_id: data.order_id,
            item_id: data.item_id,
            status: data.status
          })

          break

        case WSEvent.ORDER_STATUS_CHANGED:
          if (!isOrderStatusChangedPayload(data)) {
            console.warn(
              "Payload inválido para ORDER_STATUS_CHANGED",
              data
            )
            return
          }
          //fetchOrders()
          dispatch({
            type: "ORDER_STATUS_CHANGED",
            order_id: data.order_id,
            status: data.status
          })

          break

        case WSEvent.ORDER_CLOSED:
          if (!isOrderClosedPayload(data)) {
            console.warn(
              "Payload inválido para ORDER_CLOSED",
              data
            )
            return
          }
          //fetchOrders()
          dispatch({
            type: "ORDER_CLOSED",
            order_id: data.order_id
          })

          break
      }
    }

    wsService.subscribe(handler)

    return () => {
      wsService.unsubscribe(handler)
    }

  }, [])

  /**
   * Marca un único item como entregado.
   *
   * El backend emitirá el evento correspondiente y la pantalla
   * se actualizará a través del WebSocket.
   */
  const markAsDelivered = async (itemId: number) => {
    await apiFetch(`/order-items/${itemId}/status`, {
      method: "PATCH",
      body: {
        status: OrderItemStatus.DELIVERED
      }
    })
  }

  /**
   * Marca como entregados todos los items que actualmente
   * se encuentran en estado READY dentro de una orden.
   *
   * Las actualizaciones se ejecutan en paralelo porque son
   * operaciones independientes.
   */
  const deliverAllReady = async (order: Order) => {
    const readyItems = order.items.filter(
      item => item.status === OrderItemStatus.READY
    )

    if (readyItems.length === 0) return

    await Promise.all(
      readyItems.map(item =>
        apiFetch(`/order-items/${item.id}/status`, {
          method: "PATCH",
          body: {
            status: OrderItemStatus.DELIVERED
          }
        })
      )
    )
  }

  /* =========================
     FILTROS
  ========================= */
  const visibleOrders = orders
    .map(order => ({
      ...order,
      items: order.items.filter(i => i.status !== OrderItemStatus.DELIVERED)
    }))
    .filter(hasActiveItems)

  const ordersSorted = [...visibleOrders].sort((a, b) => {
    const readyDiff =
      Number(hasReadyItems(b)) - Number(hasReadyItems(a))
    if (readyDiff !== 0) return readyDiff
    return (
      new Date(a.created_at).getTime() -
      new Date(b.created_at).getTime()
    )
  })

  const readyOrders = ordersSorted.filter(hasReadyItems)

  const cookingOrders = ordersSorted.filter(
    order => !hasReadyItems(order)
  )

  /* =========================
     RENDER
  ========================= */

  const renderOrders = (ordersList: Order[]) =>
    ordersList.map(order => {
      const minutes = orderWaitingMinutes(order.created_at)
      const ready = hasReadyItems(order)
      return (
        <div
          key={order.id}
          className="card"
          style={{
            border: ready
              ? "1px solid var(--status-inprogress)"
              : "1px solid var(--color-border)",
            backgroundColor: ready
              ? "rgba(59, 130, 246, 0.1)"
              : "rgba(22, 28, 45, 0.4)",
            boxShadow: ready
              ? "0 0 16px rgba(59, 130, 246, 0.15)"
              : "var(--shadow-sm)",
            marginBottom: 20
          }}
        >
          <h2>
            Mesa {order.table_number}
            {ready && (
              <span style={{ marginLeft: 10 }}>🔔</span>
            )}
            <span
              style={{
                marginLeft: 12,
                fontSize: 14,
                fontWeight: "bold",
                color: waitingColor(minutes)
              }}
            >
              ⏱ {minutes} min
            </span>
          </h2>

          {ready && (
            <button
              onClick={() => deliverAllReady(order)}
              style={{
                marginBottom: 10,
                backgroundColor: "green",
                color: "white",
                borderRadius: 6,
                padding: "6px 12px",
                fontWeight: "bold"
              }}
            >
              Entregar todo
            </button>
          )}

          <ul>
            {order.items.map(item => (
              <li key={item.id} style={{ marginBottom: 5 }}>
                {item.product_name} x {item.quantity}
                <span
                  style={{
                    marginLeft: 10,
                    padding: "2px 8px",
                    borderRadius: 6,
                    backgroundColor: statusColor(item.status),
                    color: "white",
                    fontSize: 12,
                    fontWeight: "bold"
                  }}
                >
                  {item.status}
                </span>

                {item.status === OrderItemStatus.READY && (
                  <button
                    onClick={() => markAsDelivered(item.id)}
                    style={{
                      marginLeft: 10,
                      backgroundColor: "green",
                      color: "white",
                      borderRadius: 6,
                      padding: "4px 8px"
                    }}
                  >
                    Entregar
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )
    })

  return (
    <div style={{ padding: 40 }}>
      <h1>Pantalla de Mozo</h1>
      {orders.length === 0 && ( <p>No hay órdenes activas</p>)}
      {readyOrders.length > 0 && (
        <>
          <h2 style={{ color: "dodgerblue" }}>
            🔔 Listos para entregar
          </h2>
          {renderOrders(readyOrders)}
        </>
      )}
      {cookingOrders.length > 0 && (
        <>
          <h2 style={{ marginTop: 40 }}>
            ⏳ En preparación
          </h2>
          {renderOrders(cookingOrders)}
        </>
      )}
    </div>
  )

}