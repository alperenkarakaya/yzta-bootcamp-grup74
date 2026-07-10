import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import IntelligencePage from "./pages/IntelligencePage";
import PortfolioPage from "./pages/PortfolioPage";
import AuditPage from "./pages/AuditPage";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailPage from "./pages/CustomerDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<IntelligencePage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
