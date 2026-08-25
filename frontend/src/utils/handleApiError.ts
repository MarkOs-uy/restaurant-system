import type { ApiError } from "../types/apiError"
import { ErrorCode } from "../types/domainErrors"
import { showToast } from "./showToast"

// --------------------------------------------------------------------------------------
// Extrae y normaliza un error proveniente de la API.
//
// El backend devuelve:
// {
//     error: "<error_code>",
//     detail: "<mensaje>",
//     context: {...}
// }
//
// Como los datos provenientes de una respuesta HTTP son externos a TypeScript,
// el código recibido se valida antes de asignarlo como ErrorCode.
// --------------------------------------------------------------------------------------
function extractApiError(error: unknown): ApiError {

    const err = error as {
        response?: {
            data?: {
                error?: unknown
                detail?: unknown
                context?: unknown
            }
            status?: number
        }
        code?: unknown
        message?: unknown
    }

    const rawCode =
        err.response?.data?.error ??
        err.code

    const code = isErrorCode(rawCode)
        ? rawCode
        : undefined

    const message =
        typeof err.response?.data?.detail === "string"
            ? err.response.data.detail
            : typeof err.message === "string"
                ? err.message
                : "Error inesperado"

    const rawContext = err.response?.data?.context

    return {
        code,
        message,
        context: isRecord(rawContext)
            ? rawContext
            : undefined,
        status: err.response?.status
    }
}

// --------------------------------------------------------------------------------------
// Comprueba si un valor recibido desde una fuente externa corresponde a uno de los
// códigos de error definidos por la aplicación.
// --------------------------------------------------------------------------------------
function isErrorCode(value: unknown): value is ErrorCode {

    return (
        typeof value === "string" &&
        Object.values(ErrorCode).includes(
            value as ErrorCode
        )
    )
}


function isRecord(value: unknown): value is Record<string, unknown> {
    return (
        typeof value === "object" &&
        value !== null &&
        !Array.isArray(value)
    )
}


// --------------------------------------------------------------------------------------
// Procesa un error de API y muestra al usuario el mensaje correspondiente.
// --------------------------------------------------------------------------------------
export function handleApiError(error: unknown): void {

    console.error("API ERROR:", error)

    const apiError = extractApiError(error)
    const message = mapErrorToMessage(apiError)

    showToast(message)
}

// --------------------------------------------------------------------------------------
// Traduce los códigos de error del backend a mensajes amigables para el usuario.
// --------------------------------------------------------------------------------------
function mapErrorToMessage(error: ApiError): string {

    const ERROR_MESSAGES: Partial<Record<ErrorCode, string>> = {

        // ORDERS
        [ErrorCode.ORDER_NOT_FOUND]:
            "La orden no existe",

        [ErrorCode.ORDER_ALREADY_CLOSED]:
            "La orden ya fue cerrada",

        [ErrorCode.ORDER_ITEMS_NOT_DELIVERED]:
            "No se puede cerrar la orden: hay items sin entregar",

        [ErrorCode.ORDER_EMPTY]:
            "La orden no tiene productos",

        [ErrorCode.ORDER_HAS_REMAINING_BALANCE]:
            "La orden aún tiene saldo pendiente",

        [ErrorCode.INVALID_TRANSITION]:
            "Transición de orden inválida",

        // ORDER ITEMS
        [ErrorCode.ITEM_NOT_FOUND]:
            "Item no encontrado",

        [ErrorCode.ITEM_NOT_IN_ORDER]:
            "El item no pertenece a la orden",

        [ErrorCode.ITEM_ALREADY_SENT]:
            "El item ya fue enviado a cocina",

        [ErrorCode.NOT_PENDING_ITEMS_TO_SEND]:
            "No hay items pendientes para enviar",

        [ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN]:
            "No tienes permisos para cambiar el estado del item",

        [ErrorCode.ITEM_INVALID_TRANSITION]:
            "Transición de estado del item inválida",

        // PAYMENTS
        [ErrorCode.PAYMENT_NOT_FOUND]:
            "Pago no encontrado",

        [ErrorCode.PAYMENT_INVALID_METHOD]:
            "Método de pago inválido",

        [ErrorCode.PAYMENT_EXCEEDS_REMAINING]:
            "El pago excede el saldo restante",

        // CASH REGISTER
        [ErrorCode.CASH_REGISTER_ALREADY_OPEN]:
            "Ya existe una caja abierta",

        [ErrorCode.CASH_REGISTER_ALREADY_CLOSED]:
            "La caja ya fue cerrada",

        [ErrorCode.CASH_REGISTER_NOT_OPEN]:
            "No hay una caja abierta",

        [ErrorCode.CASH_REGISTER_PENDING_ORDERS]:
            "No se puede cerrar la caja: hay órdenes abiertas",

        [ErrorCode.CASH_REGISTER_INVALID_COUNT]:
            "El importe contado no es válido",

        [ErrorCode.CASH_MOVEMENT_NOT_FOUND]:
            "Movimiento de caja no encontrado",

        // USERS
        [ErrorCode.USER_NOT_FOUND]:
            "Usuario no encontrado",

        [ErrorCode.USER_CANNOT_DEACTIVATE_SELF]:
            "No puedes desactivar tu propio usuario",

        [ErrorCode.USERNAME_ALREADY_EXISTS]:
            "Ya existe un usuario con ese nombre",

        // AUTH
        [ErrorCode.INVALID_TOKEN]:
            "El token de autenticación no es válido",

        [ErrorCode.INVALID_TOKEN_PAYLOAD]:
            "El token de autenticación no contiene datos válidos",

        [ErrorCode.USER_INACTIVE]:
            "El usuario está inactivo",

        [ErrorCode.ROLE_MISMATCH]:
            "El rol del usuario no coincide con el token",

        // EMAIL Y BACKUP
        [ErrorCode.INVALID_BACKUP_CONFIGURATION]:
            "La configuración del backup no es válida",

        [ErrorCode.EMAIL_NOT_CONFIGURED]:
            "El correo electrónico no está configurado",

        [ErrorCode.SMTP_NOT_CONFIGURED]:
            "SMTP no está configurado",

        [ErrorCode.SMTP_HOST_NOT_CONFIGURED]:
            "El servidor SMTP no está configurado",

        [ErrorCode.BACKUP_EMAIL_NOT_CONFIGURED]:
            "El correo para backups no está configurado",

        [ErrorCode.EMAIL_SEND_FAILURE]:
            "No se pudo enviar el correo",

        [ErrorCode.BACKUP_NOT_FOUND]:
            "Backup no encontrado",

        [ErrorCode.BACKUP_INVALID_PATH]:
            "La ruta del backup no es válida",

        [ErrorCode.BACKUP_DATABASE_NOT_FOUND]:
            "La base de datos del backup no fue encontrada",

        [ErrorCode.BACKUP_ENGINE_NOT_SUPPORTED]:
            "El motor de base de datos no está soportado",

        [ErrorCode.BACKUP_FAILED]:
            "El backup falló",

        // TABLES
        [ErrorCode.TABLE_NOT_FOUND]:
            "Mesa no encontrada",

        [ErrorCode.TABLE_NUMBER_ALREADY_EXISTS]:
            "El número de mesa ya existe",

        // PRODUCTS
        [ErrorCode.PRODUCT_NOT_FOUND]:
            "Producto no encontrado",

        [ErrorCode.PRODUCT_ALREADY_EXISTS]:
            "El producto ya existe",

        [ErrorCode.INVALID_PRODUCT_NAME]:
            "El nombre del producto no es válido",

        // CATEGORIES
        [ErrorCode.CATEGORY_NOT_FOUND]:
            "Categoría no encontrada",

        [ErrorCode.CATEGORY_ALREADY_EXISTS]:
            "La categoría ya existe",

        [ErrorCode.INVALID_CATEGORY_NAME]:
            "El nombre de la categoría no es válido",

        // STATIONS
        [ErrorCode.STATION_NOT_FOUND]:
            "Estación no encontrada",

        [ErrorCode.STATION_NAME_ALREADY_EXISTS]:
            "El nombre de estación ya existe",

        [ErrorCode.INVALID_STATION_NAME]:
            "El nombre de estación no es válido",

        // LAYOUT
        [ErrorCode.LAYOUT_BACKGROUND_INVALID_FORMAT]:
            "El formato de la imagen de fondo no es válido",

        [ErrorCode.LAYOUT_BACKGROUND_TOO_LARGE]:
            "La imagen de fondo es demasiado grande",

        // PERMISSIONS
        [ErrorCode.PERMISSION_DENIED]:
            "No tienes permisos para realizar esta acción",

        // REPORTS
        [ErrorCode.REPORT_INVALID_DATE_RANGE]:
            "El rango de fechas del reporte no es válido",

        // SETTINGS
        [ErrorCode.BACKUP_DESTINATION_REQUIRED]:
            "Debes indicar el destino del backup",

        [ErrorCode.BACKUP_WEEKDAY_REQUIRED]:
            "Debes indicar el día de la semana del backup",

        [ErrorCode.BACKUP_MONTHDAY_REQUIRED]:
            "Debes indicar el día del mes del backup"
    }

    return (
        (error.code
            ? ERROR_MESSAGES[error.code]
            : undefined) ??
        error.message ??
        "Error inesperado"
    )
}