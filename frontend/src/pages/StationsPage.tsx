import { useEffect, useState } from "react"
import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"
import { showToast } from "../utils/showToast"

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
    const data = await apiFetch(`/stations/`)
    setStations(data)
  }

  useEffect(() => {
    fetchStations()
  }, [])

  const saveStation = async () => {
    if (!name.trim()) {
      showToast("Ingrese un nombre de estación")
      return
    }
    const method = editingId ? "PATCH" : "POST"
    const url = editingId
      ? `/stations/${editingId}`
      : `/stations/`
    await apiFetch(url, {
      method,
      body: { name }
    })
    setName("")
    setEditingId(null)
    await fetchStations()
  }


  const toggleStation = async (id: number) => {
    await apiFetch(`/stations/${id}/toggle`,
      {
        method: "PATCH"
      }
    )
    await fetchStations()
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

          <button className="btn btn-primary"
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

                  <button className="btn btn-primary"
                    onClick={() => editStation(s)}>
                    Editar
                  </button>

                  <button className="btn btn-primary"
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