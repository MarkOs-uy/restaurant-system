import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { API_URL, API_HEADERS } from "../api"

interface KitchenItem {
  item_id: number
  product_name: string
  quantity: number
  status: string
  table_number: number
  order_id: number
}

export default function Kitchen() {

  const { stationId } = useParams()
  const station = Number(stationId)

  const [items, setItems] = useState<KitchenItem[]>([])

  const fetchItems = async () => {
    const res = await fetch(
      `${API_URL}/kitchen/stations/${station}/items`, {
      headers: API_HEADERS
    }
    )
    const data = await res.json()
    setItems(data)
  }

  useEffect(() => {
    if (!station) return

    fetchItems()

    const interval = setInterval(() => {
      fetchItems()
    }, 5000)

    return () => clearInterval(interval)
  }, [station])

  const updateStatus = async (
    itemId: number,
    newStatus: string
  ) => {
    await fetch(
      `${API_URL}/order-items/${itemId}/status`,
      {
        method: "PATCH",
        headers: API_HEADERS,
        body: JSON.stringify({ status: newStatus })
      }
    )

    fetchItems()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SENT": return "orange"
      case "IN_PROGRESS": return "blue"
      case "READY": return "green"
      default: return "black"
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>Estación #{station}</h1>

      {items.length === 0 && (
        <p>No hay pedidos pendientes</p>
      )}

      {items.map(item => (
        <div
          key={item.item_id}
          style={{
            border: "1px solid #ccc",
            padding: 15,
            marginBottom: 15,
            borderRadius: 8
          }}
        >
          <h3>Mesa {item.table_number}</h3>

          <p>
            {item.product_name} x {item.quantity}
          </p>

          <p>
            Estado:{" "}
            <strong style={{ color: getStatusColor(item.status) }}>
              {item.status}
            </strong>
          </p>

          {item.status === "SENT" && (
            <button
              onClick={() =>
                updateStatus(item.item_id, "IN_PROGRESS")
              }
              style={{ marginRight: 10 }}
            >
              Iniciar
            </button>
          )}

          {item.status === "IN_PROGRESS" && (
            <button
              onClick={() =>
                updateStatus(item.item_id, "READY")
              }
              style={{ marginRight: 10 }}
            >
              Listo
            </button>
          )}

          {item.status === "READY" && (
            <button
              onClick={() =>
                updateStatus(item.item_id, "DELIVERED")
              }
            >
              Entregado
            </button>
          )}
        </div>
      ))}
    </div>
  )
}

