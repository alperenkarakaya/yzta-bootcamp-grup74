# Sprint 3 — Daily Scrum & Ekip Koordinasyon Notları

**Sprint aralığı:** 20 Temmuz – 2 Ağustos 2026
**Kanallar:** Slack (`#bootcamp-2026` + ekip kanalı), Instagram grup mesajlaşması
ve sesli huddle. Sprint 1 ve 2'de olduğu gibi toplantılar asenkron ve yazılı
yürütüldü; sprint açılışı sesli huddle ile yapıldı.

> Not: Aşağıdaki kayıtlar ekibin Slack yazışmalarından, Instagram grup
> mesajlarından ve huddle'lardan derlenmiştir. İlgili ekran görüntüleri bu klasörde.

---

## 19 Temmuz gecesi — Sprint Planning (huddle)

Sprint 3'ün resmi aralığı 20 Temmuz'da açılıyordu; ekip planlamayı bir gece
önce, 19 Temmuz akşamı sesli huddle'da yaptı. Sprint kapsamı ve iç takvim bu
toplantıda belirlendi ve sprint 20 Temmuz sabahı bu planla başladı.

- **Alperen (PO) — iç takvim:** Konuşulan değişikliklerin **22 Temmuz Çarşamba**
  gün sonuna kadar yapılması, projenin **29 Temmuz Çarşamba**'ya kadar
  bitirilmesi, kalan sürenin eklemeler için ayrılması kararlaştırıldı. Bootcamp
  teslim tarihi 2 Ağustos 23.59 olduğu için iç takvim üç günlük bir tampon
  bırakacak şekilde kuruldu.
- **Alperen (PO) — kapsam:** Sprint dört başlık altında toplandı: model
  optimizasyonu, karar mekanizması değişiklikleri ve veri ile model eğitimi,
  frontend değişiklikleri, metrik değişiklikleri.
- **Huddle katılımcıları:** Alperen Karakaya, Ahmet Özdoğan, Havva Balta,
  Zeynep Salkaya.

> Scrum'a göre her Sprint bir Sprint Planning ile başlar. Bu toplantı Sprint 3'ün
> planning etkinliğidir; takvimsel olarak sprint penceresinden birkaç saat önce
> yapılmıştır.

## 20 Temmuz — Dürüst benchmark hattı devreye alındı

Sprint 2'nin döngüsellik bulgusundan sonra ilk iş, dekuple veri üreticisini
eğitim ve değerlendirme hattına bağlamaktı.

- **Ahmet (SM):** Eğitim ve değerlendirme dekuple veri kaynağına taşındı
  (2000 müşteri, taban temerrüt oranı %17.15). Değerlendirme harness'ı
  `RepeatedStratifiedKFold(5×5)` + bootstrap %95 CI, OOF Brier/ECE/reliability
  ve persona bazlı kırılım üretecek şekilde genişletildi.
- **Bulgu — basit model kazandı:** Lojistik regresyon dört metrikte de
  gradient boosting'i geçti (AUC 0.8621 vs 0.8399, PR-AUC 0.6096 vs 0.5571,
  Brier 0.0979 vs 0.1054, ECE 0.0141 vs 0.0337). Güven aralıkları kesişmiyor.
  Sprint 2'de "klasik yöntem varsayılan olarak kazanır" diye bıraktığımız
  karar doğrulandı; üretimdeki model `LogisticRegression`'a çevrildi.
- **Bulgu — kalibrasyon fark yaratmadı:** İzotonik kalibrasyon eklendi ve
  ölçüldü. ECE 0.0391 → 0.0394. Model zaten kalibre olduğu için düzeltilecek
  bir şey bulunamadı. Adım hatta bırakıldı, kazanım olarak raporlanmıyor.
- **Ahmet (SM):** Django geçişinde kırılan test paketi yeniden kuruldu —
  24 `aks_core` + 15 Django API testi.

## 23 Temmuz — Veri paylaşımı, kapsamın detaylandırılması, görev dağılımı

- **Zeynep (Dev):** Hazırladığı veri paketini (`Akademi.rar`) ekip kanalında
  paylaştı.
- **Alperen (PO):** 19 Temmuz'da dört başlık olarak açıklanan kapsamı madde
  madde detaylandırdı ve sprintin ana hedefini yazıya döktü.
- **Ana hedef:** "İnce dosyalı ama aslında güvenilir müşterilere, sabit bir
  risk seviyesinde, gerçekten daha fazla kredi onayı verebiliyoruz" iddiasını
  dürüst ve kanıtlanmış şekilde ortaya koymak. Tek bir başarı rakamı
  hedefleniyor: *aynı riski taşırken bu segmentte yüzde kaç daha fazla iyi
  müşteriyi onaylayabiliyoruz* — güven aralığıyla ve dairesel olmayan veriyle.
- **Alperen (PO):** "No-go" da geçerli bir sonuç olarak tanımlandı. Sonucu
  bükmemek sprintin açık kuralı.
- **Engel — veri tutarsızlığı:** Canlı demoda kullanılan veri seti ile arka
  planda düzeltilmiş veri seti aynı değil. "Eğitimde bir veri, ekranda başka
  veri" durumu tek ve tutarlı bir hikâye anlatmayı engelliyor. → Birleştirme
  Zeynep'in kapsamında.
- **Engel — yayımlanmış rakamlar güncel değil:** README ve arayüzdeki AUC ve
  "kurtarılan müşteri" sayıları Sprint 2'nin döngüsel verisinden geliyor.
  → Metrik başlığı altında güncellenecek.
- **Engel — iç takvim kaydı:** 22 Temmuz hedefi tam olarak tutmadı; kapsamın
  detaylandırılması 23 Temmuz'a sarktı. 29 Temmuz hedefi korunuyor.

**Görev dağılımı:**

| Alan | Sahip |
|---|---|
| Araştırma | Havva |
| Model optimizasyonu ve metrik kontrolleri | Alperen, Ahmet |
| Veri ve sentetik veri hazırlığı | Zeynep |

Veri tarafında değişiklik/ekleme gerektiğinde ihtiyaç anında koordine
olunacak şekilde anlaşıldı.

---

## 24 Temmuz – 2 Ağustos — Sprint'in kalan günleri

> Bu bölüm plandır, kayıt değil. Gerçekleşen daily scrum notları gün geçtikçe
> buraya eklenecektir.

İç takvime göre 29 Temmuz'a kadar proje bitmiş, kalan günler ekleme ve
kapanış için ayrılmış olacak.

`<!-- TODO: günlük kayıtlar buraya. Bootcamp teslimi 2 Ağustos 23.59. -->`

---

| Engel | Çözüm |
|---|---|
| Headline sayı Sprint 2'de yapısal olarak geçersiz çıkmıştı | Dekuple hat devreye alındı, tüm metrikler yeniden üretildi |
| Django geçişinde 22 test kırılmıştı | Test paketi iki pakete taşındı, 39 test çalışıyor |
| 22 Temmuz iç hedefi tam tutmadı | Kapsam 23 Temmuz'da netleşti; 29 Temmuz hedefi korundu |
| Demo verisi ile eğitim verisi farklı | `<!-- TODO: birleştirme sonrası doldurulacak -->` |
| Yayımlanmış rakamlar döngüsel veriden geliyor | `<!-- TODO -->` |

---

## Kanıt görüntüleri

**Huddle:**

- `huddle_sprint3.png` — 19 Temmuz gecesi yapılan Sprint Planning huddle'ı

**Slack (dokümantasyon ve duyurular):**

- `slack_01_ic_takvim.png` — Sprint Planning çıktısı: iç takvim (22/29 Temmuz) ve dört başlıklı kapsam
- `slack_02_yapilacaklar.png` — 23 Temmuz detaylı yapılacaklar listesi
- `slack_03_ana_hedef_gorev.png` — ana hedef ve görev dağılımı

**Instagram grup DM (günlük koordinasyon):**

- `<!-- TODO -->`
