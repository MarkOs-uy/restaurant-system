import type { OrderStatus } from "./orderStatus"
import type { OrderItemStatus } from "./orderItemStatus"

export interface OrderItem {
    id: number
    product_name: string
    quantity: number
    status: OrderItemStatus
}

export interface Order {
    id: number
    table_number: number
    status: OrderStatus
    created_at: string
    items: OrderItem[]
}