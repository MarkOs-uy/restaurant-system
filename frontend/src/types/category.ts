import type { Product } from "./product"

/**
 * Interface de categorías
 */
export interface Category {
  id: number
  name: string
  active: boolean
}

export interface CategoryCreate {
  name: string
}

export interface CategoryUpdate {
  name: string
}

export interface CategoryWithProducts {
  id: number
  name: string
  active: boolean
  products: Product[]
}