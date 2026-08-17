export interface ChartPoint {
  date: string
  total: number
}

export interface ProductRankItem {
  product_id: number
  name: string
  category_id: number
  quantity: number
  total: number
}

export interface SalesReport {
  series: ChartPoint[]
  max_day: ChartPoint | null
  min_day: ChartPoint | null
}

export interface ProductsReport {
  today_best_seller: ProductRankItem | null
  top_products: ProductRankItem[]
  least_products: ProductRankItem[]
}

export interface SalesOrderItem {
  product_id: number
  product_name: string
  unit_price: number
  quantity: number
  line_total: number
}

export interface SalesOrder {
  order_id: number
  table_number: number | null
  closed_at: string | null
  items: SalesOrderItem[]
  subtotal: number
  discount: number
  total: number
}

export type RawChartPoint =
  Omit<ChartPoint, "total"> & {
    total: unknown
  }

export type RawProductRankItem =
  Omit<ProductRankItem, "total"> & {
    total: unknown
  }

export type RawSalesOrderItem =
  Omit<
    SalesOrderItem,
    "unit_price" | "line_total"
  > & {
    unit_price: unknown
    line_total: unknown
  }

export type RawSalesOrder =
  Omit<
    SalesOrder,
    | "items"
    | "subtotal"
    | "discount"
    | "total"
  > & {
    items: RawSalesOrderItem[]
    subtotal: unknown
    discount: unknown
    total: unknown
  }

export interface RawSalesReport {
  series: RawChartPoint[]
  max_day: RawChartPoint | null
  min_day: RawChartPoint | null
}

export interface RawProductsReport {
  today_best_seller:
    RawProductRankItem | null
  top_products: RawProductRankItem[]
  least_products: RawProductRankItem[]
}

export interface RawSalesOrdersReport {
  orders: RawSalesOrder[]
}

export interface RawProductEvolutionReport {
  series: RawChartPoint[]
}

export interface SalesOrdersReport {
  orders: SalesOrder[]
}

export interface ProductEvolutionReport {
  series: ChartPoint[]
}