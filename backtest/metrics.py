"""Performans metrikleri (memo §8.6 ile uyumlu) + 1.000$ hesap abonelik-gideri analizi."""
from __future__ import annotations
import numpy as np
import pandas as pd

TRADING_DAYS = 252


def equity_curve(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    return start_value * (1.0 + returns.fillna(0.0)).cumprod()


def cagr(returns: pd.Series) -> float:
    eq = equity_curve(returns)
    years = len(returns) / TRADING_DAYS
    if years <= 0 or eq.iloc[-1] <= 0:
        return float("nan")
    return eq.iloc[-1] ** (1 / years) - 1


def ann_vol(returns: pd.Series) -> float:
    return returns.std(ddof=0) * np.sqrt(TRADING_DAYS)


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / TRADING_DAYS
    sd = excess.std(ddof=0)
    return np.nan if sd == 0 else excess.mean() / sd * np.sqrt(TRADING_DAYS)


def sortino(returns: pd.Series, rf: float = 0.0) -> float:
    excess = returns - rf / TRADING_DAYS
    downside = excess[excess < 0]
    dd = downside.std(ddof=0)
    return np.nan if dd == 0 else excess.mean() / dd * np.sqrt(TRADING_DAYS)


def max_drawdown(returns: pd.Series) -> float:
    eq = equity_curve(returns)
    peak = eq.cummax()
    return (eq / peak - 1.0).min()


def calmar(returns: pd.Series) -> float:
    mdd = abs(max_drawdown(returns))
    return np.nan if mdd == 0 else cagr(returns) / mdd


def summary(returns: pd.Series, rf: float = 0.0) -> dict:
    return {
        "CAGR": cagr(returns),
        "AnnVol": ann_vol(returns),
        "Sharpe": sharpe(returns, rf),
        "Sortino": sortino(returns, rf),
        "MaxDD": max_drawdown(returns),
        "Calmar": calmar(returns),
    }


def summary_table(results: dict, rf: float = 0.0) -> pd.DataFrame:
    rows = {name: summary(r, rf) for name, r in results.items()}
    df = pd.DataFrame(rows).T
    return df[["CAGR", "AnnVol", "Sharpe", "Sortino", "MaxDD", "Calmar"]]


def subscription_drag(gross_cagr: float, fee_per_year: float, accounts=(1000, 5000, 25000)):
    """
    Sabit yıllık abonelik ücretinin (örn. InvestingPro ~250$) farklı hesap
    boyutlarında net CAGR'a etkisi. Net getiri ~ brüt - ücret/sermaye.
    Küçük hesapta sabit ücret yüzde olarak dev bir gider haline gelir.
    """
    rows = []
    for acct in accounts:
        fee_pct = fee_per_year / acct
        rows.append({
            "Hesap ($)": acct,
            "Yıllık ücret ($)": fee_per_year,
            "Ücret/Sermaye (%)": 100 * fee_pct,
            "Brüt CAGR (%)": 100 * gross_cagr,
            "Net CAGR (%)": 100 * (gross_cagr - fee_pct),
        })
    return pd.DataFrame(rows)
