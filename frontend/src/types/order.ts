import type { OrderStatus } from "./orderStatus"
import type { OrderItemStatus } from "./orderItemStatus"
import type { PaymentMethod } from "./paymentMethod"

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

export interface OrderDetailItem {
  id: number
  product_name: string
  quantity: number
  unit_price: number
  status: OrderItemStatus
  notes?: string | null
}


export interface OrderPayment {
  id: number
  amount: number
  method: PaymentMethod
}


export interface OrderDetail {
  id: number
  table_id: number
  table_number: number
  status: OrderStatus
  items: OrderDetailItem[]
  subtotal: number
  payments: OrderPayment[]
  total: number
  total_paid: number
  remaining: number
  discount: number
}

export type RawOrderDetail = Omit<
  OrderDetail,
  | "items"
  | "payments"
  | "subtotal"
  | "total"
  | "total_paid"
  | "remaining"
  | "discount"
> & {
  items: Array<
    Omit<OrderDetailItem, "unit_price"> & {
      unit_price: unknown
    }
  >
  payments: Array<
    Omit<OrderPayment, "amount"> & {
      amount: unknown
    }
  >
  subtotal: unknown
  total: unknown
  total_paid: unknown
  remaining: unknown
  discount: unknown
}

export interface AddProductToTableResponse {
  order_id: number
}

export interface CashierOrder {
  id: number
  table_number: number
  status: OrderStatus
  subtotal: number
  total: number
  total_paid: number
  remaining: number
  discount: number
  payments: OrderPayment[]
}

export type RawOrderPayment =
  Omit<OrderPayment, "amount"> & {
    amount: unknown
  }

export type RawCashierOrder =
  Omit<
    CashierOrder,
    | "subtotal"
    | "total"
    | "total_paid"
    | "remaining"
    | "discount"
    | "payments"
  > & {
    subtotal: unknown
    total: unknown
    total_paid: unknown
    remaining: unknown
    discount: unknown
    payments: RawOrderPayment[]
  }