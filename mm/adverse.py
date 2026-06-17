"""Ters-seçim (adverse selection) tespiti ve kapısı (SPEC §5).

Birincil sinyal markout: fill sonrası mid'in bizim aleyhimize sürüklenmesi.
Ek sinyaller VPIN ve OFI z-skoru ile skorlama yapılır.
"""
from __future__ import annotations
from collections import deque


class MarkoutTracker:
    """Bekleyen fill'leri tutar, tau saniye sonra markout'u realize eder (SPEC §5.1).

    markout_t = side * (s_{t+tau} - p_fill);  side=+1 alış, -1 satış.
    EWMA(adverse) = (-markout)_+ üzerinden -> pozitif = ters seçim baskısı.
    """

    def __init__(self, tau: float = 30.0, lam: float = 0.97):
        self.tau = tau
        self.lam = lam
        self.pending = deque()      # (realize_time, side, fill_price)
        self._ewma = 0.0            # net (-markout) EWMA, işaretli (fiyat birimi)
        self.realized = []          # markout listesi — raporlama

    def on_fill(self, t, side, fill_price):
        self.pending.append((t + self.tau, side, fill_price))

    def step(self, t, mid):
        while self.pending and self.pending[0][0] <= t:
            _, side, fp = self.pending.popleft()
            markout = side * (mid - fp)
            self.realized.append(markout)
            # İşaretli: iyi fill'ler (markout>0) kötüleri telafi eder.
            self._ewma = self.lam * self._ewma + (1 - self.lam) * (-markout)

    @property
    def adverse_ewma(self):
        """Ters-seçim tahmini: yalnızca net NEGATİF markout (kayıp) raporlanır."""
        return max(self._ewma, 0.0)

    def mean_markout(self):
        return sum(self.realized) / len(self.realized) if self.realized else 0.0


class VPIN:
    """Hacim-senkronize bilgili işlem olasılığı (SPEC §5.2)."""

    def __init__(self, bucket_volume: float, n_buckets: int = 50):
        self.V = bucket_volume
        self.buckets = deque(maxlen=n_buckets)
        self._buy = 0.0
        self._sell = 0.0
        self._filled = 0.0

    def on_trade(self, volume, is_buy):
        (setattr(self, "_buy", self._buy + volume) if is_buy
         else setattr(self, "_sell", self._sell + volume))
        self._filled += volume
        while self._filled >= self.V:
            self.buckets.append(abs(self._buy - self._sell) / self.V)
            self._buy = self._sell = self._filled = 0.0

    def value(self):
        return sum(self.buckets) / len(self.buckets) if self.buckets else 0.0


def gate(markout_ewma, vpin, ofi_z, queue_depletion, spread_z,
         mk_th=0.0, vpin_th=0.6, ofi_th=2.0, qd_th=2.0, sprd_th=3.0):
    """Skor tabanlı kapı (SPEC §5.4) -> 'HALT' | 'WIDEN' | 'NORMAL'."""
    score = 0
    if markout_ewma > mk_th:
        score += 2
    if vpin > vpin_th:
        score += 1
    if abs(ofi_z) > ofi_th:
        score += 1
    if queue_depletion > qd_th:
        score += 1
    if spread_z > sprd_th:
        score += 1
    if score >= 4:
        return "HALT"
    if score >= 2:
        return "WIDEN"
    return "NORMAL"
