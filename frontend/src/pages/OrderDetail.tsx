import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

interface Item {
  product_name: string
  quantity: number
  unit_price: number
  status: string
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

interface Category {
  id: number
  name: string
  products: Product[]
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
  const [categories, setCategories] = useState<Category[]>([])
  const [openCategory, setOpenCategory] = useState<number | null>(null)
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("CASH")
  const [quantities, setQuantities] = useState<{ [key: number]: number }>({})

  useEffect(() => {
    fetchOrder()
    fetchCategories()
  }, [])

  const fetchOrder = async () => {
    const res = await fetch(`${API_URL}/orders/${id}`, {headers: getAuthHeaders()})
    const data = await res.json()
    setOrder(data)
  }

  const fetchCategories = async () => {
    const res = await fetch(`${API_URL}/categories/with-products`, {headers: getAuthHeaders()})
    const data = await res.json()
    setCategories(data)
  }

  const addProduct = async (productId: number) => {
    if (order?.status === "CLOSED") return

    const quantity = quantities[productId] || 1

    await fetch(`${API_URL}/orders/${id}/items`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity
      })
    })

    fetchOrder()
  }

  const registerPayment = async () => {
    if (!paymentAmount) return

    const res = await fetch(`${API_URL}/orders/${id}/payments`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        amount: Number(paymentAmount),
        method: paymentMethod
      })
    })

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    setPaymentAmount("")
    fetchOrder()
  }

  const closeOrder = async () => {
    const res = await fetch(`${API_URL}/orders/${id}/close`, {
      method: "POST",
      headers: getAuthHeaders()
    })

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    fetchOrder()
  }

  const sendToKitchen = async () => {
    const res = await fetch(`${API_URL}/orders/${id}/send-to-kitchen`, {
      method: "POST",
      headers: getAuthHeaders()
    })

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    fetchOrder()
  }

  if (!order) return <p>Cargando...</p>

  const allDelivered =
    order.items.length > 0 &&
    order.items.every(i => i.status === "DELIVERED")

  const canClose =
    order.remaining === 0 &&
    allDelivered &&
    order.status !== "CLOSED"

  const hasPendingItems =
    order.items.some(i => i.status === "PENDING")

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
            {(item.quantity * item.unit_price).toFixed(2)} —{" "}
            <strong>{item.status}</strong>
          </li>
        ))}
      </ul>

      <h3>Total: ${order.total.toFixed(2)}</h3>

      <hr />

      {/* ENVIAR A COCINA */}
      {order.status !== "CLOSED" && hasPendingItems && (
        <div style={{ marginTop: 20 }}>
          <button
            onClick={sendToKitchen}
            style={{
              padding: 10,
              backgroundColor: "orange",
              color: "white",
              borderRadius: 8
            }}
          >
            Enviar a Cocina
          </button>
        </div>
      )}

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

      {/* FORMULARIO DE PAGO */}
      {order.status !== "CLOSED" && (
        <div style={{ marginTop: 20 }}>
          <h3>Registrar Pago</h3>

          <input
            type="number"
            placeholder="Monto"
            value={paymentAmount}
            onChange={(e) => setPaymentAmount(e.target.value)}
            style={{ marginRight: 10, padding: 5 }}
          />

          <select
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            style={{ marginRight: 10, padding: 5 }}
          >
            <option value="CASH">Efectivo</option>
            <option value="CARD">Tarjeta</option>
            <option value="TRANSFER">Transferencia</option>
          </select>

          <button
            onClick={registerPayment}
            style={{
              padding: 8,
              borderRadius: 6
            }}
          >
            Agregar Pago
          </button>
        </div>
      )}

      {/* CERRAR ORDEN SOLO SI CUMPLE REGLAS */}
      {canClose && (
        <div style={{ marginTop: 20 }}>
          <p style={{ color: "green", fontWeight: "bold" }}>
            ✔ Orden pagada y entregada. Puede cerrarse.
          </p>

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

      {categories.map(category => (
        <div key={category.id} style={{ marginBottom: 15 }}>
          <div
            onClick={() =>
              setOpenCategory(
                openCategory === category.id ? null : category.id
              )
            }
            style={{
              cursor: "pointer",
              fontWeight: "bold",
              background: "#eee",
              padding: 10,
              borderRadius: 6
            }}
          >
            {category.name}
          </div>

          {openCategory === category.id && (
            <div style={{ padding: 10 }}>
              {category.products.map(p => (
                <div key={p.id} style={{ marginBottom: 8 }}>
                  <input
                    type="number"
                    min="1"
                    value={quantities[p.id] || 1}
                    onChange={(e) =>
                      setQuantities({
                        ...quantities,
                        [p.id]: Number(e.target.value)
                      })
                    }
                    style={{ width: 60, marginRight: 5 }}
                  />

                  <button
                    disabled={order.status === "CLOSED"}
                    onClick={() => addProduct(p.id)}
                    style={{
                      padding: 6,
                      borderRadius: 6
                    }}
                  >
                    {p.name} - ${p.price}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

