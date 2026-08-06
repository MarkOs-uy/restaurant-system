import { useEffect, useReducer, useRef, useState } from "react"
import { apiFetch } from "../api"
import { CashMovementType,
  OrderStatus,
  PaymentMethod,
  WSEvent,  
   } from "../types"
import type { CashRegisterDashboard, CashMovement, CashRegisterCloseSummary } from "../types"
import type { WSEventParsed } from "../ws"
import { wsService } from "../services/wsService"
import { moneyToNumber } from "../utils/money"

interface Order {
  id: number
  table_number: number
  status: string
  subtotal: number
  total: number
  total_paid: number
  remaining: number
  discount: number
  payments: Payment[]
}

interface State {
  dashboard: CashRegisterDashboard | null
  orders: Order[]
  selectedOrder: Order | null
  loading: boolean
  movementModalOpen: boolean
  movementType: "cash_in" | "cash_out" | null
}

interface Payment {
  id: number
  amount: number
  method: string
  created_at: string
}

type Action =
  | { type: "SET_DASHBOARD"; payload: CashRegisterDashboard | null }
  | { type: "SET_ORDERS"; payload: Order[] }
  | { type: "SELECT_ORDER"; payload: Order | null }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "OPEN_MOVEMENT_MODAL"; payload: "cash_in" | "cash_out" }
  | { type: "CLOSE_MOVEMENT_MODAL" }
  | { type: "UPDATE_ORDER_STATUS"; payload: { order_id: number; status: string } }
  | { type: "REMOVE_ORDER"; payload: number }
  | { type: "PAYMENT_ADDED"; payload:{order_id:number, amount:number} }
  | { type: "PAYMENT_DELETED"; payload:{order_id:number, amount:number, method: string} }
  | { type: "ADD_MOVEMENT"; payload:CashMovement }
  | { type: "DELETE_MOVEMENT"; payload:{ movement_id: number; amount: number; movement_type: CashMovementType } }

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "SET_DASHBOARD":
      return { ...state, dashboard: action.payload }
    case "SET_ORDERS":
      return { ...state, orders: action.payload }
    case "SELECT_ORDER":
      return { ...state, selectedOrder: action.payload }
    case "SET_LOADING":
      return { ...state, loading: action.payload }
    case "OPEN_MOVEMENT_MODAL":
      return { ...state, movementModalOpen: true, movementType: action.payload }
    case "CLOSE_MOVEMENT_MODAL":
      return { ...state, movementModalOpen: false, movementType: null }
    case "UPDATE_ORDER_STATUS":
      return {
        ...state,
        orders: state.orders.map(o =>
          o.id === action.payload.order_id
            ? { ...o, status: action.payload.status }
            : o
        )
      }
    case "REMOVE_ORDER":
      return {
        ...state,
        orders: state.orders.filter(o => o.id !== action.payload),
        selectedOrder:
          state.selectedOrder?.id === action.payload
            ? null
            : state.selectedOrder
      }
    case "ADD_MOVEMENT":
      if (!state.dashboard) return state
      if (state.dashboard.cash_movements.some(m => m.id === action.payload.id)) {
        return state
      }
      return {
        ...state,
        dashboard:{
          ...state.dashboard,
          expected_cash:
            action.payload.type === CashMovementType.CASH_IN
              ? state.dashboard.expected_cash + action.payload.amount
              : state.dashboard.expected_cash - action.payload.amount,
          cash_movements:[
            action.payload,
            ...state.dashboard.cash_movements
          ]
        }
      }  
    case "DELETE_MOVEMENT":
      if (!state.dashboard) return state
      return {
        ...state,
        dashboard:{
          ...state.dashboard,
          expected_cash:
            action.payload.movement_type === CashMovementType.CASH_IN
              ? state.dashboard.expected_cash - action.payload.amount
              : state.dashboard.expected_cash + action.payload.amount,
          cash_movements: state.dashboard.cash_movements.filter(
            m => m.id !== action.payload.movement_id
          )
        }
      }
    default:
      return state
  }
}


function normalizeDashboard(data: any): CashRegisterDashboard {

  return {
    ...data,
    opening_amount: moneyToNumber(data.opening_amount),
    total_sales: moneyToNumber(data.total_sales),
    average_ticket: moneyToNumber(data.average_ticket),
    expected_cash: moneyToNumber(data.expected_cash),
    by_method: Object.fromEntries(
      Object.entries(data.by_method ?? {}).map(
        ([method, amount]) => [method, moneyToNumber(amount)]
      )
    ),
    cash_movements: (data.cash_movements ?? []).map((m: any) => ({
      ...m,
      amount: moneyToNumber(m.amount)
    }))
  }
}

function normalizePayment(data: any): Payment {
  return {
    ...data,
    amount: moneyToNumber(data.amount)
  }
}

function normalizeOrder(data: any): Order {
  return {
    ...data,
    subtotal: moneyToNumber(data.subtotal),
    total: moneyToNumber(data.total),
    total_paid: moneyToNumber(data.total_paid),
    remaining: moneyToNumber(data.remaining),
    discount: moneyToNumber(data.discount),
    payments: (data.payments ?? []).map(normalizePayment)
  }
}

function normalizeCloseSummary(data: any): CashRegisterCloseSummary {
  return {
    ...data,
    total_sales: moneyToNumber(data.total_sales),
    opening_amount: moneyToNumber(data.opening_amount),
    closing_amount: moneyToNumber(data.closing_amount),
    cash_in: moneyToNumber(data.cash_in),
    cash_out: moneyToNumber(data.cash_out),
    expected_cash: moneyToNumber(data.expected_cash),
    counted_cash: moneyToNumber(data.counted_cash),
    difference: moneyToNumber(data.difference),
    by_method: Object.fromEntries(
      Object.entries(data.by_method ?? {}).map(
        ([method, amount]) => [method, moneyToNumber(amount)]
      )
    ) as Record<PaymentMethod, number>
  }
}


export default function CashierPage() {

  const [state, dispatch] = useReducer(reducer, {
    dashboard: null,
    orders: [],
    selectedOrder: null,
    loading: true,
    movementModalOpen: false,
    movementType: null
  })

  const paymentInputRef = useRef<HTMLInputElement>(null)
  const [openingAmount, setOpeningAmount] = useState("")
  const [paymentAmount, setPaymentAmount] = useState("")
  const selectedOrderRef = useRef<Order | null>(null)
  const [movementAmount, setMovementAmount] = useState("")
  const [movementReason, setMovementReason] = useState("")
  const [discount, setDiscount] = useState("")
  const [discountType, setDiscountType] = useState<"amount" | "percent">("amount")
  const [closeModalOpen, setCloseModalOpen] = useState(false)
  const [realCash, setRealCash] = useState("")
  const [differenceReason, setDifferenceReason] = useState("")
  const [processingPayment,setProcessingPayment] = useState(false)
  const [closeSummary, setCloseSummary] =
    useState<CashRegisterCloseSummary | null>(null)
  const [showCloseSummary, setShowCloseSummary] = useState(false)

  const {
    opening_amount = 0,
    total_sales = 0,
    orders_count = 0,
    average_ticket = 0,
    expected_cash = 0,
    by_method = {} as Record<PaymentMethod, number>,
    cash_movements = []
  } = state.dashboard || {}

  const orders = state.orders
  const selectedOrder = state.selectedOrder

  useEffect(() => {
    selectedOrderRef.current = selectedOrder
  }, [selectedOrder])

  const methodLabels: Record<string, string> = {
    CASH: "💵 Efectivo",
    CARD: "💳 Tarjeta",
    TRANSFER: "📲 Transferencia",
    OTHER: "🤝 Otro"
  }

  const methodColors: Record<string, string> = {
    CASH: "#2e7d32",
    CARD: "#1565c0",
    TRANSFER: "#6a1b9a",
    OTHER: "#c67213"
  }

  const paymentStatusIcon = (order: Order) => {
    if (order.remaining === 0) return "🟢"
    if (order.total_paid > 0) return "🟡"
    return "🔴"
  }


  const fetchDashboard = async () => {
    try {
      const data = await apiFetch("/cash-register/dashboard")
      const normalized = normalizeDashboard(data)
      dispatch({
        type: "SET_DASHBOARD",
        payload: normalized
      })
    } catch (err: any) {
      if (err.code === "cash_register_not_open") {
        dispatch({
          type: "SET_DASHBOARD",
          payload: null
        })
      } else {
        console.error("No se pudo actualizar el dashboard de caja", err)
      }
    }
  }

  const fetchActiveOrders = async () => {
    try {
      const data = await apiFetch("/orders/active")
      dispatch({ type: "SET_ORDERS", payload: data.map(normalizeOrder) })
    } catch {
      dispatch({ type: "SET_ORDERS", payload: [] })
    }
  }


  const dashboardTimer = useRef<any>(null)
  const ordersTimer = useRef<any>(null)


  const scheduleDashboardRefresh = () => {
    if (dashboardTimer.current) clearTimeout(dashboardTimer.current)
    dashboardTimer.current = setTimeout(() => {
      fetchDashboard()
    }, 200)
  }


  const scheduleOrdersRefresh = () => {
    if (ordersTimer.current) clearTimeout(ordersTimer.current)
    ordersTimer.current = setTimeout(() => {
      fetchActiveOrders()
    }, 200)
  }


  const selectOrder = async (orderId:number)=>{
    setPaymentAmount("")
    try {
      const data = await apiFetch(`/orders/${orderId}`)
      dispatch({
        type:"SELECT_ORDER",
        payload: normalizeOrder(data)
      })
      setPaymentAmount(moneyToNumber(data.remaining).toString())
      setDiscount("")
      setTimeout(()=>{
        paymentInputRef.current?.focus()
      },50)
    } catch(err:any){
      alert(err.message)
    }
  }

  const registerPayment = async (method: string) => {
    if (!selectedOrder) return
    if (processingPayment) return    
    setProcessingPayment(true)  
    let amount = Number(paymentAmount)
    if (Number.isNaN(amount) || amount <= 0) {
      amount = selectedOrder.remaining
    }
    if (amount <= 0) return
    amount = Math.min(amount, selectedOrder.remaining)
    try {
      await apiFetch(`/orders/${selectedOrder.id}/payments`, {
        method:"POST",
        body:{ amount, method }
      })
      setPaymentAmount("")
      await selectOrder(selectedOrder.id)
    } catch (err:any) {
      alert(err.message)
    } finally {
      setProcessingPayment(false)
    }
  }

  const setOrderDiscount = async (amount: number) => {
    if (!selectedOrder) return
    try {
      await apiFetch(
        `/orders/${selectedOrder.id}/discount?discount=${amount}`,
        { method: "PUT" }
      )
      setDiscount("")
      await selectOrder(selectedOrder.id)
      await fetchActiveOrders()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const applyDiscount = async () => {
    if (!selectedOrder || discount.trim() === "") return
    let finalDiscount = Number(discount)
    if (Number.isNaN(finalDiscount) || finalDiscount < 0) {
      alert("Descuento invalido")
      return
    }
    if (discountType === "percent") {
      finalDiscount = (selectedOrder.subtotal * finalDiscount) / 100
    }
    await setOrderDiscount(finalDiscount)
  }


  const removeDiscount = async () => {
    await setOrderDiscount(0)
  }


  const openMovementModal = (type: "cash_in" | "cash_out") => {
    setMovementAmount("")
    setMovementReason("")
    dispatch({ type: "OPEN_MOVEMENT_MODAL", payload: type })
  }


  const registrarMovimiento = async () => {
    if (!state.movementType) return

    if (!movementAmount || Number(movementAmount) <= 0) {
      alert("Monto inválido")
      return
    }
    if (!movementReason.trim()) {
      alert("Debe indicar un motivo")
      return
    }
    try {
      await apiFetch("/cash-register/movements", {
        method: "POST",
        body: {
          type: state.movementType,
          amount: Number(movementAmount),
          reason: movementReason
        }
      })
    } catch (err: any) {
      alert(err.message)
      return
    }
    await fetchDashboard()
    setMovementAmount("")
    setMovementReason("")
    dispatch({ type: "CLOSE_MOVEMENT_MODAL" })
    setTimeout(()=>{
      paymentInputRef.current?.focus()
    },50)
  }


  const closeCashRegister = async () => {
    if (!realCash) {
      alert("Ingrese efectivo contado")
      return
    }
    try {
      const summary = await apiFetch("/cash-register/close", {
        method: "POST",
        body: {
          counted_cash: Number(realCash),
          difference_reason: differenceReason
        }
      })
      setCloseModalOpen(false)
      setCloseSummary(normalizeCloseSummary(summary))
      setShowCloseSummary(true)
      dispatch({
        type: "SET_DASHBOARD",
        payload: null
      })
    } catch (err: any) {
      switch (err.code) {
        case "order_has_remaining_balance":
          alert(`Falta pagar ${err.context.remaining}`)
        break
        case "order_items_not_delivered":
          alert(`Platos pendientes: ${err.context.items.join(", ")}`)
        break
        default:
          alert(err.message)
      }
    }
  }


  useEffect(()=>{
    let fetching = false
    let pending = false

    const safeFetchOrders = async () => {
      if (fetching) {
        pending = true
        return
      }
      fetching = true
      await fetchActiveOrders()
      fetching = false
      if (pending) {
        pending = false
        safeFetchOrders()
      }
    }

    // CARGA INICIAL
    const init = async () => {
      await fetchDashboard()
      await safeFetchOrders()
      dispatch({ type: "SET_LOADING", payload: false })
    }

    init()


    wsService.connect()

    const handler = async ({ type, data }: WSEventParsed) => {
      switch (type) {

        case WSEvent.CASH_MOVEMENT_ADDED:
          dispatch({
            type: "ADD_MOVEMENT",
            payload: {
              ...data.movement,
              amount: moneyToNumber(data.movement.amount)
            }
          })
        break

        case WSEvent.CASH_MOVEMENT_DELETED:
          dispatch({
            type: "DELETE_MOVEMENT",
            payload:{
              movement_id: data.movement_id,
              amount: moneyToNumber(data.amount),
              movement_type: data.movement_type
            }
          })
        break

        case WSEvent.PAYMENT_ADDED:
        case WSEvent.PAYMENT_DELETED:
          scheduleOrdersRefresh()
          scheduleDashboardRefresh()
          if (selectedOrderRef.current?.id === data.order_id) {
            await selectOrder(data.order_id)
          }
        break

        case WSEvent.ORDER_UPDATED:
          scheduleOrdersRefresh()
          if (selectedOrderRef.current?.id === data.order_id) {
            await selectOrder(data.order_id)
          }
        break

        case "ORDER_STATUS_CHANGED":
          dispatch({
            type:"UPDATE_ORDER_STATUS",
            payload:{
              order_id:data.order_id,
              status:data.status
            }
          })
        break

        case "ORDER_CLOSED":
          dispatch({
            type:"REMOVE_ORDER",
            payload:data.order_id
          })
          scheduleOrdersRefresh()
          scheduleDashboardRefresh()
        break

        case WSEvent.CASH_REGISTER_UPDATED:
          scheduleDashboardRefresh()
        break
      }
    }

    wsService.subscribe(handler)

    return ()=>{
      wsService.unsubscribe(handler)
      if (dashboardTimer.current) clearTimeout(dashboardTimer.current)
      if (ordersTimer.current) clearTimeout(ordersTimer.current)
    }
  },[])

  useEffect(()=>{
    if(!state.movementModalOpen){
      setTimeout(()=>{
        paymentInputRef.current?.focus()
      },50)
    }
  },[state.movementModalOpen])

  useEffect(() => {
    if (selectedOrder) {
      setPaymentAmount(selectedOrder.remaining.toString())
    }
  }, [selectedOrder?.remaining])

  if (state.loading) return <div style={{ padding: 40 }}>Cargando...</div>

  if (!state.dashboard) {
    return (
      <div style={{ padding: 40 }}>
        <h1>💰 Abrir Caja</h1>
        <input
          type="number"
          placeholder="Monto inicial"
          value={openingAmount}
          ref={paymentInputRef}
          onChange={e => setOpeningAmount(e.target.value)}
        />
        <button
          onClick={async () => {
            const amount = Number(openingAmount)
            if (!openingAmount || isNaN(amount)) {
              alert("Ingrese un monto válido")
              return
            }
            if (amount < 0) {
              alert("El monto no puede ser negativo")
              return
            }
            try {
              await apiFetch("/cash-register/open", {
                method: "POST",
                body: {
                  opening_amount: amount
                }
              })
              await fetchDashboard()
            } catch (err: any) {
              alert(err.message)
            }
          }}
        >
          Abrir Caja
        </button>
      </div>
    )
  }

  if(showCloseSummary && closeSummary){
    return (
      <div
        style={{
          display:"flex",
          alignItems:"center",
          justifyContent:"center",
          height:"100vh",
          background:"#121212",
          color:"white"
        }}
      >
        <div
          style={{
            width:500,
            background:"#1e1e1e",
            padding:40,
            borderRadius:10,
            border:"1px solid #333"
          }}
        >

          <h1>📊 Cierre de Caja</h1>

          <hr style={{margin:"20px 0"}}/>

          <p>Apertura</p>
          <h3>${closeSummary.opening_amount.toFixed(2)}</h3>

          <p>Ventas Totales</p>
          <h2>${closeSummary.total_sales.toFixed(2)}</h2>

          <p>Órdenes atendidas</p>
          <b>{closeSummary.transactions_count}</b>

          <hr style={{margin:"20px 0"}}/>

          <h3>Ventas por método</h3>

          {Object.entries(closeSummary.by_method).map(([method, amount]) => (
            <p key={method}>
              {methodLabels[method as PaymentMethod]}: ${amount.toFixed(2)}
            </p>
          ))}

          <hr style={{margin:"20px 0"}}/>

          <p>Efectivo esperado</p>
          <h2 style={{color:"#00e676"}}>
            ${closeSummary.expected_cash.toFixed(2)}
          </h2>

          <p>Efectivo contado</p>
          <h2>${closeSummary.counted_cash.toFixed(2)}</h2>

          <p>Diferencia</p>
          <h2
            style={{
              color:
                closeSummary.difference === 0
                  ? "#00e676"
                  : "#ff5252"
            }}
          >
            ${closeSummary.difference.toFixed(2)}
          </h2>

          <button
            style={{
              marginTop:30,
              width:"100%",
              padding:16,
              background:"#1976d2",
              borderRadius:6,
              color:"white",
              fontSize:18
            }}
            onClick={async ()=>{
              setShowCloseSummary(false)
              setCloseSummary(null)
              setRealCash("")
              setDifferenceReason("")

              await fetchDashboard()
              await fetchActiveOrders()
            }}
          >
            Finalizar
          </button>

        </div>
      </div>
    )
  }


  // ✅ Render principal usando desestructuración con valores por defecto
  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr 420px", gap: 20, padding: 20 }}>
      {/* CASH SUMMARY */}
      <div style={{ background: "#1e1e1e", padding: 20, borderRadius: 8, border: "1px solid #333" }}>
        <h2>💰 Caja</h2>
        <p>Apertura</p>
        <h3>${Number(opening_amount).toFixed(2)}</h3>

        <p>Ventas</p>
        <h1>${Number(total_sales).toFixed(2)}</h1>

        <p>Órdenes</p>
        <b>{orders_count}</b>

        <p>Ticket promedio</p>
        <b>${Number(average_ticket).toFixed(2)}</b>

        <hr />

        <h3>Efectivo esperado</h3>
        <h1 style={{ color: "#00e676" }}>${Number(expected_cash).toFixed(2)}</h1>

        <hr />
        <h3>Ventas por método</h3>
        {Object.entries(by_method)
          .sort((a, b) => b[1] - a[1])
          .map(([method, amount]) => (
            <p key={method} style={{ color: methodColors[method] }}>
              {methodLabels[method]}: ${amount.toFixed(2)}
            </p>
          ))}

        <hr />
        <h3>Movimientos</h3>
        {cash_movements.slice(0, 5).map(m => (
          <div
            key={m.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 6
            }}
          >
            <span>
              {m.type === "cash_in" ? "➕" : "➖"} {m.reason}
            </span>

            <div style={{display:"flex", gap:8}}>
              <span>${m.amount.toFixed(2)}</span>

              <button
                onClick={async()=>{
                  if(!confirm("¿Eliminar movimiento?")) return
                  try {
                    await apiFetch(`/cash-register/movements/${m.id}`, {
                      method: "DELETE"
                    })
                    await fetchDashboard()
                  } catch (err: any) {
                    alert(err.message)
                  }
                }}
                style={{
                  background:"#444",
                  borderRadius:4,
                  padding:"2px 6px",
                  cursor:"pointer"
                }}
              >
                ✕
              </button>
            </div>
          </div>
        ))}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
          <button
            style={{ padding: 10, background: "#2e7d32", color: "white", borderRadius: 6 }}
            onClick={() => openMovementModal("cash_in")}
          >
            Ingreso
          </button>
          <button
            style={{ padding: 10, background: "#c62828", color: "white", borderRadius: 6 }}
            onClick={() => openMovementModal("cash_out")}
          >
            Retiro
          </button>
        </div>
        {state.movementModalOpen && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            <div
              style={{
                background: "#1e1e1e",
                padding: 30,
                borderRadius: 8,
                width: 400,
                border: "1px solid #333"
              }}
            >
              <h2>
                {state.movementType === "cash_in"
                  ? "➕ Ingreso de caja"
                  : "➖ Retiro de caja"}
              </h2>

              <input
                type="number"
                placeholder="Monto"
                value={movementAmount}
                onChange={e => setMovementAmount(e.target.value)}
                onKeyDown={(e)=>{
                  if(e.key === "Enter"){
                    registrarMovimiento()
                  }
                }}
                style={{
                  width: "100%",
                  padding: 10,
                  marginTop: 10,
                  borderRadius: 6
                }}
              />

              <input
                type="text"
                placeholder="Motivo"
                value={movementReason}
                onChange={e => setMovementReason(e.target.value)}
                onKeyDown={(e)=>{
                  if(e.key === "Enter"){
                    registrarMovimiento()
                  }
                }}
                style={{
                  width: "100%",
                  padding: 10,
                  marginTop: 10,
                  borderRadius: 6
                }}
              />

              <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
                <button
                  style={{
                    flex: 1,
                    padding: 12,
                    background: "#555",
                    borderRadius: 6
                  }}
                  onClick={() => dispatch({ type: "CLOSE_MOVEMENT_MODAL" })}
                >
                  Cancelar
                </button>

                <button
                  style={{
                    flex: 1,
                    padding: 12,
                    background:
                      state.movementType === CashMovementType.CASH_IN
                        ? "#2e7d32"
                        : "#c62828",
                    color: "white",
                    borderRadius: 6
                  }}
                  onClick={registrarMovimiento}
                >
                  Registrar
                </button>
              </div>
            </div>
          </div>
        )}
      <hr/>
      <button
        style={{
          marginTop:20,
          padding:12,
          width:"100%",
          background:"#d32f2f",
          color:"white",
          borderRadius:6
        }}
        onClick={()=>setCloseModalOpen(true)}
      >
        Cerrar Caja
      </button>
      {closeModalOpen && (
        <div
          style={{
            position:"fixed",
            inset:0,
            background:"rgba(0,0,0,0.6)",
            display:"flex",
            alignItems:"center",
            justifyContent:"center",
            zIndex:1000
          }}
        >
          <div
            style={{
              width:500,
              background:"#1e1e1e",
              borderRadius:10,
              padding:30,
              border:"1px solid #333"
            }}
          >

            <h2>🔒 Cierre de Caja</h2>

            <hr style={{margin:"15px 0"}}/>

            <p>Apertura</p>
            <h3>${Number(opening_amount).toFixed(2)}</h3>

            <p>Ventas totales</p>
            <h3>${total_sales.toFixed(2)}</h3>

            <p>Órdenes atendidas</p>
            <b>{orders_count}</b>

            <hr style={{margin:"15px 0"}}/>

            <h3>Ventas por método</h3>

            {Object.entries(by_method).map(([method,amount])=>(
              <p key={method} style={{color:methodColors[method]}}>
                {methodLabels[method]}: ${amount.toFixed(2)}
              </p>
            ))}

            <hr style={{margin:"15px 0"}}/>

            <p>Efectivo esperado</p>
            <h2 style={{color:"#00e676"}}>
              ${expected_cash.toFixed(2)}
            </h2>

            <p style={{marginTop:10}}>Efectivo contado</p>

            <input
              type="number"
              value={realCash}
              onChange={e=>setRealCash(e.target.value)}
              placeholder="Ingrese efectivo real"
              style={{
                width:"100%",
                padding:12,
                borderRadius:6,
                marginTop:6,
                fontSize:18
              }}
            />

            {realCash && (
              <>
                <p style={{marginTop:10}}>Diferencia</p>
                <h2
                  style={{
                    color:
                      Number(realCash) - expected_cash === 0
                        ? "#00e676"
                        : "#ff5252"
                  }}
                >
                  ${(Number(realCash) - expected_cash).toFixed(2)}
                </h2>
              </>
            )}

            {realCash && Number(realCash) !== expected_cash && (
              <textarea
                placeholder="Motivo de diferencia"
                value={differenceReason}
                onChange={e=>setDifferenceReason(e.target.value)}
                style={{
                  width:"100%",
                  marginTop:10,
                  padding:10,
                  borderRadius:6
                }}
              />
            )}

            <div style={{display:"flex", gap:10, marginTop:20}}>
              <button
                style={{
                  flex:1,
                  padding:14,
                  background:"#555",
                  borderRadius:6
                }}
                onClick={()=>setCloseModalOpen(false)}
              >
                Cancelar
              </button>

              <button
                style={{
                  flex:1,
                  padding:14,
                  background:"#d32f2f",
                  color:"white",
                  borderRadius:6
                }}
                onClick={closeCashRegister}
              >
                Confirmar Cierre
              </button>
            </div>

          </div>
        </div>
      )}


      </div>

      {/* ORDENES ACTIVAS */}
      <div style={{ background: "#1e1e1e", padding: 20, borderRadius: 8, border: "1px solid #333", overflowY: "auto", maxHeight: "80vh" }}>
        <h2>Órdenes Activas</h2>
        {orders
          .filter(o => o.status !== OrderStatus.CLOSED && o.status !== OrderStatus.CANCELLED)
          .sort((a, b) => b.remaining - a.remaining)
          .map(o => {
            const selected = selectedOrder?.id === o.id
            return (
              <div
                key={o.id}
                onClick={() => selectOrder(o.id)}
                style={{
                  padding: 14,
                  marginBottom: 10,
                  border: selected ? "2px solid #1976d2" : "1px solid #333",
                  borderRadius: 6,
                  cursor: "pointer",
                  background: selected ? "#263238" : "#111"
                }}
              >
                {paymentStatusIcon(o)} Mesa {o.table_number}
                <div style={{ fontSize: 13, opacity: 0.7 }}>Orden #{o.id}</div>
                <div style={{ fontSize: 18, fontWeight: "bold", marginTop: 6 }}>
                  Saldo ${o.remaining.toFixed(2)}
                </div>
              </div>
            )
          })}
      </div>

      {/* PANEL DE PAGO */}
      <div style={{ background: "#1e1e1e", padding: 20, borderRadius: 8, border: "1px solid #333" }}>
        {selectedOrder ? (
          <>
            <h2>Mesa {selectedOrder.table_number}</h2>
            <p>Subtotal ${selectedOrder.subtotal.toFixed(2)}</p>
            {selectedOrder.discount > 0 && (
              <p style={{ color: "#ff8a80" }}>
                Descuento -${selectedOrder.discount.toFixed(2)}
              </p>
            )}
            <p>Total ${selectedOrder.total.toFixed(2)}</p>
            <p>Pagado ${selectedOrder.total_paid.toFixed(2)}</p>
            <h1 style={{ color: "#ff4d4d", fontSize: 34 }}>Saldo ${selectedOrder.remaining.toFixed(2)}</h1>

            <hr style={{marginTop:20}}/>

            <h3>Descuento</h3>
            <div style={{ display: "grid", gridTemplateColumns: "120px 1fr", gap: 10 }}>
              <select
                value={discountType}
                onChange={(e) => setDiscountType(e.target.value as "amount" | "percent")}
                style={{ padding: 10, borderRadius: 6 }}
              >
                <option value="amount">Monto</option>
                <option value="percent">%</option>
              </select>

              <input
                type="number"
                step="0.01"
                placeholder="Descuento"
                value={discount}
                onChange={(e) => setDiscount(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    applyDiscount()
                  }
                }}
                style={{ padding: 10, borderRadius: 6 }}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: selectedOrder.discount > 0 ? "1fr 1fr" : "1fr", gap: 10, marginTop: 10 }}>
              <button
                disabled={selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED}
                onClick={applyDiscount}
                style={{
                  padding: 14,
                  fontSize: 16,
                  background: "#455a64",
                  color: "white",
                  borderRadius: 6,
                  opacity:
                    selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED
                      ? 0.4
                      : 1
                }}
              >
                Aplicar Descuento
              </button>

              {selectedOrder.discount > 0 && (
                <button
                  disabled={selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED}
                  onClick={removeDiscount}
                  style={{
                    padding: 14,
                    fontSize: 16,
                    background: "#6d4c41",
                    color: "white",
                    borderRadius: 6,
                    opacity:
                      selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED
                        ? 0.4
                        : 1
                  }}
                >
                  Quitar Descuento
                </button>
              )}
            </div>

            <hr style={{marginTop:20}}/>

            <h3>Pagos</h3>

            {selectedOrder.payments?.length === 0 && (
              <p style={{opacity:0.6}}>Sin pagos</p>
            )}

            {selectedOrder.payments?.map(p => (
              <div
                key={p.id}
                style={{
                  display:"flex",
                  justifyContent:"space-between",
                  alignItems:"center",
                  marginBottom:8,
                  padding:"6px 8px",
                  background:"#111",
                  borderRadius:6
                }}
              >
                <span>
                  {methodLabels[p.method]} ${p.amount.toFixed(2)}
                </span>
                {selectedOrder.status !== OrderStatus.CLOSED && (
                  <button
                    onClick={async()=>{
                      if(!confirm("¿Cancelar pago?")) return
                      try {
                        await apiFetch(`/orders/payments/${p.id}`, {
                          method: "DELETE"
                        })
                      } catch (err: any) {
                        alert(err.message)
                      }

                    }}
                    style={{
                      background:"#c62828",
                      borderRadius:4,
                      padding:"2px 8px",
                      color:"white",
                      cursor:"pointer"
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}

            <p style={{marginTop:10,opacity:0.7}}>
              Total pagos: ${selectedOrder.total_paid.toFixed(2)}
            </p>

            <div style={{ marginTop: 20, background: "#000", color: "#00ff9d", fontSize: 32, padding: 12, borderRadius: 6, textAlign: "right", fontFamily: "monospace" }}>
              ${paymentAmount || "0.00"}
            </div>

            <input
              ref={paymentInputRef}
              type="number"
              step="0.01"
              value={paymentAmount}
              onChange={e => setPaymentAmount(e.target.value)}
              style={{ width: "100%", marginTop: 10, padding: 10, fontSize: 18, borderRadius: 6 }}
            />

            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 20 }}>
              {Object.entries(methodLabels).map(([value, label]) => (
                <button
                  key={value}
                  disabled={processingPayment || selectedOrder.remaining <= 0}
                  onClick={() => registerPayment(value)}
                  style={{
                    padding: 16,
                    fontSize: 18,
                    borderRadius: 6,
                    background: methodColors[value],
                    color: "white",
                    opacity: selectedOrder.remaining <= 0 ? 0.4 : 1,
                    cursor: selectedOrder.remaining <= 0 ? "not-allowed" : "pointer"
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            <div style={{ marginTop: 20 }}>
              <button
                disabled={processingPayment || selectedOrder.remaining <= 0}
                onClick={() => registerPayment(PaymentMethod.CASH)}
                style={{
                  width: "100%",
                  padding: 16,
                  fontSize: 18,
                  background: "#2e7d32",
                  color: "white",
                  borderRadius: 6,
                  opacity: selectedOrder.remaining <= 0 ? 0.4 : 1,
                  cursor: selectedOrder.remaining <= 0 ? "not-allowed" : "pointer"
                }}
              >
                Pagar Total - (Efectivo)
              </button>
            </div>

            {selectedOrder.remaining === 0 &&
              selectedOrder.status !== OrderStatus.CLOSED &&
              selectedOrder.status !== OrderStatus.CANCELLED && (
                <button
                  onClick={async () => {
                    try {
                      await apiFetch(`/orders/${selectedOrder.id}/close`, {
                        method: "POST"
                      })
                    } catch (err: any) {
                      alert(err.message)
                    }
                  }}
                  style={{ marginTop: 20, width: "100%", padding: 14, background: "#1976d2", color: "white", borderRadius: 6 }}
                >
                  Cerrar Orden
                </button>
            )}
          </>
        ) : (
          <div>Selecciona una orden</div>
        )}
      </div>
    </div>
  )
}
