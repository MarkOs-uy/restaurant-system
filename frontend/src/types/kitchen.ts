/**
 * Interfaces de cocina
 */
import type { OrderItemStatus } from "./orderItemStatus"

export interface KitchenItem {
  item_id: number
  product_name: string
  quantity: number
  status: OrderItemStatus
  table_number: number
  order_id: number
  created_at: string
  notes?: string | null
}