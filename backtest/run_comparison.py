"""
ANA KIYAS: Guru-klon (13F gecikmeli) vs. Çekirdek kantit vs. Benchmark'lar.

Soruyu veriyle yanıtlar: "Guru portföylerini klonlayan bot mu yoksa kendi
sistematik stratejimiz mi hedefe daha hızlı götürür?" + abonelik gideri etkisi.

Çalıştırma:
    python -m backtest.run_comparison
    python -m backtest.run_comparison --source yfinance --start 2015-01-01
    python -m backtest.run_comparison --source csv

Sentetik mod varsayılandır (offline çalışır). Gerçek hüküm için CSV/yfinance.
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd

from . import data as datamod
from . import strategies as strat
from . import engine
from . import metrics


# Evren: SPY benchmark + büyük-kap hisse/ETF proxy seti (memo §2)
DEFAULT_UNIVERSE = [
    "SPY", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "JPM", "JNJ",
    "XOM", "PG", "KO", "HD", "UNH", "V", "MA", "BAC", "DIS", "CVX", "WMT",
]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def build_strategies(prices):
    return {
        "SPY (benchmark)": strat.spy_buy_hold(prices),
        "MTUM (momentum faktör)": strat.mtum_momentum(prices),
        "Guru-klon (13F +45g gecikme)": strat.guru_clone(prices),
        "Cekirdek Kantit (TSMR-CX)": strat.core_quant(prices),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="auto", choices=["auto", "csv", "yfinance", "synthetic"])
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--end", default="2024-12-31")
    ap.add_argument("--cost_bps", type=float, default=5.0)
    ap.add_argument("--rf", type=float, default=0.02, help="risksiz oran (yıllık)")
    ap.add_argument("--fee", type=float, default=250.0, help="yıllık abonelik ücreti ($)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    prices, src = datamod.load_prices(
        DEFAULT_UNIVERSE, start=args.start, end=args.end, source=args.source, seed=args.seed
    )

    weights = build_strategies(prices)
    results = {
        name: engine.run_backtest(prices, w, cost_bps=args.cost_bps)
        for name, w in weights.items()
    }

    # --- Performans tablosu (memo §8.6 / §9) ---
    table = metrics.summary_table(results, rf=args.rf)
    pct_cols = ["CAGR", "AnnVol", "MaxDD"]
    disp = table.copy()
    for c in pct_cols:
        disp[c] = (disp[c] * 100).round(2)
    disp[["Sharpe", "Sortino", "Calmar"]] = disp[["Sharpe", "Sortino", "Calmar"]].round(2)

    print("\n" + "=" * 74)
    print("PERFORMANS KIYASI  (kaynak = %s)" % src.upper())
    print("=" * 74)
    print(disp.to_string())

    # --- Turnover ---
    print("\nTurnover / kaldirac:")
    for name, w in weights.items():
        ts = engine.turnover_stats(w)
        print(f"  {name:32s} yillik_turnover={ts['ann_turnover']:.1f}x  "
              f"ort_kaldirac={ts['avg_gross_leverage']:.2f}")

    # --- Abonelik gideri analizi (1.000$ hesap gerçeği) ---
    core_cagr = metrics.cagr(results["Cekirdek Kantit (TSMR-CX)"])
    drag = metrics.subscription_drag(core_cagr, fee_per_year=args.fee)
    print("\n" + "=" * 74)
    print(f"ABONELIK GIDERI ETKISI  (yillik ucret = {args.fee:.0f}$, brut CAGR = cekirdek)")
    print("=" * 74)
    print(drag.round(2).to_string(index=False))
    print("\n-> 1.000$ hesapta sabit abonelik ucreti, getirinin buyuk kismini "
          "yok eder (memo Bolum: 'asil kaldirac katki+zaman').")

    # --- Equity curve grafiği ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(11, 6))
        for name, r in results.items():
            metrics.equity_curve(r, start_value=1000.0).plot(ax=ax, label=name, lw=1.6)
        ax.set_title(f"1.000$ baslangic — Strateji Kiyasi (kaynak: {src})")
        ax.set_ylabel("Portfoy degeri ($)")
        ax.set_yscale("log")
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, alpha=0.3)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        out = os.path.join(RESULTS_DIR, "equity_curves.png")
        fig.tight_layout()
        fig.savefig(out, dpi=130)
        print(f"\n[grafik] kaydedildi -> {out}")
    except Exception as e:
        print(f"\n[grafik] atlandi: {e}")

    # CSV çıktısı
    os.makedirs(RESULTS_DIR, exist_ok=True)
    table.to_csv(os.path.join(RESULTS_DIR, "summary.csv"))
    print(f"[tablo] kaydedildi -> {os.path.join(RESULTS_DIR, 'summary.csv')}")
    print("\nNOT: Sentetik veride sonuclar yalnizca metodolojiyi gosterir; "
          "gercek hukum icin --source yfinance veya --source csv kullanin.\n")


if __name__ == "__main__":
    main()
