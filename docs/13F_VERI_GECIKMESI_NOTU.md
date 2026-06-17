# NOT: 13F Veri Gecikmesi ve Guru-Klon Stratejisine Etkisi

**Belge türü:** Araştırma notu (memo §1.1, §2.1, §8.1 ile bağlantılı)
**Tarih:** 2026-06-17
**İlgili kod:** `backtest/strategies.py::guru_clone`

> Özet: 13F **çeyreklik** bir rapordur ama veriyi gerçek zamanlı vermez.
> Çeyrek sonundaki bir *anlık fotoğrafı*, çeyrek bitiminden **45 takvim günü
> sonrasına kadar** açıklar. Bu iki gecikme birleşince, gördüğünüz pozisyon
> **90 gün (ortalama) – 135 gün (en kötü)** bayatlamış olabilir. Guru-klon
> stratejisinin edge'ini piyasa seviyesine eriten yapısal sebep budur.

---

## 1. Açıklama takvimi (çeyreklik)

Form 13F, **13(f) menkul kıymetlerinde > 100 milyon $** yöneten kurumsal
yatırım yöneticileri için zorunludur. Her takvim çeyreği için, çeyrek
bitiminden **en geç 45 takvim günü içinde** dosyalanır.

| Çeyrek | Çeyrek sonu (snapshot tarihi) | Son dosyalama tarihi (≈ +45 gün) |
|---|---|---|
| Q1 | 31 Mart | ~15 Mayıs |
| Q2 | 30 Haziran | ~14 Ağustos |
| Q3 | 30 Eylül | ~14 Kasım |
| Q4 | 31 Aralık | ~14 Şubat |

Pratikte birçok kurum **son güne kadar** bekleyip 45. günde dosyalar
(stratejilerini gizlemek için). Yani çoğu zaman gecikmenin tamamı yaşanır.

---

## 2. İki ayrı gecikme katmanı

Toplam bilgi bayatlığı **tek** değil, **iki** kaynaktan gelir:

1. **Snapshot gecikmesi (0–90 gün):** 13F yalnızca çeyrek *sonundaki*
   pozisyonu gösterir; çeyrek *boyunca* yapılan alım-satımları göstermez.
   Guru bir hisseyi 5 Ocak'ta alıp 20 Mart'ta sattıysa, Q1 snapshot'ında
   (31 Mart) o pozisyon **hiç görünmez**. Tersine, 31 Mart'ta tuttuğu bir
   pozisyon aslında 5 Ocak'tan beri olabilir → fikir zaten ~85 günlük.

2. **Dosyalama gecikmesi (0–45 gün):** Snapshot tarihinden, kamuya açıklanma
   tarihine kadar geçen süre.

### Efektif bayatlık matematiği

Bir pozisyonun, siz onu *görüp uyguladığınızda* ne kadar eski olduğu:

$$
\text{Bayatlık} = \underbrace{(t_{snapshot} - t_{pozisyon\_açılış})}_{0..\,90\text{ gün}}
\;+\; \underbrace{(t_{dosyalama} - t_{snapshot})}_{0..\,45\text{ gün}}
$$

- **En iyi durum:** pozisyon çeyrek sonunda açıldı + kurum erken dosyaladı → birkaç gün.
- **Ortalama:** çeyrek ortasında açılış (~45 gün) + tam dosyalama (45 gün) ≈ **~90 gün**.
- **En kötü durum:** pozisyon çeyrek başında açıldı (~90 gün) + tam dosyalama (45 gün) ≈ **~135 gün (~4.5 ay)**.

---

## 3. Ek gecikme/eksiklik kaynakları

| Mekanizma | Etki |
|---|---|
| **Gizli muamele talebi (confidential treatment)** | Kurum, hassas pozisyonlar için açıklamayı *aylarca* erteleyebilir; sonradan 13F-HR/A ile gelir |
| **Düzeltme (13F-HR/A)** | İlk dosyalama hatalıysa sonradan güncellenir; ilk gördüğünüz yanlış olabilir |
| **Sadece long ABD hissesi** | Short, opsiyon (çoğu), nakit, yurtdışı pozisyonlar **görünmez** → riskten korunmayı göremezsiniz |
| **Net pozisyon, işlem değil** | Giriş/çıkış fiyatını, zamanlamayı, kademeleri bilemezsiniz |

---

## 4. Guru-klon stratejisine sonuç

Bu gecikme, guru-klonun neden çoğu zaman **piyasa seviyesinde** performans
verdiğinin (bizim backtest bulgumuz: Sharpe guru ≈ SPY) yapısal açıklamasıdır:

- Gurunun gerçek edge'i çoğunlukla **giriş zamanlamasında** ve gizli
  (short/opsiyon) bacaklarındadır — ikisi de 13F'te yok.
- Siz pozisyonu 90–135 gün geç gördüğünüzde, kısa/orta vadeli alfanın büyük
  kısmı çoktan fiyatlanmıştır. Geriye büyük ölçüde **beta (piyasa maruziyeti)** kalır.
- Bu yüzden guru-klon, "bedava alfa" değil, gecikmeyle filtrelenmiş bir
  **beta + zayıf kalıntı alfa** ürünüdür.

### Kodda nasıl modellendi
`guru_clone()` fonksiyonu bu gecikmeyi `lag_days=31` (işlem günü) ile modeller;
bu ≈ 45 takvim gününe denk gelir (snapshot→dosyalama bacağı). Snapshot
gecikmesinin kendisi ise çeyreklik rebalance + çeyrek-sonu sinyali kullanımıyla
zaten içerilir. Daha muhafazakâr test için `lag_days` artırılabilir
(örn. tam ~135 gün bayatlığı yansıtmak için ~90 işlem günü).

---

## 5. Pratik azaltma yolları (gecikmeyle başa çıkma)

| Yaklaşım | Mantık |
|---|---|
| **Form 4'e geç (insider)** | İçeriden işlemler ~2 iş günü içinde bildirilir → çok daha taze sinyal |
| **13D/13G aktivist** | Olay-bazlı; açıklama daha hızlı (10 gün içinde) ve fiyat tepkisi büyük |
| **Yüksek-konvansiyon, düşük-turnover gurulara odaklan** | Buffett gibi pozisyonu *yıllarca* tutanlarda 90 günlük gecikme görece önemsizdir; gecikme yalnızca hızlı dönen pozisyonlarda öldürücüdür |
| **13F'i alfa değil, evren filtresi olarak kullan** | "Akıllı para nerede?" diye evren daraltıp asıl zamanlamayı kendi sinyallerinizle (memo §3) yapın |

---

## 6. Kaynak doğrulama

Bu nottaki takvim ve eşikler SEC Form 13F kurallarına dayanır. Birincil
kaynaktan (SEC) teyit için (bu sandbox'ta egress allowlist engelli; kendi
makinenizde erişilebilir):
- `https://www.sec.gov/files/form13f.pdf` (resmi form/talimat)
- `https://www.sec.gov/divisions/investment/13ffaq` (13F SSS)
- Dosyalama erişimi: `https://data.sec.gov/submissions/CIK##########.json`
