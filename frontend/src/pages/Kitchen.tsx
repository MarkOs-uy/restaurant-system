import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { apiFetch, WS_URL } from "../api"

interface KitchenItem {
  item_id: number
  product_name: string
  quantity: number
  status: string
  table_number: number
  order_id: number
  created_at: string
}

export default function Kitchen() {

  const { stationId } = useParams()
  const station = Number(stationId)
  const navigate = useNavigate()

  const [items, setItems] = useState<KitchenItem[]>([])
  const [stationName, setStationName] = useState("")

  const fetchItems = async () => {
    const data = await apiFetch(
      `/kitchen/stations/${station}/items`
    )
    setItems(data)
  }

  useEffect(() => {
    if (!station) return
    fetchItems()
    fetchStation()
  }, [station])

//-----------------------------------------------------------

  const fetchStation = async () => {
    const data = await apiFetch(
      `/production-stations/${station}`
    )
    setStationName(data.name)
  }

  //-----------------------------------------------------------

  const updateStatus = async (
    itemId: number,
    newStatus: string
  ) => {
    await apiFetch(
      `/order-items/${itemId}/status`,
      {
        method: "PATCH",
        body: { status: newStatus }
      }
    )
    fetchItems()
  }

//-----------------------------------------------------------

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SENT": return "orange"
      case "IN_PROGRESS": return "blue"
      case "READY": return "green"
      default: return "black"
    }
  }

//-----------------------------------------------------------

  const getWaitingTime = (createdAt: string) => {
    const created = new Date(createdAt).getTime()
    const now = Date.now()

    const diff = Math.floor((now - created) / 1000)

    const minutes = Math.floor(diff / 60)
    const seconds = diff % 60

    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

//-----------------------------------------------------------

  const groupedOrders = items.reduce((acc, item) => {
    if (!acc[item.order_id]) {
      acc[item.order_id] = {
        table: item.table_number,
        created_at: item.created_at,
        items: []
      }
    }

    acc[item.order_id].items.push(item)

    return acc
  }, {} as Record<number, { table: number, created_at: string, items: KitchenItem[] }>)

//-----------------------------------------------------------

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: any = null
    let shouldReconnect = true

    // 🔥 CONTROL DE FETCH
    let fetching = false
    let pending = false

    const safeFetchItems = async () => {

      if (fetching) {
        pending = true
        return
      }

      fetching = true

      await fetchItems()

      fetching = false

      if (pending) {
        pending = false
        safeFetchItems()
      }
    }

    // 👉 carga inicial
    safeFetchItems()

    const connect = () => {

      const token = localStorage.getItem("token")

      ws = new WebSocket(
        `${WS_URL}/ws?token=${token}&station_id=${stationId}`
      )

      ws.onopen = () => {
        console.log("Kitchen WS connected")
      }

      ws.onmessage = (event) => {

        const data = JSON.parse(event.data)

        switch (data.type) {

          case "ORDER_UPDATED":
          case "ORDER_STATUS_CHANGED":
            safeFetchItems()
            break

        }

      }

      ws.onclose = () => {
        console.log("Kitchen WS disconnected")

        if (!shouldReconnect) return

        reconnectTimer = setTimeout(() => {
          console.log("Reconnecting kitchen WS...")
          connect()
        }, 2000)
      }

      ws.onerror = () => {
        ws?.close()
      }

    }

    connect()

    return () => {
      shouldReconnect = false
      ws?.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }

  }, [stationId])

//-----------------------------------------------------------

return (
    <div style={{ padding: 40 }}>
      <h1>Estación {stationName} - (#{station})</h1>

      <button
        onClick={() => navigate("/kitchen")}
        style={{ marginBottom: 20 }}
      >
        Cambiar estación
      </button>

      {items.length === 0 && (
        <p>No hay pedidos pendientes</p>
      )}

      {Object.entries(groupedOrders).map(([orderId, order]) => (
        <div
          key={orderId}
          className="card"
          style={{
            border: "2px solid #ddd",
            marginBottom: 20,
            background: "#fafafa",
            boxShadow: "0 3px 10px rgba(0,0,0,0.08)"
          }}
        >

          <h2 style={{ fontSize: 28, marginBottom: 10 }}>
            Mesa {order.table}

            {order.created_at && (
              <span
                style={{
                  marginLeft: 15,
                  fontSize: 16,
                  fontWeight: "normal",
                  color: "#666"
                }}
              >
                ⏱ {getWaitingTime(order.created_at)}
              </span>
            )}

          </h2>

          {order.items.map(item => (

            <div
              key={item.item_id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 12,
                padding: 12,
                border: "1px solid #eee",
                borderRadius: 6,
                background:
                  item.status === "SENT"
                    ? "#fff3cd"
                    : "white"
              }}
            >

              <div style={{ fontSize: 20, fontWeight: 600 }}>
                {item.product_name} × {item.quantity}
              </div>

              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>

                <strong
                  style={{
                    background: getStatusColor(item.status),
                    color: "white",
                    padding: "6px 12px",
                    borderRadius: 6,
                    fontSize: 14
                  }}
                >
                  {item.status}
                </strong>

                {item.status === "SENT" && (
                  <button
                    style={{
                      fontSize: 16,
                      padding: "8px 14px"
                    }}
                    onClick={() =>
                      updateStatus(item.item_id, "IN_PROGRESS")
                    }
                  >
                    Iniciar
                  </button>
                )}

                {item.status === "IN_PROGRESS" && (
                  <button
                    style={{
                      fontSize: 16,
                      padding: "8px 14px"
                    }}
                    onClick={() =>
                      updateStatus(item.item_id, "READY")
                    }
                  >
                    Listo
                  </button>
                )}

                {item.status === "READY" && (
                  <button
                    style={{
                      fontSize: 16,
                      padding: "8px 14px"
                    }}
                    onClick={() =>
                      updateStatus(item.item_id, "DELIVERED")
                    }
                  >
                    Entregado
                  </button>
                )}

              </div>

            </div>

          ))}
        </div>
      ))}
    </div>
  )
}

