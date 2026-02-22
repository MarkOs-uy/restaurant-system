import { Routes, Route, Link } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"
import Kitchen from "./pages/Kitchen"
import WaiterPage from "./pages/Waiter"
import CashierPage from "./pages/CashierPage"

function App() {
  return (
    <>
      <nav style={{ padding: 10, background: "#eee" }}>
        <Link to="/">Mesas</Link> |{" "}
        <Link to="/waiter">Mozo</Link> |{" "}
        <Link to="/kitchen">Cocina</Link> |{" "}
        <Link to="/cashier">Caja</Link>
      </nav>

      <Routes>
        <Route path="/" element={<TablesPage />} />
        <Route path="/orders/:orderId" element={<OrderDetail />} />
        <Route path="/kitchen/:stationId" element={<Kitchen />} />
        <Route path="/waiter" element={<WaiterPage />} />
        <Route path="/cashier" element={<CashierPage />} />
      </Routes>
    </>
  )
}

export default App
