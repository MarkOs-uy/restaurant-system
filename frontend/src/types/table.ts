/**
 * Interface de mesas
 */
export interface Table {
  id: number
  number: number
  x: number
  y: number
  capacity: number
  shape: string
  status: string
  active: boolean
  order_id?: number | null
  order_status?: string | null
}

export interface InactiveTable {
  id: number
  number: number
  capacity: number
  shape: string
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