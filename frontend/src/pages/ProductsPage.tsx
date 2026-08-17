import {
  Fragment,
  useEffect,
  useState
} from "react"

import { apiFetch } from "../api"

import type {
  Product,
  ProductCreate,
  ProductUpdate,
  RawProduct
} from "../types/product"

import type { Category } from "../types/category"
import type { Station } from "../types/station"

import Page from "../components/Page"
import Card from "../components/Card"
import DataTable from "../components/DataTable"
import ProductForm from "../components/ProductForm"

import { moneyToNumber } from "../utils/money"


type GroupedProducts = Record<string, Product[]>


function normalizeProduct(
  product: RawProduct
): Product {
  return {
    ...product,
    price: moneyToNumber(product.price)
  }
}


function compareProducts(
  a: Product,
  b: Product
): number {
  if (a.active !== b.active) {
    return a.active ? -1 : 1
  }

  return a.name.localeCompare(
    b.name,
    "es",
    { sensitivity: "base" }
  )
}

export default function ProductsPage() {
  const [products, setProducts] =
    useState<Product[]>([])

  const [categories, setCategories] =
    useState<Category[]>([])

  const [stations, setStations] =
    useState<Station[]>([])

  const [
    editingProduct,
    setEditingProduct
  ] = useState<Product | null>(null)

  const [showForm, setShowForm] =
    useState(false)

  const [
    openCategories,
    setOpenCategories
  ] = useState<Record<string, boolean>>({})


  /**
   * Carga todos los productos.
   */
  const fetchProducts = async () => {
    const [
      activeProducts,
      inactiveProducts
    ] = await Promise.all([
      apiFetch<RawProduct[]>(
        "/products/?active=true"
      ),
      apiFetch<RawProduct[]>(
        "/products/?active=false"
      )
    ])

    setProducts([
      ...activeProducts.map(normalizeProduct),
      ...inactiveProducts.map(normalizeProduct)
    ])
  }


  /**
   * Carga las categorías activas disponibles
   * para asignar a productos.
   */
  const fetchCategories = async () => {
    const data =
      await apiFetch<Category[]>(
        "/categories/?active=true"
      )

    setCategories(data)
  }


  /**
   * Carga las estaciones activas disponibles
   * para asignar a productos.
   */
  const fetchStations = async () => {
    const data =
      await apiFetch<Station[]>(
        "/stations/?active=true"
      )

    setStations(data)
  }


  useEffect(() => {
    fetchProducts()
    fetchCategories()
    fetchStations()
  }, [])


  /**
   * Crea un producto nuevo o actualiza
   * el producto actualmente en edición.
   */
  const saveProduct = async (
    product: ProductCreate
  ) => {
    if (editingProduct) {
      const payload: ProductUpdate = {
        name: product.name,
        price: product.price,
        category_id: product.category_id,
        station_id: product.station_id
      }

      await apiFetch(
        `/products/${editingProduct.id}`,
        {
          method: "PATCH",
          body: payload
        }
      )
    } else {
      await apiFetch(
        "/products/",
        {
          method: "POST",
          body: product
        }
      )
    }

    setShowForm(false)
    setEditingProduct(null)

    await fetchProducts()
  }


  /**
   * Activa o desactiva un producto.
   */
  const toggleActive = async (
    id: number
  ) => {
    await apiFetch(
      `/products/${id}/toggle`,
      {
        method: "PATCH"
      }
    )

    await fetchProducts()
  }


  /**
   * Agrupa los productos por categoría
   * para mostrarlos en la tabla.
   */
  const groupedProducts =
    products.reduce<GroupedProducts>(
      (groups, product) => {
        const categoryName =
          product.category?.name ??
          "Sin categoría"

        if (!groups[categoryName]) {
          groups[categoryName] = []
        }

        groups[categoryName].push(product)

        return groups
      },
      {}
    )

// Activa-Desactiva una categoría
  const toggleCategory = (categoryName: string) => {
    setOpenCategories(previous => ({
      ...previous,
      [categoryName]:
        !previous[categoryName]
    }))
  }


  return (
    <Page title="Productos">
      <Card>
        <button
          className="btn btn-primary"
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
              <th style={{ width: 300 }}>
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            {Object.entries(groupedProducts)
              .sort(([a], [b]) =>
                a.localeCompare(b)
              )
              .map(
                ([categoryName, items]) => (
                  <Fragment
                    key={categoryName}
                  >
                    <tr
                      style={{
                        background:
                          "rgba(255, 255, 255, 0.04)",
                        cursor: "pointer"
                      }}
                      onClick={() =>
                        toggleCategory(
                          categoryName
                        )
                      }
                    >
                      <td
                        colSpan={6}
                        style={{
                          fontWeight: "bold",
                          color:
                            "var(--color-primary)"
                        }}
                      >
                        {openCategories[
                          categoryName
                        ]
                          ? "▼"
                          : "▶"}{" "}
                        {categoryName}
                      </td>
                    </tr>


                    {openCategories[
                      categoryName
                    ] &&
                      [...items]
                        .sort(compareProducts)
                        .map(product => (
                          <tr
                            key={product.id}
                          >
                            <td>
                              {product.name}
                            </td>

                            <td>
                              $
                              {product.price.toFixed(
                                2
                              )}
                            </td>

                            <td>
                              {product.category
                                ?.name ?? "-"}
                            </td>

                            <td>
                              {product.station
                                ?.name ?? "-"}
                            </td>

                            <td>
                              {product.active
                                ? "✔"
                                : "❌"}
                            </td>

                            <td>
                              <button
                                className="btn btn-primary"
                                onClick={() => {
                                  setEditingProduct(
                                    product
                                  )
                                  setShowForm(
                                    true
                                  )
                                }}
                              >
                                Editar
                              </button>

                              <button
                                className="btn btn-primary"
                                onClick={() =>
                                  toggleActive(
                                    product.id
                                  )
                                }
                                style={{
                                  marginLeft: 10
                                }}
                              >
                                {product.active
                                  ? "Desactivar"
                                  : "Activar"}
                              </button>
                            </td>
                          </tr>
                        ))}
                  </Fragment>
                )
              )}
          </tbody>
        </DataTable>
      </Card>
    </Page>
  )
}