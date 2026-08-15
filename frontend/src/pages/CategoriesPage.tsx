import { useEffect, useState } from "react"

import { apiFetch } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

import type {
  Category,
  CategoryCreate,
  CategoryUpdate
} from "../types/category"


export default function CategoriesPage() {
  const [categories, setCategories] =
    useState<Category[]>([])

  const [name, setName] =
    useState("")

  const [editingId, setEditingId] =
    useState<number | null>(null)


  /**
   * Carga todas las categorías, activas e inactivas,
   * para permitir su administración.
   */
  const fetchCategories = async () => {
    const [
      activeCategories,
      inactiveCategories
    ] = await Promise.all([
      apiFetch<Category[]>(
        "/categories/?active=true"
      ),
      apiFetch<Category[]>(
        "/categories/?active=false"
      )
    ])

    setCategories([
      ...activeCategories,
      ...inactiveCategories
    ])
  }


  useEffect(() => {
    fetchCategories()
  }, [])


  /**
   * Crea una nueva categoría o actualiza
   * la que se encuentra en edición.
   */
  const saveCategory = async () => {
    const trimmedName = name.trim()

    if (!trimmedName) {
      return
    }

    if (editingId) {
      const payload: CategoryUpdate = {
        name: trimmedName
      }

      await apiFetch(
        `/categories/${editingId}`,
        {
          method: "PATCH",
          body: payload
        }
      )
    } else {
      const payload: CategoryCreate = {
        name: trimmedName
      }

      await apiFetch(
        "/categories/",
        {
          method: "POST",
          body: payload
        }
      )
    }

    setName("")
    setEditingId(null)

    await fetchCategories()
  }


  /**
   * Activa o desactiva una categoría.
   *
   * Las categorías no se eliminan físicamente
   * para preservar la integridad histórica.
   */
  const toggleCategory = async (
    id: number
  ) => {
    await apiFetch(
      `/categories/${id}/toggle`,
      {
        method: "PATCH"
      }
    )

    await fetchCategories()
  }


  /**
   * Carga una categoría en el formulario de edición.
   */
  const editCategory = (
    category: Category
  ) => {
    setEditingId(category.id)
    setName(category.name)
  }


  /**
   * Cancela la edición actual y limpia el formulario.
   */
  const cancelEdit = () => {
    setEditingId(null)
    setName("")
  }


  return (
    <Page title="Categorías">
      <Card>
        <div style={{ marginBottom: 20 }}>
          <input
            placeholder="Nombre categoría"
            value={name}
            onChange={event =>
              setName(event.target.value)
            }
          />

          <button
            className="btn btn-primary"
            onClick={saveCategory}
            style={{ marginLeft: 10 }}
          >
            {editingId
              ? "Actualizar"
              : "Crear"}
          </button>

          {editingId !== null && (
            <button
              className="btn btn-primary"
              onClick={cancelEdit}
              style={{ marginLeft: 10 }}
            >
              Cancelar
            </button>
          )}
        </div>


        <DataTable>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Estado</th>
              <th style={{ width: 300 }}>
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            {categories.length === 0 && (
              <tr>
                <td colSpan={3}>
                  No hay categorías
                </td>
              </tr>
            )}

            {categories.map(category => (
              <tr key={category.id}>
                <td>{category.name}</td>

                <td>
                  {category.active
                    ? "Activa"
                    : "Inactiva"}
                </td>

                <td>
                  <button
                    className="btn btn-primary"
                    onClick={() =>
                      editCategory(category)
                    }
                  >
                    Editar
                  </button>

                  <button
                    className="btn btn-primary"
                    onClick={() =>
                      toggleCategory(category.id)
                    }
                    style={{ marginLeft: 10 }}
                  >
                    {category.active
                      ? "Desactivar"
                      : "Activar"}
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