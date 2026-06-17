"""Giriş noktası: iki rejimi karşılaştır — düşük toksisite vs. yüksek toksisite.

    python -m mm.run_sim

Düşük informed_frac: spread yakalama domine eder, net pozitif beklenir.
Yüksek informed_frac: ters seçim + kapı/kill-switch devreye girer; motor
agresif kotasyonu kısar (WIDEN/HALT) ve riski sınırlar.
"""
from __future__ import annotations
import argparse

from .engine import QuoteParams
from .simulator import SimConfig, run_simulation


def main():
    ap = argparse.ArgumentParser(description="XMM-CX market making simülasyonu")
    ap.add_argument("--steps", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--fee", type=float, default=0.0,
                    help="tek-yön maker komisyonu (MEXC spot ~0)")
    args = ap.parse_args()

    params = QuoteParams(tick=0.01, size0=0.1, fee_rate=args.fee)

    print("\n### REJİM A — DÜŞÜK TOKSİSİTE (informed_frac=0.05) ###")
    run_simulation(SimConfig(steps=args.steps, seed=args.seed,
                             informed_frac=0.05), params)

    print("\n### REJİM B — YÜKSEK TOKSİSİTE (informed_frac=0.45) ###")
    run_simulation(SimConfig(steps=args.steps, seed=args.seed,
                             informed_frac=0.45), params)

    print("\n### REJİM C — SÜREKLİ TEK-YÖNLÜ TOKSİK PATLAMA (gate testi) ###")
    run_simulation(SimConfig(steps=args.steps, seed=args.seed,
                             informed_frac=0.60, informed_edge=8.0,
                             p_switch=0.0004), params)

    print("\nGözlem:")
    print("  A) Benign akış: spread yakalama domine eder -> net pozitif.")
    print("  B) Toksik akış: brüt spread sağlıklı görünse de yönlü/envanter")
    print("     maliyeti net'i negatife çevirir (ters seçim envanterden ısırır).")
    print("  C) Sürekli toksik: ters-seçim kapısı WIDEN ile devreye girer,")
    print("     fill sayısı çöker (motor toksik akıştan geri çekilir), zarar")
    print("     sınırlanır. Kill-switch envanteri/zararı bantta tutar.")
    print("\nNot: Sentetik veri — metodoloji gösterimi; canlı kâr kanıtı DEĞİL.")
    print("Gerçek hüküm için MEXC tarihsel L2/trade replay'i gerekir.\n")


if __name__ == "__main__":
    main()
