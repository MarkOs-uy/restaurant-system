import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { API_URL, getAuthHeaders } from "../api"

interface OrderItem {
  product_name: string
  quantity: number
  unit_price: number
}

interface Order {
  id: number
  table_number: number
  status: string
  items: OrderItem[]
  total: number
}

export default function OrderPage() {
  const { orderId } = useParams()
  const id = Number(orderId)

  const [order, setOrder] = useState<Order | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/orders/${id}`,{headers: getAuthHeaders()})
      .then(res => res.json())
      .then(data => setOrder(data))
      .catch(err => console.error("Error cargando orden:", err))
  }, [id])

  if (!order) return <h2>Cargando orden...</h2>

  return (
    <div style={{ padding: 40 }}>
      <h1>Orden #{order.id}</h1>
      <h2>Mesa {order.table_number}</h2>
      <p>Estado: {order.status}</p>

      <h3>Items:</h3>
      {order.items.length === 0 && <p>No hay productos aún</p>}

      {order.items.map((item, index) => (
        <div key={index}>
          {item.product_name} x{item.quantity} - ${item.unit_price}
        </div>
      ))}

      <h2>Total: ${order.total}</h2>
    </div>
  )
}
