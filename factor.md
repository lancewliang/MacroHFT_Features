# 特征工程因子目录 (Factor Catalog V4)

基于OHLCV数据的分钟级特征库,专注于K线形态和价量关系分析。

---

## 1. 流动性因子 (Liquidity Factors)

流动性因子衡量市场的交易活跃度和价格冲击成本,反映资金进出的难易程度。

### 成交量加权价格因子

- **WAP** (Weighted Average Price) - 加权平均价格
  - 公式: `WAP = (∑(价格_i × 数量_i)) / ∑数量_i`
  - 作用: 衡量真实成交的平均价格,反映市场参与者的实际成交成本,常用于订单簿分析

- **VWAP** (Volume Weighted Average Price) - 成交量加权平均价格
  - 公式: `VWAP = (∑(价格_i × 成交量_i)) / ∑成交量_i`
  - 作用: 衡量时间段内的平均成交价格,机构交易的重要基准,作为支撑/阻力位参考

### 对数收益率因子

- **Log_Return_WAP_1** - WAP对数收益率(1期)
  - 公式: `log_return_wap_1 = ln(WAP_t / WAP_{t-1})`
  - 作用: 衡量基于WAP的短期价格变动,对数形式更适合统计分析和模型训练

- **Log_Return_WAP_2** - WAP对数收益率(2期)
  - 公式: `log_return_wap_2 = ln(WAP_t / WAP_{t-2})`
  - 作用: 捕捉稍长周期的WAP价格动量,用于识别短期趋势延续或反转

### 成交量趋势因子

- **Volume_Trend_60** - 60期成交量趋势指标
  - 公式: `volume_trend_60 = (Volume_t - MA(Volume, 60)) / Std(Volume, 60)`
  - 作用: 标准化的成交量偏离度,识别异常放量或缩量,值>2表示显著放量,值<-2表示显著缩量

### 成交量异常因子

- **Volume_ZScore** - 成交量Z-Score
  - 公式: `volume_zscore = (Volume_t - Rolling_Mean(Volume, N)) / Rolling_Std(Volume, N)`
  - 参数: N通常取30-100根K线
  - 作用: 识别突然放量事件,捕捉重要交易活动,|Z-Score| > 2表示异常成交量
  - 解释: 正值表示放量,负值表示缩量,绝对值越大表示异常程度越高

- **Turnover_ZScore** - 成交金额Z-Score
  - 公式: `turnover = Volume × (High + Low + Close) / 3`
  - 公式: `turnover_zscore = (Turnover_t - Rolling_Mean(Turnover, N)) / Rolling_Std(Turnover, N)`
  - 作用: 反映资金规模的异常变化,比单纯成交量更能体现大资金行为

- **Volume_Ratio** - 成交量比率
  - 公式: `volume_ratio = MA(Volume, short) / MA(Volume, long)`
  - 参数: short=5, long=30 (分钟)
  - 作用: 对比短期与长期成交量,捕捉资金流入/流出加速度
  - 解释: VR > 1且上升表示交易活动增强,VR < 1表示活跃度减弱

- **Volume_Acceleration** - 成交量加速度
  - 公式: `volume_accel = Volume_t / EMA(Volume, N)`
  - 作用: 衡量当前成交量相对于指数加权平均的倍数,识别成交量突变

### 量价关系因子

- **Price_Volume_Correlation_Rolling** - 滚动量价相关性
  - 公式: `corr = Rolling_Corr(Returns, Volume, N)`
  - 参数: N=5-10根K线
  - 作用: 短期窗口内价格变动与成交量的相关性,判断趋势的可持续性
  - 解释: 正相关表示价格与成交量同向变动,负相关表示反向变动

---

## 2. 波动性因子 (Volatility Factors)

波动性因子衡量价格波动的幅度和频率,是风险管理和趋势识别的重要指标。

### 基础波动率

- **Intrabar_Volatility** - 分钟内波动率
  - 公式: `intrabar_vol = (High - Low) / Open`
  - 作用: 衡量单根K线的相对波动幅度,标准化到开盘价
  - 解释: 值越大表示该分钟内波动越剧烈

- **High_Low_Range** - 最高最低价差
  - 公式: `hl_range = High - Low`
  - 作用: 绝对价格波动范围,反映分钟内的价格震荡幅度

- **High_Low_Range_Pct** - 最高最低价差百分比
  - 公式: `hl_range_pct = (High - Low) / Close`
  - 作用: 相对波动幅度,便于跨品种和跨时间比较

### 流动性调整波动率

- **Volume_Weighted_Volatility** - 单位成交量波动率
  - 公式: `vw_vol = Intrabar_Volatility / (Volume + ε)`
  - 作用: 衡量单位成交量带来的价格波动,反映市场流动性深度
  - 解释:
    - 高值表示成交量小但价格波动大,可能存在流动性不足
    - 低值表示大量成交但价格稳定,流动性充足
    - 可用于评估市场的价格稳定性

- **Liquidity_Cost_Proxy** - 流动性成本代理
  - 公式: `liq_cost = (High - Low) / (Volume × Close + ε)`
  - 作用: 估算交易的相对成本,值越高表示流动性越差

---

## 3. 趋势因子 (Trend Factors)

趋势因子捕捉价格的方向性运动和动量特征,是趋势跟踪策略的核心。使用60期(1小时)、180期(3小时)、360期(6小时)三个时间窗口。

### 移动平均线因子

- **SMA_60/180/360** - 简单移动平均线
  - 公式: `SMA_N = (∑Close_i) / N, i=1...N`
  - 作用: 平滑价格序列,识别价格趋势方向,作为动态支撑/阻力位
  - 解释: 价格在均线上方表示上升趋势,下方表示下降趋势

- **EMA_60/180/360** - 指数移动平均线
  - 公式: `EMA_t = α × Close_t + (1-α) × EMA_{t-1}`, α = 2/(N+1)
  - 作用: 对近期价格赋予更高权重,比SMA反应更灵敏
  - 解释: 适用于快速捕捉趋势变化,减少滞后

### 价格与均线关系

- **Price_to_SMA_60/180/360** - 价格相对均线位置
  - 公式: `price_to_ma = (Close - SMA_N) / SMA_N`
  - 作用: 衡量价格偏离均线的程度,识别超买超卖
  - 解释: 正值表示价格高于均线,负值表示低于均线,绝对值越大偏离越严重

- **Price_to_EMA_60/180/360** - 价格相对EMA位置
  - 公式: `price_to_ema = (Close - EMA_N) / EMA_N`
  - 作用: 价格相对指数均线的偏离度
  - 解释: 可用于均值回归策略,极端值预示回归机会

### 均线斜率因子

- **SMA_Slope_60/180/360** - 均线斜率
  - 公式: `slope = (SMA_N,t - SMA_N,t-M) / (SMA_N,t-M)`
  - 参数: M通常取5-10期
  - 作用: 衡量均线的变化速度,判断趋势强度和方向
  - 解释: 正斜率表示上升趋势,负斜率表示下降趋势,绝对值越大趋势越强

- **EMA_Slope_60/180/360** - EMA斜率
  - 公式: `slope = (EMA_N,t - EMA_N,t-M) / (EMA_N,t-M)`
  - 作用: EMA的变化率,更敏感的趋势方向指标

### 均线交叉因子

- **MA_Cross_60_180** - 60期与180期均线交叉
  - 公式: `ma_cross = (SMA_60 - SMA_180) / SMA_180`
  - 作用: 捕捉中短期趋势转折,金叉/死叉信号
  - 解释: 正值且上升为金叉(看涨),负值且下降为死叉(看跌)

- **MA_Cross_180_360** - 180期与360期均线交叉
  - 公式: `ma_cross = (SMA_180 - SMA_360) / SMA_360`
  - 作用: 捕捉中长期趋势转折,更可靠但滞后较大

- **EMA_Cross_60_180** - EMA快慢线交叉
  - 公式: `ema_cross = (EMA_60 - EMA_180) / EMA_180`
  - 作用: 更灵敏的均线交叉信号,减少滞后

### 价格动量因子

- **ROC_60/180/360** - 变化率 (Rate of Change)
  - 公式: `ROC_N = (Close_t - Close_{t-N}) / Close_{t-N}`
  - 作用: 衡量N期价格变化百分比,直接的动量指标
  - 解释: 正值表示上涨动量,负值表示下跌动量,绝对值反映动量强度

- **Momentum_60/180/360** - 动量
  - 公式: `Momentum_N = Close_t - Close_{t-N}`
  - 作用: 绝对价格变化,简单的动量度量

- **Price_Acceleration_60/180/360** - 价格加速度
  - 公式: `accel = ROC_N,t - ROC_N,t-M`
  - 参数: M通常取5-10期
  - 作用: 捕捉动量的变化率,预警趋势转折
  - 解释: 正值表示加速上涨,负值表示减速或加速下跌

### 趋势强度因子

- **ADX_60/180/360** - 平均趋向指标 (Average Directional Index)
  - 计算步骤:
    1. `+DM = High_t - High_{t-1}` (如果>0且>-DM)
    2. `-DM = Low_{t-1} - Low_t` (如果>0且>+DM)
    3. `TR = max(High-Low, |High-Close_prev|, |Low-Close_prev|)`
    4. `+DI = 100 × EMA(+DM, N) / EMA(TR, N)`
    5. `-DI = 100 × EMA(-DM, N) / EMA(TR, N)`
    6. `DX = 100 × |+DI - -DI| / (+DI + -DI)`
    7. `ADX = EMA(DX, N)`
  - 作用: 衡量趋势强度(不判断方向),ADX>25表示强趋势,<20表示震荡
  - 解释: 值越高趋势越强,适合趋势跟踪;值越低适合均值回归

- **DI_Plus_60/180/360** - 正向趋向指标
  - 公式: 见ADX计算中的+DI
  - 作用: 衡量上涨力量,+DI > -DI表示上升趋势占优

- **DI_Minus_60/180/360** - 负向趋向指标
  - 公式: 见ADX计算中的-DI
  - 作用: 衡量下跌力量,-DI > +DI表示下降趋势占优

### 价格位置因子

- **Price_Position_60/180/360** - 价格在N期范围内的位置
  - 公式: `position = (Close - Low_N) / (High_N - Low_N + ε)`
  - 作用: 衡量当前价格在N期高低点范围内的相对位置
  - 解释: 接近1表示处于高位,接近0表示处于低位,可识别超买超卖

- **Higher_High_Count_60/180/360** - N期内创新高次数
  - 公式: `count = ∑(High_t > max(High_{t-1...t-M}))`
  - 参数: M为检测窗口,如5期
  - 作用: 统计创新高的频率,强上升趋势特征
  - 解释: 高值表示持续创新高,趋势强劲

- **Lower_Low_Count_60/180/360** - N期内创新低次数
  - 公式: `count = ∑(Low_t < min(Low_{t-1...t-M}))`
  - 作用: 统计创新低的频率,强下降趋势特征

### 趋势持续性因子

- **Trend_Consistency_60/180/360** - 趋势一致性
  - 公式: `consistency = (上涨K线数 - 下跌K线数) / N`
  - 作用: 衡量价格运动的方向一致性,范围[-1, 1]
  - 解释: 接近+1表示持续上涨,接近-1表示持续下跌,接近0表示震荡

- **Trend_Strength_Index_60/180/360** - 趋势强度指数
  - 公式: `TSI = (∑|Close_t - Close_{t-1}| where 方向一致) / (∑|Close_t - Close_{t-1}|)`
  - 作用: 衡量同向运动占总波动的比例
  - 解释: 值越高表示趋势越明确,值低表示震荡

- **Linear_Regression_Slope_60/180/360** - 线性回归斜率
  - 公式: 对Close序列进行线性回归,取斜率
  - 作用: 拟合价格的长期趋势方向和强度
  - 解释: 正斜率表示上升趋势,负斜率表示下降趋势

- **R_Squared_60/180/360** - 线性回归R²
  - 公式: 线性回归的决定系数
  - 作用: 衡量价格趋势的线性程度,范围[0, 1]
  - 解释: R²接近1表示强趋势,接近0表示震荡无序

### MACD因子

- **MACD_12_26** - MACD快慢线差值
  - 公式: `MACD = EMA(Close, 12) - EMA(Close, 26)`
  - 作用: 经典动量振荡指标,捕捉短期趋势
  - 解释: 正值表示短期上升动量,负值表示下降动量

- **MACD_Signal_9** - MACD信号线
  - 公式: `Signal = EMA(MACD, 9)`
  - 作用: MACD的平滑版本,产生交易信号

- **MACD_Histogram** - MACD柱状图
  - 公式: `Histogram = MACD - Signal`
  - 作用: MACD与信号线的差值,动量加速度
  - 解释: 柱状图扩张表示动量增强,收敛表示动量减弱

### 多周期趋势一致性

- **Multi_Timeframe_Trend_Alignment** - 多周期趋势对齐度
  - 公式: `alignment = sign(ROC_60) + sign(ROC_180) + sign(ROC_360)`
  - 作用: 综合多个时间周期的趋势方向
  - 解释: 值为+3表示三个周期全部上涨,-3表示全部下跌,绝对值越大趋势越可靠

- **Trend_Strength_Composite** - 综合趋势强度
  - 公式: `strength = (ADX_60 + ADX_180 + ADX_360) / 3`
  - 作用: 多周期趋势强度的平均值
  - 解释: 高值表示多周期均处于强趋势状态

---

## 4. 市场微观结构因子 (Market Microstructure Factors)

市场微观结构因子捕捉价格形成过程中的精细特征,反映市场的运行状态。

### 价格路径因子

- **Range_Utilization** - 范围利用率
  - 公式: `range_util = |Close - Open| / (High - Low + ε)`
  - 作用: 衡量K线实体占总波动范围的比例,反映价格运动的方向性
  - 解释:
    - 值接近1表示单边行情,价格沿单一方向运动
    - 值接近0表示震荡行情,价格反复波动
    - 高范围利用率配合放量通常表示强趋势

- **Signed_Range_Utilization** - 带符号范围利用率
  - 公式: `signed_range_util = sign(Close - Open) × Range_Utilization`
  - 作用: 带方向的范围利用率,正值表示上涨,负值表示下跌
  - 解释: 绝对值越大表示单边性越强,方向越明确

- **True_Strength_Proxy** - 真实强弱代理
  - 公式: `true_strength = Signed_Range_Utilization × (Volume / MA(Volume, N))`
  - 作用: 结合范围利用率和成交量强度,综合判断价格运动的力度
  - 解释: 高绝对值表示强势的、有成交量支撑的单边行情

### 价格效率因子

- **Price_Efficiency** - 价格效率
  - 公式: `price_eff = |Close - Open| / (High - Low + ε)`
  - 作用: 同Range_Utilization,衡量价格从开盘到收盘的净运动效率
  - 解释: 值越大表示趋势越明确,值越小表示震荡越剧烈

- **Price_Reversal_Indicator** - 价格反转指标
  - 公式: `price_rev = (High + Low - Open - Close) / (High - Low + ε)`
  - 作用: 衡量价格在分钟内的反转程度
  - 解释: 正值表示价格先涨后跌或先跌后涨,负值表示单边运动

### 成交量分布因子

- **Volume_at_High** - 高位成交量占比估算
  - 公式: `vol_at_high = KUP × Volume`
  - 作用: 基于上影线长度估算高价位区域的成交量分布

- **Volume_at_Low** - 低位成交量占比估算
  - 公式: `vol_at_low = KLOW × Volume`
  - 作用: 基于下影线长度估算低价位区域的成交量分布

---

## 5. K线形态因子 (Candlestick Pattern Factors)

K线形态因子捕捉蜡烛图的几何特征,反映市场多空力量对比和投资者情绪。

### 基础形态特征

- **KMID** - K线中间价位置
  - 公式: `kmid = (close - open) / (high - low + ε)`
  - 作用: 衡量K线实体在整体波动范围中的位置,值>0表示收盘价高于开盘价(阳线),值<0表示阴线
  - 解释: kmid ≈ 1表示全实体大阳线,kmid ≈ -1表示全实体大阴线,kmid ≈ 0表示十字星

- **KLEN** - K线长度(相对波动)比例
  - 公式: `klen = (high - low) / (open + ε)`
  - 作用: 衡量K线整体波动幅度相对于开盘价的比例,反映市场波动强度
  - 解释: 值越大表示波动越剧烈,适用于识别关键转折点或突破

- **KUP** - 上影线比例
  - 公式: `kup = (high - max(open, close)) / (high - low + ε)`
  - 作用: 衡量上影线在整体波动范围中的占比,反映上方压力
  - 解释: 值越大表示价格在高位遇阻回落,可能预示上涨乏力

- **KLOW** - 下影线比例
  - 公式: `klow = (min(open, close) - low) / (high - low + ε)`
  - 作用: 衡量下影线在整体波动范围中的占比,反映下方支撑
  - 解释: 值越大表示价格在低位获得支撑反弹

- **KSFT** - K线实体偏移度
  - 公式: `ksft = (max(open, close) - (high + low)/2) / (high - low + ε)`
  - 作用: 衡量K线实体相对于高低价中点的偏移程度,反映多空力量的空间分布
  - 解释: 值>0表示实体偏向上方,值<0表示实体偏向下方

### 非线性增强特征

- **KMID2** - K线中间价位置平方项
  - 公式: `kmid2 = kmid²`
  - 作用: 增强kmid的非线性特征,放大极端值的影响,帮助模型捕捉大阳线/大阴线的信号

- **KUP2** - 上影线比例平方项
  - 公式: `kup2 = kup²`
  - 作用: 增强上影线的非线性关系,强化长上影线的反转信号

- **KLOW2** - 下影线比例平方项
  - 公式: `klow2 = klow²`
  - 作用: 增强下影线的非线性关系,强化长下影线的支撑信号

- **KSFT2** - K线实体偏移度平方项
  - 公式: `ksft2 = ksft²`
  - 作用: 增强实体偏移的非线性特征,放大多空力量失衡的影响

---

## 6. K线形态识别参考表

以下是常见K线形态的特征值范围及其市场含义:

| 形态名称 | kmid | kup | klow | ksft | 市场含义 |
|---------|------|-----|------|------|---------|
| **大阳线** | >0.7 | 小(<0.2) | 小(<0.2) | >0.3 | 强烈看涨,买方主导 |
| **大阴线** | <-0.7 | 小(<0.2) | 小(<0.2) | <-0.3 | 强烈看跌,卖方主导 |
| **十字星** | ≈0 (±0.1) | ≈0.5 (±0.1) | ≈0.5 (±0.1) | ≈0 (±0.1) | 市场犹豫,方向不明 |
| **锤子线** | >0 | 小(<0.2) | >0.7 | <0 | 底部反转信号,下方支撑强 |
| **射击之星** | <0 | >0.7 | 小(<0.2) | >0 | 顶部反转信号,上方压力大 |
| **纺锤线** | ≈0 (±0.1) | ≈0.3 (±0.1) | ≈0.3 (±0.1) | ≈0 (±0.1) | 平衡市场,震荡行情 |

### 形态组合策略建议

1. **趋势确认**: 大阳线/大阴线配合成交量放大,确认趋势延续
2. **反转识别**: 锤子线/射击之星出现在趋势末端,结合RSI超买超卖信号
3. **震荡判断**: 连续出现十字星/纺锤线,适合均值回归策略
4. **多因子验证**: K线形态因子应与动量、波动率因子结合使用,提高信号可靠性

---

## 7. 基础数据字段 (Base OHLCV Data)

- **timestamp**: 时间戳
- **open**: 开盘价
- **high**: 最高价
- **low**: 最低价
- **close**: 收盘价
- **volume**: 成交量

---

## 8. 使用建议

### 特征工程注意事项

1. **异常值处理**:
   - K线形态因子中使用了 ε (epsilon, 通常取1e-8) 避免除零错误
   - 建议对所有比率型因子进行clip处理,限制在合理范围内

2. **特征标准化**:
   - 对数收益率通常服从正态分布,可直接使用
   - K线形态因子已归一化到[-1, 1]或[0, 1]范围,无需额外标准化
   - Volume_Trend_60、Volume_ZScore已进行Z-score标准化

3. **特征组合**:
   - K线形态因子(kmid, kup, klow, ksft)应组合使用,单一因子可能产生虚假信号
   - 平方项因子帮助非线性模型(如神经网络)更好地学习复杂模式
   - WAP/VWAP配合对数收益率,可构建更稳健的价格动量指标

4. **时间窗口考虑**:
   - 可构建多时间窗口的K线形态因子(5分钟、15分钟、60分钟)
   - 不同周期的形态因子可作为独立特征输入模型

### 因子有效性检验

- 计算K线形态因子与未来收益的IC (Information Coefficient)
- 检验形态因子在不同市场状态(趋势/震荡)下的稳定性
- 分析形态因子与成交量因子的交互效应

---

## 9. 附录: 完整特征列表

### 基础OHLCV数据
```python
'timestamp', 'volume', 'open', 'high', 'low', 'close'
```

### 1. 流动性因子

**成交量加权价格因子:**
```python
'wap'                    # 加权平均价格
'vwap'                   # 成交量加权平均价格
```

**对数收益率因子:**
```python
'log_return_wap_1'       # WAP对数收益率(1期)
'log_return_wap_2'       # WAP对数收益率(2期)
```

**成交量趋势因子:**
```python
'volume_trend_60'        # 60期成交量趋势指标
```

**成交量异常因子:**
```python
'volume_zscore'          # 成交量Z-Score
'turnover_zscore'        # 成交金额Z-Score
'volume_ratio'           # 成交量比率(短期/长期)
'volume_acceleration'    # 成交量加速度
```

**量价关系因子:**
```python
'price_volume_corr'      # 滚动量价相关性
```

### 2. 波动性因子

**基础波动率:**
```python
'intrabar_volatility'    # 分钟内波动率
'high_low_range'         # 最高最低价差
'high_low_range_pct'     # 最高最低价差百分比
```

**流动性调整波动率:**
```python
'volume_weighted_vol'    # 单位成交量波动率
'liquidity_cost_proxy'   # 流动性成本代理
```

### 3. 趋势因子

**移动平均线:**
```python
'sma_60', 'sma_180', 'sma_360'           # 简单移动平均线
'ema_60', 'ema_180', 'ema_360'           # 指数移动平均线
```

**价格与均线关系:**
```python
'price_to_sma_60'        # 价格相对SMA_60位置
'price_to_sma_180'       # 价格相对SMA_180位置
'price_to_sma_360'       # 价格相对SMA_360位置
'price_to_ema_60'        # 价格相对EMA_60位置
'price_to_ema_180'       # 价格相对EMA_180位置
'price_to_ema_360'       # 价格相对EMA_360位置
```

**均线斜率:**
```python
'sma_slope_60'           # SMA_60斜率
'sma_slope_180'          # SMA_180斜率
'sma_slope_360'          # SMA_360斜率
'ema_slope_60'           # EMA_60斜率
'ema_slope_180'          # EMA_180斜率
'ema_slope_360'          # EMA_360斜率
```

**均线交叉:**
```python
'ma_cross_60_180'        # SMA_60与SMA_180交叉
'ma_cross_180_360'       # SMA_180与SMA_360交叉
'ema_cross_60_180'       # EMA_60与EMA_180交叉
```

**价格动量:**
```python
'roc_60'                 # 60期变化率
'roc_180'                # 180期变化率
'roc_360'                # 360期变化率
'momentum_60'            # 60期动量
'momentum_180'           # 180期动量
'momentum_360'           # 360期动量
'price_accel_60'         # 60期价格加速度
'price_accel_180'        # 180期价格加速度
'price_accel_360'        # 360期价格加速度
```

**趋势强度:**
```python
'adx_60'                 # 60期平均趋向指标
'adx_180'                # 180期平均趋向指标
'adx_360'                # 360期平均趋向指标
'di_plus_60'             # 60期正向趋向指标
'di_plus_180'            # 180期正向趋向指标
'di_plus_360'            # 360期正向趋向指标
'di_minus_60'            # 60期负向趋向指标
'di_minus_180'           # 180期负向趋向指标
'di_minus_360'           # 360期负向趋向指标
```

**价格位置:**
```python
'price_position_60'      # 价格在60期范围内的位置
'price_position_180'     # 价格在180期范围内的位置
'price_position_360'     # 价格在360期范围内的位置
'higher_high_count_60'   # 60期内创新高次数
'higher_high_count_180'  # 180期内创新高次数
'higher_high_count_360'  # 360期内创新高次数
'lower_low_count_60'     # 60期内创新低次数
'lower_low_count_180'    # 180期内创新低次数
'lower_low_count_360'    # 360期内创新低次数
```

**趋势持续性:**
```python
'trend_consistency_60'   # 60期趋势一致性
'trend_consistency_180'  # 180期趋势一致性
'trend_consistency_360'  # 360期趋势一致性
'trend_strength_idx_60'  # 60期趋势强度指数
'trend_strength_idx_180' # 180期趋势强度指数
'trend_strength_idx_360' # 360期趋势强度指数
'lr_slope_60'            # 60期线性回归斜率
'lr_slope_180'           # 180期线性回归斜率
'lr_slope_360'           # 360期线性回归斜率
'r_squared_60'           # 60期R²
'r_squared_180'          # 180期R²
'r_squared_360'          # 360期R²
```

**MACD:**
```python
'macd_12_26'             # MACD值
'macd_signal_9'          # MACD信号线
'macd_histogram'         # MACD柱状图
```

**多周期综合:**
```python
'multi_tf_trend_align'   # 多周期趋势对齐度
'trend_strength_comp'    # 综合趋势强度
```

### 4. 市场微观结构因子

**价格路径因子:**
```python
'range_utilization'      # 范围利用率
'signed_range_util'      # 带符号范围利用率
'true_strength_proxy'    # 真实强弱代理
```

**价格效率因子:**
```python
'price_efficiency'       # 价格效率
'price_reversal_ind'     # 价格反转指标
```

**成交量分布因子:**
```python
'volume_at_high'         # 高位成交量占比估算
'volume_at_low'          # 低位成交量占比估算
```

### 5. K线形态因子

**基础形态特征:**
```python
'kmid'                   # K线中间价位置
'klen'                   # K线长度比例
'kup'                    # 上影线比例
'klow'                   # 下影线比例
'ksft'                   # K线实体偏移度
```

**非线性平方项:**
```python
'kmid2'                  # K线中间价平方
'kup2'                   # 上影线平方
'klow2'                  # 下影线平方
'ksft2'                  # 实体偏移度平方
```

---

## 10. 因子组合策略建议

### 趋势跟踪策略

1. **多周期趋势确认**:
   - `multi_tf_trend_align = +3` 或 `-3` (三个周期趋势一致)
   - `adx_60 > 25` 且 `adx_180 > 25` (多周期强趋势)
   - `price_to_ema_60` 与 `price_to_ema_180` 同号 (价格在均线同侧)
   - `roc_60` 与 `roc_180` 方向一致
   - 结论: 高可靠性趋势,适合趋势跟踪

2. **趋势启动信号**:
   - `ma_cross_60_180` 由负转正(金叉)或由正转负(死叉)
   - `adx_60` 快速上升且突破20
   - `macd_histogram` 扩张
   - `r_squared_60 > 0.7` (强线性趋势)
   - 结论: 趋势刚启动,及时入场

3. **强趋势持续确认**:
   - `trend_consistency_60 > 0.6` (60期内60%以上同向K线)
   - `higher_high_count_60 > 8` (60期内多次创新高)
   - `lr_slope_60` 与 `lr_slope_180` 同号且增大
   - `signed_range_util` 绝对值 > 0.7 (强单边性)
   - `volume_zscore > 2` (异常放量)
   - 结论: 趋势强劲,可加仓跟随

4. **趋势减弱预警**:
   - `price_accel_60 < 0` (动量减速)
   - `adx_60` 开始下降
   - `macd_histogram` 收敛
   - `range_utilization` 持续下降
   - `volume_ratio < 1` (成交量萎缩)
   - 结论: 趋势动能衰减,考虑减仓

5. **趋势反转信号**:
   - `price_to_sma_60` 穿越0(价格穿越均线)
   - `di_plus_60` 与 `di_minus_60` 交叉
   - `price_position_60` 达到极值后回落(>0.9或<0.1)
   - `trend_consistency_60` 符号改变
   - 结论: 趋势可能反转,及时止损或反向开仓

### 震荡市与均值回归策略

1. **震荡市确认**:
   - `adx_60 < 20` 且 `adx_180 < 20` (多周期弱趋势)
   - `r_squared_60 < 0.3` (价格无明显线性趋势)
   - `trend_consistency_60` 接近0 (±0.2内)
   - `range_utilization < 0.3` (低范围利用率)
   - K线形态多为十字星/纺锤线
   - `price_volume_corr` 接近0
   - 结论: 适合区间交易和均值回归策略

2. **超买超卖信号**:
   - `price_to_sma_60 > 0.05` 或 `< -0.05` (价格偏离均线5%以上)
   - `price_position_60 > 0.85` 或 `< 0.15` (价格处于N期极端位置)
   - `adx_60 < 25` (非强趋势)
   - 结论: 在震荡市中可考虑反向操作

3. **区间边界确认**:
   - `sma_60` 与 `sma_180` 接近水平(斜率接近0)
   - 价格反复触碰 `price_position_60` 的0.9和0.1位置
   - `higher_high_count_60` 和 `lower_low_count_60` 都较低
   - 结论: 明确的震荡区间,适合高抛低吸

4. **突破前兆**:
   - `volume_weighted_vol` 下降(波动收敛)
   - `adx_60` 在低位开始抬头
   - `volume_zscore` 突然放大
   - `range_utilization` 快速上升
   - `macd_histogram` 开始扩张
   - 结论: 可能即将突破,准备趋势跟踪

### 多时间周期验证

- 计算5分钟、15分钟、60分钟多个时间窗口的因子
- 短中长期因子方向一致时,信号可靠性显著提高
- 使用滚动窗口计算因子的均值和趋势

---

## 11. 因子有效性检验

### 单因子测试

1. **信息系数 (IC)**:
   - 计算因子值与未来N期收益的相关性
   - IC绝对值 > 0.03 通常认为有效
   - 关注IC的稳定性和方向一致性

2. **因子单调性**:
   - 将因子分组(如5分位),计算各组平均收益
   - 理想情况下收益应随因子值单调变化

3. **因子衰减**:
   - 测试因子对不同预测期(1分钟、5分钟、15分钟)的有效性
   - 价格路径因子通常在1-5分钟内效果最佳
   - 趋势因子(如ROC_60/180/360)预测能力随时间衰减较慢,适合中长期预测

### 因子组合测试

1. **相关性分析**:
   - 识别高度相关的因子,避免冗余
   - `price_efficiency` 与 `range_utilization` 完全相同
   - `sma_N` 与 `ema_N` 高度相关,可只选其一
   - 同周期的 `roc_N` 与 `momentum_N` 线性相关
   - 不同周期的趋势因子(如ROC_60, ROC_180, ROC_360)提供独立信息,建议保留
   - 选择信息系数最高的因子代表

2. **正交化处理**:
   - 对高相关因子进行正交化,提取独立信息
   - 使用PCA降维保留主要成分

3. **交互效应**:
   - 测试 `signed_range_util × volume_zscore` 等交互项
   - 价格路径因子与波动率、动量因子的组合效果
   - 重要交互项示例:
     - `adx_60 × roc_60`: 趋势强度与动量的组合,强趋势+强动量信号最可靠
     - `price_to_sma_60 × adx_60`: 价格偏离度与趋势强度,在强趋势中偏离度更有效
     - `multi_tf_trend_align × volume_zscore`: 多周期一致性配合放量,突破信号
     - `r_squared_60 × trend_consistency_60`: 线性度与一致性的组合,评估趋势质量

### 市场状态适应性

- **趋势市** vs **震荡市**:
  - 趋势市: 优先使用 ADX, ROC, 均线斜率等趋势因子,权重提升
  - 震荡市: 优先使用 price_position, price_to_sma, R²等均值回归因子
  - 使用ADX_60作为市场状态判别器: ADX>25为趋势市,ADX<20为震荡市

- **高波动** vs **低波动**:
  - 高波动期: 动态调整因子阈值,放宽趋势确认条件
  - 低波动期: 提高阈值,避免虚假信号
  - 使用 high_low_range_pct 或 intrabar_volatility 作为波动率度量

- **多周期一致性**:
  - 60期(1小时): 捕捉短期趋势和快速反转
  - 180期(3小时): 过滤噪音,确认中期趋势
  - 360期(6小时): 识别主导趋势,作为策略方向基准
  - 多周期一致时信号最强,单周期信号需谨慎

- **交易时段**:
  - 开盘和收盘时段特征更明显,趋势因子更有效
  - 午间时段可能震荡,适当降低趋势因子权重
