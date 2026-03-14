import { useState, useEffect } from "react"

interface Category {
  id: number
  name: string
}

interface Station {
  id: number
  name: string
}

interface Product {
  id?: number
  name: string
  price: number
  category_id: number
  station_id: number
}

interface Props {
  product: Product | null
  categories: Category[]
  stations: Station[]
  onSave: (product: Product) => void
  onCancel: () => void
}

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

  useEffect(() => {

    if (product) {
      setName(product.name)
      setPrice(String(product.price))
      setCategoryId(product.category_id)
      setStationId(product.station_id)
    }

  }, [product])

  const handleSubmit = () => {

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

      {/* CATEGORIA */}

      <div style={{ marginBottom: 10 }}>
        <select
          value={categoryId}
          onChange={(e) => setCategoryId(Number(e.target.value))}
          style={{ padding: 5 }}
        >
          <option value="">Seleccionar categoría</option>

          {categories.map(c => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* ESTACION */}

      <div style={{ marginBottom: 10 }}>
        <select
          value={stationId}
          onChange={(e) => setStationId(Number(e.target.value))}
          style={{ padding: 5 }}
        >
          <option value="">Seleccionar estación</option>

          {stations.map(s => (
            <option key={s.id} value={s.id}>
              {s.name}
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