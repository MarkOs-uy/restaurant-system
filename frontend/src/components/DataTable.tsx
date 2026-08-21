import type { ReactNode } from "react"

// ---------------------------------------------------------------------------------------------
// Tabla reutilizable para mostrar datos.
// El componente no impone estructura sobre las filas o columnas.
// Si el contenido supera el ancho disponible, permite desplazamiento horizontal.
// ---------------------------------------------------------------------------------------------
interface Props {
  children: ReactNode
  className?: string
}

export default function DataTable({
  children,
  className = ""
}: Props) {
  return (
    <div className="data-table-wrapper">
      <table
        className={`data-table ${className}`}
      >
        {children}
      </table>
    </div>
  )
}