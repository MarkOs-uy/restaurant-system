import { useEffect, useReducer, useRef, useState } from "react"
import { apiFetch } from "../api"

import { isApiError } from "../types/apiError"
import { ErrorCode } from "../types/domainErrors"
import { showToast } from "../utils/showToast"

import { CashMovementType,
  OrderStatus,
  PaymentMethod,
  WSEvent,  
   } from "../types"

import type { 
  CashRegisterDashboard, 
  CashMovement, 
  CashRegisterCloseSummary, 
  RawCashRegisterDashboard, 
  RawCashRegisterCloseSummary 
} from "../types/cashRegister"

import type { 
  OrderPayment, 
  CashierOrder, 
  RawOrderPayment, 
  RawCashierOrder 
} from "../types/order"

import type { WSEventParsed } from "../ws"
import { wsService } from "../services/wsService"
import { moneyToNumber } from "../utils/money"


interface State {
  dashboard: CashRegisterDashboard | null
  orders: CashierOrder[]
  selectedOrder: CashierOrder | null
  loading: boolean
  movementModalOpen: boolean
  movementType: "cash_in" | "cash_out" | null
}

type Action =
  | { type: "SET_DASHBOARD"; payload: CashRegisterDashboard | null }
  | { type: "SET_ORDERS"; payload: CashierOrder[] }
  | { type: "SELECT_ORDER"; payload: CashierOrder | null }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "OPEN_MOVEMENT_MODAL"; payload: CashMovementType }
  | { type: "CLOSE_MOVEMENT_MODAL" }
  | { type: "UPDATE_ORDER_STATUS"; payload: { order_id: number; status: OrderStatus } }
  | { type: "REMOVE_ORDER"; payload: number }
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
        orders: state.orders.map(order =>
          order.id === action.payload.order_id
            ? {
                ...order,
                status: action.payload.status
              }
            : order
        ),
        selectedOrder:
          state.selectedOrder?.id ===
          action.payload.order_id
            ? {
                ...state.selectedOrder,
                status: action.payload.status
              }
            : state.selectedOrder
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


function isObject(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null
  )
}

function hasOrderId(
  value: unknown
): value is { order_id: number } {
  return (
    isObject(value) &&
    typeof value.order_id === "number"
  )
}

function isOrderStatus(
  value: unknown
): value is OrderStatus {
  return (
    typeof value === "string" &&
    Object.values(OrderStatus).some(
      status => status === value
    )
  )
}

function isOrderStatusChangedPayload(
  value: unknown
): value is {
  order_id: number
  status: OrderStatus
} {
  return (
    isObject(value) &&
    typeof value.order_id === "number" &&
    isOrderStatus(value.status)
  )
}


/**
 * Normaliza los valores monetarios del dashboard de caja
 * recibidos desde la API.
 */
export function normalizeDashboard( data: RawCashRegisterDashboard): CashRegisterDashboard {
  return {
    ...data,
    opening_amount: moneyToNumber(data.opening_amount),
    total_sales: moneyToNumber(data.total_sales),
    average_ticket: moneyToNumber(data.average_ticket),
    expected_cash: moneyToNumber(data.expected_cash),
    by_method: Object.fromEntries(
      Object.entries(
        data.by_method ?? {}
      ).map(
        ([method, amount]) => [
          method,
          moneyToNumber(amount)
        ]
      )
    ) as Record<PaymentMethod, number>,
    cash_movements:
      (data.cash_movements ?? []).map(
        movement => ({
          ...movement,
          amount:
            moneyToNumber(
              movement.amount
            )
        })
      )
  }
}


function normalizePayment( data: RawOrderPayment): OrderPayment {
  return {...data, amount: moneyToNumber(data.amount)}
}


function normalizeOrder( data: RawCashierOrder): CashierOrder {
  return {
    ...data,
    subtotal:
      moneyToNumber(data.subtotal),
    total:
      moneyToNumber(data.total),
    total_paid:
      moneyToNumber(data.total_paid),
    remaining:
      moneyToNumber(data.remaining),
    discount:
      moneyToNumber(data.discount),
    payments:
      (data.payments ?? [])
        .map(normalizePayment)
  }
}

/**
 * Normaliza los valores monetarios del resumen
 * devuelto al cerrar una caja.
 */
function normalizeCloseSummary(data: RawCashRegisterCloseSummary): CashRegisterCloseSummary {
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

function paymentMethodClass(
  method: PaymentMethod
): string {
  switch (method) {
    case PaymentMethod.CASH:
      return "btn-payment-cash"

    case PaymentMethod.CARD:
      return "btn-payment-card"

    case PaymentMethod.TRANSFER:
      return "btn-payment-transfer"

    case PaymentMethod.OTHER:
      return "btn-payment-other"

    default:
      return ""
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
  const selectedOrderRef = useRef<CashierOrder | null>(null)
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

  const methodLabels:
    Record<PaymentMethod, string> = {
      [PaymentMethod.CASH]: "💵 Efectivo",
      [PaymentMethod.CARD]: "💳 Tarjeta",
      [PaymentMethod.TRANSFER]: "📲 Transferencia",
      [PaymentMethod.OTHER]: "🤝 Otro"
    }

  const methodColors:
    Record<PaymentMethod, string> = {
      [PaymentMethod.CASH]: "#2e7d32",
      [PaymentMethod.CARD]: "#1565c0",
      [PaymentMethod.TRANSFER]: "#6a1b9a",
      [PaymentMethod.OTHER]: "#c67213"
    }

  const paymentStatusIcon = (order: CashierOrder) => {
    if (order.remaining === 0) return "🟢"
    if (order.total_paid > 0) return "🟡"
    return "🔴"
  }

  const fetchDashboard = async () => {
    try {
      const data =
        await apiFetch<RawCashRegisterDashboard>(
          "/cash-register/dashboard",
          {
            suppressErrorToast: true
          }
        )

      dispatch({
        type: "SET_DASHBOARD",
        payload: normalizeDashboard(data)
      })

    } catch (error: unknown) {
      if (
        isApiError(error) &&
        error.code ===
          ErrorCode.CASH_REGISTER_NOT_OPEN
      ) {
        dispatch({
          type: "SET_DASHBOARD",
          payload: null
        })

        return
      }

      showToast(
        error instanceof Error
          ? error.message
          : "No se pudo cargar la caja"
      )
    }
  }

  const fetchActiveOrders = async () => {
    try {
      const data = await apiFetch<RawCashierOrder[]>( "/orders/active")
      dispatch({ type: "SET_ORDERS", payload: data.map(normalizeOrder) })
    } catch {
      dispatch({ type: "SET_ORDERS", payload: [] })
    }
  }

  const dashboardTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const ordersTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

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
      const data = await apiFetch<RawCashierOrder>( `/orders/${orderId}`)
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

    }
  }

  /**
   * Registrar un pago
   */
  const registerPayment = async (method: PaymentMethod, amountOverride?: number) => {
    if (!selectedOrder) return
    if (processingPayment) return

    let amount = amountOverride ?? Number(paymentAmount)

    if ( !Number.isFinite(amount) || amount <= 0) {
      amount = selectedOrder.remaining
    }

    if (amount <= 0) { return}

    amount = Math.min( amount, selectedOrder.remaining)

    setProcessingPayment(true)

    try {
      await apiFetch(`/orders/${selectedOrder.id}/payments`,
        {
          method: "POST",
          body: {
            amount,
            method
          }
        }
      )
      setPaymentAmount("")
      await selectOrder(selectedOrder.id)
    } catch {
      // apiFetch ya mostró el error.
    } finally {
      setProcessingPayment(false)
    }
  }

  /**
   * Realiza un descuento en la orden seleccionada
   */
  const setOrderDiscount = async (amount: number) => {
    if (!selectedOrder) return
    try {
      await apiFetch(`/orders/${selectedOrder.id}/discount?discount=${amount}`, { method: "PUT" })
      setDiscount("")
      await selectOrder(selectedOrder.id)
      await fetchActiveOrders()
    } catch {
      // apiFetch ya mostró el error.
    }
  }

  /**
   * Aplica un descuento en la orden seleccionada
   */
  const applyDiscount = async () => {
    if (!selectedOrder || discount.trim() === "") return
    let finalDiscount = Number(discount)
    if (Number.isNaN(finalDiscount) || finalDiscount < 0) {
      showToast("Descuento invalido")
      return
    }
    if (discountType === "percent") {
      finalDiscount = (selectedOrder.subtotal * finalDiscount) / 100
    }
    await setOrderDiscount(finalDiscount)
  }

  /**
   * Elimina un descuento en la orden seleccionada
   */
  const removeDiscount = async () => {await setOrderDiscount(0)}

  /**
   * Abre el modal para agregar un movimiento de caja
   */
  const openMovementModal = ( type: CashMovementType ) => {
    setMovementAmount("")
    setMovementReason("")
    dispatch({ type: "OPEN_MOVEMENT_MODAL", payload: type })
  }

  /**
   * Registra un movimiento de caja
   */
  const registrarMovimiento = async () => {
    if (!state.movementType) return

    if (!movementAmount || Number(movementAmount) <= 0) {
      showToast("Monto inválido")
      return
    }
    if (!movementReason.trim()) {
      showToast("Debe indicar un motivo")
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
    } catch {
      // apiFetch ya mostró el error.
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

  /**
   * Cerrar caja
   */
  const closeCashRegister = async () => {
    if (!realCash) {
      showToast("Ingrese efectivo contado")
      return
    }

    try {
      const summary =
        await apiFetch<RawCashRegisterCloseSummary>(
          "/cash-register/close",
          {
            method: "POST",
            body: {
              counted_cash: Number(realCash),
              difference_reason: differenceReason
            },
            suppressErrorToast: true
          }
        )

      const normalizedSummary = normalizeCloseSummary(summary)

      setCloseModalOpen(false)

      setCloseSummary(normalizedSummary)

      setShowCloseSummary(true)

      dispatch({
        type: "SET_DASHBOARD",
        payload: null
      })

    } catch (error: unknown) {
      if (!isApiError(error)) {
        showToast("No se pudo cerrar la caja")
        return
      }

      switch (error.code) {
        case ErrorCode.ORDER_HAS_REMAINING_BALANCE: {
          const remaining = error.context?.remaining
          showToast(`Falta pagar ${ typeof remaining === "number" || typeof remaining === "string" ? remaining: ""}`)
          break
        }

        case ErrorCode.ORDER_ITEMS_NOT_DELIVERED: {
          const items = error.context?.items
          showToast(Array.isArray(items) ? `Platos pendientes: ${items.join(", ")}` : "Hay platos pendientes de entregar")
          break
        }

        case ErrorCode.CASH_REGISTER_PENDING_ORDERS:
          showToast(
            "No se puede cerrar la caja mientras existan órdenes abiertas"
          )
          break

        default:
          showToast(
            error.message ||
            "No se pudo cerrar la caja"
          )
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
      try {
        await fetchActiveOrders()
      } finally {
        fetching = false
      }
      if (pending) {
        pending = false
        await safeFetchOrders()
      }
    }

    // CARGA INICIAL
    const init = async () => {
      try {
        await fetchDashboard()
        await safeFetchOrders()
      } finally {
        dispatch({
          type: "SET_LOADING",
          payload: false
        })
      }
    }

    init()


    wsService.connect()

    const handler = async ({ type, data }: WSEventParsed) => {
      switch (type) {

        case WSEvent.CASH_MOVEMENT_ADDED:
        case WSEvent.CASH_MOVEMENT_DELETED:
          scheduleDashboardRefresh()
          break

        case WSEvent.PAYMENT_ADDED:
        case WSEvent.PAYMENT_DELETED:
          if (!hasOrderId(data)) {
            console.warn(
              `Payload inválido para ${type}`,
              data
            )
            return
          }
          scheduleOrdersRefresh()
          scheduleDashboardRefresh()
          if (
            selectedOrderRef.current?.id ===
            data.order_id
          ) {
            await selectOrder(data.order_id)
          }
        break

        case WSEvent.ORDER_UPDATED:
          if (!hasOrderId(data)) {
            console.warn(
              "Payload inválido para ORDER_UPDATED",
              data
            )
            return
          }
          scheduleOrdersRefresh()
          if ( selectedOrderRef.current?.id === data.order_id) {
            await selectOrder(data.order_id)
          }
        break

        case WSEvent.ORDER_UPDATED:
          if (!hasOrderId(data)) {
            console.warn(
              "Payload inválido para ORDER_UPDATED",
              data
            )
            return
          }
          scheduleOrdersRefresh()
          if (
            selectedOrderRef.current?.id ===
            data.order_id
          ) {
            await selectOrder(data.order_id)
          }
          break

        case WSEvent.ORDER_STATUS_CHANGED:
          if (!isOrderStatusChangedPayload(data)) {
            console.warn("Payload inválido para ORDER_STATUS_CHANGED", data)
            return
          }
          dispatch({
            type: "UPDATE_ORDER_STATUS",
            payload: {
              order_id: data.order_id,
              status: data.status
            }
          })
        break

        case WSEvent.ORDER_CLOSED:
          if (!hasOrderId(data)) {
            return
          }
          dispatch({
            type: "REMOVE_ORDER",
            payload: data.order_id
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

          <hr/>

          <p>Apertura</p>
          <h3>${closeSummary.opening_amount.toFixed(2)}</h3>

          <p>Ventas Totales</p>
          <h2>${closeSummary.total_sales.toFixed(2)}</h2>

          <p>Órdenes atendidas</p>
          <b>{closeSummary.transactions_count}</b>

          <hr/>

          <h3>Ventas por método</h3>

          {Object.entries(closeSummary.by_method).map(([method, amount]) => (
            <p key={method}>
              {methodLabels[method as PaymentMethod]}: ${amount.toFixed(2)}
            </p>
          ))}

          <hr/>

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
            }}
          >
            Finalizar
          </button>

        </div>
      </div>
    )
  }


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
              showToast("Ingrese un monto válido")
              return
            }
            if (amount < 0) {
              showToast("El monto no puede ser negativo")
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
            } catch {
            // apiFetch ya mostró el error.
            }
          }}
        >
          Abrir Caja
        </button>
      </div>
    )
  }


  // ✅ Render principal usando desestructuración con valores por defecto
  return (
    <div className="cashier-page">

      {/* CASH SUMMARY */}
      <aside className="cashier-summary">

        <div className="cashier-panel-header">
          <p>Caja</p>
          <h2>💰 Resumen</h2>
        </div>

        <div className="cashier-metrics">

          <div>
            <span>Apertura</span>
            <strong>
              ${opening_amount.toFixed(2)}
            </strong>
          </div>

          <div className="cashier-metric--featured">
            <span>Ventas</span>
            <strong>
              ${total_sales.toFixed(2)}
            </strong>
          </div>

          <div>
            <span>Órdenes</span>
            <strong>{orders_count}</strong>
          </div>

          <div>
            <span>Ticket promedio</span>
            <strong>
              ${average_ticket.toFixed(2)}
            </strong>
          </div>

        </div>

        <div className="cashier-expected">
          <span>Efectivo esperado</span>
          <strong>
            ${expected_cash.toFixed(2)}
          </strong>
        </div>

        {/* Ventas por Método*/}
        <div className="cashier-payment-breakdown">

          <h3>Ventas por método</h3>

          {(
            Object.entries(by_method) as
              [PaymentMethod, number][]
          )
            .sort((a, b) => b[1] - a[1])
            .map(([method, amount]) => (
              <div
                key={method}
                className="cashier-payment-breakdown__row"
              >
                <span
                  style={{
                    color: methodColors[method]
                  }}
                >
                  {methodLabels[method]}
                </span>

                <strong>
                  ${amount.toFixed(2)}
                </strong>
              </div>
            ))}
        </div>

        {/* Movimientos de Caja */}
        <div className="cashier-movements">

          <h3>Movimientos</h3>

          {cash_movements
            .slice(0, 5)
            .map(movement => (
              <div
                key={movement.id}
                className="cashier-movement"
              >
                <div>
                  <span>
                    {movement.type ===
                      CashMovementType.CASH_IN
                      ? "➕"
                      : "➖"}
                  </span>

                  <span>
                    {movement.reason}
                  </span>
                </div>

                <div className="cashier-movement__amount">
                  <strong>
                    ${movement.amount.toFixed(2)}
                  </strong>

                  <button
                    type="button"
                    className="btn btn-icon btn-danger"
                    title="Eliminar movimiento"
                    onClick={async () => {
                      if (
                        !confirm(
                          "¿Eliminar movimiento?"
                        )
                      ) {
                        return
                      }

                      try {
                        await apiFetch(
                          `/cash-register/movements/${movement.id}`,
                          {
                            method: "DELETE"
                          }
                        )

                        await fetchDashboard()

                      } catch {
                        // apiFetch ya mostró el error.
                      }
                    }}
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
        </div>

        {/* Ingreso y Retiro de Caja*/}
        <div className="cashier-movement-actions">

          <button
            className="btn btn-cash-in"
            onClick={() =>
              openMovementModal(
                CashMovementType.CASH_IN
              )
            }
          >
            ➕ Ingreso
          </button>

          <button
            className="btn btn-cash-out"
            onClick={() =>
              openMovementModal(
                CashMovementType.CASH_OUT
              )
            }
          >
            ➖ Retiro
          </button>
        </div>
      </aside>

      {/* ORDENES ACTIVAS */}
      <section className="cashier-orders">

        <div className="cashier-panel-header">
          <p>Cobros</p>
          <h2>Órdenes activas</h2>
        </div>

        <div className="cashier-order-list">

          {orders
            .filter(order =>
              order.status !== OrderStatus.CLOSED &&
              order.status !== OrderStatus.CANCELLED
            )
            .sort(
              (a, b) =>
                b.remaining - a.remaining
            )
            .map(order => {
              const selected =
                selectedOrder?.id === order.id

              return (
                <button
                  key={order.id}
                  type="button"
                  className={
                    selected
                      ? "cashier-order cashier-order--selected"
                      : "cashier-order"
                  }
                  onClick={() =>
                    selectOrder(order.id)
                  }
                >
                  <div className="cashier-order__header">
                    <strong>
                      {paymentStatusIcon(order)}
                      {" "}
                      Mesa {order.table_number}
                    </strong>

                    <span>
                      #{order.id}
                    </span>
                  </div>

                  <div className="cashier-order__balance">
                    Saldo
                    <strong>
                      ${order.remaining.toFixed(2)}
                    </strong>
                  </div>
                </button>
              )
            })}

        </div>

      </section>

      {/* PANEL DE PAGO */}
      <section className="cashier-payment">
        {selectedOrder ? (
          <>
            <div className="cashier-payment-header">
              <div>
                <p>Cobro</p>
                <h2>
                  Mesa {selectedOrder.table_number}
                </h2>
              </div>

              <span>
                Orden #{selectedOrder.id}
              </span>
            </div>

            <div className="cashier-order-totals">

              <div>
                <span>Subtotal</span>
                <strong>
                  ${selectedOrder.subtotal.toFixed(2)}
                </strong>
              </div>

              <div>
                <span>Descuento</span>
                <strong
                  className={
                    selectedOrder.discount > 0
                      ? "cashier-order-discount"
                      : "cashier-order-discount--empty"
                  }
                >
                  {selectedOrder.discount > 0
                    ? `-$${selectedOrder.discount.toFixed(2)}`
                    : "$0.00"}
                </strong>
              </div>

              <div>
                <span>Total</span>
                <strong>
                  ${selectedOrder.total.toFixed(2)}
                </strong>
              </div>

              <div>
                <span>Pagado</span>
                <strong>
                  ${selectedOrder.total_paid.toFixed(2)}
                </strong>
              </div>

            </div>
            
            <hr/>
            <h3>Descuento</h3>
            <div className="cashier-discount-fields">
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
              />
            </div>

            <div className={selectedOrder.discount > 0
                  ? "cashier-discount-actions cashier-discount-actions--two"
                  : "cashier-discount-actions"
              }
            >
              <button
                className="btn btn-secondary"
                disabled={selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED}
                onClick={applyDiscount}
              >
                Aplicar Descuento
              </button>

              <button
                className="btn btn-danger"
                disabled={selectedOrder.status === OrderStatus.CLOSED || selectedOrder.status === OrderStatus.CANCELLED}
                onClick={removeDiscount}
              >
                Quitar Descuento
              </button>
            </div>

            <hr/>

            <h3>Pagos</h3>

            {selectedOrder.payments?.length === 0 && (
              <p style={{opacity:0.6}}>Sin pagos</p>
            )}

            <div className="cashier-existing-payments">

              {selectedOrder.payments?.map(payment => (
                <div
                  key={payment.id}
                  className="cashier-existing-payment"
                >
                  <span>
                    {methodLabels[payment.method]}
                  </span>

                  <strong>
                    ${payment.amount.toFixed(2)}
                  </strong>

                  {selectedOrder.status !==
                    OrderStatus.CLOSED && (
                    <button
                      type="button"
                      className="btn btn-icon btn-danger"
                      title="Cancelar pago"
                      onClick={async () => {
                        if (
                          !confirm(
                            "¿Cancelar pago?"
                          )
                        ) {
                          return
                        }

                        try {
                          await apiFetch(
                            `/orders/payments/${payment.id}`,
                            {
                              method: "DELETE"
                            }
                          )
                        } catch {
                          // apiFetch ya mostró el error.
                        }
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}

            </div>

            <p style={{marginTop:10,opacity:0.7}}>
              Total pagos: ${selectedOrder.total_paid.toFixed(2)}
            </p>

            <div className="cashier-payment-display">
              ${paymentAmount || "0.00"}
            </div>

            <input
              className="cashier-payment-input"
              ref={paymentInputRef}
              type="number"
              step="0.01"
              value={paymentAmount}
              onChange={e => setPaymentAmount(e.target.value)}
            />

            <div className="cashier-payment-methods">
              {Object.values(PaymentMethod)
                .map(method => (
                  <button
                    key={method}
                    className={`btn ${paymentMethodClass(method)}`}
                    disabled={processingPayment || selectedOrder.remaining <= 0}
                    onClick={() => registerPayment(method)
                    }
                  >
                    {methodLabels[method]}
                  </button>
                ))}
            </div>

            <button
              className="btn btn-success cashier-pay-total"
              disabled={
                processingPayment ||
                selectedOrder.remaining <= 0
              }
              onClick={() => registerPayment(PaymentMethod.CASH, selectedOrder.remaining)}
            >
              💵 Pagar total en efectivo
            </button>

            {selectedOrder.remaining === 0 &&
              selectedOrder.status !== OrderStatus.CLOSED &&
              selectedOrder.status !== OrderStatus.CANCELLED && (
                <button
                  className="btn btn-primary cashier-close-order"
                  onClick={async () => {
                    try {
                      await apiFetch(`/orders/${selectedOrder.id}/close`, {method: "POST"})
                    } catch {
                    // apiFetch ya mostró el error.
                    }
                  }}
                >
                  Cerrar Orden
                </button>
            )}
          </>
        ) : (
          <div className="cashier-no-selection">
            <strong>Seleccione una orden</strong>

            <span>
              El detalle y las opciones de cobro aparecerán aquí.
            </span>
          </div>
        )}
      </section>

      {/* Registrar un movimiento*/}
      {state.movementModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-card">

            <h2>
              {state.movementType ===
                CashMovementType.CASH_IN
                ? "➕ Ingreso de caja"
                : "➖ Retiro de caja"}
            </h2>

            <div className="modal-fields">
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
              />
            </div>

            <div className="modal-actions">

              <button
                className="btn btn-secondary"
                onClick={() =>
                  dispatch({
                    type:
                      "CLOSE_MOVEMENT_MODAL"
                  })
                }
              >
                Cancelar
              </button>

              <button
                className={
                  state.movementType ===
                  CashMovementType.CASH_IN
                    ? "btn btn-cash-in"
                    : "btn btn-cash-out"
                }
                onClick={registrarMovimiento}
              >
                Registrar
              </button>

            </div>

          </div>
        </div>
      )}

      {/* Cerrar caja*/}
      <button
        className="btn btn-danger cashier-close-button"
        onClick={() =>
          setCloseModalOpen(true)
        }
      >
        Cerrar caja
      </button>

      {/* Modal de cierre de caja*/}
      {closeModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-card">

            <h2>🔒 Cierre de Caja</h2>

            <hr/>

            <div className="cashier-close-summary">
              <div>
                <span>Apertura</span>
                <strong>
                  ${opening_amount.toFixed(2)}
                </strong>
              </div>

              <div>
                <span>Ventas</span>
                <strong>
                  ${total_sales.toFixed(2)}
                </strong>
              </div>

              <div>
                <span>Órdenes</span>
                <strong>{orders_count}</strong>
              </div>
            </div>

            <hr/>

            <h3>Ventas por método</h3>

            {Object.values(PaymentMethod).map(method => (
              <p
                key={method}
                style={{ color: methodColors[method] }}
              >
                {methodLabels[method]}: $
                {by_method[method].toFixed(2)}
              </p>
            ))}

            <hr/>

            <p>Efectivo esperado</p>
            <h2 style={{color:"#00e676"}}>
              ${expected_cash.toFixed(2)}
            </h2>

            <p style={{marginTop:10}}>Efectivo contado</p>
            <div className="modal-fields">
              <input
                type="number"
                value={realCash}
                onChange={e=>setRealCash(e.target.value)}
                placeholder="Ingrese efectivo real"
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
                />
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={()=>setCloseModalOpen(false)}
              >
                Cancelar
              </button>

              <button
                className="btn btn-danger"
                onClick={closeCashRegister}
              >
                Confirmar Cierre
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  )
}
