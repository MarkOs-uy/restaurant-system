import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { apiFetch } from "../api"

import type {
  Table,
  TableUpdate
} from "../types/table"

import { TableShape } from "../types/table"


export default function ManageTables() {
  const navigate = useNavigate()

  const [tables, setTables] =
    useState<Table[]>([])

  const [originalTables, setOriginalTables] =
    useState<Table[]>([])


  /**
   * Recupera todas las mesas del restaurante,
   * tanto activas como inactivas.
   */
  const loadTables = async () => {
    const [
      activeTables,
      inactiveTables
    ] = await Promise.all([
      apiFetch<Table[]>(
        "/tables/?active=true"
      ),
      apiFetch<Table[]>(
        "/tables/?active=false"
      )
    ])

    const data = [
      ...activeTables,
      ...inactiveTables
    ]

    setTables(data)
    setOriginalTables(data)
  }


  useEffect(() => {
    loadTables()
  }, [])


  const activeTables =
    tables.filter(table => table.active)

  const inactiveTables =
    tables.filter(table => !table.active)


  /**
   * Determina si una mesa tiene modificaciones
   * pendientes respecto de los datos originales.
   */
  const hasChanges = (
    table: Table
  ) => {
    const original =
      originalTables.find(
        item => item.id === table.id
      )

    if (!original) {
      return false
    }

    return (
      original.number !== table.number ||
      original.capacity !== table.capacity ||
      original.shape !== table.shape ||
      original.active !== table.active
    )
  }


  /**
   * Persiste los datos editables de una mesa.
   */
  const updateTable = async (
    table: Table
  ) => {
    if (
      !Number.isInteger(table.number) ||
      table.number <= 0
    ) {
      alert("Número de mesa inválido")
      return
    }

    if (
      !Number.isInteger(table.capacity) ||
      table.capacity <= 0
    ) {
      alert("Capacidad inválida")
      return
    }

    const repeated =
      tables.some(
        other =>
          other.id !== table.id &&
          other.number === table.number
      )

    if (repeated) {
      alert(
        `Ya existe una mesa con el número ${table.number}`
      )
      return
    }

    const payload: TableUpdate = {
      number: table.number,
      capacity: table.capacity,
      shape: table.shape,
      active: table.active
    }

    await apiFetch(
      `/tables/${table.id}`,
      {
        method: "PATCH",
        body: payload
      }
    )

    await loadTables()
  }


  /**
   * Actualiza localmente un campo editable de una mesa
   * sin persistir todavía el cambio.
   */
  const updateField = <
    K extends keyof Table
  >(
    id: number,
    field: K,
    value: Table[K]
  ) => {
    setTables(current =>
      current.map(table =>
        table.id === id
          ? {
              ...table,
              [field]: value
            }
          : table
      )
    )
  }

    return (
    <div style={{ padding: 20 }}>

        <button onClick={() => navigate("/")}>
        ← Volver al plano
        </button>

        <h1>Administrar mesas</h1>

        <h2 style={{ marginTop: 20 }}>Mesas activas</h2>

        <table style={{ width: "100%", textAlign: "center" }}>
        <thead>
            <tr>
                <th style={{ width: 120, textAlign: "center" }}>Número</th>
                <th style={{ width: 120, textAlign: "center" }}>Capacidad</th>
                <th style={{ width: 120, textAlign: "center" }}>Forma</th>
                <th style={{ width: 120, textAlign: "center" }}>Activa</th>
                <th style={{ width: 120, textAlign: "center" }}></th>
            </tr>
        </thead>

        <tbody>
            {activeTables.length === 0 && (
                <tr>
                    <td colSpan={5}>No hay mesas activas</td>
                </tr>
            )}
            {activeTables.map((t) => (
            <tr key={t.id}>

                <td>
                    <input
                        type="number"
                        value={t.number}
                        style={{ textAlign: "center", width: 60 }}
                        onChange={(e) =>
                            updateField(t.id, "number", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                    <input
                        type="number"
                        value={t.capacity}
                        style={{ textAlign: "center", width: 60 }}
                        onChange={(e) =>
                            updateField(t.id, "capacity", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                <select
                    value={t.shape}
                    style={{ textAlign: "center" }}
                    onChange={(e) =>
                    updateField(
                        t.id,
                        "shape",
                        e.target.value as TableShape
                    )
                    }
                >
                    <option value={TableShape.CIRCLE}>
                    Circular
                    </option>

                    <option value={TableShape.SQUARE}>
                    Cuadrada
                    </option>

                    <option value={TableShape.RECTANGLE_HORIZONTAL}>
                    Rectangular horizontal
                    </option>

                    <option value={TableShape.RECTANGLE_VERTICAL}>
                    Rectangular vertical
                    </option>
                </select>
                </td>

                <td style={{ textAlign: "center" }}>
                <input
                    type="checkbox"
                    checked={t.active}
                    onChange={(e) =>
                    updateField(t.id, "active", e.target.checked)
                    }
                />
                </td>

                <td>
                <button
                    onClick={() => updateTable(t)}
                    disabled={!hasChanges(t)}
                    style={{
                        opacity: hasChanges(t) ? 1 : 0.5,
                        cursor: hasChanges(t) ? "pointer" : "not-allowed"
                    }}
                >
                    Guardar
                </button>
                </td>

            </tr>
            ))}
        </tbody>
        </table>


        <h2 style={{ marginTop: 30 }}>Mesas inactivas</h2>

        <table style={{ width: "100%", textAlign: "center" }}>
        <thead>
            <tr>
                <th style={{ width: 120, textAlign: "center" }}>Número</th>
                <th style={{ width: 120, textAlign: "center" }}>Capacidad</th>
                <th style={{ width: 120, textAlign: "center" }}>Forma</th>
                <th style={{ width: 120, textAlign: "center" }}>Activa</th>
                <th style={{ width: 120, textAlign: "center" }}></th>
            </tr>
        </thead>

        <tbody>
            {inactiveTables.length === 0 && (
                <tr>
                    <td colSpan={5}>No hay mesas inactivas</td>
                </tr>
            )}
            {inactiveTables.map((t) => (
            <tr key={t.id}>

                <td>
                    <input
                        type="number"
                        value={t.number}
                        style={{ textAlign: "center", width: 60 }}
                        onChange={(e) =>
                            updateField(t.id, "number", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                    <input
                        type="number"
                        style={{ textAlign: "center", width: 60 }}
                        value={t.capacity}
                        onChange={(e) =>
                        updateField(t.id, "capacity", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                    <select
                        value={t.shape}
                        style={{ textAlign: "center" }}
                        onChange={(e) =>
                        updateField(
                            t.id,
                            "shape",
                            e.target.value as TableShape
                        )
                        }
                    >
                        <option value={TableShape.CIRCLE}>
                        Circular
                        </option>

                        <option value={TableShape.SQUARE}>
                        Cuadrada
                        </option>

                        <option value={TableShape.RECTANGLE_HORIZONTAL}>
                        Rectangular horizontal
                        </option>

                        <option value={TableShape.RECTANGLE_VERTICAL}>
                        Rectangular vertical
                        </option>
                    </select>
                </td>

                <td style={{ textAlign: "center" }}>
                    <input
                        type="checkbox"
                        checked={t.active}
                        onChange={(e) =>
                        updateField(t.id, "active", e.target.checked)
                        }
                    />
                </td>

                <td>
                    <button
                        onClick={() => updateTable(t)}
                        disabled={!hasChanges(t)}
                        style={{
                            opacity: hasChanges(t) ? 1 : 0.5,
                            cursor: hasChanges(t) ? "pointer" : "not-allowed"
                        }}
                    >
                        Guardar
                    </button>
                </td>

            </tr>
            ))}
        </tbody>
        </table>

    </div>
    )
}
