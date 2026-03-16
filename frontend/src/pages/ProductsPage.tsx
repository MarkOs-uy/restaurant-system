import { useEffect, useState } from "react"
import { API_URL, getAuthHeaders } from "../api"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"

import ProductForm from "../components/ProductForm"

interface Product {
  id: number
  name: string
  price: number
  active: boolean
  category_id: number
  station_id: number
  category?: { name: string }
  station?: { name: string }
}

interface Category {
  id: number
  name: string
}

interface Station {
  id: number
  name: string
}

export default function ProductsPage() {

  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [stations, setStations] = useState<Station[]>([])

  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [showForm, setShowForm] = useState(false)

  const [openCategories, setOpenCategories] = useState<Record<string, boolean>>({})

  const fetchProducts = async () => {

    const res = await fetch(
      `${API_URL}/products/`,
      { headers: getAuthHeaders() }
    )

    const data = await res.json()
    setProducts(data)
  }

  const fetchCategories = async () => {

    const res = await fetch(
      `${API_URL}/categories/`,
      { headers: getAuthHeaders() }
    )

    const data = await res.json()
    setCategories(data)
  }

  const fetchStations = async () => {

    const res = await fetch(
      `${API_URL}/stations/`,
      { headers: getAuthHeaders() }
    )

    const data = await res.json()
    setStations(data)
  }

  useEffect(() => {
    fetchProducts()
    fetchCategories()
    fetchStations()
  }, [])

  const saveProduct = async (product: any) => {

    const method = product.id ? "PATCH" : "POST"

    const url = product.id
      ? `${API_URL}/products/${product.id}`
      : `${API_URL}/products/`

    await fetch(url, {
      method,
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "application/json"
      },
      body: JSON.stringify(product)
    })

    setShowForm(false)
    setEditingProduct(null)

    fetchProducts()
  }

  const toggleActive = async (id: number) => {

    await fetch(
      `${API_URL}/products/${id}/toggle`,
      {
        method: "PATCH",
        headers: getAuthHeaders()
      }
    )

    fetchProducts()
  }

  const groupedProducts = products.reduce((acc: any, p) => {
    const cat = p.category?.name || "Sin categoría"

    if (!acc[cat]) acc[cat] = []

    acc[cat].push(p)

    return acc
  }, {})

  const toggleCategory = (cat: string) => {
    setOpenCategories(prev => ({
      ...prev,
      [cat]: !prev[cat]
    }))
  }

  return (
    <Page title="Productos">

      <Card>

        <button
          onClick={() => {
            setEditingProduct(null)
            setShowForm(true)
          }}
          style={{ marginBottom: 20 }}
        >
          + Nuevo producto
        </button>

        {showForm && (
          <ProductForm
            product={editingProduct}
            categories={categories}
            stations={stations}
            onSave={saveProduct}
            onCancel={() => {
              setShowForm(false)
              setEditingProduct(null)
            }}
          />
        )}

        <DataTable>

          <thead>
            <tr>
              <th>Nombre</th>
              <th>Precio</th>
              <th>Categoría</th>
              <th>Estación</th>
              <th>Activo</th>
              <th style={{ width: 220 }}>Acciones</th>
            </tr>
          </thead>

          <tbody>

          {Object.entries(groupedProducts)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([categoryName, items]: any) => (

              <>
                {/* HEADER CATEGORÍA */}

                <tr
                  style={{
                    background: "#e9e9e9",
                    cursor: "pointer"
                  }}
                  onClick={() => toggleCategory(categoryName)}
                >
                  <td colSpan={6} style={{ fontWeight: "bold" }}>
                    {openCategories[categoryName] ? "▼" : "▶"} {categoryName}
                  </td>
                </tr>

                {/* PRODUCTOS */}

                {openCategories[categoryName] &&
                  items
                    .sort((a: any, b: any) => a.name.localeCompare(b.name))
                    .map((p: any) => (

                      <tr key={p.id}>

                        <td>{p.name}</td>

                        <td>${p.price}</td>

                        <td>{p.category?.name || "-"}</td>

                        <td>{p.station?.name || "-"}</td>

                        <td>{p.active ? "✔" : "❌"}</td>

                        <td>

                          <button
                            onClick={() => {
                              setEditingProduct(p)
                              setShowForm(true)
                            }}
                          >
                            Editar
                          </button>

                          <button
                            onClick={() => toggleActive(p.id)}
                            style={{ marginLeft: 10 }}
                          >
                            Activar / Desactivar
                          </button>

                        </td>

                      </tr>

                    ))}

              </>
            ))}

          </tbody>

        </DataTable>

      </Card>

    </Page>
  )
}