import {
    parseWSEvent,
    type WSEventParsed
} from "../ws"

import { WS_URL } from "../api"

// ---------------------------------------------------------------------------------------------
// Listener utilizado por los componentes que desean recibir eventos WebSocket.
// ---------------------------------------------------------------------------------------------
type Listener = (event: WSEventParsed) => void

class WSService {

    private ws: WebSocket | null = null

    private listeners: Listener[] = []

    private reconnectTimer: ReturnType<typeof setTimeout> | null = null

    private manuallyDisconnected = false

    // -----------------------------------------------------------------------------------------
    // Establece la conexión WebSocket si no existe una conexión activa.
    // -----------------------------------------------------------------------------------------
    connect(): void {

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }

        if (
            this.ws &&
            (
                this.ws.readyState === WebSocket.OPEN ||
                this.ws.readyState === WebSocket.CONNECTING
            )
        ) {
            return
        }

        this.manuallyDisconnected = false

        const token = localStorage.getItem("token")

        if (!token) {
            return
        }

        const url =
            `${WS_URL}/ws?token=${encodeURIComponent(token)}`

        console.log("WS connecting")

        this.ws = new WebSocket(url)

        // -------------------------------------------------------------------------------------
        // Conexión establecida.
        // -------------------------------------------------------------------------------------
        this.ws.onopen = () => {
            console.log("WS connected")
        }

        // -------------------------------------------------------------------------------------
        // Mensaje recibido.
        // -------------------------------------------------------------------------------------
        this.ws.onmessage = (event: MessageEvent) => {

            try {

                const parsed = parseWSEvent(event)

                this.listeners.forEach(listener => {
                    listener(parsed)
                })

            } catch (error) {

                console.error(
                    "WS message error:",
                    error
                )
            }
        }

        // -------------------------------------------------------------------------------------
        // Conexión cerrada.
        //
        // Si el cierre no fue solicitado explícitamente por la aplicación,
        // se programa automáticamente una reconexión.
        // -------------------------------------------------------------------------------------
        this.ws.onclose = () => {

            console.log("WS closed")

            this.ws = null

            if (this.manuallyDisconnected) {
                return
            }

            this.reconnectTimer = setTimeout(() => {
                this.connect()
            }, 2000)
        }

        // -------------------------------------------------------------------------------------
        // Ante un error, cerramos la conexión para que onclose gestione
        // el proceso de reconexión.
        // -------------------------------------------------------------------------------------
        this.ws.onerror = () => {
            this.ws?.close()
        }
    }

    // -----------------------------------------------------------------------------------------
    // Cierra la conexión WebSocket y evita la reconexión automática.
    // -----------------------------------------------------------------------------------------
    disconnect(): void {

        this.manuallyDisconnected = true

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }

        if (this.ws) {

            this.ws.onclose = null

            this.ws.close()

            this.ws = null
        }
    }

    // -----------------------------------------------------------------------------------------
    // Registra un listener para recibir eventos WebSocket.
    //
    // Devuelve una función que permite eliminarlo.
    // -----------------------------------------------------------------------------------------
    subscribe(listener: Listener): () => void {

        this.listeners.push(listener)

        return () => {
            this.unsubscribe(listener)
        }
    }

    // -----------------------------------------------------------------------------------------
    // Elimina un listener previamente registrado.
    // -----------------------------------------------------------------------------------------
    unsubscribe(listener: Listener): void {

        this.listeners = this.listeners.filter(
            current => current !== listener
        )
    }
}

export const wsService = new WSService()