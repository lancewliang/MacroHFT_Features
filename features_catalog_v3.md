# 特征工程因子目录 v3.0 - 经典因子精选版

基于OHLCV数据的分钟级经典因子库，精选业界最常用和最有效的因子。

**符号约定：**
- O_t, H_t, L_t, C_t, V_t：第t期的开盘价、最高价、最低价、收盘价、成交量
- MA_n(X)：X的n期简单移动平均
- EMA_n(X)：X的n期指数移动平均，α = 2/(n+1)
- Std_n(X)：X的n期标准差
- Max_n(X)、Min_n(X)：X在n期内的最大值、最小值
- Σ：求和符号
- **[趋势]** 标记表示该因子是趋势因子

---

## 1. 流动性因子 (Liquidity Factors)

流动性因子衡量市场交易活跃度，帮助识别资金流向和市场参与度。

### 1.1 Volume_Ratio（成交量比率）

**作用：** 识别异常放量，确认突破有效性，判断市场关注度变化。放量突破更可靠，缩量运行需警惕。

**计算公式：**
```
Volume_Ratio_t = V_t / MA_n(V_t)
```

**参数：** n = 20

**使用说明：**
- Volume_Ratio > 1.5：显著放量，关注突破机会
- Volume_Ratio > 2.0：异常放量，可能有重要事件
- Volume_Ratio < 0.5：缩量，趋势可能乏力

---

### 1.2 VWAP（成交量加权平均价）**[趋势]**

**作用：** 反映市场平均成交成本，作为日内交易的重要支撑/阻力位，机构常用的执行基准。

**计算公式：**
```
TP_t = (H_t + L_t + C_t) / 3
VWAP_t = Σ(TP_i × V_i) / Σ(V_i),  i ∈ [开盘, t]
```

**使用说明：**
- 价格在VWAP之上：日内强势，多头占优
- 价格在VWAP之下：日内弱势，空头占优
- 价格回踩VWAP不破：良好的买入点
- 常用于日内交易的进出场参考

---

### 1.3 VWAP_Distance（VWAP偏离度）

**作用：** 衡量价格偏离平均成本的程度，识别超买超卖和均值回归机会。

**计算公式：**
```
VWAP_Distance_t = (C_t - VWAP_t) / VWAP_t × 100%
```

**使用说明：**
- |Distance| > 1%：价格显著偏离，可能回归
- |Distance| > 2%：极端偏离，高概率回调
- 配合趋势指标使用，避免逆势操作

---

### 1.4 OBV (On Balance Volume)（能量潮）**[趋势]**

**作用：** 累积成交量指标，判断资金流向，验证价格趋势真实性，发现背离信号。

**计算公式：**
```
OBV_t = OBV_{t-1} + V_t      if C_t > C_{t-1}
OBV_t = OBV_{t-1} - V_t      if C_t < C_{t-1}
OBV_t = OBV_{t-1}            if C_t = C_{t-1}
```

初始值：OBV_0 = 0

**使用说明：**
- OBV上升 + 价格上升：趋势健康
- OBV下降 + 价格上升：顶背离，警惕反转
- OBV上升 + 价格下降：底背离，关注反转机会
- OBV突破前高：确认价格突破有效性

---

## 2. 波动性因子 (Volatility Factors)

波动性因子衡量价格波动幅度，用于风险管理、止损设置和识别市场状态。

### 2.1 ATR (Average True Range)（平均真实波幅）

**作用：** 最重要的波动率指标，用于动态止损、仓位管理、识别趋势强度。波动率是风控的核心。

**计算公式：**
```
TR_t = Max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)
ATR_t = EMA_n(TR_t)
```

**参数：** n = 14

**使用说明：**
- 止损距离：2-3倍ATR
- ATR扩大：趋势启动或加速
- ATR缩小：震荡市，趋势可能结束
- 用ATR_Percent = ATR/Close进行跨品种比较

---

### 2.2 Bollinger_Bands（布林带）

**作用：** 识别超买超卖，判断波动率扩张/收缩，提供动态支撑阻力位。

**计算公式：**
```
BB_Middle_t = MA_n(C_t)
BB_Std_t = Std_n(C_t)
BB_Upper_t = BB_Middle_t + k × BB_Std_t
BB_Lower_t = BB_Middle_t - k × BB_Std_t

BB_Width_t = (BB_Upper_t - BB_Lower_t) / BB_Middle_t
%B_t = (C_t - BB_Lower_t) / (BB_Upper_t - BB_Lower_t)
```

**参数：** n = 20, k = 2

**使用说明：**
- %B > 1：突破上轨，超买或趋势启动
- %B < 0：突破下轨，超卖或趋势启动
- BB_Width收缩（喇叭口收窄）：蓄势待发
- BB_Width扩张：趋势启动，波动率增加
- 中轨作为趋势判断线

---

### 2.3 Historical_Volatility（历史波动率）

**作用：** 衡量价格波动的标准差，用于期权定价、风险预算、市场状态分类。

**计算公式：**
```
Return_t = ln(C_t / C_{t-1})
HV_t = Std_n(Return_t) × sqrt(252 × 1440/k) × 100%
```

其中k为K线周期（分钟），对于1分钟线：k=1

**参数：** n = 20

**使用说明：**
- HV < 20%：低波环境，适合卖出期权
- HV > 40%：高波环境，适合趋势策略
- HV突增：市场状态转变，风险加剧

---

## 3. 动量因子 (Momentum Factors)

动量因子捕捉价格运动的速度和方向，是趋势跟踪和反转策略的核心。

### 3.1 RSI (Relative Strength Index)（相对强弱指标）

**作用：** 最经典的超买超卖指标，识别反转时机，判断价格强弱，发现背离信号。

**计算公式：**
```
Up_t = Max(C_t - C_{t-1}, 0)
Down_t = Max(C_{t-1} - C_t, 0)

EMA_Up_t = EMA_n(Up_t)
EMA_Down_t = EMA_n(Down_t)

RS_t = EMA_Up_t / EMA_Down_t
RSI_t = 100 - 100 / (1 + RS_t)
```

**参数：** n = 14

**使用说明：**
- RSI > 70：超买区，关注做空机会
- RSI < 30：超卖区，关注做多机会
- RSI > 80 或 < 20：极端超买超卖
- 背离信号：
  - 顶背离：价格创新高，RSI不创新高→看跌
  - 底背离：价格创新低，RSI不创新低→看涨
- 强势市场：RSI在40-80区间震荡
- 弱势市场：RSI在20-60区间震荡

---

### 3.2 MACD（异同移动平均线）**[趋势]**

**作用：** 最流行的趋势跟踪指标，判断趋势方向、强度和转折点，产生明确的买卖信号。

**计算公式：**
```
EMA_fast_t = EMA_12(C_t)
EMA_slow_t = EMA_26(C_t)

MACD_t = EMA_fast_t - EMA_slow_t
MACD_Signal_t = EMA_9(MACD_t)
MACD_Hist_t = MACD_t - MACD_Signal_t
```

**使用说明：**
- **金叉（买入信号）：** MACD上穿Signal线
- **死叉（卖出信号）：** MACD下穿Signal线
- **柱状图分析：**
  - Histogram > 0 且扩大：上涨动能增强
  - Histogram < 0 且扩大：下跌动能增强
  - Histogram收敛：动能衰减，警惕反转
- **零轴分析：**
  - MACD > 0：中期多头市场
  - MACD < 0：中期空头市场
- **背离信号：** 价格与MACD方向不一致时预示反转

---

### 3.3 Stochastic（随机指标）

**作用：** 衡量价格在N期范围内的相对位置，敏感的超买超卖指标，适合震荡市。

**计算公式：**
```
Lowest_Low_n = Min_n(L_t)
Highest_High_n = Max_n(H_t)

%K_t = (C_t - Lowest_Low_n) / (Highest_High_n - Lowest_Low_n) × 100
%D_t = MA_3(%K_t)
```

**参数：** n = 14, m = 3

**使用说明：**
- %K > 80：超买区
- %K < 20：超卖区
- %K上穿%D：买入信号
- %K下穿%D：卖出信号
- 背离信号效果显著
- 适合震荡市，趋势市容易产生虚假信号

---

### 3.4 ADX (Average Directional Index)（平均趋向指标）**[趋势]**

**作用：** 衡量趋势强度的标准指标，帮助识别趋势市/震荡市，决定策略类型。

**计算公式：**
```
# 步骤1：计算方向运动
+DM_t = H_t - H_{t-1}  if H_t - H_{t-1} > L_{t-1} - L_t else 0
-DM_t = L_{t-1} - L_t  if L_{t-1} - L_t > H_t - H_{t-1} else 0

# 步骤2：平滑并计算方向指标
+DI_t = (EMA_n(+DM_t) / EMA_n(TR_t)) × 100
-DI_t = (EMA_n(-DM_t) / EMA_n(TR_t)) × 100

# 步骤3：计算ADX
DX_t = |+DI_t - -DI_t| / (+DI_t + -DI_t) × 100
ADX_t = EMA_n(DX_t)
```

**参数：** n = 14

**使用说明：**
- **ADX < 20：** 弱趋势/震荡市，使用均值回归策略
- **ADX 20-25：** 趋势形成中
- **ADX > 25：** 强趋势市，使用趋势跟踪策略
- **ADX > 40：** 极强趋势
- **+DI > -DI：** 上升趋势主导
- **-DI > +DI：** 下降趋势主导
- **ADX上升：** 趋势加强
- **ADX下降：** 趋势减弱

---

### 3.5 ROC (Rate of Change)（变化率）

**作用：** 简单直接的动量指标，衡量价格变化速度，识别超买超卖和动量发散。

**计算公式：**
```
ROC_t = (C_t - C_{t-n}) / C_{t-n} × 100%
```

**参数：** n = 10（短期）, n = 20（中期）

**使用说明：**
- ROC > 0：上涨动量
- ROC < 0：下跌动量
- ROC极值：超买超卖信号
- ROC穿越零线：动量转换
- 多周期ROC组合使用效果更好

---

## 4. 趋势与均线因子 (Trend & Moving Average Factors)

趋势因子是量化交易的基石，用于识别和跟踪价格的主要方向。

### 4.1 SMA (Simple Moving Average)（简单移动平均）**[趋势]**

**作用：** 最基础的趋势指标，平滑价格噪音，识别趋势方向，提供动态支撑阻力。

**计算公式：**
```
SMA_n(C_t) = (1/n) × Σ(C_i),  i ∈ [t-n+1, t]
```

**常用参数：**
- n = 5：超短期趋势
- n = 10：短期趋势
- n = 20：短中期趋势
- n = 50：中期趋势
- n = 200：长期趋势

**使用说明：**
- 价格 > MA：上升趋势
- 价格 < MA：下降趋势
- MA向上：趋势向上
- MA向下：趋势向下
- MA作为动态支撑/阻力位

---

### 4.2 EMA (Exponential Moving Average)（指数移动平均）**[趋势]**

**作用：** 对近期价格赋予更高权重，反应更灵敏，适合快速市场和短线交易。

**计算公式：**
```
α = 2 / (n + 1)
EMA_t = α × C_t + (1 - α) × EMA_{t-1}
```

**常用参数：**
- n = 12, 26：MACD计算
- n = 20：短期趋势
- n = 50：中期趋势

**使用说明：**
- 比SMA更快响应价格变化
- 更适合趋势跟踪
- 常用于构建多均线系统

---

### 4.3 MA_Cross（均线交叉）**[趋势]**

**作用：** 经典的趋势转折信号，金叉死叉是最广为人知的交易信号。

**计算公式：**
```
MA_Cross_t = MA_short(C_t) - MA_long(C_t)
```

**常用组合：**
- 5日/10日：超短期
- 5日/20日：短期
- 10日/30日：中短期
- 20日/60日：中期
- 50日/200日：长期（黄金交叉/死亡交叉）

**使用说明：**
- **金叉（买入）：** 短期均线上穿长期均线
- **死叉（卖出）：** 短期均线下穿长期均线
- 配合成交量确认：放量金叉更可靠
- 震荡市易产生假信号，需配合ADX使用

---

### 4.4 Price_MA_Distance（价格偏离均线）

**作用：** 衡量价格偏离趋势的程度，识别超买超卖和均值回归机会。

**计算公式：**
```
Price_MA_Dist_t = (C_t - MA_n(C_t)) / MA_n(C_t) × 100%
```

**参数：** n = 20

**使用说明：**
- |Distance| > 5%：显著偏离，可能回归
- |Distance| > 10%：极端偏离，高概率回调
- 趋势市：偏离度可能持续较大
- 震荡市：偏离后快速回归

---

### 4.5 MA_Slope（均线斜率）**[趋势]**

**作用：** 量化趋势的方向和强度，判断趋势的加速或减速。

**计算公式：**
```
MA_Slope_t = (MA_n(C_t) - MA_n(C_{t-m})) / MA_n(C_{t-m}) × 100%
```

**参数：** n = 20, m = 5

**使用说明：**
- Slope > 0：上升趋势
- Slope < 0：下降趋势
- |Slope|增大：趋势加速
- |Slope|减小：趋势减速，可能反转
- Slope接近0：震荡市

---

## 5. 市场强度因子 (Market Strength Factors)

市场强度因子评估多空力量对比和资金流向。

### 5.1 CMF (Chaikin Money Flow)（蔡金资金流）**[趋势]**

**作用：** 结合价格位置和成交量的资金流指标，判断买卖压力强度。

**计算公式：**
```
MF_Multiplier_t = ((C_t - L_t) - (H_t - C_t)) / (H_t - L_t)
MF_Volume_t = MF_Multiplier_t × V_t

CMF_t = Σ(MF_Volume_i) / Σ(V_i),  i ∈ [t-n+1, t]
```

**参数：** n = 20

**使用说明：**
- CMF > 0：买盘压力主导，资金流入
- CMF < 0：卖盘压力主导，资金流出
- CMF > 0.25：强烈买压
- CMF < -0.25：强烈卖压
- CMF背离：价格与资金流方向不一致

---

### 5.2 Force_Index（力量指数）

**作用：** 综合价格变化和成交量的力量指标，识别趋势的真实强度。

**计算公式：**
```
Force_Index_t = (C_t - C_{t-1}) × V_t
Force_Index_EMA_t = EMA_13(Force_Index_t)
```

**使用说明：**
- Force_Index > 0：买方力量强
- Force_Index < 0：卖方力量强
- 极值点：短期反转信号
- 配合趋势指标使用

---

## 6. 价格形态因子 (Price Pattern Factors)

价格形态因子从K线结构中提取信息，识别市场情绪和可能的转折。

### 6.1 Price_Range_Position（价格区间位置）

**作用：** 收盘价在当日高低价区间的位置，反映日内多空力量对比。

**计算公式：**
```
Price_Range_Pos_t = (C_t - L_t) / (H_t - L_t)
```

**使用说明：**
- 接近1：收在最高点，强势
- 接近0：收在最低点，弱势
- 接近0.5：多空平衡
- 结合趋势判断K线强弱

---

### 6.2 Candle_Body_Ratio（实体比例）

**作用：** K线实体相对影线的比例，判断多空确定性程度。

**计算公式：**
```
Candle_Body_Ratio_t = |C_t - O_t| / (H_t - L_t)
```

**使用说明：**
- 接近1：大实体，方向确定性强
- 接近0：十字星，犹豫不决
- 配合趋势判断K线可靠性

---

## 7. 统计因子 (Statistical Factors)

统计因子从概率角度评估价格状态。

### 7.1 Z_Score（标准分数）

**作用：** 价格相对历史均值的标准差倍数，识别极端价格和均值回归机会。

**计算公式：**
```
Z_Score_t = (C_t - MA_n(C_t)) / Std_n(C_t)
```

**参数：** n = 20

**使用说明：**
- |Z| > 2：价格异常偏离（95%置信度）
- |Z| > 3：极端偏离（99.7%置信度）
- 用于均值回归策略的入场信号
- 趋势市慎用

---

### 7.2 Percentile_Rank（百分位排名）

**作用：** 当前价格在历史分布中的相对位置。

**计算公式：**
```
Percentile_Rank_t = Rank(C_t in [C_{t-n+1}...C_t]) / n × 100%
```

**参数：** n = 100

**使用说明：**
- > 90%：接近历史高位
- < 10%：接近历史低位
- 配合其他指标判断超买超卖

---

## 8. 趋势因子总结

以下因子专门用于趋势识别和跟踪，在构建趋势策略时优先考虑：

### 8.1 强趋势因子（核心）
这些是最可靠的趋势判断指标：

| 因子 | 类型 | 主要用途 | 典型参数 |
|------|------|----------|----------|
| **MACD** | 动量 | 趋势方向与转折点 | 12/26/9 |
| **ADX** | 趋势强度 | 判断趋势市/震荡市 | 14 |
| **MA_Cross** | 趋势 | 金叉死叉信号 | 5/20, 50/200 |
| **EMA** | 趋势 | 趋势方向与支撑阻力 | 20, 50 |
| **MA_Slope** | 趋势 | 趋势强度量化 | 20 |

**组合使用示例：**
```
趋势确认 = (ADX > 25) & (MACD > MACD_Signal) & (Price > EMA_50)
```

---

### 8.2 趋势确认因子
用于验证趋势的真实性：

| 因子 | 验证作用 |
|------|----------|
| **OBV** | 成交量确认趋势 |
| **CMF** | 资金流确认趋势 |
| **Volume_Ratio** | 放量确认突破 |
| **VWAP** | 日内趋势基准 |

**使用方法：**
- 价格突破 + OBV同步突破 = 有效突破
- 价格新高 + OBV不创新高 = 背离警告

---

### 8.3 趋势强度判断
量化趋势的力度：

- **ADX值大小：** 直接量化趋势强度
- **ATR变化：** 波动率扩大表示趋势加强
- **MA_Slope绝对值：** 均线斜率的陡峭程度
- **MACD_Histogram幅度：** 动量的强弱

---

### 8.4 趋势反转预警因子
识别趋势可能结束的信号：

| 信号 | 含义 |
|------|------|
| **RSI极值（>70或<30）** | 超买超卖 |
| **MACD背离** | 价格与动量不一致 |
| **MACD_Histogram收敛** | 动量衰减 |
| **ADX下降** | 趋势强度减弱 |
| **Volume萎缩** | 参与度降低 |

---

## 9. 因子组合策略

### 9.1 趋势跟踪策略

**入场条件（做多）：**
```python
# 1. 趋势确认
trend_confirm = (ADX > 25) & (Price > EMA_20) & (EMA_20 > EMA_50)

# 2. 动量确认
momentum_confirm = (MACD > MACD_Signal) & (RSI > 50)

# 3. 成交量确认
volume_confirm = (Volume_Ratio > 1.2) & (OBV_trend_up)

# 综合入场
entry_long = trend_confirm & momentum_confirm & volume_confirm
```

**止损设置：**
```python
stop_loss = Entry_Price - 2 * ATR
```

**出场信号：**
```python
exit_long = (MACD < MACD_Signal) | (Price < EMA_20) | (RSI < 30)
```

---

### 9.2 均值回归策略

**入场条件（做多）：**
```python
# 1. 震荡市确认
range_market = (ADX < 20)

# 2. 超卖确认
oversold = (RSI < 30) & (Bollinger_%B < 0) & (Z_Score < -2)

# 3. 价格偏离
deviation = (Price_MA_Distance < -5%)

# 综合入场
entry_long = range_market & oversold & deviation
```

**止损设置：**
```python
stop_loss = Entry_Price - 1.5 * ATR
```

**止盈设置：**
```python
take_profit = (RSI > 70) | (Bollinger_%B > 1) | (Price_MA_Distance > 0)
```

---

### 9.3 突破策略

**入场条件（做多）：**
```python
# 1. 价格突破
price_breakout = (Close > Max_20(High)) & (Close > Bollinger_Upper)

# 2. 放量确认
volume_breakout = (Volume_Ratio > 1.5)

# 3. 趋势启动
trend_start = (Bollinger_Width < 前期均值) & (ADX开始上升)

# 综合入场
entry_long = price_breakout & volume_breakout & trend_start
```

**止损设置：**
```python
stop_loss = Breakout_Level - 1 * ATR
```

---

## 10. 因子计算最佳实践

### 10.1 数据预处理

```python
import pandas as pd
import numpy as np

# 1. 异常值处理（Winsorize）
def winsorize(series, lower=0.01, upper=0.99):
    return series.clip(
        lower=series.quantile(lower),
        upper=series.quantile(upper)
    )

# 2. 标准化（Z-Score）
def standardize(series):
    return (series - series.mean()) / series.std()

# 3. 归一化（Min-Max）
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())
```

---

### 10.2 因子计算示例

```python
# 假设df有列：['open', 'high', 'low', 'close', 'volume']

# === 1. 基础因子 ===
df['return'] = df['close'].pct_change()
df['log_return'] = np.log(df['close'] / df['close'].shift(1))

# === 2. 流动性因子 ===
df['volume_ma20'] = df['volume'].rolling(20).mean()
df['volume_ratio'] = df['volume'] / df['volume_ma20']

# VWAP
df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
df['vwap_distance'] = (df['close'] - df['vwap']) / df['vwap'] * 100

# OBV
df['obv'] = (np.sign(df['return']) * df['volume']).cumsum()

# === 3. 波动性因子 ===
# ATR
df['tr'] = np.maximum(
    df['high'] - df['low'],
    np.maximum(
        abs(df['high'] - df['close'].shift(1)),
        abs(df['low'] - df['close'].shift(1))
    )
)
df['atr'] = df['tr'].ewm(span=14, adjust=False).mean()

# 布林带
df['bb_mid'] = df['close'].rolling(20).mean()
df['bb_std'] = df['close'].rolling(20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
df['bb_pctb'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

# 历史波动率（年化）
df['hv'] = df['log_return'].rolling(20).std() * np.sqrt(252 * 1440) * 100

# === 4. 动量因子 ===
# RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
loss = -delta.where(delta < 0, 0).ewm(span=14, adjust=False).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# MACD
df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = df['ema12'] - df['ema26']
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
df['macd_hist'] = df['macd'] - df['macd_signal']

# Stochastic
low_14 = df['low'].rolling(14).min()
high_14 = df['high'].rolling(14).max()
df['stoch_k'] = (df['close'] - low_14) / (high_14 - low_14) * 100
df['stoch_d'] = df['stoch_k'].rolling(3).mean()

# ROC
df['roc'] = df['close'].pct_change(10) * 100

# === 5. 趋势因子 ===
df['sma5'] = df['close'].rolling(5).mean()
df['sma20'] = df['close'].rolling(20).mean()
df['sma50'] = df['close'].rolling(50).mean()
df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()

df['ma_cross'] = df['sma5'] - df['sma20']
df['price_ma_dist'] = (df['close'] - df['sma20']) / df['sma20'] * 100
df['ma_slope'] = df['sma20'].pct_change(5) * 100

# === 6. 统计因子 ===
df['z_score'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
df['percentile'] = df['close'].rolling(100).apply(lambda x: pd.Series(x).rank().iloc[-1] / len(x) * 100)

# === 7. 价格形态 ===
df['price_range_pos'] = (df['close'] - df['low']) / (df['high'] - df['low'])
df['body_ratio'] = abs(df['close'] - df['open']) / (df['high'] - df['low'])
```

---

### 10.3 ADX计算（完整实现）

```python
def calculate_adx(df, period=14):
    """计算ADX及DI指标"""

    # 1. 计算TR
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )

    # 2. 计算+DM和-DM
    df['high_diff'] = df['high'] - df['high'].shift(1)
    df['low_diff'] = df['low'].shift(1) - df['low']

    df['plus_dm'] = np.where(
        (df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0),
        df['high_diff'],
        0
    )

    df['minus_dm'] = np.where(
        (df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0),
        df['low_diff'],
        0
    )

    # 3. 平滑TR、+DM、-DM
    df['tr_smooth'] = df['tr'].ewm(span=period, adjust=False).mean()
    df['plus_dm_smooth'] = df['plus_dm'].ewm(span=period, adjust=False).mean()
    df['minus_dm_smooth'] = df['minus_dm'].ewm(span=period, adjust=False).mean()

    # 4. 计算+DI和-DI
    df['plus_di'] = (df['plus_dm_smooth'] / df['tr_smooth']) * 100
    df['minus_di'] = (df['minus_dm_smooth'] / df['tr_smooth']) * 100

    # 5. 计算DX和ADX
    df['dx'] = (abs(df['plus_di'] - df['minus_di']) /
                (df['plus_di'] + df['minus_di'])) * 100
    df['adx'] = df['dx'].ewm(span=period, adjust=False).mean()

    return df[['plus_di', 'minus_di', 'adx']]
```

---

### 10.4 CMF计算（完整实现）

```python
def calculate_cmf(df, period=20):
    """计算Chaikin Money Flow"""

    # 1. 计算Money Flow Multiplier
    df['mf_multiplier'] = (
        ((df['close'] - df['low']) - (df['high'] - df['close'])) /
        (df['high'] - df['low'])
    )

    # 处理分母为0的情况
    df['mf_multiplier'] = df['mf_multiplier'].fillna(0)

    # 2. 计算Money Flow Volume
    df['mf_volume'] = df['mf_multiplier'] * df['volume']

    # 3. 计算CMF
    df['cmf'] = (
        df['mf_volume'].rolling(period).sum() /
        df['volume'].rolling(period).sum()
    )

    return df['cmf']
```

---

## 11. 因子验证与评估

### 11.1 因子有效性检验

```python
def calculate_ic(factor, forward_return, method='pearson'):
    """
    计算信息系数（IC）
    factor: 因子值
    forward_return: 未来收益率
    method: 'pearson' or 'spearman'
    """
    return factor.corr(forward_return, method=method)

def calculate_ir(ic_series):
    """
    计算信息比率（IR）
    IR = IC均值 / IC标准差
    """
    return ic_series.mean() / ic_series.std()

# 使用示例
df['forward_return'] = df['close'].pct_change(5).shift(-5)  # 5期后收益率
ic = calculate_ic(df['rsi'], df['forward_return'])
print(f"RSI的IC: {ic:.4f}")
```

---

### 11.2 因子分组回测

```python
def factor_quantile_analysis(df, factor_col, n_quantiles=10):
    """
    因子分组分析
    将因子分为n组，计算各组的平均收益
    """
    # 计算未来收益
    df['forward_return'] = df['close'].pct_change(1).shift(-1)

    # 因子分组
    df['quantile'] = pd.qcut(df[factor_col], n_quantiles, labels=False, duplicates='drop')

    # 各组收益统计
    group_stats = df.groupby('quantile').agg({
        'forward_return': ['mean', 'std', 'count'],
        factor_col: 'mean'
    })

    return group_stats
```

---

## 12. 实战要点

### 12.1 因子使用原则

1. **多因子组合：** 单一因子容易失效，至少组合3-5个不同类型的因子
2. **市场状态适配：** 根据ADX判断使用趋势策略还是均值回归策略
3. **时间周期匹配：** 因子的计算周期应与交易周期匹配
4. **样本外验证：** 必须在未见过的数据上测试因子效果
5. **定期重估：** 因子有效性会衰减，需定期评估和调整

---

### 12.2 常见陷阱

1. **过拟合：** 过多参数优化导致样本内优秀、样本外失效
2. **未来函数：** 使用了未来数据，回测结果失真
3. **幸存者偏差：** 只用存活标的的数据，忽略退市标的
4. **数据窥探：** 反复测试调参，实际上是拟合历史
5. **交易成本忽略：** 未考虑滑点、手续费、冲击成本

---

### 12.3 因子失效的信号

- IC显著下降或变为负值
- IR下降到阈值以下
- 因子分组的单调性消失
- 夏普比率大幅下降
- 回撤显著增加

**应对措施：** 定期（如每月）重新评估因子，及时淘汰失效因子，引入新因子。

---

## 附录：快速查询表

### A. 因子参数速查

| 因子 | 经典参数 | 适用周期 | 更新频率 |
|------|----------|----------|----------|
| RSI | 14 | 所有 | 每Bar |
| MACD | 12/26/9 | 日线以下 | 每Bar |
| ADX | 14 | 所有 | 每Bar |
| ATR | 14 | 所有 | 每Bar |
| 布林带 | 20, 2σ | 所有 | 每Bar |
| Stochastic | 14, 3 | 分钟/小时 | 每Bar |
| MA | 20/50/200 | 根据交易周期 | 每Bar |
| Volume_Ratio | 20 | 所有 | 每Bar |

---

### B. 超买超卖阈值

| 指标 | 超买 | 超卖 | 极端超买 | 极端超卖 |
|------|------|------|----------|----------|
| RSI | 70 | 30 | 80 | 20 |
| Stochastic %K | 80 | 20 | 90 | 10 |
| Bollinger %B | > 1 | < 0 | > 1.2 | < -0.2 |
| Z-Score | > 2 | < -2 | > 3 | < -3 |

---

### C. 趋势强度判断

| ADX值 | 市场状态 | 策略选择 |
|-------|----------|----------|
| < 20 | 无趋势/震荡 | 均值回归、做市 |
| 20-25 | 趋势形成中 | 谨慎跟踪 |
| 25-40 | 强趋势 | 趋势跟踪 |
| > 40 | 极强趋势 | 积极跟踪，警惕过度 |
| 下降中 | 趋势衰竭 | 考虑减仓 |

---

**文档版本：** v3.0
**更新日期：** 2026-01-07
**适用范围：** 分钟级OHLCV数据
**因子数量：** 25个经典因子
**趋势因子：** 8个核心趋势因子

---

**使用建议：**
- 新手先掌握MACD、RSI、均线、ATR这4个最基础的指标
- 进阶后学习ADX判断市场状态，然后根据状态选择策略
- 最后学习OBV、CMF等资金流指标进行趋势确认
- 实盘前务必做充分的回测和模拟盘验证
