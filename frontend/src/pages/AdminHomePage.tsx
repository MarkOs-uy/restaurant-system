import { Link } from "react-router-dom"

interface AdminAction {
  title: string
  description: string
  to: string
}

const adminActions: AdminAction[] = [
  {
    title: "Diseño del restaurante",
    description: "Ver y configurar el plano de mesas.",
    to: "/"
  },
  {
    title: "Gestionar categorías",
    description: "Crear, editar y organizar las categorías del menú.",
    to: "/admin/categories"
  },
  {
    title: "Gestionar productos",
    description: "Crear, editar y activar productos del menú.",
    to: "/admin/products"
  },
  {
    title: "Gestionar estaciones",
    description: "Administrar las estaciones de cocina.",
    to: "/admin/stations"
  },
  {
    title: "Gestionar usuarios",
    description: "Gestionar accesos y roles del equipo.",
    to: "/admin/users"
  },
  {
    title: "Reportes y métricas",
    description: "Consultar ventas, productos y rendimiento.",
    to: "/admin/reports"
  },
  {
    title: "Backups",
    description: "Gestionar respaldos y configuración de copias de seguridad.",
    to: "/admin/backups"
  }
]

export default function AdminHomePage() {
  return (
    <main className="admin-home">

      <header className="admin-home__header">
        <p>Panel de administración</p>
        <h1>Administración</h1>
      </header>

      <section
        className="admin-home__grid"
        aria-label="Accesos de administración"
      >
        {adminActions.map(action => (
          <Link
            className="admin-home__button"
            to={action.to}
            key={action.to}
          >
            <span>{action.title}</span>
            <small>{action.description}</small>
          </Link>
        ))}
      </section>

    </main>
  )
}