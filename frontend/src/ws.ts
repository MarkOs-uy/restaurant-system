export interface WSEventParsed<T = any> {
  type: string
  data: T
  payload: T
}

export function parseWSEvent(event: MessageEvent): WSEventParsed {

  const evt = JSON.parse(event.data)

  const payload = evt.payload ?? evt.data ?? {}

  return {
    type: evt.type,
    data: payload,
    payload
  }

}
