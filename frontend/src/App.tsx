import { Routes, Route } from "react-router-dom"
import TablesPage from "./pages/TablesPage"
import OrderDetail from "./pages/OrderDetail"

function App() {
  return (
    <Routes>
      <Route path="/" element={<TablesPage />} />
      <Route path="/orders/:orderId" element={<OrderDetail />} />
    </Routes>
  )
}

export default App
