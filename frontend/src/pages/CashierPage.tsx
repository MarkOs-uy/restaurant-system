import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

interface CashRegister {
  cash_register_id: number
  opened_at: string
  total_sales: number
  orders_count: number
  average_ticket: number
  by_method: Record<string, number>
}

interface Order {
  id: number
  table_number: number
  status: string
  total: number
  total_paid: number
  remaining: number
}

export default function CashierPage() {
  const [cashRegister, setCashRegister] = useState<CashRegister | null>(null)
  const [openingAmount, setOpeningAmount] = useState("")
  const [orders, setOrders] = useState<Order[]>([])
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("CASH")

  useEffect(() => {
    checkCashRegister()
  }, [])

  const checkCashRegister = async () => {
    const res = await fetch(`${API_URL}/cash-register/current`, {
      headers: getAuthHeaders()
    })

    if (res.ok) {
      const data = await res.json()
      setCashRegister(data)
      fetchActiveOrders()
    } else {
      setCashRegister(null)
    }
  }

  const openCashRegister = async () => {
    const res = await fetch(
      `${API_URL}/cash-register/open`,
      {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          opening_amount: Number(openingAmount)
        })
      }
    )

    if (!res.ok) {
      const error = await res.json()
      console.log(error)
      alert("Error abriendo caja")
      return
    }

    checkCashRegister()
  }

  const closeCashRegister = async () => {
    const res = await fetch(`${API_URL}/cash-register/close`, {
      method: "POST",
      headers: getAuthHeaders()
    })

    if (!res.ok) {
      alert("Error cerrando caja")
      return
    }

    setCashRegister(null)
  }

  const fetchActiveOrders = async () => {
    const res = await fetch(`${API_URL}/orders/active`, {
      headers: getAuthHeaders()
    })
    const data = await res.json()
    setOrders(data)
  }

  const selectOrder = async (orderId: number) => {
    const res = await fetch(`${API_URL}/orders/${orderId}`, {
      headers: getAuthHeaders()
    })
    const data = await res.json()
    setSelectedOrder(data)
  }

  const registerPayment = async () => {
    if (!selectedOrder || !paymentAmount) return

    const res = await fetch(
      `${API_URL}/orders/${selectedOrder.id}/payments`,
      {
        method: "POST",
        headers: getAuthHeaders(),
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
    selectOrder(selectedOrder.id)
    fetchActiveOrders()
    checkCashRegister()
  }

  const closeOrder = async () => {
    if (!selectedOrder) return

    const res = await fetch(
      `${API_URL}/orders/${selectedOrder.id}/close`,
      {
        method: "POST",
        headers: getAuthHeaders()
      }
    )

    if (!res.ok) {
      const error = await res.json()
      alert(error.detail)
      return
    }

    setSelectedOrder(null)
    fetchActiveOrders()
  }

  /* =========================
     SI NO HAY CAJA ABIERTA
  ========================== */
  
  if (!cashRegister) {
    return (
      <div style={{ padding: 40 }}>
        <h1>💰 Abrir Caja</h1>

        <input
          type="number"
          placeholder="Monto inicial"
          value={openingAmount}
          onChange={e => setOpeningAmount(e.target.value)}
        />

        <button onClick={openCashRegister}>
          Abrir Caja
        </button>
      </div>
    )
  }

  /* =========================
     CAJA ABIERTA
  ========================== */
  return (
    <div style={{ padding: 40 }}>
      <h1>💰 Caja Abierta</h1>

      <p>Total vendido: $ {Number(cashRegister.total_sales).toFixed(2)}</p>
      <p>Órdenes cobradas: {cashRegister.orders_count}</p>
      <p>Ticket promedio: $ {Number(cashRegister.average_ticket).toFixed(2)}</p>

      <button
        onClick={closeCashRegister}
        style={{ marginBottom: 20 }}
      >
        Cerrar Caja
      </button>

      <h2>Órdenes Activas</h2>

      {orders.map(o => (
        <div
          key={o.id}
          onClick={() => selectOrder(o.id)}
          style={{
            padding: 10,
            marginBottom: 8,
            cursor: "pointer",
            border: "1px solid #ccc"
          }}
        >
          Mesa {o.table_number} — Saldo: ${o.remaining.toFixed(2)}
        </div>
      ))}

      {selectedOrder && (
        <div style={{ marginTop: 40 }}>
          <h2>Orden #{selectedOrder.id}</h2>

          <p>Total: ${selectedOrder.total.toFixed(2)}</p>
          <p>Total Pagado: ${selectedOrder.total_paid.toFixed(2)}</p>
          <p><strong>Saldo: ${selectedOrder.remaining.toFixed(2)}</strong></p>

          {selectedOrder.remaining > 0 && (
            <div>
              <input
                type="number"
                value={paymentAmount}
                onChange={e => setPaymentAmount(e.target.value)}
              />

              <select
                value={paymentMethod}
                onChange={e => setPaymentMethod(e.target.value)}
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
            <button onClick={closeOrder}>
              Cerrar Orden
            </button>
          )}
        </div>
      )}
    </div>
  )
}
