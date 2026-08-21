import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { apiFetch } from "../api"
import type { Station } from "../types/station"


export default function KitchenStations() {
  const navigate = useNavigate()

  const [stations, setStations] = useState<Station[]>([])
  const [loading, setLoading] = useState(true)


  /**
   * Carga las estaciones de producción activas.
   */
  const fetchStations = async () => {
    try {
      const data = await apiFetch<Station[]>(
        "/stations/active"
      )
      setStations(data)
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    fetchStations()
  }, [])


  const selectStation = (station: Station) => {
    localStorage.setItem(
      "kitchen_station_id",
      String(station.id)
    )
    navigate(`/kitchen/${station.id}`)
  }


  if (loading) {
    return (
      <div style={{ padding: 40 }}>
        <p>Cargando estaciones...</p>
      </div>
    )
  }


  return (
    <div className="kitchen-stations-page">

      <header className="kitchen-stations-header">
        <p>Cocina</p>
        <h1>Elegir estación</h1>
      </header>

      {stations.length === 0 ? (
        <div className="kitchen-empty">
          <strong>
            No hay estaciones activas
          </strong>

          <span>
            Configure una estación desde
            administración.
          </span>
        </div>
      ) : (
        <div className="kitchen-stations-grid">
          {stations.map(station => (
            <button
              key={station.id}
              type="button"
              className="kitchen-station-button"
              onClick={() =>
                selectStation(station)
              }
            >
              <span>
                {station.name}
              </span>

              <small>
                Abrir estación →
              </small>
            </button>
          ))}
        </div>
      )}

    </div>
  )
}