import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { apiFetch } from "../api"
import { wsService } from "../services/wsService"

import { OrderItemStatus } from "../types/orderItemStatus"
import { WSEvent } from "../types/webSocketEvents"

import type { KitchenItem } from "../types/kitchen"
import type { Station } from "../types/station"
import type { WSEventParsed } from "../ws"


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
    <div style={{ padding: 40 }}>
      <h1>
        Estación: {stationName}
      </h1>

      <button
        onClick={() => navigate("/kitchen")}
        style={{ marginBottom: 20 }}
      >
        Cambiar estación
      </button>

      {items.length === 0 && (
        <p>No hay pedidos pendientes</p>
      )}

      {Object.entries(groupedOrders).map(
        ([orderId, order]) => (
          <div
            key={orderId}
            className="card"
            style={{
              border:
                "1px solid var(--color-border)",
              marginBottom: 20,
              background:
                "rgba(22, 28, 45, 0.4)",
              boxShadow: "var(--shadow-md)"
            }}
          >
            <h2
              style={{
                fontSize: 28,
                marginBottom: 10
              }}
            >
              Mesa {order.table}

              {order.created_at && (
                <span
                  style={{
                    marginLeft: 15,
                    fontSize: 16,
                    fontWeight: "normal",
                    color:
                      "var(--color-text-secondary)"
                  }}
                >
                  ⏱ {getWaitingTime(
                    order.created_at
                  )}
                </span>
              )}
            </h2>

            {order.items.map(item => (
              <div
                key={item.item_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "space-between",
                  marginBottom: 12,
                  padding: 12,
                  border:
                    "1px solid var(--color-border)",
                  borderRadius: 6,
                  background:
                    item.status ===
                    OrderItemStatus.SENT
                      ? "rgba(245, 158, 11, 0.12)"
                      : "rgba(255, 255, 255, 0.02)",
                  color:
                    "var(--color-text-primary)"
                }}
              >
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 600
                  }}
                >
                  {item.product_name} ×{" "}
                  {item.quantity}
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: 10,
                    alignItems: "center"
                  }}
                >
                  <strong
                    style={{
                      background:
                        getStatusColor(
                          item.status
                        ),
                      color: "white",
                      padding: "6px 12px",
                      borderRadius: 6,
                      fontSize: 14
                    }}
                  >
                    {item.status}
                  </strong>

                  {item.status ===
                    OrderItemStatus.SENT && (
                    <button
                      style={{
                        fontSize: 16,
                        padding: "8px 14px"
                      }}
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
                      style={{
                        fontSize: 16,
                        padding: "8px 14px"
                      }}
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
                    <button
                      style={{
                        fontSize: 16,
                        padding: "8px 14px"
                      }}
                      onClick={() =>
                        updateStatus(
                          item.item_id,
                          OrderItemStatus.DELIVERED
                        )
                      }
                    >
                      Entregado
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  )
}