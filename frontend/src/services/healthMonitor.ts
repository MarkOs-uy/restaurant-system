import { checkHealth } from "./health"
import { logout } from "./auth"

// ---------------------------------------------------------------------------------------------
// Monitoriza periódicamente la disponibilidad del backend.
// Si se producen varios fallos consecutivos, se cierra la sesión local.
// ---------------------------------------------------------------------------------------------

const HEALTH_CHECK_INTERVAL = 5000
const MAX_CONSECUTIVE_FAILURES = 3

let interval: ReturnType<typeof setInterval> | null = null
let consecutiveFailures = 0

// ---------------------------------------------------------------------------------------------
// Inicia el monitor de salud del backend.
// Si ya está iniciado, no crea un segundo monitor.
// ---------------------------------------------------------------------------------------------
export function startHealthMonitor(): void {

    if (interval) {
        return
    }

    interval = setInterval(
        async () => {

            const healthy = await checkHealth()

            if (healthy) {

                consecutiveFailures = 0

                return
            }

            consecutiveFailures++

            if (
                consecutiveFailures >=
                MAX_CONSECUTIVE_FAILURES
            ) {

                console.warn(
                    "Servidor no disponible"
                )

                stopHealthMonitor()
                logout()
            }

        },
        HEALTH_CHECK_INTERVAL
    )
}

// ---------------------------------------------------------------------------------------------
// Detiene el monitor de salud del backend.
// ---------------------------------------------------------------------------------------------
export function stopHealthMonitor(): void {

    if (!interval) {
        return
    }

    clearInterval(interval)

    interval = null
    consecutiveFailures = 0
}