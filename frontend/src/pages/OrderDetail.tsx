import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { API_URL } from "../api"

interface Item {
  product_name: string
  quantity: number
  unit_price: number
}

interface Payment {
  id: number
  amount: number
  method: string
}

interface Order {
  order_id: number
  table_number: number
  status: string
  items: Item[]
  payments: Payment[]
  total: number
  total_paid: number
  remaining: number
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
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("CASH")

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
    if (order?.status === "CLOSED") return

    await fetch(`${API_URL}/orders/${id}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_id: productId,
        quantity: 1
      })
    })

    fetchOrder()
  }

  const registerPayment = async () => {
    if (!paymentAmount) return

    await fetch(`${API_URL}/orders/${id}/payments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: Number(paymentAmount),
        method: paymentMethod
      })
    })

    setPaymentAmount("")
    fetchOrder()
  }

  const closeOrder = async () => {
    await fetch(`${API_URL}/orders/${id}/force-close`, {
      method: "POST"
    })

    fetchOrder()
  }

  if (!order) return <p>Cargando...</p>

  const getStatusColor = () => {
    switch (order.status) {
      case "OPEN": return "green"
      case "SENT": return "orange"
      case "IN_PROGRESS": return "blue"
      case "READY": return "purple"
      case "CLOSED": return "gray"
      case "CANCELLED": return "red"
      default: return "black"
    }
  }

  return (
    <div style={{ padding: 40, maxWidth: 900 }}>
      <h1>Orden #{order.order_id}</h1>
      <p>Mesa: {order.table_number}</p>
      <p>
        Estado:{" "}
        <strong style={{ color: getStatusColor() }}>
          {order.status}
        </strong>
      </p>

      {/* ITEMS */}
      <h2>Items</h2>
      <ul>
        {order.items.map((item, index) => (
          <li key={index}>
            {item.product_name} x {item.quantity} — $
            {(item.quantity * item.unit_price).toFixed(2)}
          </li>
        ))}
      </ul>

      <h3>Total: ${order.total.toFixed(2)}</h3>

      <hr />

      {/* PAGOS */}
      <h2>Pagos</h2>

      {order.payments.length === 0 && <p>No hay pagos registrados</p>}

      <ul>
        {order.payments.map(p => (
          <li key={p.id}>
            ${p.amount.toFixed(2)} — {p.method}
          </li>
        ))}
      </ul>

      <p><strong>Total pagado:</strong> ${order.total_paid.toFixed(2)}</p>
      <p><strong>Saldo pendiente:</strong> ${order.remaining.toFixed(2)}</p>

      {order.remaining > 0 && order.status !== "CLOSED" && (
        <>
          <h3>Registrar Pago</h3>

          <input
            type="number"
            placeholder="Monto"
            value={paymentAmount}
            onChange={e => setPaymentAmount(e.target.value)}
            style={{ marginRight: 10 }}
          />

          <select
            value={paymentMethod}
            onChange={e => setPaymentMethod(e.target.value)}
            style={{ marginRight: 10 }}
          >
            <option value="CASH">Efectivo</option>
            <option value="CARD">Tarjeta</option>
            <option value="TRANSFER">Transferencia</option>
          </select>

          <button onClick={registerPayment}>
            Pagar
          </button>
        </>
      )}

      {/* CERRAR ORDEN */}
      {order.remaining === 0 && order.status !== "CLOSED" && (
        <div style={{ marginTop: 20 }}>
          <button
            onClick={closeOrder}
            style={{
              padding: 10,
              backgroundColor: "black",
              color: "white",
              borderRadius: 8
            }}
          >
            Cerrar Orden
          </button>
        </div>
      )}

      <hr />

      {/* PRODUCTOS */}
      <h2>Agregar Productos</h2>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {products.map(p => (
          <button
            key={p.id}
            disabled={order.status === "CLOSED"}
            onClick={() => addProduct(p.id)}
            style={{
              padding: 10,
              borderRadius: 8,
              cursor: order.status === "CLOSED" ? "not-allowed" : "pointer",
              opacity: order.status === "CLOSED" ? 0.5 : 1
            }}
          >
            {p.name} - ${p.price}
          </button>
        ))}
      </div>
    </div>
  )
}
