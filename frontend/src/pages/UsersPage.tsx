import { useEffect, useState } from "react"
import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

import { UserRole } from "../types/userRole"
import type {
  User,
  UserCreate,
  UserUpdate
} from "../types/user"

export default function UsersPage() {

  const [users, setUsers] = useState<User[]>([])
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState<UserRole>(UserRole.WAITER)
  const [editingId, setEditingId] = useState<number | null>(null)

  const resetForm = () => {
    setUsername("")
    setPassword("")
    setRole(UserRole.WAITER)
    setEditingId(null)
  }

  // -------------------------
  // Recargar usuarios
  // -------------------------

  const fetchUsers = async () => {
    const data = await apiFetch<User[]>("/users/")
    setUsers(data)
  }

  // -------------------------
  // Guardar usuario
  // -------------------------

  const saveUser = async () => {
    const trimmedUsername = username.trim()
    if (!trimmedUsername) {
      return
    }
    if (editingId !== null) {
      const payload: UserUpdate = {
        username: trimmedUsername,
        role
      }
      if (password) {
        payload.password = password
      }
      await apiFetch(
        `/users/${editingId}`,
        {
          method: "PATCH",
          body: payload
        }
      )
    } else {
      if (!password) {
        return
      }
      const payload: UserCreate = {
        username: trimmedUsername,
        password,
        role
      }
      await apiFetch(
        "/users/",
        {
          method: "POST",
          body: payload
        }
      )
    }
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

  const editUser = ( user: User) => {
    setEditingId(user.id)
    setUsername(user.username)
    setRole(user.role)
    setPassword("")
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

          {Object.values(UserRole).map(
            userRole => (
              <option
                key={userRole}
                value={userRole}
              >
                {userRole}
              </option>
            )
          )}

          <button className="btn btn-primary"
            onClick={saveUser}
            style={{ marginLeft: 10 }}
          >
            {editingId !== null ? "Actualizar" : "Crear"}
          </button>

        </div>

        <DataTable>

          <thead>
            <tr>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Activo</th>
              <th style={{ width: 300 }}>Acciones</th>
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
                    {u.active ? "Desactivar" : "Activar"}
                  </button>

                  {editingId !== null && (
                    <button
                      className="btn btn-primary"
                      onClick={resetForm}
                      style={{ marginLeft: 10 }}
                    >
                      Cancelar
                    </button>
                  )}

                </td>

              </tr>
            ))}

          </tbody>

        </DataTable>

      </Card>

    </Page>
  )
}