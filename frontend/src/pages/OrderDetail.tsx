import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { apiFetch } from "../api"
import { wsService } from "../services/wsService"
import type { WSEventParsed } from "../ws"

import { moneyToNumber } from "../utils/money"

import type {
  AddProductToTableResponse,
  OrderDetail,
  RawOrderDetail
} from "../types/order"

import type { CategoryWithProducts } from "../types/category"

import { OrderStatus } from "../types/orderStatus"
import { OrderItemStatus } from "../types/orderItemStatus"
import { PaymentMethod } from "../types/paymentMethod"
import { WSEvent } from "../types/webSocketEvents"


/**
 * Eventos WebSocket que pueden modificar la información
 * mostrada en el detalle de una orden.
 */
const ORDER_DETAIL_EVENTS = new Set<string>([
  WSEvent.ORDER_UPDATED,
  WSEvent.ORDER_STATUS_CHANGED,
  WSEvent.ORDER_CLOSED,
  WSEvent.ITEM_STATUS_CHANGED,
  WSEvent.PAYMENT_ADDED,
  WSEvent.PAYMENT_DELETED
])


/**
 * Comprueba que el payload recibido por WebSocket
 * contiene un identificador de orden válido.
 */
function hasOrderId(
  value: unknown
): value is { order_id: number } {
  return (
    typeof value === "object" &&
    value !== null &&
    "order_id" in value &&
    typeof value.order_id === "number"
  )
}


/**
 * Convierte los valores monetarios recibidos desde la API
 * a number para poder utilizarlos de forma segura en la UI.
 */
function normalizeOrder(
  data: RawOrderDetail
): OrderDetail {
  return {
    ...data,

    items: (data.items ?? []).map(item => ({
      ...item,
      unit_price: moneyToNumber(item.unit_price)
    })),

    payments: (data.payments ?? []).map(payment => ({
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

  const id = orderId
    ? Number(orderId)
    : null

  const navigate = useNavigate()

  const [order, setOrder] =
    useState<OrderDetail | null>(null)

  const [loading, setLoading] =
    useState(true)

  const [categories, setCategories] =
    useState<CategoryWithProducts[]>([])

  const [openCategory, setOpenCategory] =
    useState<number | null>(null)

  const [paymentAmount, setPaymentAmount] =
    useState("")

  const [quantities, setQuantities] =
    useState<Record<number, number>>({})

  const [discount, setDiscount] =
    useState("")

  const [discountType, setDiscountType] =
    useState<"amount" | "percent">("amount")

  const updating = useRef(false)

  /**
   * Obtiene la orden actual desde el backend y normaliza
   * sus valores monetarios.
   *
   * El backend permanece como fuente de verdad.
   */
  const fetchOrder = async () => {
    if (!id) return

    try {
      const data =
        await apiFetch<RawOrderDetail>(
          `/orders/${id}`
        )

      setOrder(normalizeOrder(data))
    } finally {
      setLoading(false)
    }
  }


  /**
   * Carga las categorías activas junto con sus productos
   * disponibles para agregar a la orden.
   */
  const fetchCategories = async () => {
    const data =
      await apiFetch<CategoryWithProducts[]>(
        "/categories/with-products"
      )

    setCategories(data)
  }


  /**
   * Agrega un producto a la orden.
   *
   * Si todavía no existe una orden para la mesa,
   * el backend la crea y devuelve su identificador.
   */
  const addProduct = async (
    productId: number
  ) => {
    const quantity =
      quantities[productId] || 1

    if (
      order?.status === OrderStatus.CLOSED
    ) {
      return
    }

    if (!orderId) {
      if (!tableId) return

      const data =
        await apiFetch<AddProductToTableResponse>(
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

    await apiFetch(
      `/orders/${orderId}/items`,
      {
        method: "POST",
        body: {
          product_id: productId,
          quantity
        }
      }
    )

    await fetchOrder()
  }


  /**
   * Elimina un ítem pendiente de la orden.
   */
  const removeItem = async (
    orderId: number,
    itemId: number
  ) => {
    await apiFetch(
      `/orders/${orderId}/items/${itemId}`,
      {
        method: "DELETE"
      }
    )

    await fetchOrder()
  }


  /**
   * Actualiza la cantidad de un ítem pendiente.
   *
   * El ref evita enviar modificaciones concurrentes
   * mientras una actualización anterior sigue en curso.
   */
  const updateQuantity = async (
    itemId: number,
    quantity: number
  ) => {
    if (updating.current) return

    updating.current = true

    try {
      await apiFetch(
        `/orders/order-items/${itemId}?quantity=${quantity}`,
        {
          method: "PATCH"
        }
      )

      await fetchOrder()
    } finally {
      updating.current = false
    }
  }


  /**
   * Marca un ítem READY como entregado.
   */
  const markDelivered = async (
    itemId: number
  ) => {
    await apiFetch(
      `/order-items/${itemId}/status`,
      {
        method: "PATCH",
        body: {
          status: OrderItemStatus.DELIVERED
        }
      }
    )

    await fetchOrder()
  }


  /**
   * Registra un pago para la orden actual.
   */
  const registerPayment = async (
    method: PaymentMethod
  ) => {
    if (!id) return

    const amount = Number(paymentAmount)

    if (
      !Number.isFinite(amount) ||
      amount <= 0
    ) {
      alert("El pago debe ser mayor a 0")
      return
    }

    await apiFetch(
      `/orders/${id}/payments`,
      {
        method: "POST",
        body: {
          amount,
          method
        }
      }
    )

    await fetchOrder()
  }


  /**
   * Elimina un pago registrado mientras la orden
   * todavía permanece abierta.
   */
  const cancelPayment = async (
    paymentId: number
  ) => {
    await apiFetch(
      `/orders/payments/${paymentId}`,
      {
        method: "DELETE"
      }
    )

    await fetchOrder()
  }


  /**
   * Cierra una orden que cumple las reglas de negocio
   * de pago completo e ítems entregados.
   */
  const closeOrder = async () => {
    if (!id) return

    await apiFetch(
      `/orders/${id}/close`,
      {
        method: "POST"
      }
    )

    await fetchOrder()
  }


  /**
   * Envía todos los ítems pendientes de la orden
   * hacia sus respectivas estaciones de producción.
   */
  const sendToKitchen = async () => {
    if (!id) return

    await apiFetch(
      `/orders/${id}/send-to-kitchen`,
      {
        method: "POST"
      }
    )

    await fetchOrder()
  }

  /**
   * El catálogo no depende de la orden,
   * por lo que se carga una sola vez.
   */
  useEffect(() => {
    fetchCategories()
  }, [])


  /**
   * Carga el detalle cuando existe una orden.
   * Si todavía estamos creando una orden desde una mesa,
   * simplemente habilita la pantalla.
   */
  useEffect(() => {
    if (id) {
      setLoading(true)
      fetchOrder()
    } else {
      setOrder(null)
      setLoading(false)
    }
  }, [id])


  /**
   * Mantiene sincronizado el detalle ante cambios
   * realizados desde otras terminales.
   */
  useEffect(() => {
    if (!id) return

    const handler = ({
      type,
      data
    }: WSEventParsed) => {
      if (!ORDER_DETAIL_EVENTS.has(type)) {
        return
      }
      console.log("WS EVENT:", type, data)
      if (
        !hasOrderId(data) ||
        data.order_id !== id
      ) {
        return
      }

      fetchOrder()
    }

    wsService.subscribe(handler)

    return () => {
      wsService.unsubscribe(handler)
    }
  }, [id])


  /**
   * Propone por defecto pagar exactamente
   * el saldo pendiente de la orden.
   */
  useEffect(() => {
    if (!order) return

    setPaymentAmount(
      order.remaining.toFixed(2)
    )
  }, [order?.remaining])

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
    items.every(i => i.status === OrderItemStatus.DELIVERED)
  const canClose =
    remaining === 0 &&
    allDelivered &&
    status !== OrderStatus.CLOSED
  const hasPendingItems =
    items.some(i => i.status === OrderItemStatus.PENDING)
  const getStatusColor = () => {
    switch (status) {
      case OrderStatus.OPEN:
        return "green"

      case OrderStatus.SENT:
        return "orange"

      case OrderStatus.IN_PROGRESS:
        return "blue"

      case OrderStatus.READY:
        return "purple"

      case OrderStatus.CLOSED:
        return "gray"

      case OrderStatus.CANCELLED:
        return "red"

      default:
        return "black"
    }
  }

  /**
   * Persiste el descuento monetario aplicado a la orden.
   */
  const setOrderDiscount = async (
    amount: number
  ) => {
    if (!order) return

    await apiFetch(
      `/orders/${order.id}/discount?discount=${amount}`,
      {
        method: "PUT"
      }
    )

    setDiscount("")

    await fetchOrder()
  }


  /**
   * Convierte, cuando corresponde, un porcentaje
   * en un importe monetario y aplica el descuento.
   */
  const applyDiscount = async () => {
    if (
      !order ||
      discount.trim() === ""
    ) {
      return
    }

    let finalDiscount =
      Number(discount)

    if (
      !Number.isFinite(finalDiscount) ||
      finalDiscount < 0
    ) {
      alert("Descuento inválido")
      return
    }

    if (
      discountType === "percent"
    ) {
      finalDiscount =
        (order.subtotal * finalDiscount) / 100
    }

    await setOrderDiscount(finalDiscount)
  }


  /**
   * Elimina cualquier descuento existente.
   */
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

        {order && (
          <p>
            Estado:{" "}
            <strong
              style={{
                color: getStatusColor()
              }}
            >
              {order.status}
            </strong>
          </p>
        )}

        {order?.status === OrderStatus.DRAFT && (
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

              {item.status === OrderItemStatus.PENDING && (
                <>
                  <button className="btn btn-icon"
                    onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
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
                    item.status === OrderItemStatus.PENDING
                      ? "#b58900"
                      : item.status === OrderItemStatus.READY
                      ? "#268bd2"
                      : item.status === OrderItemStatus.DELIVERED
                      ? "#2a9d8f"
                      : "#333",
                  textDecoration:
                    item.status === OrderItemStatus.DELIVERED
                      ? "line-through"
                      : "none"
                }}
              >
                {item.status}
              </strong>
              {item.status === OrderItemStatus.PENDING && (
                <button
                  onClick={() => {
                    if (order) {
                      removeItem(order.id, item.id)
                    }
                  }}
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
              {item.status === OrderItemStatus.READY && (
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
        {status !== OrderStatus.CLOSED && hasPendingItems && (
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

        {order && order.status !== OrderStatus.DRAFT && (
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
        {order && (
          <>
            <h2>Pagos</h2>

            {payments.length === 0 && (
              <p>No hay pagos registrados</p>
            )}

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
                    ${p.amount.toFixed(2)} — {p.method}
                  </span>

                  {status !== OrderStatus.CLOSED && (
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

            <p>
              <strong>Total pagado:</strong>{" "}
              ${total_paid.toFixed(2)}
            </p>

            <p>
              <strong>Saldo pendiente:</strong>{" "}
              ${remaining.toFixed(2)}
            </p>
          </>
        )}

        {/* FORMULARIO DE PAGO */}
        {order &&
          order.status !== OrderStatus.CLOSED && (
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
                  onClick={() => registerPayment(PaymentMethod.CASH)}
                >
                💵 Efectivo
                </button>

                <button
                  className="btn btn-payment-card"
                  onClick={() => registerPayment(PaymentMethod.CARD)}
                >
                💳 Tarjeta
                </button>

                <button
                  className="btn btn-payment-transfer"
                  onClick={() => registerPayment(PaymentMethod.TRANSFER)}
                >
                🏦 Transferencia
                </button>

                <button
                  className="btn btn-payment-other"
                  onClick={() => registerPayment(PaymentMethod.OTHER)}
                >
                🤝 Otro
                </button>
              </div>
            </div>
          )
        }

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
                        setQuantities(current => ({
                          ...current,
                          [p.id]: Math.max(
                            (current[p.id] || 1) - 1,
                            1
                          )
                        }))
                      }
                    >
                      −
                    </button>

                    <strong>{quantities[p.id] || 1}</strong>

                    <button className="btn btn-primary"
                      onClick={() =>
                        setQuantities(current => ({
                          ...current,
                          [p.id]: (current[p.id] || 1) + 1
                        }))
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
