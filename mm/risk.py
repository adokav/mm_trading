"""Risk limitleri ve kill-switch (SPEC §9).

Tasarım ilkesi: belirsizlikte önce iptal, sonra düzleştir, sonra dur.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RiskLimits:
    capital: float = 500.0
    max_inventory_notional: float = 200.0   # tek çift, %40
    daily_stop: float = 15.0                 # %3
    max_drawdown: float = 25.0               # %5
    max_open_orders: int = 8


class RiskManager:
    """Durum biriktirir, kill-switch kararı verir."""

    def __init__(self, limits: RiskLimits):
        self.lim = limits
        self.daily_pnl = 0.0
        self.peak_pnl = 0.0
        self.halted = False
        self.reasons: list[str] = []

    def update_pnl(self, total_pnl):
        self.daily_pnl = total_pnl
        self.peak_pnl = max(self.peak_pnl, total_pnl)

    @property
    def drawdown(self):
        return self.peak_pnl - self.daily_pnl

    def check(self, inventory_notional, data_stale=False, vol_shock=False,
              toxic_flow=False):
        """Tetikleyici listesi döndürür (SPEC §9.2). Boşsa kote etmek güvenli."""
        t = []
        if self.daily_pnl <= -self.lim.daily_stop:
            t.append("DAILY_LOSS")
        if self.drawdown >= self.lim.max_drawdown:
            t.append("DRAWDOWN")
        if abs(inventory_notional) > self.lim.max_inventory_notional:
            t.append("MAX_INVENTORY")
        if data_stale:
            t.append("DATA_STALE")
        if vol_shock:
            t.append("VOL_SHOCK")
        if toxic_flow:
            t.append("TOXIC_FLOW")
        # Sert tetikler -> kalıcı halt (manuel re-arm); yumuşaklar -> geçici
        hard = {"DAILY_LOSS", "DRAWDOWN", "DATA_STALE"}
        if t and (set(t) & hard):
            self.halted = True
            self.reasons = t
        return t

    def must_flatten(self, triggers):
        return bool({"DRAWDOWN", "DATA_STALE", "MAX_INVENTORY"} & set(triggers))
