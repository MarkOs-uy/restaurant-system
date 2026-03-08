import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { API_URL, getAuthHeaders } from "../api"

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

  console.log("Calling:", `${API_URL}/kitchen/stations/${station}/items`)
  const fetchItems = async () => {
    const res = await fetch(
      `${API_URL}/kitchen/stations/${station}/items`, {
      headers: getAuthHeaders()
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
        headers: getAuthHeaders(),
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

  const groupedByTable = items.reduce((acc, item) => {
    if (!acc[item.table_number]) {
      acc[item.table_number] = []
    }

    acc[item.table_number].push(item)

    return acc
  }, {} as Record<number, KitchenItem[]>)
  
  return (
    <div style={{ padding: 40 }}>
      <h1>Estación #{station}</h1>

      {items.length === 0 && (
        <p>No hay pedidos pendientes</p>
      )}

      {Object.entries(groupedByTable).map(([tableNumber, tableItems]) => (
        <div
          key={tableNumber}
          style={{
            border: "2px solid #ddd",
            padding: 20,
            marginBottom: 20,
            borderRadius: 10,
            background: "#fafafa"
          }}
        >
          <h2>Mesa {tableNumber}</h2>

          {tableItems.map(item => (
            <div
              key={item.item_id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 10,
                padding: 10,
                border: "1px solid #eee",
                borderRadius: 6,
                background: "white"
              }}
            >
              <div>
                {item.product_name} x {item.quantity}
              </div>

              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>

                <strong style={{ color: getStatusColor(item.status) }}>
                  {item.status}
                </strong>

                {item.status === "SENT" && (
                  <button
                    onClick={() =>
                      updateStatus(item.item_id, "IN_PROGRESS")
                    }
                  >
                    Iniciar
                  </button>
                )}

                {item.status === "IN_PROGRESS" && (
                  <button
                    onClick={() =>
                      updateStatus(item.item_id, "READY")
                    }
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
            </div>
          ))}

        </div>
      ))}
    </div>
  )
}

