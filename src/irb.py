"""Basel II IRB-style regulatory capital calculations used in the coursework."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri


def _regulatory_correlation(pd_value: float, regulatory_class: str) -> float:
    if regulatory_class == "qrre":
        return 0.04
    if regulatory_class == "residential_mortgage":
        return 0.15
    if regulatory_class == "other_retail":
        w = (1.0 - np.exp(-35.0 * pd_value)) / (1.0 - np.exp(-35.0))
        return 0.03 * w + 0.16 * (1.0 - w)
    if regulatory_class == "corporate":
        w = (1.0 - np.exp(-50.0 * pd_value)) / (1.0 - np.exp(-50.0))
        return 0.12 * w + 0.24 * (1.0 - w)
    raise ValueError(f"Unsupported regulatory class: {regulatory_class}")


def _maturity_adjustment(pd_value: float, regulatory_class: str, maturity_years: float = 1.0) -> float:
    # Retail exposures do not use the corporate maturity adjustment in this exercise.
    if regulatory_class != "corporate":
        return 1.0
    b = (0.11852 - 0.05478 * np.log(pd_value)) ** 2
    return (1.0 + (maturity_years - 2.5) * b) / (1.0 - 1.5 * b)


def calculate_irb_capital(portfolio: pd.DataFrame, confidence: float = 0.999) -> pd.DataFrame:
    """Calculate IRB capital and RWA for every position.

    Formula follows the Basel II/ASRF specification used in the academic exercise.
    Corporate maturity is M=1 year, making the maturity adjustment equal to 1.
    """
    rows = []
    z = ndtri(confidence)
    for _, r in portfolio.iterrows():
        pdv = float(r["pd"])
        lgd = float(r["lgd"])
        ead = float(r["ead_mn"])
        cls = str(r["regulatory_class"])
        corr = _regulatory_correlation(pdv, cls)
        ma = _maturity_adjustment(pdv, cls, maturity_years=1.0)
        conditional_pd = ndtr((ndtri(pdv) + np.sqrt(corr) * z) / np.sqrt(1.0 - corr))
        k = lgd * (conditional_pd - pdv) * ma
        capital = k * ead
        rwa = 12.5 * capital
        rows.append({
            "position": r["position"],
            "regulatory_class": cls,
            "pd": pdv,
            "lgd": lgd,
            "ead_mn": ead,
            "regulatory_correlation": corr,
            "maturity_adjustment": ma,
            "conditional_pd_999": conditional_pd,
            "capital_ratio": k,
            "capital_mn": capital,
            "rwa_mn": rwa,
            "expected_loss_mn": pdv * lgd * ead,
        })
    return pd.DataFrame(rows)
