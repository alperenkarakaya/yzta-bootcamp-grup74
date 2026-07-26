"""AKS numarası üretimi — rastgele, KİŞİSEL VERİDEN BAĞIMSIZ, checksum'lı
pseudonim kimlik. Format: `AKS-XXXX-XXXX-XC` (Crockford Base32; karışan
karakterler I/L/O/U alfabeden çıkarıldı — elle yazarken/okurken hata payı
azalır, banka personeli müşteriden bu numarayı isteyebilir).

execution.md §3b Phase 7 / 7.2 — PO kararı: "e-posta + telefon OTP", TCKN/isim
YOK. Bu numara hiçbir kimlik belgesinden türetilmez; yalnızca `secrets` ile
üretilen rastgele bitlerin kodlanmış hâlidir — iki kullanıcı asla aynı
numarayı paylaşmaz (DB `unique=True` ile de garanti altına alınır) ama
numaradan geriye kişiye dönük hiçbir bilgi çıkarılamaz.
"""
import secrets

# Crockford Base32 — 0/O, 1/I/L, 2/Z gibi karışan karakterlerin bir kısmı
# elenmiş; standart, yaygın kullanılan bir "insan tarafından okunabilir kimlik"
# kodlaması (bkz. ULID, ISBN benzeri checksum'lı kodlar).
_ALFABE = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_GOVDE_UZUNLUK = 9  # 45 bit rastgelelik


def _base32_kodla(sayi: int, uzunluk: int) -> str:
    karakterler = []
    for _ in range(uzunluk):
        sayi, kalan = divmod(sayi, 32)
        karakterler.append(_ALFABE[kalan])
    return "".join(reversed(karakterler))


def _checksum(govde: str) -> str:
    toplam = sum(_ALFABE.index(c) for c in govde)
    return _ALFABE[toplam % 32]


def uret() -> str:
    """Yeni bir AKS numarası üretir: `AKS-XXXX-XXXX-XC` (C = checksum hanesi).

    Çağıran taraf (kimlik.models.Profil kaydı) DB unique kısıtıyla çakışma
    ihtimaline karşı yeniden deneme yapmalı — 45 bitlik uzayda çakışma
    olasılığı ihmal edilebilir düzeyde ama sıfır değil.
    """
    ham = secrets.randbits(_GOVDE_UZUNLUK * 5)
    govde = _base32_kodla(ham, _GOVDE_UZUNLUK)
    kontrol = _checksum(govde)
    return f"AKS-{govde[0:4]}-{govde[4:8]}-{govde[8]}{kontrol}"


def gecerli_mi(aks_no: str) -> bool:
    """Checksum doğrulaması — bir kurum personeli numarayı elle girerken
    yazım hatasını erken yakalar. Bu bir KİMLİK doğrulaması DEĞİL, yalnızca
    FORMAT doğrulaması (bkz. plan §"Dürüstlük notu")."""
    if not aks_no or not aks_no.startswith("AKS-"):
        return False
    parcalar = aks_no[4:].replace("-", "")
    if len(parcalar) != _GOVDE_UZUNLUK + 1:
        return False
    govde, kontrol = parcalar[:_GOVDE_UZUNLUK], parcalar[_GOVDE_UZUNLUK]
    if any(c not in _ALFABE for c in govde + kontrol):
        return False
    return _checksum(govde) == kontrol
