import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import PortalLayout from "./components/PortalLayout";
import IntelligencePage from "./pages/IntelligencePage";
import PortfolioPage from "./pages/PortfolioPage";
import AuditPage from "./pages/AuditPage";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailPage from "./pages/CustomerDetailPage";
import CsvUploadPage from "./pages/CsvUploadPage";
import PortalLoginPage from "./pages/portal/PortalLoginPage";
import PortalPage from "./pages/portal/PortalPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Banka arayüzü (iç kullanım) */}
        <Route element={<Layout />}>
          <Route index element={<IntelligencePage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
          <Route path="upload" element={<CsvUploadPage />} />
        </Route>

        {/* Kullanıcı portalı (§3b Phase 6) — ayrı giriş + nav */}
        <Route path="portal/giris" element={<PortalLoginPage />} />
        <Route element={<PortalLayout />}>
          <Route path="portal" element={<PortalPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
