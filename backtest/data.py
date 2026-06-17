"""
Veri katmanı — kaynaktan bağımsız fiyat yükleyici.

Öncelik sırası (source='auto'):
  1. CSV         : data/<TICKER>.csv  (sütunlar: Date, Close)  — kendi verinizi koyun
  2. yfinance    : ağ erişimi varsa Yahoo'dan indirir (kendi makinenizde çalışır)
  3. synthetic   : kalibre edilmiş sentetik üreteç (sandbox / offline doğrulama)

ÖNEMLİ: Sentetik mod yalnızca BORU HATTINI doğrulamak içindir. Belgelenmiş
momentum (yavaş trend) ve kısa-vadeli reversal etkilerini *gömer*, ama bu
gömülü etkiler tasarımla oraya konmuştur — dolayısıyla sentetik sonuçlar bir
stratejinin gerçekte çalıştığını KANITLAMAZ. Gerçek hüküm için gerçek veri
(CSV veya yfinance) kullanın.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# --------------------------------------------------------------------------- #
# 1) CSV yükleyici
# --------------------------------------------------------------------------- #
def _load_csv(tickers, start, end):
    frames = {}
    for t in tickers:
        path = os.path.join(DATA_DIR, f"{t}.csv")
        if not os.path.exists(path):
            return None  # eksik dosya -> CSV modu kullanılamaz
        df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
        col = "Close" if "Close" in df.columns else df.columns[0]
        frames[t] = df[col]
    prices = pd.DataFrame(frames).sort_index()
    return prices.loc[str(start):str(end)].dropna(how="all")


# --------------------------------------------------------------------------- #
# 2) yfinance yükleyici
# --------------------------------------------------------------------------- #
def _load_yfinance(tickers, start, end):
    try:
        import yfinance as yf
    except ImportError:
        return None
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    if df is None or len(df) == 0:
        return None
    close = df["Close"] if "Close" in df.columns.get_level_values(0) else df
    close = close.dropna(how="all")
    return None if close.empty else close


# --------------------------------------------------------------------------- #
# 3) Sentetik üreteç (kalibre)
# --------------------------------------------------------------------------- #
def _synthetic(tickers, start, end, seed=7):
    """
    İKİ AYRI, ORTOGONAL etki gömülür (memo §1 tezini yansıtacak şekilde):

      mkt[t]  = mu_m/252 + (sig_m/sqrt(252)) * z_m              (piyasa faktörü)

      # (a) YAVAŞ trend  -> orta-vadeli MOMENTUM (12-1 ufkunda öngörücü)
      g[t]    = rho_s * g[t-1] + es                              (rho_s~0.97)

      # (b) HIZLI sapma -> kısa-vadeli ORTALAMAYA DÖNÜŞ (5g ufkunda öngörücü)
      x[t]    = rho_f * x[t-1] + ef                              (rho_f~0.6, hızlı söner)
      dx[t]   = x[t] - x[t-1]   (getiri katkısı; yükselen sapma sonra geri döner)

      r_i[t]  = beta_i*mkt[t] + g[t] + dx[t] + u[t]

    Böylece momentum ve reversal AYRI horizonlarda yaşar; biri diğerini ezmez.
    'SPY' saf piyasa faktörüdür (temiz benchmark).
    ÖNEMLİ: etkiler tasarımla gömülüdür -> sonuçlar metodolojiyi gösterir,
    bir stratejinin gerçekte çalıştığını KANITLAMAZ.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    assets = [t for t in tickers if t != "SPY"]

    mu_m, sig_m = 0.085, 0.16
    z_m = rng.standard_normal(n)
    z_m -= z_m.mean()                       # drift'i küçük örneklemde koru
    mkt = mu_m / 252 + (sig_m / np.sqrt(252)) * z_m

    out = {}
    if "SPY" in tickers:
        out["SPY"] = mkt.copy()

    rho_s, sig_g = 0.97, 0.00045            # yavaş trend (momentum)
    rho_f, sig_x = 0.60, 0.011              # hızlı sapma (reversal)
    sig_u = 0.008                           # idiyosenkratik gürültü
    for t in assets:
        beta = rng.uniform(0.7, 1.4)

        g = np.zeros(n)
        es = rng.standard_normal(n) * sig_g
        for k in range(1, n):
            g[k] = rho_s * g[k - 1] + es[k]
        g -= g.mean()                       # seviye merkezle; persistans (momentum) korunur

        x = np.zeros(n)
        ef = rng.standard_normal(n) * sig_x
        for k in range(1, n):
            x[k] = rho_f * x[k - 1] + ef[k]
        dx = np.diff(x, prepend=0.0)        # mean-reverting getiri katkısı

        u = rng.standard_normal(n) * sig_u
        u -= u.mean()

        r = beta * mkt + g + dx + u
        out[t] = r

    rets = pd.DataFrame(out, index=dates)
    prices = 100.0 * (1.0 + rets).cumprod()
    return prices


# --------------------------------------------------------------------------- #
# Genel arayüz
# --------------------------------------------------------------------------- #
def load_prices(tickers, start="2015-01-01", end="2024-12-31", source="auto", seed=7):
    """Fiyat DataFrame'i döndürür (index=tarih, sütun=ticker). Kaynağı da yazar."""
    tickers = list(tickers)
    if source in ("auto", "csv"):
        p = _load_csv(tickers, start, end)
        if p is not None and not p.empty:
            print(f"[data] kaynak = CSV  ({p.shape[0]} gün, {p.shape[1]} enstrüman)")
            return p, "csv"
        if source == "csv":
            raise FileNotFoundError("CSV verisi data/ altında bulunamadı.")

    if source in ("auto", "yfinance"):
        p = _load_yfinance(tickers, start, end)
        if p is not None and not p.empty:
            print(f"[data] kaynak = yfinance  ({p.shape[0]} gün, {p.shape[1]} enstrüman)")
            return p, "yfinance"
        if source == "yfinance":
            raise ConnectionError("yfinance verisi indirilemedi (ağ/allowlist).")

    p = _synthetic(tickers, start, end, seed=seed)
    print(f"[data] kaynak = SENTETIK  ({p.shape[0]} gün, {p.shape[1]} enstrüman)")
    print("[data] UYARI: sentetik veri yalnızca boru hattı doğrulaması içindir; "
          "gerçek hüküm için CSV/yfinance kullanın.")
    return p, "synthetic"
