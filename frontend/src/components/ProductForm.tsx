import { useEffect, useState } from "react"

import type { Category } from "../types/category.ts"
import type { Product } from "../types/product.ts"
import type { Station } from "../types/station.ts"

// ---------------------------------------------------------------------------------------------
// Props del formulario de productos.
// ---------------------------------------------------------------------------------------------
interface Props {
  product: Product | null
  categories: Category[]
  stations: Station[]
  onSave: (product: Product) => void
  onCancel: () => void
}

// ---------------------------------------------------------------------------------------------
// Formulario reutilizable para crear o editar productos.
// ---------------------------------------------------------------------------------------------
export default function ProductForm({
  product,
  categories,
  stations,
  onSave,
  onCancel
}: Props) {

  const [name, setName] = useState("")
  const [price, setPrice] = useState("")
  const [categoryId, setCategoryId] = useState<number | "">("")
  const [stationId, setStationId] = useState<number | "">("")

  // -------------------------------------------------------------------------------------------
  // Inicializa el formulario al editar un producto.
  // Si no hay producto, limpia el formulario para crear uno nuevo.
  // -------------------------------------------------------------------------------------------
  useEffect(() => {

    if (product) {
      setName(product.name)
      setPrice(String(product.price))
      setCategoryId(product.category_id)
      setStationId(product.station_id)
      return
    }

    setName("")
    setPrice("")
    setCategoryId("")
    setStationId("")

  }, [product])

  // -------------------------------------------------------------------------------------------
  // Valida y envía los datos del formulario al componente padre.
  // -------------------------------------------------------------------------------------------
  const handleSubmit = (): void => {

    if (!name || !price || !categoryId || !stationId) {
      alert("Complete todos los campos")
      return
    }

    onSave({
      id: product?.id,
      name,
      price: Number(price),
      category_id: Number(categoryId),
      station_id: Number(stationId)
    })
  }

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: 20,
        marginBottom: 20,
        borderRadius: 8,
        background: "#fafafa"
      }}
    >

      <h3>
        {product ? "Editar Producto" : "Nuevo Producto"}
      </h3>

      {/* NOMBRE */}
      <div style={{ marginBottom: 10 }}>
        <input
          placeholder="Nombre"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: 250, padding: 5 }}
        />
      </div>

      {/* PRECIO */}
      <div style={{ marginBottom: 10 }}>
        <input
          type="number"
          placeholder="Precio"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          style={{ width: 120, padding: 5 }}
        />
      </div>

      {/* CATEGORÍA */}
      <div style={{ marginBottom: 10 }}>
        <select
          value={categoryId}
          onChange={(e) => {
            const value = e.target.value
            setCategoryId(value ? Number(value) : "")
          }}
          style={{ padding: 5 }}
        >
          <option value="">Seleccionar categoría</option>

          {categories.map(category => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      {/* ESTACIÓN */}
      <div style={{ marginBottom: 10 }}>
        <select
          value={stationId}
          onChange={(e) => {
            const value = e.target.value
            setStationId(value ? Number(value) : "")
          }}
          style={{ padding: 5 }}
        >
          <option value="">Seleccionar estación</option>

          {stations.map(station => (
            <option key={station.id} value={station.id}>
              {station.name}
            </option>
          ))}
        </select>
      </div>

      {/* BOTONES */}
      <button
        onClick={handleSubmit}
        style={{
          marginRight: 10,
          padding: "6px 12px"
        }}
      >
        Guardar
      </button>

      <button
        onClick={onCancel}
        style={{
          padding: "6px 12px"
        }}
      >
        Cancelar
      </button>

    </div>
  )
}