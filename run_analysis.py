"""Run the credit portfolio simulation and save the main results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.model import load_inputs, simulate_credit_losses
from src.metrics import analytical_expected_loss, portfolio_metrics, es_contributions
from src.irb import calculate_irb_capital
from src.plotting import plot_loss_distribution, plot_es_contributions, plot_capital_comparison


def main():
    parser = argparse.ArgumentParser(description="Credit portfolio risk & economic capital analysis")
    parser.add_argument("--scenarios", type=int, default=1_000_000, help="Number of Monte Carlo scenarios")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    results_dir = root / "results"
    results_dir.mkdir(exist_ok=True)

    portfolio, _ = load_inputs()
    losses, diagnostics = simulate_credit_losses(args.scenarios, args.seed)
    metrics = portfolio_metrics(losses)
    contributions = es_contributions(losses)
    irb = calculate_irb_capital(portfolio)

    summary = {
        **metrics,
        "analytical_expected_loss": analytical_expected_loss(portfolio),
        "regulatory_capital_irb": float(irb["capital_mn"].sum()),
        "rwa_total": float(irb["rwa_mn"].sum()),
        "diagnostics": diagnostics,
    }

    contributions.to_csv(results_dir / "es_contributions.csv")
    irb.to_csv(results_dir / "irb_capital.csv", index=False)
    with open(results_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    plot_loss_distribution(losses, metrics, results_dir / "loss_distribution.png")
    plot_es_contributions(contributions, results_dir / "es_contributions.png")
    plot_capital_comparison(
        metrics["economic_capital_var_minus_el"],
        summary["regulatory_capital_irb"],
        results_dir / "capital_comparison.png",
    )

    print("Credit Portfolio Risk & Economic Capital")
    print("-" * 45)
    print(f"Scenarios:              {summary['n_scenarios']:,}")
    print(f"Expected loss:          {summary['expected_loss']:.3f} M€")
    print(f"Analytical EL:          {summary['analytical_expected_loss']:.3f} M€")
    print(f"VaR 99.9%:             {summary['var']:.3f} M€")
    print(f"Expected Shortfall:     {summary['expected_shortfall']:.3f} M€")
    print(f"Economic capital:       {summary['economic_capital_var_minus_el']:.3f} M€")
    print(f"IRB regulatory capital: {summary['regulatory_capital_irb']:.3f} M€")
    print(f"RWA:                    {summary['rwa_total']:.3f} M€")


if __name__ == "__main__":
    main()
