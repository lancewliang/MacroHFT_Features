"""
因子计算器使用示例

展示如何使用FactorCalculator进行完整的因子计算流程
"""

import polars as pl
import numpy as np
from pathlib import Path
from factor_calculator import FactorCalculator


def create_sample_data(output_path: str = 'data/sample_ohlcv.feather', n_days: int = 30):
    """
    创建样本OHLCV数据用于演示

    Args:
        output_path: 输出文件路径
        n_days: 生成数据的天数
    """
    print(f"生成 {n_days} 天的样本数据...")

    # 每天1440分钟(24小时 * 60分钟)
    n_minutes = n_days * 1440
    np.random.seed(42)

    # 生成模拟价格序列（几何布朗运动）
    base_price = 100.0
    drift = 0.0001  # 每分钟漂移
    volatility = 0.02  # 每分钟波动率

    returns = np.random.randn(n_minutes) * volatility + drift
    log_prices = np.cumsum(returns)
    close_prices = base_price * np.exp(log_prices)

    # 生成OHLC
    # 高低价基于收盘价波动
    intrabar_vol = np.abs(np.random.randn(n_minutes)) * 0.005
    high_prices = close_prices * (1 + intrabar_vol)
    low_prices = close_prices * (1 - intrabar_vol)

    # 开盘价在高低价之间
    open_prices = low_prices + (high_prices - low_prices) * np.random.rand(n_minutes)

    # 确保OHLC关系正确
    high_prices = np.maximum.reduce([open_prices, high_prices, close_prices])
    low_prices = np.minimum.reduce([open_prices, low_prices, close_prices])

    # 生成成交量（具有一定的周期性和随机性）
    # 添加日内模式：开盘和收盘时段成交量较大
    time_of_day = np.arange(n_minutes) % 1440
    intraday_pattern = 1 + 0.5 * np.sin(2 * np.pi * time_of_day / 1440)  # 日内周期
    base_volume = np.random.lognormal(mean=9, sigma=0.5, size=n_minutes)  # 对数正态分布
    volumes = (base_volume * intraday_pattern).astype(np.int64)

    # 创建DataFrame
    df = pl.DataFrame({
        'timestamp': pl.datetime_range(
            start=pl.datetime(2024, 1, 1, 0, 0),
            end=pl.datetime(2024, 1, 1, 0, 0) + pl.duration(minutes=n_minutes-1),
            interval='1m',
            eager=True
        ),
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })

    # 保存数据
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_ipc(output_path)

    print(f"样本数据已保存到: {output_path}")
    print(f"  - 数据行数: {len(df):,}")
    print(f"  - 时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
    print(f"  - 价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"  - 平均成交量: {df['volume'].mean():.0f}")

    return df


def example_basic_usage():
    """
    示例1: 基本使用流程
    """
    print("\n" + "="*60)
    print("示例1: 基本使用流程")
    print("="*60)

    # 1. 创建样本数据
    create_sample_data('data/sample_ohlcv.feather', n_days=10)

    # 2. 初始化计算器
    calc = FactorCalculator()

    # 3. 加载数据
    calc.load_data('data/sample_ohlcv.feather')

    # 4. 计算所有因子
    df_with_factors = calc.calculate_all_factors()

    # 5. 保存结果
    calc.save_factors('output/factors_all.feather')

    # 6. 查看摘要
    summary = calc.get_factor_summary()
    print(f"\n因子计算完成!")
    print(f"  - 总因子数: {summary['factor_columns']}")
    print(f"  - 数据行数: {summary['total_rows']:,}")

    return df_with_factors


def example_step_by_step():
    """
    示例2: 分步计算因子
    """
    print("\n" + "="*60)
    print("示例2: 分步计算因子")
    print("="*60)

    # 加载数据
    calc = FactorCalculator()
    calc.load_data('data/sample_ohlcv.feather')

    # 只计算流动性因子
    print("\n计算流动性因子...")
    calc.calculate_liquidity_factors()
    print(f"  已添加列: {[col for col in calc.df.columns if 'volume' in col or 'wap' in col][:5]}...")

    # 只计算波动性因子
    print("\n计算波动性因子...")
    calc.calculate_volatility_factors()
    print(f"  已添加列: {[col for col in calc.df.columns if 'volatility' in col or 'range' in col][:5]}...")

    # 只计算趋势因子
    print("\n计算趋势因子...")
    calc.calculate_trend_factors()
    print(f"  已添加列: {[col for col in calc.df.columns if 'sma' in col or 'ema' in col or 'roc' in col][:5]}...")

    return calc.df


def example_custom_analysis():
    """
    示例3: 自定义分析
    """
    print("\n" + "="*60)
    print("示例3: 自定义分析")
    print("="*60)

    # 计算因子
    calc = FactorCalculator()
    calc.load_data('data/sample_ohlcv.feather')
    df = calc.calculate_all_factors()

    # 分析1: 查看强趋势时段
    print("\n分析1: 强趋势时段（ADX_60 > 25）")
    strong_trend = df.filter(pl.col('adx_60') > 25)
    print(f"  强趋势时段占比: {len(strong_trend) / len(df) * 100:.1f}%")

    if len(strong_trend) > 0:
        print(f"  平均ROC_60: {strong_trend['roc_60'].mean():.4f}")
        print(f"  平均成交量: {strong_trend['volume'].mean():.0f}")

    # 分析2: 多周期趋势一致时段
    print("\n分析2: 多周期趋势一致（alignment = ±3）")
    aligned_trend = df.filter(pl.col('multi_tf_trend_align').abs() == 3)
    print(f"  一致趋势时段占比: {len(aligned_trend) / len(df) * 100:.1f}%")

    if len(aligned_trend) > 0:
        up_trend = aligned_trend.filter(pl.col('multi_tf_trend_align') > 0)
        down_trend = aligned_trend.filter(pl.col('multi_tf_trend_align') < 0)
        print(f"  上升趋势: {len(up_trend)} 个时段")
        print(f"  下降趋势: {len(down_trend)} 个时段")

    # 分析3: K线形态分布
    print("\n分析3: K线形态分布")
    # 大阳线: kmid > 0.7
    big_bullish = df.filter(pl.col('kmid') > 0.7)
    # 大阴线: kmid < -0.7
    big_bearish = df.filter(pl.col('kmid') < -0.7)
    # 十字星: |kmid| < 0.1
    doji = df.filter(pl.col('kmid').abs() < 0.1)

    print(f"  大阳线: {len(big_bullish)} ({len(big_bullish)/len(df)*100:.1f}%)")
    print(f"  大阴线: {len(big_bearish)} ({len(big_bearish)/len(df)*100:.1f}%)")
    print(f"  十字星: {len(doji)} ({len(doji)/len(df)*100:.1f}%)")

    # 分析4: 因子相关性
    print("\n分析4: 关键因子间相关性")
    # 选择几个关键因子
    key_factors = ['roc_60', 'adx_60', 'volume_zscore_60', 'signed_range_util']
    correlation_df = df.select(key_factors).drop_nulls()

    if len(correlation_df) > 0:
        # Polars相关性矩阵
        print("  ROC_60 vs ADX_60 相关性:",
              correlation_df['roc_60'].corr(correlation_df['adx_60']))
        print("  ROC_60 vs Volume_ZScore 相关性:",
              correlation_df['roc_60'].corr(correlation_df['volume_zscore_60']))


def example_performance_analysis():
    """
    示例4: 性能分析
    """
    print("\n" + "="*60)
    print("示例4: 性能分析")
    print("="*60)

    import time

    # 测试不同数据量的计算时间
    for n_days in [1, 7, 30]:
        print(f"\n测试 {n_days} 天数据...")

        # 创建数据
        create_sample_data('data/temp_data.feather', n_days=n_days)

        # 计算因子
        calc = FactorCalculator()
        calc.load_data('data/temp_data.feather')

        start_time = time.time()
        calc.calculate_all_factors()
        elapsed_time = time.time() - start_time

        n_rows = len(calc.df)
        n_factors = calc.get_factor_summary()['factor_columns']

        print(f"  数据行数: {n_rows:,}")
        print(f"  因子数量: {n_factors}")
        print(f"  计算时间: {elapsed_time:.2f} 秒")
        print(f"  速度: {n_rows/elapsed_time:.0f} 行/秒")


def example_export_to_csv():
    """
    示例5: 导出特定因子到CSV进行分析
    """
    print("\n" + "="*60)
    print("示例5: 导出特定因子到CSV")
    print("="*60)

    # 加载并计算因子
    calc = FactorCalculator()
    calc.load_data('data/sample_ohlcv.feather')
    df = calc.calculate_all_factors()

    # 选择要导出的因子
    export_columns = [
        'timestamp', 'close', 'volume',
        'roc_60', 'roc_180', 'roc_360',
        'adx_60', 'adx_180', 'adx_360',
        'sma_60', 'ema_60',
        'volume_zscore_60',
        'kmid', 'kup', 'klow'
    ]

    # 导出到CSV
    output_path = Path('output/key_factors.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.select(export_columns).write_csv(output_path)
    print(f"\n关键因子已导出到: {output_path}")
    print(f"  导出列数: {len(export_columns)}")


def main():
    """
    运行所有示例
    """
    print("\n" + "="*60)
    print("MacroHFT Features - 因子计算器使用示例")
    print("="*60)

    # 示例1: 基本使用
    example_basic_usage()

    # 示例2: 分步计算
    example_step_by_step()

    # 示例3: 自定义分析
    example_custom_analysis()

    # 示例4: 性能分析
    example_performance_analysis()

    # 示例5: 导出CSV
    example_export_to_csv()

    print("\n" + "="*60)
    print("所有示例运行完成!")
    print("="*60)


if __name__ == '__main__':
    main()
