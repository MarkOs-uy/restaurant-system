import { useEffect, useState } from "react"
import { API_URL, WS_URL, getAuthHeaders } from "../api"

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
  items: Item[]
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

const hasReadyItems = (order: Order) => {
  return order.items.some(item => item.status === "READY")
}

const playSound = () => {
  const audio = new Audio("/bell.mp3")
  audio.play().catch(() => {})
}

export default function Waiter() {
  const [orders, setOrders] = useState<Order[]>([])

  useEffect(() => {

    let ws: WebSocket | null = null
    let reconnectTimer: any = null

    // 🔥 CONTROL DE FETCH
    let fetching = false
    let pending = false

    const safeFetchOrders = async () => {

      if (fetching) {
        pending = true
        return
      }

      fetching = true

      await fetchOrders()

      fetching = false

      if (pending) {
        pending = false
        safeFetchOrders()
      }
    }

    // 👇 PRIMER FETCH
    safeFetchOrders()

    const connect = () => {

      ws = new WebSocket(`${WS_URL}/ws?token=${localStorage.getItem("token")}`)

      ws.onopen = () => {
        console.log("Waiter WS connected")
      }

      ws.onmessage = (event) => {

        const data = JSON.parse(event.data)

        switch (data.type) {

          case "ITEM_READY":
            playSound()
            setOrders(prev => prev.map(order => {
              if (order.id !== data.order_id) return order
              return {
                ...order,
                items: order.items.map(item =>
                  item.id === data.item_id
                    ? { ...item, status: "READY" }
                    : item
                )
              }
            }))
            setTimeout(() => {
              safeFetchOrders()
            }, 2000)
            break

            case "ORDER_STATUS_CHANGED":
              setOrders(prev => prev.map(order =>
                order.id === data.order_id
                  ? { ...order, status: data.status }
                  : order
              ))
              break

            case "ORDER_UPDATED":case "ORDER_UPDATED":
              safeFetchOrders()
            break   

            case "ORDER_CLOSED":
              setOrders(prev =>
                prev.filter(order => order.id !== data.order_id)
              )
              break
        }
      }

      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 2000)
      }

      ws.onerror = () => {
        ws?.close()
      }

    }

    connect()

    return () => {
      ws?.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }

  }, [])

  const fetchOrders = async () => {
    const res = await fetch(`${API_URL}/orders/active`, {headers: getAuthHeaders()})
    const data = await res.json()
    setOrders(data)
  }

  const markAsDelivered = async (itemId: number) => {
    const res = await fetch(
      `${API_URL}/order-items/${itemId}/status`,
      {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({ status: "DELIVERED" })
      }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    fetchOrders()
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>Pantalla de Mozo</h1>

      {orders.length === 0 && <p>No hay órdenes activas</p>}

      {[...orders]
        .sort((a, b) => Number(hasReadyItems(b)) - Number(hasReadyItems(a)))
        .map(order => (
          <div
            key={order.id}
            className="card"
            style={{
              border: hasReadyItems(order) ? "2px solid dodgerblue" : "1px solid #ccc",
              backgroundColor: hasReadyItems(order) ? "#eef6ff" : "white",
              marginBottom: 20,
            }}
  >
            <h2>
              Mesa {order.table_number}
              {hasReadyItems(order) && (
                <span style={{ marginLeft: 10 }}>🔔</span>
              )}
            </h2>

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
      ))}
    </div>
  )
}
