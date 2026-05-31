import { useEffect, useMemo, useState } from "react"
import { apiFetch } from "../api"

interface Category {
  id: number
  name: string
}

interface Product {
  id: number
  name: string
  category_id: number
}

interface ChartPoint {
  date: string
  total: number
}

interface ProductRankItem {
  product_id: number
  name: string
  category_id: number
  quantity: number
  total: number
}

interface SalesReport {
  series: ChartPoint[]
  max_day: ChartPoint | null
  min_day: ChartPoint | null
}

interface ProductsReport {
  today_best_seller: ProductRankItem | null
  top_products: ProductRankItem[]
  least_products: ProductRankItem[]
}

const money = new Intl.NumberFormat("es-UY", {
  style: "currency",
  currency: "UYU",
  maximumFractionDigits: 0
})

const today = new Date().toISOString().slice(0, 10)

function daysAgo(days: number) {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().slice(0, 10)
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("es-UY", {
    day: "2-digit",
    month: "2-digit"
  })
}

function buildQuery(params: Record<string, string>) {
  return new URLSearchParams(params).toString()
}

function LineChart({ data, label }: { data: ChartPoint[]; label: string }) {
  const width = 720
  const height = 240
  const padding = 28
  const max = Math.max(...data.map(point => point.total), 0)
  const hasData = data.some(point => point.total > 0)
  const chartWidth = width - padding * 2
  const chartHeight = height - padding * 2
  const points = data.map((point, index) => {
    const x = padding + (data.length <= 1 ? 0 : (index / (data.length - 1)) * chartWidth)
    const y = padding + chartHeight - (max ? (point.total / max) * chartHeight : 0)
    return { ...point, x, y }
  })
  const line = points.map(point => `${point.x},${point.y}`).join(" ")
  const maxPoint = points.length > 0
    ? points.reduce((best, point) => point.total > best.total ? point : best)
    : null

  return (
    <div className="report-chart" aria-label={label}>
      {hasData ? (
        <svg viewBox={`0 0 ${width} ${height}`} role="img">
          <text className="report-chart__axis-label" x={padding} y={18}>
            {money.format(max)}
          </text>
          <text className="report-chart__axis-label" x={padding} y={height - 6}>
            {points[0] ? formatDate(points[0].date) : ""}
          </text>
          <text className="report-chart__axis-label" x={width - padding} y={height - 6} textAnchor="end">
            {points[points.length - 1] ? formatDate(points[points.length - 1].date) : ""}
          </text>
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} />
          <polyline points={line} />
          {maxPoint && (
            <g>
              <text
                className="report-chart__point-label"
                x={Math.min(maxPoint.x + 10, width - 170)}
                y={Math.max(maxPoint.y - 10, 18)}
              >
                Máx. {money.format(maxPoint.total)}
              </text>
            </g>
          )}
          {points.map(point => (
            <circle key={`${point.date}-${point.total}`} cx={point.x} cy={point.y} r="4">
              <title>
                {formatDate(point.date)} - {money.format(point.total)}
              </title>
            </circle>
          ))}
        </svg>
      ) : (
        <div className="report-chart__empty">Sin ventas registradas para el rango seleccionado</div>
      )}
    </div>
  )
}

function DateRange({
  startDate,
  endDate,
  onStartDate,
  onEndDate
}: {
  startDate: string
  endDate: string
  onStartDate: (value: string) => void
  onEndDate: (value: string) => void
}) {
  return (
    <div className="report-filters">
      <label>
        Desde
        <input type="date" value={startDate} onChange={event => onStartDate(event.target.value)} />
      </label>

      <label>
        Hasta
        <input type="date" value={endDate} onChange={event => onEndDate(event.target.value)} />
      </label>
    </div>
  )
}

function ProductTable({ title, items }: { title: string; items: ProductRankItem[] }) {
  return (
    <div className="report-rank">
      <h3>{title}</h3>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <tr>
              <td colSpan={4}>Sin datos para el rango seleccionado</td>
            </tr>
          ) : (
            items.map((item, index) => (
              <tr key={item.product_id}>
                <td>{index + 1}</td>
                <td>{item.name}</td>
                <td>{item.quantity}</td>
                <td>{money.format(item.total)}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default function ReportsPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [salesStartDate, setSalesStartDate] = useState(daysAgo(30))
  const [salesEndDate, setSalesEndDate] = useState(today)
  const [productStartDate, setProductStartDate] = useState(daysAgo(30))
  const [productEndDate, setProductEndDate] = useState(today)
  const [productEvolutionStartDate, setProductEvolutionStartDate] = useState(daysAgo(30))
  const [productEvolutionEndDate, setProductEvolutionEndDate] = useState(today)
  const [categoryId, setCategoryId] = useState("all")
  const [selectedProductId, setSelectedProductId] = useState("")
  const [salesReport, setSalesReport] = useState<SalesReport | null>(null)
  const [productsReport, setProductsReport] = useState<ProductsReport | null>(null)
  const [productEvolution, setProductEvolution] = useState<ChartPoint[]>([])

  const filteredProducts = useMemo(() => {
    if (categoryId === "all") return products
    return products.filter(product => String(product.category_id) === categoryId)
  }, [categoryId, products])

  useEffect(() => {
    const loadFilters = async () => {
      const [categoriesData, productsData] = await Promise.all([
        apiFetch("/categories/"),
        apiFetch("/products/")
      ])

      setCategories(categoriesData)
      setProducts(productsData)
      setSelectedProductId(productsData[0] ? String(productsData[0].id) : "")
    }

    loadFilters()
  }, [])

  useEffect(() => {
    const loadSales = async () => {
      const query = buildQuery({
        start_date: salesStartDate,
        end_date: salesEndDate
      })
      setSalesReport(await apiFetch(`/reports/sales?${query}`))
    }

    loadSales()
  }, [salesStartDate, salesEndDate])

  useEffect(() => {
    const loadProductsReport = async () => {
      const params: Record<string, string> = {
        start_date: productStartDate,
        end_date: productEndDate
      }

      if (categoryId !== "all") {
        params.category_id = categoryId
      }

      setProductsReport(await apiFetch(`/reports/products?${buildQuery(params)}`))
    }

    loadProductsReport()
  }, [productStartDate, productEndDate, categoryId])

  useEffect(() => {
    if (!selectedProductId) {
      setProductEvolution([])
      return
    }

    const loadProductEvolution = async () => {
      const query = buildQuery({
        start_date: productEvolutionStartDate,
        end_date: productEvolutionEndDate
      })
      const data = await apiFetch(`/reports/products/${selectedProductId}/evolution?${query}`)
      setProductEvolution(data.series)
    }

    loadProductEvolution()
  }, [selectedProductId, productEvolutionStartDate, productEvolutionEndDate])

  useEffect(() => {
    if (filteredProducts.length === 0) {
      setSelectedProductId("")
      return
    }

    if (!filteredProducts.some(product => String(product.id) === selectedProductId)) {
      setSelectedProductId(String(filteredProducts[0].id))
    }
  }, [filteredProducts, selectedProductId])

  return (
    <main className="reports-page reports-page--dashboard">
      <header className="reports-header">
        <p>Reportes y métricas</p>
        <h1>Centro de Reportes</h1>
      </header>

      <section className="report-section">
        <div className="report-section__header">
          <div>
            <p>Sección ventas</p>
            <h2>Evolución de ventas</h2>
          </div>

          <DateRange
            startDate={salesStartDate}
            endDate={salesEndDate}
            onStartDate={setSalesStartDate}
            onEndDate={setSalesEndDate}
          />
        </div>

        <LineChart data={salesReport?.series || []} label="Evolución de ventas" />

        <div className="sales-summary">
          <div>
            <span>Mayor venta diaria</span>
            <strong>
              {salesReport?.max_day
                ? `${formatDate(salesReport.max_day.date)} - ${money.format(salesReport.max_day.total)}`
                : "Sin datos"}
            </strong>
          </div>

          <div>
            <span>Menor venta diaria</span>
            <strong>
              {salesReport?.min_day
                ? `${formatDate(salesReport.min_day.date)} - ${money.format(salesReport.min_day.total)}`
                : "Sin datos"}
            </strong>
          </div>
        </div>
      </section>

      <section className="report-section">
        <div className="report-section__header">
          <div>
            <p>Sección productos</p>
            <h2>Rendimiento de productos</h2>
          </div>

          <div className="report-filters">
            <label>
              Categoría
              <select value={categoryId} onChange={event => setCategoryId(event.target.value)}>
                <option value="all">Todos los productos</option>
                {categories.map(category => (
                  <option value={category.id} key={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="today-product">
          <span>Producto más vendido hoy</span>
          <strong>{productsReport?.today_best_seller?.name || "Sin ventas hoy"}</strong>
          {productsReport?.today_best_seller && (
            <small>
              {productsReport.today_best_seller.quantity} vendidos -{" "}
              {money.format(productsReport.today_best_seller.total)}
            </small>
          )}
        </div>

        <DateRange
          startDate={productStartDate}
          endDate={productEndDate}
          onStartDate={setProductStartDate}
          onEndDate={setProductEndDate}
        />

        <div className="product-ranks-grid">
          <ProductTable title="Top 10 más vendidos" items={productsReport?.top_products || []} />
          <ProductTable title="Top 10 menos vendidos" items={productsReport?.least_products || []} />
        </div>

        <div className="product-evolution">
          <div className="report-section__header">
            <div>
              <p>Producto seleccionado</p>
              <h2>Evolución de ventas por producto</h2>
            </div>

            <div className="report-filters">
              <label>
                Producto
                <select
                  value={selectedProductId}
                  onChange={event => setSelectedProductId(event.target.value)}
                  disabled={filteredProducts.length === 0}
                >
                  {filteredProducts.map(product => (
                    <option value={product.id} key={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <DateRange
            startDate={productEvolutionStartDate}
            endDate={productEvolutionEndDate}
            onStartDate={setProductEvolutionStartDate}
            onEndDate={setProductEvolutionEndDate}
          />

          <LineChart data={productEvolution} label="Evolución de ventas por producto" />
        </div>
      </section>
    </main>
  )
}
