# Methodology

## 1. Portfolio

The portfolio contains five positions:

- **C1:** other retail / small-business retail portfolio
- **C2:** qualifying revolving retail exposure (QRRE)
- **C3:** residential mortgage portfolio
- **E1:** single-name corporate exposure
- **E2:** single-name corporate exposure

The three retail positions are treated as infinitely granular and homogeneous. Conditional on the systematic factor, borrower-specific idiosyncratic risk is therefore assumed to diversify away. E1 and E2 are individual corporate names, so their idiosyncratic default risk remains in the simulation.

## 2. Credit inputs

Each position is described by:

- **PD**: probability of default
- **LGD**: loss given default
- **EAD**: exposure at default

The analytical Expected Loss is

`EL = Σ(PD_i × LGD_i × EAD_i)`

which gives approximately **3.07945 M€** for the input portfolio.

## 3. Systematic factors

Three sector factors drive the portfolio. They are standard normal variables with correlation matrix:

```text
       FS1  FS2  FS3
FS1    1.0  0.8  0.7
FS2    0.8  1.0  0.6
FS3    0.7  0.6  1.0
```

Independent Gaussian draws are transformed with a Cholesky decomposition so that the simulated factors reproduce this dependence structure.

## 4. Retail losses

For the granular retail books, the conditional default rate is obtained from the Vasicek/ASRF formulation using the unconditional PD, the asset correlation and the corresponding sector factor.

The scenario loss for a retail position is

`Loss_i = EAD_i × LGD_i × conditional_PD_i`

so adverse sector-factor realizations translate into higher conditional default rates and larger portfolio losses.

## 5. Corporate defaults

The two corporate names are modelled through latent asset values:

```text
E1 asset value = 0.50 × FS1 + 0.40 × FS2 + epsilon1
E2 asset value = 0.25 × FS2 + 0.60 × FS3 + epsilon2
```

The idiosyncratic terms `epsilon1` and `epsilon2` preserve single-name default risk. A name defaults when its simulated latent asset value falls below the threshold associated with its unconditional PD.

The E2 latent construction has variance 1.03 rather than exactly 1.00, so its default threshold is scaled by `sqrt(1.03)` in order to preserve the target unconditional PD.

## 6. Portfolio simulation

For each Monte Carlo scenario the model:

1. draws the three correlated sector factors;
2. calculates losses for C1, C2 and C3;
3. simulates default events for E1 and E2;
4. sums the five position losses.

Repeating the process produces the empirical distribution of total portfolio losses.

## 7. Risk measures

### Expected Loss

The mean simulated portfolio loss. It is compared with the analytical `Σ(PD × LGD × EAD)` value as a validation check.

### VaR 99.9%

The 99.9th percentile of the simulated loss distribution.

### Expected Shortfall 99.9%

The mean loss across scenarios at or beyond the 99.9% VaR threshold.

### Expected Shortfall contribution

For each position, the contribution is calculated as its average loss in the same tail scenarios used to calculate portfolio Expected Shortfall. The position contributions therefore add up to total ES.

## 8. Economic capital

For this exercise, economic capital is defined as

`Economic Capital = VaR 99.9% - Expected Loss`

so capital covers the simulated unexpected-loss component above average losses.

## 9. Basel IRB-style capital

Regulatory capital is calculated position by position using the IRB/ASRF-style formula specified in the original exercise.

Regulatory asset correlations depend on exposure class:

- other retail;
- QRRE;
- residential mortgage;
- corporate.

The two corporate positions use a one-year maturity in this implementation. Risk-Weighted Assets are obtained from

`RWA = 12.5 × capital`

## 10. Concentration effect

The main difference between the economic and regulatory views comes from the two corporate names, particularly E2. Their discrete defaults create large jumps in portfolio losses and dominate the simulated tail.

The granular retail positions are much closer to the diversification assumptions underlying the ASRF framework. The comparison therefore provides a simple illustration of why single-name concentration can require additional attention beyond a granular Pillar 1 capital calculation.
