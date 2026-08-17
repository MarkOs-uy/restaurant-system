/**
 * Interface de mesas
 */
export interface Table {
  id: number
  number: number
  x: number
  y: number
  capacity: number
  shape: TableShape
  status: string
  active: boolean
  order_id?: number | null
  order_status?: string | null
}

export interface InactiveTable {
  id: number
  number: number
  capacity: number
  shape: TableShape
  active: boolean
}

export interface TouchTableResponse {
  order_id: number | null
}

export interface TablePosition {
  id: number
  x: number
  y: number
}

export interface TableUpdate {
  number?: number
  capacity?: number
  shape?: TableShape
  active?: boolean
}

export const TableShape = {
  CIRCLE: "circle",
  SQUARE: "square",
  RECTANGLE_HORIZONTAL: "rectangle-horizontal",
  RECTANGLE_VERTICAL: "rectangle-vertical"
} as const

export type TableShape =
  typeof TableShape[keyof typeof TableShape]