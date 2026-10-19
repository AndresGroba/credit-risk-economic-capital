"""Plotting helpers for portfolio-risk results."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_loss_distribution(losses: pd.DataFrame, metrics: dict, output_path: str | Path):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(losses["Total"], bins=120)
    ax.axvline(metrics["var"], linestyle="--", linewidth=1.5, label=f"VaR 99.9% = {metrics['var']:.1f} M€")
    ax.axvline(metrics["expected_shortfall"], linestyle=":", linewidth=1.8, label=f"ES 99.9% = {metrics['expected_shortfall']:.1f} M€")
    ax.set_title("Simulated credit portfolio loss distribution")
    ax.set_xlabel("Loss (EUR mn)")
    ax.set_ylabel("Scenario count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_es_contributions(contrib: pd.DataFrame, output_path: str | Path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    vals = contrib["es_contribution_mn"]
    ax.bar(vals.index, vals.values)
    ax.set_title("Expected Shortfall contribution by exposure")
    ax.set_ylabel("ES contribution (EUR mn)")
    ax.set_xlabel("Position")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_capital_comparison(economic_capital: float, regulatory_capital: float, output_path: str | Path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(["Economic capital\n(VaR - EL)", "Regulatory capital\n(IRB)"], [economic_capital, regulatory_capital])
    ax.set_title("Economic vs regulatory capital")
    ax.set_ylabel("EUR mn")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
