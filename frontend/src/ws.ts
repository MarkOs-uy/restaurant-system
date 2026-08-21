import type { WSEvent } from "./types/webSocketEvents.ts"

// ---------------------------------------------------------------------------------------------
// Representa un evento recibido desde el WebSocket una vez parseado.
// T permite indicar el tipo concreto del payload cuando sea necesario.
// ---------------------------------------------------------------------------------------------
export interface WSEventParsed<T = unknown> {
    type: WSEvent
    data: T
    payload: T
}

// ---------------------------------------------------------------------------------------------
// Parsea un mensaje recibido desde el WebSocket.
//
// El backend utiliza "payload" como estructura principal del evento.
// "data" se mantiene como compatibilidad por si algún evento antiguo utiliza
// ese nombre.
// ---------------------------------------------------------------------------------------------
export function parseWSEvent(event: MessageEvent): WSEventParsed {

    let evt: unknown

    try {
        evt = JSON.parse(event.data)
    } catch {
        throw new Error("Mensaje WebSocket inválido")
    }

    if (
        typeof evt !== "object" ||
        evt === null ||
        !("type" in evt)
    ) {
        throw new Error("Formato de evento WebSocket inválido")
    }

    const eventData = evt as {
        type: WSEvent
        payload?: unknown
        data?: unknown
    }

    const payload = eventData.payload ?? eventData.data ?? {}

    return {
        type: eventData.type,
        data: payload,
        payload
    }
}