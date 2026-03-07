import { Routes, Route, Link } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"
import Kitchen from "./pages/Kitchen"
import WaiterPage from "./pages/Waiter"
import CashierPage from "./pages/CashierPage"
import LoginPage from "./pages/LoginPage"
import ProtectedRoute from "./components/ProtectedRoute"
import { useState, useEffect } from "react"

function App() {
  const [role, setRole] = useState<string | null>(null)
  const isWaiter = role === "ADMIN" || role === "WAITER"
  const isKitchen = role === "ADMIN" || role === "KITCHEN"
  const isCashier = role === "ADMIN" || role === "CASHIER"
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
        <nav style={{ padding: 10, background: "#eee" }}>
          <span style={{ marginRight: 20 }}>
            Rol: <strong>{role}</strong>
          </span>

            {isWaiter && <Link to="/">Mesas</Link>}
            {isWaiter && <> | <Link to="/waiter">Mozo</Link></>}
            {isKitchen && <> | <Link to="/kitchen/1">Cocina</Link></>}
            {isCashier && <> | <Link to="/cashier">Caja</Link></>}

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

        {/* COCINA */}
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
      </Routes>
    </>
  )
}

export default App
