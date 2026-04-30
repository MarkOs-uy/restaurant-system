import { useEffect, useState } from "react"
import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

interface User {
  id: number
  username: string
  role: string
  active: boolean
}

export default function UsersPage() {

  const [users, setUsers] = useState<User[]>([])
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState("WAITER")
  const [editingId, setEditingId] = useState<number | null>(null)

  const resetForm = () => {
    setUsername("")
    setPassword("")
    setRole("WAITER")
    setEditingId(null)
  }

  // -------------------------
  // Recargar usuarios
  // -------------------------

  const fetchUsers = async () => {
    const data = await apiFetch("/users/")
    setUsers(data)
  }

  // -------------------------
  // Guardar usuario
  // -------------------------

  const saveUser = async () => {
    if (!username) return
    const method = editingId ? "PATCH" : "POST"
    const url = editingId
      ? `/users/${editingId}`
      : `/users/`
    await apiFetch(url, {
      method,
      body: {
        username,
        ...(password && { password }),
        role
      }
    })
    resetForm()
    await fetchUsers()
  }

  // -------------------------
  // Activar/Desactivar usuarios
  // -------------------------

  const toggleUser = async (id: number) => {
    await apiFetch(`/users/${id}/toggle`, {
      method: "PATCH"
    })
    await fetchUsers()
  }

  // -------------------------
  // Editar usuarios
  // -------------------------

  const editUser = (u: User) => {
    setEditingId(u.id)
    setUsername(u.username)
    setRole(u.role)
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  return (
    <Page title="Usuarios">

      <Card>

        <div style={{ marginBottom: 20 }}>

          <input
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ marginLeft: 10 }}
          />

          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{ marginLeft: 10 }}
          >
            <option value="ADMIN">ADMIN</option>
            <option value="WAITER">WAITER</option>
            <option value="KITCHEN">KITCHEN</option>
            <option value="CASHIER">CASHIER</option>
          </select>

          <button className="btn btn-primary"
            onClick={saveUser}
            style={{ marginLeft: 10 }}
          >
            {editingId ? "Actualizar" : "Crear"}
          </button>

        </div>

        <DataTable>

          <thead>
            <tr>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Activo</th>
              <th style={{ width: 260 }}>Acciones</th>
            </tr>
          </thead>

          <tbody>

            {users.map(u => (
              <tr key={u.id}>

                <td>{u.username}</td>

                <td>{u.role}</td>

                <td>{u.active ? "✔" : "❌"}</td>

                <td>

                  <button className="btn btn-primary"
                    onClick={() => editUser(u)}>
                    Editar
                  </button>

                  <button className="btn btn-primary"
                    onClick={() => toggleUser(u.id)}
                    style={{ marginLeft: 5 }}
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