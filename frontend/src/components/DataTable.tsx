import type { ReactNode } from "react"

// ---------------------------------------------------------------------------------------------
// Tabla reutilizable para mostrar datos.
// El componente no impone estructura sobre las filas o columnas.
// ---------------------------------------------------------------------------------------------
interface Props {
  children: ReactNode
}

export default function DataTable({ children }: Props) {
  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse"
      }}
    >
      {children}
    </table>
  )
}