/**
 * Interface de estaciones
 */
export interface Station {
  id: number
  name: string
  active: boolean
}

export interface StationCreate {
  name: string
}

export interface StationUpdate {
  name: string
}