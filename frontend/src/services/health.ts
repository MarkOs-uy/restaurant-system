import { API_URL } from "../api"

// ---------------------------------------------------------------------------------------------
// Comprueba si el backend está disponible y responde correctamente.
// No requiere autenticación.
// ---------------------------------------------------------------------------------------------
export async function checkHealth(): Promise<boolean> {

    try {

        const response = await fetch(
            `${API_URL}/health`
        )

        if (!response.ok) {
            return false
        }

        const data = await response.json()

        return data.status === "ok"

    } catch {
        return false
    }
}

// ---------------------------------------------------------------------------------------------
// Espera hasta que el backend vuelva a estar disponible o se alcance el timeout.
// Se utiliza principalmente durante el arranque/reinicio de la aplicación.
// ---------------------------------------------------------------------------------------------
export async function waitForServer(
    timeout = 60000,
    interval = 2000
): Promise<boolean> {

    const deadline = Date.now() + timeout

    while (Date.now() < deadline) {

        if (await checkHealth()) {
            return true
        }

        await new Promise<void>(
            resolve => setTimeout(resolve, interval)
        )
    }

    return false
}