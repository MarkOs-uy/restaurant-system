import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"
import { showToast } from "../utils/showToast"
import toast from "react-hot-toast"

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

interface InactiveTable {
  id: number
  number: number
  capacity: number
  shape: string
  active: boolean
}

interface DragState {
  id: number
  offsetX: number
  offsetY: number
  width: number
  height: number
  x: number
  y: number
}

export default function TablesPage({ isAdmin }: { isAdmin: boolean }) {

  const [tables, setTables] = useState<Table[]>([])
  const [inactiveTables, setInactiveTables] = useState<InactiveTable[]>([])
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  const [editMode, setEditMode] = useState(false)
  const [dragging, setDragging] = useState<number | null>(null)

  const [newTableForm, setNewTableForm] = useState({
    number: "",
    shape: "circle",
    capacity: 4
  })

  const [showForm, setShowForm] = useState(false)
  const positionTimers = useRef<Record<number, any>>({})
  const floorRef = useRef<HTMLDivElement | null>(null)
  const draggingRef = useRef<DragState | null>(null)

  const [layout, setLayout] = useState({
    width: 900,
    height: 500,
    grid_size: 40,
    snap_to_grid: true
  })

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
    if (draggingRef.current) return
    try {
      const [activeData, inactiveData] = await Promise.all([
        apiFetch("/tables/status"),
        apiFetch("/tables/?active=false")
      ])
      setTables(activeData)
      setInactiveTables(inactiveData)
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
      const updatedPosition = await apiFetch(`/tables/${tableId}/position`, {
        method: "PATCH",
        body: { x, y }
      })
      moveTable(updatedPosition.id, updatedPosition.x, updatedPosition.y)
    }, 300)
  }

  const getNextAvailableTableNumber = () => {
    const usedNumbers = new Set([
      ...tables.map(t => t.number),
      ...inactiveTables.map(t => t.number)
    ])
    let number = 1
    while (usedNumbers.has(number)) {
      number += 1
    }
    return number
  }

  const getTableDimensions = (table: Pick<Table, "capacity" | "shape">) => {
    const size = 60 + (table.capacity || 4) * 10
    return {
      width: table.shape === "rectangle" ? size * 1.4 : size,
      height: size
    }
  }

  // -------------------------
  // Crear nueva mesa con forma y capacidad seleccionada en el formulario
  // -------------------------

  const createTable = async () => {
    const number = Number(newTableForm.number)
    const usedNumbers = new Set([
      ...tables.map(t => t.number),
      ...inactiveTables.map(t => t.number)
    ])

    if (!Number.isInteger(number) || number <= 0) {
      showToast("Ingresá un número de mesa válido")
      return
    }

    if (usedNumbers.has(number)) {
      showToast(`La mesa ${number} ya está asignada`)
      return
    }

    const table = await apiFetch("/tables/", {
      method: "POST",
      body: {
        number,
        x: 50,
        y: 50,
        shape: newTableForm.shape,
        capacity: newTableForm.capacity
      }
    })
    setTables(prev => [...prev, table])
    setNewTableForm({
      number: "",
      shape: "circle",
      capacity: 4
    })
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
    await loadTables()
  }

  const requestDeleteTable = (table: Table) => {
    toast.custom((t) => (
      <div
        style={{
          background: "#1e1e1e",
          color: "white",
          padding: 16,
          borderRadius: 8,
          border: "1px solid #444",
          width: 320,
          boxShadow: "0 8px 24px rgba(0,0,0,0.35)"
        }}
      >
        <strong>Eliminar mesa {table.number}?</strong>
        <p style={{ margin: "8px 0 14px", opacity: 0.8 }}>
          La mesa quedará inactiva y podrás reactivarla luego.
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={() => toast.dismiss(t.id)}
            style={{ flex: 1, padding: 10, borderRadius: 6 }}
          >
            Cancelar
          </button>
          <button
            onClick={async () => {
              toast.dismiss(t.id)
              try {
                await deleteTable(table.id)
                toast.success(`Mesa ${table.number} eliminada`)
              } catch (err: any) {
                alert(err.message)
              }
            }}
            style={{
              flex: 1,
              padding: 10,
              borderRadius: 6,
              background: "#c62828",
              color: "white"
            }}
          >
            Eliminar
          </button>
        </div>
      </div>
    ))
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


  useEffect(() => {
    loadLayout()
    loadTables()
    const interval = setInterval(loadTables, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handlePointerMove = (e: PointerEvent) => {
      const drag = draggingRef.current
      const floor = floorRef.current
      if (!drag || !floor) return

      const rect = floor.getBoundingClientRect()
      let x = Math.round(e.clientX - rect.left - drag.offsetX)
      let y = Math.round(e.clientY - rect.top - drag.offsetY)

      if (layout.snap_to_grid) {
        const grid = layout.grid_size || 40
        x = Math.round(x / grid) * grid
        y = Math.round(y / grid) * grid
      }

      x = Math.max(0, Math.min(layout.width - drag.width, x))
      y = Math.max(0, Math.min(layout.height - drag.height, y))

      draggingRef.current = { ...drag, x, y }
      moveTable(drag.id, x, y)
    }

    const handlePointerUp = () => {
      const drag = draggingRef.current
      if (drag) {
        savePosition(drag.id, drag.x, drag.y)
      }
      draggingRef.current = null
      setDragging(null)
    }

    window.addEventListener("pointermove", handlePointerMove)
    window.addEventListener("pointerup", handlePointerUp)
    return () => {
      window.removeEventListener("pointermove", handlePointerMove)
      window.removeEventListener("pointerup", handlePointerUp)
    }
  }, [layout])

  if (loading) {
    return <p>Cargando mesas...</p>
  }

  return (

    <div style={{ padding: 20 }}>
      {isAdmin && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 12,
            marginBottom: 16,
            flexWrap: "wrap"
          }}
        >
          <button
            onClick={() => setEditMode(!editMode)}
          >
            {editMode ? "Salir edición" : "Editar plano"}
          </button>

          <button
            onClick={() => {
              setNewTableForm({
                ...newTableForm,
                number: String(getNextAvailableTableNumber())
              })
              setShowForm(true)
            }}
          >
            + Mesa
          </button>

          <button onClick={() => navigate("/tables/manage")}>
            Administrar mesas
          </button>
        </div>
      )}

      {isAdmin && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 12,
            marginBottom: 10,
            flexWrap: "wrap"
          }}
        >

          Plano:

          <input
            type="number"
            value={layout.width}
            onChange={(e) =>
              setLayout({ ...layout, width: Number(e.target.value) })
            }
            style={{ width: 80 }}
          />

          x

          <input
            type="number"
            value={layout.height}
            onChange={(e) =>
              setLayout({ ...layout, height: Number(e.target.value) })
            }
            style={{ width: 80 }}
          />

          Grid:

          <input
            type="number"
            value={layout.grid_size}
            onChange={(e) =>
              setLayout({ ...layout, grid_size: Number(e.target.value) })
            }
            style={{ width: 60 }}
          />

          <label
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6
            }}
          >
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

          <input
            type="number"
            min="1"
            placeholder="Número"
            value={newTableForm.number}
            onChange={(e) =>
              setNewTableForm({ ...newTableForm, number: e.target.value })
            }
            style={{ width: 90, marginRight: 10 }}
          />

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
        ref={floorRef}
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

          let borderRadius = "12px"
          const { width, height } = getTableDimensions(t)

          if (t.shape === "circle") {
            borderRadius = "50%"
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

              onPointerDown={(e) => {
                if (!editMode) return
                e.preventDefault()
                const tableRect = e.currentTarget.getBoundingClientRect()
                setDragging(t.id)
                draggingRef.current = {
                  id: t.id,
                  offsetX: e.clientX - tableRect.left,
                  offsetY: e.clientY - tableRect.top,
                  width,
                  height,
                  x: t.x,
                  y: t.y
                }
              }}

              onContextMenu={(e) => {

                e.preventDefault()

                if (!editMode) return

                requestDeleteTable(t)

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
                touchAction: "none",
                transition: dragging === t.id ? "none" : "transform 0.1s"
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
