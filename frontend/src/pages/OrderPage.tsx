import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"

import { apiFetch } from "../api"

import type { OrderDetail } from "../types/order"


export default function OrderPage() {
  const { orderId } = useParams()
  const id = Number(orderId)

  const [order, setOrder] = useState<OrderDetail | null>(null)


  useEffect(() => {
    if (
      !Number.isInteger(id) ||
      id <= 0
    ) {
      return
    }

    const loadOrder = async () => {
      try {
        const data = await apiFetch<OrderDetail>(
          `/orders/${id}`
        )

        setOrder(data)
      } catch {
        // apiFetch ya muestra el error correspondiente.
      }
    }

    loadOrder()
  }, [id])


  if (!order) {
    return <h2>Cargando orden...</h2>
  }


  return (
    <div style={{ padding: 40 }}>
      <h1>Orden #{order.id}</h1>

      <h2>Mesa {order.table_number}</h2>

      <p>
        Estado: {order.status}
      </p>

      <h3>Items:</h3>

      {order.items.length === 0 && (
        <p>No hay productos aún</p>
      )}

      {order.items.map((item, index) => (
        <div key={index}>
          {item.product_name} × {item.quantity}
          {" - "}
          ${item.unit_price}
        </div>
      ))}

      <h2>
        Total: ${order.total}
      </h2>
    </div>
  )
}