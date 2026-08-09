// ---------------------------------------------------------------------------------------------
// Convierte un valor desconocido a un número válido para operaciones monetarias.
//
// Si el valor es null, undefined o no puede convertirse en un número finito,
// devuelve 0.
// ---------------------------------------------------------------------------------------------
export function moneyToNumber(value: unknown): number {
    const amount = Number(value ?? 0)

    return Number.isFinite(amount)
        ? amount
        : 0
}