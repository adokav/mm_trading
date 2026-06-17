"""Tick-seviyesi piyasa simülatörü (SPEC doğrulama iskeleti).

Sentetik bir mid süreci + gürültü/bilgili (informed) emir akışı üretir; motorun
kotasyonlarını AS arrival modeliyle (lambda(d)=A e^{-k d}) doldurur. Amaç:
spread yakalama vs. ters seçim dinamiğini ve PnL ayrıştırmasını GÖSTERMEK.

UYARI: Sentetik veridir. Bilgili akış 'tasarımla' gömülüdür; sonuçlar yalnızca
metodolojinin doğru çalıştığını gösterir, canlı kârı KANITLAMAZ. Gerçek hüküm
için MEXC tarihsel L2/trade verisiyle replay gerekir.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import random

from .engine import QuoteParams, VolEstimator, microprice, compute_quotes
from .adverse import MarkoutTracker, VPIN, gate
from .risk import RiskLimits, RiskManager
from .pnl import PnLBook


@dataclass
class SimConfig:
    steps: int = 20_000
    dt: float = 1.0                 # saniye / adım
    s0: float = 100.0               # başlangıç fiyatı
    true_vol: float = 0.00005       # adım başına getiri std (~0.5 bp/s)
    tick: float = 0.01
    A: float = 1.2                  # arrival taban yoğunluğu
    informed_frac: float = 0.15     # bilgili emir oranı (toksisite)
    informed_edge: float = 5.0      # bilgili sonrası drift (tick); > yarım-spread olmalı ki ısırsın
    p_switch: float = 0.003         # bilgili yön rejimi değişme olasılığı (otokorelasyon)
    seed: int = 7


def run_simulation(cfg: SimConfig, params: QuoteParams | None = None, verbose=True):
    rng = random.Random(cfg.seed)
    params = params or QuoteParams(tick=cfg.tick, size0=0.1)

    s = cfg.s0
    vol = VolEstimator(lam=0.97, init_var=cfg.true_vol ** 2)
    mk = MarkoutTracker(tau=5.0, lam=0.97)   # kısa horizon: sinyal > gürültü
    vpin = VPIN(bucket_volume=5.0, n_buckets=50)
    risk = RiskManager(RiskLimits())
    book = PnLBook()

    fills = 0
    halts = 0
    widens = 0
    inv_abs_sum = 0.0
    traded_volume = 0.0
    pending_drift = 0.0     # bilgili emrin yarattığı sonraki-adım drift'i (fiyat)
    informed_dir = 1 if rng.random() < 0.5 else -1   # kalıcı (otokorelasyonlu) yön

    for t in range(cfg.steps):
        # Bilgili akış yönü yavaş değişir (gerçek bilgili trader ısrarcıdır)
        if rng.random() < cfg.p_switch:
            informed_dir = -informed_dir
        # --- Mid süreci: GBM + bekleyen bilgili drift ---
        shock = rng.gauss(0.0, cfg.true_vol)
        s *= math.exp(shock)
        s += pending_drift
        pending_drift = 0.0
        s = max(s, 0.01)

        # --- Sentetik defter (top-of-book hacim dengesizliği) ---
        base = 300.0
        imb = rng.gauss(0.0, 0.25)              # gürültü imbalance
        bid_vol = base * (1 + imb)
        ask_vol = base * (1 - imb)
        half = params.tick                       # piyasa spread'i ~2 tick
        p_micro = microprice(s - half, s + half, bid_vol, ask_vol)

        sigma = vol.update(p_micro)
        mk.step(t, p_micro)
        book.mark(p_micro)

        # --- Ters-seçim kapısı ---
        ofi_z = imb / 0.25                       # basit z-yaklaşımı
        decision = gate(mk.adverse_ewma, vpin.value(), ofi_z,
                        queue_depletion=1.0, spread_z=0.0,
                        mk_th=2 * params.tick)   # ~2 tick markout eşiği
        widen_mult = {"NORMAL": 1.0, "WIDEN": 2.0, "HALT": float("inf")}[decision]
        if decision == "WIDEN":
            widens += 1
        if decision == "HALT":
            halts += 1

        # --- Risk / kill-switch ---
        total = book.total(p_micro)
        risk.update_pnl(total)
        triggers = risk.check(book.inventory * p_micro)
        if risk.halted:
            break
        inv_abs_sum += abs(book.inventory * p_micro)

        if math.isinf(widen_mult):               # HALT: kote etme
            continue

        # --- Kotasyonlar ---
        eff = QuoteParams(**{**params.__dict__})
        eff.alpha_AS = params.alpha_AS * widen_mult
        (P_bid, s_bid), (P_ask, s_ask) = compute_quotes(
            p_micro, sigma, book.inventory, mk.adverse_ewma,
            vol_ratio=1.0, params=eff)

        # --- Emir akışı + fill (AS arrival modeli) ---
        informed = rng.random() < cfg.informed_frac
        if informed:
            direction = informed_dir                      # kalıcı gizli yön
        # Buy MO bizim ask'imizi vurur; sell MO bizim bid'imizi vurur.
        d_ask = max(P_ask - p_micro, 0.0)
        d_bid = max(p_micro - P_bid, 0.0)
        lam_buy = cfg.A * math.exp(-params.k * d_ask) * cfg.dt
        lam_sell = cfg.A * math.exp(-params.k * d_bid) * cfg.dt
        if informed:
            # Bilgili taraf, kârlı yönde bizden alır/satar (bizim aleyhimize)
            if direction > 0:
                lam_buy *= 3.0
            else:
                lam_sell *= 3.0

        # Buy MO -> ask fill (biz satarız, side=-1)
        if s_ask > 0 and rng.random() < min(lam_buy, 1.0):
            book.on_fill(-1, P_ask, s_ask, p_micro, params.fee_rate)
            mk.on_fill(t, -1, P_ask)
            vpin.on_trade(s_ask, is_buy=True)
            fills += 1
            traded_volume += s_ask * P_ask
            if informed and direction > 0:
                pending_drift += cfg.informed_edge * params.tick

        # Sell MO -> bid fill (biz alırız, side=+1)
        if s_bid > 0 and rng.random() < min(lam_sell, 1.0):
            book.on_fill(+1, P_bid, s_bid, p_micro, params.fee_rate)
            mk.on_fill(t, +1, P_bid)
            vpin.on_trade(s_bid, is_buy=False)
            fills += 1
            traded_volume += s_bid * P_bid
            if informed and direction < 0:
                pending_drift -= cfg.informed_edge * params.tick

    fair = vol._last or s
    avg_inv = inv_abs_sum / max(t, 1)
    summary = book.summary(fair)
    summary.update({
        "steps_run": t + 1,
        "fills": fills,
        "halts": halts,
        "widens": widens,
        "avg_abs_inventory_notional": avg_inv,
        "traded_volume": traded_volume,
        "turnover_per_capital": traded_volume / 500.0,
        "mean_markout": mk.mean_markout(),
        "vpin_final": vpin.value(),
        "halted": risk.halted,
        "halt_reasons": risk.reasons,
        "final_price": fair,
    })

    if verbose:
        _print_summary(cfg, summary)
    return summary


def _print_summary(cfg: SimConfig, s: dict):
    print("=" * 64)
    print(f"  XMM-CX SİMÜLASYON — informed_frac={cfg.informed_frac:.2f}, "
          f"adım={s['steps_run']}")
    print("=" * 64)
    print(f"  Fill sayısı            : {s['fills']}")
    print(f"  İşlem hacmi (USDT)     : {s['traded_volume']:.1f}")
    print(f"  Ort. |envanter| (USDT) : {s['avg_abs_inventory_notional']:.2f}")
    print(f"  WIDEN / HALT adımları  : {s['widens']} / {s['halts']}")
    print(f"  Ort. markout (fiyat)   : {s['mean_markout']:+.5f}  "
          f"(<0 = ters seçim)")
    print(f"  VPIN (final)           : {s['vpin_final']:.3f}")
    print("-" * 64)
    print("  PnL AYRIŞTIRMASI (SPEC §8):")
    print(f"    (1) Spread yakalama  : {s['spread_capture']:+.4f} USDT")
    print(f"    (2) Envanter/yönlü   : {s['inventory_pnl']:+.4f} USDT")
    print(f"    (3) Komisyon/iade    : {s['fees']:+.4f} USDT")
    print(f"    (4) Hedge            : {s['hedge_pnl']:+.4f} USDT")
    print(f"    --------------------------------------------")
    print(f"    NET TOPLAM           : {s['total']:+.4f} USDT")
    if s["halted"]:
        print(f"  ** KILL-SWITCH: {s['halt_reasons']} **")
    print("=" * 64)
