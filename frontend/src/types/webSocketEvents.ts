import { OrderStatus } from "./orderStatus"
import { OrderItemStatus } from "./orderItemStatus"

/**
 * Eventos Websocket
 */
export const WSEvent = {
  CASH_REGISTER_UPDATED: "CASH_REGISTER_UPDATED",
  CASH_MOVEMENT_ADDED: "CASH_MOVEMENT_ADDED",
  CASH_MOVEMENT_DELETED: "CASH_MOVEMENT_DELETED",

  ORDER_UPDATED: "ORDER_UPDATED",
  ORDER_STATUS_CHANGED: "ORDER_STATUS_CHANGED",
  ORDER_CLOSED: "ORDER_CLOSED",
  
  ITEM_STATUS_CHANGED: "ITEM_STATUS_CHANGED",
  NEW_ITEM: "NEW_ITEM",
  ITEM_READY: "ITEM_READY",

  PAYMENT_ADDED: "PAYMENT_ADDED",
  PAYMENT_DELETED: "PAYMENT_DELETED",

  TABLE_CREATED: "TABLE_CREATED",
  TABLE_UPDATED: "TABLE_UPDATED",
  TABLE_POSITION_UPDATED: "TABLE_POSITION_UPDATED",
  TABLE_ACTIVATED: "TABLE_ACTIVATED",
  TABLE_DEACTIVATED: "TABLE_DEACTIVATED",
  LAYOUT_UPDATED: "LAYOUT_UPDATED"

} as const

export type WSEvent = typeof WSEvent[keyof typeof WSEvent]

export interface OrderStatusChangedPayload {
  order_id: number
  status: OrderStatus
}

export interface ItemStatusChangedPayload {
  order_id: number
  item_id: number
  status: OrderItemStatus
}

export interface OrderUpdatedPayload {
  order_id: number
}

export interface OrderClosedPayload {
  order_id: number
}