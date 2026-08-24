import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { apiFetch } from "../api"
import { wsService } from "../services/wsService"
import type { WSEventParsed } from "../ws"

import { moneyToNumber } from "../utils/money"

import { showToast } from "../utils/showToast"

import type {
  AddProductToTableResponse,
  OrderDetail,
  RawOrderDetail
} from "../types/order"

import type { 
  CategoryWithProducts,
  RawProduct,
  RawCategoryWithProducts
} from "../types/category"

import type { Product } from "../types/product"

import { OrderStatus } from "../types/orderStatus"
import { OrderItemStatus } from "../types/orderItemStatus"
import { PaymentMethod } from "../types/paymentMethod"
import { WSEvent } from "../types/webSocketEvents"


type CancellationTarget =
  | {
      type: "item"
      itemId: number
      productName: string
      cancelsOrder: boolean
    }
  | {
      type: "order"
    }


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

function normalizeProduct(
  product: RawProduct
): Product {
  return {
    ...product,
    price: moneyToNumber(product.price)
  }
}


function orderStatusLabel(status: OrderStatus): string {
  switch (status) {
    case OrderStatus.OPEN:
      return "Abierta"

    case OrderStatus.SENT:
      return "Enviada"

    case OrderStatus.IN_PROGRESS:
      return "Preparando"

    case OrderStatus.READY:
      return "Lista"

    case OrderStatus.CLOSED:
      return "Cerrada"

    case OrderStatus.CANCELLED:
      return "Cancelada"
    
    default:
      return status
  }
}

function paymentMethodLabel(method: PaymentMethod): string {
  switch (method) {
    case PaymentMethod.CASH:
      return "Efectivo"

    case PaymentMethod.CARD:
      return "Tarjeta"

    case PaymentMethod.TRANSFER:
      return "Transferencia"

    case PaymentMethod.OTHER:
      return "Otra forma de pago"

    default:
      return method
  }
}

/**
 * Asigna una etiqueta al item dependiendo de su status
 */
function orderItemStatusLabel(
  status: OrderItemStatus
): string {
  switch (status) {
    case OrderItemStatus.PENDING:
      return "Pendiente"

    case OrderItemStatus.SENT:
      return "Enviado"

    case OrderItemStatus.IN_PROGRESS:
      return "Preparando"

    case OrderItemStatus.READY:
      return "Listo"

    case OrderItemStatus.DELIVERED:
      return "Entregado"

    case OrderItemStatus.CANCELLED:
      return "Cancelado"

    default:
      return status
  }
}

function getItemStatusColor(
  status: OrderItemStatus
): string {
  switch (status) {
    case OrderItemStatus.PENDING:
      return "var(--status-draft)"

    case OrderItemStatus.SENT:
      return "var(--status-sent)"

    case OrderItemStatus.IN_PROGRESS:
      return "var(--status-inprogress)"

    case OrderItemStatus.READY:
      return "var(--status-ready)"

    case OrderItemStatus.DELIVERED:
      return "var(--status-delivered)"

    case OrderItemStatus.CANCELLED:
      return "var(--color-danger)"

    default:
      return "var(--color-text-secondary)"
  }
}

export default function OrderDetail() {
  const { orderId, tableId } = useParams()

  const id = orderId ? Number(orderId) : null

  const navigate = useNavigate()

  const [order, setOrder] = useState<OrderDetail | null>(null)

  const [loading, setLoading] = useState(true)

  const [categories, setCategories] = useState<CategoryWithProducts[]>([])

  const [openCategory, setOpenCategory] = useState<number | null>(null)

  const [paymentAmount, setPaymentAmount] = useState("")

  const [quantities, setQuantities] = useState<Record<number, number>>({})

  const [discount, setDiscount] = useState("")

  const [notes, setNotes] = useState<Record<number, string>>({})

  const [openNotes, setOpenNotes] = useState<Record<number, boolean>>({})

  const [discountType, setDiscountType] = useState<"amount" | "percent">("amount")

  const updating = useRef(false)

  const [cancellationTarget, setCancellationTarget] = useState<CancellationTarget | null>(null)

  const [cancellationReason, setCancellationReason] = useState("")

  const [cancelling, setCancelling] = useState(false)

  /**
   * Obtiene la orden actual desde el backend y normaliza
   * sus valores monetarios.
   *
   * El backend permanece como fuente de verdad.
   */
  const fetchOrder = async () => {
    if (!id) return
    try {
      const data = await apiFetch<RawOrderDetail>(`/orders/${id}`)
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
    const data = await apiFetch<RawCategoryWithProducts[]>("/categories/with-products")
    setCategories(
      data.map(category => ({...category, products: category.products.map(normalizeProduct)}))
    )
  }

  /**
   * Agrega un producto a la orden.
   *
   * Si todavía no existe una orden para la mesa,
   * el backend la crea y devuelve su identificador.
   */
  const addProduct = async (productId: number) => {
    const quantity = quantities[productId] || 1
    const note = notes[productId]?.trim() || null

    if (order?.status === OrderStatus.CLOSED) {
      showToast("No se pueden agregar productos a una orden cerrada")
      return
    }

    if (order?.status === OrderStatus.CANCELLED) {
      showToast("No se pueden agregar productos a una orden cancelada")
      return
    }
    
    if (!orderId) {
      if (!tableId) return

      const data = await apiFetch<AddProductToTableResponse>(
          `/tables/${tableId}/add-product`,
          {
            method: "POST",
            body: {
              product_id: productId,
              quantity,
              notes: note
            }
          }
        )
      setQuantities(current => ({...current, [productId]: 1}))
      setNotes(current => ({...current, [productId]: ""}))
      setOpenNotes(current => ({...current, [productId]: false}))

      navigate(`/orders/${data.order_id}`)
      return
    }

    await apiFetch(`/orders/${orderId}/items`,
      {
        method: "POST",
        body: {
          product_id: productId,
          quantity,
          notes: note
        }
      }
    )

    setQuantities(current => ({...current, [productId]: 1}))
    setNotes(current => ({...current, [productId]: ""}))
    setOpenNotes(current => ({...current, [productId]: false}))

    await fetchOrder()
  }


  /**
   * Elimina un ítem pendiente de la orden.
   *
   * Si se trata del último ítem activo, solicita confirmación
   * porque su eliminación puede cancelar la orden completa.
   */
  const removeItem = async (
    orderId: number,
    itemId: number
  ) => {
    if (!order) return

    const activeItems = order.items.filter(
      item =>
        item.status !== OrderItemStatus.CANCELLED
    )

    const isLastActiveItem =
      activeItems.length === 1 &&
      activeItems[0].id === itemId

    if (
      isLastActiveItem &&
      !window.confirm(
        "Este es el único producto de la orden.\n\n" +
        "Al eliminarlo se cancelará la orden.\n" +
        "¿Desea continuar?"
      )
    ) {
      return
    }

    try {
      await apiFetch(
        `/orders/${orderId}/items/${itemId}`,
        {
          method: "DELETE"
        }
      )

      await fetchOrder()
    } catch {
      // apiFetch ya mostró el error.
    }
  }
  /**
   * Actualiza la cantidad de un ítem pendiente.
   *
   * El ref evita enviar modificaciones concurrentes
   * mientras una actualización anterior sigue en curso.
   */
  const updateQuantity = async (itemId: number, quantity: number) => {
    if (updating.current) return
    updating.current = true
    try {
      await apiFetch(`/orders/order-items/${itemId}?quantity=${quantity}`,{method: "PATCH"})
      await fetchOrder()
    } finally {
      updating.current = false
    }
  }

  /**
   * Marca un ítem READY como entregado.
   */
  const markDelivered = async (itemId: number) => {
    await apiFetch(`/order-items/${itemId}/status`,
      {method: "PATCH", body: {status: OrderItemStatus.DELIVERED}}
    )
    await fetchOrder()
  }

  /**
   * Registra un pago para la orden actual.
   */
  const registerPayment = async (method: PaymentMethod) => {
    if (!id) return

    const amount = Number(paymentAmount)

    if (!Number.isFinite(amount) || amount <= 0) {
      alert("El pago debe ser mayor a 0")
      return
    }
    await apiFetch(`/orders/${id}/payments`,
      {method: "POST", body: {amount, method}}
    )
    await fetchOrder()
  }

  /**
   * Elimina un pago registrado mientras la orden
   * todavía permanece abierta.
   */
  const cancelPayment = async (paymentId: number) => {
    await apiFetch(`/orders/payments/${paymentId}`,{method: "DELETE"})
    await fetchOrder()
  }

  /**
   * Cierra una orden que cumple las reglas de negocio
   * de pago completo e ítems entregados.
   */
  const closeOrder = async () => {
    if (!id) return
    await apiFetch(`/orders/${id}/close`,{method: "POST"})
    await fetchOrder()
  }

  /**
   * Envía todos los ítems pendientes de la orden
   * hacia sus respectivas estaciones de producción.
   */
  const sendToKitchen = async () => {
    if (!id) return
    await apiFetch(`/orders/${id}/send-to-kitchen`,{method: "POST"})
    await fetchOrder()
  }

  /**
   * Abre y Cierra el modal de Cancelación de items y ordenes
   */
  const openItemCancellation = (itemId: number, productName: string) => {
    const activeItems = items.filter(
      item =>
        item.status !== OrderItemStatus.CANCELLED
    )

    setCancellationReason("")

    setCancellationTarget({
      type: "item",
      itemId,
      productName,
      cancelsOrder: activeItems.length === 1
    })
  }

  const openOrderCancellation = () => {
    setCancellationReason("")
    setCancellationTarget({type: "order"})
  }

  const closeCancellationModal = () => {
    if (cancelling) return
    setCancellationTarget(null)
    setCancellationReason("")
  }

  /**
   * Confirma la cancelación
   */
  const confirmCancellation = async () => {
    if (!cancellationTarget) return

    const reason = cancellationReason.trim()

    if (!reason) {showToast("Debe indicar un motivo para la cancelación")
      return
    }

    try {
      setCancelling(true)

      if (cancellationTarget.type === "item") {
        await apiFetch(
          `/order-items/${cancellationTarget.itemId}/cancel`,
          {
            method: "PATCH",
            body: {
              reason
            }
          }
        )
      } else {
        if (!orderId) return

        await apiFetch(
          `/orders/${orderId}/cancel`,
          {
            method: "PATCH",
            body: {
              reason
            }
          }
        )
      }

      setCancellationTarget(null)
      setCancellationReason("")

      await fetchOrder()

    } catch {
      // apiFetch ya mostró el error.
    } finally {
      setCancelling(false)
    }
  }

  /**
   * Estados en los que es posible cancelar el item
   */
  const canCancelItem = (status: OrderItemStatus): boolean =>
    status === OrderItemStatus.SENT ||
    status === OrderItemStatus.IN_PROGRESS ||
    status === OrderItemStatus.READY



  /**
   * El catálogo no depende de la orden,
   * por lo que se carga una sola vez.
   */
  useEffect(() => {fetchCategories()}, [])

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

    const handler = ({type, data}: WSEventParsed) => {
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

    return () => {wsService.unsubscribe(handler)}
  }, [id])


  /**
   * Propone por defecto pagar exactamente
   * el saldo pendiente de la orden.
   */
  useEffect(() => {
    if (!order) return
    setPaymentAmount(order.remaining.toFixed(2))
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
   * Condiciones para desabilitar descuentos y agregar productos
   */
  const orderLocked = order?.status === OrderStatus.CLOSED || order?.status === OrderStatus.CANCELLED

  /**
   * Persiste el descuento monetario aplicado a la orden.
   */
  const setOrderDiscount = async (amount: number) => {
    if (!order) return
    await apiFetch(`/orders/${order.id}/discount?discount=${amount}`,{method: "PUT"})
    setDiscount("")
    await fetchOrder()
  }

  /**
   * Convierte, cuando corresponde, un porcentaje
   * en un importe monetario y aplica el descuento.
   */
  const applyDiscount = async () => {
    if (!order || discount.trim() === "") {
      return
    }
    if (
      !order ||
      order.status === OrderStatus.CLOSED ||
      order.status === OrderStatus.CANCELLED
    ) {
      showToast("No se puede modificar una orden cerrada")
      return
    }
    let finalDiscount = Number(discount)
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
  const removeDiscount = async () => {await setOrderDiscount(0)}

  
  return (

    <div className="order-detail-page">
      <main className="order-detail-main">
        <header className="order-detail-header">

          <div>
            <p className="order-detail-header__eyebrow">
              Mesa {order?.table_number ?? tableId}
            </p>

            <h1>
              {order
                ? `Orden #${order.id}`
                : "Nueva orden"}
            </h1>
          </div>

          {order && (
            <span
              className="order-status-badge"
              style={{
                color: getStatusColor(),
                borderColor: getStatusColor()
              }}
            >
              {orderStatusLabel(order.status)}
            </span>
          )}

        </header>

        {order?.status === OrderStatus.DRAFT && (
          <div className="order-draft-notice">
            🧾 Agrega productos para iniciar la orden.
          </div>
        )}

        {/* PEDIDO */}
        <section className="order-section">
          <div className="order-section__header">
            <h2>Pedido</h2>

            <span>
              {items.length} ítem
              {items.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="order-items">
            {items.map(item => (
              <div
                key={item.id}
                className={
                  item.status === OrderItemStatus.CANCELLED
                    ? "order-item order-item--cancelled"
                    : "order-item"
                }
              >
                <div className="order-item__info">
                  <div className="order-item__name">
                    {item.product_name}
                  </div>

                  {item.notes && (
                    <div className="order-item__notes">
                      {item.notes}
                    </div>
                  )}
                </div>

                {item.status === OrderItemStatus.PENDING && (
                  <div className="order-item__quantity">
                    <button
                      className="btn btn-icon"
                      onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                    >
                      −
                    </button>

                    <strong>{item.quantity}</strong>

                    <button
                      className="btn btn-icon"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>
                )}

                <div className="order-item__price">
                  <span>
                    ${(item.quantity * item.unit_price).toFixed(2)}
                  </span>
                </div>

                <div className="order-item__status">
                  <strong
                    style={{color: getItemStatusColor(item.status)
                    }}
                  >
                    {orderItemStatusLabel(item.status)}
                  </strong>
                </div>
                
                <div className="order-item__actions">
                  {item.status === OrderItemStatus.PENDING && (
                    <button
                      type="button"
                      className="btn btn-icon btn-danger"
                      title="Eliminar ítem"
                      onClick={() => {if (order) {void removeItem(order.id, item.id)}}}
                    >
                      ❌
                    </button>
                  )}

                  {canCancelItem(item.status) && (
                    <button
                      className="btn btn-danger"
                      onClick={() => openItemCancellation(item.id, item.product_name)}
                    >
                      Cancelar
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
                </div>
              </div>
            ))}
          </div>
  
          {/* Subtotales y Totales*/}
          <div className="order-totals">
            <div>
              <span>Subtotal</span>
              <strong>${subtotal.toFixed(2)}</strong>
            </div>

            <div>
              <span>Descuento</span>
              <strong
                className={(order?.discount ?? 0) > 0 ? "order-totals__discount" : ""}
              >
                {(order?.discount ?? 0) > 0 ? "-" : ""}
                ${(order?.discount ?? 0).toFixed(2)}
              </strong>
            </div>

            <div className="order-totals__total">
              <span>Total</span>
              <strong>${total.toFixed(2)}</strong>
            </div>
          </div>
        </section>

        {/* ENVIAR A COCINA */}
        {status !== OrderStatus.CLOSED &&
          hasPendingItems && (
            <div className="order-kitchen-action">
              <button
                type="button"
                className="btn btn-kitchen order-primary-action"
                onClick={sendToKitchen}
              >
                Enviar a cocina
              </button>
            </div>
        )}

        {/* Descuentos */}
        {order && order.status !== OrderStatus.DRAFT && (
          <section className="order-section">
            <div className="order-section__header">
              <h2>Descuento</h2>
            </div>
            <div className="discount-controls">
              <select
                value={discountType}
                onChange={e =>
                  setDiscountType(
                    e.target.value as
                      "amount" | "percent"
                  )
                }
              >
                <option value="amount">
                  Monto
                </option>
                <option value="percent">
                  %
                </option>
              </select>

              <input
                type="text"
                inputMode="decimal"
                placeholder="Monto descuento"
                value={discount}
                onChange={e =>
                  setDiscount(e.target.value)
                }
                disabled={orderLocked}
              />

              <button
                className="btn btn-primary"
                onClick={applyDiscount}
                disabled={orderLocked}
              >
                Aplicar descuento
              </button>

              {(order.discount ?? 0) > 0 && (
                <button
                  className="btn btn-secondary"
                  onClick={removeDiscount}
                  disabled={orderLocked}
                >
                  Quitar descuento
                </button>
              )}
            </div>
          </section>
        )}

        {/* PAGOS */}
        <section className="order-section">
          {order && (
            <>
              <h2>Pagos</h2>
              {payments.length === 0 && ( <p>No hay pagos registrados</p>)}

              <div className="payment-list">
                {payments.map(payment => (
                  <div
                    key={payment.id}
                    className="payment-row"
                  >
                    <span>
                      ${payment.amount.toFixed(2)}
                      {" — "}
                      {paymentMethodLabel(
                        payment.method
                      )}
                    </span>

                    {status !== OrderStatus.CLOSED && (
                      <button
                        type="button"
                        className="btn btn-icon btn-danger"
                        title="Cancelar pago"
                        onClick={() =>
                          cancelPayment(payment.id)
                        }
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <div className="payment-summary">
                <div>
                  <span>Total pagado</span>
                  <strong>
                    ${total_paid.toFixed(2)}
                  </strong>
                </div>

                <div>
                  <span>Saldo pendiente</span>
                  <strong>
                    ${remaining.toFixed(2)}
                  </strong>
                </div>
              </div>
            </>
          )}
        
          {/* FORMULARIO DE PAGO */}
          {order &&
            order.status !== OrderStatus.CLOSED && (
              <div className="payment-form">
                <h3>Registrar pago</h3>

                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Monto"
                  value={paymentAmount}
                  onChange={e => setPaymentAmount(e.target.value)}
                />

                <div className="payment-methods">
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
          )}
        </section>

        {/* CANCELAR ORDEN */}
        {order &&
          order.status !== OrderStatus.CLOSED &&
          order.status !== OrderStatus.CANCELLED && (
            <button
              className="btn btn-danger"
              onClick={openOrderCancellation}
            >
              Cancelar orden
            </button>
        )}


        {/* CERRAR ORDEN SOLO SI CUMPLE REGLAS */}
        {canClose && (
          <div className="order-close-ready">
            <div>
              <strong>✓ Orden lista para cerrar</strong>
              <span>
                Todos los ítems fueron entregados
                y el saldo está pago.
              </span>
            </div>
            <button
              type="button"
              className="btn btn-success"
              onClick={closeOrder}
            >
              Cerrar orden
            </button>
          </div>
        )}
      </main>

      {/* AGREGAR PRODUCTOS */}
      <aside className="order-detail-sidebar">
        <section className="product-picker">
          <div className="product-picker__header">
            <h2>Agregar productos</h2>
          </div>

          {categories.map(category => (
            <div key={category.id} className="product-category-block">
              <button
                type="button"
                className="product-category"
                disabled={orderLocked}
                onClick={() => setOpenCategory(openCategory === category.id ? null : category.id)}
              >
                <span>
                  {category.name}
                </span>

                <span>
                  {openCategory === category.id
                    ? "−"
                    : "+"}
                </span>
              </button>

              {openCategory === category.id && (
                <div className="product-picker__items">
                  {category.products.map(product => (
                    <div
                      key={product.id}
                      className="product-picker__item"
                    >
                      <button
                        className="btn btn-product"
                        disabled={orderLocked}
                        onClick={() =>
                          addProduct(product.id)
                        }
                      >
                        <span>
                          {product.name}
                        </span>

                        <strong>
                          ${product.price.toFixed(2)}
                        </strong>
                      </button>

                      <button
                        className="btn btn-icon"
                        disabled={orderLocked}
                        onClick={() => setQuantities(current => ({...current,
                            [product.id]:
                              Math.max((current[product.id] || 1) - 1, 1)
                          }))
                        }
                      >
                        −
                      </button>

                      <strong className="product-picker__quantity">
                        {quantities[product.id] || 1}
                      </strong>

                      <button
                        className="btn btn-icon"
                        disabled={orderLocked}
                        onClick={() =>
                          setQuantities(current => ({
                            ...current,

                            [product.id]:
                              (current[product.id] || 1) + 1
                          }))
                        }
                      >
                        +
                      </button>

                      <button
                        type="button"
                        className="product-note-toggle"
                        disabled={orderLocked}
                        onClick={() =>
                          setOpenNotes(current => ({
                            ...current,
                            [product.id]: !current[product.id]
                          }))
                        }
                      >
                        {openNotes[product.id]
                          ? "− Ocultar nota"
                          : "+ Nota"}
                      </button>

                      {openNotes[product.id] && (
                        <textarea
                          className="product-notes"
                          disabled={orderLocked}
                          value={notes[product.id] || ""}
                          onChange={event =>
                            setNotes(current => ({
                              ...current,
                              [product.id]: event.target.value
                            }))
                          }
                          placeholder="Ej.: sin mayonesa, sin cebolla..."
                          maxLength={500}
                          rows={2}
                        />
                      )}


                    </div>
                  ))}
                </div>
              )}
            </div>

          ))}
        </section>
      </aside>
      
      {/* Modal para cancelación de items y de ordenes */}
      {cancellationTarget && (
        <div className="modal-backdrop">
          <div className="modal-card">

            <h2>
              {cancellationTarget.type === "item"
                ? "Cancelar item"
                : "Cancelar orden"}
            </h2>

            {cancellationTarget.type === "item" ? (
              <>
                <p>
                  Se cancelará{" "}
                  <strong>
                    {cancellationTarget.productName}
                  </strong>
                  . El item permanecerá registrado en el
                  historial de la orden.
                </p>

                {cancellationTarget.cancelsOrder && (
                  <p className="cancellation-warning">
                    Este es el último item activo. Al cancelarlo,
                    la orden también será cancelada.
                  </p>
                )}
              </>
            ) : (
              <p>
                Se cancelará la orden completa.
                Los items permanecerán registrados
                para conservar el historial.
              </p>
            )}

            <div className="modal-fields">
              <label>
                Motivo de cancelación

                <textarea
                  value={cancellationReason}
                  onChange={event =>
                    setCancellationReason(
                      event.target.value
                    )
                  }
                  maxLength={500}
                  rows={4}
                  autoFocus
                  placeholder={
                    cancellationTarget.type === "item"
                      ? "Ej.: plato frío, pedido incorrecto..."
                      : "Ej.: cliente canceló el pedido..."
                  }
                />
              </label>
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={closeCancellationModal}
                disabled={cancelling}
              >
                Volver
              </button>

              <button
                className="btn btn-danger"
                onClick={confirmCancellation}
                disabled={
                  cancelling ||
                  !cancellationReason.trim()
                }
              >
                {cancelling
                  ? "Cancelando..."
                  : cancellationTarget.type === "item"
                    ? "Cancelar item"
                    : "Cancelar orden"}
              </button>
            </div>

          </div>
        </div>
      )}



  </div>      
  )

}
