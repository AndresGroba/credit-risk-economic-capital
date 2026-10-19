import numpy as np

from src.model import load_inputs, simulate_credit_losses
from src.metrics import analytical_expected_loss, portfolio_metrics
from src.irb import calculate_irb_capital


def test_analytical_expected_loss_matches_coursework():
    portfolio, _ = load_inputs()
    assert np.isclose(analytical_expected_loss(portfolio), 3.07945, atol=1e-6)


def test_irb_capital_matches_coursework():
    portfolio, _ = load_inputs()
    irb = calculate_irb_capital(portfolio)
    assert np.isclose(irb["capital_mn"].sum(), 23.4537, atol=0.01)
    assert np.isclose(irb["rwa_mn"].sum(), 293.17, atol=0.2)


def test_simulation_is_consistent_with_academic_results():
    # Broad tolerance: Monte Carlo output depends on the random seed/sample.
    losses, diagnostics = simulate_credit_losses(n_scenarios=200_000, seed=123)
    m = portfolio_metrics(losses)
    assert 2.9 < m["expected_loss"] < 3.3
    assert 74.0 < m["var"] < 84.0
    assert 88.0 < m["expected_shortfall"] < 101.0
    assert abs(diagnostics["simulated_default_rate_E1"] - 0.0038) < 0.001
    assert abs(diagnostics["simulated_default_rate_E2"] - 0.0090) < 0.002
