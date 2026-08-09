/**
 * Estados de pago soportados por el sistema.
 */
export const PaymentStatus = {
  PENDING: "PENDING",
  PAID: "PAID",
  CANCELLED: "CANCELLED"
} as const

export type PaymentStatus = typeof PaymentStatus[keyof typeof PaymentStatus]