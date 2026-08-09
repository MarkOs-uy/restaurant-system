import type { ReactNode } from "react"

// ---------------------------------------------------------------------------------------------
// Contenedor visual reutilizable para agrupar contenido de la interfaz.
// ---------------------------------------------------------------------------------------------
interface Props {
  children: ReactNode
}

export default function Card({ children }: Props) {
  return <div className="card">{children}</div>
}