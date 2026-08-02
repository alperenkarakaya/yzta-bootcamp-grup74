from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404, JsonResponse
from django.urls import include, path, re_path


def kok(_request):
    return JsonResponse({
        "servis": "AKS - Alternatif Kapasite Skoru API (Django)",
        "api": "/api/",
        "admin": "/admin/",
        "docs": "/api/bilgi",
    })


def spa(request):
    """React Router'ın sahip olduğu yolları derlenmiş arayüze devreder.

    Tek servis dağıtımında (§7.15) `/panel`, `/portal/*`, `/kurum/*` gibi yollar
    sunucuda TANIMLI DEĞİL — yönlendirme tarayıcıda React Router'da yapılıyor.
    Kullanıcı bu adreslerden birini doğrudan açtığında (veya sayfayı
    yenilediğinde) Django'ya bir istek gelir; bu view olmasaydı 404 dönerdi.

    Yerelde `spa/` dizini bulunmadığı için davranış değişmez: kök hâlâ API
    künyesini döndürür, eşleşmeyen yol hâlâ 404 verir.
    """
    if settings.SPA_INDEX.is_file():
        yanit = FileResponse(open(settings.SPA_INDEX, "rb"), content_type="text/html")
        # Vite varlıkları hash'li olduğu için sonsuza dek cache'lenebilir, ama
        # index.html o hash'lere işaret eden TEK sabit adres — cache'lenirse
        # tarayıcı yeni dağıtımdan sonra silinmiş dosyaları ister ve arayüz
        # beyaz ekrana düşer.
        yanit["Cache-Control"] = "no-cache"
        return yanit
    if request.path == "/":
        return kok(request)
    raise Http404()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/kimlik/", include("kimlik.urls")),  # §3b Phase 7/7.2
    # EN SONDA olmalı: yakalanmayan her yolu SPA'ya devreder. `api/`, `admin/`
    # ve `static/` negatif ileri-bakışla dışarıda bırakıldı — aksi halde
    # var olmayan bir API ucu, JSON 404 yerine sessizce HTML döndürür ve
    # istemci tarafında "Unexpected token '<'" gibi teşhis edilmesi zor bir
    # hataya dönüşürdü.
    re_path(r"^(?!api/|admin/|static/).*$", spa),
]
