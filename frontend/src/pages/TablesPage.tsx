import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"
import { showToast } from "../utils/showToast"

interface Table {
  id: number
  number: number
  x: number
  y: number
  capacity: number
  shape: string
  status: string
  active: boolean
  order_id?: number | null
  order_status?: string | null
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
  const positionTimers = useRef<Record<number, any>>({})

  const [layout, setLayout] = useState({
    width: 900,
    height: 500,
    grid_size: 40,
    snap_to_grid: true
  })

  const TABLE_SIZE = 100

  // -------------------------
  // Cargar layout y mesas
  // -------------------------

  const loadLayout = async () => {
    const data = await apiFetch(`/layout/`)
    setLayout(data)
  }

  // -------------------------
  // Salvar layout (tamaño, grid, snap)
  // -------------------------

  const saveLayout = async () => {
    await apiFetch("/layout/", {
      method: "PATCH",
      body: layout
    })
    showToast("Layout guardado")
  }

  // -------------------------
  // Cargar mesas y sus estados
  // -------------------------

  const loadTables = async () => {
    try {
      const data = await apiFetch("/tables/status")
      setTables(data)
    } finally {
      setLoading(false)
    }
  }

  // -------------------------
  // Tocar mesa: si tiene orden abierta, ir a la orden. Si no, crear nueva orden para esa mesa
  // -------------------------

  const touchTable = async (tableId: number) => {
    const data = await apiFetch(`/tables/${tableId}/touch`, {
      method: "POST"
    })
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

  // -------------------------
  // Mover mesa (modo edición): actualizar posición en backend al soltar
  // -------------------------

  const moveTable = (id: number, x: number, y: number) => {
    setTables(prev =>
      prev.map(t =>
        t.id === id ? { ...t, x, y } : t
      )
    )
  }

  // -------------------------
  // Salvar nueva posición de la mesa al soltar
  // -------------------------

  const savePosition = (tableId: number, x: number, y: number) => {
    if (positionTimers.current[tableId]) {
      clearTimeout(positionTimers.current[tableId])
    }
    positionTimers.current[tableId] = setTimeout(async () => {
      await apiFetch(`/tables/${tableId}/position?x=${x}&y=${y}`, {
        method: "PATCH",
      })
    }, 300)
  }

  // -------------------------
  // Crear nueva mesa con forma y capacidad seleccionada en el formulario
  // -------------------------

  const createTable = async () => {
    const table = await apiFetch("/tables/", {
      method: "POST",
      body: {
        x: 50,
        y: 50,
        shape: newTableForm.shape,
        capacity: newTableForm.capacity
      }
    })
    setTables(prev => [...prev, table])
    setShowForm(false)
  }

  // -------------------------
  // Eliminar mesa (modo edición, click derecho)
  // -------------------------

  const deleteTable = async (id: number) => {
    await apiFetch(`/tables/${id}`, {
      method: "DELETE"
    })
    setTables(prev => prev.filter(t => t.id !== id))
  }

  // -------------------------
  // Reactivar mesa inactiva desde la tabla de mesas inactivas
  // -------------------------

  const activateTable = async (id: number) => {
    await apiFetch(`/tables/${id}/activate`, {
      method: "PATCH"
    })
    await loadTables()
  }


  const inactiveTables = tables.filter(t => !t.active)
  
  useEffect(() => {
    loadLayout()
    loadTables()
    const interval = setInterval(loadTables, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <p>Cargando mesas...</p>
  }

  return (

    <div style={{ padding: 20 }}>
      {isAdmin && (
        <>
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
        </>
      )}

      {isAdmin && (
        <div style={{ marginBottom: 10 }}>

          Plano:

          <input
            type="number"
            value={layout.width}
            onChange={(e) =>
              setLayout({ ...layout, width: Number(e.target.value) })
            }
            style={{ width: 80, marginLeft: 10 }}
          />

          x

          <input
            type="number"
            value={layout.height}
            onChange={(e) =>
              setLayout({ ...layout, height: Number(e.target.value) })
            }
            style={{ width: 80, marginLeft: 10 }}
          />

          Grid:

          <input
            type="number"
            value={layout.grid_size}
            onChange={(e) =>
              setLayout({ ...layout, grid_size: Number(e.target.value) })
            }
            style={{ width: 60, marginLeft: 10 }}
          />

          <label style={{ marginLeft: 20 }}>
            <input
              type="checkbox"
              checked={layout.snap_to_grid}
              onChange={(e) =>
                setLayout({ ...layout, snap_to_grid: e.target.checked })
              }
            />
            Snap
          </label>

          <button
            onClick={saveLayout}
            style={{ marginLeft: 15 }}
          >
            Guardar
          </button>
        </div>
      )}

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
            <option value="circle">Circular</option>
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
          backgroundSize: `${layout.grid_size}px ${layout.grid_size}px`
        }}
      >

        {tables.filter(t => t.active).map(t => {

          const size = 60 + (t.capacity || 4) * 10
          let borderRadius = "12px"
          let width = size
          let height = size

          if (t.shape === "circle") {
            borderRadius = "50%"
          }

          if (t.shape === "rectangle") {
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

                if (layout.snap_to_grid) {
                  const GRID = layout.grid_size || 40
                  x = Math.round(x / GRID) * GRID
                  y = Math.round(y / GRID) * GRID
                }

                x = Math.max(0, Math.min(layout.width - TABLE_SIZE, x))
                y = Math.max(0, Math.min(layout.height - TABLE_SIZE, y))

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

          <table style={{ width: 400, textAlign: "center" }}>
            <thead>
              <tr>
                <th>Número</th>
                <th>Forma</th>
                <th>Capacidad</th>
                <th></th>
              </tr>
            </thead>

            <tbody>

              {inactiveTables.map(t => (

                <tr key={t.id}>
                  <td>{t.number}</td>
                  <td>{t.shape}</td>
                  <td>{t.capacity}</td>

                  <td>
                    <button onClick={() => activateTable(t.id)}>
                      Reactivar
                    </button>
                  </td>
                </tr>

              ))}

            </tbody>

          </table>

        </div>
      )}

    </div>

  )

}