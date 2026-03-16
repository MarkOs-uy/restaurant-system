import { useParams, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

interface Item {
  id: number
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
  id: number
  table_id: number
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
  const { orderId, tableId } = useParams()
  const id = Number(orderId)
  const navigate = useNavigate()

  const isNewOrder = !orderId
  const [order, setOrder] = useState<Order | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [openCategory, setOpenCategory] = useState<number | null>(null)
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("CASH")
  const [quantities, setQuantities] = useState<{ [key: number]: number }>({})

  useEffect(() => {
    if (!isNewOrder) {
      fetchOrder()
    }
    fetchCategories()
  }, [orderId])

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

    const quantity = quantities[productId] || 1

    // 🟢 si la orden no existe → crearla
    if (isNewOrder) {

      const res = await fetch(
        `${API_URL}/tables/${tableId}/add-product`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            product_id: productId,
            quantity
          })
        }
      )

      const data = await res.json()

      navigate(`/orders/${data.order_id}`)

      return
    }

    // 🟢 orden normal
    if (order?.status === "CLOSED") return

    await fetch(`${API_URL}/orders/${orderId}/items`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        product_id: productId,
        quantity
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

  if (!order && orderId) return <p>Cargando...</p>
  const o = order!
  const items = o?.items ?? []
  const remaining = o?.remaining ?? 0
  const status = o?.status
  const total = o?.total ?? 0
  const total_paid = o?.total_paid ?? 0
  const payments = o?.payments ?? []

  const allDelivered =
    items.length > 0 &&
    items.every(i => i.status === "DELIVERED")

  const canClose =
    remaining === 0 &&
    allDelivered &&
    status !== "CLOSED"

  const hasPendingItems =
    items.some(i => i.status === "PENDING")

  const getStatusColor = () => {
    switch (status) {
      case "OPEN": return "green"
      case "SENT": return "orange"
      case "IN_PROGRESS": return "blue"
      case "READY": return "purple"
      case "CLOSED": return "gray"
      case "CANCELLED": return "red"
      default: return "black"
    }
  }

  const removeItem = async (itemId: number) => {
    const res = await fetch(
      `${API_URL}/orders/order-items/${itemId}`,
      {
        method: "DELETE",
        headers: getAuthHeaders()
      }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    fetchOrder()
  }

  const updateQuantity = async (itemId: number, quantity: number) => {

    const res = await fetch(
      `${API_URL}/orders/order-items/${itemId}?quantity=${quantity}`,
      {
        method: "PATCH",
        headers: getAuthHeaders()
      }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    fetchOrder()
  }

  return (
    <div style={{ padding: 40, maxWidth: 900 }}>
      <h1>{o ? `Orden #${o.id}` : `Nueva orden - Mesa ${tableId}`}</h1>
      <p>Mesa: {order?.table_number || tableId}</p>
      <p>
        Estado:{" "}
        <strong style={{ color: getStatusColor() }}>
          {status}
        </strong>
      </p>

      {/* ITEMS */}
      <h2>Items</h2>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {items.map((item) => (
          <li
            key={item.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "6px 0",
              borderBottom: "1px solid #eee"
            }}
          >
            <span style={{ flex: 1 }}>
              {item.product_name}
            </span>

            {item.status === "PENDING" && (
              <>
                <button
                  onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 6,
                    border: "1px solid #ccc",
                    background: "white",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 16,
                    lineHeight: 1,
                    padding: 0
                  }}
                >
                  −
                </button>

                <strong>{item.quantity}</strong>

                <button
                  onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 6,
                    border: "1px solid #ccc",
                    background: "white",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 16,
                    lineHeight: 1,
                    padding: 0
                  }}
                >
                  +
                </button>
              </>
            )}

            <span style={{ width: 80, textAlign: "right" }}>
              ${(item.quantity * item.unit_price).toFixed(2)}
            </span>

            <strong
              style={{
                width: 80,
                textAlign: "center",
                color: item.status === "PENDING" ? "#b58900" : "#2a9d8f"
              }}
            >
              {item.status}
            </strong>

            {item.status === "PENDING" && (
              <button
                onClick={() => removeItem(item.id)}
                style={{
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  fontSize: 16
                }}
              >
                ❌
              </button>
            )}
          </li>
        ))}
      </ul>
      <h3>Total: ${total.toFixed(2)}</h3>

      <hr />

      {/* ENVIAR A COCINA */}
      {status !== "CLOSED" && hasPendingItems && (
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

      {payments.length === 0 && <p>No hay pagos registrados</p>}

      <ul>
        {payments.map(p => (
          <li key={p.id}>
            ${Number(p.amount).toFixed(2)} — {p.method}
          </li>
        ))}
      </ul>

      <p><strong>Total pagado:</strong> ${total_paid.toFixed(2)}</p>
      <p><strong>Saldo pendiente:</strong> ${remaining.toFixed(2)}</p>

      {/* FORMULARIO DE PAGO */}
      {status !== "CLOSED" && (
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
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    marginBottom: 6
                  }}
                >

                  <button
                    onClick={() => addProduct(p.id)}
                    style={{
                      flex: 1,
                      padding: 8,
                      borderRadius: 6
                    }}
                  >
                    {p.name} - ${p.price}
                  </button>

                  <button
                    onClick={() =>
                      setQuantities({
                        ...quantities,
                        [p.id]: Math.max((quantities[p.id] || 1) - 1, 1)
                      })
                    }
                  >
                    −
                  </button>

                  <strong>{quantities[p.id] || 1}</strong>

                  <button
                    onClick={() =>
                      setQuantities({
                        ...quantities,
                        [p.id]: (quantities[p.id] || 1) + 1
                      })
                    }
                  >
                    +
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

