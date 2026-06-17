"""
Strateji tanımları. Her strateji günlük HEDEF AĞIRLIK matrisi döndürür
(index=tarih, sütun=enstrüman). Ağırlık toplamı kaldıracı verir.
Long-only varsayılır (1.000$ nakit hesap gerçeği; short yok).

Stratejiler:
  - spy_buy_hold      : %100 SPY (birincil benchmark, memo §9)
  - mtum_momentum     : pasif momentum faktörü (top yarı, 12-1, aylık) — MTUM proxy
  - guru_clone        : 13F-tarzı klon, ÇEYREKLİK rebal + ~45 gün uygulama GECİKMESİ
  - core_quant        : memo §3/§6 — kesitsel momentum + reversal, rejim-koşullu,
                        vol-hedefli, haftalık rebal
"""
from __future__ import annotations
import numpy as np
import pandas as pd

TRADING_DAYS = 252


# --------------------------------------------------------------------------- #
# Yardımcı sinyal fonksiyonları (memo §3)
# --------------------------------------------------------------------------- #
def _returns(prices):
    return prices.pct_change()


def riskadj_momentum(prices, lookback=252, skip=21, vol_win=63):
    """12-1 momentum / 63g volatilite (memo §3.1)."""
    mom = prices.shift(skip) / prices.shift(lookback) - 1.0
    vol = _returns(prices).rolling(vol_win).std() * np.sqrt(TRADING_DAYS)
    return mom / vol.replace(0, np.nan)


def short_term_reversal(prices, win=5):
    """-(5g getiri); kesitsel olarak z-skorlanır (memo §3.2, basitleştirilmiş)."""
    r = prices / prices.shift(win) - 1.0
    return -r


def cross_sectional_z(df, clip=3.0):
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=0).replace(0, np.nan)
    z = df.sub(mu, axis=0).div(sd, axis=0)
    return z.clip(-clip, clip)


def regime_risk_on(spy_prices, win=200):
    """SPY > 200g SMA -> Risk-On (memo §3.3)."""
    sma = spy_prices.rolling(win).mean()
    return spy_prices > sma


def _rebal_table_to_daily(rebal_weights: dict, full_index, columns):
    """
    {rebal_tarihi: agirlik_serisi} sözlüğünü günlük ağırlık matrisine çevirir.
    Her rebal satırı TAM tahsis içerir (seçilmeyenler 0). Rebal günleri arası
    ffill ile taşınır. Bu, 'eski pozisyonlar sıfırlanmıyor' hatasını önler.
    """
    if not rebal_weights:
        return pd.DataFrame(0.0, index=full_index, columns=columns)
    tbl = pd.DataFrame(rebal_weights).T.reindex(columns=columns).fillna(0.0)
    tbl = tbl.sort_index()
    return tbl.reindex(full_index).ffill().fillna(0.0)


# --------------------------------------------------------------------------- #
# Strateji 1: SPY al-tut
# --------------------------------------------------------------------------- #
def spy_buy_hold(prices):
    w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    if "SPY" in w.columns:
        w["SPY"] = 1.0
    return w


# --------------------------------------------------------------------------- #
# Strateji 2: Pasif momentum faktörü (MTUM proxy)
# --------------------------------------------------------------------------- #
def mtum_momentum(prices, rebal="ME", top_frac=0.5):
    assets = [c for c in prices.columns if c != "SPY"]
    px = prices[assets]
    mom = riskadj_momentum(px)
    rebal_dates = px.resample(rebal).last().index
    rebal_w = {}
    for d in rebal_dates:
        valid = mom.index[mom.index <= d]
        if len(valid) == 0:
            continue
        day = valid[-1]
        row = mom.loc[day].dropna()
        if len(row) < 3:
            continue
        k = max(1, int(len(row) * top_frac))
        picks = row.nlargest(k).index
        rebal_w[day] = pd.Series(1.0 / k, index=picks)
    return _rebal_table_to_daily(rebal_w, prices.index, prices.columns)


# --------------------------------------------------------------------------- #
# Strateji 3: Guru-klon (13F gecikmesiyle)
# --------------------------------------------------------------------------- #
def guru_clone(prices, lag_days=31, top_k=5):
    """
    13F gerçeği: 'guru' çeyrek sonunda en iyi (burada: en yüksek momentumlu)
    isimleri tutar, AMA siz bunu ~45 takvim günü (≈31 işlem günü) GECİKMEYLE
    görüp uygularsınız. Bu gecikme, klonun yapısal sürtünmesini modeller.
    Eşit ağırlık, çeyreklik yeniden dengeleme.
    """
    assets = [c for c in prices.columns if c != "SPY"]
    px = prices[assets]
    mom = riskadj_momentum(px)
    q_ends = px.resample("QE").last().index
    idx = px.index
    rebal_w = {}
    for qd in q_ends:
        avail = idx[idx <= qd]
        if len(avail) == 0:
            continue
        signal_day = avail[-1]                       # gurunun bildiği an (çeyrek sonu)
        row = mom.loc[signal_day].dropna()
        if len(row) < 1:
            continue
        picks = row.nlargest(min(top_k, len(row))).index
        # Uygulama gecikmesi: sinyal gününden lag_days işlem günü SONRA pozisyon al
        loc = idx.get_loc(signal_day)
        apply_loc = min(loc + lag_days, len(idx) - 1)
        apply_day = idx[apply_loc]
        rebal_w[apply_day] = pd.Series(1.0 / len(picks), index=picks)
    return _rebal_table_to_daily(rebal_w, prices.index, prices.columns)


# --------------------------------------------------------------------------- #
# Strateji 4: Çekirdek kantit (memo §3 + §6)
# --------------------------------------------------------------------------- #
def _cap_weights(w: pd.Series, max_single=0.20, iters=8):
    """Tek-pozisyon tavanı (memo §7): >max_single kırp, kalanı yeniden dağıt."""
    w = w.copy()
    for _ in range(iters):
        over = w > max_single
        if not over.any():
            break
        excess = (w[over] - max_single).sum()
        w[over] = max_single
        room = ~over & (w > 0)
        if not room.any():
            break
        w[room] += excess * (w[room] / w[room].sum())
    return w.clip(upper=max_single)


def core_quant(prices, rebal="W-FRI", target_vol=0.15, max_leverage=1.5,
               top_frac=0.4, vol_win=63, max_single=0.20):
    """
    Birleşik alfa (rejim-koşullu momentum+reversal) -> long-only top dilim,
    inanç-ağırlıklı, sonra portföy vol-hedefleme (memo §6.1).
    """
    assets = [c for c in prices.columns if c != "SPY"]
    px = prices[assets]
    rets = _returns(px)

    z_mom = cross_sectional_z(riskadj_momentum(px))
    z_rev = cross_sectional_z(short_term_reversal(px))

    if "SPY" in prices.columns:
        risk_on = regime_risk_on(prices["SPY"])
    else:
        risk_on = pd.Series(True, index=prices.index)

    w_mom = risk_on.map({True: 0.70, False: 0.30})
    w_rev = risk_on.map({True: 0.30, False: 0.70})
    alpha = z_mom.mul(w_mom, axis=0) + z_rev.mul(w_rev, axis=0)

    inst_vol = rets.rolling(vol_win).std() * np.sqrt(TRADING_DAYS)

    rebal_dates = px.resample(rebal).last().index
    rebal_w = {}
    for d in rebal_dates:
        valid = alpha.index[alpha.index <= d]
        if len(valid) == 0:
            continue
        day = valid[-1]
        a = alpha.loc[day].dropna()
        a = a[a > 0]  # long-only: yalnızca pozitif alfa
        if len(a) < 2:
            continue
        k = max(1, int(len(a) * top_frac))
        picks = a.nlargest(k)
        conv = picks / picks.sum()                       # inanç payı
        iv = inst_vol.loc[day, picks.index].replace(0, np.nan)
        rp = (1.0 / iv) / (1.0 / iv).sum()               # risk-parite
        wt = (conv * rp)
        wt = wt / wt.sum()
        wt = _cap_weights(wt, max_single=max_single)   # memo §7 tek-pozisyon tavanı
        rebal_w[day] = wt

    raw = _rebal_table_to_daily(rebal_w, prices.index, prices.columns)

    # Portföy vol-hedefleme (memo §6.1): L = target/realized, tavan max_leverage
    port_ret_unscaled = (raw.shift(1) * rets.reindex(raw.index).fillna(0.0)
                         .reindex(columns=raw.columns).fillna(0.0)).sum(axis=1)
    realized = port_ret_unscaled.rolling(vol_win).std() * np.sqrt(TRADING_DAYS)
    lev = (target_vol / realized.replace(0, np.nan)).clip(upper=max_leverage).fillna(1.0)
    lev = lev.ewm(span=10).mean()
    # Kaldıracı rebal frekansında sabitle -> günlük kaldıraç oynamasından gelen
    # yapay turnover'ı önle (1.000$ hesapta komisyon kritik).
    lev = lev.resample(rebal).last().reindex(prices.index, method="ffill").fillna(1.0)
    return raw.mul(lev, axis=0)
