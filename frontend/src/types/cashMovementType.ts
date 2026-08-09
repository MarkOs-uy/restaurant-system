/**
 * Movimientos de caja soportados por el sistema.
 */
export const CashMovementType = {
  CASH_IN: "cash_in",
  CASH_OUT: "cash_out"
} as const

export type CashMovementType = typeof CashMovementType[keyof typeof CashMovementType]