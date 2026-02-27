import { Routes, Route, Link } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"
import Kitchen from "./pages/Kitchen"
import WaiterPage from "./pages/Waiter"
import CashierPage from "./pages/CashierPage"
import LoginPage from "./pages/LoginPage"
import ProtectedRoute from "./components/ProtectedRoute"

function App() {
  const role = localStorage.getItem("role")

  const logout = () => {
    localStorage.clear()
    window.location.href = "/login"
  }

  return (
    <>
      {/* NAVBAR DINÁMICO */}
      {role && (
        <nav style={{ padding: 10, background: "#eee" }}>
          <span style={{ marginRight: 20 }}>
            Rol: <strong>{role}</strong>
          </span>

          {(role === "ADMIN" || role === "WAITER") && (
            <>
              <Link to="/">Mesas</Link> |{" "}
            </>
          )}

          {(role === "ADMIN" || role === "WAITER") && (
            <>
              <Link to="/waiter">Mozo</Link> |{" "}
            </>
          )}

          {(role === "ADMIN" || role === "KITCHEN") && (
            <>
              <Link to="/kitchen/1">Cocina</Link> |{" "}
            </>
          )}

          {(role === "ADMIN" || role === "CASHIER") && (
            <>
              <Link to="/cashier">Caja</Link> |{" "}
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
