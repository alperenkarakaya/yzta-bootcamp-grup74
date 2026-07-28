"""
Kullanıcı portalı kimlik doğrulaması — session tabanlı, Django'nun kendi
`django.contrib.auth` sistemi (Supabase Auth DEĞİL — OQ-33'ün bu kapsamdaki
karşılığı: ek credential/kurulum gerektirmeyen, hazır şifre-hashleme içeren
yol PO tarafından seçildi, execution.md §3b Phase 6).

Kullanıcı adı = e-posta (özel bir User modeli yok, `django.contrib.auth.User`
doğrudan kullanılıyor — küçük ayak izi, ekstra migration riski yok).

CSRF: DRF'nin `SessionAuthentication`'ı, session ile kimliği doğrulanmış her
istekte CSRF token'ı zorunlu kılar (Django'nun genel CsrfViewMiddleware'i DRF
view'larında devre dışıdır — bkz. `APIView.csrf_exempt`). Frontend, `ben()`
çağrısıyla `csrftoken` çerezinin var olduğundan emin olur (`ensure_csrf_cookie`)
ve sonraki POST'larda `X-CSRFToken` header'ında gönderir.

§3b Phase 7/7.2: her yeni kayıtta otomatik olarak bir `kimlik.Profil` (rastgele
AKS numarası) oluşturulur — isim/soyisim/TCKN İSTENMEZ, yalnızca e-posta+şifre.
Telefon doğrulaması ayrı, opsiyonel bir sonraki adımdır (`kimlik/views.py`).
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def _kullanici_sozluk(user):
    # "ad" yalnızca arayüzde selamlama için türetilir (e-posta yerel kısmı) —
    # saklanan bir kişisel veri DEĞİLDİR (§3b Phase 7/7.2: isim/soyisim istenmez).
    #
    # `yonetici` / `kurum_uyesi`: frontend'in giriş sonrası kullanıcıyı DOĞRU
    # yüzeye yönlendirebilmesi için (banka içi araştırma / kurum paneli /
    # müşteri portalı). Bunlar yalnızca YÖNLENDİRME ipucudur — gerçek yetki
    # kontrolü her zaman sunucuda, ilgili izin sınıfındadır (YoneticiKullanici,
    # KurumUyesi, ProfilSahibi). Frontend'de bayrağı taklit etmek hiçbir veriye
    # erişim sağlamaz, yalnızca 403 alınan bir sayfaya gider.
    from kimlik.models import KurumUyeligi
    sozluk = {
        "id": user.id,
        "email": user.email,
        "ad": user.email.split("@")[0],
        "yonetici": user.is_staff,
        "kurum_uyesi": KurumUyeligi.objects.filter(user=user).exists(),
    }
    profil = getattr(user, "profil", None)
    if profil is not None:
        sozluk["aks_no"] = profil.aks_no
    return sozluk


def _profil_olustur(user):
    """Rastgele AKS numarası üretir ve `Profil`'e bağlar. 45 bitlik uzayda
    çakışma ihtimali ihmal edilebilir düzeyde ama `unique=True` kısıtına karşı
    birkaç kez denenir (kayıt akışını asla sonsuz döngüye sokmaz)."""
    from kimlik.aks_no import uret
    from kimlik.models import Profil
    for _ in range(5):
        try:
            with transaction.atomic():
                return Profil.objects.create(user=user, aks_no=uret())
        except IntegrityError:
            continue
    raise RuntimeError("AKS numarası üretilemedi (çakışma sınırı aşıldı)")


@ensure_csrf_cookie
@api_view(["GET"])
def ben(request):
    """Oturum durumu + CSRF çerezini garanti eder — frontend her açılışta çağırır."""
    if request.user.is_authenticated:
        return Response(_kullanici_sozluk(request.user))
    return Response({"giris_yapmamis": True}, status=401)


@api_view(["POST"])
def kayit(request):
    email = (request.data.get("email") or "").strip().lower()
    sifre = request.data.get("sifre") or ""
    try:
        validate_email(email)
    except DjangoValidationError:
        return Response({"hata": "Geçersiz e-posta adresi"}, status=400)
    if User.objects.filter(username=email).exists():
        return Response({"hata": "Bu e-posta ile zaten bir hesap var"}, status=400)
    try:
        validate_password(sifre)
    except DjangoValidationError as e:
        return Response({"hata": " ".join(e.messages)}, status=400)
    # Kullanıcı + profil TEK transaction'da: `create_user` başarılı olup
    # `_profil_olustur` patlarsa geriye AKS numarası OLMAYAN yetim bir hesap
    # kalıyordu — o hesap giriş yapabiliyor ama portal uçlarında `ProfilSahibi`
    # izninden geçemediği için hiçbir şey yapamıyordu (sessiz, kalıcı bozuk
    # durum). Ayrıca yukarıdaki `exists()` kontrolü ile `create_user` arasında
    # bir yarış penceresi var (aynı e-postayla iki eşzamanlı kayıt) — bunu
    # `username` unique kısıtı yakalar, IntegrityError'ı 500 yerine anlamlı bir
    # 400'e çeviriyoruz.
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=email, email=email, password=sifre)
            _profil_olustur(user)
    except IntegrityError:
        return Response({"hata": "Bu e-posta ile zaten bir hesap var"}, status=400)
    login(request, user)
    return Response(_kullanici_sozluk(user), status=201)


@api_view(["POST"])
def giris(request):
    email = (request.data.get("email") or "").strip().lower()
    sifre = request.data.get("sifre") or ""
    user = authenticate(request, username=email, password=sifre)
    if user is None:
        return Response({"hata": "E-posta veya şifre hatalı"}, status=401)
    login(request, user)
    return Response(_kullanici_sozluk(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cikis(request):
    logout(request)
    return Response({"cikis_yapildi": True})
