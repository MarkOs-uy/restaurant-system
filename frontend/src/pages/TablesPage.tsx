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
  active: boolean
  order_id?: number | null
  order_status?: string | null
  capacity: number
}

export default function TablesPage({ isAdmin }: { isAdmin: boolean }) {

  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  const [editMode, setEditMode] = useState(false)
  const [dragging, setDragging] = useState<number | null>(null)

  const [newTableForm, setNewTableForm] = useState({
    shape: "circle",
    capacity: 4
  })

  const [showForm, setShowForm] = useState(false)

  const [layout, setLayout] = useState({
    width: 900,
    height: 500
  })

  const TABLE_SIZE = 100
  const FLOOR_WIDTH = 900
  const FLOOR_HEIGHT = 500

  const loadTables = () => {
    fetch(`${API_URL}/tables/status`, { headers: getAuthHeaders() })
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
    if (!table.order_status) return "#bdc3c7"   // gris claro (libre)
    if (table.order_status === "OPEN") return "#f1c40f"   // amarillo
    if (table.order_status === "SENT") return "#e67e22"   // naranja
    if (table.order_status === "READY") return "#27ae60"  // verde fuerte
    if (table.order_status === "PAYING") return "#8e44ad" // violeta
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

    const res = await fetch(`${API_URL}/tables/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        x: 50,
        y: 50,
        shape: newTableForm.shape,
        capacity: newTableForm.capacity
      })
    })

    if (!res.ok) {
      alert("Error creando mesa")
      return
    }

    const table = await res.json()

    setTables(prev => [...prev, table])
    setShowForm(false)
  }


  const deleteTable = async (id: number) => {
    await fetch(`${API_URL}/tables/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    })
    setTables(prev => prev.filter(t => t.id !== id))
  }


  const activateTable = async (id: number) => {
    await fetch(`${API_URL}/tables/${id}/activate`, {
      method: "PATCH",
      headers: getAuthHeaders()
    })
    loadTables()
  }


  const inactiveTables = tables.filter(t => !t.active)
  
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

      <button onClick={() => setShowForm(true)}>
        + Mesa
      </button>

      <button onClick={() => navigate("/tables/manage")}>
        Administrar mesas
      </button>

      {editMode && (
        <div style={{
          background: "#fff3cd",
          color: "#856404",
          padding: "8px 12px",
          borderRadius: 6,
          marginTop: 10,
          marginBottom: 10,
          fontSize: 14
        }}>
          🛠 Modo edición activo — arrastrar mesas / click derecho elimina
        </div>
      )}

      {showForm && (
        <div style={{
          background: "#fff",
          padding: 15,
          borderRadius: 8,
          marginBottom: 10,
          color: "#111"
        }}>
          <h3>Nueva mesa</h3>

          <select
            value={newTableForm.shape}
            onChange={(e) =>
              setNewTableForm({ ...newTableForm, shape: e.target.value })
            }
          >
            <option value="circle">Redonda</option>
            <option value="square">Cuadrada</option>
            <option value="rectangle">Rectangular</option>
          </select>

          <input
            type="number"
            value={newTableForm.capacity}
            onChange={(e) =>
              setNewTableForm({ ...newTableForm, capacity: Number(e.target.value) })
            }
            style={{ marginLeft: 10 }}
          />

          <button onClick={createTable} style={{ marginLeft: 10 }}>
            Crear
          </button>

          <button onClick={() => setShowForm(false)} style={{ marginLeft: 10 }}>
            Cancelar
          </button>
        </div>
      )}

      <div
        style={{
          position: "relative",
          width: layout.width,
          height: layout.height,
          background: "#f5f5f5",
          borderRadius: 20,
          border: "2px solid #ddd",
          overflow: "hidden",
          margin: "0 auto",
          backgroundImage: `
            linear-gradient(#ddd 1px, transparent 1px),
            linear-gradient(90deg, #ddd 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
        }}
      >

        {tables.map(t => {

          const size = 60 + (t.capacity || 4) * 10
          let borderRadius = "12px"
          let width = size
          let height = size

          if (t.shape === "Circular") {
            borderRadius = "50%"
          }

          if (t.shape === "Rectangular") {
            width = size * 1.4
          }

          return (

            <div
              key={t.id}

              onClick={() => !editMode && touchTable(t.id)}

              onMouseEnter={(e) => {
                if (editMode) return
                e.currentTarget.style.transform = "scale(1.05)"
              }}

              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "scale(1)"
              }}

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

                let x = Math.round(e.clientX - rect.left - TABLE_SIZE / 2)
                let y = Math.round(e.clientY - rect.top - TABLE_SIZE / 2)

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
                width,
                height,
                borderRadius,
                background: getTableColor(t),
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
                fontWeight: "bold",
                cursor: dragging === t.id ? "grabbing" : editMode ? "grab" : "pointer",
                boxShadow: "0 4px 10px rgba(0,0,0,0.2)",
                userSelect: "none",
                transition: "0.1s"
              }}

            >
                <div style={{ textAlign: "center", color: "#fff" }}>
                  <div style={{ fontSize: 18, fontWeight: "bold" }}>
                    {t.number}
                  </div>

                  {t.order_status && (
                    <div style={{ fontSize: 10 }}>
                      {t.order_status}
                    </div>
                  )}
                </div>
            </div>

          )

        })}

      </div>

      {isAdmin && inactiveTables.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <h3>Mesas inactivas</h3>

          {inactiveTables.map(t => (
            <div key={t.id}>
              Mesa {t.number}

              <button onClick={() => activateTable(t.id)}>
                Reactivar
              </button>
            </div>
          ))}
        </div>
      )}

    </div>

  )

}