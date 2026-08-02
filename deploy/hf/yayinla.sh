#!/usr/bin/env bash
# AKS -> Hugging Face Spaces yayın betiği.
#
# Kullanım:
#   deploy/hf/yayinla.sh https://huggingface.co/spaces/<kullanici>/<space-adi>
#   deploy/hf/yayinla.sh --hazirla <dizin>    # göndermeden, yalnızca içeriği üret
#
# `--hazirla`, Space'e gidecek ağacı bir dizine çıkarır. Docker build'i bu
# dizinde denemek, canlıya çıkmadan önce gerçek dağıtım içeriğini (ve bu
# betiğin kendisini) test etmenin yoludur.
#
# NEDEN AYRI BİR BETİK (doğrudan `git push hf main` yerine)?
# Hugging Face, Space'in yapılandırmasını (sdk: docker, app_port) SADECE
# deponun kökündeki README.md'nin YAML ön-bilgisinden okur. Bu depodaki
# README.md ise YZTA Bootcamp jürisinin notlandırdığı teslim belgesi
# (CLAUDE.md: "asla silinmez/düzenlenmez"). İkisi aynı dosya adını istediği
# için depolar birleştirilemez; bu betik Space kopyasındaki README.md'yi
# ÜRETİR ve bizim README'mize hiç dokunmaz.
#
# Ek fayda: kopyalama `git ls-files` üzerinden yapılır — yani yalnızca
# versiyonlanmış dosyalar gider. `.env`, `.venv/`, `node_modules/`,
# `aks_dev.sqlite3` gibi sır/çöp Space'e FİZİKSEL OLARAK giremez.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Space ağacını $1'de verilen dizine üretir. Hem yayında hem `--hazirla`
# modunda AYNI kod çalışır — yani denenen şey, gönderilen şeydir.
hazirla() {
    local hedef="$1"

    echo "==> Kaynaklar kopyalanıyor (yalnızca git'in tanıdığı dosyalar)"
    cd "$REPO"
    # stitch-output/ hariç: Google Stitch'in tasarım referansı (mockup HTML'leri +
    # 5 ekran görüntüsü, ~1.7 MB). Dağıtımda HİÇ kullanılmıyor — Vite yalnızca
    # src/'yi paketliyor. Dahası HF'in pre-receive hook'u bu PNG'ler için git-lfs
    # dayatıp push'u reddediyor. Referans olarak GitHub deposunda kalıyor.
    git ls-files -z product/01-data product/02-ai-agents product/03-frontend product/04-backend \
        ':(exclude)product/03-frontend/stitch-output/*' \
        | while IFS= read -r -d '' dosya; do
            mkdir -p "$hedef/$(dirname "$dosya")"
            cp "$dosya" "$hedef/$dosya"
        done

    # Dockerfile ve .dockerignore Space'in KÖKÜNE gider (build bağlamı orası).
    cp "$REPO/deploy/Dockerfile" "$hedef/Dockerfile"
    cp "$REPO/.dockerignore" "$hedef/.dockerignore"
    mkdir -p "$hedef/deploy"
    cp "$REPO/deploy/baslat.sh" "$hedef/deploy/baslat.sh"
    chmod +x "$hedef/deploy/baslat.sh"

    # HF'in pre-receive hook'u ikili dosyaları düz git ile kabul etmiyor
    # ("Your push was rejected because it contains binary files"). Model
    # artifact'ları (`anomali_model.joblib`, 2.7 MB) çalışma anında GEREKLİ,
    # atlanamaz — bu yüzden Space kopyasında LFS ile izleniyor. HF, imajı
    # derlerken LFS içeriğini çözüyor, dolayısıyla konteynere gerçek dosya iniyor.
    # `eol=lf` kuralı da buraya taşınıyor: kök .gitattributes Space'e
    # kopyalanmıyor ve CRLF'e dönen bir `baslat.sh` konteyneri
    # "no such file or directory" ile düşürürdü.
    echo "==> Space .gitattributes (LFS + LF satır sonu) yazılıyor"
    cat > "$hedef/.gitattributes" <<'ATTR'
*.joblib filter=lfs diff=lfs merge=lfs -text
*.sh        text eol=lf
Dockerfile  text eol=lf
ATTR

    echo "==> Space yapılandırması (README.md) üretiliyor"
    cat > "$hedef/README.md" <<'YAML'
---
title: AKS - Alternatif Kapasite Skoru
emoji: 📊
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
# HF sınırı: short_description en fazla 60 karakter (aşarsa push reddedilir).
short_description: Alternatif verilerle finansal kapasite skorlama
---

# AKS — Alternatif Kapasite Skoru

Bu depo bir **dağıtım kopyasıdır**; `deploy/hf/yayinla.sh` tarafından üretilir.
Bu dosyanın kendisi Hugging Face Space yapılandırmasıdır — projenin gerçek
README'si, dokümantasyonu ve commit geçmişi GitHub deposundadır.

Elle düzenlemeyin: bir sonraki yayında üzerine yazılır.
YAML
}

# --- Mod 1: yalnızca hazırla (göndermeden dene) ---
if [ "${1:-}" = "--hazirla" ]; then
    HEDEF="${2:-}"
    [ -z "$HEDEF" ] && { echo "Kullanım: $0 --hazirla <dizin>" >&2; exit 1; }
    mkdir -p "$HEDEF"
    hazirla "$(cd "$HEDEF" && pwd)"
    echo ""
    echo "==> Hazır: $HEDEF"
    echo "    Denemek için:  docker build -t aks:test \"$HEDEF\""
    exit 0
fi

# --- Mod 2: yayınla ---
SPACE_URL="${1:-}"
if [ -z "$SPACE_URL" ]; then
    echo "Kullanım: $0 https://huggingface.co/spaces/<kullanici>/<space-adi>" >&2
    echo "         $0 --hazirla <dizin>" >&2
    echo "" >&2
    echo "Kimlik doğrulama için token'ı URL'e gömebilirsiniz:" >&2
    echo "  $0 https://<kullanici>:hf_XXXX@huggingface.co/spaces/<kullanici>/<space-adi>" >&2
    exit 1
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

echo "==> Space deposu klonlanıyor"
git clone --depth 1 "$SPACE_URL" "$STAGE/space"

echo "==> Eski içerik temizleniyor (.git korunuyor)"
# Depodan SİLİNEN dosyalar Space'te hayalet olarak kalmasın diye önce boşaltılıp
# baştan dolduruluyor.
find "$STAGE/space" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +

hazirla "$STAGE/space"

echo "==> Space'e gönderiliyor"
cd "$STAGE/space"
# LFS filtresi `git add`'den ÖNCE kayıtlı olmalı; aksi halde .joblib dosyaları
# pointer yerine ham içerikle indekslenir ve hook yine reddeder.
git lfs install --local >/dev/null
git add -A
if git diff --cached --quiet; then
    echo "!! Değişiklik yok, gönderilmedi."
    exit 0
fi
git commit -m "AKS dağıtımı — $(cd "$REPO" && git rev-parse --short HEAD)"
git push

echo ""
echo "==> Tamam. Space yeniden derleniyor (ilk build ~5-10 dk sürer)."
echo "    Build günlüğünü Space sayfasındaki 'Logs' sekmesinden izleyin."
