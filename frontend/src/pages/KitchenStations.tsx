import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"

interface Station {
  id: number
  name: string
}

export default function KitchenStations() {

  const navigate = useNavigate()

  const [stations, setStations] = useState<Station[]>([])

  useEffect(() => {
    fetchStations()
  }, [])

  const fetchStations = async () => {
    const data = await apiFetch(
      `/stations/active`
    )
    setStations(data)
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>Elegir estación</h1>

      {stations.map(station => (
        <button
          key={station.id}
          onClick={() => {
            localStorage.setItem("kitchen_station_id", station.id.toString())
            navigate(`/kitchen/${station.id}`)
          }}
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