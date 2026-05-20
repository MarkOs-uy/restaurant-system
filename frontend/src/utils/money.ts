export function moneyToNumber(value: unknown): number {
  const amount = Number(value ?? 0)
  return Number.isFinite(amount) ? amount : 0
}
