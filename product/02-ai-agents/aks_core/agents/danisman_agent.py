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

# kod -> (yon, metin)
#
# `yon`, riski AZALTMAK için özelliğin hangi yöne gitmesi gerektiğidir ve
# modelin ÖĞRENDİĞİ katsayı işaretiyle uyumlu olmak ZORUNDADIR:
# katsayı > 0 (değer arttıkça risk artar) -> "azalt", katsayı < 0 -> "artir".
# `tests/test_danisman_yon.py` bunu eğitilmiş modele karşı doğrular; model
# yeniden eğitilir de bir yön değişirse test kırılır ve ürün sessizce yanlış
# tavsiye vermeye başlamaz.
#
# `metin=None`: modelin öğrendiği yön sezgiye aykırı ve davranışsal bir
# tavsiye olarak savunulabilir değil — kullanıcıya ters yönde eylem önermek
# yerine o faktör için hiçbir şey söylenmez (bkz. overview.md §5: doğruluk >
# iş değeri; "hedef arama" yasağı).
ONERI_HARITASI = {
    "gider_gelir_orani": ("azalt", "Aylık giderini gelirinin altında tut; gider/gelir oranını 0.7'nin altına çekmek skoru belirgin yükseltir."),
    "toplam_gider_hacmi": ("azalt", "Dönem içindeki toplam harcama hacmini kısmak, bu profilde riski en çok düşüren adımlardan biri."),
    "gelir_kaynagi_sayisi": ("azalt", "Gelirini çok sayıda küçük kaleme dağıtmak yerine ana gelir kaynağını güçlendir; model dağınık gelir yapısını istikrar değil kırılganlık sinyali olarak okuyor."),
    "gelir_duzenliligi": ("azalt", None),
    "bakiye_trendi": ("artir", "Ay sonunu artı bakiyeyle kapat; düzenli tasarruf eğilimi en güçlü olumlu sinyallerden biri."),
    "fatura_odeme_duzeni": ("artir", "Faturalarını düzenli ve zamanında öde; ödeme düzeni güvenilirlik sinyalidir."),
    "toplam_gelir_hacmi": ("artir", "Hesap üzerinden geçen düzenli gelir hacmini artırmak kapasiteyi güçlendirir."),
    "hesap_hareket_yogunlugu": ("artir", "Hesabını aktif ve düzenli kullanmak canlı hesap sinyali verir."),
    "gelir_islem_sayisi": ("artir", "Gelirini hesabın üzerinden ve daha sık akıt; kayıt dışı/nakit akış model tarafından görülemiyor."),
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
            _, metin = ONERI_HARITASI.get(f["kod"], (None, None))
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
