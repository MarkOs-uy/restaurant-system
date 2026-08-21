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

        <div className="admin-page-actions">
          <button
            className="btn btn-primary"
            onClick={() => {
              setEditingProduct(null)
              setShowForm(true)
            }}
          >
            + Nuevo producto
          </button>
        </div>


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


        <DataTable className="products-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Precio</th>
              <th>Categoría</th>
              <th>Estación</th>
              <th>Estado</th>
              <th className="admin-actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            {Object.entries(groupedProducts)
              .sort(([a], [b]) =>
                a.localeCompare(b)
              )
              .map(([categoryName, items]) => (
                <Fragment key={categoryName}>

                  {/* Grupo de categoría */}
                  <tr
                    className="product-category-row"
                    onClick={() =>
                      toggleCategory(categoryName)
                    }
                  >
                    <td colSpan={6}>
                      <span className="product-category-row__toggle">
                        {openCategories[categoryName]
                          ? "▼"
                          : "▶"}
                      </span>

                      <strong>
                        {categoryName}
                      </strong>

                      <span className="product-category-row__count">
                        {items.length}
                      </span>
                    </td>
                  </tr>


                  {openCategories[categoryName] &&
                    [...items]
                      .sort(compareProducts)
                      .map(product => (
                        <tr
                          key={product.id}
                          className={
                            product.active
                              ? ""
                              : "admin-row--inactive"
                          }
                        >
                          <td>
                            <strong>
                              {product.name}
                            </strong>
                          </td>

                          <td>
                            ${product.price.toFixed(2)}
                          </td>

                          <td>
                            {product.category?.name ?? "-"}
                          </td>

                          <td>
                            {product.station?.name ?? "-"}
                          </td>

                          <td>
                            <span
                              className={
                                product.active
                                  ? "status-badge status-badge--active"
                                  : "status-badge status-badge--inactive"
                              }
                            >
                              {product.active
                                ? "Activo"
                                : "Inactivo"}
                            </span>
                          </td>

                          <td>
                            <div className="admin-table-actions">

                              <button
                                className="btn btn-secondary"
                                onClick={() => {
                                  setEditingProduct(product)
                                  setShowForm(true)
                                }}
                              >
                                Editar
                              </button>

                              <button
                                className={
                                  product.active
                                    ? "btn btn-danger"
                                    : "btn btn-success"
                                }
                                onClick={() =>
                                  toggleActive(product.id)
                                }
                              >
                                {product.active
                                  ? "Desactivar"
                                  : "Activar"}
                              </button>

                            </div>
                          </td>
                        </tr>
                      ))}

                </Fragment>
              ))}
          </tbody>
        </DataTable>

      </Card>
    </Page>
  )
}