"""
AKS Asistanı
------------
Kullanıcının/banka görevlisinin doğal dil sorularını yanıtlar
("skorumu nasıl yükseltirim?", "neden düşük?", "ne kadar limit?").

İki modlu tasarım:
  - LLM modu: GEMINI_API_KEY tanımlıysa Google Gemini ile doğal dil yanıtı.
  - Kural modu: anahtar yoksa ya da LLM hata verirse, mevcut skor/SHAP/öneri
    bağlamından niyet tespitiyle deterministik yanıt üretir.

Demo her koşulda çalışır; anahtar eklenince tam güç devreye girer.
"""
import os

ANAHTAR_KELIMELER = {
    "yukselt": ["yükselt", "artır", "arttır", "iyileştir", "yukarı", "çıkar", "geliştir"],
    "limit":   ["limit", "ne kadar", "kaç para", "kredi ver", "tutar"],
    "neden":   ["neden", "niçin", "niye", "sebep", "düşük", "neye göre"],
    "risk":    ["risk", "temerrüt", "batar", "geri öde", "tehlike"],
    "adalet":  ["adalet", "adil", "ayrım", "haksız", "eşit", "önyargı"],
    "nasil":   ["nasıl çalış", "ne yapıyor", "hangi model", "nasıl hesap"],
}


def _niyet(soru):
    s = soru.lower()
    for niyet, kelimeler in ANAHTAR_KELIMELER.items():
        if any(k in s for k in kelimeler):
            return niyet
    return "genel"


def _kural_yanit(soru, baglam):
    niyet = _niyet(soru)
    aks = baglam.get("aks_skor")
    klasik = baglam.get("klasik_skor")
    seviye = baglam.get("risk_seviyesi", "—")
    limit = baglam.get("onerilen_limit")
    aciklama = baglam.get("aciklama", {})
    danisman = baglam.get("danisman", {})

    if aks is None:
        return ("Önce bir müşteri profili skorlayın ya da bir hesap dökümü yükleyin; "
                "ardından skora dair her şeyi yanıtlayabilirim.")

    if niyet == "yukselt":
        oneriler = danisman.get("oneriler", [])
        if oneriler:
            return "Skoru yükseltmek için en etkili adımlar:\n" + "\n".join(f"• {o}" for o in oneriler)
        return "Skor zaten güçlü; düzenli tasarruf ve zamanında ödeme alışkanlığını sürdürmek yeterli."

    if niyet == "limit":
        if limit:
            return (f"Bu profil için önerilen kredi limiti {limit:,.0f} TL. "
                    f"Limit, aylık net nakit akışına ve {aks}/850 skorun risk seviyesine ({seviye}) göre hesaplanır.")
        return "Bu skor seviyesinde kredi limiti önerilmiyor; önce riski azaltacak adımlar gerekiyor."

    if niyet == "neden":
        art = aciklama.get("riski_azaltan", [])[:3]
        azalt = aciklama.get("riski_artiran", [])[:2]
        cevap = f"Skor {aks}/850 ({seviye}). "
        if art:
            cevap += "Skoru yükselten faktörler: " + ", ".join(x["faktor"] for x in art) + ". "
        if azalt:
            cevap += "Aşağı çeken faktörler: " + ", ".join(x["faktor"] for x in azalt) + "."
        return cevap

    if niyet == "risk":
        if klasik and aks:
            return (f"Risk seviyesi: {seviye}. Klasik skor {klasik} verirken davranışsal model {aks} görüyor. "
                    "Model, temerrüt olasılığını hesap hareketlerindeki disiplinden tahmin eder.")
        return f"Risk seviyesi: {seviye} (AKS {aks}/850)."

    if niyet == "adalet":
        return ("AKS, kararı kişinin resmi statüsüne (öğrenci/stajyer) göre değil, gerçek davranışına göre verir. "
                "Böylece klasik skorun haksızca elediği disiplinli kişiler adil bir şans bulur — "
                "banka görünümündeki adalet tablosu bunu gruplar arası onaylanma oranıyla gösterir.")

    if niyet == "nasil":
        return ("AKS, hesap hareketlerinden 9 davranışsal özellik çıkarır, bunları XGBoost modeline verir ve "
                "300–850 arası bir skor üretir. SHAP ile her faktörün etkisi açıklanır; üç agent (veri, skorlama, "
                "danışman) bu süreci yürütür.")

    # genel
    ozet = danisman.get("ozet", f"Skor {aks}/850 ({seviye}).")
    return ozet + " Skoru yükseltme, limit, faktörler ya da risk hakkında soru sorabilirsiniz."


def gemini_fonksiyonu():
    """GEMINI_API_KEY tanımlıysa Gemini çağrısı yapan fonksiyon döner, yoksa None."""
    anahtar = os.environ.get("GEMINI_API_KEY")
    if not anahtar:
        return None

    def _cagir(istem):
        import httpx
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               "gemini-1.5-flash:generateContent?key=" + anahtar)
        govde = {"contents": [{"parts": [{"text": istem}]}]}
        r = httpx.post(url, json=govde, timeout=20)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    return _cagir


class AsistanAgent:
    ad = "asistan_agent"

    def __init__(self, llm_fonksiyonu=None):
        self.llm = llm_fonksiyonu or gemini_fonksiyonu()

    def yanitla(self, soru, baglam):
        if self.llm and baglam.get("aks_skor") is not None:
            istem = (
                "Sen bir kredi değerlendirme asistanısın (AKS - Alternatif Kapasite Skoru). "
                "Kısa, net ve Türkçe yanıt ver. Bağlam:\n"
                f"- AKS skoru: {baglam.get('aks_skor')}/850 ({baglam.get('risk_seviyesi')})\n"
                f"- Klasik skor: {baglam.get('klasik_skor')}\n"
                f"- Önerilen limit: {baglam.get('onerilen_limit')} TL\n"
                f"- Skoru yükselten faktörler: {[x['faktor'] for x in baglam.get('aciklama',{}).get('riski_azaltan',[])[:3]]}\n"
                f"- İyileştirme önerileri: {baglam.get('danisman',{}).get('oneriler',[])}\n"
                f"Kullanıcı sorusu: {soru}"
            )
            try:
                return {"yanit": self.llm(istem), "mod": "llm"}
            except Exception:
                pass
        return {"yanit": _kural_yanit(soru, baglam), "mod": "kural"}
