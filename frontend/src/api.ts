import { logout } from "./services/auth"
import type { ApiError } from "./types/apiError"
import { handleApiError } from "./utils/handleApiError"

// ---------------------------------------------------------------------------------------------
// URL base de la API.
// En desarrollo puede definirse mediante VITE_API_URL.
// Si no existe, se utiliza /api.
// ---------------------------------------------------------------------------------------------
export const API_URL: string =
    import.meta.env.VITE_API_URL || "/api"

// ---------------------------------------------------------------------------------------------
// URL base del WebSocket.
// Si no se configura explícitamente, se utiliza el mismo host actual,
// cambiando automáticamente HTTP por WS o HTTPS por WSS.
// ---------------------------------------------------------------------------------------------
const defaultWsProtocol: string =
    window.location.protocol === "https:" ? "wss:" : "ws:"

export const WS_URL: string =
    import.meta.env.VITE_WS_URL ||
    `${defaultWsProtocol}//${window.location.host}`

// ---------------------------------------------------------------------------------------------
// Construye las cabeceras de autenticación utilizando el JWT almacenado localmente.
// ---------------------------------------------------------------------------------------------
export function getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem("token")

    return token
        ? {
              Authorization: `Bearer ${token}`
          }
        : {}
}

// ---------------------------------------------------------------------------------------------
// Opciones adicionales aceptadas por apiFetch.
// body puede ser un objeto que será convertido automáticamente a JSON,
// o cualquier BodyInit válido como FormData, string, Blob, etc.
// ---------------------------------------------------------------------------------------------
type ApiFetchOptions = Omit<RequestInit, "body"> & {
    body?: unknown
    suppressErrorToast?: boolean
}

// ---------------------------------------------------------------------------------------------
// Realiza una petición HTTP contra la API.
//
// - Agrega automáticamente el token JWT.
// - Serializa objetos como JSON.
// - Procesa respuestas JSON.
// - Maneja automáticamente errores de autenticación.
// - Muestra el toast correspondiente salvo que se solicite lo contrario.
// - Lanza un ApiError compatible con el sistema centralizado de errores.
// ---------------------------------------------------------------------------------------------
export async function apiFetch<T = unknown>(
    url: string,
    options: ApiFetchOptions = {}
): Promise<T> {

    const {
        suppressErrorToast,
        body: requestBody,
        ...fetchOptions
    } = options

    // -------------------------------------------------------------------------
    // Determina si el body debe serializarse como JSON.
    // FormData debe enviarse directamente para permitir que el navegador
    // establezca automáticamente su Content-Type con el boundary correspondiente.
    // -------------------------------------------------------------------------
    const isJsonBody =
        requestBody !== undefined &&
        requestBody !== null &&
        typeof requestBody === "object" &&
        !(requestBody instanceof FormData) &&
        !(requestBody instanceof Blob) &&
        !(requestBody instanceof ArrayBuffer)

    const body: BodyInit | undefined =
        isJsonBody
            ? JSON.stringify(requestBody)
            : requestBody as BodyInit | undefined

    const res = await fetch(`${API_URL}${url}`, {
        ...fetchOptions,
        body,
        headers: {
            ...getAuthHeaders(),
            ...(isJsonBody
                ? { "Content-Type": "application/json" }
                : {}),
            ...(fetchOptions.headers || {})
        }
    })

    // -------------------------------------------------------------------------
    // La API normalmente devuelve JSON.
    // Algunas respuestas pueden no tener body, por ejemplo un 204.
    // -------------------------------------------------------------------------
    let data: unknown = null

    try {
        data = await res.json()
    } catch {
        // Respuesta sin contenido JSON.
    }

    // -------------------------------------------------------------------------
    // Un 401 indica que la sesión dejó de ser válida.
    // No hacemos logout nuevamente cuando el propio login devuelve 401.
    // -------------------------------------------------------------------------
    if (
        res.status === 401 &&
        url !== "/auth/login"
    ) {
        logout()
    }

    // -------------------------------------------------------------------------
    // Normaliza cualquier respuesta HTTP de error al formato ApiError.
    // Esto permite que handleApiError tenga una única entrada para todos
    // los errores provenientes de la API.
    // -------------------------------------------------------------------------
    if (!res.ok) {

        const responseData =
            typeof data === "object" &&
            data !== null
                ? data as Record<string, unknown>
                : {}

        const error: ApiError = {
            code:
                typeof responseData.error === "string"
                    ? responseData.error as ApiError["code"]
                    : undefined,

            message:
                typeof responseData.detail === "string"
                    ? responseData.detail
                    : `HTTP ${res.status}`,

            context: responseData.context,

            status: res.status
        }

        if (!suppressErrorToast) {
            handleApiError(error)
        }

        throw error
    }

    return data as T
}
