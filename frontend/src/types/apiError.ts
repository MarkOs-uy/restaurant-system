import type { ErrorCode } from "./domainErrors";

export interface ApiError {
    code?: ErrorCode
    message?: string
    context?: unknown
    status?: number
}