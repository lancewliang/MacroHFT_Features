# 特征工程因子目录 v2.0 - 数学公式版

基于OHLCV数据的分钟级特征库，包含所有因子的精确数学计算公式。

**符号约定：**
- O_t, H_t, L_t, C_t, V_t：第t期的开盘价、最高价、最低价、收盘价、成交量
- MA_n(X)：X的n期简单移动平均
- EMA_n(X)：X的n期指数移动平均，α = 2/(n+1)
- Std_n(X)：X的n期标准差
- Max_n(X)、Min_n(X)：X在n期内的最大值、最小值
- Σ：求和符号

---

## 1. 流动性因子 (Liquidity Factors)

流动性因子衡量市场的交易活跃度和价格冲击成本，反映资金进出的难易程度。

### 1.1 基础成交量因子

#### 1.1.1 Volume_Ratio（成交量比率）
衡量当前成交量相对历史平均水平的倍数，识别异常放量。

```
Volume_Ratio_t = V_t / MA_n(V_t)
```

参数：n = 20（建议）

---

#### 1.1.2 Volume_Std（成交量标准差）
衡量成交量的波动程度，反映流动性稳定性。

```
Volume_Std_t = Std_n(V_t)
```

参数：n = 20

---

#### 1.1.3 Volume_MA_Cross（成交量均线交叉）
短期与长期成交量趋势的比较。

```
Volume_MA_Cross_t = MA_short(V_t) / MA_long(V_t)
```

参数：short = 5, long = 20（建议）

---

#### 1.1.4 Cumulative_Volume（累计成交量）
时间窗口内的总成交量。

```
Cumulative_Volume_t = Σ(V_{t-n+1} to V_t)
```

参数：n = 60（60分钟累计）

---

### 1.2 价量关系因子

#### 1.2.1 Price_Volume_Correlation（价量相关性）
价格变化与成交量的滚动相关系数。

```
Return_t = (C_t - C_{t-1}) / C_{t-1}
PV_Corr_t = Corr_n(Return_t, V_t)
```

参数：n = 20

---

#### 1.2.2 VWAP（成交量加权平均价）
反映平均成交成本。

```
TP_t = (H_t + L_t + C_t) / 3
VWAP_t = Σ(TP_i × V_i) / Σ(V_i),  i ∈ [t-n+1, t]
```

参数：n = 60（日内从开盘到当前）或滚动窗口

---

#### 1.2.3 VWAP_Distance（VWAP偏离度）
当前价格相对VWAP的偏离百分比。

```
VWAP_Distance_t = (C_t - VWAP_t) / VWAP_t × 100%
```

---

#### 1.2.4 Volume_Price_Trend (VPT)（量价趋势）
累计的价格变化率加权成交量。

```
VPT_t = VPT_{t-1} + V_t × (C_t - C_{t-1}) / C_{t-1}
```

初始值：VPT_0 = 0

---

### 1.3 买卖压力因子

#### 1.3.1 Money_Flow（资金流）
简单的资金流量指标。

```
Money_Flow_t = C_t × V_t
```

---

#### 1.3.2 Money_Flow_Ratio（资金流比率）
多空力量对比。

```
Positive_MF = Σ(C_i × V_i), where C_i > C_{i-1}, i ∈ [t-n+1, t]
Negative_MF = Σ(C_i × V_i), where C_i < C_{i-1}, i ∈ [t-n+1, t]

MF_Ratio_t = Positive_MF / Negative_MF
```

参数：n = 14

---

#### 1.3.3 Ease_of_Movement (EMV)（移动便利度）
单位成交量引起的价格变动幅度。

```
Distance_t = (H_t + L_t) / 2 - (H_{t-1} + L_{t-1}) / 2
Box_Ratio_t = (V_t / 10^8) / (H_t - L_t)
EMV_t = Distance_t / Box_Ratio_t
```

可以取EMV的n期移动平均平滑：`EMV_MA_t = MA_n(EMV_t)`

参数：n = 14

---

#### 1.3.4 Force_Index（力量指数）
价格变动幅度与成交量的乘积。

```
Force_Index_t = (C_t - C_{t-1}) × V_t
```

可以取n期EMA平滑：`Force_Index_EMA_t = EMA_n(Force_Index_t)`

参数：n = 13

---

## 2. 波动性因子 (Volatility Factors)

### 2.1 True_Range (TR)（真实波幅）
考虑跳空的真实价格波动范围。

```
TR_t = Max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)
```

---

### 2.2 ATR (Average True Range)（平均真实波幅）
标准化的波动率指标。

```
ATR_t = EMA_n(TR_t)
或
ATR_t = (ATR_{t-1} × (n-1) + TR_t) / n
```

参数：n = 14（经典）

---

### 2.3 ATR_Percent（ATR百分比）
标准化的波动率，便于跨品种比较。

```
ATR_Percent_t = ATR_t / C_t × 100%
```

---

### 2.4 High_Low_Range（高低价区间）
日内波动幅度百分比。

```
HL_Range_t = (H_t - L_t) / C_t × 100%
```

---

### 2.5 Return_Std（收益率标准差）
收益率的历史波动性。

```
Return_t = (C_t - C_{t-1}) / C_{t-1}
Return_Std_t = Std_n(Return_t)
```

参数：n = 20

---

### 2.6 Parkinson_Volatility（Parkinson波动率）
基于高低价的波动率估计，效率高于收盘价波动率。

```
Parkinson_Vol_t = sqrt(1/(4×n×ln(2)) × Σ(ln(H_i/L_i))^2)
i ∈ [t-n+1, t]
```

参数：n = 20

---

### 2.7 Garman_Klass_Volatility（Garman-Klass波动率）
利用OHLC的波动率估计，比Parkinson更准确。

```
GK_Vol_t = sqrt(1/n × Σ[0.5×(ln(H_i/L_i))^2 - (2×ln(2)-1)×(ln(C_i/O_i))^2])
i ∈ [t-n+1, t]
```

参数：n = 20

---

### 2.8 Yang_Zhang_Volatility（Yang-Zhang波动率）
综合隔夜和日内波动的估计，考虑开盘跳空。

```
O_Vol = Std_n(ln(O_t/C_{t-1}))  # 隔夜波动
C_Vol = Std_n(ln(C_t/O_t))      # 日内收盘波动

RS_Vol = sqrt(1/n × Σ[(ln(H_i/C_i))×(ln(H_i/O_i)) + (ln(L_i/C_i))×(ln(L_i/O_i))])

k = 0.34/(1.34 + (n+1)/(n-1))

YZ_Vol_t = sqrt(O_Vol^2 + k×C_Vol^2 + (1-k)×RS_Vol^2)
```

参数：n = 20

---

### 2.9 Bollinger_Band_Width（布林带宽度）
价格通道的宽度，衡量波动率。

```
BB_Middle_t = MA_n(C_t)
BB_Std_t = Std_n(C_t)
BB_Upper_t = BB_Middle_t + k × BB_Std_t
BB_Lower_t = BB_Middle_t - k × BB_Std_t

BB_Width_t = (BB_Upper_t - BB_Lower_t) / BB_Middle_t × 100%
```

参数：n = 20, k = 2

---

### 2.10 Bollinger_Percent_B（布林带%B）
价格在布林带中的相对位置。

```
%B_t = (C_t - BB_Lower_t) / (BB_Upper_t - BB_Lower_t)
```

%B > 1：价格在上轨之上
%B < 0：价格在下轨之下
%B = 0.5：价格在中轨

---

### 2.11 Keltner_Channel_Width（肯特纳通道宽度）
基于ATR的趋势通道宽度。

```
KC_Middle_t = EMA_n(C_t)
KC_Upper_t = KC_Middle_t + m × ATR_t
KC_Lower_t = KC_Middle_t - m × ATR_t

KC_Width_t = (KC_Upper_t - KC_Lower_t) / KC_Middle_t × 100%
```

参数：n = 20, m = 2

---

### 2.12 Historical_Volatility (HV)（历史波动率）
年化的历史波动率。

```
Return_t = ln(C_t / C_{t-1})
HV_t = Std_n(Return_t) × sqrt(252 × 1440/k)
```

其中k为K线周期（分钟），252为年交易日数
对于1分钟K线：k=1
对于5分钟K线：k=5

参数：n = 20

---

### 2.13 Volatility_Ratio（波动率比率）
识别波动率的突变。

```
Vol_Short_t = Std_short(Return_t)
Vol_Long_t = Std_long(Return_t)

Volatility_Ratio_t = Vol_Short_t / Vol_Long_t
```

参数：short = 5, long = 20

---

### 2.14 Realized_Range（实际波动区间）
时间段内的最大波动幅度。

```
Realized_Range_t = (Max_n(H_t) - Min_n(L_t)) / O_{t-n+1} × 100%
```

参数：n = 60

---

## 3. 动量因子 (Momentum Factors)

### 3.1 ROC (Rate of Change)（变化率）
价格变化的百分比。

```
ROC_t = (C_t - C_{t-n}) / C_{t-n} × 100%
```

参数：n = 10

---

### 3.2 Momentum（动量）
价格的绝对变化。

```
Momentum_t = C_t - C_{t-n}
```

参数：n = 10

---

### 3.3 Price_Acceleration（价格加速度）
动量的变化率，捕捉加速/减速。

```
ROC_t = (C_t - C_{t-n}) / C_{t-n}
Price_Accel_t = ROC_t - ROC_{t-1}
```

或使用二阶差分：
```
Price_Accel_t = (C_t - C_{t-1}) - (C_{t-1} - C_{t-2})
```

---

### 3.4 RSI (Relative Strength Index)（相对强弱指标）
超买超卖指标。

```
Up_t = Max(C_t - C_{t-1}, 0)
Down_t = Max(C_{t-1} - C_t, 0)

EMA_Up_t = EMA_n(Up_t)
EMA_Down_t = EMA_n(Down_t)

RS_t = EMA_Up_t / EMA_Down_t

RSI_t = 100 - 100 / (1 + RS_t)
```

参数：n = 14（经典）

RSI > 70：超买区域
RSI < 30：超卖区域

---

### 3.5 Stochastic_K（随机指标K值）
价格在N期范围内的相对位置。

```
Lowest_Low_n = Min_n(L_t)
Highest_High_n = Max_n(H_t)

%K_t = (C_t - Lowest_Low_n) / (Highest_High_n - Lowest_Low_n) × 100
```

参数：n = 14

---

### 3.6 Stochastic_D（随机指标D值）
K值的移动平均，产生交易信号。

```
%D_t = MA_m(%K_t)
```

参数：m = 3

---

### 3.7 Williams_%R（威廉指标）
与Stochastic相反的超买超卖指标。

```
Highest_High_n = Max_n(H_t)
Lowest_Low_n = Min_n(L_t)

%R_t = (Highest_High_n - C_t) / (Highest_High_n - Lowest_Low_n) × (-100)
```

参数：n = 14

%R > -20：超买区域
%R < -80：超卖区域

---

### 3.8 ADX (Average Directional Index)（平均趋向指标）
衡量趋势强度（不判断方向）。

**步骤1：计算+DM和-DM**
```
+DM_t = H_t - H_{t-1}  if H_t - H_{t-1} > L_{t-1} - L_t else 0
-DM_t = L_{t-1} - L_t  if L_{t-1} - L_t > H_t - H_{t-1} else 0
```

**步骤2：平滑DM和TR**
```
+DM_smooth_t = EMA_n(+DM_t)
-DM_smooth_t = EMA_n(-DM_t)
TR_smooth_t = EMA_n(TR_t)
```

**步骤3：计算DI**
```
+DI_t = (+DM_smooth_t / TR_smooth_t) × 100
-DI_t = (-DM_smooth_t / TR_smooth_t) × 100
```

**步骤4：计算DX和ADX**
```
DX_t = |+DI_t - -DI_t| / (+DI_t + -DI_t) × 100

ADX_t = EMA_n(DX_t)
```

参数：n = 14

ADX < 20：弱趋势/震荡市
ADX > 25：强趋势市
ADX > 50：极强趋势

---

### 3.9 +DI (Positive Directional Indicator)（正向指标）
上涨动能，见ADX计算公式中的+DI_t。

---

### 3.10 -DI (Negative Directional Indicator)（负向指标）
下跌动能，见ADX计算公式中的-DI_t。

---

### 3.11 Mass_Index（质量指标）
识别趋势反转。

```
Single_EMA_t = EMA_9(H_t - L_t)
Double_EMA_t = EMA_9(Single_EMA_t)

ER_t = Single_EMA_t / Double_EMA_t

Mass_Index_t = Σ(ER_i),  i ∈ [t-24, t]
```

Mass_Index > 27：可能反转
Mass_Index < 26.5：反转确认

---

### 3.12 MACD（异同移动平均线）
趋势跟踪和动量指标。

```
EMA_fast_t = EMA_12(C_t)
EMA_slow_t = EMA_26(C_t)

MACD_t = EMA_fast_t - EMA_slow_t
```

参数：fast = 12, slow = 26

---

### 3.13 MACD_Signal（MACD信号线）
MACD的平滑线，产生买卖信号。

```
MACD_Signal_t = EMA_9(MACD_t)
```

买入信号：MACD上穿Signal
卖出信号：MACD下穿Signal

---

### 3.14 MACD_Histogram（MACD柱状图）
MACD与信号线的差值，衡量动量加速度。

```
MACD_Hist_t = MACD_t - MACD_Signal_t
```

柱状图由负转正：看涨
柱状图由正转负：看跌
柱状图收敛：动能减弱

---

### 3.15 CCI (Commodity Channel Index)（顺势指标）
衡量价格偏离统计平均值的程度。

```
TP_t = (H_t + L_t + C_t) / 3
MA_TP_t = MA_n(TP_t)
MD_t = (1/n) × Σ|TP_i - MA_TP_t|,  i ∈ [t-n+1, t]

CCI_t = (TP_t - MA_TP_t) / (0.015 × MD_t)
```

参数：n = 20

CCI > 100：超买
CCI < -100：超卖

---

### 3.16 Ultimate_Oscillator（终极振荡器）
多时间周期的综合动量指标。

```
BP_t = C_t - Min(L_t, C_{t-1})
TR_t = Max(H_t, C_{t-1}) - Min(L_t, C_{t-1})

Avg7_t = Σ(BP_i) / Σ(TR_i),  i ∈ [t-6, t]
Avg14_t = Σ(BP_i) / Σ(TR_i),  i ∈ [t-13, t]
Avg28_t = Σ(BP_i) / Σ(TR_i),  i ∈ [t-27, t]

UO_t = 100 × (4×Avg7_t + 2×Avg14_t + Avg28_t) / 7
```

UO > 70：超买
UO < 30：超卖

---

## 4. 时序因子 (Time Series Factors)

### 4.1 SMA (Simple Moving Average)（简单移动平均）
最基础的趋势指标。

```
SMA_n(C_t) = (1/n) × Σ(C_i),  i ∈ [t-n+1, t]
```

常用参数：n = 5, 10, 20, 50, 200

---

### 4.2 EMA (Exponential Moving Average)（指数移动平均）
对近期价格赋予更高权重。

```
α = 2 / (n + 1)
EMA_t = α × C_t + (1 - α) × EMA_{t-1}
```

或初始化：`EMA_n = SMA_n`，然后递归计算

常用参数：n = 12, 26, 50, 200

---

### 4.3 WMA (Weighted Moving Average)（加权移动平均）
线性递减权重。

```
WMA_t = Σ(w_i × C_{t-i+1}) / Σ(w_i)
其中 w_i = n - i + 1,  i ∈ [1, n]
```

参数：n = 10

---

### 4.4 DEMA (Double EMA)（双重指数移动平均）
减少滞后的快速均线。

```
EMA1_t = EMA_n(C_t)
EMA2_t = EMA_n(EMA1_t)

DEMA_t = 2 × EMA1_t - EMA2_t
```

参数：n = 20

---

### 4.5 TEMA (Triple EMA)（三重指数移动平均）
进一步减少滞后。

```
EMA1_t = EMA_n(C_t)
EMA2_t = EMA_n(EMA1_t)
EMA3_t = EMA_n(EMA2_t)

TEMA_t = 3 × EMA1_t - 3 × EMA2_t + EMA3_t
```

参数：n = 20

---

### 4.6 HMA (Hull Moving Average)（赫尔移动平均）
平滑且低滞后的均线。

```
Half_WMA_t = WMA_{n/2}(C_t)
Full_WMA_t = WMA_n(C_t)
Raw_HMA_t = 2 × Half_WMA_t - Full_WMA_t

HMA_t = WMA_{sqrt(n)}(Raw_HMA_t)
```

参数：n = 16（使用sqrt(n)=4）

---

### 4.7 MA_Cross（均线交叉）
金叉/死叉信号。

```
MA_Cross_t = MA_short(C_t) - MA_long(C_t)
```

MA_Cross > 0 且前一期 < 0：金叉（买入信号）
MA_Cross < 0 且前一期 > 0：死叉（卖出信号）

参数：short = 5, long = 20

---

### 4.8 Price_MA_Distance（价格偏离均线）
价格相对均线的偏离度。

```
Price_MA_Dist_t = (C_t - MA_n(C_t)) / MA_n(C_t) × 100%
```

参数：n = 20

---

### 4.9 MA_Slope（均线斜率）
均线的变化率，判断趋势方向和强度。

```
MA_Slope_t = (MA_n(C_t) - MA_n(C_{t-m})) / MA_n(C_{t-m}) × 100%
```

或使用线性回归斜率：
```
对MA_n在[t-m+1, t]区间进行线性拟合，取斜率
```

参数：n = 20, m = 5

---

### 4.10 MA_Convergence（均线收敛度）
多条均线的收敛/发散程度。

```
MA_5 = MA_5(C_t)
MA_10 = MA_10(C_t)
MA_20 = MA_20(C_t)

MA_Convergence_t = Std([MA_5, MA_10, MA_20]) / Mean([MA_5, MA_10, MA_20])
```

值越小表示越收敛，值越大表示越发散

---

### 4.11 Higher_High（更高高点）
识别上升趋势的价格结构。

```
Higher_High_t = 1  if H_t > Max_{lookback}(H_{t-1}...H_{t-n}) else 0
```

参数：lookback = 5

---

### 4.12 Lower_Low（更低低点）
识别下降趋势的价格结构。

```
Lower_Low_t = 1  if L_t < Min_{lookback}(L_{t-1}...L_{t-n}) else 0
```

参数：lookback = 5

---

### 4.13 Higher_Low（更高低点）
上升趋势的确认信号。

```
定义局部低点：L_t < L_{t-1} 且 L_t < L_{t+1}

Higher_Low_t = 1  if 当前局部低点 > 前一个局部低点 else 0
```

---

### 4.14 Lower_High（更低高点）
下降趋势的确认信号。

```
定义局部高点：H_t > H_{t-1} 且 H_t > H_{t+1}

Lower_High_t = 1  if 当前局部高点 < 前一个局部高点 else 0
```

---

### 4.15 Autocorrelation（自相关系数）
判断价格序列的持续性。

```
Return_t = (C_t - C_{t-1}) / C_{t-1}

Autocorr_lag_k = Corr(Return_t, Return_{t-k})
```

在窗口n内计算k阶自相关：
```
Autocorr_k_t = Corr_n(Return_t, Return_{t-k})
```

参数：n = 50, k = 1

Autocorr > 0：动量效应
Autocorr < 0：反转效应

---

### 4.16 Hurst_Exponent（赫斯特指数）
衡量时间序列的长期记忆性。

**简化计算（R/S方法）：**

```
对于不同的时间跨度τ:
1. 计算平均收益率：Mean_Return_τ = (1/τ)×Σ(Return_i)
2. 计算累计偏差：Y_k = Σ(Return_i - Mean_Return_τ), i ∈ [1, k]
3. 计算范围：R_τ = Max(Y_k) - Min(Y_k)
4. 计算标准差：S_τ = Std(Return_τ)
5. 计算R/S：(R/S)_τ = R_τ / S_τ

对不同τ值（如2,4,8,16,32）计算R/S
使用线性回归拟合：log(R/S) = H × log(τ) + constant
斜率H即为Hurst指数
```

H > 0.5：趋势性（持续）
H = 0.5：随机游走
H < 0.5：均值回归

---

### 4.17 Pivot_Point（枢轴点）
经典的支撑阻力位计算。

```
PP_t = (H_{t-1} + L_{t-1} + C_{t-1}) / 3

R1_t = 2 × PP_t - L_{t-1}
R2_t = PP_t + (H_{t-1} - L_{t-1})
R3_t = H_{t-1} + 2 × (PP_t - L_{t-1})

S1_t = 2 × PP_t - H_{t-1}
S2_t = PP_t - (H_{t-1} - L_{t-1})
S3_t = L_{t-1} - 2 × (H_{t-1} - PP_t)
```

通常使用前一日（或前一个周期）的HLC数据

---

### 4.18 Fractal_High（分形高点）
识别局部高点（Williams Fractal）。

```
Fractal_High_t = 1  if H_t > H_{t-2} 且 H_t > H_{t-1} 且
                        H_t > H_{t+1} 且 H_t > H_{t+2}
                   else 0
```

需要2个确认周期

---

### 4.19 Fractal_Low（分形低点）
识别局部低点。

```
Fractal_Low_t = 1  if L_t < L_{t-2} 且 L_t < L_{t-1} 且
                       L_t < L_{t+1} 且 L_t < L_{t+2}
                  else 0
```

---

## 5. 价格形态因子 (Price Pattern Factors)

### 5.1 Typical_Price（典型价格）
日内平均价格。

```
TP_t = (H_t + L_t + C_t) / 3
```

---

### 5.2 Weighted_Close（加权收盘价）
更重视收盘价的平均价格。

```
WC_t = (H_t + L_t + 2 × C_t) / 4
```

---

### 5.3 Price_Efficiency（价格效率）
价格运动的方向性程度。

```
Price_Efficiency_t = |C_t - O_t| / (H_t - L_t)
```

值越大表示单边行情，值越小表示震荡

---

### 5.4 Candle_Body_Ratio（K线实体比例）
实体相对整体的占比。

```
Candle_Body_Ratio_t = |C_t - O_t| / (H_t - L_t)
```

---

### 5.5 Upper_Shadow（上影线）
上方抛压的度量。

```
Upper_Shadow_t = H_t - Max(O_t, C_t)

Upper_Shadow_Ratio_t = Upper_Shadow_t / (H_t - L_t)
```

---

### 5.6 Lower_Shadow（下影线）
下方支撑的度量。

```
Lower_Shadow_t = Min(O_t, C_t) - L_t

Lower_Shadow_Ratio_t = Lower_Shadow_t / (H_t - L_t)
```

---

### 5.7 Candle_Type（K线类型）
分类K线形态。

```
Body = C_t - O_t

阳线：Body > 0
阴线：Body < 0
十字星：|Body| / (H_t - L_t) < 0.1

大阳线：Body > ATR_t
大阴线：Body < -ATR_t
```

---

### 5.8 Price_Range_Position（价格区间位置）
收盘价在高低价区间的相对位置。

```
Price_Range_Pos_t = (C_t - L_t) / (H_t - L_t)
```

值接近1：收在最高点附近（强势）
值接近0：收在最低点附近（弱势）

---

### 5.9 Open_Close_Relation（开收盘关系）
开盘价与收盘价的相对位置。

```
OC_Relation_t = (C_t - O_t) / O_t × 100%
```

---

### 5.10 Gap（跳空）
相邻K线的跳空程度。

```
Gap_Up_t = Max(O_t - C_{t-1}, 0) / C_{t-1} × 100%
Gap_Down_t = Max(C_{t-1} - O_t, 0) / C_{t-1} × 100%

Gap_t = Gap_Up_t - Gap_Down_t
```

---

## 6. 市场强度因子 (Market Strength Factors)

### 6.1 Bull_Power（多头力量）
多头推动价格上涨的能力。

```
Bull_Power_t = H_t - EMA_13(C_t)
```

---

### 6.2 Bear_Power（空头力量）
空头压制价格的能力。

```
Bear_Power_t = L_t - EMA_13(C_t)
```

---

### 6.3 Elder_Bull_Bear_Power（Elder多空力量）
综合多空力量指标。

```
EMA_t = EMA_13(C_t)
Bull_Power_t = H_t - EMA_t
Bear_Power_t = L_t - EMA_t

Bull_Bear_Power_t = Bull_Power_t + Bear_Power_t
```

---

### 6.4 Accumulation_Distribution（累积派发线）
基于价量关系的资金流向。

```
MF_Multiplier_t = ((C_t - L_t) - (H_t - C_t)) / (H_t - L_t)

MF_Volume_t = MF_Multiplier_t × V_t

AD_t = AD_{t-1} + MF_Volume_t
```

初始值：AD_0 = 0

---

### 6.5 Chaikin_Money_Flow（蔡金资金流）
衡量买卖压力的资金流指标。

```
MF_Multiplier_t = ((C_t - L_t) - (H_t - C_t)) / (H_t - L_t)
MF_Volume_t = MF_Multiplier_t × V_t

CMF_t = Σ(MF_Volume_i) / Σ(V_i),  i ∈ [t-n+1, t]
```

参数：n = 20

CMF > 0：买盘压力
CMF < 0：卖盘压力

---

### 6.6 On_Balance_Volume (OBV)（能量潮）
累积成交量，判断资金流向。

```
OBV_t = OBV_{t-1} + V_t      if C_t > C_{t-1}
OBV_t = OBV_{t-1} - V_t      if C_t < C_{t-1}
OBV_t = OBV_{t-1}            if C_t = C_{t-1}
```

初始值：OBV_0 = 0

---

### 6.7 Price_Volume_Trend_Oscillator（量价趋势振荡器）
VPT的标准化版本。

```
VPT_t = VPT_{t-1} + V_t × (C_t - C_{t-1}) / C_{t-1}

VPT_Oscillator_t = (VPT_t - EMA_n(VPT_t)) / EMA_n(VPT_t) × 100%
```

参数：n = 20

---

## 7. 多周期因子 (Multi-Timeframe Factors)

### 7.1 Multi_Period_Return（多周期收益率）
不同时间跨度的收益率。

```
Return_1m_t = (C_t - C_{t-1}) / C_{t-1}
Return_5m_t = (C_t - C_{t-5}) / C_{t-5}
Return_15m_t = (C_t - C_{t-15}) / C_{t-15}
Return_60m_t = (C_t - C_{t-60}) / C_{t-60}
```

---

### 7.2 Multi_Period_Volume_Ratio（多周期成交量比率）
不同时间跨度的成交量对比。

```
Vol_Ratio_5m_t = MA_5(V_t) / MA_20(V_t)
Vol_Ratio_15m_t = MA_15(V_t) / MA_60(V_t)
```

---

### 7.3 Trend_Alignment（多周期趋势一致性）
多个时间周期的趋势方向是否一致。

```
Trend_5 = Sign(MA_5(C_t) - MA_10(C_t))
Trend_20 = Sign(MA_20(C_t) - MA_40(C_t))
Trend_60 = Sign(MA_60(C_t) - MA_120(C_t))

Trend_Alignment_t = (Trend_5 + Trend_20 + Trend_60) / 3
```

值接近+1：多周期共振上涨
值接近-1：多周期共振下跌
值接近0：周期不一致

---

## 8. 高级统计因子 (Advanced Statistical Factors)

### 8.1 Skewness（偏度）
收益率分布的偏斜程度。

```
Return_t = (C_t - C_{t-1}) / C_{t-1}
Mean_Return = Mean_n(Return_t)
Std_Return = Std_n(Return_t)

Skewness_t = (1/n) × Σ((Return_i - Mean_Return) / Std_Return)^3
i ∈ [t-n+1, t]
```

参数：n = 20

Skewness > 0：正偏（右尾），有大幅上涨的倾向
Skewness < 0：负偏（左尾），有大幅下跌的风险

---

### 8.2 Kurtosis（峰度）
收益率分布的尖峰程度。

```
Kurtosis_t = (1/n) × Σ((Return_i - Mean_Return) / Std_Return)^4 - 3
i ∈ [t-n+1, t]
```

参数：n = 20

Kurtosis > 0：厚尾分布，极端事件概率高
Kurtosis < 0：薄尾分布

---

### 8.3 Z_Score（标准分数）
价格相对历史均值的标准差倍数。

```
Z_Score_t = (C_t - MA_n(C_t)) / Std_n(C_t)
```

参数：n = 20

|Z_Score| > 2：价格异常偏离
|Z_Score| > 3：极端偏离

---

### 8.4 Percentile_Rank（百分位排名）
当前价格在历史分布中的位置。

```
Percentile_Rank_t = Rank(C_t in [C_{t-n+1}...C_t]) / n × 100%
```

参数：n = 100

值接近100：处于历史高位
值接近0：处于历史低位

---

### 8.5 Distance_from_High（距离历史高点）
当前价格相对N期最高点的回撤。

```
Distance_High_t = (C_t - Max_n(C_t)) / Max_n(C_t) × 100%
```

参数：n = 50

---

### 8.6 Distance_from_Low（距离历史低点）
当前价格相对N期最低点的涨幅。

```
Distance_Low_t = (C_t - Min_n(C_t)) / Min_n(C_t) × 100%
```

参数：n = 50

---

## 9. 趋势因子分类总结

### 9.1 强趋势因子
直接用于趋势判断和跟踪：

- **MA_Cross**：均线金叉/死叉
- **MACD**：趋势方向和强度
- **ADX**：趋势强度量化（ADX > 25表示强趋势）
- **+DI/-DI**：上升/下降趋势力量
- **EMA/SMA系统**：多均线排列
- **Price_MA_Distance**：价格趋势偏离

### 9.2 中期趋势因子
中长期趋势的度量：

- **ROC（10-20期）**：中期动量
- **Momentum（10-20期）**：绝对价格动量
- **VWAP_Distance**：相对平均成本
- **MA_Slope**：均线倾斜角度
- **Volume_Price_Trend**：量价确认

### 9.3 趋势确认因子
用于验证趋势真实性：

- **Volume_MA_Cross**：成交量放大确认
- **Price_Volume_Correlation**：价量同步性
- **ATR / Volatility增加**：趋势市波动率特征
- **Higher_High/Lower_Low**：价格结构确认
- **Bollinger_Band_Width扩张**：趋势启动信号
- **OBV方向**：资金流向确认

### 9.4 趋势强度因子
量化趋势的力度：

- **ADX**：最直接的趋势强度指标
- **Price_Efficiency**：单边运动效率
- **Hurst_Exponent**：长期持续性（H > 0.5）
- **MA_Convergence**：均线发散度
- **Trend_Alignment**：多周期共振

### 9.5 趋势反转预警因子
识别趋势可能结束：

- **RSI极值**：>70或<30
- **Stochastic背离**：价格与指标不同步
- **MACD_Histogram收敛**：柱状图缩小
- **Price_Acceleration减速**：动量衰减
- **Volatility_Ratio突变**：波动率急剧变化
- **Lower_High/Higher_Low**：趋势结构破坏
- **Mass_Index > 27**：反转前兆
- **Bollinger_Band_Width收缩后扩张**：趋势转折

---

## 使用建议

### 因子计算优化
1. **向量化计算**：使用Pandas/NumPy的滚动窗口函数
2. **增量更新**：对于EMA、OBV等递归公式，实时计算时使用增量更新
3. **缓存中间结果**：TR、TP等被多次使用的中间变量应缓存
4. **并行计算**：不同类别的因子可以并行计算

### 数据处理
1. **异常值处理**：对比率型因子进行clip或winsorize（如限制在[-5σ, +5σ]）
2. **缺失值处理**：
   - 前向填充（forward fill）用于价格
   - 填充0用于成交量（停盘期间）
   - 或删除不完整的样本
3. **标准化**：使用z-score或min-max归一化统一量纲
4. **去极值**：使用MAD（中位数绝对偏差）方法

### 因子有效性检验
```python
# IC (Information Coefficient)
IC_t = Corr(Factor_t, Forward_Return_{t+k})

# 因子单调性
对因子分10组，检验各组平均收益率的单调性

# 因子稳定性
检验IC的时间序列统计特性（IR = Mean(IC) / Std(IC)）
```

### 因子组合策略示例

**趋势跟踪组合：**
```
Entry_Long = (ADX > 25) & (MACD > MACD_Signal) &
             (MA_5 > MA_20) & (Volume_Ratio > 1.2)
```

**均值回归组合：**
```
Entry_Long = (ADX < 20) & (RSI < 30) &
             (Bollinger_%B < 0) & (Z_Score < -2)
```

**突破策略组合：**
```
Entry_Long = (C_t > Max_20(H_t)) & (Volume_Ratio > 1.5) &
             (Price_Volume_Corr > 0.5)
```

---

## 实现参考

### Python计算示例（使用Pandas）

```python
import pandas as pd
import numpy as np

# 假设df有列：['open', 'high', 'low', 'close', 'volume']

# 1. 简单因子
df['return'] = df['close'].pct_change()
df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

# 2. 技术指标
df['sma_20'] = df['close'].rolling(20).mean()
df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()

# 3. ATR
df['tr'] = np.maximum(
    df['high'] - df['low'],
    np.maximum(
        abs(df['high'] - df['close'].shift(1)),
        abs(df['low'] - df['close'].shift(1))
    )
)
df['atr'] = df['tr'].ewm(span=14, adjust=False).mean()

# 4. RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).ewm(span=14, adjust=False).mean()
loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 5. MACD
df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = df['ema_12'] - df['ema_26']
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
df['macd_hist'] = df['macd'] - df['macd_signal']

# 6. 布林带
df['bb_mid'] = df['close'].rolling(20).mean()
df['bb_std'] = df['close'].rolling(20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
df['bb_pctb'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
```

---

**文档版本：** v2.0
**更新日期：** 2026-01-07
**数据要求：** OHLCV (Open, High, Low, Close, Volume)
**时间粒度：** 分钟级（可调整参数适配其他周期）
