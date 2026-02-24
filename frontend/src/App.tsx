import { Routes, Route, Link } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"
import Kitchen from "./pages/Kitchen"
import WaiterPage from "./pages/Waiter"
import CashierPage from "./pages/CashierPage"
import LoginPage from "./pages/LoginPage"
import ProtectedRoute from "./components/ProtectedRoute.tsx"

function App() {
  return (
    <>
      <nav style={{ padding: 10, background: "#eee" }}>
        <Link to="/">Mesas</Link> |{" "}
        <Link to="/waiter">Mozo</Link> |{" "}
        <Link to="/kitchen/1">Cocina</Link> |{" "}
        <Link to="/cashier">Caja</Link>
      </nav>

      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <TablesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/orders/:orderId"
          element={
            <ProtectedRoute>
              <OrderDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/kitchen/:stationId"
          element={
            <ProtectedRoute>
              <Kitchen />
            </ProtectedRoute>
          }
        />

        <Route
          path="/waiter"
          element={
            <ProtectedRoute>
              <WaiterPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/cashier"
          element={
            <ProtectedRoute>
              <CashierPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  )
}

export default App

