# Sprint 2 — Daily Scrum & Ekip Koordinasyon Notları

**Sprint aralığı:** 6 Temmuz – 19 Temmuz 2026
**Kanallar:** Slack (`#bootcamp-2026` + ekip kanalı), Instagram grup mesajlaşması
ve sesli huddle. Toplantılar zaman kısıtı nedeniyle çoğunlukla asenkron ve yazılı
yürütüldü; günlük hızlı koordinasyon Instagram grup DM'i üzerinden, dokümantasyon
ve resmi duyurular Slack üzerinden ilerledi.

> Not: Aşağıdaki kayıtlar ekibin Slack yazışmalarından, Instagram grup
> mesajlarından ve huddle'lardan derlenmiştir. İlgili ekran görüntüleri bu klasörde.

---

## 8–9 Temmuz — Alan bölüşümü ve mimari yön

Sprint 1'de tek bir kod paketi üzerinden ilerlenmişti. Sprint 2'de iş
paralelleşince proje beş alana bölündü ve sahipleri belirlendi.

- **Alperen (PO):** Projeyi beş alana ayırdı — Yapay Zeka, Veri, Frontend,
  Backend, Business Plan. Backend'i üstlendi. Frontend için toplantıda konuşulan
  React + Django uyumlu bir taslağı Google Stitch üzerinden çıkarmaya başladı.
- **Zeynep (Dev):** Persona tasarımını üstlendi; veri üretimi netleştiğinde
  persona tanımlarını oluşturacağını belirtti ("sen bitirdiğinde ben sana
  kişilikler oluşturacaktım").
- **Alperen (PO):** Kendi tarafındaki veri araştırmasını sürdürdü; task bazlı
  bölme çalışmasının devam ettiğini, bitince paylaşacağını bildirdi.
- **Engel:** Repo'nun o anki hâli dağınıktı ("biraz karışık şu an"). → Sprint
  ortasında yeniden yapılandırmayla çözüldü, ancak bu yapılandırma ekip hizası
  alınmadan yapıldı (retrospektif maddesi).

**Nihai alan dağılımı:**

| Alan | Sahip |
|---|---|
| Veri | Zeynep |
| Yapay Zeka | Ahmet |
| Backend | Alperen |
| Frontend | Havva |

## 10–11 Temmuz — Model, mimari ve denetim izi

- **Ahmet (SM):** Denetimli model hattını kurdu — XGBoost/LightGBM eğitimi,
  klasik skora karşı baseline karşılaştırması, SHAP açıklama katmanı, adalet ve
  iş etkisi raporları.
- **Alperen (PO):** FastAPI'nin denetim izi (audit trail), ORM ve migration
  ihtiyacını karşılayamadığını tespit etti; Django + DRF'e geçiş kararı alındı ve
  uygulandı. 11 endpoint ile parite doğrulandı.
- **Havva (Dev):** React + Vite + TypeScript arayüzü, Stitch taslağı üzerinden
  beş sayfa olarak kuruldu ve gerçek `/api/*` uçlarına bağlandı.
- **Zeynep (Dev):** Persona tanımları ve veri sözlüğü tamamlandı.

## 11 Temmuz — Döngüsellik (circularity) bulgusu

Sprint'in dönüm noktası. Model 0.829 AUC ile klasik skorun 0.729'unu geçti, ama
sonuç fazla iyi göründü.

- **Ahmet (SM):** Ablasyon testi yazdı (`circularity_ablation.py`). Sonuç: modelin
  eğitildiği 9 özelliğin 4'ü, sentetik etiketin doğrudan üretildiği değişkenler.
  XGBoost ile lojistik regresyon arasındaki fark yalnızca 0.0004 AUC — yani
  "gelişmiş model" hiçbir şey katmıyor, kuralı yeniden inşa ediyor.
- **Karar:** Sayı saklanmayacak, çerçevelenecek. Yayımlanan tüm figürler bu
  uyarıyla birlikte sunulacak. Etiketi özelliklerden ayıran dekuple veri üretici
  (`uretici_kapasite.py`) yazıldı; eğitim hattına bağlanması Sprint 3'e alındı.
- **Engel:** Headline sayının geçersiz olması. → Gizlenmedi; sprintin teslimatı
  olarak raporlandı ve düzeltme yolu kuruldu.

## 11 Temmuz (akşam) — Sprint 2 dokümantasyonu

- **Ahmet (SM):** README'ye Sprint 2 bölümünü yazdı. Sprint 1 bloğuna dokunulmadı
  (puanlandı, dondurulmuş durumda). Klasör yapısı, mimari, API uçları ve backlog
  güncellendi.
- **Ahmet (SM):** Sprint kanıtları iki ayrı klasörde duruyordu; hepsi
  `sprints/docs/sprint<N>/` altında toplandı, kopyalar silindi.
- **Alperen (PO):** Değişiklikleri onayladı ("tamamdır eline sağlık").

## 11–12 Temmuz — Çalıştırılabilirlik bug'ları ve testler

Ürün ekran görüntüsü almak için arayüz ayağa kaldırılmaya çalışıldı; iki bug
çıktı. İkisi de "repoyu klonlayan kimse ürünü çalıştıramaz" sınıfındaydı.

- **Bug 1 — model taşınabilirliği:** Model `joblib`/pickle ile kaydediliyordu.
  Pickle, XGBoost'un ham C++ buffer'ını gömer; bu buffer platforma bağlıdır.
  Linux'ta eğitilen model Windows'ta `XGBoostError: input stream corrupted`
  veriyordu. → Model artık XGBoost'un kendi JSON formatında kaydediliyor
  (`aks_core/model/kayit.py`).
- **Bug 2 — bağımlılık pini:** `pyproject.toml` içindeki `numpy<2` pini, SHAP'i
  0.49'a düşürüyordu; o sürüm XGBoost 3.x'in `base_score` formatını okuyamıyordu.
  → Pin kaldırıldı, `shap>=0.52` istendi.
- **Ahmet (SM):** 27 test yazıldı (16 `aks_core` + 11 Django).
- **Bulgu:** Testler, denetim izinin (`AuditLog`) aslında **değiştirilebilir**
  olduğunu ortaya çıkardı. README "değiştirilemez denetim izi" diyordu ama modelde
  bunu engelleyen hiçbir şey yoktu — satır güncellenebiliyor ve silinebiliyordu.
  Ürünün en güçlü iddiası kodda karşılığı olmayan bir yorum satırıydı. → `save`
  ve `delete` engellendi; `AuditLog` artık gerçekten append-only.

Sprint 1 retrospektifinde alınan "unit test eforu artırılmalı" kararı bu sprintte
tutuldu ve testler ilk gün gerçek bir açık buldu.

---

## 13–19 Temmuz — Sprint'in kalan günleri

> Bu bölüm plandır, kayıt değil. Gerçekleşen daily scrum notları gün geçtikçe
> buraya eklenecektir.

Sprint 2'nin ana teslimatları (model, agent mimarisi, API, arayüz) tamamlandı.
Kalan günler kapanış ve düzeltme için ayrıldı:

- **Sprint kanıtlarının tamamlanması:** Miro'da Sprint 2 kolonunun açılması ve
  story'lerin Done'a çekilmesi (board screenshot'ı için), çalışan arayüzden ürün
  durumu ekran görüntüsünün alınması.
- **Hata düzeltme ve iyileştirme:** Sprint boyunca biriken küçük hataların
  giderilmesi, gerekirse kapsam dışı kalan ufak eklemelerin yapılması. Sprint'in
  ana teslimatları bittiği için bu günler yeni özellik değil, mevcut işin
  sağlamlaştırılması için kullanılacak.
- **Sprint 3 hazırlığı:** Dekuple etiketin eğitim/değerlendirme hattına bağlanması
  için ön çalışma, deploy (Docker + Render) araştırması, demo videosu planı.

---

| Engel | Çözüm |
|---|---|
| Repo yapısı dağınıktı, yollar karışıyordu | Yeniden yapılandırma + kanıt ağacının tek yerde toplanması |
| Yeniden yapılandırma ekip hizası alınmadan yapıldı | Retrospektif kararı: yapısal değişiklikler Daily Scrum'da duyurulmadan main'e girmeyecek |
| FastAPI denetim izi/migration ihtiyacını karşılayamadı | Django + DRF'e geçiş, parite doğrulandı |
| Headline sayı (0.829 AUC) yapısal olarak geçersiz çıktı | Ablasyonla belgelendi, dekuple üretici yazıldı, düzeltme Sprint 3'e alındı |
| Model Windows'ta açılmıyordu | Taşınabilir kayıt formatına geçildi |
| Bağımlılık pini SHAP'i çalışmaz sürüme düşürüyordu | Pin kaldırıldı |

---

## Kanıt görüntüleri

Bu klasördeki ilgili ekran görüntüleri:

**Instagram grup DM (günlük koordinasyon):**

- `dm_01_alan_bolusumu.png` — projenin beş alana bölünmesi, Backend ve Stitch taslağı sahiplenmeleri
- `dm_02_persona_veri.png` — persona tasarımı ve veri tarafının koordinasyonu
- `dm_03_repo_paylasimi.png` — GitHub repo paylaşımı ve o anki durumun değerlendirilmesi
- `dm_04_sprint2_duyuru.png` — Sprint 2 README duyurusu ve kalan işlerin paylaşılması
- `dm_04_sprint2_duyuru.png` — Sprint 2 README duyurusu ve kalan işlerin paylaşılması


**Slack (dokümantasyon ve duyurular):**

- `slack_01_gorev_dagilimi.png` — Sprint 2 durum duyurusu ve nihai alan dağılımı (Veri/Yapay Zeka/Backend/Frontend)
- `slack_02_sprint2_son.png` — Sprint 2 durum güncellemesi ve herkesin yaptığı görevleri bildirmesi

**Huddle:**

- `huddle_sprint2.png` — sprint içi sesli huddle
