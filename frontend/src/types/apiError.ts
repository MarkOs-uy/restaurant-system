import type { ErrorCode } from "./domainErrors";

export interface ApiError {
    code?: ErrorCode
    message?: string
    context?: unknown
    status?: number
}

export function isApiError(
  value: unknown
): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    "status" in value &&
    typeof value.status === "number" &&
    "message" in value &&
    typeof value.message === "string"
  )
}