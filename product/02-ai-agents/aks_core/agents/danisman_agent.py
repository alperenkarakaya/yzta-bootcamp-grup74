"""
Agent 3 — Danışman Agent
------------------------
Sorumluluk: Skoru ve SHAP açıklamasını alır; kullanıcıya (a) skorun neden
böyle olduğunu sade dille anlatır, (b) skoru yükseltmek için somut, faktöre
özel öneriler üretir.

Varsayılan çalışma deterministik ve şablon tabanlıdır (API anahtarı gerekmez).
İsteğe bağlı LLM entegrasyonu için `llm_fonksiyonu` parametresi bırakılmıştır;
verilirse doğal dil metnini o üretir.
"""

ONERI_HARITASI = {
    "gider_gelir_orani": "Aylık giderini gelirinin altında tut; gider/gelir oranını 0.7'nin altına çekmek skoru belirgin yükseltir.",
    "bakiye_trendi": "Ay sonunu artı bakiyeyle kapat; düzenli tasarruf eğilimi en güçlü olumlu sinyallerden biri.",
    "gelir_duzenliligi": "Gelirini daha düzenli ve öngörülebilir hale getir; düzensiz aralıklar riski artırır.",
    "fatura_odeme_duzeni": "Faturalarını düzenli ve zamanında öde; ödeme düzeni güvenilirlik sinyalidir.",
    "gelir_kaynagi_sayisi": "Gelir kaynaklarını çeşitlendir; tek kaynağa bağımlılık kırılganlık yaratır.",
    "toplam_gelir_hacmi": "Hesap üzerinden geçen düzenli gelir hacmini artırmak kapasiteyi güçlendirir.",
    "hesap_hareket_yogunlugu": "Hesabını aktif ve düzenli kullanmak canlı hesap sinyali verir.",
}


class DanismanAgent:
    ad = "danisman_agent"

    def __init__(self, llm_fonksiyonu=None):
        self.llm = llm_fonksiyonu  # opsiyonel: metin -> metin

    def calistir(self, skor_sonucu, aciklama):
        aks = skor_sonucu["aks_skor"]
        seviye = skor_sonucu["risk_seviyesi"]

        pozitif = [f["faktor"] for f in aciklama["riski_azaltan"][:3]]
        ozet = (f"AKS skorun {aks}/850 ({seviye}). "
                + ("Skorunu en çok yukarı çeken faktörler: " + ", ".join(pozitif) + "." if pozitif else ""))

        oneriler = []
        for f in aciklama["riski_artiran"][:3]:
            metin = ONERI_HARITASI.get(f["kod"])
            if metin:
                oneriler.append(metin)
        if not oneriler:
            oneriler.append("Mevcut finansal davranışın güçlü; düzenli tasarruf ve ödeme alışkanlığını sürdür.")

        sonuc = {"ozet": ozet, "oneriler": oneriler}

        if self.llm:  # opsiyonel doğal dil zenginleştirme
            istem = (f"Kullanıcının kredi kapasite skoru {aks}/850. "
                     f"Skoru yükselten faktörler: {pozitif}. "
                     f"İyileştirme alanları: {[f['faktor'] for f in aciklama['riski_artiran'][:3]]}. "
                     "Kısa, samimi ve yapıcı bir finansal tavsiye yaz.")
            try:
                sonuc["dogal_dil"] = self.llm(istem)
            except Exception as e:
                sonuc["dogal_dil_hatasi"] = str(e)

        return sonuc
