import { useEffect, useState } from "react"
import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

interface Category {
  id: number
  name: string
}

export default function CategoriesPage() {

  const [categories, setCategories] = useState<Category[]>([])
  const [name, setName] = useState("")
  const [editingId, setEditingId] = useState<number | null>(null)

  const fetchCategories = async () => {
    const data = await apiFetch(`/categories/`)
    setCategories(data)
  }

  useEffect(() => {
    fetchCategories()
  }, [])

  const saveCategory = async () => {

    if (!name) return

    try {

      const method = editingId ? "PATCH" : "POST"

      const url = editingId
        ? `/categories/${editingId}`
        : `/categories/`

      await apiFetch(url, {
        method,
        body: { name }
      })

      setName("")
      setEditingId(null)

      fetchCategories()

    } catch (err:any) {
      alert(err.message)
    }
  }

  const deleteCategory = async (id: number) => {

    if (!confirm("Eliminar categoría?")) return

    await apiFetch(
      `/categories/${id}`,
      {
        method: "DELETE",
      }
    )

    fetchCategories()
  }

  const editCategory = (c: Category) => {
    setEditingId(c.id)
    setName(c.name)
  }

  return (
    <Page title="Categorías">

      <Card>

        <div style={{ marginBottom: 20 }}>

          <input
            placeholder="Nombre categoría"
            value={name}
            onChange={e => setName(e.target.value)}
          />

          <button className="btn btn-primary"
            onClick={saveCategory}
            style={{ marginLeft: 10 }}
          >
            {editingId ? "Actualizar" : "Crear"}
          </button>

        </div>

        <DataTable>

          <thead>
            <tr>
              <th>Nombre</th>
              <th style={{ width: 300 }}>Acciones</th>
            </tr>
          </thead>

          <tbody>

            {categories.map(c => (
              <tr key={c.id}>

                <td>{c.name}</td>

                <td>

                  <button className="btn btn-primary"
                    onClick={() => editCategory(c)}>
                    Editar
                  </button>

                  <button className="btn btn-primary"
                    onClick={() => deleteCategory(c.id)}
                    style={{ marginLeft: 10 }}
                  >
                    Eliminar
                  </button>

                  {editingId && (
                    <button className="btn btn-primary"
                      onClick={() => {
                        setEditingId(null)
                        setName("")
                      }}
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