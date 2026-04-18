export const OrderStatus = {
  DRAFT: "DRAFT",
  OPEN: "OPEN",
  SENT: "SENT",
  IN_PROGRESS: "IN_PROGRESS",
  READY: "READY",
  CLOSED: "CLOSED",
  CANCELLED: "CANCELLED"
} as const

export type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus]