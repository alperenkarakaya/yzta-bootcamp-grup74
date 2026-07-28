"""
Müşteri-taraflı kimlik/rıza uçları — kullanıcı portalinin (`/portal/*`)
oturum-korumalı API'si. Kurum-taraflı uçlar `kurum_views.py`'de (execution.md
§3b Phase 7 / 7.2).

Telefon doğrulama, e-posta+şifre kaydından (`api/auth_views.py::kayit`)
AYRI bir adım — kayıt anında `Profil` otomatik oluşturulur (rastgele
`aks_no` ile) ama `telefon_dogrulandi_mi=False` kalır; kullanıcı istediği
an bu iki uçla telefonunu doğrulayabilir (zorunlu tutulmuyor, PO onayı
gerekirse ileride `IsAuthenticated` + `telefon_dogrulandi_mi` şartına
sıkılaştırılabilir — yeni OQ olarak execution.md'de).
"""
from django.db import IntegrityError
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response

from . import telefon as telefon_modul
from .models import ErisimTalebi, Profil, RizaKaydi, TelefonDogrulama
from .izinler import ProfilSahibi
from .throttle import OtpThrottle


def _ip(request):
    return request.META.get("REMOTE_ADDR")


def _riza_yaz(erisim_talebi, olay, request=None):
    """`RizaKaydi`'ne bir olay ekler — append-only defter (bkz. models.py).
    Best-effort DEĞİL: rıza olayı yazılamıyorsa çağıran taraf hatayı görmeli
    (AuditLog'un aksine burada sessiz yutma yok — rıza kaydı ürünün KVKK
    savunmasının kendisi)."""
    RizaKaydi.objects.create(
        erisim_talebi=erisim_talebi, olay=olay,
        aks_no=erisim_talebi.profil.aks_no, kurum_kod=erisim_talebi.kurum.kod,
        ip=_ip(request) if request else None,
    )


@api_view(["GET"])
@permission_classes([ProfilSahibi])
def profilim(request):
    profil = request.user.profil
    return Response({
        "aks_no": profil.aks_no,
        "telefon_dogrulandi_mi": profil.telefon_dogrulandi_mi,
    })


@api_view(["POST"])
@permission_classes([ProfilSahibi])
@throttle_classes([OtpThrottle])
def telefon_gonder(request):
    telefon = (request.data.get("telefon") or "").strip()
    if not telefon or len(telefon) < 8:
        return Response({"hata": "Geçerli bir telefon numarası girin (E.164, ör. +905551112233)"}, status=400)

    telefon_hash = telefon_modul.hashle(telefon)
    # Bu numara BAŞKA bir hesaba zaten bağlıysa reddet (Sybil direnci — PO kararı).
    if Profil.objects.filter(telefon_hash=telefon_hash).exclude(user=request.user).exists():
        return Response({"hata": "Bu telefon numarası başka bir hesaba kayıtlı"}, status=409)

    # Yeni kod istenince ESKİ bekleyen kodlar geçersizleşir. Aksi halde aynı
    # anda birden fazla geçerli OTP olurdu (sızan eski bir kod, yenisi
    # istendikten sonra da süresi dolana kadar çalışırdı) ve MAKS_DENEME
    # sınırı yeni kod isteyerek sıfırlanabilirdi.
    TelefonDogrulama.objects.filter(user=request.user, kullanildi_mi=False).update(kullanildi_mi=True)

    kod = telefon_modul.otp_uret()
    dogrulama = TelefonDogrulama.objects.create(
        user=request.user, telefon_hash=telefon_hash,
        kod_hash=telefon_modul.hashle(kod), son_gecerlilik=telefon_modul.otp_son_gecerlilik(),
    )
    yanit = {
        "gonderildi": True, "gecerlilik_dakika": telefon_modul.OTP_GECERLILIK_DK,
        "dogrulama_id": dogrulama.id,
    }
    from django.conf import settings
    # SMS sağlayıcısı henüz yok (açık OQ, execution.md) — demo/test ortamında
    # kod doğrudan yanıtta görünür, aksi halde telefon doğrulama akışı hiç
    # denenemez. GERÇEK DAĞITIMDA İKİSİ DE KAPALI OLMALI.
    #
    # `AKS_OTP_DEMO_KOD` ayrı bir bayrak: `.env`'de `DJANGO_DEBUG=false`
    # (üretim benzeri davranış isteniyor — traceback sızmasın) ama demo
    # hesaplarıyla akışın denenebilmesi gerekiyor. İkisini tek bayrağa bağlamak,
    # "kodu görebilmek için DEBUG'ı aç" gibi çok daha kötü bir ödünleşim
    # dayatıyordu.
    if settings.DEBUG or settings.OTP_DEMO_KOD:
        yanit["demo_kod"] = kod
        yanit["debug_kod"] = kod  # geriye dönük ad (frontend/testler)
    return Response(yanit)


@api_view(["POST"])
@permission_classes([ProfilSahibi])
@throttle_classes([OtpThrottle])
def telefon_dogrula(request):
    dogrulama_id = request.data.get("dogrulama_id")
    kod = (request.data.get("kod") or "").strip()
    try:
        dogrulama = TelefonDogrulama.objects.get(id=dogrulama_id, user=request.user)
    except (TelefonDogrulama.DoesNotExist, ValueError, TypeError):
        return Response({"hata": "Doğrulama isteği bulunamadı"}, status=404)

    if not dogrulama.gecerli_mi():
        return Response({"hata": "Kod süresi dolmuş ya da deneme hakkı bitti — yeniden kod isteyin"}, status=400)

    if telefon_modul.hashle(kod) != dogrulama.kod_hash:
        dogrulama.deneme_sayisi += 1
        dogrulama.save(update_fields=["deneme_sayisi"])
        kalan = dogrulama.MAKS_DENEME - dogrulama.deneme_sayisi
        return Response({"hata": f"Kod hatalı ({max(kalan, 0)} deneme hakkı kaldı)"}, status=400)

    # Sybil kontrolü BURADA tekrarlanır. `telefon_gonder`'deki kontrol tek
    # başına yetmiyordu: iki hesap da aynı numara için kod isterse ikisi de o
    # kontrolden geçer (henüz ikisinin de `telefon_hash`'i boş), sonra ikisi de
    # doğrulayınca ikinci `save()` `telefon_hash` unique kısıtına takılıp 500
    # veriyordu. Kontrol yazma anına taşındı; kısıt ihlali yine olursa (gerçek
    # yarış) 500 yerine anlamlı 409 döner.
    profil = request.user.profil
    if Profil.objects.filter(telefon_hash=dogrulama.telefon_hash).exclude(pk=profil.pk).exists():
        return Response({"hata": "Bu telefon numarası başka bir hesaba kayıtlı"}, status=409)

    dogrulama.kullanildi_mi = True
    dogrulama.save(update_fields=["kullanildi_mi"])

    profil.telefon_hash = dogrulama.telefon_hash
    profil.telefon_dogrulandi_mi = True
    profil.telefon_dogrulandi_at = timezone.now()
    try:
        profil.save(update_fields=["telefon_hash", "telefon_dogrulandi_mi", "telefon_dogrulandi_at"])
    except IntegrityError:
        return Response({"hata": "Bu telefon numarası başka bir hesaba kayıtlı"}, status=409)
    return Response({"dogrulandi": True})


@api_view(["GET"])
@permission_classes([ProfilSahibi])
def erisim_talepleri(request):
    """Bu müşteriye (kendi profiline) gelen tüm erişim talepleri — bekleyen,
    onaylı, reddedilmiş, iptal edilmiş; hepsi görünür (şeffaflık)."""
    profil = request.user.profil
    talepler = ErisimTalebi.objects.filter(profil=profil).select_related("kurum")
    return Response({"talepler": [
        {
            "id": t.id, "kurum": t.kurum.ad, "kurum_kod": t.kurum.kod, "amac": t.amac,
            "durum": t.durum, "gecerlilik_bitis": t.gecerlilik_bitis.isoformat() if t.gecerlilik_bitis else None,
            "created_at": t.created_at.isoformat(timespec="seconds"), "aktif_mi": t.aktif_mi(),
        }
        for t in talepler
    ]})


def _kendi_talebi_getir(request, talep_id):
    try:
        return ErisimTalebi.objects.select_related("kurum", "profil").get(
            id=talep_id, profil=request.user.profil
        )
    except (ErisimTalebi.DoesNotExist, ValueError, TypeError):
        return None


@api_view(["POST"])
@permission_classes([ProfilSahibi])
def erisim_talebi_onayla(request, talep_id: int):
    talep = _kendi_talebi_getir(request, talep_id)
    if talep is None:
        return Response({"hata": "Talep bulunamadı"}, status=404)
    if talep.durum != "bekliyor":
        return Response({"hata": f"Talep zaten '{talep.durum}' durumunda"}, status=400)

    # `int(...)` çıplak bırakılınca sayı olmayan bir değer (ör. "otuz")
    # ValueError fırlatıp 500 döndürüyordu — kullanıcı hatası 500 olmamalı.
    try:
        gecerlilik_gun = int(request.data.get("gecerlilik_gun") or 30)
    except (TypeError, ValueError):
        return Response({"hata": "gecerlilik_gun bir tam sayı olmalı"}, status=400)

    talep.durum = "onaylandi"
    talep.karar_at = timezone.now()
    talep.gecerlilik_bitis = timezone.now() + timezone.timedelta(days=max(1, min(gecerlilik_gun, 365)))
    talep.save(update_fields=["durum", "karar_at", "gecerlilik_bitis"])
    _riza_yaz(talep, "onaylandi", request)
    return Response({"onaylandi": True, "gecerlilik_bitis": talep.gecerlilik_bitis.isoformat()})


@api_view(["POST"])
@permission_classes([ProfilSahibi])
def erisim_talebi_reddet(request, talep_id: int):
    talep = _kendi_talebi_getir(request, talep_id)
    if talep is None:
        return Response({"hata": "Talep bulunamadı"}, status=404)
    if talep.durum != "bekliyor":
        return Response({"hata": f"Talep zaten '{talep.durum}' durumunda"}, status=400)

    talep.durum = "reddedildi"
    talep.karar_at = timezone.now()
    talep.save(update_fields=["durum", "karar_at"])
    _riza_yaz(talep, "reddedildi", request)
    return Response({"reddedildi": True})


@api_view(["POST"])
@permission_classes([ProfilSahibi])
def erisim_talebi_iptal(request, talep_id: int):
    """Onaylanmış bir erişimi GERİ ALMA — PO kararı: onay "süreli ve iptal
    edilebilir" olmalı. `durum` değişince `izinler.aktif_riza()` artık bu
    talebi döndürmez, kurum erişimi anında kesilir."""
    talep = _kendi_talebi_getir(request, talep_id)
    if talep is None:
        return Response({"hata": "Talep bulunamadı"}, status=404)
    if talep.durum != "onaylandi":
        return Response({"hata": "Yalnızca onaylanmış bir erişim iptal edilebilir"}, status=400)

    talep.durum = "iptal_edildi"
    talep.karar_at = timezone.now()
    talep.save(update_fields=["durum", "karar_at"])
    _riza_yaz(talep, "iptal_edildi", request)
    return Response({"iptal_edildi": True})


@api_view(["GET"])
@permission_classes([ProfilSahibi])
def riza_defterim(request):
    """Müşterinin KENDİ rıza defteri — kim, ne zaman, ne için erişti/erişmeye
    çalıştı. Append-only `RizaKaydi`'nin doğrudan okunabilir hâli."""
    profil = request.user.profil
    kayitlar = RizaKaydi.objects.filter(aks_no=profil.aks_no).select_related("erisim_talebi__kurum")
    return Response({"kayitlar": [
        {
            "id": k.id, "olay": k.olay, "kurum": k.erisim_talebi.kurum.ad,
            "amac": k.erisim_talebi.amac, "created_at": k.created_at.isoformat(timespec="seconds"),
        }
        for k in kayitlar
    ]})
