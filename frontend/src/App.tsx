import "./App.css"

import {
  Routes,
  Route,
  Link,
  Navigate
} from "react-router-dom"

import {
  useEffect,
  useState
} from "react"

import { Toaster } from "react-hot-toast"

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
import AdminHomePage from "./pages/AdminHomePage"
import ReportsPage from "./pages/ReportsPage"
import BackupsPage from "./pages/BackupsPage"
import KitchenStations from "./pages/KitchenStations"
import ManageTables from "./pages/ManageTables"

import ProtectedRoute from "./components/ProtectedRoute"

import {
  startHealthMonitor
} from "./services/healthMonitor"

import {
  wsService
} from "./services/wsService"

import {
  logout,
  readAuth
} from "./services/auth"

import { UserRole } from "./types/userRole"


function getHomeRoute(
  role: UserRole | null
): string {
  switch (role) {
    case UserRole.ADMIN:
      return "/admin"

    case UserRole.WAITER:
      return "/waiter"

    case UserRole.KITCHEN:
      return "/kitchen"

    case UserRole.CASHIER:
      return "/cashier"

    default:
      return "/login"
  }
}


function App() {
  const [role, setRole] =
    useState<UserRole | null>(null)

  const isWaiter =
    role === UserRole.ADMIN ||
    role === UserRole.WAITER

  const isKitchen =
    role === UserRole.ADMIN ||
    role === UserRole.KITCHEN

  const isCashier =
    role === UserRole.ADMIN ||
    role === UserRole.CASHIER

  const isAdmin =
    role === UserRole.ADMIN


  useEffect(() => {
    startHealthMonitor()
  }, [])


  useEffect(() => {
    const loadAuth = () => {
      const auth = readAuth()

      setRole(auth.role)

      if (auth.token) {
        wsService.connect()
      } else {
        wsService.disconnect()
      }
    }

    loadAuth()

    window.addEventListener(
      "authChanged",
      loadAuth
    )

    return () => {
      window.removeEventListener(
        "authChanged",
        loadAuth
      )

      wsService.disconnect()
    }
  }, [])


  useEffect(() => {

    const reconnectIfAuthenticated = () => {
      if (!localStorage.getItem("token")) {
        return
      }

      wsService.reconnect()
    }

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        reconnectIfAuthenticated()
      }
    }

    const handleOnline = () => {
      reconnectIfAuthenticated()
    }

    document.addEventListener(
      "visibilitychange",
      handleVisibilityChange
    )

    window.addEventListener(
      "online",
      handleOnline
    )

    return () => {
      document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange
      )

      window.removeEventListener(
        "online",
        handleOnline
      )
    }

  }, [])

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000
        }}
      />

      {role && (
        <nav className="navbar">
          <span style={{ marginRight: 20 }}>
            Rol: <strong>{role}</strong>
          </span>

          {isWaiter && (
            <Link to="/">Mesas</Link>
          )}

          {isWaiter && (
            <>
              {" | "}
              <Link to="/waiter">
                Mozo
              </Link>
            </>
          )}

          {isKitchen && (
            <>
              {" | "}
              <Link to="/kitchen">
                Cocina
              </Link>
            </>
          )}

          {isCashier && (
            <>
              {" | "}
              <Link to="/cashier">
                Caja
              </Link>
            </>
          )}

          {isAdmin && (
            <>
              {" | "}
              <Link to="/admin">
                Inicio Admin
              </Link>

              {" | "}
              <Link to="/tables/manage">
                Administración de Mesas
              </Link>

              {" | "}
              <Link to="/admin/products">
                Productos
              </Link>

              {" | "}
              <Link to="/admin/categories">
                Categorías
              </Link>

              {" | "}
              <Link to="/admin/stations">
                Estaciones
              </Link>

              {" | "}
              <Link to="/admin/users">
                Usuarios
              </Link>

              {" | "}
              <Link to="/admin/reports">
                Reportes
              </Link>

              {" | "}
              <Link to="/admin/backups">
                Backups
              </Link>
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
        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <AdminHomePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.WAITER
              ]}
            >
              <TablesPage
                isAdmin={isAdmin}
              />
            </ProtectedRoute>
          }
        />

        <Route
          path="/orders/:orderId"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.WAITER
              ]}
            >
              <OrderDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/orders/table/:tableId"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.WAITER
              ]}
            >
              <OrderDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/kitchen"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.KITCHEN
              ]}
            >
              <KitchenStations />
            </ProtectedRoute>
          }
        />

        <Route
          path="/kitchen/:stationId"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.KITCHEN
              ]}
            >
              <Kitchen />
            </ProtectedRoute>
          }
        />

        <Route
          path="/waiter"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.WAITER
              ]}
            >
              <WaiterPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/cashier"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN,
                UserRole.CASHIER
              ]}
            >
              <CashierPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/products"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <ProductsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/categories"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <CategoriesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/stations"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <StationsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <UsersPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/reports"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <ReportsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/backups"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <BackupsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tables/manage"
          element={
            <ProtectedRoute
              allowedRoles={[
                UserRole.ADMIN
              ]}
            >
              <ManageTables />
            </ProtectedRoute>
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to={getHomeRoute(role)}
              replace
            />
          }
        />
      </Routes>
    </>
  )
}

export default App