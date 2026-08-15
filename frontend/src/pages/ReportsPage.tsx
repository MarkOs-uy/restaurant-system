import { useEffect, useMemo, useState } from "react"
import { apiFetch } from "../api"
import { moneyToNumber } from "../utils/money"

import type { Product } from "../types/product"
import type { Category } from "../types/category"

import type { 
  ChartPoint,
  ProductRankItem,
  SalesReport,
  ProductsReport,
  SalesOrderItem,
  SalesOrdersReport,
  SalesOrder,
  RawChartPoint,
  RawProductEvolutionReport,
  RawProductRankItem,
  RawProductsReport,
  RawSalesOrder,
  RawSalesOrderItem,
  RawSalesOrdersReport,
  RawSalesReport
} from "../types/reports"

interface DateRangeProps {
  startDate: string
  endDate: string
  onStartDate: (value: string) => void
  onEndDate: (value: string) => void
}

interface LineChartProps {
  data: ChartPoint[]
  label: string
}

interface ProductTableProps {
  title: string
  items: ProductRankItem[]
}

interface SalesOrdersListProps {
  orders: SalesOrder[]
  startDate: string
  endDate: string
}



const money = new Intl.NumberFormat("es-UY", {
  style: "currency",
  currency: "UYU",
  maximumFractionDigits: 0
})

function toLocalDateString(
  date: Date
): string {
  const year = date.getFullYear()
  const month = String(
    date.getMonth() + 1
  ).padStart(2, "0")
  const day = String(
    date.getDate()
  ).padStart(2, "0")

  return `${year}-${month}-${day}`
}

const today = toLocalDateString(new Date())

function daysAgo(days: number) {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return toLocalDateString(date)
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("es-UY", {
    day: "2-digit",
    month: "2-digit"
  })
}

function formatFullDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  })
}

function formatDateTime(value: string | null) {
  if (!value) return "Sin fecha"

  return new Date(value).toLocaleString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  })
}

function normalizeChartPoint(
  point: RawChartPoint
): ChartPoint {
  return {
    ...point,
    total: moneyToNumber(point.total)
  }
}

function normalizeProductRankItem(
  item: RawProductRankItem
): ProductRankItem {
  return {
    ...item,
    total: moneyToNumber(item.total)
  }
}

function normalizeSalesOrderItem(
  item: RawSalesOrderItem
): SalesOrderItem {
  return {
    ...item,
    unit_price:
      moneyToNumber(item.unit_price),
    line_total:
      moneyToNumber(item.line_total)
  }
}

function normalizeSalesOrder(
  order: RawSalesOrder
): SalesOrder {
  return {
    ...order,

    subtotal:
      moneyToNumber(order.subtotal),

    discount:
      moneyToNumber(order.discount),

    total:
      moneyToNumber(order.total),

    items:
      order.items.map(
        normalizeSalesOrderItem
      )
  }
}

function normalizeSalesReport(
  data: RawSalesReport
): SalesReport {
  return {
    series:
      data.series.map(normalizeChartPoint),

    max_day:
      data.max_day
        ? normalizeChartPoint(data.max_day)
        : null,

    min_day:
      data.min_day
        ? normalizeChartPoint(data.min_day)
        : null
  }
}


function normalizeProductsReport(
  data: RawProductsReport
): ProductsReport {
  return {
    today_best_seller:
      data.today_best_seller
        ? normalizeProductRankItem(
            data.today_best_seller
          )
        : null,

    top_products:
      data.top_products.map(
        normalizeProductRankItem
      ),

    least_products:
      data.least_products.map(
        normalizeProductRankItem
      )
  }
}

function normalizeSalesOrdersReport(
  data: RawSalesOrdersReport
): SalesOrdersReport {
  return {
    orders:
      data.orders.map(
        normalizeSalesOrder
      )
  }
}

function buildQuery(params: Record<string, string>) {
  return new URLSearchParams(params).toString()
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;")
}

function buildSalesOrdersPrintHtml(
  orders: SalesOrder[],
  startDate: string,
  endDate: string,
  output: "pdf" | "print"
) {
  const total = orders.reduce((sum, order) => sum + order.total, 0)
  const title = output === "pdf" ? "Reporte de ventas para PDF" : "Reporte de ventas"

  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Ventas ${escapeHtml(formatFullDate(startDate))} - ${escapeHtml(formatFullDate(endDate))}</title>
        <style>
          @page { size: A4; margin: 16mm; }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            color: #111827;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            line-height: 1.35;
          }
          header {
            display: flex;
            justify-content: space-between;
            gap: 24px;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 2px solid #111827;
          }
          h1 {
            margin: 0 0 6px;
            font-size: 22px;
          }
          p {
            margin: 0;
          }
          .muted {
            color: #6b7280;
          }
          .summary {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 16px;
          }
          .summary div {
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
          }
          .summary span {
            display: block;
            color: #6b7280;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
          }
          .summary strong {
            display: block;
            margin-top: 4px;
            font-size: 16px;
          }
          .order {
            page-break-inside: avoid;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #d1d5db;
          }
          .order-header {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 8px;
          }
          .order-header h2 {
            margin: 0 0 4px;
            font-size: 15px;
          }
          .order-header strong {
            font-size: 15px;
            white-space: nowrap;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          th,
          td {
            padding: 7px 8px;
            border: 1px solid #d1d5db;
            text-align: left;
          }
          th {
            background: #f3f4f6;
            font-size: 11px;
            text-transform: uppercase;
          }
          .number {
            text-align: right;
            white-space: nowrap;
          }
          .center {
            text-align: center;
          }
          .totals {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 8px;
            font-weight: 700;
          }
        </style>
      </head>
      <body>
        <header>
          <div>
            <h1>${title}</h1>
            <p class="muted">Periodo: ${escapeHtml(formatFullDate(startDate))} al ${escapeHtml(formatFullDate(endDate))}</p>
          </div>
          <div>
            <p class="muted">Generado: ${escapeHtml(new Date().toLocaleString("es-UY"))}</p>
          </div>
        </header>

        <section class="summary">
          <div>
            <span>Ordenes vendidas</span>
            <strong>${orders.length}</strong>
          </div>
          <div>
            <span>Total vendido</span>
            <strong>${escapeHtml(money.format(total))}</strong>
          </div>
        </section>

        ${orders.map(order => `
          <section class="order">
            <div class="order-header">
              <div>
                <h2>Orden #${order.order_id}</h2>
                <p class="muted">${escapeHtml(order.table_number !== null ? `Mesa ${order.table_number}` : "Sin mesa")} - ${escapeHtml(formatDateTime(order.closed_at))}</p>
              </div>
              <strong>${escapeHtml(money.format(order.total))}</strong>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th class="number">Precio unitario</th>
                  <th class="center">Cantidad</th>
                  <th class="number">Total item</th>
                </tr>
              </thead>
              <tbody>
                ${order.items.map(item => `
                  <tr>
                    <td>${escapeHtml(item.product_name)}</td>
                    <td class="number">${escapeHtml(money.format(item.unit_price))}</td>
                    <td class="center">${item.quantity}</td>
                    <td class="number">${escapeHtml(money.format(item.line_total))}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>

            <div class="totals">
              <span>Subtotal ${escapeHtml(money.format(order.subtotal))}</span>
              ${order.discount > 0 ? `<span>Descuento -${escapeHtml(money.format(order.discount))}</span>` : ""}
              <span>Total ${escapeHtml(money.format(order.total))}</span>
            </div>
          </section>
        `).join("")}
      </body>
    </html>
  `
}

function printSalesOrders(
  orders: SalesOrder[],
  startDate: string,
  endDate: string,
  output: "pdf" | "print"
) {
  if (orders.length === 0) return

  const frame = document.createElement("iframe")
  frame.style.position = "fixed"
  frame.style.right = "0"
  frame.style.bottom = "0"
  frame.style.width = "0"
  frame.style.height = "0"
  frame.style.border = "0"
  document.body.appendChild(frame)

  const printDocument = frame.contentDocument
  const printWindow = frame.contentWindow

  if (!printDocument || !printWindow) {
    document.body.removeChild(frame)
    return
  }

  printDocument.open()
  printDocument.write(buildSalesOrdersPrintHtml(orders, startDate, endDate, output))
  printDocument.close()

  setTimeout(() => {
    printWindow.focus()
    printWindow.print()
    setTimeout(() => document.body.removeChild(frame), 1000)
  }, 150)
}

function LineChart({ data, label }: LineChartProps) {
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
}: DateRangeProps) {
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

function ProductTable({ title, items }: ProductTableProps) {
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

function SalesOrdersList({
  orders,
  startDate,
  endDate
}: SalesOrdersListProps) {
  const total = orders.reduce((sum, order) => sum + order.total, 0)

  return (
    <div className="sales-orders">
      <div className="sales-orders__actions">
        <button
          type="button"
          className="btn btn-report"
          onClick={() => printSalesOrders(orders, startDate, endDate, "pdf")}
          disabled={orders.length === 0}
        >
          Guardar como PDF
        </button>

        <button
          type="button"
          className="btn btn-report"
          onClick={() => printSalesOrders(orders, startDate, endDate, "print")}
          disabled={orders.length === 0}
        >
          Imprimir
        </button>
      </div>

      <div className="sales-orders__summary">
        <div>
          <span>Órdenes vendidas</span>
          <strong>{orders.length}</strong>
        </div>
        <div>
          <span>Total vendido</span>
          <strong>{money.format(total)}</strong>
        </div>
      </div>

      {orders.length === 0 ? (
        <div className="sales-orders__empty">Sin ventas realizadas para el rango seleccionado</div>
      ) : (
        <div className="sales-orders__list">
          {orders.map(order => (
            <article className="sales-order" key={order.order_id}>
              <div className="sales-order__header">
                <div>
                  <h3>Orden #{order.order_id}</h3>
                  <p>
                    {order.table_number !== null  ? `Mesa ${order.table_number}` : "Sin mesa"} ·{" "}
                    {formatDateTime(order.closed_at)}
                  </p>
                </div>
                <strong>{money.format(order.total)}</strong>
              </div>

              <div className="sales-order__table-wrap">
                <table className="sales-order__items">
                  <thead>
                    <tr>
                      <th>Ítem</th>
                      <th>Precio unitario</th>
                      <th>Cantidad</th>
                      <th>Total ítem</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.items.map(item => (
                      <tr key={item.item_id}>
                        <td>{item.product_name}</td>
                        <td>{money.format(item.unit_price)}</td>
                        <td>{item.quantity}</td>
                        <td>{money.format(item.line_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="sales-order__totals">
                <span>Subtotal {money.format(order.subtotal)}</span>
                {order.discount > 0 && <span>Descuento -{money.format(order.discount)}</span>}
                <strong>Total {money.format(order.total)}</strong>
              </div>
            </article>
          ))}
        </div>
      )}
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
  const [salesOrdersReport, setSalesOrdersReport] = useState<SalesOrdersReport | null>(null)
  const [productsReport, setProductsReport] = useState<ProductsReport | null>(null)
  const [productEvolution, setProductEvolution] = useState<ChartPoint[]>([])

  const filteredProducts = useMemo(() => {
    if (categoryId === "all") return products
    return products.filter(product => String(product.category_id) === categoryId)
  }, [categoryId, products])

  useEffect(() => {
    const loadFilters = async () => {
      const [categoriesData, productsData] = await Promise.all([
        apiFetch<Category[]>("/categories/?active=true"),
        apiFetch<Product[]>("/products/?active=true")
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
      const [salesData, salesOrdersData] = await Promise.all([
        apiFetch<RawSalesReport>(`/reports/sales?${query}`),
        apiFetch<RawSalesOrdersReport>(`/reports/sales/orders?${query}`)
      ])
      setSalesReport(
        normalizeSalesReport(salesData)
      )

      setSalesOrdersReport(
        normalizeSalesOrdersReport(
          salesOrdersData
        )
      )
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
      const data = await apiFetch<RawProductsReport>(`/reports/products?${buildQuery(params)}`)
      setProductsReport(normalizeProductsReport(data))
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
      const data = await apiFetch<RawProductEvolutionReport>(`/reports/products/${selectedProductId}/evolution?${query}`)
      setProductEvolution(data.series.map(normalizeChartPoint))
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

        <div className="sales-orders-block">
          <div className="report-section__header">
            <div>
              <p>Detalle de ventas</p>
              <h2>Ventas realizadas por orden</h2>
            </div>
          </div>

          <SalesOrdersList
            orders={salesOrdersReport?.orders || []}
            startDate={salesStartDate}
            endDate={salesEndDate}
          />
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
