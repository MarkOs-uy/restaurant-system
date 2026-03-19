import "./App.css"
import { Routes, Route, Link } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"
import Kitchen from "./pages/Kitchen"
import WaiterPage from "./pages/Waiter"
import CashierPage from "./pages/CashierPage"
import LoginPage from "./pages/LoginPage"
import CategoriesPage from "./pages/CategoriesPage"
import StationsPage from "./pages/StationsPage"
import UsersPage from "./pages/UsersPage"
import ProductsPage from "./pages/ProductsPage"
import ProtectedRoute from "./components/ProtectedRoute"
import KitchenStations from "./pages/KitchenStations"
import { useState, useEffect } from "react"

function App() {
  const [role, setRole] = useState<string | null>(null)
  const isWaiter = role === "ADMIN" || role === "WAITER"
  const isKitchen = role === "ADMIN" || role === "KITCHEN"
  const isCashier = role === "ADMIN" || role === "CASHIER"
  const isAdmin = role === "ADMIN"
  const logout = () => {
    localStorage.clear()
    window.dispatchEvent(new Event("authChanged"))
    window.location.href = "/login"
}

    useEffect(() => {

    const loadRole = () => {
      const r = localStorage.getItem("role")
      setRole(r)
    }

    loadRole()

    window.addEventListener("authChanged", loadRole)

    return () => {
      window.removeEventListener("authChanged", loadRole)
    }

  }, [])
  
  console.log("APP ROLE:", role)
  
  return (
    <>
      {console.log("RENDER NAVBAR ROLE:", role)}
      {/* NAVBAR DINÁMICO */}
      {role && (
        <nav className="navbar" style={{ padding: 10 }}>
          <span className="navbar span" style={{ marginRight: 20 }}>
            Rol: <strong>{role}</strong>
          </span>

          {isWaiter && <Link to="/">Mesas</Link>}
          {isWaiter && <> | <Link to="/waiter">Mozo</Link></>}
          {isKitchen && <> | <Link to="/kitchen">Cocina</Link></>}
          {isCashier && <> | <Link to="/cashier">Caja</Link></>}

          {isAdmin && (
            <>
              {" | "}
              <Link to="/admin/products">Productos</Link>
              {" | "}
              <Link to="/admin/categories">Categorías</Link>
              {" | "}
              <Link to="/admin/stations">Estaciones</Link>
              {" | "}
              <Link to="/admin/users">Usuarios</Link>
            </>
          )}

          <button
            onClick={logout}
            style={{
              marginLeft: 20,
              padding: "4px 10px",
              cursor: "pointer"
            }}
          >
            Logout
          </button>
        </nav>
      )}

      <Routes>
        {/* LOGIN libre */}
        <Route path="/login" element={<LoginPage />} />

        {/* MESAS */}
        <Route
          path="/"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "WAITER"]}>
              <TablesPage />
            </ProtectedRoute>
          }
        />

        {/* DETALLE ORDEN */}
        <Route
          path="/orders/:orderId"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "WAITER"]}>
              <OrderDetail />
            </ProtectedRoute>
          }
        />

        {/* ORDEN NUEVA DESDE MESA */}
        <Route
          path="/orders/table/:tableId"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "WAITER"]}>
              <OrderDetail />
            </ProtectedRoute>
          }
        />

        {/* COCINA - SELECCIÓN */}
        <Route
          path="/kitchen"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "KITCHEN"]}>
              <KitchenStations />
            </ProtectedRoute>
          }
        />

        {/* COCINA - ESTACIÓN */}
        <Route
          path="/kitchen/:stationId"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "KITCHEN"]}>
              <Kitchen />
            </ProtectedRoute>
          }
        />

        {/* MOZOS */}
        <Route
          path="/waiter"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "WAITER"]}>
              <WaiterPage />
            </ProtectedRoute>
          }
        />

        {/* CAJA */}
        <Route
          path="/cashier"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "CASHIER"]}>
              <CashierPage />
            </ProtectedRoute>
          }
        />

        {/* ADMIN PRODUCTS */}
        <Route
          path="/admin/products"
          element={
            <ProtectedRoute allowedRoles={["ADMIN"]}>
              <ProductsPage />
            </ProtectedRoute>
          }
        />

        {/* ADMIN CATEGORIES */}
        <Route
          path="/admin/categories"
          element={
            <ProtectedRoute allowedRoles={["ADMIN"]}>
              <CategoriesPage />
            </ProtectedRoute>
          }
        />

        {/* ADMIN STATIONS */}
        <Route
          path="/admin/stations"
          element={
            <ProtectedRoute allowedRoles={["ADMIN"]}>
              <StationsPage />
            </ProtectedRoute>
          }
        />

        {/* ADMIN USERS */}
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={["ADMIN"]}>
              <UsersPage />
            </ProtectedRoute>
          }
        />

      </Routes>
    </>
  )
}

export default App
