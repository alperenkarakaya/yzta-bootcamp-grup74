# Sprint 1 — Daily Scrum & Ekip Koordinasyon Notları

**Sprint aralığı:** 19 Haziran – 5 Temmuz 2026
**Kanal:** Slack (grup DM + huddle). Toplantılar zaman kısıtı nedeniyle çoğunlukla
asenkron, yazılı yürütüldü; iki kez sesli huddle yapıldı.

> Not: Aşağıdaki kayıtlar ekibin Slack yazışmalarından ve huddle'larından
> derlenmiştir. İlgili Slack ekran görüntüleri bu klasöre eklenebilir.

---

## 21–22 Haziran — Fikir turu

Ekip birden fazla proje fikri tartıştı. Zeynep görüntü işleme temelli fikirler
önerdi: belediyeye yol/altyapı bozukluklarını otomatik bildiren bir sistem ve
tarım alanında görüntü işlemeli bir çözüm. Alperen bu fikirlerin bilinen ama
bootcamp'e uygunluğu konusunda çekince belirtti. Tartışma sonunda finans/kredi
yönünde ilerlemeye karar verildi.

- **Engel:** Net bir fikirde çok uzun takılı kalmamak. → Kredi skorlama fikrinde
  hızlıca karar kılınarak aşıldı.

## 23 Haziran (Salı)

- **Alperen (PO):** Repo/form erişimini çözdü ("şimdi ekleyebildim"), kurulum
  tarafını hazırladı.

## 28–29 Haziran — Fikrin netleşmesi ve başvuru

Nihai fikir yazıya döküldü ve başvuru formu gönderildi:

> "Banka kredisi reddedilen ya da düşük limit alan kişilerin banka hareketlerini
> analiz ederek görmezden gelinen gerçek gelir/kapasitesini ortaya çıkaran,
> alternatif bir kredi skoru üreten ve skoru artırmak için tavsiye veren yapay
> zeka uygulaması."

- **Alperen (PO):** Fikri formüle etti, başvuru formunu gönderdi.
- **Ahmet (SM):** Fikri onayladı ("eline sağlık"), süreç dokümantasyonunu üstlendi.
- **Havva (Dev):** Bilgisayarı bozulmuş; çalışmaya devam ediyor, üzerine düşen
  görevi tamamlayacağını bildirdi.
- **Engel:** Slack bildirimlerinin güvenilmez olması. → Ekip, koordinasyonu
  huddle ve ek kanal üzerinden de sürdürme kararı aldı.

## 30 Haziran (Salı) — 43 dakikalık huddle

- **Ahmet (SM):** Referans olarak Akademi'nin BootcampScrumTemplate repo'sunu
  paylaştı; Sprint dokümantasyon formatı buna göre kuruldu.
- **Alperen (PO):** Proje kapsamını netleştirdi — küçük çaplı kredilerde
  (öğrenci/stajyer) işlem hacmi yüksek olmasına rağmen düşük limit verilmesi,
  bankanın bu segmentte kaçırdığı getiri, ve iki tarafı da kazançlı kılacak
  alternatif skor hedefi.
- **Ahmet (SM):** İlk kod paketini paylaştı — sentetik veri üreticisi, özellik
  mühendisliği + skorlama motoru, skor raporu ve README.
- Veri güvenliği/KVKK için bir "veri yolculuğu" şeması hazırlandı: giriş ve
  maskeleme → saklama → işleme (AI model çağrısı) → erişim ve çıktı.

## 3–4 Temmuz — Sprint 1 kapanışı

- **Zeynep (Dev):** Mevcut durumu inceledi, onay verdi ("gayet okey").
- **Alperen (PO):** GitHub'a push durumunu takip etti; Sprint 1 teslimi için repo
  son haline getirildi.
- **Ahmet (SM):** README, board görseli ve ürün durumu görseli dahil tüm Sprint 1
  dokümantasyonunu tamamladı.

---

## Sprint 1 boyunca öne çıkan engeller (blockers)

| Engel | Çözüm |
|---|---|
| Slack bildirimlerinin düzensiz gelmesi | Huddle + ek kanal üzerinden koordinasyon |
| Bir üyenin donanım (bilgisayar) sorunu | Görev dağılımı korundu, iş devam etti |
| Fikir seçiminde zaman kaybı riski | Kredi skorlama fikrinde erken karar |

---

## Slack kanıt görüntüleri

Bu klasördeki ilgili ekran görüntüleri:

- `slack_01_fikir_tartismasi.png` — proje fikri tartışması (görüntü işleme fikirleri → kredi skorlama kararı) ve veri güvenliği/KVKK katman şeması
- `slack_02_fikir_form_gorev.png` — nihai fikrin forma yazılması ve ekip içi görev sahiplenmeleri
- `slack_03_huddle_roadmap.png` — 43 dk huddle thread'i, referans template ve proje kapsamının netleştirilmesi
- `slack_04_koordinasyon.png` — genel koordinasyon ve GitHub push takibi
