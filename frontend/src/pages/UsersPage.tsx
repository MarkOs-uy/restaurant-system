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

function userRoleLabel(
  role: UserRole
): string {
  switch (role) {
    case UserRole.ADMIN:
      return "Administrador"

    case UserRole.WAITER:
      return "Mozo"

    case UserRole.KITCHEN:
      return "Cocina"

    case UserRole.CASHIER:
      return "Caja"

    default:
      return role
  }
}


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

        {/* Alta / edición */}
        <div className="admin-form-row admin-form-row--users">

          <input
            placeholder="Usuario"
            value={username}
            onChange={event =>
              setUsername(event.target.value)
            }
          />

          <input
            type="password"
            placeholder={
              editingId !== null
                ? "Nueva contraseña (opcional)"
                : "Contraseña"
            }
            value={password}
            onChange={event =>
              setPassword(event.target.value)
            }
          />

          <select
            value={role}
            onChange={event =>
              setRole(
                event.target.value as UserRole
              )
            }
          >
            {Object.values(UserRole).map(
              userRole => (
                <option
                  key={userRole}
                  value={userRole}
                >
                  {userRoleLabel(userRole)}
                </option>
              )
            )}
          </select>

          <button
            className="btn btn-primary"
            onClick={saveUser}
          >
            {editingId !== null
              ? "Actualizar"
              : "Crear"}
          </button>

          {editingId !== null && (
            <button
              className="btn btn-secondary"
              onClick={resetForm}
            >
              Cancelar
            </button>
          )}

        </div>


        <DataTable className="users-table">

          <thead>
            <tr>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Estado</th>
              <th className="admin-actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>

            {users.length === 0 && (
              <tr>
                <td
                  colSpan={4}
                  className="admin-table-empty"
                >
                  No hay usuarios
                </td>
              </tr>
            )}

            {users.map(user => (
              <tr
                key={user.id}
                className={
                  user.active
                    ? ""
                    : "admin-row--inactive"
                }
              >

                <td>
                  <strong>
                    {user.username}
                  </strong>
                </td>

                <td>
                  {userRoleLabel(user.role)}
                </td>

                <td>
                  <span
                    className={
                      user.active
                        ? "status-badge status-badge--active"
                        : "status-badge status-badge--inactive"
                    }
                  >
                    {user.active
                      ? "Activo"
                      : "Inactivo"}
                  </span>
                </td>

                <td>
                  <div className="admin-table-actions">

                    <button
                      className="btn btn-secondary"
                      onClick={() =>
                        editUser(user)
                      }
                    >
                      Editar
                    </button>

                    <button
                      className={
                        user.active
                          ? "btn btn-danger"
                          : "btn btn-success"
                      }
                      onClick={() =>
                        toggleUser(user.id)
                      }
                    >
                      {user.active
                        ? "Desactivar"
                        : "Activar"}
                    </button>

                  </div>
                </td>

              </tr>
            ))}

          </tbody>

        </DataTable>

      </Card>
    </Page>
  )
}