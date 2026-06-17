"""
Backtest motoru. Hedef ağırlık matrisini, işlem maliyeti düşülmüş günlük
portföy getirilerine çevirir.

Maliyet modeli (memo §8.2, basitleştirilmiş): turnover * (yarı-spread + komisyon_bps).
Sinyal t gününde, icra t+1'de (look-ahead bias yok, memo §8.1).
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def run_backtest(prices, weights, cost_bps=5.0, slippage_bps=2.0):
    """
    prices  : fiyat DataFrame
    weights : hedef ağırlık DataFrame (aynı sütunlar)
    cost_bps: tek yön işlem maliyeti (komisyon+yarı-spread), baz puan
    Döner: günlük net getiri Series.
    """
    rets = prices.pct_change().reindex(columns=weights.columns).fillna(0.0)

    # t günü ağırlığı t+1 getirisine uygulanır
    w_lag = weights.shift(1).fillna(0.0)
    gross = (w_lag * rets).sum(axis=1)

    # Turnover = |w_t - w_{t-1}| toplamı; maliyet = turnover * bps
    turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
    cost = turnover * ((cost_bps + slippage_bps) / 1e4)

    net = gross - cost
    net.name = "net_return"
    return net


def turnover_stats(weights):
    daily_to = weights.diff().abs().sum(axis=1).fillna(0.0)
    return {
        "ann_turnover": daily_to.mean() * 252,
        "avg_gross_leverage": weights.abs().sum(axis=1).mean(),
    }
