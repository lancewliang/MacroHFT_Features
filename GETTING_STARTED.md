# 快速上手指南

欢迎使用MacroHFT Features因子计算库！

## 📦 已创建的文件

### 核心文件
- `factor_calculator.py` - 主因子计算库（核心代码）
- `config.py` - 配置文件（可调整参数）
- `factor.md` - 完整的因子定义文档

### 测试和示例
- `test_factor_calculator.py` - 完整的单元测试套件
- `example_usage.py` - 详细的使用示例
- `quick_start.py` - 一键启动脚本

### 文档
- `README_FACTOR_CALCULATOR.md` - 详细使用文档
- `GETTING_STARTED.md` - 本文件（快速上手）
- `requirements.txt` - 依赖列表

## 🚀 5分钟快速开始

### 步骤1: 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `polars>=0.20.0` - 高性能数据处理
- `numpy>=1.24.0` - 数值计算
- `pytest>=7.4.0` - 单元测试

### 步骤2: 运行快速启动脚本

```bash
python quick_start.py
```

这将：
1. 自动生成30天的样本OHLCV数据
2. 计算所有100+个因子
3. 保存结果到 `output/factors_quick_start.feather`
4. 显示计算摘要

### 步骤3: 查看结果

```python
import polars as pl

# 加载计算好的因子
df = pl.read_ipc('output/factors_quick_start.feather')

# 查看数据
print(df.head())
print(f"共 {len(df.columns)} 列")

# 查看特定因子
print(df.select(['timestamp', 'close', 'roc_60', 'adx_60', 'sma_60']).tail(10))
```

## 📖 使用自己的数据

### 数据格式要求

你的数据必须是Feather格式，包含以下列：

```python
{
    'timestamp': datetime,  # 时间戳
    'open': float,          # 开盘价
    'high': float,          # 最高价
    'low': float,           # 最低价
    'close': float,         # 收盘价
    'volume': int/float     # 成交量
}
```

### 使用自己的数据

```bash
# 方式1: 使用快速启动脚本
python quick_start.py --input data/your_data.feather --output output/your_factors.feather

# 方式2: 使用Python代码
python
```

```python
from factor_calculator import FactorCalculator

calc = FactorCalculator()
calc.load_data('data/your_data.feather')
df = calc.calculate_all_factors()
calc.save_factors('output/your_factors.feather')
```

## 🧪 运行测试

验证代码正确性：

```bash
# 运行所有测试
pytest test_factor_calculator.py -v

# 运行特定测试
pytest test_factor_calculator.py::TestLiquidityFactors -v

# 生成覆盖率报告
pytest test_factor_calculator.py --cov=factor_calculator --cov-report=html
```

## 📊 查看示例

运行完整示例代码：

```bash
python example_usage.py
```

包含5个示例：
1. 基本使用流程
2. 分步计算因子
3. 自定义分析
4. 性能分析
5. 导出特定因子到CSV

## 🔧 常见操作

### 只计算特定类别的因子

```python
from factor_calculator import FactorCalculator

calc = FactorCalculator()
calc.load_data('data/ohlcv.feather')

# 只计算流动性和趋势因子
calc.calculate_liquidity_factors()
calc.calculate_trend_factors()

calc.save_factors('output/selected_factors.feather')
```

### 调整因子参数

编辑 `config.py` 文件：

```python
# 修改趋势窗口
TREND_CONFIG = {
    'ma_windows': [30, 90, 180],  # 改为30分钟、1.5小时、3小时
}

# 修改MACD参数
TREND_CONFIG = {
    'macd': {
        'fast': 8,
        'slow': 21,
        'signal': 5
    }
}
```

### 转换数据格式

如果你的数据是CSV或Parquet：

```python
import polars as pl

# 从CSV转换到Feather
df = pl.read_csv('data/ohlcv.csv')
df.write_ipc('data/ohlcv.feather')

# 从Parquet转换到Feather
df = pl.read_parquet('data/ohlcv.parquet')
df.write_ipc('data/ohlcv.feather')
```

## 📚 因子列表

### 已实现的因子（100+个）

#### 1. 流动性因子 (15个)
- WAP, VWAP
- log_return_wap_1/2
- volume_trend_60
- volume_zscore (3个窗口)
- turnover_zscore (3个窗口)
- volume_ratio (2组)
- volume_acceleration (2个)
- price_volume_corr (3个窗口)

#### 2. 波动性因子 (5个)
- intrabar_volatility
- high_low_range
- high_low_range_pct
- volume_weighted_vol
- liquidity_cost_proxy

#### 3. 趋势因子 (60+个)
- SMA/EMA (各3个窗口)
- price_to_sma/ema (各3个窗口)
- sma_slope/ema_slope (各3个窗口)
- ma_cross (3组)
- ROC/momentum/price_accel (各3个窗口)
- ADX/DI+/DI- (各3个窗口)
- price_position/higher_high_count/lower_low_count (各3个窗口)
- trend_consistency/trend_strength_idx (各3个窗口)
- linear_regression/r_squared (各3个窗口)
- MACD系列 (3个)
- 多周期综合 (2个)

#### 4. 微观结构因子 (7个)
- range_utilization
- signed_range_util
- true_strength_proxy
- price_efficiency
- price_reversal_ind
- volume_at_high
- volume_at_low

#### 5. K线形态因子 (9个)
- kmid, klen, kup, klow, ksft
- kmid2, kup2, klow2, ksft2

## ⚡ 性能优化

### 提升计算速度

1. **使用Polars的并行能力**（自动）
2. **分批处理大数据集**：

```python
import polars as pl

# 按月份分批
months = ['2024-01', '2024-02', '2024-03']
for month in months:
    calc = FactorCalculator()
    calc.load_data(f'data/{month}.feather')
    calc.calculate_all_factors()
    calc.save_factors(f'output/factors_{month}.feather')
```

3. **只计算需要的因子**：

```python
# 修改 config.py
FACTOR_SELECTION = {
    'calculate_liquidity': True,
    'calculate_volatility': False,  # 跳过
    'calculate_trend': True,
    'calculate_microstructure': False,  # 跳过
    'calculate_candlestick': True,
}
```

## 🐛 故障排除

### 问题1: 安装Polars失败

```bash
# 尝试升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple polars
```

### 问题2: 计算结果有很多NaN

这是正常的！滚动窗口因子在开始的N行会是NaN。

```python
# 查看数据从哪里开始完整
df_clean = df.drop_nulls()
print(f"完整数据从第 {len(df) - len(df_clean)} 行开始")
```

### 问题3: 内存不足

```python
# 分批处理
batch_size = 10000
for i in range(0, len(df), batch_size):
    batch_df = df.slice(i, batch_size)
    # 处理batch_df
```

## 📞 获取帮助

1. 查看详细文档：`README_FACTOR_CALCULATOR.md`
2. 查看因子定义：`factor.md`
3. 查看使用示例：`example_usage.py`
4. 运行测试了解用法：`test_factor_calculator.py`

## ✅ 下一步

- [ ] 计算因子
- [ ] 进行因子有效性测试（IC、单调性）
- [ ] 因子筛选和去冗余
- [ ] 构建量化策略
- [ ] 回测验证

## 🎯 实用命令速查

```bash
# 生成样本数据
python quick_start.py --sample-only --sample-days 10

# 使用自己的数据
python quick_start.py -i data/my_data.feather -o output/my_factors.feather

# 运行测试
pytest test_factor_calculator.py -v

# 查看示例
python example_usage.py

# 查看配置
python config.py
```

---

**祝你使用愉快！** 🚀

如有问题，请查看详细文档或运行测试代码了解更多用法。
