import { useEffect, useState } from "react"

import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

import { showToast } from "../utils/showToast"

import type {
  Station,
  StationCreate,
  StationUpdate
} from "../types/station"


export default function StationsPage() {
  const [stations, setStations] =
    useState<Station[]>([])

  const [name, setName] =
    useState("")

  const [editingId, setEditingId] =
    useState<number | null>(null)


  /**
   * Carga todas las estaciones del restaurante,
   * tanto activas como inactivas.
   */
  const fetchStations = async () => {
    const [
      activeStations,
      inactiveStations
    ] = await Promise.all([
      apiFetch<Station[]>(
        "/stations/?active=true"
      ),
      apiFetch<Station[]>(
        "/stations/?active=false"
      )
    ])

    setStations([
      ...activeStations,
      ...inactiveStations
    ])
  }


  useEffect(() => {
    fetchStations()
  }, [])


  /**
   * Crea una nueva estación o actualiza
   * la estación actualmente en edición.
   */
  const saveStation = async () => {
    const trimmedName = name.trim()

    if (!trimmedName) {
      showToast(
        "Ingrese un nombre de estación"
      )
      return
    }

    if (editingId !== null) {
      const payload: StationUpdate = {
        name: trimmedName
      }

      await apiFetch(
        `/stations/${editingId}`,
        {
          method: "PATCH",
          body: payload
        }
      )
    } else {
      const payload: StationCreate = {
        name: trimmedName
      }

      await apiFetch(
        "/stations/",
        {
          method: "POST",
          body: payload
        }
      )
    }

    setName("")
    setEditingId(null)

    await fetchStations()
  }


  /**
   * Activa o desactiva una estación.
   */
  const toggleStation = async (
    id: number
  ) => {
    await apiFetch(
      `/stations/${id}/toggle`,
      {
        method: "PATCH"
      }
    )

    await fetchStations()
  }


  /**
   * Carga una estación en el formulario
   * para permitir su edición.
   */
  const editStation = (
    station: Station
  ) => {
    setEditingId(station.id)
    setName(station.name)
  }


  /**
   * Cancela la edición actual y limpia
   * el formulario.
   */
  const cancelEdit = () => {
    setEditingId(null)
    setName("")
  }

  return (
    <Page title="Estaciones">
      <Card>

        {/* Alta / edición */}
        <div className="admin-form-row">
          <input
            placeholder="Nombre de la estación"
            value={name}
            onChange={event =>
              setName(event.target.value)
            }
          />

          <button
            className="btn btn-primary"
            onClick={saveStation}
          >
            {editingId !== null
              ? "Actualizar"
              : "Crear"}
          </button>

          {editingId !== null && (
            <button
              className="btn btn-secondary"
              onClick={cancelEdit}
            >
              Cancelar
            </button>
          )}
        </div>


        <DataTable>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Estado</th>
              <th className="admin-actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            {stations.length === 0 && (
              <tr>
                <td
                  colSpan={3}
                  className="admin-table-empty"
                >
                  No hay estaciones
                </td>
              </tr>
            )}

            {stations.map(station => (
              <tr key={station.id}>
                <td>
                  <strong>
                    {station.name}
                  </strong>
                </td>

                <td>
                  <span
                    className={
                      station.active
                        ? "status-badge status-badge--active"
                        : "status-badge status-badge--inactive"
                    }
                  >
                    {station.active
                      ? "Activa"
                      : "Inactiva"}
                  </span>
                </td>

                <td>
                  <div className="admin-table-actions">

                    <button
                      className="btn btn-secondary"
                      onClick={() =>
                        editStation(station)
                      }
                    >
                      Editar
                    </button>

                    <button
                      className={
                        station.active
                          ? "btn btn-danger"
                          : "btn btn-success"
                      }
                      onClick={() =>
                        toggleStation(station.id)
                      }
                    >
                      {station.active
                        ? "Desactivar"
                        : "Activar"}
                    </button>

                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </DataTable>

      </Card>
    </Page>
  )
}