"""
Save trend feature column names to numpy file for dtype specification.
These are specifically the trend-related features (60-period and MACD only).
"""
import numpy as np

# Define all trend feature column names (only 60-period and MACD features)
trend_features = [
    'volume_acceleration_60',
    'volume_zscore_60',
    'volume_zscore_100',
    'turnover_zscore_60',
    'turnover_zscore_100',
    'volume_ratio_10_60',
    'volume_trend_60',
    'sma_60',
    'ema_60',
    'price_to_sma_60',
    'price_to_ema_60',
    'sma_slope_60',
    'ema_slope_60',
    'roc_60',
    'momentum_60',
    'plus_dm_ema_60',
    'minus_dm_ema_60',
    'tr_ema_60',
    'di_plus_60',
    'di_minus_60',
    'adx_60',
    'price_position_60',
    'higher_high_count_60',
    'lower_low_count_60',
    'trend_consistency_60',
    'trend_strength_idx_60',
    'lr_slope_60',
    'r_squared_60',
    'ema_12',
    'ema_26',
    'macd_12_26',
    'macd_signal_9',
    'macd_histogram',
    'multi_tf_trend_align',
    'trend_strength_comp'
]

# Save to numpy file
np.save('data/ETHUSDT/tmp/trend_features.npy', np.array(trend_features))

print(f"Saved {len(trend_features)} trend feature names to trend_features.npy")
print(f"\nThese are specifically trend-related features including:")
print(f"  - 60-period features (SMA, EMA, ROC, Momentum, ADX, etc.)")
print(f"  - MACD indicators (ema_12, ema_26, macd_12_26, macd_signal_9, macd_histogram)")
print(f"  - Trend strength and alignment metrics")
print(f"  - Volume trends and z-scores (60, 100 periods)")
print(f"  - Total: {len(trend_features)} features")

# Verify unique feature names
if len(trend_features) != len(set(trend_features)):
    duplicates = [f for f in trend_features if trend_features.count(f) > 1]
    print(f"\nWARNING: Found duplicate features: {set(duplicates)}")
else:
    print("\n✓ All feature names are unique")

# Example usage
print("\n" + "="*60)
print("Example usage:")
print("="*60)
print("""
import pandas as pd
import numpy as np

# Load the trend feature names
trend_features = np.load('trend_features.npy', allow_pickle=True)

# Create dtype specification for DataFrame
dtype_spec = {col: 'float32' for col in trend_features}

# Option 1: Specify dtypes when reading CSV
df = pd.read_csv('data.csv', dtype=dtype_spec)

# Option 2: Convert existing DataFrame columns
df[trend_features] = df[trend_features].astype('float32')

# Option 3: Select only trend feature columns
df_trend = df[trend_features]

# Option 4: Filter for specific feature types
# Volume-related trend features
volume_features = [f for f in trend_features if 'volume' in f or 'turnover' in f]

# MACD features
macd_features = [f for f in trend_features if 'macd' in f or 'ema_12' in f or 'ema_26' in f]

# ADX features
adx_features = [f for f in trend_features if 'adx' in f or 'di_' in f or 'dm_' in f]
""")
