# 特征工程因子目录

基于OHLCV数据的分钟级特征库，用于量化交易策略开发。

---

## 1. 流动性因子 (Liquidity Factors)

流动性因子衡量市场的交易活跃度和价格冲击成本，反映资金进出的难易程度。

### 基础成交量因子
- **Volume_Ratio**: 当前成交量/过去N期平均成交量
  - 作用：识别异常交易活跃时段，放量突破信号

- **Volume_Std**: 成交量的标准差（滚动窗口）
  - 作用：衡量交易量的波动性，识别流动性变化

- **Volume_MA_Cross**: 短期成交量均线/长期成交量均线
  - 作用：捕捉成交量趋势变化，确认价格突破有效性

- **Cumulative_Volume**: 时间段内累计成交量
  - 作用：衡量整体市场参与度

### 价量关系因子
- **Price_Volume_Correlation**: 价格变化与成交量的滚动相关性
  - 作用：判断价格运动的可持续性，相关性高表示趋势强劲

- **VWAP** (Volume Weighted Average Price): 成交量加权平均价
  - 作用：衡量平均成交成本，作为支撑/阻力位参考

- **VWAP_Distance**: (Close - VWAP) / VWAP
  - 作用：判断当前价格相对平均成本的偏离度

- **Volume_Price_Trend** (VPT): 累计的(价格变化率 × 成交量)
  - 作用：结合价量关系的趋势指标

### 买卖压力因子
- **Money_Flow**: Close × Volume (资金流)
  - 作用：衡量资金流入流出强度

- **Money_Flow_Ratio**: 上涨期资金流/下跌期资金流
  - 作用：判断多空力量对比

- **Ease_of_Movement** (EMV): (High + Low)/2 的变化 / (Volume / (High - Low))
  - 作用：衡量单位成交量带来的价格变动，反映推动价格的难易程度

- **Force_Index**: (Close - Close_prev) × Volume
  - 作用：衡量价格变动背后的力量强度

---

## 2. 波动性因子 (Volatility Factors)

波动性因子衡量价格波动的幅度和频率，是风险管理和趋势识别的重要指标。

### 价格波动范围
- **True_Range** (TR): max(High-Low, |High-Close_prev|, |Low-Close_prev|)
  - 作用：衡量真实波动范围，考虑跳空

- **ATR** (Average True Range): TR的N期移动平均
  - 作用：标准化波动率指标，用于止损和仓位管理

- **ATR_Percent**: ATR / Close
  - 作用：标准化的波动率，便于跨品种比较

- **High_Low_Range**: (High - Low) / Close
  - 作用：日内波动幅度百分比

### 收益率波动
- **Return_Std**: 收益率的滚动标准差
  - 作用：衡量价格波动的离散程度

- **Parkinson_Volatility**: sqrt(1/(4×N×ln(2)) × Σ(ln(High/Low))²)
  - 作用：基于高低价的波动率估计，比收盘价波动率更有效

- **Garman_Klass_Volatility**: 结合开高低收的波动率估计
  - 作用：更准确的波动率度量，考虑日内所有价格信息

- **Yang_Zhang_Volatility**: 结合隔夜和日内波动的估计
  - 作用：考虑跳空的波动率，适用于分钟级数据

### 波动率指标
- **Bollinger_Band_Width**: (Upper_Band - Lower_Band) / Middle_Band
  - 作用：衡量价格通道宽度，识别波动率扩张/收缩

- **Bollinger_Percent_B**: (Close - Lower_Band) / (Upper_Band - Lower_Band)
  - 作用：价格在布林带中的相对位置

- **Keltner_Channel_Width**: 基于ATR的价格通道宽度
  - 作用：趋势强度和波动率的综合指标

- **Historical_Volatility**: 对数收益率的标准差（年化）
  - 作用：传统波动率度量，用于期权定价和风险管理

### 波动变化
- **Volatility_Ratio**: 短期波动率 / 长期波动率
  - 作用：识别波动率突变，预警风险变化

- **Realized_Range**: (Max_High - Min_Low) / Open (时间段内)
  - 作用：衡量时间段内的价格震荡幅度

---

## 3. 动量因子 (Momentum Factors)

动量因子捕捉价格的运动速度和加速度，是趋势跟踪和反转策略的核心。

### 价格动量
- **ROC** (Rate of Change): (Close - Close_N) / Close_N
  - 作用：价格变化率，衡量涨跌速度

- **Momentum**: Close - Close_N
  - 作用：绝对价格变动，简单动量指标

- **Price_Acceleration**: ROC的变化率
  - 作用：捕捉动量的加速/减速，预警趋势转折

### 相对强弱
- **RSI** (Relative Strength Index): 100 - 100/(1 + RS)
  - 作用：超买超卖指标，判断价格强弱和反转时机

- **Stochastic_K**: (Close - Low_N) / (High_N - Low_N) × 100
  - 作用：价格在N期范围内的相对位置

- **Stochastic_D**: Stochastic_K的移动平均
  - 作用：平滑的随机指标，产生交易信号

- **Williams_%R**: (High_N - Close) / (High_N - Low_N) × -100
  - 作用：类似随机指标，反向计算的超买超卖指标

### 趋势强度
- **ADX** (Average Directional Index): DI+和DI-的综合指标
  - 作用：衡量趋势强度（不判断方向），识别趋势市/震荡市

- **DI+** (Positive Directional Indicator): 上涨动能指标
  - 作用：衡量向上运动的力量

- **DI-** (Negative Directional Indicator): 下跌动能指标
  - 作用：衡量向下运动的力量

- **Mass_Index**: 基于价格范围的趋势反转指标
  - 作用：识别趋势可能的反转点

### 震荡指标
- **MACD**: EMA_short - EMA_long
  - 作用：趋势跟踪和动量指标，捕捉中期趋势

- **MACD_Signal**: MACD的移动平均
  - 作用：产生买卖信号的参考线

- **MACD_Histogram**: MACD - MACD_Signal
  - 作用：动量的加速度，预警趋势变化

- **CCI** (Commodity Channel Index): (TP - MA_TP) / (0.015 × MD)
  - 作用：衡量价格偏离统计平均的程度，超买超卖信号

- **Ultimate_Oscillator**: 综合多时间周期的动量指标
  - 作用：减少单一周期的虚假信号

---

## 4. 时序因子 (Time Series Factors)

时序因子利用价格的时间序列特性，捕捉周期性、季节性和自相关结构。

### 均线系统
- **SMA** (Simple Moving Average): 简单移动平均
  - 作用：平滑价格，识别趋势方向

- **EMA** (Exponential Moving Average): 指数移动平均
  - 作用：对近期价格赋予更高权重，反应更灵敏

- **WMA** (Weighted Moving Average): 加权移动平均
  - 作用：线性递减权重的平滑方法

- **DEMA** (Double EMA): 2×EMA - EMA(EMA)
  - 作用：减少滞后的快速均线

- **TEMA** (Triple EMA): 三重指数平滑
  - 作用：进一步减少滞后，更快响应价格变化

- **HMA** (Hull Moving Average): WMA(2×WMA(n/2) - WMA(n))
  - 作用：平滑且低滞后的均线

### 均线关系
- **MA_Cross**: 短期均线 - 长期均线
  - 作用：金叉死叉信号，趋势转折

- **Price_MA_Distance**: (Close - MA) / MA
  - 作用：价格偏离均线的程度，均值回归信号

- **MA_Slope**: MA的变化率
  - 作用：趋势方向和强度

- **MA_Convergence**: 多条均线的收敛/发散程度
  - 作用：识别趋势启动或结束

### 价格形态
- **Higher_High**: 当前高点 > 前N个高点
  - 作用：上升趋势特征

- **Lower_Low**: 当前低点 < 前N个低点
  - 作用：下降趋势特征

- **Higher_Low**: 在下跌后创更高的低点
  - 作用：上升趋势恢复信号

- **Lower_High**: 在上涨后创更低的高点
  - 作用：下降趋势开始信号

### 周期和节奏
- **Price_Cycle**: 基于傅里叶变换的周期检测
  - 作用：识别价格的主导周期

- **Autocorrelation**: 价格序列的自相关系数
  - 作用：判断价格的持续性或反转倾向

- **Hurst_Exponent**: 分形维度，衡量序列的长期记忆
  - 作用：识别趋势性(>0.5)或均值回归性(<0.5)

- **Detrended_Price**: 去趋势价格
  - 作用：识别周期性波动

### 支撑阻力
- **Pivot_Point**: (High + Low + Close) / 3
  - 作用：经典枢轴点，作为支撑阻力参考

- **Resistance_1/2/3**: 基于枢轴点计算的阻力位
  - 作用：价格可能遇阻的位置

- **Support_1/2/3**: 基于枢轴点计算的支撑位
  - 作用：价格可能获得支撑的位置

- **Fractal_High/Low**: 分形高低点（局部极值）
  - 作用：识别关键的转折点位

---

## 5. 复合因子与其他

### 市场微观结构
- **Typical_Price**: (High + Low + Close) / 3
  - 作用：日内平均价格

- **Weighted_Close**: (High + Low + 2×Close) / 4
  - 作用：更重视收盘价的平均价格

- **Price_Efficiency**: |Close - Open| / (High - Low)
  - 作用：趋势效率，值越大表示单边行情

- **Candle_Body_Ratio**: |Close - Open| / (High - Low)
  - 作用：实体与影线比例，判断多空力量

- **Upper_Shadow**: High - max(Open, Close)
  - 作用：上影线长度，上方抛压

- **Lower_Shadow**: min(Open, Close) - Low
  - 作用：下影线长度，下方支撑

### 市场强度
- **Price_Strength**: (Close - Low) / (High - Low)
  - 作用：收盘价在日内范围的相对位置

- **Bull_Bear_Power**: Close - EMA
  - 作用：多空力量对比

- **Elder_Force_Index**: (Close - Close_prev) × Volume
  - 作用：综合价量的力量指标

### 反转信号
- **Reversal_Score**: 综合多个反转指标的得分
  - 作用：量化反转概率

- **Exhaustion_Gaps**: 跳空后的动能衰竭
  - 作用：趋势末期的反转信号

---

## 6. 趋势因子分类

以下因子具有明确的趋势识别和跟踪能力：

### 强趋势因子
- **MA_Cross** (均线交叉)
- **MACD** (异同移动平均)
- **ADX** (平均趋向指标) - 当ADX > 25时表示强趋势
- **DI+/DI-** (方向指标)
- **EMA/SMA** (移动平均线)
- **Price_MA_Distance** (价格与均线距离)

### 中期趋势因子
- **ROC** (变化率) - 中长周期
- **Momentum** (动量)
- **VWAP_Distance** (与VWAP偏离)
- **MA_Slope** (均线斜率)
- **Volume_Price_Trend** (量价趋势)

### 趋势确认因子
- **Volume_MA_Cross** (成交量确认)
- **Price_Volume_Correlation** (价量相关性)
- **ATR** (波动率扩张表示趋势增强)
- **Higher_High/Lower_Low** (价格结构)
- **Bollinger_Band_Width** (通道宽度)

### 趋势强度因子
- **ADX** (趋势强度的直接度量)
- **Mass_Index** (趋势持续性)
- **Price_Efficiency** (价格运动效率)
- **Hurst_Exponent** (长期记忆性)

### 趋势反转预警因子
- **RSI** (极值区域)
- **Stochastic** (超买超卖)
- **MACD_Histogram** (柱状图收敛)
- **Price_Acceleration** (动量减速)
- **Volatility_Ratio** (波动率突变)
- **Lower_High/Higher_Low** (趋势结构变化)

---

## 使用建议

### 因子组合策略
1. **趋势跟踪**: 使用ADX识别趋势市场，配合MACD和均线系统入场，ATR设置止损
2. **均值回归**: 在震荡市（ADX<20）使用RSI/Stochastic识别超买超卖，配合布林带边界
3. **突破策略**: 结合Volume_Ratio和Price_Volume_Correlation确认突破有效性
4. **多周期验证**: 短中长期因子结合，提高信号可靠性

### 特征工程注意事项
- 对所有比率型因子进行异常值处理（clip或winsorize）
- 标准化/归一化特征，保证不同因子处于同一量级
- 考虑特征的滞后项（lag features）作为额外输入
- 计算特征的滚动统计量（均值、标准差、分位数）
- 不同时间窗口的同一因子可作为独立特征

### 因子有效性检验
- 计算因子的IC (Information Coefficient)
- 进行因子单调性测试
- 检验因子的稳定性（不同市场阶段）
- 分析因子之间的相关性，避免冗余
