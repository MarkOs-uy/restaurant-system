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
      original.shape !== table.shape
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
      shape: table.shape
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
   * Activa o desactiva una mesa y persiste
   * inmediatamente el cambio.
   */
  const toggleTableActive = async (
    table: Table,
    active: boolean
  ) => {
    const payload: TableUpdate = {
      active
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
    <main className="manage-tables-page">

      <div className="manage-tables-header">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => navigate("/")}
        >
          ← Volver al plano
        </button>

        <div>
          <p>Configuración</p>
          <h1>Administrar mesas</h1>
        </div>
      </div>


      {/* MESAS ACTIVAS */}
      <section className="manage-tables-section">

        <div className="manage-tables-section__header">
          <h2>Mesas activas</h2>

          <span>
            {activeTables.length}
          </span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table manage-tables-table">

            <thead>
              <tr>
                <th>Número</th>
                <th>Capacidad</th>
                <th>Forma</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>

              {activeTables.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="admin-table-empty"
                  >
                    No hay mesas activas
                  </td>
                </tr>
              )}

              {activeTables.map(table => {
                const changed = hasChanges(table)

                return (
                  <tr
                    key={table.id}
                    className={
                      changed
                        ? "manage-table-row manage-table-row--changed"
                        : "manage-table-row"
                    }
                  >
                    <td>
                      <input
                        className="manage-table-number"
                        type="number"
                        value={table.number}
                        onChange={event =>
                          updateField(
                            table.id,
                            "number",
                            Number(event.target.value)
                          )
                        }
                      />
                    </td>

                    <td>
                      <input
                        className="manage-table-number"
                        type="number"
                        value={table.capacity}
                        onChange={event =>
                          updateField(
                            table.id,
                            "capacity",
                            Number(event.target.value)
                          )
                        }
                      />
                    </td>

                    <td>
                      <select
                        value={table.shape}
                        onChange={event =>
                          updateField(
                            table.id,
                            "shape",
                            event.target.value as TableShape
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

                    <td>
                      <label className="manage-table-active">
                        <input
                          type="checkbox"
                          checked={table.active}
                          onChange={event =>
                            void toggleTableActive(
                              table,
                              event.target.checked
                            )
                          }
                        />

                        <span>
                          Activa
                        </span>
                      </label>
                    </td>

                    <td>
                      <button
                        type="button"
                        className={
                          changed
                            ? "btn btn-primary manage-table-save"
                            : "btn btn-secondary manage-table-save"
                        }
                        onClick={() =>
                          updateTable(table)
                        }
                        disabled={!changed}
                      >
                        {changed
                          ? "Guardar cambios"
                          : "Guardado"}
                      </button>
                    </td>
                  </tr>
                )
              })}

            </tbody>

          </table>
        </div>

      </section>


      {/* MESAS INACTIVAS */}
      <section className="manage-tables-section">

        <div className="manage-tables-section__header">
          <h2>Mesas inactivas</h2>

          <span>
            {inactiveTables.length}
          </span>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table manage-tables-table">

            <thead>
              <tr>
                <th>Número</th>
                <th>Capacidad</th>
                <th>Forma</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>

              {inactiveTables.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="admin-table-empty"
                  >
                    No hay mesas inactivas
                  </td>
                </tr>
              )}

              {inactiveTables.map(table => {
                const changed = hasChanges(table)

                return (
                  <tr
                    key={table.id}
                    className={
                      changed
                        ? "manage-table-row manage-table-row--changed"
                        : "manage-table-row manage-table-row--inactive"
                    }
                  >
                    <td>
                      <input
                        className="manage-table-number"
                        type="number"
                        value={table.number}
                        onChange={event =>
                          updateField(
                            table.id,
                            "number",
                            Number(event.target.value)
                          )
                        }
                      />
                    </td>

                    <td>
                      <input
                        className="manage-table-number"
                        type="number"
                        value={table.capacity}
                        onChange={event =>
                          updateField(
                            table.id,
                            "capacity",
                            Number(event.target.value)
                          )
                        }
                      />
                    </td>

                    <td>
                      <select
                        value={table.shape}
                        onChange={event =>
                          updateField(
                            table.id,
                            "shape",
                            event.target.value as TableShape
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

                    <td>
                      <label className="manage-table-active">
                        <input
                          type="checkbox"
                          checked={table.active}
                          onChange={event =>
                            void toggleTableActive(
                              table,
                              event.target.checked
                            )
                          }
                        />

                        <span>
                          Inactiva
                        </span>
                      </label>
                    </td>

                    <td>
                      <button
                        type="button"
                        className={
                          changed
                            ? "btn btn-primary manage-table-save"
                            : "btn btn-secondary manage-table-save"
                        }
                        onClick={() =>
                          updateTable(table)
                        }
                        disabled={!changed}
                      >
                        {changed
                          ? "Guardar cambios"
                          : "Guardado"}
                      </button>
                    </td>
                  </tr>
                )
              })}

            </tbody>

          </table>
        </div>

      </section>

    </main>
  )
}
