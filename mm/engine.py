"""Kotasyon motoru — Avellaneda-Stoikov + envanter skew (SPEC §2-4).

Bütün fiyat matematiği burada toplanır. Motor durumsuzdur (stateless) sayılır:
volatilite EWMA durumu hariç her şey çağrı başına parametre olarak gelir, böylece
hem canlıda hem simülasyonda aynı kod yolu kullanılır.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass
class QuoteParams:
    gamma: float = 0.3          # risk-kaçınma (SPEC §2.6)
    eta: float = 20.0           # envanter-zaman ölçeği, (T-t) yerine (s)
    k: float = 150.0            # arrival decay (fiyat birimi başına), lambda(d)=A e^{-k d}
    fee_rate: float = 0.0       # tek-yön maker komisyonu (MEXC spot ~0; API'den oku!)
    alpha_AS: float = 2.0       # ters-seçim güvenlik çarpanı
    n_tick: int = 3             # minimum spread (tick katı)
    tick: float = 0.01          # fiyat adımı (symbol filter'dan)
    phi: float = 0.6            # mikro-fiyat imbalance duyarlılığı
    theta: float = 0.6          # skew yoğunluğu (Kanal B)
    rho: float = 0.4            # boyut asimetrisi (Kanal C)
    beta_V: float = 0.3         # hacim genişletme
    size0: float = 0.1          # taban emir boyutu (BASE birim; ~10 USDT @ p=100)
    Q_max: float = 200.0        # maks envanter notional (USDT) -> kırmızı band


def microprice(bid_px, ask_px, bid_vol, ask_vol):
    """Hacim-ağırlıklı (çapraz) mikro-fiyat (SPEC §2.1)."""
    tot = bid_vol + ask_vol
    if tot <= 0:
        return 0.5 * (bid_px + ask_px)
    return (bid_px * ask_vol + ask_px * bid_vol) / tot


def book_imbalance(bid_vol, ask_vol):
    """I in [-1, 1]; pozitif = alıcı baskısı (SPEC §2.1)."""
    tot = bid_vol + ask_vol
    return 0.0 if tot <= 0 else (bid_vol - ask_vol) / tot


class VolEstimator:
    """EWMA gerçekleşen volatilite (SPEC §2.2). sigma, adım başına std döner."""

    def __init__(self, lam: float = 0.97, init_var: float = 1e-6):
        self.lam = lam
        self.var = init_var
        self._last = None

    def update(self, price: float) -> float:
        if self._last is not None and self._last > 0 and price > 0:
            r = math.log(price / self._last)
            self.var = self.lam * self.var + (1 - self.lam) * r * r
        self._last = price
        return math.sqrt(self.var)


def round_to_tick(price: float, tick: float, mode: str) -> float:
    n = price / tick
    n = math.floor(n) if mode == "DOWN" else math.ceil(n)
    return round(n * tick, 10)


def compute_quotes(p_fair, sigma, q, as_estimate, vol_ratio, params: QuoteParams):
    """Bid/ask (fiyat, boyut) çiftlerini döndürür (SPEC §2.4, §4.4).

    p_fair      : mikro-fiyat (adil değer)
    sigma       : adım başına volatilite (EWMA)
    q           : işaretli envanter (base birim)
    as_estimate : ters-seçim tahmini (fiyat birimi; markout EWMA)
    vol_ratio   : V_win / V_ort (hacim genişletme için)
    """
    Q = q * p_fair
    u = max(-1.0, min(1.0, Q / params.Q_max))   # envanter oranı

    # Rezervasyon fiyatı (Kanal A) — sürekli/stationary AS
    r = p_fair - q * params.gamma * sigma ** 2 * params.eta

    # Optimal + taban spread (SPEC §2.4)
    delta_AS = params.gamma * sigma ** 2 * params.eta \
        + (2.0 / params.gamma) * math.log(1.0 + params.gamma / params.k)
    delta_min = 2 * params.fee_rate * p_fair \
        + params.alpha_AS * as_estimate \
        + params.n_tick * params.tick
    delta = max(delta_AS, delta_min)

    # Hacim koşullandırması (SPEC §2.5)
    delta *= (1.0 + params.beta_V * max(vol_ratio - 1.0, 0.0))

    # Asimetrik yarım-spread (Kanal B)
    skew = params.theta * u * 0.5 * delta
    d_bid = 0.5 * delta + skew
    d_ask = 0.5 * delta - skew

    P_bid = round_to_tick(r - d_bid, params.tick, "DOWN")
    P_ask = round_to_tick(r + d_ask, params.tick, "UP")
    # spread'in çökmesini engelle (round sonrası en az 1 tick aralık)
    if P_ask - P_bid < params.tick:
        P_ask = round_to_tick(P_bid + params.tick, params.tick, "UP")

    # Boyut asimetrisi (Kanal C): ağır taraf küçülür
    up, un = max(u, 0.0), max(-u, 0.0)
    s_bid = params.size0 * (1 + params.rho * un) * (1 - params.rho * up)
    s_ask = params.size0 * (1 + params.rho * up) * (1 - params.rho * un)

    # Kırmızı band override (SPEC §3.2): risk-artıran tarafı kapat
    if abs(u) >= 1.0:
        if u > 0:
            s_bid = 0.0
        else:
            s_ask = 0.0

    return (P_bid, max(s_bid, 0.0)), (P_ask, max(s_ask, 0.0))
