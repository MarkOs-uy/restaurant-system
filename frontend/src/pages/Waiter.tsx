import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

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

export default function Waiter() {
  const [orders, setOrders] = useState<Order[]>([])

  useEffect(() => {
    fetchOrders()
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

      {orders.map(order => (
        <div
          key={order.id}
          style={{
            border: "1px solid #ccc",
            padding: 20,
            marginBottom: 20,
            borderRadius: 8
          }}
        >
          <h2>Mesa {order.table_number}</h2>

          <ul>
            {order.items.map(item => (
              <li key={item.id} style={{ marginBottom: 5 }}>
                {item.product_name} x {item.quantity} — {item.status}

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
