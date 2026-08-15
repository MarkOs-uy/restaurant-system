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
    <div style={{ padding: 40 }}>
      <h1>Elegir estación</h1>

      {stations.length === 0 && (
        <p>No hay estaciones activas.</p>
      )}

      {stations.map(station => (
        <button
          key={station.id}
          onClick={() => selectStation(station)}
          style={{
            display: "block",
            width: "100%",
            padding: 20,
            marginBottom: 20,
            fontSize: 22,
            borderRadius: 8
          }}
        >
          {station.name}
        </button>
      ))}
    </div>
  )
}