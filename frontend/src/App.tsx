import { useEffect, useState } from "react"
import TableCard from "./components/TableCard"
import { API_URL } from "./api"

interface Table {
  id: number
  number: number
  occupied: boolean
  order_id?: number | null
  order_status?: string | null
}

function App() {
  const [tables, setTables] = useState<Table[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/tables/`)
      .then(res => res.json())
      .then(data => {
        setTables(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error cargando mesas:", err)
        setLoading(false)
      })
  }, [])

  const touchTable = async (tableId: number) => {
    try {
      const res = await fetch(`${API_URL}/tables/${tableId}/touch`, {
        method: "POST"
      })

      const data = await res.json()

      setTables(prev =>
        prev.map(t =>
          t.id === tableId
            ? {
                ...t,
                occupied: true,
                order_id: data.order_id,
                order_status: data.status
              }
            : t
        )
      )
    } catch (err) {
      console.error("Error tocando mesa:", err)
    }
  }

  if (loading) return <h2>Cargando mesas...</h2>

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 20,
        padding: 20
      }}
    >
      {tables.map(t => (
        <TableCard
          key={t.id}
          number={t.number}
          occupied={t.occupied}
          onClick={() => touchTable(t.id)}
        />
      ))}
    </div>
  )
}

export default App
