# Sprint 3 — Daily Scrum & Ekip Koordinasyon Notları

**Sprint aralığı:** 20 Temmuz – 2 Ağustos 2026
**Kanallar:** Slack (`#bootcamp-2026` + ekip kanalı), Instagram grup mesajlaşması
ve sesli huddle. Sprint 1 ve 2'de olduğu gibi toplantılar asenkron ve yazılı
yürütüldü; sprint açılışı sesli huddle ile yapıldı.

> Not: Aşağıdaki kayıtlar ekibin Slack yazışmalarından, huddle'lardan ve
> Instagram grup mesajlarından derlenmiştir. İlgili ekran görüntüleri (Slack
> koordinasyonu, huddle, çalışan arayüz ve board dâhil) bu klasörde.

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

## 25 Temmuz (Cumartesi) — Güncel veri seti teslim edildi

- **Zeynep (Dev):** "Dosyaların güncel hali burada" — güncellenmiş veri
  paketini (`Akademi.rar`) ekip kanalında paylaştı. Bir gün önce "verileri
  tekrar hazırlayıp ileteceğim" demişti. Bu teslim, 23 Temmuz'da açılan
  **"demo verisi ile eğitim verisi farklı"** engelini kapatan adım oldu:
  eğitim ve demo artık aynı güncel sete dayanıyor.

## 27 Temmuz (Pazartesi) — Çalışma huddle'ı

- **Sesli huddle (27 dk):** Alperen, Ahmet, Havva, Zeynep katıldı; devamında
  36 yanıtlı thread üzerinden senkron sürdü. Model/metrik durumunun ve kalan
  frontend + deploy işlerinin gözden geçirildiği ara senkron.

## 28 Temmuz (Salı) — Frontend, bug düzeltmeleri, deploy altyapısı

**Gece:**
- **Havva (Dev):** Birkaç sayfada tasarım düzenlemesi yaptı ve çalışan
  arayüzün ekran görüntüsünü paylaştı (Operations Overview / terminal
  görünümü). "Nasıl buldunuz, ona göre diğerlerini de aynı stilde
  hazırlayacağım" — geri bildirim bekliyor, henüz push yok.
- **Alperen (PO):** Frontend üzerinde ertesi gün Havva ile **birlikte
  çalışma** kararı ("önyüzde beraber bakarız düzenleriz"). Ayrıca bir push
  attı: **bug düzenlemeleri** + **Redis agent ve Supabase ayağa kaldırıldı**
  ("çalışıyorlar"); ekstra kontroller sürüyor. → Deploy altyapısı (#15) için
  ilk somut adım.

**Öğle/öğleden sonra:**
- **Alperen (PO):** "Bahsettiğim şeyleri ekledim ve **bug testlerini yaptım,
  bir sorun gözükmüyor**. Frontend kısmını da güncelleyip ileteceğim."
- **Ahmet (SM):** Bootcamp finali için **video hazırlama rehberini** paylaştı
  (≤3 dk demo, yatay 16:9, net ses, YouTube **Unlisted**) ve örnek tanıtım
  videolarını iletti. → Demo videosu çekimi kalan iş olarak netleşti.

## 29 Temmuz – 2 Ağustos — Kapanış

İç takvime göre proje 29 Temmuz'da bitmiş, kalan günler kapanış için ayrılmış
durumda. Kalan işler: demo videosunun çekilip YouTube'a (Unlisted) yüklenmesi,
frontend tasarım düzenlemelerinin push'lanması ve deploy'un (#15)
tamamlanması. Bu kalemler teslim (2 Ağustos 23.59) öncesi kapatılacak.

---

| Engel | Çözüm |
|---|---|
| Headline sayı Sprint 2'de yapısal olarak geçersiz çıkmıştı | Dekuple hat devreye alındı, tüm metrikler yeniden üretildi |
| Django geçişinde 22 test kırılmıştı | Test paketi iki pakete taşındı; **161 test** çalışıyor (95 `aks_core` + 66 Django) |
| 22 Temmuz iç hedefi tam tutmadı | Kapsam 23 Temmuz'da netleşti; 29 Temmuz hedefi korundu |
| Demo verisi ile eğitim verisi farklı | Birleştirme Zeynep'in kapsamında; teslim öncesi tamamlanacak |
| Yayımlanmış rakamlar döngüsel veriden geliyor | Metrik güncel dekuple sayılarla değiştirildi (README Sprint 3 §5); arayüz canlı `/api/*`'ten besleniyor |

---

## Kanıt görüntüleri

**Huddle:**

- `huddle_sprint3.png` — 19 Temmuz gecesi yapılan Sprint Planning huddle'ı

**Slack (dokümantasyon ve duyurular):**

- `slack_01_ic_takvim.png` — Sprint Planning çıktısı: iç takvim (22/29 Temmuz) ve dört başlıklı kapsam
- `slack_02_yapilacaklar.png` — 23 Temmuz detaylı yapılacaklar listesi
- `slack_03_ana_hedef_gorev.png` — ana hedef ve görev dağılımı

**Slack (günlük koordinasyon — 25–28 Temmuz):**

- `slack_04_daily_koordinasyon.png` — 25 Temmuz güncel veri teslimi, 27 dk huddle ve Havva'nın tasarım paylaşımı
- `slack_05_frontend_bugfix_deploy.png` — frontend eşleşmesi, Alperen'in bug-fix push'u + Supabase/Redis ayağa kaldırma

**Ürün çıktıları (Sprint Board & Ürün Durumu):**

- `urun_arayuz_sprint3.png` — çalışan arayüz: Operations Overview (canlı model, LIVE ENGINE FEED, PIPELINE HUB)
- `urun_durumu_sprint3.png` — canlı metriklerden üretilen dört panel (model AUC, persona, ek onay, portföy kurtarma)
- `board_sprint3.png` — Sprint 3 board (story/task durumu)

**Instagram grup DM:**

- _Ekip tarafından eklenecek (opsiyonel): Instagram grup DM ekran görüntüsü — Slack kanıtları yukarıda mevcut._
