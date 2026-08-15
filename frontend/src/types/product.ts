/**
 * Interface de producto
 */
import type { Category } from "./category"
import type { Station } from "./station"


export interface Product {
  id: number
  name: string
  price: number
  active: boolean
  category_id: number
  station_id: number

  category?: Pick<Category, "id" | "name">
  station?: Pick<Station, "id" | "name">
}


export interface ProductCreate {
  name: string
  price: number
  category_id: number
  station_id: number
}


export interface ProductUpdate {
  name?: string
  price?: number
  category_id?: number
  station_id?: number
}