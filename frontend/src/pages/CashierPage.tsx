import { useEffect, useState } from "react"
import { API_URL } from "../api"

interface Order {
  order_id: number
  table_number: number
  status: string
  total: number
  total_paid: number
  remaining: number
}

export default function CashierPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("CASH")

  useEffect(() => {
    fetchActiveOrders()
  }, [])

  const fetchActiveOrders = async () => {
    const res = await fetch(`${API_URL}/orders/active`)
    const data = await res.json()
    setOrders(data)
  }

  const selectOrder = async (orderId: number) => {
    const res = await fetch(`${API_URL}/orders/${orderId}`)
    const data = await res.json()
    setSelectedOrder(data)
  }

  const registerPayment = async () => {
    if (!selectedOrder || !paymentAmount) return

    const res = await fetch(
      `${API_URL}/orders/${selectedOrder.order_id}/payments`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: Number(paymentAmount),
          method: paymentMethod
        })
      }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    setPaymentAmount("")
    selectOrder(selectedOrder.order_id)
    fetchActiveOrders()
  }

  const closeOrder = async () => {
    if (!selectedOrder) return

    const res = await fetch(
      `${API_URL}/orders/${selectedOrder.order_id}/close`,
      { method: "POST" }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    setSelectedOrder(null)
    fetchActiveOrders()
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>💰 Caja</h1>

      <h2>Órdenes Activas</h2>

      {orders.map(o => (
        <div
          key={o.order_id}
          onClick={() => selectOrder(o.order_id)}
          style={{
            padding: 10,
            marginBottom: 8,
            cursor: "pointer",
            border: "1px solid #ccc",
            borderRadius: 6
          }}
        >
          Mesa {o.table_number} — Saldo: ${o.remaining.toFixed(2)}
        </div>
      ))}

      {selectedOrder && (
        <div style={{ marginTop: 40 }}>
          <h2>Orden #{selectedOrder.order_id}</h2>

          <p>Total: ${selectedOrder.total.toFixed(2)}</p>
          <p>Total Pagado: ${selectedOrder.total_paid.toFixed(2)}</p>
          <p>
            <strong>Saldo: ${selectedOrder.remaining.toFixed(2)}</strong>
          </p>

          {selectedOrder.remaining > 0 && (
            <div style={{ marginTop: 20 }}>
              <input
                type="number"
                placeholder="Monto"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                style={{ marginRight: 10 }}
              />

              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                style={{ marginRight: 10 }}
              >
                <option value="CASH">Efectivo</option>
                <option value="CARD">Tarjeta</option>
                <option value="TRANSFER">Transferencia</option>
              </select>

              <button onClick={registerPayment}>
                Registrar Pago
              </button>
            </div>
          )}

          {selectedOrder.remaining === 0 && (
            <div style={{ marginTop: 20 }}>
              <p style={{ color: "green" }}>
                ✔ Orden saldada
              </p>

              <button
                onClick={closeOrder}
                style={{
                  backgroundColor: "black",
                  color: "white",
                  padding: 10,
                  borderRadius: 6
                }}
              >
                Cerrar Orden
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
