import { useEffect, useReducer } from "react"
import { apiFetch } from "../api"
import { wsService } from "../services/wsService"
import type { WSEventParsed } from "../ws"

interface Item {
  id: number
  product_name: string
  quantity: number
  status: string
}

interface Order {
  id: number
  table_number: number
  status: string
  created_at: string
  items: Item[]
}

type Event =
  | { type: "SET_ORDERS"; orders: Order[] }
  | { type: "ITEM_STATUS_CHANGED"; order_id: number; item_id: number; status: string }
  | { type: "ORDER_STATUS_CHANGED"; order_id: number; status: string }
  | { type: "ORDER_UPDATED"; order_id: number }
  | { type: "ORDER_CLOSED"; order_id: number }

const bell = new Audio("/bell.mp3")

const playSound = () => {
  bell.currentTime = 0
  bell.play().catch(() => {})
}

const statusColor = (status: string) => {
  switch (status) {
    case "PENDING":
      return "#999"
    case "SENT":
      return "orange"
    case "READY":
      return "dodgerblue"
    case "DELIVERED":
      return "green"
    case "IN_PROGRESS":
      return "purple"
    default:
      return "black"
  }
}

function orderWaitingMinutes(created_at?: string) {
  if (!created_at) return 0
  const normalized = created_at.replace(" -", "-")
  const created = new Date(normalized)
  if (isNaN(created.getTime())) return 0
  const diff = Date.now() - created.getTime()
  return Math.floor(diff / 60000)
}

const waitingColor = (minutes: number) => {
  if (minutes >= 15) return "red"
  if (minutes >= 10) return "orange"
  return "#666"
}

const hasReadyItems = (order: Order) =>
  order.items.some(item => item.status === "READY")

const hasActiveItems = (order: Order) =>
  order.items.some(item => item.status !== "DELIVERED")

/* =========================
   REDUCER
========================= */

function ordersReducer(state: Order[], event: Event): Order[] {
  switch (event.type) {
    case "SET_ORDERS":
      return event.orders

    case "ITEM_STATUS_CHANGED":
      return state.map(order => {
        if (order.id !== event.order_id) return order
        const updatedItems = order.items.map(item =>
          item.id === event.item_id
            ? { ...item, status: event.status }
            : item
        )
        return {
          ...order,
          items: updatedItems
        }
      })

    case "ORDER_STATUS_CHANGED":
      return state.map(order =>
        order.id === event.order_id
          ? { ...order, status: event.status }
          : order
      )

    case "ORDER_CLOSED":
      return state.filter(order => order.id !== event.order_id)

    case "ORDER_UPDATED":
      return state

    default:
      return state

  }
}

/* =========================
   COMPONENT
========================= */

export default function Waiter() {

  const [orders, dispatch] = useReducer(ordersReducer, [])

  /* =========================
     FETCH
  ========================= */

  const fetchOrders = async () => {
    const data = await apiFetch("/orders/active")
    dispatch({
      type: "SET_ORDERS",
      orders: data
    })
  }

  /* =========================
     WEBSOCKET
  ========================= */

  useEffect(() => {
    fetchOrders()
    const handler = ({ type, data }: WSEventParsed) => {
      console.log("WS EVENT:", type, data)
      if (type === "ITEM_READY") {
        playSound()
      }
      dispatch({
        type,
        ...data
      })
    }
    wsService.subscribe(handler)
    return () => {
      wsService.unsubscribe(handler)
    }
  }, [])

  /* =========================
     ACTIONS
  ========================= */

  const markAsDelivered = async (itemId: number) => {
    await apiFetch(`/order-items/${itemId}/status`, {
      method: "PATCH",
      body: { status: "DELIVERED" }
    })
  }

  const deliverAllReady = async (order: Order) => {
    const readyItems = order.items.filter(i => i.status === "READY")
    if (readyItems.length === 0) return
    await Promise.all(
      readyItems.map(i =>
        apiFetch(`/order-items/${i.id}/status`, {
          method: "PATCH",
          body: { status: "DELIVERED" }
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
      items: order.items.filter(i => i.status !== "DELIVERED")
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

                {item.status === "READY" && (

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

      {orders.length === 0 && (
        <p>No hay órdenes activas</p>
      )}

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