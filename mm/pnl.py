"""PnL ayrıştırması (SPEC §8).

Temel kimlik:
  dPnL = (1) spread yakalama + (2) envanter/yönlü + (3) komisyon/iade + (4) hedge

Her fill, adil değere göre 'içeriden' yakaladığı edge'i (1)'e yazar; envanteri
taşırken fair value hareketi (2)'ye işlenir.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PnLBook:
    spread_capture: float = 0.0     # (1)
    inventory_pnl: float = 0.0      # (2)
    fees: float = 0.0               # (3) maker iade (+) / taker (-)
    hedge_pnl: float = 0.0          # (4)
    cash: float = 0.0               # realize nakit (envanter hariç)
    inventory: float = 0.0          # base birim, işaretli
    _last_fair: float | None = field(default=None, repr=False)

    def on_fill(self, side, price, size, fair, fee_rate):
        """side=+1 alış (envanter artar), -1 satış."""
        # Nakit: alışta çıkar, satışta girer
        self.cash -= side * price * size
        self.inventory += side * size
        # (1) spread yakalama: adil değere göre kazanılan edge
        self.spread_capture += side * (fair - price) * size
        # (3) komisyon: maker iadesi pozitif olabilir; burada fee_rate>=0 maliyet
        self.fees -= fee_rate * price * size

    def mark(self, fair):
        """(2) envanteri yeni adil değere markla."""
        if self._last_fair is not None:
            self.inventory_pnl += self.inventory * (fair - self._last_fair)
        self._last_fair = fair

    def add_hedge(self, pnl):
        self.hedge_pnl += pnl

    def total(self, fair):
        """Realize + unrealize toplam (envanter mid'e marklanmış)."""
        return self.cash + self.inventory * fair + self.fees + self.hedge_pnl

    def summary(self, fair):
        return {
            "spread_capture": self.spread_capture,
            "inventory_pnl": self.inventory_pnl,
            "fees": self.fees,
            "hedge_pnl": self.hedge_pnl,
            "inventory_units": self.inventory,
            "inventory_notional": self.inventory * fair,
            "total": self.total(fair),
        }
