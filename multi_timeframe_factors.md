# 多周期因子计算指南

基于1分钟OHLCV数据，计算不同时间周期的因子以捕捉多层次的市场信息。

---

## 1. 为什么需要多周期因子

### 1.1 不同周期捕捉不同信息

- **短周期（5-15分钟）**：捕捉短期噪音、快速反转、日内波动
- **中周期（30-60分钟）**：捕捉日内主趋势、关键支撑阻力
- **长周期（120-240分钟）**：捕捉跨时段趋势、大级别结构

### 1.2 多周期共振提高胜率

当多个时间周期的信号一致时（共振），交易胜率显著提高：
- 3个周期同向：高胜率信号
- 大周期确定方向，小周期确定入场点

---

## 2. 核心多周期因子

### 2.1 趋势类因子（最重要）

这些因子**必须**计算多周期版本：

#### A. 移动平均线（SMA/EMA）

**周期设置：**
```python
# 1分钟数据计算不同周期的均线
timeframes = {
    '5m': 5,      # 5分钟
    '15m': 15,    # 15分钟
    '30m': 30,    # 30分钟
    '60m': 60,    # 60分钟（1小时）
    '120m': 120,  # 120分钟（2小时）
    '240m': 240,  # 240分钟（4小时）
}

# 每个周期计算的均线参数
ma_params = {
    '5m': [5, 10, 20],      # 5分钟级别：5、10、20周期
    '15m': [5, 10, 20],     # 15分钟级别
    '30m': [10, 20, 50],    # 30分钟级别
    '60m': [10, 20, 50],    # 60分钟级别
    '120m': [20, 50, 100],  # 120分钟级别
    '240m': [20, 50, 100],  # 240分钟级别
}
```

**作用说明：**
- **5分钟EMA(5/10)**：超短线入场/出场信号
- **15分钟EMA(10/20)**：短线趋势判断
- **30分钟EMA(20/50)**：日内主趋势方向
- **60分钟EMA(20/50)**：日内大趋势，隔夜持仓参考
- **120分钟EMA(50)**：跨时段趋势，日间交易方向
- **240分钟EMA(50)**：大级别趋势背景

**实现示例：**
```python
def calculate_multi_timeframe_ma(df, timeframes):
    """
    计算多周期移动平均线
    df: 1分钟K线数据，必须有datetime索引
    """
    results = {}

    for tf_name, tf_minutes in timeframes.items():
        # 重采样到指定周期
        df_resampled = df.resample(f'{tf_minutes}T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        # 计算该周期的均线
        for period in [5, 10, 20, 50]:
            col_name = f'ema_{period}_{tf_name}'
            df_resampled[col_name] = df_resampled['close'].ewm(
                span=period, adjust=False
            ).mean()

        # 将高周期数据回填到1分钟数据
        for col in df_resampled.columns:
            if col.startswith('ema_'):
                df[col] = df_resampled[col].reindex(
                    df.index, method='ffill'
                )

        results[tf_name] = df_resampled

    return df, results
```

---

#### B. MACD

**周期设置：**
```python
macd_timeframes = {
    '15m': 15,   # 短线信号
    '30m': 30,   # 日内主信号
    '60m': 60,   # 日内趋势
    '120m': 120, # 大趋势
}

# 每个周期的MACD参数
macd_params = {
    '15m': (12, 26, 9),   # 标准参数
    '30m': (12, 26, 9),
    '60m': (12, 26, 9),
    '120m': (12, 26, 9),
}
```

**作用说明：**
- **15分钟MACD**：短线交易信号，快进快出
- **30分钟MACD**：日内主要交易信号
- **60分钟MACD**：日内趋势判断，持仓时间1-4小时
- **120分钟MACD**：大趋势背景，跨日持仓参考

**多周期共振示例：**
```python
# 金叉共振
macd_golden_cross_15m = (df['macd_15m'] > df['macd_signal_15m'])
macd_golden_cross_30m = (df['macd_30m'] > df['macd_signal_30m'])
macd_golden_cross_60m = (df['macd_60m'] > df['macd_signal_60m'])

# 三周期共振信号
strong_bullish = macd_golden_cross_15m & macd_golden_cross_30m & macd_golden_cross_60m
```

**实现示例：**
```python
def calculate_macd_multi_tf(df, timeframes):
    """计算多周期MACD"""
    for tf_name, tf_minutes in timeframes.items():
        # 重采样
        df_tf = df.resample(f'{tf_minutes}T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        # 计算MACD
        ema12 = df_tf['close'].ewm(span=12, adjust=False).mean()
        ema26 = df_tf['close'].ewm(span=26, adjust=False).mean()
        df_tf[f'macd_{tf_name}'] = ema12 - ema26
        df_tf[f'macd_signal_{tf_name}'] = df_tf[f'macd_{tf_name}'].ewm(
            span=9, adjust=False
        ).mean()
        df_tf[f'macd_hist_{tf_name}'] = (
            df_tf[f'macd_{tf_name}'] - df_tf[f'macd_signal_{tf_name}']
        )

        # 回填到1分钟
        for col in [f'macd_{tf_name}', f'macd_signal_{tf_name}', f'macd_hist_{tf_name}']:
            df[col] = df_tf[col].reindex(df.index, method='ffill')

    return df
```

---

#### C. ADX（趋势强度）

**周期设置：**
```python
adx_timeframes = {
    '15m': 15,
    '30m': 30,
    '60m': 60,
    '120m': 120,
}

adx_period = 14  # ADX周期固定为14
```

**作用说明：**
- **15分钟ADX**：判断短线是否适合趋势策略
- **30分钟ADX**：判断日内主策略类型
- **60分钟ADX**：大周期趋势强度
- **120分钟ADX**：跨时段趋势判断

**使用策略：**
```python
# 策略选择逻辑
if adx_60m > 25 and adx_30m > 25:
    strategy = 'trend_following'  # 趋势跟踪
elif adx_60m < 20 and adx_30m < 20:
    strategy = 'mean_reversion'   # 均值回归
else:
    strategy = 'wait'             # 观望
```

---

#### D. MA_Cross（均线交叉）

**周期设置：**
```python
ma_cross_configs = {
    '5m': (5, 10),     # 5分钟：5MA x 10MA
    '15m': (5, 20),    # 15分钟：5MA x 20MA
    '30m': (10, 30),   # 30分钟：10MA x 30MA
    '60m': (20, 50),   # 60分钟：20MA x 50MA
}
```

**作用说明：**
- **小周期金叉**：快速入场信号
- **大周期金叉**：主趋势确认
- **多周期同时金叉**：强烈买入信号

---

### 2.2 动量类因子

#### A. RSI

**周期设置：**
```python
rsi_timeframes = {
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '60m': 60,
}

rsi_period = 14  # 固定使用14周期
```

**作用说明：**
- **5分钟RSI**：超短线超买超卖
- **15分钟RSI**：日内短线信号
- **30分钟RSI**：日内主要参考
- **60分钟RSI**：大级别超买超卖

**多周期背离检测：**
```python
# 60分钟RSI背离 + 15分钟RSI超卖 = 强烈反转信号
bullish_divergence_60m = (price_new_low) & (rsi_60m_higher_low)
rsi_15m_oversold = (rsi_15m < 30)

strong_reversal_signal = bullish_divergence_60m & rsi_15m_oversold
```

---

#### B. ROC（变化率）

**周期设置：**
```python
roc_configs = {
    '5m': {'timeframe': 5, 'period': 10},
    '15m': {'timeframe': 15, 'period': 10},
    '30m': {'timeframe': 30, 'period': 10},
    '60m': {'timeframe': 60, 'period': 20},
}
```

**作用说明：**
- 不同周期的ROC反映不同时间尺度的动量
- 多周期ROC同向表示强烈动量

---

#### C. Stochastic

**周期设置：**
```python
stoch_timeframes = {
    '5m': 5,
    '15m': 15,
    '30m': 30,
}

stoch_params = (14, 3)  # K周期14，D周期3
```

**作用说明：**
- 随机指标更适合短周期
- 30分钟以上建议使用RSI替代

---

### 2.3 波动率因子

#### A. ATR

**周期设置：**
```python
atr_timeframes = {
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '60m': 60,
    '120m': 120,
}

atr_period = 14
```

**作用说明：**
- **5分钟ATR**：超短线止损距离
- **15分钟ATR**：短线止损参考
- **30分钟ATR**：日内主要止损标准
- **60分钟ATR**：隔夜持仓止损
- **120分钟ATR**：跨日持仓风控

**止损设置示例：**
```python
# 根据持仓预期时间选择ATR周期
if holding_period == 'scalping':        # 5-15分钟
    stop_loss = entry_price - 2 * atr_5m
elif holding_period == 'intraday':      # 1-4小时
    stop_loss = entry_price - 2.5 * atr_30m
elif holding_period == 'swing':         # 跨日
    stop_loss = entry_price - 3 * atr_120m
```

---

#### B. Bollinger Bands

**周期设置：**
```python
bb_timeframes = {
    '15m': 15,
    '30m': 30,
    '60m': 60,
}

bb_params = (20, 2)  # 20周期，2倍标准差
```

**作用说明：**
- **15分钟布林带**：短线超买超卖
- **30分钟布林带**：日内主要通道
- **60分钟布林带**：大级别通道和突破

---

#### C. Historical Volatility

**周期设置：**
```python
hv_timeframes = {
    '30m': 30,
    '60m': 60,
    '120m': 120,
}

hv_period = 20
```

**作用说明：**
- 不同周期的波动率用于不同策略
- 高周期HV用于宏观风险管理

---

### 2.4 成交量因子

#### A. Volume_Ratio

**周期设置：**
```python
volume_timeframes = {
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '60m': 60,
}

volume_period = 20
```

**作用说明：**
- **5分钟放量**：瞬时异动
- **15分钟放量**：短期关注
- **30分钟放量**：重要信号
- **60分钟放量**：大级别突破确认

**多周期放量共振：**
```python
# 多周期同时放量 = 强烈信号
volume_surge_5m = (volume_ratio_5m > 2.0)
volume_surge_15m = (volume_ratio_15m > 1.8)
volume_surge_30m = (volume_ratio_30m > 1.5)

strong_volume_signal = volume_surge_5m & volume_surge_15m & volume_surge_30m
```

---

#### B. OBV

**周期设置：**
```python
obv_timeframes = {
    '15m': 15,
    '30m': 30,
    '60m': 60,
}
```

**作用说明：**
- 不同周期OBV趋势判断不同级别的资金流向
- 多周期OBV共振确认趋势

---

#### C. VWAP

**特殊说明：**
VWAP通常以**日内累计**方式计算，不需要多周期版本。但可以计算：
- 日内VWAP（从开盘累计）
- 滚动VWAP（如60分钟滚动窗口）

```python
# 日内VWAP（每天重置）
df['vwap_daily'] = df.groupby(df.index.date).apply(
    lambda x: (x['typical_price'] * x['volume']).cumsum() / x['volume'].cumsum()
)

# 滚动VWAP（60分钟窗口）
window = 60
df['vwap_60m'] = (
    (df['typical_price'] * df['volume']).rolling(window).sum() /
    df['volume'].rolling(window).sum()
)
```

---

## 3. 不需要多周期的因子

以下因子通常在1分钟数据上计算即可，不需要多周期版本：

### 3.1 价格形态因子
- **Price_Range_Position**：反映当前bar的结构
- **Candle_Body_Ratio**：K线实体比例
- **Gap**：跳空缺口

### 3.2 即时统计因子
- **Z_Score**：建议使用中长周期（如60分钟）
- **Percentile_Rank**：建议使用中长周期

---

## 4. 多周期因子计算完整示例

```python
import pandas as pd
import numpy as np

def resample_ohlcv(df, timeframe_minutes):
    """
    将1分钟数据重采样到指定周期
    df: DataFrame with columns [open, high, low, close, volume]
    timeframe_minutes: int, 目标周期（分钟）
    """
    df_resampled = df.resample(f'{timeframe_minutes}T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    return df_resampled

def calculate_all_multi_timeframe_features(df_1m):
    """
    计算所有多周期因子
    df_1m: 1分钟K线数据，必须有DatetimeIndex
    """

    # 定义时间周期
    timeframes = {
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '60m': 60,
        '120m': 120,
    }

    # 存储所有重采样数据
    df_dict = {'1m': df_1m}

    # 重采样到各个周期
    for tf_name, tf_minutes in timeframes.items():
        df_dict[tf_name] = resample_ohlcv(df_1m, tf_minutes)

    # ===== 1. 计算各周期的因子 =====
    for tf_name, df_tf in df_dict.items():

        # --- 趋势因子 ---
        # EMA
        for period in [5, 10, 20, 50]:
            df_tf[f'ema{period}'] = df_tf['close'].ewm(
                span=period, adjust=False
            ).mean()

        # SMA
        for period in [5, 10, 20, 50]:
            df_tf[f'sma{period}'] = df_tf['close'].rolling(period).mean()

        # MACD
        ema12 = df_tf['close'].ewm(span=12, adjust=False).mean()
        ema26 = df_tf['close'].ewm(span=26, adjust=False).mean()
        df_tf['macd'] = ema12 - ema26
        df_tf['macd_signal'] = df_tf['macd'].ewm(span=9, adjust=False).mean()
        df_tf['macd_hist'] = df_tf['macd'] - df_tf['macd_signal']

        # ADX
        df_tf = calculate_adx(df_tf, period=14)

        # --- 动量因子 ---
        # RSI
        delta = df_tf['close'].diff()
        gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
        loss = -delta.where(delta < 0, 0).ewm(span=14, adjust=False).mean()
        rs = gain / loss
        df_tf['rsi'] = 100 - (100 / (1 + rs))

        # ROC
        df_tf['roc'] = df_tf['close'].pct_change(10) * 100

        # Stochastic (仅短周期)
        if tf_name in ['1m', '5m', '15m', '30m']:
            low_14 = df_tf['low'].rolling(14).min()
            high_14 = df_tf['high'].rolling(14).max()
            df_tf['stoch_k'] = (df_tf['close'] - low_14) / (high_14 - low_14) * 100
            df_tf['stoch_d'] = df_tf['stoch_k'].rolling(3).mean()

        # --- 波动率因子 ---
        # ATR
        df_tf['tr'] = np.maximum(
            df_tf['high'] - df_tf['low'],
            np.maximum(
                abs(df_tf['high'] - df_tf['close'].shift(1)),
                abs(df_tf['low'] - df_tf['close'].shift(1))
            )
        )
        df_tf['atr'] = df_tf['tr'].ewm(span=14, adjust=False).mean()

        # Bollinger Bands
        df_tf['bb_mid'] = df_tf['close'].rolling(20).mean()
        df_tf['bb_std'] = df_tf['close'].rolling(20).std()
        df_tf['bb_upper'] = df_tf['bb_mid'] + 2 * df_tf['bb_std']
        df_tf['bb_lower'] = df_tf['bb_mid'] - 2 * df_tf['bb_std']
        df_tf['bb_width'] = (df_tf['bb_upper'] - df_tf['bb_lower']) / df_tf['bb_mid']
        df_tf['bb_pctb'] = (df_tf['close'] - df_tf['bb_lower']) / (df_tf['bb_upper'] - df_tf['bb_lower'])

        # Historical Volatility
        log_return = np.log(df_tf['close'] / df_tf['close'].shift(1))
        df_tf['hv'] = log_return.rolling(20).std() * np.sqrt(252 * 1440 / tf_minutes) * 100

        # --- 成交量因子 ---
        df_tf['volume_ma20'] = df_tf['volume'].rolling(20).mean()
        df_tf['volume_ratio'] = df_tf['volume'] / df_tf['volume_ma20']

        # OBV
        df_tf['obv'] = (np.sign(df_tf['close'].diff()) * df_tf['volume']).cumsum()

    # ===== 2. 将高周期因子回填到1分钟数据 =====
    for tf_name in ['5m', '15m', '30m', '60m', '120m']:
        df_tf = df_dict[tf_name]

        # 选择要回填的列
        columns_to_forward = [col for col in df_tf.columns if col not in ['open', 'high', 'low', 'close', 'volume']]

        for col in columns_to_forward:
            # 添加周期后缀
            new_col_name = f'{col}_{tf_name}'
            df_1m[new_col_name] = df_tf[col].reindex(df_1m.index, method='ffill')

    return df_1m, df_dict

def calculate_adx(df, period=14):
    """ADX计算（辅助函数）"""
    df['high_diff'] = df['high'] - df['high'].shift(1)
    df['low_diff'] = df['low'].shift(1) - df['low']

    df['plus_dm'] = np.where(
        (df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0),
        df['high_diff'], 0
    )
    df['minus_dm'] = np.where(
        (df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0),
        df['low_diff'], 0
    )

    df['tr_smooth'] = df['tr'].ewm(span=period, adjust=False).mean()
    df['plus_dm_smooth'] = df['plus_dm'].ewm(span=period, adjust=False).mean()
    df['minus_dm_smooth'] = df['minus_dm'].ewm(span=period, adjust=False).mean()

    df['plus_di'] = (df['plus_dm_smooth'] / df['tr_smooth']) * 100
    df['minus_di'] = (df['minus_dm_smooth'] / df['tr_smooth']) * 100

    df['dx'] = (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])) * 100
    df['adx'] = df['dx'].ewm(span=period, adjust=False).mean()

    return df

# ===== 使用示例 =====
# 假设已有1分钟数据
# df_1m = pd.read_csv('1min_ohlcv.csv', parse_dates=['datetime'], index_col='datetime')

# 计算所有多周期因子
# df_1m_enhanced, df_dict = calculate_all_multi_timeframe_features(df_1m)

# 现在df_1m_enhanced包含所有周期的因子：
# - ema20_5m, ema20_15m, ema20_30m, ema20_60m, ema20_120m
# - macd_5m, macd_15m, macd_30m, macd_60m, macd_120m
# - rsi_5m, rsi_15m, rsi_30m, rsi_60m, rsi_120m
# - atr_5m, atr_15m, atr_30m, atr_60m, atr_120m
# 等等...
```

---

## 5. 多周期策略示例

### 5.1 趋势跟踪（多周期共振）

```python
def multi_timeframe_trend_signal(df):
    """
    多周期趋势共振策略
    """
    # 1. 大周期确定方向（120分钟）
    trend_120m = df['ema20_120m'] > df['ema50_120m']

    # 2. 中周期确认（60分钟）
    trend_60m = (df['macd_60m'] > df['macd_signal_60m']) & (df['adx_60m'] > 25)

    # 3. 小周期入场（15分钟）
    entry_15m = (
        (df['ema5_15m'] > df['ema20_15m']) &  # 短期金叉
        (df['rsi_15m'] > 50) &                 # 不在超卖区
        (df['volume_ratio_15m'] > 1.2)         # 放量确认
    )

    # 综合信号：大周期方向 + 中周期确认 + 小周期入场
    long_signal = trend_120m & trend_60m & entry_15m

    return long_signal

# 使用示例
df['long_entry'] = multi_timeframe_trend_signal(df)
```

---

### 5.2 均值回归（多周期超买超卖）

```python
def multi_timeframe_reversal_signal(df):
    """
    多周期反转策略
    """
    # 1. 大周期震荡市（60分钟）
    range_market_60m = df['adx_60m'] < 20

    # 2. 中周期超卖（30分钟）
    oversold_30m = (
        (df['rsi_30m'] < 30) &
        (df['bb_pctb_30m'] < 0)
    )

    # 3. 小周期背离或极值（15分钟）
    # 这里简化，实际需要检测背离
    oversold_15m = df['rsi_15m'] < 25

    # 综合信号
    long_signal = range_market_60m & oversold_30m & oversold_15m

    return long_signal
```

---

### 5.3 突破策略（多周期突破确认）

```python
def multi_timeframe_breakout_signal(df):
    """
    多周期突破策略
    """
    # 1. 大周期窄幅震荡（60分钟）
    consolidation_60m = df['bb_width_60m'] < df['bb_width_60m'].rolling(50).mean() * 0.8

    # 2. 中周期突破（30分钟）
    breakout_30m = df['close'] > df['high'].rolling(30).max().shift(1)

    # 3. 小周期放量确认（15分钟）
    volume_confirm_15m = (
        (df['volume_ratio_15m'] > 1.5) &
        (df['volume_ratio_30m'] > 1.3)
    )

    # 4. 趋势启动（30分钟ADX开始上升）
    adx_rising_30m = df['adx_30m'] > df['adx_30m'].shift(1)

    # 综合信号
    long_signal = consolidation_60m & breakout_30m & volume_confirm_15m & adx_rising_30m

    return long_signal
```

---

## 6. 周期选择建议

### 6.1 根据交易风格选择周期

| 交易风格 | 主要周期 | 参考周期 | 持仓时间 |
|----------|----------|----------|----------|
| **超短线（Scalping）** | 5分钟 | 1分钟、15分钟 | 5-30分钟 |
| **短线（Day Trading）** | 15-30分钟 | 5分钟、60分钟 | 1-6小时 |
| **日内波段** | 30-60分钟 | 15分钟、120分钟 | 数小时-1天 |
| **隔夜持仓** | 60-120分钟 | 30分钟、240分钟 | 1-数天 |

---

### 6.2 因子-周期匹配表

| 因子类型 | 必须多周期 | 推荐周期 | 优先级 |
|----------|-----------|----------|--------|
| **EMA/SMA** | ✅ 是 | 5m, 15m, 30m, 60m, 120m | ⭐⭐⭐⭐⭐ |
| **MACD** | ✅ 是 | 15m, 30m, 60m, 120m | ⭐⭐⭐⭐⭐ |
| **ADX** | ✅ 是 | 15m, 30m, 60m, 120m | ⭐⭐⭐⭐⭐ |
| **RSI** | ✅ 是 | 5m, 15m, 30m, 60m | ⭐⭐⭐⭐ |
| **ATR** | ✅ 是 | 5m, 15m, 30m, 60m, 120m | ⭐⭐⭐⭐⭐ |
| **Bollinger** | ✅ 是 | 15m, 30m, 60m | ⭐⭐⭐⭐ |
| **Volume_Ratio** | ✅ 是 | 5m, 15m, 30m, 60m | ⭐⭐⭐⭐ |
| **OBV** | ✅ 是 | 15m, 30m, 60m | ⭐⭐⭐⭐ |
| **ROC** | 建议 | 15m, 30m, 60m | ⭐⭐⭐ |
| **Stochastic** | 建议 | 5m, 15m, 30m | ⭐⭐⭐ |
| **CMF** | 建议 | 30m, 60m | ⭐⭐⭐ |
| **Z_Score** | 可选 | 60m, 120m | ⭐⭐ |
| **VWAP** | 特殊 | 日内累计 + 60m滚动 | ⭐⭐⭐⭐ |

---

## 7. 实战要点

### 7.1 数据对齐问题

**注意事项：**
```python
# ❌ 错误：直接使用高周期数据会有未来函数
df_1m['signal'] = df_60m['rsi'].iloc[-1]  # 错误！

# ✅ 正确：使用ffill回填
df_1m['rsi_60m'] = df_60m['rsi'].reindex(df_1m.index, method='ffill')
```

---

### 7.2 计算效率优化

```python
# 优化1：只重采样一次，然后计算所有因子
df_60m = resample_ohlcv(df_1m, 60)
# 在df_60m上计算所有60分钟因子

# 优化2：缓存重采样结果
cache_dict = {}
for tf in [5, 15, 30, 60, 120]:
    cache_dict[tf] = resample_ohlcv(df_1m, tf)

# 优化3：增量更新（实盘）
# 每分钟只更新当前bar，不重新计算全部历史
```

---

### 7.3 内存管理

```python
# 对于长时间运行的系统，不要保存所有周期的所有因子
# 只保存必要的因子

essential_features = [
    'ema20_15m', 'ema20_30m', 'ema50_60m',
    'macd_30m', 'macd_signal_30m', 'macd_hist_30m',
    'rsi_15m', 'rsi_30m', 'rsi_60m',
    'adx_30m', 'adx_60m',
    'atr_15m', 'atr_30m', 'atr_60m',
    'volume_ratio_15m', 'volume_ratio_30m',
]

df_1m = df_1m[['open', 'high', 'low', 'close', 'volume'] + essential_features]
```

---

## 8. 总结

### 必须计算多周期的因子（Top 10）：

1. **EMA/SMA** - 所有周期（5m, 15m, 30m, 60m, 120m）
2. **MACD** - 15m, 30m, 60m, 120m
3. **ADX** - 15m, 30m, 60m, 120m
4. **RSI** - 5m, 15m, 30m, 60m
5. **ATR** - 5m, 15m, 30m, 60m, 120m
6. **Bollinger Bands** - 15m, 30m, 60m
7. **Volume_Ratio** - 5m, 15m, 30m, 60m
8. **OBV** - 15m, 30m, 60m
9. **ROC** - 15m, 30m, 60m
10. **MA_Cross** - 5m, 15m, 30m, 60m

### 周期选择原则：

- **5分钟**：超短线信号，快速反应
- **15分钟**：短线交易主周期
- **30分钟**：日内交易核心周期⭐
- **60分钟**：大趋势判断⭐⭐
- **120分钟**：跨时段趋势背景

### 多周期使用原则：

1. **大周期定方向，小周期找入场**
2. **多周期共振信号胜率更高**
3. **根据持仓时间选择主要参考周期**
4. **避免单一周期的虚假信号**

---

**文档版本：** 1.0
**更新日期：** 2026-01-07
**适用场景：** 1分钟K线数据的多周期因子计算
