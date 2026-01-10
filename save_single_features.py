"""
Save single feature column names to numpy file for dtype specification.
These are all the basic single-stock features EXCLUDING trend features.
"""
import numpy as np

# Define all single feature column names (excluding trend features)
single_features = [
    # Liquidity factors (17 features - removed trend-related volume features)
    'wap',
    'price_volume',
    'log_return_wap_1',
    'log_return_wap_2',
    'volume_zscore_30',
    'volume_ratio_5_30',
    'turnover',
    'turnover_zscore_30',
    'volume_acceleration_20',
    'price_volume_corr_5',
    'price_volume_corr_10',
    'price_volume_corr_20',
    'volume_weighted_vol',
    'volume_at_high',
    'volume_at_low',

    # Volatility factors (7 features)
    'intrabar_volatility',
    'high_low_range',
    'high_low_range_pct',
    'liquidity_cost_proxy',
    'true_range',
    'range_utilization',
    'signed_range_util',

    # Microstructure factors (3 features)
    'true_strength_proxy',
    'price_efficiency',
    'price_reversal_ind',

    # K-line pattern factors (9 features)
    'kmid',
    'klen',
    'kup',
    'klow',
    'ksft',
    'kmid2',
    'kup2',
    'klow2',
    'ksft2'
]

# Save to numpy file
np.save('single_features.npy', np.array(single_features))

print(f"Saved {len(single_features)} single feature names to single_features.npy")
print(f"\nFeature breakdown:")
print(f"  - Liquidity factors: 15")
print(f"  - Volatility factors: 7")
print(f"  - Microstructure factors: 3")
print(f"  - K-line pattern factors: 9")
print(f"  - Total: {len(single_features)}")
print(f"\nNote: Trend-related features (72 features) are stored separately in trend_features.npy")

# Verify unique feature names
if len(single_features) != len(set(single_features)):
    duplicates = [f for f in single_features if single_features.count(f) > 1]
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

# Load the feature names
single_features = np.load('single_features.npy', allow_pickle=True)
trend_features = np.load('trend_features.npy', allow_pickle=True)

# Combine both if needed
all_features = np.concatenate([single_features, trend_features])

# Create dtype specification for DataFrame
dtype_spec_single = {col: 'float32' for col in single_features}
dtype_spec_trend = {col: 'float32' for col in trend_features}
dtype_spec_all = {col: 'float32' for col in all_features}

# Option 1: Load only single features
df_single = pd.read_csv('data.csv', usecols=single_features, dtype=dtype_spec_single)

# Option 2: Load only trend features
df_trend = pd.read_csv('data.csv', usecols=trend_features, dtype=dtype_spec_trend)

# Option 3: Load all features
df_all = pd.read_csv('data.csv', usecols=all_features, dtype=dtype_spec_all)

# Option 4: Convert existing DataFrame columns
df[single_features] = df[single_features].astype('float32')
df[trend_features] = df[trend_features].astype('float32')
""")
