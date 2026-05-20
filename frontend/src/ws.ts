export interface WSEventParsed<T = any> {
  type: string
  data: T
}

export function parseWSEvent(event: MessageEvent): WSEventParsed {

  const evt = JSON.parse(event.data)

  return {
    type: evt.type,
    data: evt.payload ?? evt.data ?? {}
  }

}