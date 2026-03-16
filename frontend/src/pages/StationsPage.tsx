import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

interface Station {
  id: number
  name: string
  active: boolean
}

export default function StationsPage() {

  const [stations, setStations] = useState<Station[]>([])
  const [name, setName] = useState("")
  const [editingId, setEditingId] = useState<number | null>(null)

  const fetchStations = async () => {

    const res = await fetch(
      `${API_URL}/stations/`,
      { headers: getAuthHeaders() }
    )

    const data = await res.json()
    setStations(data)
  }

  useEffect(() => {
    fetchStations()
  }, [])

  const saveStation = async () => {

    if (!name) return

    const method = editingId ? "PATCH" : "POST"

    const url = editingId
      ? `${API_URL}/stations/${editingId}`
      : `${API_URL}/stations/`

    await fetch(url, {
      method,
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    })

    setName("")
    setEditingId(null)

    fetchStations()
  }

  const toggleStation = async (id: number) => {

    await fetch(
      `${API_URL}/stations/${id}/toggle`,
      {
        method: "PATCH",
        headers: getAuthHeaders()
      }
    )

    fetchStations()
  }

  const editStation = (station: Station) => {
    setEditingId(station.id)
    setName(station.name)
  }

  return (
    <Page title="Estaciones">

      <Card>

        <div style={{ marginBottom: 20 }}>
          <input
            placeholder="Nombre estación"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <button
            onClick={saveStation}
            style={{ marginLeft: 10 }}
          >
            {editingId ? "Actualizar" : "Crear"}
          </button>
        </div>

        <DataTable>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Activa</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {stations.map(s => (
              <tr key={s.id}>

                <td>{s.name}</td>

                <td>{s.active ? "✔" : "❌"}</td>

                <td>

                  <button onClick={() => editStation(s)}>
                    Editar
                  </button>

                  <button
                    onClick={() => toggleStation(s.id)}
                    style={{ marginLeft: 10 }}
                  >
                    Activar / Desactivar
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