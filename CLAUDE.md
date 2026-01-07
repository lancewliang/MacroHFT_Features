# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MacroHFT_features is a feature engineering project for high-frequency trading strategies. The project generates minute-level features based on OHLCV data (Open, High, Low, Close, Volume) without considering order flow factors.

## Feature Categories

The project organizes quantitative factors into four main categories:

1. **Liquidity Factors (流动性因子)**: Measure trading activity and price impact costs
2. **Volatility Factors (波动性因子)**: Measure price fluctuation magnitude and frequency
3. **Momentum Factors (动量因子)**: Capture price movement velocity and acceleration
4. **Time Series Factors (时序因子)**: Leverage temporal patterns and cyclical structures

Additionally, factors are classified by their trending characteristics - see `features_catalog.md` for the complete taxonomy.

## Repository Structure

```
MacroHFT_features/
├── features_catalog.md    # Comprehensive factor library and documentation
└── CLAUDE.md             # This file
```

## Key Documentation

- **features_catalog.md**: Complete catalog of quantitative factors including:
  - Factor definitions and formulas
  - Use cases and interpretations
  - Trend factor classifications
  - Feature engineering best practices
  - Factor combination strategies

## Development Guidelines

### Feature Implementation Principles

When implementing new factors:

1. **Input Data**: All factors should be computed from OHLCV data only
2. **Time Granularity**: Features are calculated at minute-level resolution
3. **Vectorization**: Use vectorized operations (NumPy/Pandas) for performance
4. **Window Parameters**: Make lookback periods configurable (e.g., N-period moving average)
5. **Missing Data**: Handle gaps in time series appropriately (forward fill, interpolation, or NaN)

### Factor Computation Best Practices

- Avoid look-ahead bias: use only historical data available at time T
- Handle edge cases (division by zero, empty windows at start of series)
- Normalize/standardize features to comparable scales
- Consider computational efficiency for real-time applications
- Add proper validation for input data quality

### Factor Engineering Workflow

1. **Feature Calculation**: Implement factor formulas from `features_catalog.md`
2. **Feature Validation**:
   - Check for NaN/Inf values
   - Verify calculation logic with known examples
   - Compare against established libraries when possible
3. **Feature Analysis**:
   - Compute Information Coefficient (IC)
   - Test monotonicity
   - Check stability across market regimes
   - Analyze inter-factor correlations
4. **Feature Selection**: Remove redundant or low-quality factors

### Code Organization

When structuring the codebase:

- Group factors by category (liquidity, volatility, momentum, time_series)
- Create reusable utility functions for common operations (moving average, rolling window stats)
- Separate data loading, feature computation, and feature storage
- Include comprehensive docstrings with factor formulas and parameters

## Testing Strategy

- Unit tests for individual factor calculations
- Integration tests for feature pipeline
- Validation tests comparing against reference implementations
- Performance tests for computational efficiency
- Tests for handling edge cases (missing data, extreme values, etc.)

## Common Pitfalls to Avoid

- **Look-ahead bias**: Never use future information in historical feature calculation
- **Survivorship bias**: Ensure historical data includes delisted instruments if applicable
- **Overfitting**: Don't overfit factor parameters to historical data
- **Unstable factors**: Monitor factor behavior during market regime changes
- **Computational cost**: Balance factor complexity with real-time computation requirements

## Factor Combination Strategies

Reference Section 6 in `features_catalog.md` for:
- Trend following strategies (ADX + MACD + moving averages)
- Mean reversion strategies (RSI + Bollinger Bands in ranging markets)
- Breakout strategies (volume confirmation + price-volume correlation)
- Multi-timeframe validation approaches
