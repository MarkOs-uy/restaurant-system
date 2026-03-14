import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

interface Category {
  id: number
  name: string
}

export default function CategoriesPage() {

  const [categories, setCategories] = useState<Category[]>([])
  const [name, setName] = useState("")
  const [editingId, setEditingId] = useState<number | null>(null)

  const fetchCategories = async () => {

    const res = await fetch(
      `${API_URL}/categories`,
      { headers: getAuthHeaders() }
    )

    const data = await res.json()
    setCategories(data)
  }

  useEffect(() => {
    fetchCategories()
  }, [])

  const saveCategory = async () => {

    if (!name) return

    const method = editingId ? "PATCH" : "POST"

    const url = editingId
      ? `${API_URL}/categories/${editingId}`
      : `${API_URL}/categories`

    await fetch(url, {
      method,
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    })

    setName("")
    setEditingId(null)

    fetchCategories()
  }

  const deleteCategory = async (id: number) => {

    if (!confirm("Eliminar categoría?")) return

    await fetch(
      `${API_URL}/categories/${id}`,
      {
        method: "DELETE",
        headers: getAuthHeaders()
      }
    )

    fetchCategories()
  }

  const editCategory = (c: Category) => {
    setEditingId(c.id)
    setName(c.name)
  }

  return (
    <div style={{ padding: 40 }}>

      <h1>Categorías</h1>

      <div style={{ marginBottom: 20 }}>
        <input
          placeholder="Nombre categoría"
          value={name}
          onChange={e => setName(e.target.value)}
        />

        <button
          onClick={saveCategory}
          style={{ marginLeft: 10 }}
        >
          {editingId ? "Actualizar" : "Crear"}
        </button>
      </div>

      <ul>
        {categories.map(c => (
          <li key={c.id}>

            {c.name}

            <button
              onClick={() => editCategory(c)}
              style={{ marginLeft: 10 }}
            >
              Editar
            </button>

            <button
              onClick={() => deleteCategory(c.id)}
              style={{ marginLeft: 10 }}
            >
              Eliminar
            </button>

          </li>
        ))}
      </ul>

    </div>
  )
}