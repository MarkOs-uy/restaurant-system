import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { API_URL, getAuthHeaders } from "../api"

interface Table {
  id: number
  number: number
  x: number
  y: number
  shape: string
  status: string
  order_id?: number | null
  order_status?: string | null
}

export default function TablesPage() {

  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  const [editMode, setEditMode] = useState(false)
  const [dragging, setDragging] = useState<number | null>(null)

  const TABLE_SIZE = 100
  const FLOOR_WIDTH = 900
  const FLOOR_HEIGHT = 500

  const loadTables = () => {
    fetch(`${API_URL}/tables/`, { headers: getAuthHeaders() })
      .then(res => res.json())
      .then(data => {
        setTables(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error cargando mesas:", err)
        setLoading(false)
      })
  }

  useEffect(() => {

    loadTables()

    // refresco automático (muy útil en POS)
    const interval = setInterval(loadTables, 5000)

    return () => clearInterval(interval)

  }, [])

  const touchTable = async (tableId: number) => {

    const res = await fetch(`${API_URL}/tables/${tableId}/touch`, {
      method: "POST",
      headers: getAuthHeaders()
    })

    const data = await res.json()

    if (data.order_id) {
      navigate(`/orders/${data.order_id}`)
    } else {
      navigate(`/orders/table/${tableId}`)
    }

  }

  const getTableColor = (table: Table) => {

    if (!table.order_status) return "#dcdcdc" // libre

    if (table.order_status === "OPEN") return "#f1c40f"

    if (table.order_status === "SENT") return "#e67e22"

    if (table.order_status === "READY") return "#2ecc71"

    if (table.order_status === "PAYING") return "#9b59b6"

    return "#95a5a6"

  }

  const moveTable = (id: number, x: number, y: number) => {

    setTables(prev =>
      prev.map(t =>
        t.id === id ? { ...t, x, y } : t
      )
    )

  }

  const savePosition = async (tableId: number, x: number, y: number) => {

    await fetch(`${API_URL}/tables/${tableId}/position?x=${x}&y=${y}`, {
      method: "PATCH",
      headers: getAuthHeaders()
    })

  }

  const createTable = async () => {

    const number = tables.length + 1

    const res = await fetch(`${API_URL}/tables/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        number,
        x: 50,
        y: 50,
        shape: "round",
        capacity: 4
      })
    })

    const table = await res.json()

    setTables(prev => [...prev, table])

  }

  const deleteTable = async (id: number) => {

    await fetch(`${API_URL}/tables/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    })

    setTables(prev => prev.filter(t => t.id !== id))

  }

  if (loading) {
    return <p>Cargando mesas...</p>
  }

  return (

    <div style={{ padding: 20 }}>

      <button
        onClick={() => setEditMode(!editMode)}
        style={{ marginBottom: 20 }}
      >
        {editMode ? "Salir edición" : "Editar plano"}
      </button>

      <button onClick={createTable}>
        + Mesa
      </button>

      <div
        style={{
          position: "relative",
          width: FLOOR_WIDTH,
          height: FLOOR_HEIGHT,
          background: "#f5f5f5",
          borderRadius: 20,
          border: "2px solid #ddd",
          overflow: "hidden",
          margin: "0 auto"
        }}
      >

        {tables.map(t => {

          const borderRadius = t.shape === "square" ? "12px" : "50%"

          return (

            <div
              key={t.id}

              onClick={() => !editMode && touchTable(t.id)}

              onMouseDown={() => {
                if (!editMode) return
                setDragging(t.id)
              }}

              onMouseUp={() => {

                if (dragging === t.id) {
                  savePosition(t.id, t.x, t.y)
                }

                setDragging(null)

              }}

              onMouseMove={(e) => {

                if (dragging !== t.id) return

                const rect = e.currentTarget.parentElement!.getBoundingClientRect()

                let x = e.clientX - rect.left - TABLE_SIZE / 2
                let y = e.clientY - rect.top - TABLE_SIZE / 2

                x = Math.max(0, Math.min(FLOOR_WIDTH - TABLE_SIZE, x))
                y = Math.max(0, Math.min(FLOOR_HEIGHT - TABLE_SIZE, y))

                moveTable(t.id, x, y)

              }}

              onContextMenu={(e) => {

                e.preventDefault()

                if (!editMode) return

                deleteTable(t.id)

              }}

              style={{
                position: "absolute",
                left: t.x,
                top: t.y,
                width: TABLE_SIZE,
                height: TABLE_SIZE,
                borderRadius,
                background: getTableColor(t),
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
                fontWeight: "bold",
                cursor: editMode ? "grab" : "pointer",
                boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
                userSelect: "none"
              }}

            >
              {t.number}
            </div>

          )

        })}

      </div>

    </div>

  )

}