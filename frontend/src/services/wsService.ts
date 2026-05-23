import { parseWSEvent, type WSEventParsed } from "../ws"

const defaultWsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
const WS_URL =
  import.meta.env.VITE_WS_URL || `${defaultWsProtocol}//${window.location.host}`

type Listener = (event: WSEventParsed) => void

class WSService {

  private ws: WebSocket | null = null
  private listeners: Listener[] = []
  private reconnectTimer: any = null
  private manuallyDisconnected = false

  connect() {

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
    if (!token) return

    const url = `${WS_URL}/ws?token=${encodeURIComponent(token)}`

    console.log("WS connecting")

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log("WS connected")
    }

    this.ws.onmessage = (event) => {

      const parsed = parseWSEvent(event)

      this.listeners.forEach(listener =>
        listener(parsed)
      )

    }

    this.ws.onclose = () => {

      console.log("WS closed")

      this.ws = null

      if (this.manuallyDisconnected) return

      this.reconnectTimer = setTimeout(() => {
        this.connect()
      }, 2000)

    }

    this.ws.onerror = () => {
      this.ws?.close()
    }

  }

  disconnect() {

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

  subscribe(listener: Listener) {
    this.listeners.push(listener)
  }

  unsubscribe(listener: Listener) {
    this.listeners = this.listeners.filter(l => l !== listener)
  }

}

export const wsService = new WSService()
