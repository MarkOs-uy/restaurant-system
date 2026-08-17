import { useEffect, useState } from "react"

import type { Category } from "../types/category"
import type {
  Product,
  ProductCreate
} from "../types/product"
import type { Station } from "../types/station"


// ---------------------------------------------------------------------------------------------
// Props del formulario de productos.
// ---------------------------------------------------------------------------------------------
interface Props {
  product: Product | null
  categories: Category[]
  stations: Station[]
  onSave: (product: ProductCreate) => void
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
  const [categoryId, setCategoryId] =
    useState<number | "">("")
  const [stationId, setStationId] =
    useState<number | "">("")


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
    const trimmedName = name.trim()
    const numericPrice = Number(price)

    if (
      !trimmedName ||
      price === "" ||
      categoryId === "" ||
      stationId === ""
    ) {
      alert("Complete todos los campos")
      return
    }

    if (
      Number.isNaN(numericPrice) ||
      numericPrice < 0
    ) {
      alert("Ingrese un precio válido")
      return
    }

    onSave({
      name: trimmedName,
      price: numericPrice,
      category_id: categoryId,
      station_id: stationId
    })
  }


  return (
    <div
      style={{
        border: "1px solid #333",
        padding: 20,
        marginBottom: 20,
        borderRadius: 8,
        background: "#1e1e1e",
        color: "white"
      }}
    >

      <h3>
        {product
          ? "Editar Producto"
          : "Nuevo Producto"}
      </h3>


      {/* NOMBRE */}
      <div style={{ marginBottom: 10 }}>
        <input
          placeholder="Nombre"
          value={name}
          onChange={e =>
            setName(e.target.value)
          }
          style={{
            width: 250,
            padding: 8,
            background: "#111",
            color: "white",
            border: "1px solid #444",
            borderRadius: 6
          }}
        />
      </div>


      {/* PRECIO */}
      <div style={{ marginBottom: 10 }}>
        <input
          type="number"
          min="0"
          step="0.01"
          placeholder="Precio"
          value={price}
          onChange={e =>
            setPrice(e.target.value)
          }
          style={{
            width: 120,
            padding: 8,
            background: "#111",
            color: "white",
            border: "1px solid #444",
            borderRadius: 6
          }}
        />
      </div>


      {/* CATEGORÍA */}
      <div style={{ marginBottom: 10 }}>
        <select
          value={categoryId}
          onChange={e => {
            const value = e.target.value

            setCategoryId(
              value
                ? Number(value)
                : ""
            )
          }}
          style={{
            padding: 8,
            background: "#111",
            color: "white",
            border: "1px solid #444",
            borderRadius: 6
          }}
        >
          <option value="">
            Seleccionar categoría
          </option>

          {categories.map(category => (
            <option
              key={category.id}
              value={category.id}
            >
              {category.name}
            </option>
          ))}
        </select>
      </div>


      {/* ESTACIÓN */}
      <div style={{ marginBottom: 10 }}>
        <select
          value={stationId}
          onChange={e => {
            const value = e.target.value

            setStationId(
              value
                ? Number(value)
                : ""
            )
          }}
          style={{
            padding: 8,
            background: "#111",
            color: "white",
            border: "1px solid #444",
            borderRadius: 6
          }}
        >
          <option value="">
            Seleccionar estación
          </option>

          {stations.map(station => (
            <option
              key={station.id}
              value={station.id}
            >
              {station.name}
            </option>
          ))}
        </select>
      </div>


      {/* BOTONES */}
      <button
        className="btn btn-primary"
        onClick={handleSubmit}
        style={{ marginRight: 10 }}
      >
        Guardar
      </button>

      <button
        className="btn btn-primary"
        onClick={onCancel}
      >
        Cancelar
      </button>

    </div>
  )
}