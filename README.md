# mm_trading — Kantitatif Strateji Araştırması

Bu repo iki ayrı kantitatif çerçeve içerir:

1. **TSMR-CX** — sistematik ABD hisse/ETF/opsiyon stratejisinin tasarım
   memorandumu + karşılaştırmalı backtest iskeleti.
2. **XMM-CX** — kripto (MEXC, 500 USDT) **piyasa yapıcılığı (market making)**
   sistem spesifikasyonu + çalışan referans kotasyon motoru ve simülatör.

## İçerik

| Dosya | Açıklama |
|---|---|
| `STRATEGY_MEMORANDUM.md` | Goldman tarzı tam strateji memorandumu (tez, evren, sinyal, giriş/çıkış, boyutlandırma, risk, backtest, benchmark, edge-decay, 100x matematiği) |
| `MARKET_MAKING_SPEC.md` | **Jane Street tarzı piyasa yapıcılığı spesifikasyonu** (spread modeli, envanter yönetimi, kotasyon skew, ters-seçim tespiti, hedge, mikro yapı, PnL ayrıştırması, risk limitleri, metrikler) — MEXC kripto, 500 USDT |
| `mm/` | **Çalışan MM referans motoru** — Avellaneda-Stoikov kotasyon + ters-seçim kapısı + risk/kill-switch + PnL ayrıştırması + tick-seviyesi simülatör |
| `backtest/` | Çalışan backtest çerçevesi — guru-klon vs. çekirdek kantit vs. benchmark |
| `requirements.txt` | Python bağımlılıkları |

## Piyasa Yapıcılığı (XMM-CX) — MEXC, 500 USDT

Tam tasarım için `MARKET_MAKING_SPEC.md`. Çalışan iskelet `mm/` altında ve
**yalnızca standart kütüphane** ile çalışır (numpy gerekmez):

```bash
python -m mm.run_sim                 # üç rejimi karşılaştır
python -m mm.run_sim --steps 50000 --fee 0.0005   # pozitif komisyon senaryosu
```

Simülatör üç rejimi gösterir ve metodolojiyi doğrular:

| Rejim | Senaryo | Tipik sonuç |
|---|---|---|
| **A** | Düşük toksisite | Spread yakalama domine eder → **net pozitif** |
| **B** | Yüksek toksisite | Brüt spread sağlıklı ama **envanter/yönlü maliyet** net'i negatife çeker (ters seçim) |
| **C** | Sürekli tek-yönlü toksik patlama | **Ters-seçim kapısı (WIDEN)** devreye girer, fill çöker, zarar sınırlanır |

**Sentetik veri uyarısı:** Bilgili (informed) akış simülatöre *tasarımla*
gömülüdür; sonuçlar yalnızca motorun ve risk mantığının doğru çalıştığını
gösterir, canlı kârı **kanıtlamaz**. Gerçek hüküm için MEXC tarihsel L2/trade
replay'i gerekir. **MEXC %0 spot maker komisyonu koda gömülmez** — fiili
komisyon her döngüde API'den okunmalıdır (`--fee` ile pozitif senaryo test edin).

## Backtest: "Guru-klon botu mu, kendi stratejimiz mi?"

Bu iskelet, somut soruyu **veriyle** yanıtlar: InvestingPro tarzı bir guru/13F
portföy klonlama botu mu yoksa kendi sistematik stratejimiz mi daha iyi?

Karşılaştırılan stratejiler:
1. **SPY (benchmark)** — al-tut, piyasa
2. **MTUM** — pasif momentum faktörü
3. **Guru-klon** — 13F-tarzı, çeyreklik rebal + **~45 gün uygulama gecikmesi**
4. **Çekirdek Kantit (TSMR-CX)** — kesitsel momentum + reversal, rejim-koşullu,
   vol-hedefli (memo §3/§6/§7)

### Çalıştırma

```bash
pip install -r requirements.txt

# Offline (sentetik veri — boru hattını doğrular, hemen çalışır):
python -m backtest.run_comparison

# Gerçek veri (kendi makinenizde, ağ erişimiyle):
python -m backtest.run_comparison --source yfinance --start 2015-01-01

# Kendi CSV verinizle (data/<TICKER>.csv, sütunlar: Date,Close):
python -m backtest.run_comparison --source csv
```

Çıktılar: konsol performans tablosu + `backtest/results/equity_curves.png`
+ `backtest/results/summary.csv` + abonelik-gideri analizi.

### Sentetik veri uyarısı (ÖNEMLİ)

Bu sandbox'ta finansal veri sağlayıcıları (Yahoo/Stooq) ağ allowlist'inde
olmadığından, varsayılan mod **sentetik veridir**. Sentetik üreteç, belgelenen
momentum ve kısa-vadeli reversal etkilerini *tasarımla* gömer; dolayısıyla
sonuçlar yalnızca **metodolojinin doğru çalıştığını** gösterir, bir stratejinin
gerçekte para kazandığını **kanıtlamaz**. Gerçek hüküm için `--source yfinance`
veya `--source csv` ile gerçek veri kullanın.

### Sentetik veride tipik bulgu (metodoloji gösterimi)

| Strateji | Sharpe (tipik) | Yorum |
|---|---|---|
| SPY | ~0.40 | Piyasa tabanı |
| MTUM | ~0.35–0.65 | Faktör; değişken |
| **Guru-klon (13F +45g)** | **~0.30–0.47** | **Gecikme edge'i piyasa seviyesine eritir** |
| **Çekirdek Kantit** | **~0.58–1.03** | Çok-sinyalli + vol-hedefleme risk-ayarlı üstünlük |

**Çıkarım:** Guru-klon, 45 günlük 13F gecikmesi yüzünden çoğu zaman ancak
piyasa seviyesinde performans verir (literatürle uyumlu). Sistematik bir
stratejinin daha yüksek tavanı vardır — ama emek, doğrulama ve disiplin ister.
Ayrıca 1.000$ hesapta sabit abonelik ücreti (~250$/yıl = %25 gider) getiriyi
ezer. Detaylı tartışma için `STRATEGY_MEMORANDUM.md` §11.

> **YASAL UYARI:** Eğitim/araştırma amaçlıdır; yatırım tavsiyesi değildir.
> Geçmiş/simüle performans gelecek getiriyi garanti etmez.
