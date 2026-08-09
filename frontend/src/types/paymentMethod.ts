/**
 * Métodos de pago soportados por el sistema.
 */
export const PaymentMethod = {
  CASH: "CASH",
  CARD: "CARD",
  TRANSFER: "TRANSFER",
  MERCADO_PAGO: "MERCADO_PAGO"
} as const

export type PaymentMethod = typeof PaymentMethod[keyof typeof PaymentMethod]