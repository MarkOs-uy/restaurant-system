import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"

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
    const [originalTables, setOriginalTables] = useState<Table[]>([])
    const navigate = useNavigate()

    const loadTables = async () => {
        const data = await apiFetch("/tables/")
        setTables(data)
        setOriginalTables(data)
    }

    useEffect(() => {
        loadTables()
    }, [])

    const activeTables = tables.filter(t => t.active)
    const inactiveTables = tables.filter(t => !t.active)

    const hasChanges = (t: Table) => {
        const original = originalTables.find(o => o.id === t.id)

        if (!original) return false

        return (
            original.capacity !== t.capacity ||
            original.shape !== t.shape ||
            original.active !== t.active
        )
    }


    const updateTable = async (t: Table) => {
        const payload = {
            capacity: t.capacity,
            shape: t.shape,
            active: t.active
        }
        await apiFetch(`/tables/${t.id}`, {
            method: "PATCH",
            body: payload
        })
        loadTables()
    }


    const updateField = <K extends keyof Table>(
        id: number,
        field: K,
        value: Table[K]
    ) => {
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

        <button onClick={() => navigate("/")}>
        ← Volver al plano
        </button>

        <h1>Administrar mesas</h1>

        <h2 style={{ marginTop: 20 }}>Mesas activas</h2>

        <table style={{ width: "100%", textAlign: "center" }}>
        <thead>
            <tr>
                <th style={{ width: 120, textAlign: "center" }}>Número</th>
                <th style={{ width: 120, textAlign: "center" }}>Capacidad</th>
                <th style={{ width: 120, textAlign: "center" }}>Forma</th>
                <th style={{ width: 120, textAlign: "center" }}>Activa</th>
                <th style={{ width: 120, textAlign: "center" }}></th>
            </tr>
        </thead>

        <tbody>
            {activeTables.length === 0 && (
                <tr>
                    <td colSpan={5}>No hay mesas activas</td>
                </tr>
            )}
            {activeTables.map((t) => (
            <tr key={t.id}>

                <td>
                    <span>{t.number}</span>
                </td>

                <td>
                    <input
                        type="number"
                        value={t.capacity}
                        style={{ textAlign: "center", width: 60 }}
                        onChange={(e) =>
                            updateField(t.id, "capacity", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                <select
                    value={t.shape}
                    style={{ textAlign: "center" }}
                    onChange={(e) =>
                    updateField(t.id, "shape", e.target.value)
                    }
                >
                    <option value="circle">Circular</option>
                    <option value="square">Cuadrada</option>
                    <option value="rectangle">Rectangular</option>
                </select>
                </td>

                <td style={{ textAlign: "center" }}>
                <input
                    type="checkbox"
                    checked={t.active}
                    onChange={(e) =>
                    updateField(t.id, "active", e.target.checked)
                    }
                />
                </td>

                <td>
                <button
                    onClick={() => updateTable(t)}
                    disabled={!hasChanges(t)}
                    style={{
                        opacity: hasChanges(t) ? 1 : 0.5,
                        cursor: hasChanges(t) ? "pointer" : "not-allowed"
                    }}
                >
                    Guardar
                </button>
                </td>

            </tr>
            ))}
        </tbody>
        </table>


        <h2 style={{ marginTop: 30 }}>Mesas inactivas</h2>

        <table style={{ width: "100%", textAlign: "center" }}>
        <thead>
            <tr>
                <th style={{ width: 120, textAlign: "center" }}>Número</th>
                <th style={{ width: 120, textAlign: "center" }}>Capacidad</th>
                <th style={{ width: 120, textAlign: "center" }}>Forma</th>
                <th style={{ width: 120, textAlign: "center" }}>Activa</th>
                <th style={{ width: 120, textAlign: "center" }}></th>
            </tr>
        </thead>

        <tbody>
            {inactiveTables.length === 0 && (
                <tr>
                    <td colSpan={5}>No hay mesas inactivas</td>
                </tr>
            )}
            {inactiveTables.map((t) => (
            <tr key={t.id}>

                <td>
                    <span>{t.number}</span>
                </td>

                <td>
                    <input
                        type="number"
                        style={{ textAlign: "center", width: 60 }}
                        value={t.capacity}
                        onChange={(e) =>
                        updateField(t.id, "capacity", Number(e.target.value))
                        }
                    />
                </td>

                <td>
                    <select
                        value={t.shape}
                        style={{ textAlign: "center" }}
                        onChange={(e) =>
                        updateField(t.id, "shape", e.target.value)
                        }
                    >
                        <option value="circle">Circular</option>
                        <option value="square">Cuadrada</option>
                        <option value="rectangle">Rectangular</option>
                    </select>
                </td>

                <td style={{ textAlign: "center" }}>
                    <input
                        type="checkbox"
                        checked={t.active}
                        onChange={(e) =>
                        updateField(t.id, "active", e.target.checked)
                        }
                    />
                </td>

                <td>
                    <button
                        onClick={() => updateTable(t)}
                        disabled={!hasChanges(t)}
                        style={{
                            opacity: hasChanges(t) ? 1 : 0.5,
                            cursor: hasChanges(t) ? "pointer" : "not-allowed"
                        }}
                    >
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