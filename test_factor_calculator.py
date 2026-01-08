"""
因子计算器单元测试

使用pytest框架进行测试
运行方式: pytest test_factor_calculator.py -v
"""

import pytest
import polars as pl
import numpy as np
from pathlib import Path
from factor_calculator import FactorCalculator


@pytest.fixture
def sample_data():
    """
    创建测试用的样本OHLCV数据

    Returns:
        pl.DataFrame: 包含100行测试数据的DataFrame
    """
    np.random.seed(42)
    n = 500  # 需要足够多的数据来测试滚动窗口因子

    # 生成模拟价格数据
    base_price = 100
    returns = np.random.randn(n) * 0.02  # 2%标准差
    close = base_price * np.exp(np.cumsum(returns))

    # 生成OHLC
    high = close * (1 + np.abs(np.random.randn(n) * 0.01))
    low = close * (1 - np.abs(np.random.randn(n) * 0.01))
    open_price = close * (1 + np.random.randn(n) * 0.005)

    # 生成成交量
    volume = np.random.randint(1000, 10000, n)

    df = pl.DataFrame({
        'timestamp': pl.datetime_range(
            start=pl.datetime(2024, 1, 1),
            end=pl.datetime(2024, 1, 1) + pl.duration(minutes=n-1),
            interval='1m',
            eager=True
        ),
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })

    return df


@pytest.fixture
def calculator(sample_data):
    """
    创建已加载测试数据的FactorCalculator实例

    Args:
        sample_data: 样本数据fixture

    Returns:
        FactorCalculator: 初始化好的计算器实例
    """
    calc = FactorCalculator(df=sample_data)
    return calc


class TestLiquidityFactors:
    """流动性因子测试类"""

    def test_wap_calculation(self, calculator):
        """测试WAP计算"""
        df = calculator.calculate_liquidity_factors()

        # WAP应该是(H+L+C)/3
        assert 'wap' in df.columns
        assert df['wap'].null_count() == 0

        # 手动验证第一行
        expected_wap = (df['high'][0] + df['low'][0] + df['close'][0]) / 3
        assert abs(df['wap'][0] - expected_wap) < 1e-6

    def test_log_return_calculation(self, calculator):
        """测试对数收益率计算"""
        df = calculator.calculate_liquidity_factors()

        assert 'log_return_wap_1' in df.columns
        assert 'log_return_wap_2' in df.columns

        # 第一行应该是null（没有前值）
        assert df['log_return_wap_1'][0] is None or np.isnan(df['log_return_wap_1'][0])

        # 第二行开始应该有值
        assert not np.isnan(df['log_return_wap_1'][1])

    def test_volume_trend_60(self, calculator):
        """测试60期成交量趋势指标"""
        df = calculator.calculate_liquidity_factors()

        assert 'volume_trend_60' in df.columns

        # 前60行可能是null或有值，但第61行之后应该都有值
        non_null_from = df['volume_trend_60'][60:].null_count()
        assert non_null_from < len(df) - 60  # 允许一些null，但不应该全是null

    def test_volume_zscore(self, calculator):
        """测试成交量Z-Score"""
        df = calculator.calculate_liquidity_factors()

        for window in [30, 60, 100]:
            col_name = f'volume_zscore_{window}'
            assert col_name in df.columns

            # Z-Score的值域检查（大部分应该在-3到3之间）
            valid_data = df[col_name].drop_nulls()
            if len(valid_data) > 0:
                # 大部分值应该在合理范围内
                in_range = ((valid_data > -5) & (valid_data < 5)).sum()
                assert in_range / len(valid_data) > 0.9  # 90%以上在合理范围

    def test_volume_ratio(self, calculator):
        """测试成交量比率"""
        df = calculator.calculate_liquidity_factors()

        assert 'volume_ratio_5_30' in df.columns
        assert 'volume_ratio_10_60' in df.columns

        # 比率应该大于0
        valid_data = df['volume_ratio_5_30'].drop_nulls()
        if len(valid_data) > 0:
            assert (valid_data > 0).all()


class TestVolatilityFactors:
    """波动性因子测试类"""

    def test_intrabar_volatility(self, calculator):
        """测试分钟内波动率"""
        calculator.calculate_liquidity_factors()  # 先计算依赖的因子
        df = calculator.calculate_volatility_factors()

        assert 'intrabar_volatility' in df.columns

        # 波动率应该非负
        assert (df['intrabar_volatility'] >= 0).all()

        # 手动验证第一行
        expected = (df['high'][0] - df['low'][0]) / df['open'][0]
        assert abs(df['intrabar_volatility'][0] - expected) < 1e-6

    def test_high_low_range(self, calculator):
        """测试最高最低价差"""
        calculator.calculate_liquidity_factors()
        df = calculator.calculate_volatility_factors()

        assert 'high_low_range' in df.columns
        assert 'high_low_range_pct' in df.columns

        # Range应该非负
        assert (df['high_low_range'] >= 0).all()

        # Range应该等于High - Low
        expected = df['high'] - df['low']
        assert ((df['high_low_range'] - expected).abs() < 1e-6).all()

    def test_volume_weighted_vol(self, calculator):
        """测试单位成交量波动率"""
        calculator.calculate_liquidity_factors()
        df = calculator.calculate_volatility_factors()

        assert 'volume_weighted_vol' in df.columns

        # 应该是正数
        assert (df['volume_weighted_vol'] >= 0).all()


class TestTrendFactors:
    """趋势因子测试类"""

    def test_moving_averages(self, calculator):
        """测试移动平均线"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        for window in [60, 180, 360]:
            assert f'sma_{window}' in df.columns
            assert f'ema_{window}' in df.columns

            # SMA应该是收盘价的平均
            sma_col = df[f'sma_{window}']
            # 检查非null值的范围是否合理
            valid_sma = sma_col.drop_nulls()
            if len(valid_sma) > 0:
                close_min = df['close'].min()
                close_max = df['close'].max()
                assert (valid_sma >= close_min * 0.5).all()  # 允许一定偏差
                assert (valid_sma <= close_max * 1.5).all()

    def test_price_to_ma(self, calculator):
        """测试价格与均线关系"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        for window in [60, 180, 360]:
            assert f'price_to_sma_{window}' in df.columns
            assert f'price_to_ema_{window}' in df.columns

    def test_roc(self, calculator):
        """测试变化率(ROC)"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        for window in [60, 180, 360]:
            assert f'roc_{window}' in df.columns
            assert f'momentum_{window}' in df.columns

            # ROC的值域检查（通常在-1到1之间，极端情况可能更大）
            valid_roc = df[f'roc_{window}'].drop_nulls()
            if len(valid_roc) > 0:
                # 大部分值应该在合理范围
                in_range = ((valid_roc > -0.5) & (valid_roc < 0.5)).sum()
                assert in_range / len(valid_roc) > 0.8  # 80%以上在±50%内

    def test_adx_factors(self, calculator):
        """测试ADX相关因子"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        for window in [60, 180, 360]:
            assert f'adx_{window}' in df.columns
            assert f'di_plus_{window}' in df.columns
            assert f'di_minus_{window}' in df.columns

            # ADX和DI应该在0-100之间
            valid_adx = df[f'adx_{window}'].drop_nulls()
            if len(valid_adx) > 0:
                assert (valid_adx >= 0).all()
                assert (valid_adx <= 100).all()

    def test_macd(self, calculator):
        """测试MACD因子"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        assert 'macd_12_26' in df.columns
        assert 'macd_signal_9' in df.columns
        assert 'macd_histogram' in df.columns

        # MACD Histogram应该等于MACD - Signal
        valid_idx = ~df['macd_histogram'].is_null()
        if valid_idx.sum() > 0:
            expected = df['macd_12_26'] - df['macd_signal_9']
            diff = (df['macd_histogram'] - expected).abs()
            assert (diff[valid_idx] < 1e-6).all()

    def test_multi_timeframe_alignment(self, calculator):
        """测试多周期趋势对齐度"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        df = calculator.calculate_trend_factors()

        assert 'multi_tf_trend_align' in df.columns

        # 值应该在-3到+3之间
        valid_data = df['multi_tf_trend_align'].drop_nulls()
        if len(valid_data) > 0:
            assert (valid_data >= -3).all()
            assert (valid_data <= 3).all()


class TestMicrostructureFactors:
    """市场微观结构因子测试类"""

    def test_range_utilization(self, calculator):
        """测试范围利用率"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        df = calculator.calculate_microstructure_factors()

        assert 'range_utilization' in df.columns
        assert 'signed_range_util' in df.columns

        # Range utilization应该在0-1之间
        assert (df['range_utilization'] >= 0).all()
        assert (df['range_utilization'] <= 1).all()

        # Signed range util应该在-1到1之间
        assert (df['signed_range_util'] >= -1).all()
        assert (df['signed_range_util'] <= 1).all()

    def test_price_efficiency(self, calculator):
        """测试价格效率"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        df = calculator.calculate_microstructure_factors()

        assert 'price_efficiency' in df.columns
        assert 'price_reversal_ind' in df.columns


class TestCandlestickFactors:
    """K线形态因子测试类"""

    def test_kmid_calculation(self, calculator):
        """测试K线中间价位置"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        calculator.calculate_microstructure_factors()
        df = calculator.calculate_candlestick_factors()

        assert 'kmid' in df.columns

        # KMID应该在-1到1之间
        assert (df['kmid'] >= -1.1).all()  # 允许小误差
        assert (df['kmid'] <= 1.1).all()

    def test_kup_klow(self, calculator):
        """测试上下影线比例"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        calculator.calculate_microstructure_factors()
        df = calculator.calculate_candlestick_factors()

        assert 'kup' in df.columns
        assert 'klow' in df.columns

        # KUP和KLOW应该在0-1之间
        assert (df['kup'] >= 0).all()
        assert (df['kup'] <= 1).all()
        assert (df['klow'] >= 0).all()
        assert (df['klow'] <= 1).all()

        # KUP + KLOW + |KMID| * (H-L中实体占比) 应该约等于1
        # 简化检查：kup + klow应该 <= 1
        assert ((df['kup'] + df['klow']) <= 1.01).all()  # 允许小误差

    def test_squared_features(self, calculator):
        """测试平方项特征"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        calculator.calculate_microstructure_factors()
        df = calculator.calculate_candlestick_factors()

        for feature in ['kmid', 'kup', 'klow', 'ksft']:
            squared_col = f'{feature}2'
            assert squared_col in df.columns

            # 平方值应该等于原值的平方
            expected = df[feature] ** 2
            diff = (df[squared_col] - expected).abs()
            assert (diff < 1e-6).all()

    def test_volume_distribution(self, calculator):
        """测试成交量分布因子"""
        calculator.calculate_liquidity_factors()
        calculator.calculate_volatility_factors()
        calculator.calculate_trend_factors()
        calculator.calculate_microstructure_factors()
        df = calculator.calculate_candlestick_factors()

        assert 'volume_at_high' in df.columns
        assert 'volume_at_low' in df.columns

        # 应该非负
        assert (df['volume_at_high'] >= 0).all()
        assert (df['volume_at_low'] >= 0).all()


class TestIntegration:
    """集成测试类"""

    def test_calculate_all_factors(self, calculator):
        """测试计算所有因子"""
        df = calculator.calculate_all_factors()

        # 检查数据行数未改变
        assert len(df) == len(calculator.df)

        # 检查关键因子列存在
        key_factors = [
            'wap', 'log_return_wap_1',
            'volume_trend_60', 'volume_zscore_60',
            'intrabar_volatility', 'high_low_range',
            'sma_60', 'ema_60', 'roc_60', 'adx_60',
            'range_utilization', 'signed_range_util',
            'kmid', 'kup', 'klow'
        ]

        for factor in key_factors:
            assert factor in df.columns, f"Missing factor: {factor}"

    def test_no_infinite_values(self, calculator):
        """测试没有无穷值"""
        df = calculator.calculate_all_factors()

        # 检查所有数值列没有无穷值
        for col in df.columns:
            if df[col].dtype in [pl.Float32, pl.Float64]:
                finite_count = df[col].drop_nulls().is_finite().sum()
                total_non_null = len(df[col].drop_nulls())
                if total_non_null > 0:
                    # 允许极少量的无穷值（可能由于极端数据）
                    assert finite_count / total_non_null > 0.99, f"Too many infinite values in {col}"

    def test_factor_summary(self, calculator):
        """测试因子摘要功能"""
        calculator.calculate_all_factors()
        summary = calculator.get_factor_summary()

        assert 'total_rows' in summary
        assert 'total_columns' in summary
        assert 'factor_columns' in summary
        assert summary['total_rows'] == len(calculator.df)
        assert summary['factor_columns'] > 0


class TestDataIO:
    """数据IO测试类"""

    def test_save_and_load_feather(self, calculator, tmp_path):
        """测试保存和加载feather格式"""
        # 计算因子
        calculator.calculate_all_factors()

        # 保存
        output_file = tmp_path / "test_factors.feather"
        calculator.save_factors(output_file, format='feather')

        assert output_file.exists()

        # 重新加载并验证
        loaded_df = pl.read_ipc(output_file)
        assert len(loaded_df) == len(calculator.df)
        assert loaded_df.columns == calculator.df.columns

    def test_save_parquet(self, calculator, tmp_path):
        """测试保存parquet格式"""
        calculator.calculate_all_factors()

        output_file = tmp_path / "test_factors.parquet"
        calculator.save_factors(output_file, format='parquet')

        assert output_file.exists()

        # 验证可以读取
        loaded_df = pl.read_parquet(output_file)
        assert len(loaded_df) == len(calculator.df)


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
