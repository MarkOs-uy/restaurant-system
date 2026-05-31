import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"
import { showToast } from "../utils/showToast"
import toast from "react-hot-toast"
import { wsService } from "../services/wsService"
import type { WSEventParsed } from "../ws"

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

const normalizeShape = (shape: string) => shape.split("-")[0]
const getRectangleOrientation = (shape: string) =>
  shape.endsWith("-vertical") ? "vertical" : "horizontal"
const rectangleShape = (orientation: "horizontal" | "vertical") =>
  `rectangle-${orientation}`

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
    orientation: "horizontal" as "horizontal" | "vertical",
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
    if (!table.order_status) return "#1e293b"   // Slate oscuro (libre)
    if (table.order_status === "OPEN") return "#f59e0b"   // Naranja/Amarillo cálido
    if (table.order_status === "SENT") return "#ef4444"   // Rojo vibrante
    if (table.order_status === "READY") return "#10b981"  // Verde esmeralda
    if (table.order_status === "PAYING") return "#8b5cf6" // Violeta místico
    return "#637381"
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
    const shape = normalizeShape(table.shape)
    const size = 60 + (table.capacity || 4) * 10
    const rectangleHeight = 100
    const rectangleWidth = 100 + (table.capacity || 4) * 16

    if (shape === "rectangle") {
      const isVertical = getRectangleOrientation(table.shape) === "vertical"
      return {
        width: isVertical ? rectangleHeight : rectangleWidth,
        height: isVertical ? rectangleWidth : rectangleHeight
      }
    }

    return {
      width: size,
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
        shape: newTableForm.shape === "rectangle"
          ? rectangleShape(newTableForm.orientation)
          : newTableForm.shape,
        capacity: newTableForm.capacity
      }
    })
    setTables(prev => [...prev, table])
    setNewTableForm({
      number: "",
      shape: "circle",
      orientation: "horizontal",
      capacity: 4
    })
    setShowForm(false)
  }

  const rotateTable = async (table: Table) => {
    if (normalizeShape(table.shape) !== "rectangle") return

    const nextOrientation =
      getRectangleOrientation(table.shape) === "vertical"
        ? "horizontal"
        : "vertical"

    const updated = await apiFetch(`/tables/${table.id}`, {
      method: "PATCH",
      body: {
        shape: rectangleShape(nextOrientation)
      }
    })

    setTables(prev =>
      prev.map(t =>
        t.id === table.id
          ? { ...t, shape: updated.shape }
          : t
      )
    )
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
  }, [])

  useEffect(() => {
    const relevantEvents = new Set([
      "ORDER_UPDATED",
      "ORDER_STATUS_CHANGED",
      "ORDER_CLOSED",
      "ITEM_STATUS_CHANGED",
      "PAYMENT_ADDED",
      "PAYMENT_DELETED",
      "TABLE_CREATED",
      "TABLE_UPDATED",
      "TABLE_POSITION_UPDATED",
      "TABLE_ACTIVATED",
      "TABLE_DEACTIVATED",
      "LAYOUT_UPDATED"
    ])

    const handler = ({ type }: WSEventParsed) => {
      if (!relevantEvents.has(type)) return

      if (type === "LAYOUT_UPDATED") {
        loadLayout()
      }

      loadTables()
    }

    wsService.subscribe(handler)
    return () => {
      wsService.unsubscribe(handler)
    }
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
            style={{ width: 80 }}
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
              setNewTableForm({
                ...newTableForm,
                shape: e.target.value
              })
            }
          >
            <option value="circle">Circular</option>
            <option value="square">Cuadrada</option>
            <option value="rectangle">Rectangular</option>
          </select>

          {newTableForm.shape === "rectangle" && (
            <select
              value={newTableForm.orientation}
              onChange={(e) =>
                setNewTableForm({
                  ...newTableForm,
                  orientation: e.target.value as "horizontal" | "vertical"
                })
              }
              style={{ marginLeft: 10 }}
            >
              <option value="horizontal">Horizontal</option>
              <option value="vertical">Vertical</option>
            </select>
          )}

          <input
            type="number"
            value={newTableForm.capacity}
            onChange={(e) =>
              setNewTableForm({ ...newTableForm, capacity: Number(e.target.value) })
            }
            style={{ marginLeft: 10 }}
          />

          <button onClick={createTable} style={{ marginLeft: 10, background: "#0c0f17" }}>
            Crear
          </button>

          <button onClick={() => setShowForm(false)} style={{ marginLeft: 10, background: "#0c0f17" }}>
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
          background: "#0c0f17",
          borderRadius: 20,
          border: "1px solid var(--color-border)",
          overflow: "hidden",
          margin: "0 auto",
          backgroundImage: `
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: `${layout.grid_size}px ${layout.grid_size}px`,
          boxShadow: "var(--shadow-lg), var(--shadow-glass)"
        }}
      >

        {tables.filter(t => t.active).map(t => {

          let borderRadius = "12px"
          const { width, height } = getTableDimensions(t)

          const normalizedShape = normalizeShape(t.shape)

          if (normalizedShape === "circle") {
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
                border: t.order_status ? "none" : "1px dashed rgba(255, 255, 255, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
                fontWeight: "bold",
                cursor: dragging === t.id ? "grabbing" : editMode ? "grab" : "pointer",
                boxShadow: dragging === t.id 
                  ? "var(--shadow-lg)" 
                  : `0 6px 20px rgba(0,0,0,0.35), 0 0 12px ${getTableColor(t)}2b, inset 0 1px 1px rgba(255, 255, 255, 0.08)`,
                userSelect: "none",
                touchAction: "none",
                transition: dragging === t.id ? "none" : "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
              }}

            >
                {editMode && normalizedShape === "rectangle" && (
                  <button
                    onPointerDown={(e) => e.stopPropagation()}
                    onClick={(e) => {
                      e.stopPropagation()
                      rotateTable(t)
                    }}
                    title="Girar mesa"
                    style={{
                      position: "absolute",
                      top: -10,
                      right: -10,
                      width: 28,
                      height: 28,
                      padding: 0,
                      borderRadius: "50%",
                      fontSize: 16,
                      zIndex: 2
                    }}
                  >
                    ↻
                  </button>
                )}

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
                  <td>{normalizeShape(t.shape)}</td>
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
