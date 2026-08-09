/**
 * Roles de usuario usados por el sistema
 */
export const UserRole = {
  ADMIN: "ADMIN",
  WAITER: "WAITER",
  KITCHEN: "KITCHEN",
  CASHIER: "CASHIER"
} as const

export type UserRole =
  typeof UserRole[keyof typeof UserRole]