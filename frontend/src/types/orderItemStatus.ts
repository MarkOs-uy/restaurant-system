export const OrderItemStatus = {
  PENDING: "PENDING",
  SENT: "SENT",
  IN_PROGRESS: "IN_PROGRESS",
  READY: "READY",
  DELIVERED: "DELIVERED",
  CANCELLED: "CANCELLED"
} as const

export type OrderItemStatus = typeof OrderItemStatus[keyof typeof OrderItemStatus]