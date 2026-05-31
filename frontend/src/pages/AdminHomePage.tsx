import { Link } from "react-router-dom"

const adminActions = [
  {
    title: "Diseño del restaurant",
    description: "Ver y operar el plano de mesas.",
    to: "/"
  },
  {
    title: "Manejar Categorías",
    description: "Crear, editar y ordenar las categorías del menú.",
    to: "/admin/categories"
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
    title: "Reportes y Métricas",
    description: "Acceder próximamente al centro de reportes.",
    to: "/admin/reports"
  }
]

export default function AdminHomePage() {
  return (
    <main className="admin-home">
      <div className="admin-home__header">
        <p>Panel de administración</p>
        <h1>Inicio del Administrador</h1>
      </div>

      <section className="admin-home__grid" aria-label="Accesos principales">
        {adminActions.map((action) => (
          <Link className="admin-home__button" to={action.to} key={action.to}>
            <span>{action.title}</span>
            <small>{action.description}</small>
          </Link>
        ))}
      </section>
    </main>
  )
}
