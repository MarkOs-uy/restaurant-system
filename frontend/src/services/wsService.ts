import { parseWSEvent, type WSEventParsed } from "../ws"

const WS_URL = import.meta.env.VITE_WS_URL

type Listener = (event: WSEventParsed) => void

class WSService {

  private ws: WebSocket | null = null
  private listeners: Listener[] = []
  private reconnectTimer: any = null
  private stationId?: number
  private manuallyDisconnected = false

  connect(stationId?: number) {

    const normalizedStationId = stationId || undefined
    const stationChanged = this.stationId !== normalizedStationId

    this.stationId = normalizedStationId
    this.manuallyDisconnected = false

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (
      this.ws &&
      this.ws.readyState === WebSocket.OPEN &&
      !stationChanged
    ) {
      return
    }

    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }

    const token = localStorage.getItem("token")
    if (!token) return
    
    console.log("WS connect attempt", token)
    console.log("role:", localStorage.getItem("role"))
    console.log("station_id:", stationId)

    let url = `${WS_URL}/ws?token=${encodeURIComponent(token)}`

    if (this.stationId) {
      url += `&station_id=${this.stationId}`
    }

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log("WS global connected")
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
        this.connect(this.stationId)
      }, 2000)

    }

    this.ws.onerror = () => {
      this.ws?.close()
    }

  }

  disconnect() {

    this.manuallyDisconnected = true
    this.stationId = undefined

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }

    this.listeners = []

  }

  subscribe(listener: Listener) {
    this.listeners.push(listener)
  }

  unsubscribe(listener: Listener) {
    this.listeners = this.listeners.filter(l => l !== listener)
  }

}

export const wsService = new WSService()
