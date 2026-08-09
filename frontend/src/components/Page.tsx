import type { ReactNode } from "react"

// ---------------------------------------------------------------------------------------------
// Contenedor base para las páginas de la aplicación.
// ---------------------------------------------------------------------------------------------
interface Props {
  title: string
  children: ReactNode
}

export default function Page({ title, children }: Props) {
  return (
    <div style={{ padding: 40 }}>
      <h1
        style={{
          marginBottom: 30,
          fontSize: 28
        }}
      >
        {title}
      </h1>

      {children}
    </div>
  )
}