"""
Sahiplik savunması — execution.md §3b Phase 7 / 7.3.

ÜÇ katmandan İKİSİ burada: belge parmak izi çakışma tespiti + davranışsal
tutarlılık kontrolü. Üçüncüsü (zorunlu beyan) `portal_views.portal_yukle`'de.

Dürüstlük notu (plan §"Dürüstlük notu"): bu modül "başkasının verisini
yüklemeyi ENGELLEMEZ" — minimum kişisel veriyle bu teknik olarak mümkün
değil. Yalnızca TESPİT eder; bayraklar karar mekanizmasını ASLA değiştirmez,
yalnızca kurum tarafına şeffaflık sinyali olarak gösterilir (`anomali_bayrak`
ile aynı desen — overview.md §7 sınırı burada da korunur).
"""
GELIR_TUTARLILIK_ORANI = 3.0  # yeni/geçmiş medyan oranı bu değeri aşarsa/altına inerse bayrak


def coklu_sahiplik_kontrol(parmak_izi, profil):
    """Aynı belge içeriği (parmak izi) BAŞKA bir profil altında daha önce
    yüklenmiş mi? Varsa hem yeni hem eski kayıt(lar) `coklu_sahiplik_supheli`
    ile işaretlenir (eskiler retroaktif güncellenir — Assessment append-only
    DEĞİL, yalnızca AuditLog öyle; bayrak eklemek geçmiş kararı değiştirmez).

    Döner: bool — yeni kayıt için bayrak eklenmeli mi.
    """
    if not parmak_izi:
        return False
    from audit.models import Assessment

    cakisan = Assessment.objects.filter(belge_parmak_izi=parmak_izi).exclude(profil=profil)
    if not cakisan.exists():
        return False

    for eski in cakisan:
        if "coklu_sahiplik_supheli" not in eski.sahiplik_bayraklari:
            eski.sahiplik_bayraklari = [*eski.sahiplik_bayraklari, "coklu_sahiplik_supheli"]
            eski.save(update_fields=["sahiplik_bayraklari"])
    return True


def davranissal_tutarlilik_kontrol(profil, yeni_ozellikler):
    """Yeni yükleme, bu profilin GEÇMİŞ yüklemeleriyle kaba ölçekte tutarlı mı?

    Basit, açıklanabilir bir sezgisel kural: gelir hacmi geçmiş medyanın
    `GELIR_TUTARLILIK_ORANI` katından fazla sapmışsa (çok daha yüksek ya da
    çok daha düşük) `profil_tutarsiz` bayrağı üretir. Bu bir suçlama değil —
    "iki farklı kişinin hesabı karışmış olabilir" ya da "kullanıcı gerçekten
    çok farklı bir dönem yükledi" ikisi de olabilir; kurum tarafı yorumlar.

    En az 2 geçmiş kayıt yoksa (yeni müşteri) kontrol atlanır — yanlış pozitif
    üretmemek için (bkz. anomali.py'nin de uyguladığı "veri yoksa sessiz kal"
    ilkesi).
    """
    from audit.models import Assessment

    gecmis = list(
        Assessment.objects.filter(profil=profil)
        .exclude(ozellikler={})
        .order_by("-created_at")
        .values_list("ozellikler", flat=True)[:10]
    )
    gecmis_gelirler = [o.get("toplam_gelir_hacmi") for o in gecmis if o.get("toplam_gelir_hacmi")]
    if len(gecmis_gelirler) < 2:
        return False

    gecmis_gelirler = sorted(gecmis_gelirler)
    medyan = gecmis_gelirler[len(gecmis_gelirler) // 2]
    yeni_gelir = yeni_ozellikler.get("toplam_gelir_hacmi")
    if not medyan or yeni_gelir is None:
        return False

    oran = yeni_gelir / medyan
    return oran > GELIR_TUTARLILIK_ORANI or oran < (1 / GELIR_TUTARLILIK_ORANI)
