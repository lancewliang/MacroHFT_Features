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

## 3. 市场微观结构因子 (Market Microstructure Factors)

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

## 4. K线形态因子 (Candlestick Pattern Factors)

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

## 5. K线形态识别参考表

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

## 6. 基础数据字段 (Base OHLCV Data)

- **timestamp**: 时间戳
- **open**: 开盘价
- **high**: 最高价
- **low**: 最低价
- **close**: 收盘价
- **volume**: 成交量

---

## 7. 使用建议

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

## 8. 附录: 完整特征列表

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

### 3. 市场微观结构因子

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

### 4. K线形态因子

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

## 9. 因子组合策略建议

### 趋势识别策略

1. **强趋势确认**:
   - `signed_range_util` 绝对值 > 0.7 (强单边性)
   - `volume_zscore > 2` (异常放量)
   - `price_volume_corr > 0.5` (量价同向)
   - 结论: 趋势强劲,可跟随

2. **趋势减弱信号**:
   - `range_utilization` 持续下降
   - `volume_ratio < 1` (成交量萎缩)
   - `price_reversal_ind > 0.5` (分钟内反转增多)
   - 结论: 趋势动能衰减

### 震荡识别策略

1. **震荡市确认**:
   - `range_utilization < 0.3` (低范围利用率)
   - K线形态多为十字星/纺锤线
   - `price_volume_corr` 接近0
   - 结论: 适合区间交易

2. **突破前兆**:
   - `volume_weighted_vol` 下降(波动收敛)
   - `volume_zscore` 突然放大
   - `range_utilization` 快速上升
   - 结论: 可能即将突破

### 多时间周期验证

- 计算5分钟、15分钟、60分钟多个时间窗口的因子
- 短中长期因子方向一致时,信号可靠性显著提高
- 使用滚动窗口计算因子的均值和趋势

---

## 10. 因子有效性检验

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

### 因子组合测试

1. **相关性分析**:
   - 识别高度相关的因子,避免冗余
   - `price_efficiency` 与 `range_utilization` 完全相同
   - 选择信息系数最高的因子代表

2. **正交化处理**:
   - 对高相关因子进行正交化,提取独立信息
   - 使用PCA降维保留主要成分

3. **交互效应**:
   - 测试 `signed_range_util × volume_zscore` 等交互项
   - 价格路径因子与波动率、动量因子的组合效果

### 市场状态适应性

- **趋势市** vs **震荡市**: 调整因子权重适应不同市场状态
- **高波动** vs **低波动**: 动态调整因子阈值
- **交易时段**: 开盘和收盘时段特征更明显
