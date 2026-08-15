import { Link } from "react-router-dom"

interface AdminAction {
  title: string
  description: string
  to: string
}

const adminActions: AdminAction[] = [
  {
    title: "Diseño del restaurante",
    description: "Ver y operar el plano de mesas.",
    to: "/"
  },
  {
    title: "Manejar categorías",
    description: "Crear, editar y ordenar las categorías del menú.",
    to: "/admin/categories"
  },
  {
  title: "Manejar productos",
  description: "Crear, editar y activar productos del menú.",
  to: "/admin/products"
  },
  {
    title: "Manejar estaciones",
    description: "Administrar las estaciones de cocina activas.",
    to: "/admin/stations"
  },
  {
    title: "Manejar usuarios",
    description: "Gestionar accesos y roles del equipo.",
    to: "/admin/users"
  },
  {
    title: "Reportes y métricas",
    description: "Acceder al centro de reportes.",
    to: "/admin/reports"
  },
  {
    title: "Backups",
    description: "Ver el último respaldo, generar uno nuevo y enviarlo por correo.",
    to: "/admin/backups"
  }
]

export default function AdminHomePage() {
  return (
    <main className="admin-home">
      <div className="admin-home__header">
        <p>Panel de administración</p>
        <h1>Inicio del Administrador</h1>
      </div>

      <section
        className="admin-home__grid"
        aria-label="Accesos principales"
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