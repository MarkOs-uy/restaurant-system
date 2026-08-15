/**
 * Interfaces de caja
 */
import { PaymentMethod } from "./paymentMethod"
import { CashMovementType } from "./cashMovementType"

/**
 * Movimiento de caja individual.
 */
export interface CashMovement {
  id: number
  type: CashMovementType
  amount: number
  reason: string
  created_at: string
}

/**
 * Información mostrada en el dashboard de caja.
 */
export interface CashRegisterDashboard {
  cash_register_id: number
  opened_at: string
  opening_amount: number
  total_sales: number
  orders_count: number
  transactions_count: number
  average_ticket: number
  by_method: Record<PaymentMethod, number>
  cash_movements: CashMovement[]
  expected_cash: number
}

/**
 * Información al cierre de caja.
 */
export interface CashRegisterCloseSummary {
    message: string
    total_sales: number
    transactions_count: number
    by_method: Record<PaymentMethod, number>
    opening_amount: number
    closing_amount: number
    cash_in: number
    cash_out: number
    expected_cash: number
    counted_cash: number
    difference: number
}

export type RawCashMovement =
  Omit<CashMovement, "amount"> & {
    amount: unknown
  }


export type RawCashRegisterDashboard =
  Omit<
    CashRegisterDashboard,
    | "opening_amount"
    | "total_sales"
    | "average_ticket"
    | "expected_cash"
    | "by_method"
    | "cash_movements"
  > & {
    opening_amount: unknown
    total_sales: unknown
    average_ticket: unknown
    expected_cash: unknown
    by_method: Record<PaymentMethod, unknown>
    cash_movements: RawCashMovement[]
  }


export type RawCashRegisterCloseSummary =
  Omit<
    CashRegisterCloseSummary,
    | "opening_amount"
    | "closing_amount"
    | "total_sales"
    | "cash_in"
    | "cash_out"
    | "expected_cash"
    | "counted_cash"
    | "difference"
    | "by_method"
  > & {
    opening_amount: unknown
    closing_amount: unknown
    total_sales: unknown
    cash_in: unknown
    cash_out: unknown
    expected_cash: unknown
    counted_cash: unknown
    difference: unknown
    by_method: Partial<Record<PaymentMethod, unknown>>
  }