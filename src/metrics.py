"""Risk metrics and analytical checks."""
from __future__ import annotations

import numpy as np
import pandas as pd


def analytical_expected_loss(portfolio: pd.DataFrame) -> float:
    """Sum(EAD * LGD * PD), in EUR millions."""
    return float((portfolio["ead_mn"] * portfolio["lgd"] * portfolio["pd"]).sum())


def portfolio_metrics(losses: pd.DataFrame, confidence: float = 0.999) -> dict:
    """Calculate EL, volatility, VaR, ES and economic capital."""
    total = losses["Total"].to_numpy()
    var = float(np.quantile(total, confidence, method="linear"))
    tail = total[total >= var]
    es = float(tail.mean())
    el = float(total.mean())
    return {
        "n_scenarios": int(total.size),
        "expected_loss": el,
        "std_loss": float(total.std(ddof=1)),
        "var": var,
        "expected_shortfall": es,
        "economic_capital_var_minus_el": var - el,
        "economic_capital_es_minus_el": es - el,
        "confidence": confidence,
    }


def es_contributions(losses: pd.DataFrame, confidence: float = 0.999) -> pd.DataFrame:
    """Euler-style ES contribution: mean position loss in portfolio tail scenarios."""
    total = losses["Total"].to_numpy()
    var = float(np.quantile(total, confidence, method="linear"))
    tail_mask = total >= var
    positions = [c for c in losses.columns if c != "Total"]
    contributions = losses.loc[tail_mask, positions].mean(axis=0)
    out = contributions.rename("es_contribution_mn").to_frame()
    out["share_of_es"] = out["es_contribution_mn"] / contributions.sum()
    return out
