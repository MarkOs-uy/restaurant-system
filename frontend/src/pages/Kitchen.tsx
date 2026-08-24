import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { apiFetch } from "../api"
import { wsService } from "../services/wsService"

import { OrderItemStatus } from "../types/orderItemStatus"
import { WSEvent } from "../types/webSocketEvents"

import type { KitchenItem } from "../types/kitchen"
import type { Station } from "../types/station"
import type { WSEventParsed } from "../ws"


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


export default function Kitchen() {
  const { stationId } = useParams()
  const station = Number(stationId)

  const navigate = useNavigate()

  const [items, setItems] = useState<KitchenItem[]>([])
  const [stationName, setStationName] = useState("")
  const [, setClock] = useState(0)


  /**
   * Carga los ítems pendientes de la estación actual.
   */
  const fetchItems = async () => {
    const data = await apiFetch<KitchenItem[]>(
      `/kitchen/stations/${station}/items`
    )
    setItems(data)
  }


  /**
   * Obtiene los datos de la estación actual.
   */
  const fetchStation = async () => {
    const data = await apiFetch<Station>(
      `/stations/${station}`
    )
    setStationName(data.name)
  }


  /**
   * Actualiza el estado de un ítem y refresca la vista
   * usando el backend como fuente de verdad.
   */
  const updateStatus = async (
    itemId: number,
    newStatus: OrderItemStatus
  ) => {
    await apiFetch(
      `/order-items/${itemId}/status`,
      {
        method: "PATCH",
        body: { status: newStatus }
      }
    )

    await fetchItems()
  }


  /**
   * Devuelve el color visual asociado al estado del ítem.
   */
  const getStatusColor = (
    status: OrderItemStatus
  ) => {
    switch (status) {
      case OrderItemStatus.SENT:
        return "orange"

      case OrderItemStatus.IN_PROGRESS:
        return "blue"

      case OrderItemStatus.READY:
        return "green"

      default:
        return "black"
    }
  }


  /**
   * Calcula el tiempo transcurrido desde la creación del pedido.
   */
  const getWaitingTime = (
    createdAt: string
  ) => {
    const created = new Date(createdAt).getTime()
    const now = Date.now()

    const diff = Math.max(
      0,
      Math.floor((now - created) / 1000)
    )

    const minutes = Math.floor(diff / 60)
    const seconds = diff % 60

    return `${minutes}:${seconds
      .toString()
      .padStart(2, "0")}`
  }


  /**
   * Inicializa la estación y la conexión WebSocket.
   */
  useEffect(() => {
    if (
      !Number.isInteger(station) ||
      station <= 0
    ) {
      return
    }

    localStorage.setItem(
      "kitchen_station_id",
      String(station)
    )

    wsService.connect()

    fetchStation()
  }, [station])


  /**
   * Mantiene actualizado el contador de espera.
   */
  useEffect(() => {
    const timer = setInterval(() => {
      setClock(current => current + 1)
    }, 1000)

    return () => {
      clearInterval(timer)
    }
  }, [])


  /**
   * Escucha eventos de cocina evitando múltiples
   * solicitudes simultáneas al backend.
   */
  useEffect(() => {
    if (
      !Number.isInteger(station) ||
      station <= 0
    ) {
      return
    }

    let fetching = false
    let pending = false


    const safeFetchItems = async () => {
      if (fetching) {
        pending = true
        return
      }

      fetching = true

      try {
        await fetchItems()
      } finally {
        fetching = false
      }

      if (pending) {
        pending = false
        await safeFetchItems()
      }
    }


    const listener = (
      event: WSEventParsed
    ) => {
      const { type, data } = event
      if (
        data &&
        typeof data === "object" &&
        "station_id" in data &&
        data.station_id != null &&
        Number(data.station_id) !== station
      ) {
        return
      }

      switch (type) {
        case WSEvent.NEW_ITEM:
        case WSEvent.ORDER_UPDATED:
        case WSEvent.ORDER_STATUS_CHANGED:
        case WSEvent.ITEM_STATUS_CHANGED:
          safeFetchItems()
          break
      }
    }

    safeFetchItems()

    wsService.subscribe(listener)

    return () => {
      wsService.unsubscribe(listener)
    }
  }, [station])


  const groupedOrders = items.reduce(
    (acc, item) => {
      if (!acc[item.order_id]) {
        acc[item.order_id] = {
          table: item.table_number,
          created_at: item.created_at,
          items: []
        }
      }

      acc[item.order_id].items.push(item)

      return acc
    },
    {} as Record<
      number,
      {
        table: number
        created_at: string
        items: KitchenItem[]
      }
    >
  )


  return (
    <div className="kitchen-page">

      <header className="kitchen-header">
        <div>
          <p>Cocina</p>

          <h1>
            {stationName}
          </h1>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={() =>
            navigate("/kitchen")
          }
        >
          Cambiar estación
        </button>
      </header>


      {items.length === 0 ? (
        <div className="kitchen-empty">
          <strong>
            No hay pedidos pendientes
          </strong>

          <span>
            Los nuevos pedidos aparecerán
            automáticamente.
          </span>
        </div>
      ) : (
        <div className="kitchen-orders">

          {Object.entries(
            groupedOrders
          ).map(
            ([orderId, order]) => (

              <article
                key={orderId}
                className="kitchen-order"
              >

                <header className="kitchen-order__header">

                  <h2>
                    Mesa {order.table}
                  </h2>

                  {order.created_at && (
                    <span className="kitchen-order__time">
                      ⏱{" "}
                      {getWaitingTime(
                        order.created_at
                      )}
                    </span>
                  )}

                </header>


                <div className="kitchen-order__items">

                  {order.items.map(item => (

                    <div
                      key={item.item_id}
                      className={
                        item.status ===
                        OrderItemStatus.SENT
                          ? "kitchen-item kitchen-item--new"
                          : "kitchen-item"
                      }
                    >

                      <div className="kitchen-item__info">

                        <div className="kitchen-item__product">
                          <strong>
                            {item.product_name}
                          </strong>

                          <span>
                            × {item.quantity}
                          </span>
                        </div>

                        {item.notes && (
                          <div className="kitchen-item-notes">
                            {item.notes}
                          </div>
                        )}

                      </div>

                      <span
                        className="kitchen-item__status"
                        style={{
                          backgroundColor:
                            getStatusColor(
                              item.status
                            )
                        }}
                      >
                        {orderItemStatusLabel(
                          item.status
                        )}
                      </span>


                      <div className="kitchen-item__action">

                        {item.status ===
                          OrderItemStatus.SENT && (
                          <button
                            type="button"
                            className="btn btn-kitchen-start"
                            onClick={() =>
                              updateStatus(
                                item.item_id,
                                OrderItemStatus.IN_PROGRESS
                              )
                            }
                          >
                            Iniciar
                          </button>
                        )}


                        {item.status ===
                          OrderItemStatus.IN_PROGRESS && (
                          <button
                            type="button"
                            className="btn btn-kitchen-ready"
                            onClick={() =>
                              updateStatus(
                                item.item_id,
                                OrderItemStatus.READY
                              )
                            }
                          >
                            Listo
                          </button>
                        )}

                        {item.status ===
                          OrderItemStatus.READY && (
                          <span className="kitchen-item__waiting-delivery">
                            Esperando entrega
                          </span>
                        )}

                      </div>

                    </div>

                  ))}

                </div>

              </article>

            )
          )}

        </div>
      )}

    </div>
  )
}