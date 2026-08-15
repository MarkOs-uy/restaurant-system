/**
 * Métodos de pago soportados por el sistema.
 */
export const PaymentMethod = {
  CASH: "CASH",
  CARD: "CARD",
  TRANSFER: "TRANSFER",
  OTHER: "OTHER"
} as const

export type PaymentMethod =
  typeof PaymentMethod[keyof typeof PaymentMethod]