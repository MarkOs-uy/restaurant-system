import { useEffect, useState } from "react"
import TableCard from "./components/TableCard"
import { API_URL } from "./api.ts"

type Table = {
  id: number
  number: number
  status: "libre" | "ocupada"
  order_id: number | null
  order_status: string | null
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

  if (loading) return <h2 style={{ padding: 20 }}>Cargando mesas...</h2>

return (
  <div
    style={{
      maxWidth: 1200,
      margin: "0 auto",
      padding: 40,
    }}
  >
    <h1 style={{ marginBottom: 30 }}>Salón</h1>

    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
        gap: 20,
      }}
    >
      {tables.map((t: any) => (
        <TableCard
          key={t.id}
          number={t.number}
          status={t.status}
          orderStatus={t.order_status}
        />
      ))}
    </div>
  </div>
)

}

export default App

