import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import PortalLayout from "./components/PortalLayout";
import KurumLayout from "./components/KurumLayout";
import AnaSayfaPage from "./pages/AnaSayfaPage";
import GirisPage from "./pages/GirisPage";
import IntelligencePage from "./pages/IntelligencePage";
import PortfolioPage from "./pages/PortfolioPage";
import AuditPage from "./pages/AuditPage";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailPage from "./pages/CustomerDetailPage";
import CsvUploadPage from "./pages/CsvUploadPage";
import BulunamadiPage from "./pages/BulunamadiPage";
import PortalLoginPage from "./pages/portal/PortalLoginPage";
import PortalPage from "./pages/portal/PortalPage";
import PortalProfilPage from "./pages/portal/PortalProfilPage";
import PortalTaleplerPage from "./pages/portal/PortalTaleplerPage";
import PortalRizaPage from "./pages/portal/PortalRizaPage";
import KurumLoginPage from "./pages/kurum/KurumLoginPage";
import KurumMusterilerPage from "./pages/kurum/KurumMusterilerPage";
import KurumMusteriDetayPage from "./pages/kurum/KurumMusteriDetayPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Herkese açık ana sayfa — site kökü. Veri gösteren hiçbir şey yok,
            yalnızca ürünü anlatır ve doğru kapıya yönlendirir. */}
        <Route index element={<AnaSayfaPage />} />

        {/* Site geneli giriş — banka içi arayüzün önündeki zorunlu kapı */}
        <Route path="giris" element={<GirisPage />} />

        {/* Banka arayüzü (iç kullanım — demo/araştırma), YALNIZCA yönetici (bkz. Layout.tsx).
            Panel ana ekranı `/` iken `/panel`e taşındı (kök artık ana sayfa); diğer
            panel yolları geriye dönük uyumluluk için yerinde bırakıldı. */}
        <Route element={<Layout />}>
          <Route path="panel" element={<IntelligencePage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
          <Route path="upload" element={<CsvUploadPage />} />
        </Route>

        {/* Kullanıcı portalı (§3b Phase 6/7) — ayrı giriş + nav */}
        <Route path="portal/giris" element={<PortalLoginPage />} />
        <Route element={<PortalLayout />}>
          <Route path="portal" element={<PortalPage />} />
          <Route path="portal/profilim" element={<PortalProfilPage />} />
          <Route path="portal/erisim-talepleri" element={<PortalTaleplerPage />} />
          <Route path="portal/riza-defterim" element={<PortalRizaPage />} />
        </Route>

        {/* Kurum (banka) arayüzü (§3b Phase 7/7.2/7.4) — rıza-tabanlı gerçek müşteri erişimi */}
        <Route path="kurum/giris" element={<KurumLoginPage />} />
        <Route element={<KurumLayout />}>
          <Route path="kurum/musteriler" element={<KurumMusterilerPage />} />
          <Route path="kurum/musteri/:aksNo" element={<KurumMusteriDetayPage />} />
        </Route>

        {/* Eşleşmeyen her yol: aksi halde bomboş bir sayfa render ediliyordu. */}
        <Route path="*" element={<BulunamadiPage />} />
      </Routes>
    </BrowserRouter>
  );
}
