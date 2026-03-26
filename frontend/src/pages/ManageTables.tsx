import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { API_URL, getAuthHeaders } from "../api"

interface Table {
  id: number
  number: number
  x: number
  y: number
  shape: string
  status: string
  active: boolean
  order_id?: number | null
  order_status?: string | null
  capacity: number
}

export default function ManageTables() {

    const [tables, setTables] = useState<Table[]>([])
    const navigate = useNavigate()

    const loadTables = async () => {
        const res = await fetch(`${API_URL}/tables/all`, {
        headers: getAuthHeaders()
        })
        const data = await res.json()
        setTables(data)
    }

    useEffect(() => {
        loadTables()
    }, [])

    const activeTables = tables.filter(t => t.active)
    const inactiveTables = tables.filter(t => !t.active)

    const updateTable = async (t: Table) => {
        await fetch(`${API_URL}/tables/${t.id}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify(t)
        })

        loadTables()
    }

    const updateField = (id: number, field: keyof Table, value: any) => {
        setTables(prev =>
            prev.map(t =>
            t.id === id
                ? { ...t, [field]: value }
                : t
            )
        )
    }

    return (
        <div style={{ padding: 20 }}>

        <button onClick={() => navigate("/tables")}>
            ← Volver al plano
        </button>

        <h1>Administrar mesas</h1>

        <table style={{ width: "100%", marginTop: 20 }}>
            <thead>
            <tr>
                <th>Número</th>
                <th>Capacidad</th>
                <th>Forma</th>
                <th>Activa</th>
                <th></th>
            </tr>
            </thead>

            <tbody>
            <h2>Mesas activas</h2>
            {activeTables.map((t) => (
                <tr key={t.id}>

                <td>
                    <input
                    type="number"
                    value={t.number}
                    onChange={(e) =>
                        updateField(t.id, "number", Number(e.target.value))
                    }
                    />
                </td>

                <td>
                    <input
                    type="number"
                    value={t.capacity}
                    onChange={(e) =>
                        updateField(t.id, "capacity", Number(e.target.value))
                    }
                    />
                </td>

                <td>
                    <select
                    value={t.shape}
                    onChange={(e) =>
                        updateField(t.id, "shape", e.target.value)
                    }
                    >
                    <option value="circle">Circular</option>
                    <option value="square">Cuadrada</option>
                    <option value="rectangle">Rectangular</option>
                    </select>
                </td>

                <td>
                    <input
                    type="checkbox"
                    checked={t.active}
                    onChange={(e) =>
                        updateField(t.id, "active", e.target.checked)
                    }
                    />
                </td>

                <td>
                    <button onClick={() => updateTable(t)}>
                    Guardar
                    </button>
                </td>

                </tr>
            ))}

            <h2 style={{ marginTop: 30 }}>Mesas inactivas</h2>
            {inactiveTables.map((t) => (
                <tr key={t.id}>

                <td>
                    <input
                    type="number"
                    value={t.number}
                    onChange={(e) =>
                        updateField(t.id, "number", Number(e.target.value))
                    }
                    />
                </td>

                <td>
                    <input
                    type="number"
                    value={t.capacity}
                    onChange={(e) =>
                        updateField(t.id, "capacity", Number(e.target.value))
                    }
                    />
                </td>

                <td>
                    <select
                    value={t.shape}
                    onChange={(e) =>
                        updateField(t.id, "shape", e.target.value)
                    }
                    >
                    <option value="circle">Circular</option>
                    <option value="square">Cuadrada</option>
                    <option value="rectangle">Rectangular</option>
                    </select>
                </td>

                <td>
                    <input
                    type="checkbox"
                    checked={t.active}
                    onChange={(e) =>
                        updateField(t.id, "active", e.target.checked)
                    }
                    />
                </td>

                <td>
                    <button onClick={() => updateTable(t)}>
                    Guardar
                    </button>
                </td>

                </tr>
            ))}


            </tbody>
        </table>

        </div>
    )
}