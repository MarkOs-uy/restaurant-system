import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { API_URL } from "../api"

interface Item {
  product_name: string
  quantity: number
  unit_price: number
}

interface Order {
  order_id: number
  table_number: number
  status: string
  items: Item[]
  total: number
}

interface Product {
  id: number
  name: string
  price: number
}

export default function OrderDetail() {
  const { orderId } = useParams()
  const id = Number(orderId)

  const [order, setOrder] = useState<Order | null>(null)
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    fetchOrder()
    fetchProducts()
  }, [])

  const fetchOrder = async () => {
    const res = await fetch(`${API_URL}/orders/${id}`)
    const data = await res.json()
    setOrder(data)
  }

  const fetchProducts = async () => {
    const res = await fetch(`${API_URL}/products/`)
    const data = await res.json()
    setProducts(data)
  }

  const addProduct = async (productId: number) => {
    await fetch(`${API_URL}/orders/${id}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_id: productId,
        quantity: 1
      })
    })

    fetchOrder() // refresca la orden
  }

  if (!order) return <p>Cargando...</p>

  return (
    <div style={{ padding: 40 }}>
      <h1>Orden #{order.order_id}</h1>
      <p>Mesa: {order.table_number}</p>
      <p>Estado: {order.status}</p>

      <h2>Items</h2>
      <ul>
        {order.items.map((item, index) => (
          <li key={index}>
            {item.product_name} x {item.quantity} — ${item.unit_price}
          </li>
        ))}
      </ul>

      <h3>Total: ${order.total}</h3>

      <hr />

      <h2>Productos</h2>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {products.map(p => (
          <button
            key={p.id}
            onClick={() => addProduct(p.id)}
            style={{
              padding: 10,
              borderRadius: 8,
              cursor: "pointer"
            }}
          >
            {p.name} - ${p.price}
          </button>
        ))}
      </div>
    </div>
  )
}
