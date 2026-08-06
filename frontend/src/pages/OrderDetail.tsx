import { useParams, useNavigate } from "react-router-dom"
import { useEffect, useState, useRef } from "react"
import { apiFetch } from "../api"
import { wsService } from "../services/wsService"
import type { WSEventParsed } from "../ws"
import { moneyToNumber } from "../utils/money"

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
  subtotal: number
  payments: Payment[]
  total: number
  total_paid: number
  remaining: number
  discount: number
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

function normalizeOrder(data: any): Order {
  return {
    ...data,
    items: (data.items ?? []).map((item: any) => ({
      ...item,
      unit_price: moneyToNumber(item.unit_price)
    })),
    payments: (data.payments ?? []).map((payment: any) => ({
      ...payment,
      amount: moneyToNumber(payment.amount)
    })),
    subtotal: moneyToNumber(data.subtotal),
    total: moneyToNumber(data.total),
    total_paid: moneyToNumber(data.total_paid),
    remaining: moneyToNumber(data.remaining),
    discount: moneyToNumber(data.discount)
  }
}

export default function OrderDetail() {

  const { orderId, tableId } = useParams()
  const id = orderId ? Number(orderId) : null

  const navigate = useNavigate()

  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)

  const [categories, setCategories] = useState<Category[]>([])
  const [openCategory, setOpenCategory] = useState<number | null>(null)

  const [paymentAmount, setPaymentAmount] = useState("")
  const [quantities, setQuantities] = useState<{ [key: number]: number }>({})
  const [discount, setDiscount] = useState("")
  const [discountType, setDiscountType] = useState<"amount" | "percent">("amount")
  const updating = useRef(false)

  useEffect(() => {
    fetchCategories()
    if (id) {
      console.log(`${id}`)
      fetchOrder()
    } else {
      setLoading(false)
    }
  }, [orderId])


  useEffect(() => {
    if (!id) return
    const handler = ({ type, data }: WSEventParsed) => {
      const relevantEvents = [
        "ORDER_UPDATED",
        "ORDER_STATUS_CHANGED",
        "ITEM_STATUS_CHANGED",
        "PAYMENT_ADDED",
        "PAYMENT_DELETED"
      ]
      if (
        relevantEvents.includes(type) &&
        data.order_id === id
      ) {
        fetchOrder()
      }
    }
    wsService.subscribe(handler)
    return () => {
      wsService.unsubscribe(handler)
    }
  }, [id])
  
  useEffect(() => {
    if (!order) return
    setPaymentAmount(order.remaining.toFixed(2))
  }, [order?.remaining])


  const fetchOrder = async () => {
    setLoading(true)
    try {
      const data = await apiFetch(`/orders/${id}`)
      setOrder(normalizeOrder(data))
    } finally {
      setLoading(false)
    }
  }


  const fetchCategories = async () => {
    const data = await apiFetch(`/categories/with-products`)
    setCategories(data)
  }


  const addProduct = async (productId: number) => {
    const quantity = quantities[productId] || 1
    if (order?.status === "CLOSED") return
    if (!orderId) {
      const data = await apiFetch(
        `/tables/${tableId}/add-product`,
        {
          method: "POST",
          body: {
            product_id: productId,
            quantity
          }
        }
      )
      navigate(`/orders/${data.order_id}`)
      return
    }
    await apiFetch(`/orders/${orderId}/items`, {
      method: "POST",
      body: {
        product_id: productId,
        quantity
      }
    })
    await fetchOrder()
  }


  const removeItem = async (orderId: number, itemId: number) => {
    await apiFetch(`/orders/${orderId}/items/${itemId}`, {
      method: "DELETE"
    })
    await fetchOrder()
  }


  const updateQuantity = async (itemId: number, quantity: number) => {
    if (updating.current) return
    updating.current = true
    try {
      await apiFetch(`/orders/order-items/${itemId}?quantity=${quantity}`, {
        method: "PATCH"
      })
      await fetchOrder()
    } finally {
      updating.current = false
    }
  }


  const markDelivered = async (itemId: number) => {
    await apiFetch(
      `/order-items/${itemId}/status`,
      {
        method: "PATCH",
        body: { status: "DELIVERED" }
      }
    )
    await fetchOrder()
  }


  const registerPayment = async (method: string) => {
    if (!id) return
    const amount = Number(paymentAmount)
    if (!amount || amount <= 0) {
      alert("El pago debe ser mayor a 0")
      return
    }
    await apiFetch(`/orders/${id}/payments`, {
      method: "POST",
      body: {
        amount,
        method
      }
    })
    await fetchOrder()
  }


  const cancelPayment = async (paymentId: number) => {
    await apiFetch(
      `/orders/payments/${paymentId}`,
      {
        method: "DELETE",
      }
    )
    await fetchOrder()
  }


  const closeOrder = async () => {
    if (!id) return
    await apiFetch(`/orders/${id}/close`, {
      method: "POST",
    })
  }


  const sendToKitchen = async () => {
    if (!id) return
    await apiFetch(`/orders/${id}/send-to-kitchen`, {
      method: "POST",
    })
    await fetchOrder()
  }


  if (loading) return <p>Cargando...</p>

  const items = order?.items ?? []
  const remaining = order?.remaining ?? 0
  const status = order?.status
  const total = order?.total ?? 0
  const subtotal = order?.subtotal ?? 0
  const total_paid = order?.total_paid ?? 0
  const payments = order?.payments ?? []
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

  const setOrderDiscount = async (amount: number) => {
    if (!order) return
    await apiFetch(
      `/orders/${order.id}/discount?discount=${amount}`,
      {
        method: "PUT",
      }
    )
    setDiscount("")
    await fetchOrder()
  }


  const applyDiscount = async () => {
    if (!order || discount.trim() === "") return
    let finalDiscount = Number(discount)
    if (Number.isNaN(finalDiscount) || finalDiscount < 0) {
      alert("Descuento inválido")
      return
    }
    if (discountType === "percent") {
      finalDiscount = (order.subtotal * finalDiscount) / 100
    }
    await setOrderDiscount(finalDiscount)
  }


  const removeDiscount = async () => {
    await setOrderDiscount(0)
  }


  return (

    <div
      style={{
        padding: 40,
        display: "grid",
        gridTemplateColumns: "1fr 400px",
        gap: 40
      }}
    >
      <div>
        <h1>{order ? `Orden #${order.id}` : `Nueva orden - Mesa ${tableId}`}</h1>

        <p>Mesa: {order?.table_number || tableId}</p>

        <p>
          Estado:{" "}
          <strong style={{ color: getStatusColor() }}>
            {status}
          </strong>
        </p>

        {order?.status === "DRAFT" && (
          <div style={{
            background: "#333",
            padding: 10,
            borderRadius: 8,
            marginBottom: 10
          }}>
            🧾 Agrega productos para iniciar la orden
          </div>
        )}

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
                  <button className="btn btn-icon"
                    onClick={() => updateQuantity(item.id, Math.max(0, item.quantity - 1))}
                  >
                    −
                  </button>

                  <strong>{item.quantity}</strong>

                  <button className="btn btn-icon"
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
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
                  width: 100,
                  textAlign: "center",
                  fontWeight: 600,
                  color:
                    item.status === "PENDING"
                      ? "#b58900"
                      : item.status === "READY"
                      ? "#268bd2"
                      : item.status === "DELIVERED"
                      ? "#2a9d8f"
                      : "#333",
                  textDecoration:
                    item.status === "DELIVERED"
                      ? "line-through"
                      : "none"
                }}
              >
                {item.status}
              </strong>
              {item.status === "PENDING" && (
                <button
                  onClick={() => removeItem(order!.id, item.id)}
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
              {item.status === "READY" && (
                <button
                  className="btn btn-primary"
                  onClick={() => markDelivered(item.id)}
                >
                  Entregar
                </button>
              )}
            </li>
          ))}
        </ul>
        
        <div style={{
          background: "rgba(255, 255, 255, 0.03)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-primary)",
          padding: "20px",
          borderRadius: "var(--radius-md)",
          marginTop: "16px",
          boxShadow: "var(--shadow-glass)"
        }}>
          <p style={{ marginBottom: "8px", fontSize: "15px", color: "var(--color-text-secondary)" }}>
            Subtotal: ${subtotal.toFixed(2)}
          </p>

          <p style={{ color: (order?.discount ?? 0) > 0 ? "#ef4444" : "var(--color-text-secondary)", marginBottom: "12px", fontSize: "15px" }}>
            Descuento: {(order?.discount ?? 0) > 0 ? "-" : ""}${(order?.discount ?? 0).toFixed(2)}
          </p>

          <h3 style={{ fontSize: "22px", fontWeight: "700", borderTop: "1px solid var(--color-border)", paddingTop: "12px", margin: 0, color: "var(--color-primary)" }}>
            Total: ${total.toFixed(2)}
          </h3>
        </div>

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

        <hr />

        {order?.status !== "DRAFT" && (
          <>
            <h2>Descuento</h2>

            <select
              value={discountType}
              onChange={(e) => setDiscountType(e.target.value as "amount" | "percent")}
              style={{ marginRight: 10, padding: 5 }}
            >
              <option value="amount">Monto</option>
              <option value="percent">%</option>
            </select>

            <input
              type="text"
              inputMode="decimal"
              placeholder="Monto descuento"
              value={discount}
              onChange={(e) => setDiscount(e.target.value)}
              style={{ marginRight: 10, padding: 5 }}
            />

            <button className="btn btn-primary"
              onClick={applyDiscount}
              style={{ padding: 8, borderRadius: 6 }}
            >
              Aplicar Descuento
            </button>

            {(order?.discount ?? 0) > 0 && (
              <button
                className="btn btn-primary"
                onClick={removeDiscount}
                style={{ padding: 8, borderRadius: 6, marginLeft: 10 }}
              >
                Quitar Descuento
              </button>
            )}
          </>
        )}

        {/* PAGOS */}
        <h2>Pagos</h2>

        {payments.length === 0 && <p>No hay pagos registrados</p>}

        <ul style={{ listStyle: "none", padding: 0 }}>
          {payments.map(p => (
            <li
              key={p.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "6px 0",
                borderBottom: "1px solid #eee"
              }}
            >
              <span>
                ${Number(p.amount).toFixed(2)} — {p.method}
              </span>

              {status !== "CLOSED" && (
                <button
                  onClick={() => cancelPayment(p.id)}
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

        <p><strong>Total pagado:</strong> ${total_paid.toFixed(2)}</p>
        <p><strong>Saldo pendiente:</strong> ${remaining.toFixed(2)}</p>


        {/* FORMULARIO DE PAGO */}
        {status !== "CLOSED" && (
          <div style={{ marginTop: 20 }}>
            <h3>Registrar Pago</h3>

            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Monto"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(e.target.value)}
              style={{ marginRight: 10, padding: 5 }}
            />

            <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
              <button
                className="btn btn-payment-cash"
                onClick={() => registerPayment("CASH")}
              >
              💵 Efectivo
              </button>

              <button
                className="btn btn-payment-card"
                onClick={() => registerPayment("CARD")}
              >
              💳 Tarjeta
              </button>

              <button
                className="btn btn-payment-transfer"
                onClick={() => registerPayment("TRANSFER")}
              >
              🏦 Transferencia
              </button>

              <button
                className="btn btn-payment-other"
                onClick={() => registerPayment("OTHER")}
              >
              🤝 Otro
              </button>
            </div>
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
      </div>
      <div>
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
                color: "#111",
                padding: 10,
                borderRadius: 6
              }}
            >
              {category.name}
            </div>

            {openCategory === category.id && (
              <div style={{ padding: 10 }}>
                {category.products.map(p => (
                  <div key={p.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      marginBottom: 6
                    }}
                  >

                    <button className="btn btn-product"
                      onClick={() => addProduct(p.id)}
                    >
                      {p.name} - ${p.price}
                    </button>

                    <button className="btn btn-primary"
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

                    <button className="btn btn-primary"
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
    </div>

  )

}
