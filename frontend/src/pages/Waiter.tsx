import { useEffect, useRef, useState } from "react"
import { apiFetch, WS_URL } from "../api"

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

const hasReadyItems = (order: Order) =>
  order.items.some(item => item.status === "READY")

const bell = new Audio("/bell.mp3")

const playSound = () => {
  bell.currentTime = 0
  bell.play().catch(() => {})
}

function orderWaitingMinutes(created_at?: string) {
  if (!created_at) return 0

  const normalized = created_at.replace(" -", "-")
  const created = new Date(normalized)

  console.log("parsed date:", created)

  if (isNaN(created.getTime())) return 0

  const diff = Date.now() - created.getTime()
  return Math.floor(diff / 60000)
}

const waitingColor = (minutes: number) => {
  if (minutes >= 15) return "red"
  if (minutes >= 10) return "orange"
  return "#666"
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


export default function Waiter() {

  const [orders, setOrders] = useState<Order[]>([])

  const fetchingRef = useRef(false)
  const pendingRef = useRef(false)

  // FETCH PROTEGIDO
  const fetchTimerRef = useRef<any>(null)

  const safeFetchOrders = () => {
    if (fetchTimerRef.current) {
      clearTimeout(fetchTimerRef.current)
    }
    fetchTimerRef.current = setTimeout(async () => {
      if (fetchingRef.current) {
        pendingRef.current = true
        return
      }
      fetchingRef.current = true
      try {
        const data = await apiFetch("/orders/active")
        setOrders(data)
      } finally {
        fetchingRef.current = false
        if (pendingRef.current) {
          pendingRef.current = false
          safeFetchOrders()
        }
      }
    }, 300)
  }

  useEffect(() => {

    let ws: WebSocket | null = null
    let reconnectTimer: any = null

    safeFetchOrders()

    const connect = () => {

      ws = new WebSocket(`${WS_URL}/ws?token=${localStorage.getItem("token")}`)

      ws.onopen = () => {
        console.log("Waiter WS connected")
      }

      ws.onmessage = (event) => {

        let data

        try {
          data = JSON.parse(event.data)
        } catch {
          return
        }

        switch (data.type) {

          case "ITEM_STATUS_CHANGED":
            setOrders(prev =>
              prev.map(order => {
                if (order.id !== data.order_id) return order
                return {
                  ...order,
                  items: order.items.map(item => {
                    if (item.id !== data.item_id) return item
                    if (item.status === "DELIVERED") return item
                    return { ...item, status: "IN_PROGRESS" }
                  })
                }
              })
            )

            setTimeout(safeFetchOrders, 2000)

          break

          case "ITEM_READY":

            playSound()

            setOrders(prev =>
              prev.map(order => {
                if (order.id !== data.order_id) return order

                return {
                  ...order,
                  items: order.items.map(item =>
                    item.id === data.item_id
                      ? { ...item, status: "READY" }
                      : item
                  )
                }
              })
            )

            setTimeout(safeFetchOrders, 2000)

          break

          case "ORDER_STATUS_CHANGED":

            setOrders(prev =>
              prev.map(order =>
                order.id === data.order_id
                  ? { ...order, status: data.status }
                  : order
              )
            )

          break

          case "ORDER_UPDATED":

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

  // FILTRAR ITEMS VISIBLES
  const visibleOrders = orders.map(order => ({
    ...order,
    items: order.items.filter(i => i.status !== "DELIVERED")
  }))

  // ORDENAR POR READY Y ANTIGÜEDAD
  const ordersSorted = [...visibleOrders].sort((a, b) => {
    const readyDiff =
      Number(hasReadyItems(b)) - Number(hasReadyItems(a))
    if (readyDiff !== 0) return readyDiff
    return (
      new Date(a.created_at).getTime() -
      new Date(b.created_at).getTime()
    )
  })

  // SEPARAR READY / COOKING
  const readyOrders = ordersSorted.filter(hasReadyItems)

  const cookingOrders = ordersSorted.filter(
    order => !hasReadyItems(order)
  )


  const markAsDelivered = async (itemId: number) => {
    await apiFetch(`/order-items/${itemId}/status`, {
      method: "PATCH",
      body: { status: "DELIVERED" }
    })
  }


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
              ? "2px solid dodgerblue"
              : "1px solid #ccc",
            backgroundColor: ready
              ? "#eef6ff"
              : "white",
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

          {hasReadyItems(order) && (
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