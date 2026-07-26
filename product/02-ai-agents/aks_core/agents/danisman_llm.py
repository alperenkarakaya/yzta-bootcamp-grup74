"""
Danışman LLM Agent — Claude API tool-calling (execution.md §3b Phase 7 / 7.5).

Mevcut `AsistanAgent`/`DanismanAgent` (`asistan.py`, `danisman_agent.py`)
deterministik, şablon tabanlıdır; opsiyonel LLM zenginleştirmesi tüm bağlamı
TEK bir prompt string'ine gömer (model her şeyi "görür" ama hiçbir şeyi
doğrulanabilir şekilde SORGULAYAMAZ). Bu modül farklı: Claude'a tanımlı
ARAÇLAR verir (`ARAC_TANIMLARI`) — model YALNIZCA bu araçlarla veri okuyabilir,
sayı UYDURAMAZ.

Bağlayıcı kural (CLAUDE.md, overview.md §6): "LLM'ler asla karar motoru
olmamalı." Bu modül bunu İKİ katmanda zorlar:
  1) `aks_skor`/`karar`/`onerilen_limit` HER ZAMAN `SkorlamaAgent`'ten gelir
     (çağıran taraf — `api/services.py` — bunları zaten `baglam`'a koyar);
     LLM çıktısı ayrı bir `yanit` alanıdır, asla karar alanının YERİNE geçmez.
  2) Yanıt-sonrası doğrulama (`_dogrula`): LLM metninde geçen sayılar araç
     çıktılarında hiç geçmiyorsa metin ATILIR, deterministik kural motoruna
     düşülür (`anlati_reddedildi=True`) — "uydurma" riski ürüne sızmaz.

`ANTHROPIC_API_KEY` yoksa (ya da API/SDK hata verirse) doğrudan deterministik
moda düşer — sıfır regresyon, demo her koşulda çalışır (`asistan.py`'nin de
uyduğu "demo her koşulda çalışır" ilkesi). TODO (execution.md): anahtar PO
tarafından eklenince canlı tool-calling'in uçtan uca doğrulanması gerekiyor.
"""
import json
import os
import re

MODEL_ADI = "claude-sonnet-5"
MAKS_TUR = 4  # tool-calling döngüsü üst sınırı — sonsuz döngü riski yok

ARAC_TANIMLARI = [
    {
        "name": "skor_getir",
        "description": "Müşterinin güncel AKS skorunu, risk seviyesini, kararını ve (biliniyorsa) klasik skorunu döner.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "faktor_getir",
        "description": "Skoru en çok etkileyen SHAP faktörlerini (riski azaltan/artıran) döner.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "politika_getir",
        "description": "Karar mekanizması politika bantlarını (skor eşiği -> risk seviyesi/karar/limit çarpanı) döner.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "senaryo_calistir",
        "description": "Belirtilen özellik değişiklikleriyle (what-if) yeniden skorlar; yalnızca bağlamda "
                        "özellik verisi mevcutsa çalışır.",
        "input_schema": {
            "type": "object",
            "properties": {"degisiklikler": {"type": "object", "description": "özellik_adi -> yeni_deger"}},
            "required": ["degisiklikler"],
        },
    },
    {
        "name": "gecmis_getir",
        "description": "Müşterinin geçmiş değerlendirmelerini (varsa) döner.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


class AracKutusu:
    """Claude'un ÇAĞIRABİLECEĞİ araçlar — tek veri kaynağı `baglam` sözlüğü
    (skor/açıklama/politika/geçmiş) + opsiyonel `simulasyon_fn`. Model bu
    araçların DIŞINDA hiçbir veriye erişemez."""

    def __init__(self, baglam, simulasyon_fn=None):
        self.baglam = baglam
        self.simulasyon_fn = simulasyon_fn  # (degisiklikler: dict) -> dict

    def skor_getir(self):
        return {
            "aks_skor": self.baglam.get("aks_skor"), "risk_seviyesi": self.baglam.get("risk_seviyesi"),
            "karar": self.baglam.get("karar"), "klasik_skor": self.baglam.get("klasik_skor"),
        }

    def faktor_getir(self):
        aciklama = self.baglam.get("aciklama") or {}
        return {
            "riski_azaltan": [x["faktor"] for x in aciklama.get("riski_azaltan", [])[:5]],
            "riski_artiran": [x["faktor"] for x in aciklama.get("riski_artiran", [])[:5]],
        }

    def politika_getir(self):
        from aks_core import politika
        return politika.olarak_sozluk()

    def senaryo_calistir(self, degisiklikler):
        if not self.simulasyon_fn:
            return {"hata": "Bu bağlamda senaryo simülasyonu kullanılamıyor (özellik verisi yok)"}
        try:
            return self.simulasyon_fn(degisiklikler or {})
        except Exception as e:
            return {"hata": str(e)}

    def gecmis_getir(self):
        return self.baglam.get("gecmis", [])


def _sayilari_cikar(metin):
    return set(re.findall(r"\d+(?:[.,]\d+)?", metin or ""))


# AKS skorunun sabit ölçek sınırları (aks_core.agents.skorlama_agent.olasilik_to_aks) —
# model "720/850" gibi doğal, kamuya açık bir ölçek ifadesi kullanırsa bu UYDURMA
# değildir; yalnızca 300-850 dışındaki/araç çıktısında olmayan sayılar şüphelidir.
_BILINEN_SABITLER = {"300", "850"}


def _dogrula(metin, arac_ciktilari):
    """Metindeki sayılar, ARAÇ ÇIKTILARINDA geçen sayılarla örtüşüyor mu?

    Basit ama etkili bir "uydurma" filtresi: model, hiçbir araç çıktısında
    görünmeyen bir sayı söylüyorsa (ör. uydurma bir limit/skor) yanıt reddedilir.
    12'nin altındaki sayılar ("üç öneri", "ilk 2 faktör" gibi doğal dil
    ifadeleri) ve AKS'nin sabit skor ölçeği (300/850) filtreden muaf — aksi
    halde yanlış pozitif patlar.
    """
    izinli = set()
    for deger in arac_ciktilari:
        izinli |= _sayilari_cikar(json.dumps(deger, ensure_ascii=False))
    for sayi in _sayilari_cikar(metin):
        if sayi in _BILINEN_SABITLER:
            continue
        try:
            if float(sayi.replace(",", ".")) <= 12:
                continue
        except ValueError:
            pass
        if sayi not in izinli:
            return False
    return True


def _kural_yanit(soru, baglam):
    # asistan.py'nin niyet-tespitli kural motorunu TEKRAR KULLANIYORUZ,
    # kopyalamıyoruz — API anahtarı yokken/başarısız olduğunda bu modülün de
    # tek kaynağı bu (drift riski yok).
    from aks_core.agents.asistan import _kural_yanit as _asistan_kural_yanit
    return _asistan_kural_yanit(soru, baglam)


def yanitla(soru, baglam, simulasyon_fn=None):
    """Döner: {"yanit": str, "mod": "llm-arac"|"kural", "anlati_reddedildi": bool,
    "arac_cagrilari": [{"arac":..., "girdi":..., "cikti":...}, ...]}."""
    baglam = baglam or {}
    if not os.environ.get("ANTHROPIC_API_KEY") or baglam.get("aks_skor") is None:
        return {"yanit": _kural_yanit(soru, baglam), "mod": "kural", "anlati_reddedildi": False, "arac_cagrilari": []}

    try:
        import anthropic
    except ImportError:
        return {"yanit": _kural_yanit(soru, baglam), "mod": "kural", "anlati_reddedildi": False, "arac_cagrilari": []}

    kutu = AracKutusu(baglam, simulasyon_fn=simulasyon_fn)
    arac_fonksiyonlari = {
        "skor_getir": lambda **_: kutu.skor_getir(),
        "faktor_getir": lambda **_: kutu.faktor_getir(),
        "politika_getir": lambda **_: kutu.politika_getir(),
        "senaryo_calistir": lambda degisiklikler=None, **_: kutu.senaryo_calistir(degisiklikler),
        "gecmis_getir": lambda **_: kutu.gecmis_getir(),
    }
    arac_ciktilari, arac_cagrilari_kayit = [], []

    try:
        istemci = anthropic.Anthropic()
        mesajlar = [{"role": "user", "content": soru}]
        sistem = (
            "Sen AKS (Alternatif Kapasite Skoru) kredi değerlendirme asistanısın. "
            "SADECE verilen araçlarla elde ettiğin verilere dayanarak yanıt ver — "
            "hiçbir sayıyı (skor, limit, oran) UYDURMA. Kısa, net, Türkçe yanıt ver."
        )
        for _ in range(MAKS_TUR):
            yanit = istemci.messages.create(
                model=MODEL_ADI, max_tokens=600, system=sistem,
                tools=ARAC_TANIMLARI, messages=mesajlar,
            )
            if yanit.stop_reason != "tool_use":
                metin = "".join(b.text for b in yanit.content if getattr(b, "type", None) == "text")
                if not _dogrula(metin, arac_ciktilari):
                    return {
                        "yanit": _kural_yanit(soru, baglam), "mod": "kural",
                        "anlati_reddedildi": True, "arac_cagrilari": arac_cagrilari_kayit,
                    }
                return {
                    "yanit": metin, "mod": "llm-arac",
                    "anlati_reddedildi": False, "arac_cagrilari": arac_cagrilari_kayit,
                }

            mesajlar.append({"role": "assistant", "content": yanit.content})
            arac_sonuclari = []
            for blok in yanit.content:
                if getattr(blok, "type", None) != "tool_use":
                    continue
                fn = arac_fonksiyonlari.get(blok.name)
                sonuc = fn(**(blok.input or {})) if fn else {"hata": "bilinmeyen araç"}
                arac_ciktilari.append(sonuc)
                arac_cagrilari_kayit.append({"arac": blok.name, "girdi": blok.input, "cikti": sonuc})
                arac_sonuclari.append({
                    "type": "tool_result", "tool_use_id": blok.id,
                    "content": json.dumps(sonuc, ensure_ascii=False),
                })
            mesajlar.append({"role": "user", "content": arac_sonuclari})

        # MAKS_TUR aşıldı (beklenmeyen döngü) — güvenli fallback, sessizce başarısız olma
        return {
            "yanit": _kural_yanit(soru, baglam), "mod": "kural",
            "anlati_reddedildi": True, "arac_cagrilari": arac_cagrilari_kayit,
        }
    except Exception:
        return {
            "yanit": _kural_yanit(soru, baglam), "mod": "kural",
            "anlati_reddedildi": False, "arac_cagrilari": arac_cagrilari_kayit,
        }
