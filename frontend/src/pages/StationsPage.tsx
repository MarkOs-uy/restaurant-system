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
        <div style={{ marginBottom: 20 }}>
          <input
            placeholder="Nombre estación"
            value={name}
            onChange={event =>
              setName(event.target.value)
            }
          />

          <button
            className="btn btn-primary"
            onClick={saveStation}
            style={{ marginLeft: 10 }}
          >
            {editingId !== null
              ? "Actualizar"
              : "Crear"}
          </button>

          {editingId !== null && (
            <button
              className="btn btn-primary"
              onClick={cancelEdit}
              style={{ marginLeft: 10 }}
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
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            {stations.length === 0 && (
              <tr>
                <td colSpan={3}>
                  No hay estaciones
                </td>
              </tr>
            )}

            {stations.map(station => (
              <tr key={station.id}>
                <td>{station.name}</td>

                <td>
                  {station.active
                    ? "Activa"
                    : "Inactiva"}
                </td>

                <td>
                  <button
                    className="btn btn-primary"
                    onClick={() =>
                      editStation(station)
                    }
                  >
                    Editar
                  </button>

                  <button
                    className="btn btn-primary"
                    onClick={() =>
                      toggleStation(station.id)
                    }
                    style={{
                      marginLeft: 10
                    }}
                  >
                    {station.active
                      ? "Desactivar"
                      : "Activar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </DataTable>
      </Card>
    </Page>
  )
}