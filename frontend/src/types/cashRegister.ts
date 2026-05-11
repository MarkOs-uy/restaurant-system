import { PaymentMethod } from "./paymentMethod"
import { CashMovementType } from "./cashMovementType"

export interface CashMovement {
  id: number
  type: CashMovementType
  amount: number
  reason: string
  created_at: string
}

export interface CashRegisterDashboard {
  cash_register_id: number
  opened_at: string
  opening_amount: number
  total_sales: number
  orders_count: number
  average_ticket: number
  by_method: Record<PaymentMethod, number>
  expected_cash: number
  cash_movements: CashMovement[]
}

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
