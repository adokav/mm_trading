# mm_trading — Kantitatif Strateji Araştırması

Bu repo, sistematik bir ABD hisse/ETF/opsiyon işlem stratejisinin (TSMR-CX)
tasarım memorandumunu ve bir **karşılaştırmalı backtest iskeletini** içerir.

## İçerik

| Dosya | Açıklama |
|---|---|
| `STRATEGY_MEMORANDUM.md` | Goldman tarzı tam strateji memorandumu (tez, evren, sinyal, giriş/çıkış, boyutlandırma, risk, backtest, benchmark, edge-decay, 100x matematiği) |
| `backtest/` | Çalışan backtest çerçevesi — guru-klon vs. çekirdek kantit vs. benchmark |
| `requirements.txt` | Python bağımlılıkları |

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
