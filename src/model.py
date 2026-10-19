"""Monte Carlo credit portfolio model.

The implementation reproduces the structure of an MSc academic exercise:
- three infinitely granular retail sub-portfolios driven by correlated sector factors;
- two single-name corporate exposures retaining idiosyncratic default risk.

All monetary amounts are expressed in EUR millions.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

ROOT = Path(__file__).resolve().parents[1]


def load_inputs(data_dir: str | Path | None = None):
    """Load portfolio and sector-correlation inputs from CSV files."""
    data_dir = Path(data_dir) if data_dir else ROOT / "data"
    portfolio = pd.read_csv(data_dir / "portfolio.csv")
    corr_df = pd.read_csv(data_dir / "sector_correlation.csv", index_col=0)
    corr = corr_df.to_numpy(dtype=float)
    return portfolio, corr


def _retail_loss(ead, lgd, pd, rho, factor):
    """Conditional Vasicek/ASRF loss for an infinitely granular portfolio."""
    conditional_pd = ndtr((ndtri(pd) - np.sqrt(rho) * factor) / np.sqrt(1.0 - rho))
    return ead * lgd * conditional_pd


def simulate_credit_losses(
    n_scenarios: int = 1_000_000,
    seed: int = 42,
    data_dir: str | Path | None = None,
):
    """Simulate portfolio credit losses.

    Returns
    -------
    losses : pandas.DataFrame
        Scenario losses by position and total, in EUR millions.
    diagnostics : dict
        Useful model diagnostics (Cholesky matrix, asset variances/thresholds).
    """
    portfolio, corr = load_inputs(data_dir)
    rng = np.random.default_rng(seed)

    # Correlated systematic sector factors via Cholesky.
    chol = np.linalg.cholesky(corr)
    z = rng.standard_normal((n_scenarios, 3))
    factors = z @ chol.T
    fs1, fs2, fs3 = factors.T

    p = portfolio.set_index("position")

    # Infinitely granular retail portfolios: idiosyncratic risk diversifies away.
    l_c1 = _retail_loss(p.loc["C1", "ead_mn"], p.loc["C1", "lgd"], p.loc["C1", "pd"], p.loc["C1", "rho_economic"], fs1)
    l_c2 = _retail_loss(p.loc["C2", "ead_mn"], p.loc["C2", "lgd"], p.loc["C2", "pd"], p.loc["C2", "rho_economic"], fs2)
    l_c3 = _retail_loss(p.loc["C3", "ead_mn"], p.loc["C3", "lgd"], p.loc["C3", "pd"], p.loc["C3", "rho_economic"], fs3)

    # Single-name corporates: keep idiosyncratic risk.
    # Variances and loadings follow the academic exercise specification.
    var_e1_idio = 0.27
    var_e2_idio = 0.4275
    eps1 = rng.normal(0.0, np.sqrt(var_e1_idio), n_scenarios)
    eps2 = rng.normal(0.0, np.sqrt(var_e2_idio), n_scenarios)

    asset_e1 = 0.50 * fs1 + 0.40 * fs2 + eps1
    asset_e2 = 0.25 * fs2 + 0.60 * fs3 + eps2

    # The second asset construction has variance 1.03, so its threshold is scaled
    # to preserve the requested unconditional PD.
    var_e1 = 0.50**2 + 0.40**2 + 2 * 0.50 * 0.40 * corr[0, 1] + var_e1_idio
    var_e2 = 0.25**2 + 0.60**2 + 2 * 0.25 * 0.60 * corr[1, 2] + var_e2_idio
    threshold_e1 = ndtri(p.loc["E1", "pd"]) * np.sqrt(var_e1)
    threshold_e2 = ndtri(p.loc["E2", "pd"]) * np.sqrt(var_e2)

    default_e1 = asset_e1 < threshold_e1
    default_e2 = asset_e2 < threshold_e2
    l_e1 = default_e1.astype(float) * p.loc["E1", "ead_mn"] * p.loc["E1", "lgd"]
    l_e2 = default_e2.astype(float) * p.loc["E2", "ead_mn"] * p.loc["E2", "lgd"]

    total = l_c1 + l_c2 + l_c3 + l_e1 + l_e2
    losses = pd.DataFrame({
        "C1": l_c1,
        "C2": l_c2,
        "C3": l_c3,
        "E1": l_e1,
        "E2": l_e2,
        "Total": total,
    })

    diagnostics = {
        "cholesky": chol.tolist(),
        "asset_variance_E1": float(var_e1),
        "asset_variance_E2": float(var_e2),
        "threshold_E1": float(threshold_e1),
        "threshold_E2": float(threshold_e2),
        "simulated_default_rate_E1": float(default_e1.mean()),
        "simulated_default_rate_E2": float(default_e2.mean()),
    }
    return losses, diagnostics
