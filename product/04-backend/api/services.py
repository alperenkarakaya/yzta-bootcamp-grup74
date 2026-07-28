"""
Servis katmanı — aks_core'u Django'ya bağlar.

- Orkestrator + AsistanAgent tekil (singleton) örnekleri
- Demo veri yüklemesi (01-data/datasets)
- portföy / adalet hesapları (eski FastAPI main.py'den taşındı)
- Her skorlamadan sonra DEĞİŞTİRİLEMEZ denetim kaydı yazımı (boundary hikâyesi)
"""
from collections import Counter

import numpy as np
from django.core.cache import cache

from aks_core import paths
from aks_core.agents.orkestrator import Orkestrator
from aks_core.agents.asistan import AsistanAgent
from aks_core.agents.skorlama_agent import olasilik_to_aks
from aks_core.ozellik.cikarim import OZELLIK_ADLARI, csv_oku, tum_musteriler
from aks_core.model.etiketleme import etiketle
from aks_core.model.egitim import klasik_risk_skoru
from aks_core.model.adalet import adalet_raporu

# --- Tekil çekirdek nesneleri (model bir kez yüklensin) ---
orkestrator = Orkestrator()
asistan = AsistanAgent()

VERI_YOLU = paths.data("sentetik_islemler.csv")
try:
    _musteri_islemleri, _persona = csv_oku(VERI_YOLU)
except FileNotFoundError:
    _musteri_islemleri, _persona = {}, {}


def demo_islemler(mid):
    if mid not in _musteri_islemleri:
        return None
    return [dict(i) for i in _musteri_islemleri[mid]]


def demo_var():
    return bool(_musteri_islemleri)


def demo_personalar(adet_per_persona=3):
    ornekler = {}
    for mid, p in _persona.items():
        ornekler.setdefault(p, [])
        if len(ornekler[p]) < adet_per_persona:
            ornekler[p].append(mid)
    return ornekler


def bilgi():
    return {
        "servis": "AKS - Alternatif Kapasite Skoru",
        "surum": "3.0-django",
        "model": orkestrator.skorlama_agent.model_adi,
        "ozellikler": OZELLIK_ADLARI,
        "demo_musteri_sayisi": len(_musteri_islemleri),
    }


def metrikler_var():
    import os
    return os.path.exists(os.path.join(str(paths.ARTIFACTS_DIR), "degerlendirme_raporu.json"))


def metrikler():
    """§3b/U15: degerlendirme.py'nin (U6) persist ettiği tam CV+CI+kalibrasyon+alt-grup
    raporu — `metrikler.json`'ın (egitim.py'nin hızlı tek-split sağlık kontrolü) aksine,
    bu "resmi" (raporlanabilir) metrik kaynağıdır."""
    import json, os
    yol = os.path.join(str(paths.ARTIFACTS_DIR), "degerlendirme_raporu.json")
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def segmentasyon_var():
    """§3b/U26: segmentasyon.py'nin (denetimsiz K-Means keşif) persist ettiği rapor."""
    import os
    return os.path.exists(os.path.join(str(paths.ARTIFACTS_DIR), "segmentasyon_raporu.json"))


def segmentasyon():
    import json, os
    yol = os.path.join(str(paths.ARTIFACTS_DIR), "segmentasyon_raporu.json")
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def risk_istahi_var():
    """§3b Phase 7/7.4: risk_istahi.py'nin persist ettiği 3-profil raporu."""
    import os
    return os.path.exists(os.path.join(str(paths.ARTIFACTS_DIR), "risk_istahi_raporu.json"))


def risk_istahi():
    from aks_core.model import risk_istahi as risk_istahi_modul
    return risk_istahi_modul.raporu_yukle()


def musteri_risk_istahi(aks_skor):
    """Verilen bir AKS skorunun 3 risk-iştahı profilinden hangilerinde
    onaylanacağını döner — ağır hesaplama TEKRARLANMAZ, yalnızca persiste
    edilmiş eşiklerle karşılaştırılır (bkz. risk_istahi.musteri_risk_istahi)."""
    from aks_core.model import risk_istahi as risk_istahi_modul
    return risk_istahi_modul.musteri_risk_istahi(aks_skor)


def aciklama_yeniden_uret(ozellikler):
    """Persiste edilmiş özellik sözlüğünden SHAP açıklamasını yeniden üretir.

    `Assessment` SHAP çıktısını saklamaz (özellikler saklanır) — kurumun
    müşteri detayında gerekçe kodlarını göstermek için burada yeniden
    hesaplanır. Model ve açıklayıcı zaten `orkestrator` içinde tekil.
    Özellik seti eskiyse (eski bir kayıt) None döner, patlamaz.
    """
    try:
        vektor = [float(ozellikler[o]) for o in OZELLIK_ADLARI]
    except (KeyError, TypeError, ValueError):
        return None
    return orkestrator.aciklayici.acikla(vektor)


def genelleme_saglamlik_var():
    """§4 R8/R10/R11: genelleme_saglamlik.py'nin persist ettiği rapor."""
    import os
    return os.path.exists(os.path.join(str(paths.ARTIFACTS_DIR), "genelleme_saglamlik_raporu.json"))


def genelleme_saglamlik():
    import json, os
    yol = os.path.join(str(paths.ARTIFACTS_DIR), "genelleme_saglamlik_raporu.json")
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


# Portfoy/adalet toplu-istatistik eşiklerinin varsayılanları — tek yerde (views.py'nin
# query-param varsayılanları burayı referans alır; frontend de /api/politika ile aynı
# yerden okur, kendi kopyasını icat etmez — U21).
PORTFOY_ESIK_VARSAYILAN = {"klasik_esik": 680, "aks_esik": 650}


def politika():
    """§3b/U16: karar mekanizması politikası — tek, versiyonlanmış kaynak.

    İki AYRI eşik sistemini birlikte taşır (frontend'in tek çağrıda görmesi için):
    - `bantlar`: AKS skoru -> risk seviyesi/karar/limit çarpanı (aks_core.politika,
      720/620/540) — tekil müşteri kararı.
    - `portfoy_esikleri`: /api/portfoy ve /api/adalet'in TOPLU istatistik varsayılanları
      (680/650) — bunlar politika bantlarıyla AYNI değerler değildir, karıştırılmamalı.
    """
    from aks_core import politika as politika_modulu
    sozluk = politika_modulu.olarak_sozluk()
    sozluk["portfoy_esikleri"] = PORTFOY_ESIK_VARSAYILAN
    return sozluk


#: Yüklenebilecek en büyük belge (bayt). Hem anonim `/api/csv-skorla` hem de
#: `/api/portal/yukle` bu sınırdan geçer — tek yerde tanımlı.
MAKS_BELGE_BAYT = 10 * 1024 * 1024


def belge_ayristir(dosya):
    """Multipart dosyadan (CSV/XLSX/PDF) işlem listesi + kalite/meta raporu çıkarır.

    §3b Phase 7 / 7.1 + 7.5: eski `csv_ayristir()`'in (yalnızca CSV, katı kolon
    şeması) yerini alır — `aks_core.agents.belge_agent.BelgeAgent`'a devreder
    (mantık burada kopyalanmaz). `BelgeAgent`, `aks_core.belge.okuyucu.ayristir()`
    ile AYNI alt modülleri kullanır ama çok-stratejili karar sürecinin izini
    (`meta["iz"]`) de taşır — gerçek agent davranışının kanıtı. Format hatasında
    `aks_core.belge.BelgeHatasi` fırlatır (mesajı doğrudan kullanıcıya gösterilebilir,
    `hata.iz` o ana kadarki izi taşır). Hem anonim `/api/csv-skorla` hem giriş
    yapmış `/api/portal/yukle` tarafından paylaşılan tek ayrıştırma mantığı.

    Döner: (islemler, meta) — meta; kaynak_format/kategori_guveni/pencere_uyumlu/
    bayraklar/iz gibi şeffaflık alanları taşır (kalite.py + belge_agent.py).
    """
    from aks_core.agents.belge_agent import BelgeAgent
    from aks_core.belge.hatalar import BelgeHatasi

    # Boyut sınırı: `dosya.read()` dosyanın TAMAMINI belleğe alıyor ve Django'nun
    # `DATA_UPLOAD_MAX_MEMORY_SIZE`'ı multipart DOSYA alanlarına uygulanmıyor —
    # yani sınır koymazsak yüzlerce MB'lık bir yükleme (ardından pdfplumber'ın
    # ayrıştırması) süreci belleksiz bırakabilirdi. 10 MB, bir hesap ekstresi
    # için fazlasıyla yeterli (en büyük test fixture'ı birkaç yüz KB).
    boyut = getattr(dosya, "size", None)
    if boyut is not None and boyut > MAKS_BELGE_BAYT:
        raise BelgeHatasi(
            f"Dosya çok büyük ({boyut / 1_048_576:.1f} MB). "
            f"En fazla {MAKS_BELGE_BAYT // 1_048_576} MB yükleyebilirsiniz."
        )
    return BelgeAgent().calistir(dosya.name, dosya.read())


def csv_ayristir(dosya):
    """Geriye dönük uyumluluk sarmalayıcısı — yalnızca işlem listesini döner
    (meta'yı görmezden gelir). Yeni çağıranlar `belge_ayristir()` kullanmalı."""
    islemler, _meta = belge_ayristir(dosya)
    return islemler


def degerlendir(musteri_id, islemler, kaynak="api", persona="", user=None, belge_meta=None,
                 sahiplik_beyani=False, ip=None):
    """aks_core ile skorla + denetim izi yaz.

    §3b/U17: persona biliniyorsa (klasik skor hesaplanabiliyorsa) Formülasyon B
    alanları da (pd_geleneksel_bant/pd_fark/kapasite_sinyali) hesaplanır.
    `SkorlamaAgent.calistir()` ikinci kez çağrılır (orkestrator zaten bir kez
    çağırdı) — ucuz, deterministik bir tahmin (LR/XGB predict_proba), pahalı
    olan SHAP tekrar hesaplanmıyor. Bu, aks_core'a (Phase 1, kapalı) dokunmadan
    04-backend katmanında Formülasyon B'yi açığa çıkarmanın yolu — orkestratör
    klasik skoru bilmiyor (sınır: bankanın skoru yalnızca 04-backend'de hesaplanır).

    §3b/Phase 6: `user` verilirse (portal akışı) `Assessment.user`'a bağlanır —
    yalnızca o kullanıcının "Geçmişim" listesini besler, bankanın gördüğü hiçbir
    veriyi etkilemez.

    §3b/Phase 7/7.1: `belge_meta` verilirse (belge hattından gelen kalite/kaynak
    raporu, bkz. `belge_ayristir()`) `Assessment.kaynak_format`/`belge_parmak_izi`
    alanlarını besler; `user`'ın bir `Profil`'i varsa `Assessment.profil`'e
    bağlanır — kurum tarafının (`kimlik.kurum_views`) bu kaydı bulabilmesi için.

    §3b/Phase 7/7.3: `user`'ın profili varsa iki sahiplik-savunma kontrolü
    (`api.sahiplik`) çalışır — çakışan parmak izi / davranışsal tutarsızlık.
    Bulunan bayraklar KARARI DEĞİŞTİRMEZ, yalnızca `sonuc["sahiplik_bayraklari"]`
    ve denetim kaydına yazılır (anomali_bayrak ile aynı "şeffaflık sinyali,
    karar mekanizması değil" deseni — overview.md §7 sınırı).
    """
    sonuc = orkestrator.degerlendir(musteri_id, islemler)
    klasik = None
    if persona:
        veri = orkestrator.veri_agent.calistir(islemler)
        klasik = klasik_risk_skoru({"persona": persona, **veri["ozellikler"]})
        vektor = [veri["ozellikler"][o] for o in orkestrator.skorlama_agent.ozellikler]
        formulasyon_b = orkestrator.skorlama_agent.calistir(vektor, veri["ozellikler"], klasik_skor=klasik)
        sonuc["pd_geleneksel_bant"] = formulasyon_b.get("pd_geleneksel_bant")
        sonuc["pd_fark"] = formulasyon_b.get("pd_fark")
        sonuc["kapasite_sinyali"] = formulasyon_b.get("kapasite_sinyali")

    sahiplik_bayraklari = []
    gecerli_user = user if (user is not None and user.is_authenticated) else None
    profil = getattr(gecerli_user, "profil", None) if gecerli_user else None
    if profil is not None:
        from api import sahiplik as sahiplik_modul
        parmak_izi = (belge_meta or {}).get("parmak_izi", "")
        if parmak_izi and sahiplik_modul.coklu_sahiplik_kontrol(parmak_izi, profil):
            sahiplik_bayraklari.append("coklu_sahiplik_supheli")
        if sahiplik_modul.davranissal_tutarlilik_kontrol(profil, sonuc.get("ozellikler", {})):
            sahiplik_bayraklari.append("profil_tutarsiz")
    sonuc["sahiplik_bayraklari"] = sahiplik_bayraklari

    _denetim_yaz(musteri_id, klasik, sonuc, kaynak, user=user, belge_meta=belge_meta,
                 sahiplik_beyani=sahiplik_beyani, sahiplik_bayraklari=sahiplik_bayraklari, ip=ip,
                 islemler=islemler)
    return sonuc, klasik


def _denetim_yaz(musteri_id, klasik, sonuc, kaynak, user=None, belge_meta=None,
                  sahiplik_beyani=False, sahiplik_bayraklari=None, ip=None, islemler=None):
    """Best-effort: denetim yazımı skorlamayı asla düşürmemeli."""
    try:
        from audit.models import AuditLog, Assessment, Customer
        cust = None
        if kaynak == "demo":
            cust, _ = Customer.objects.get_or_create(
                external_id=str(musteri_id),
                defaults={"persona": _persona.get(musteri_id, "")},
            )
        pd_fark = sonuc.get("pd_fark")
        kapasite_sinyali = sonuc.get("kapasite_sinyali")
        gecerli_user = user if (user is not None and user.is_authenticated) else None
        profil = getattr(gecerli_user, "profil", None) if gecerli_user else None
        belge_meta = belge_meta or {}
        # PO kararı: müşteri tarafından yüklenen ham işlemler müşteri bazlı
        # saklanmalı. Yalnızca kimliği doğrulanmış bir profile bağlıyken
        # yazılır (bankanın demo/anonim skorlamalarında değil — bkz.
        # Assessment.ham_islemler docstring'i). Yalnızca kanonik şema alanları
        # (`normalizer.py::normalize()`'ın ürettiği dört alan + tarih) —
        # olası içsel/geçici anahtarlar (ör. `tarih_obj`) asla saklanmaz;
        # hem JSON-serileştirilebilirlik hem "gerekli olandan fazlasını
        # tutma" ilkesi için (bkz. §9c minimum-PII duruşu).
        ham_islemler = [
            {k: i.get(k) for k in ("tarih", "islem_tipi", "kategori", "tutar", "aciklama")}
            for i in islemler
        ] if (profil is not None and islemler) else []
        Assessment.objects.create(
            customer=cust, musteri_id=str(musteri_id), klasik_skor=klasik,
            aks_skor=sonuc["aks_skor"], risk_seviyesi=sonuc["risk_seviyesi"],
            karar=sonuc["karar"], onerilen_limit=sonuc.get("onerilen_limit"),
            ozellikler=sonuc.get("ozellikler", {}), kaynak=kaynak,
            pd_fark=pd_fark, kapasite_sinyali=kapasite_sinyali,
            user=gecerli_user, profil=profil,
            belge_parmak_izi=belge_meta.get("parmak_izi", ""),
            kaynak_format=belge_meta.get("kaynak_format", ""),
            sahiplik_beyani=sahiplik_beyani, sahiplik_bayraklari=sahiplik_bayraklari or [], yukleme_ip=ip,
            ham_islemler=ham_islemler,
        )
        AuditLog.objects.create(
            musteri_id=str(musteri_id), klasik_skor=klasik, aks_skor=sonuc["aks_skor"],
            karar=sonuc["karar"], onerilen_limit=sonuc.get("onerilen_limit"),
            ajanlar=sonuc.get("kullanilan_agentlar", []), kaynak=kaynak,
            pd_fark=pd_fark, kapasite_sinyali=kapasite_sinyali,
        )
    except Exception:  # tablo yoksa / DB yoksa demo yine çalışsın
        pass


#: Gerçek bir müşteriye ait OLMAYAN skorlamaların (portal yüklemesi, anonim
#: belge yüklemesi) `musteri_id`'si. Portal'da gerçek kimlik `Assessment.user`/
#: `.profil` FK'sindedir; bu değer yalnızca "kimliksiz" demektir — dolayısıyla
#: TÜM portal kullanıcıları bu tek anahtarı paylaşır.
KIMLIKSIZ_MUSTERI_ID = "-1"


def gecmis(musteri_id):
    """DB'den (kalıcı) DEMO/araştırma geçmişi; yoksa orkestratör hafızasına düş.

    Buradaki iki filtre GÜVENLİK kısıtıdır, kozmetik değil. Portal yüklemeleri
    `musteri_id="-1"` ile yazılıyor (gerçek kimlik `user`/`profil` FK'sinde),
    yani birbirinden habersiz tüm portal kullanıcıları bu tek anahtarı
    paylaşıyor. Filtre olmadan tek bir çağrı hepsinin skor geçmişini tek
    listede döndürüyordu — üstelik İKİ ayrı yoldan:

    1. **DB yolu** — `exclude(kaynak="portal")` ile kapatıldı.
    2. **Orkestratör hafızası (fallback)** — `Orkestrator.hafiza`, süreç-içi bir
       `{musteri_id: [...]}` sözlüğü ve portal/CSV skorlamaları da oraya aynı
       `-1` anahtarıyla yazılıyor. Yalnızca DB filtresi eklenince sorgu boş
       dönüp **fallback devreye giriyor** ve sızıntı ikinci yoldan devam
       ediyordu (bunu `YuzeyIzolasyonuTesti` yakaladı). Bu yüzden kimliksiz
       skorlamalar için fonksiyon en baştan boş döner.

    Müşterinin kendi geçmişi yalnızca `/api/portal/gecmis` (user filtresi),
    kurumun gördüğü kayıt yalnızca `kimlik/kurum_views.musteri_detay` (aktif
    rıza) üzerinden erişilir — bu uç sadece banka içi DEMO popülasyonu içindir.
    """
    if str(musteri_id) == KIMLIKSIZ_MUSTERI_ID:
        return []
    try:
        from audit.models import Assessment
        qs = (
            Assessment.objects.filter(musteri_id=str(musteri_id))
            .exclude(kaynak="portal")
            .order_by("created_at")
        )
        if qs.exists():
            return [{"zaman": a.created_at.isoformat(timespec="seconds"),
                     "aks_skor": a.aks_skor, "risk_seviyesi": a.risk_seviyesi} for a in qs]
    except Exception:
        pass
    return [{"zaman": k["zaman"], "aks_skor": k["aks_skor"], "risk_seviyesi": k["risk_seviyesi"]}
            for k in orkestrator.gecmis(musteri_id)]


def _skorla_hepsi():
    """DİKKAT (§3b/U17 bulgusu, D5): bu, canlı demo popülasyonunu (`sentetik_islemler.csv`)
    HALA eski, döngüsel `etiketle()` ile etiketliyor — Phase 1'in düzeltmesi (decoupled
    veri) şu an yalnızca offline eğitim/değerlendirme betiklerine (egitim.py,
    degerlendirme.py, circularity_ablation.py, is_etkisi.py) taşındı. `portfoy()`/
    `adalet()`'in ürettiği toplu istatistikler bu yüzden hâlâ döngüsel veri üzerinden;
    tekil skorlama (skorla/skorla_demo) gerçek (LR/dekuple-eğitilmiş) modeli kullanıyor
    ama bu fonksiyondaki "gerçek temerrüt" etiketi döngüsel kalıyor. Canlı demo veri
    kaynağının da değiştirilip değiştirilmeyeceği OQ-44 olarak açık bırakıldı (bu,
    hangi demo müşterilerin/personaların gösterileceğini değiştiren ürün kararı)."""
    musteriler = etiketle(tum_musteriler(VERI_YOLU), hedef_temerrut_orani=0.18)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    p = orkestrator.skorlama_agent.model.predict_proba(X)[:, 1]
    for m, pi in zip(musteriler, p):
        m["klasik_skor"] = klasik_risk_skoru(m)
        m["aks_skor"] = olasilik_to_aks(float(pi))
    return musteriler


# İçerik korunmalı (statistical-validity mandate — bu sayılar gerçekten döngüsel
# etiketli demo verisinden geliyor ve doğrulanmamış), yalnızca dahili dosya/OQ
# atıfları kullanıcıya sızmasın diye kaldırıldı (execution.md §3b Phase 7/7.8).
_METRIK_UYARISI = ("Bu toplu istatistikler döngüsel etiketli demo verisi üzerinden hesaplanıyor; "
                    "tekil skorlama gerçek (dekuple/LR) modeli kullanır ama bu toplu görünüm henüz "
                    "aynı kaynağa taşınmadı. Doğrulanmış olarak alıntılamayın.")


def portfoy(klasik_esik=680, aks_esik=650, ort_kredi=25000, getiri_orani=0.12, zarar_orani=0.55):
    key = f"portfoy:{klasik_esik}:{aks_esik}:{ort_kredi}:{getiri_orani}:{zarar_orani}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    musteriler = _skorla_hepsi()
    red = [m for m in musteriler if m["klasik_skor"] < klasik_esik]
    kredibl = [m for m in red if m["temerrut"] == 0]
    kurtarilan = [m for m in kredibl if m["aks_skor"] >= aks_esik]
    temerrutler = [m for m in red if m["temerrut"] == 1]
    yanlis_onay = [m for m in temerrutler if m["aks_skor"] >= aks_esik]
    kirilim = Counter(m["persona"] for m in kurtarilan)
    kazanc = len(kurtarilan) * ort_kredi * getiri_orani
    kayip = len(yanlis_onay) * ort_kredi * zarar_orani
    sonuc = {
        "toplam_musteri": len(musteriler), "klasik_red": len(red), "kredibl_red": len(kredibl),
        "kurtarilan": len(kurtarilan), "kurtarma_orani": round(len(kurtarilan) / max(1, len(kredibl)), 3),
        "yanlis_onay": len(yanlis_onay), "yanlis_onay_orani": round(len(yanlis_onay) / max(1, len(temerrutler)), 3),
        "persona_kirilimi": dict(kirilim),
        "illustratif_getiri": {
            "varsayimlar": {"ort_kredi": ort_kredi, "getiri_orani": getiri_orani, "zarar_orani": zarar_orani},
            "potansiyel_kazanc": round(kazanc), "beklenen_kayip": round(kayip), "net": round(kazanc - kayip),
        },
        "veri_kaynagi": "dongusel",
        "uyari": _METRIK_UYARISI,
    }
    cache.set(key, sonuc, timeout=600)
    return sonuc


def adalet(klasik_esik=680, aks_esik=650):
    key = f"adalet:{klasik_esik}:{aks_esik}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    musteriler = _skorla_hepsi()
    sonuc = adalet_raporu(musteriler, {"klasik_skor": klasik_esik, "aks_skor": aks_esik})
    sonuc["veri_kaynagi"] = "dongusel"
    sonuc["uyari"] = _METRIK_UYARISI
    cache.set(key, sonuc, timeout=600)
    return sonuc


def _simulasyon_fn_olustur(baglam):
    """§3b Phase 7/7.5: `baglam["ozellikler"]` verilmişse (frontend gönderirse),
    `danisman_llm`'in `senaryo_calistir` aracının çağırabileceği bir kapanış
    döner — what-if hesaplaması mevcut `SkorlamaAgent`'i kullanır, yeni bir
    skorlama mantığı İCAT EDİLMEZ (aynı `/api/simulasyon`'un kullandığı yol)."""
    ozellikler = baglam.get("ozellikler")
    if not ozellikler:
        return None

    def _calistir(degisiklikler):
        gecersiz = [k for k in degisiklikler if k not in ozellikler]
        if gecersiz:
            return {"hata": f"Geçersiz özellik(ler): {gecersiz}"}
        yeni_ozellikler = dict(ozellikler)
        yeni_ozellikler.update(degisiklikler)
        vektor = [yeni_ozellikler[o] for o in orkestrator.skorlama_agent.ozellikler]
        sonuc = orkestrator.skorlama_agent.calistir(vektor)
        return {"senaryo_aks_skor": sonuc["aks_skor"], "senaryo_karar": sonuc["karar"]}

    return _calistir


def asistan_yanit(soru, baglam):
    """§3b Phase 7/7.5, §7.10: `ANTHROPIC_API_KEY` VEYA `GEMINI_API_KEY`
    tanımlıysa tool-calling agent'ı (`danisman_llm`) tercih edilir — ikisi de
    aynı 5 aracı ve aynı uydurma-sayı guard'ını (`_dogrula`) kullanır, yalnızca
    SDK/şema farklıdır (bkz. danisman_llm.py docstring'i). Hiçbiri yoksa eski
    yola (kendi GEMINI_API_KEY kontrolü olan, tool'suz `AsistanAgent`) düşülür
    — bu dal artık yalnızca anahtarsız/SDK'sız ortamlarda erişilir, aynı
    zamanda `danisman_llm` tamamen başarısız olursa (import hatası vb.)
    davranışın sıfır regresyonla eskisi gibi çalışmasını garanti eder."""
    import os
    baglam = baglam or {}
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        from aks_core.agents import danisman_llm
        return danisman_llm.yanitla(soru, baglam, simulasyon_fn=_simulasyon_fn_olustur(baglam))
    return asistan.yanitla(soru, baglam)
