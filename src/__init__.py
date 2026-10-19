"""Credit portfolio risk project package."""

from .model import load_inputs, simulate_credit_losses
from .metrics import portfolio_metrics, es_contributions, analytical_expected_loss
from .irb import calculate_irb_capital
