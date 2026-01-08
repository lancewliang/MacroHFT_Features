"""
MacroHFT Features - Factor Calculator
基于OHLCV分钟级数据的因子计算库

使用Polars库实现高性能多核并行计算
支持feather格式数据读取

Author: Generated from factor.md
Python Version: 3.11+
"""

import polars as pl
import numpy as np
from pathlib import Path
from typing import Union, List, Optional


class FactorCalculator:
    """
    因子计算器主类

    使用Polars实现高性能因子计算，支持多核并行处理大规模分钟级OHLCV数据

    Attributes:
        df: Polars DataFrame，包含OHLCV数据
        epsilon: 防止除零的极小值
    """

    def __init__(self, df: Optional[pl.DataFrame] = None, epsilon: float = 1e-8):
        """
        初始化因子计算器

        Args:
            df: Polars DataFrame，包含timestamp, open, high, low, close, volume列
            epsilon: 防止除零的极小值，默认1e-8
        """
        self.df = df
        self.epsilon = epsilon

    def load_data(self, file_path: Union[str, Path]) -> pl.DataFrame:
        """
        从feather文件加载OHLCV数据

        Args:
            file_path: feather文件路径

        Returns:
            pl.DataFrame: 加载的数据

        Example:
            >>> calc = FactorCalculator()
            >>> df = calc.load_data('data/ohlcv.feather')
        """
        self.df = pl.read_ipc(file_path)

        # 验证必需列
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"缺少必需列: {missing_cols}")

        # 确保按时间排序
        self.df = self.df.sort('timestamp')

        print(f"数据加载成功: {len(self.df)} 行, {len(self.df.columns)} 列")
        return self.df

    def calculate_all_factors(self) -> pl.DataFrame:
        """
        计算所有因子

        按顺序调用各个因子计算方法，返回包含所有因子的DataFrame

        Returns:
            pl.DataFrame: 包含原始数据和所有计算因子的DataFrame
        """
        if self.df is None:
            raise ValueError("请先加载数据或提供DataFrame")

        print("开始计算因子...")

        # 1. 流动性因子
        print("  [1/5] 计算流动性因子...")
        self.df = self.calculate_liquidity_factors()

        # 2. 波动性因子
        print("  [2/5] 计算波动性因子...")
        self.df = self.calculate_volatility_factors()

        # 3. 趋势因子
        print("  [3/5] 计算趋势因子...")
        self.df = self.calculate_trend_factors()

        # 4. 市场微观结构因子
        print("  [4/5] 计算市场微观结构因子...")
        self.df = self.calculate_microstructure_factors()

        # 5. K线形态因子
        print("  [5/5] 计算K线形态因子...")
        self.df = self.calculate_candlestick_factors()

        print(f"因子计算完成! 总列数: {len(self.df.columns)}")
        return self.df

    def calculate_liquidity_factors(self) -> pl.DataFrame:
        """
        计算流动性因子

        包括：
        - 成交量加权价格因子 (WAP, VWAP)
        - 对数收益率因子 (log_return_wap_1/2)
        - 成交量趋势因子 (volume_trend_60)
        - 成交量异常因子 (volume_zscore, turnover_zscore, volume_ratio, volume_acceleration)
        - 量价关系因子 (price_volume_corr)

        Returns:
            pl.DataFrame: 添加了流动性因子的DataFrame
        """
        df = self.df
        eps = self.epsilon

        # 成交量加权价格因子
        # WAP = (∑(价格_i × 数量_i)) / ∑数量_i
        # 注: 分钟级OHLCV数据没有逐笔数据，使用典型价格作为代理
        df = df.with_columns([
            ((pl.col('high') + pl.col('low') + pl.col('close')) / 3).alias('wap'),
        ])

        # VWAP = 累积(价格 × 成交量) / 累积成交量
        # 使用滚动窗口计算VWAP
        df = df.with_columns([
            (pl.col('wap') * pl.col('volume')).alias('price_volume')
        ])

        # 对数收益率因子
        df = df.with_columns([
            (pl.col('wap').log() - pl.col('wap').shift(1).log()).alias('log_return_wap_1'),
            (pl.col('wap').log() - pl.col('wap').shift(2).log()).alias('log_return_wap_2'),
        ])

        # 成交量趋势因子 - 60期
        # volume_trend_60 = (Volume - MA(Volume, 60)) / Std(Volume, 60)
        df = df.with_columns([
            (
                (pl.col('volume') - pl.col('volume').rolling_mean(60)) /
                (pl.col('volume').rolling_std(60) + eps)
            ).alias('volume_trend_60')
        ])

        # 成交量异常因子
        # Volume Z-Score (多个窗口)
        for window in [30, 60, 100]:
            df = df.with_columns([
                (
                    (pl.col('volume') - pl.col('volume').rolling_mean(window)) /
                    (pl.col('volume').rolling_std(window) + eps)
                ).alias(f'volume_zscore_{window}')
            ])

        # Turnover Z-Score
        # turnover = Volume × (High + Low + Close) / 3
        df = df.with_columns([
            (pl.col('volume') * (pl.col('high') + pl.col('low') + pl.col('close')) / 3).alias('turnover')
        ])

        for window in [30, 60, 100]:
            df = df.with_columns([
                (
                    (pl.col('turnover') - pl.col('turnover').rolling_mean(window)) /
                    (pl.col('turnover').rolling_std(window) + eps)
                ).alias(f'turnover_zscore_{window}')
            ])

        # Volume Ratio - 短期/长期成交量比率
        df = df.with_columns([
            (pl.col('volume').rolling_mean(5) / (pl.col('volume').rolling_mean(30) + eps)).alias('volume_ratio_5_30'),
            (pl.col('volume').rolling_mean(10) / (pl.col('volume').rolling_mean(60) + eps)).alias('volume_ratio_10_60'),
        ])

        # Volume Acceleration - 成交量加速度
        df = df.with_columns([
            (pl.col('volume') / (pl.col('volume').ewm_mean(span=20) + eps)).alias('volume_acceleration_20'),
            (pl.col('volume') / (pl.col('volume').ewm_mean(span=60) + eps)).alias('volume_acceleration_60'),
        ])

        # 量价关系因子 - 滚动相关性
        # Rolling correlation between returns and volume
        for window in [5, 10, 20]:
            df = df.with_columns([
                pl.col('log_return_wap_1').rolling_corr(pl.col('volume'), window_size=window)
                .alias(f'price_volume_corr_{window}')
            ])

        return df

    def calculate_volatility_factors(self) -> pl.DataFrame:
        """
        计算波动性因子

        包括：
        - 基础波动率 (intrabar_volatility, high_low_range, high_low_range_pct)
        - 流动性调整波动率 (volume_weighted_vol, liquidity_cost_proxy)

        Returns:
            pl.DataFrame: 添加了波动性因子的DataFrame
        """
        df = self.df
        eps = self.epsilon

        # 基础波动率
        # Intrabar Volatility = (High - Low) / Open
        df = df.with_columns([
            ((pl.col('high') - pl.col('low')) / (pl.col('open') + eps)).alias('intrabar_volatility')
        ])

        # High-Low Range
        df = df.with_columns([
            (pl.col('high') - pl.col('low')).alias('high_low_range')
        ])

        # High-Low Range Percentage
        df = df.with_columns([
            ((pl.col('high') - pl.col('low')) / (pl.col('close') + eps)).alias('high_low_range_pct')
        ])

        # 流动性调整波动率
        # Volume Weighted Volatility = Intrabar_Volatility / Volume
        df = df.with_columns([
            (pl.col('intrabar_volatility') / (pl.col('volume') + eps)).alias('volume_weighted_vol')
        ])

        # Liquidity Cost Proxy
        df = df.with_columns([
            (
                (pl.col('high') - pl.col('low')) /
                (pl.col('volume') * pl.col('close') + eps)
            ).alias('liquidity_cost_proxy')
        ])

        return df

    def calculate_trend_factors(self) -> pl.DataFrame:
        """
        计算趋势因子

        包括三个时间窗口：60期(1小时), 180期(3小时), 360期(6小时)

        包括：
        - 移动平均线因子 (SMA, EMA)
        - 价格与均线关系 (price_to_sma, price_to_ema)
        - 均线斜率 (sma_slope, ema_slope)
        - 均线交叉 (ma_cross)
        - 价格动量 (ROC, momentum, price_acceleration)
        - 趋势强度 (ADX, DI+, DI-)
        - 价格位置 (price_position, higher_high_count, lower_low_count)
        - 趋势持续性 (trend_consistency, trend_strength_index, linear_regression)
        - MACD因子
        - 多周期综合因子

        Returns:
            pl.DataFrame: 添加了趋势因子的DataFrame
        """
        df = self.df
        eps = self.epsilon
        windows = [60, 180, 360]  # 1小时, 3小时, 6小时

        # ========== 移动平均线因子 ==========
        for window in windows:
            # SMA
            df = df.with_columns([
                pl.col('close').rolling_mean(window).alias(f'sma_{window}')
            ])

            # EMA
            df = df.with_columns([
                pl.col('close').ewm_mean(span=window).alias(f'ema_{window}')
            ])

        # ========== 价格与均线关系 ==========
        for window in windows:
            # Price to SMA
            df = df.with_columns([
                (
                    (pl.col('close') - pl.col(f'sma_{window}')) /
                    (pl.col(f'sma_{window}') + eps)
                ).alias(f'price_to_sma_{window}')
            ])

            # Price to EMA
            df = df.with_columns([
                (
                    (pl.col('close') - pl.col(f'ema_{window}')) /
                    (pl.col(f'ema_{window}') + eps)
                ).alias(f'price_to_ema_{window}')
            ])

        # ========== 均线斜率 ==========
        slope_period = 5  # 用5期计算斜率
        for window in windows:
            # SMA Slope
            df = df.with_columns([
                (
                    (pl.col(f'sma_{window}') - pl.col(f'sma_{window}').shift(slope_period)) /
                    (pl.col(f'sma_{window}').shift(slope_period) + eps)
                ).alias(f'sma_slope_{window}')
            ])

            # EMA Slope
            df = df.with_columns([
                (
                    (pl.col(f'ema_{window}') - pl.col(f'ema_{window}').shift(slope_period)) /
                    (pl.col(f'ema_{window}').shift(slope_period) + eps)
                ).alias(f'ema_slope_{window}')
            ])

        # ========== 均线交叉 ==========
        # MA Cross 60-180
        df = df.with_columns([
            ((pl.col('sma_60') - pl.col('sma_180')) / (pl.col('sma_180') + eps)).alias('ma_cross_60_180')
        ])

        # MA Cross 180-360
        df = df.with_columns([
            ((pl.col('sma_180') - pl.col('sma_360')) / (pl.col('sma_360') + eps)).alias('ma_cross_180_360')
        ])

        # EMA Cross 60-180
        df = df.with_columns([
            ((pl.col('ema_60') - pl.col('ema_180')) / (pl.col('ema_180') + eps)).alias('ema_cross_60_180')
        ])

        # ========== 价格动量 ==========
        for window in windows:
            # ROC (Rate of Change)
            df = df.with_columns([
                (
                    (pl.col('close') - pl.col('close').shift(window)) /
                    (pl.col('close').shift(window) + eps)
                ).alias(f'roc_{window}')
            ])

            # Momentum
            df = df.with_columns([
                (pl.col('close') - pl.col('close').shift(window)).alias(f'momentum_{window}')
            ])

            # Price Acceleration
            df = df.with_columns([
                (pl.col(f'roc_{window}') - pl.col(f'roc_{window}').shift(slope_period)).alias(f'price_accel_{window}')
            ])

        # ========== 趋势强度因子 (ADX, DI+, DI-) ==========
        # 计算+DM, -DM, TR
        df = df.with_columns([
            # +DM = High_t - High_{t-1} (if positive and > -DM)
            pl.when(
                (pl.col('high') - pl.col('high').shift(1) > 0) &
                (pl.col('high') - pl.col('high').shift(1) > pl.col('low').shift(1) - pl.col('low'))
            )
            .then(pl.col('high') - pl.col('high').shift(1))
            .otherwise(0.0)
            .alias('plus_dm'),

            # -DM = Low_{t-1} - Low_t (if positive and > +DM)
            pl.when(
                (pl.col('low').shift(1) - pl.col('low') > 0) &
                (pl.col('low').shift(1) - pl.col('low') > pl.col('high') - pl.col('high').shift(1))
            )
            .then(pl.col('low').shift(1) - pl.col('low'))
            .otherwise(0.0)
            .alias('minus_dm'),

            # True Range
            pl.max_horizontal([
                pl.col('high') - pl.col('low'),
                (pl.col('high') - pl.col('close').shift(1)).abs(),
                (pl.col('low') - pl.col('close').shift(1)).abs()
            ]).alias('true_range')
        ])

        for window in windows:
            # Smoothed +DM, -DM, TR using EMA
            df = df.with_columns([
                pl.col('plus_dm').ewm_mean(span=window).alias(f'plus_dm_ema_{window}'),
                pl.col('minus_dm').ewm_mean(span=window).alias(f'minus_dm_ema_{window}'),
                pl.col('true_range').ewm_mean(span=window).alias(f'tr_ema_{window}')
            ])

            # +DI, -DI
            df = df.with_columns([
                (100 * pl.col(f'plus_dm_ema_{window}') / (pl.col(f'tr_ema_{window}') + eps)).alias(f'di_plus_{window}'),
                (100 * pl.col(f'minus_dm_ema_{window}') / (pl.col(f'tr_ema_{window}') + eps)).alias(f'di_minus_{window}')
            ])

            # DX
            df = df.with_columns([
                (
                    100 * (pl.col(f'di_plus_{window}') - pl.col(f'di_minus_{window}')).abs() /
                    (pl.col(f'di_plus_{window}') + pl.col(f'di_minus_{window}') + eps)
                ).alias(f'dx_{window}')
            ])

            # ADX
            df = df.with_columns([
                pl.col(f'dx_{window}').ewm_mean(span=window).alias(f'adx_{window}')
            ])

        # ========== 价格位置因子 ==========
        for window in windows:
            # Price Position in N-period range
            df = df.with_columns([
                (
                    (pl.col('close') - pl.col('low').rolling_min(window)) /
                    (pl.col('high').rolling_max(window) - pl.col('low').rolling_min(window) + eps)
                ).alias(f'price_position_{window}')
            ])

            # Higher High Count - 统计创新高次数
            # 简化实现：检测当前高点是否为过去M期的最高点
            check_window = 5
            df = df.with_columns([
                (
                    pl.col('high') == pl.col('high').rolling_max(check_window)
                ).cast(pl.Int32).rolling_sum(window).alias(f'higher_high_count_{window}')
            ])

            # Lower Low Count - 统计创新低次数
            df = df.with_columns([
                (
                    pl.col('low') == pl.col('low').rolling_min(check_window)
                ).cast(pl.Int32).rolling_sum(window).alias(f'lower_low_count_{window}')
            ])

        # ========== 趋势持续性因子 ==========
        # 计算辅助列: 涨跌标记
        df = df.with_columns([
            (pl.col('close') > pl.col('open')).cast(pl.Int32).alias('is_up'),
            (pl.col('close') < pl.col('open')).cast(pl.Int32).alias('is_down'),
            (pl.col('close') - pl.col('close').shift(1)).abs().alias('abs_return')
        ])

        for window in windows:
            # Trend Consistency
            df = df.with_columns([
                (
                    (pl.col('is_up').rolling_sum(window) - pl.col('is_down').rolling_sum(window)) /
                    window
                ).alias(f'trend_consistency_{window}')
            ])

            # Trend Strength Index
            # 需要计算同向运动的绝对收益和
            # 简化实现：使用趋势一致性的绝对值作为代理
            df = df.with_columns([
                pl.col(f'trend_consistency_{window}').abs().alias(f'trend_strength_idx_{window}')
            ])

        # Linear Regression Slope and R²
        # 使用滚动窗口计算线性回归
        for window in windows:
            # 创建时间索引
            df = df.with_row_count('row_idx')

            # 计算线性回归斜率 (简化版本: 使用相关系数 * std(y) / std(x))
            # 更精确的实现需要使用numpy或专门的回归库
            df = df.with_columns([
                # 简化斜率计算
                (
                    (pl.col('close') - pl.col('close').shift(window)) /
                    (window + eps)
                ).alias(f'lr_slope_{window}')
            ])

            # R² 计算 (简化版本: 使用滚动相关系数的平方)
            # 真实R²需要完整的线性回归计算
            close_corr = pl.col('close').rolling_corr(pl.col('row_idx').cast(pl.Float64), window_size=window)
            df = df.with_columns([
                (close_corr ** 2).alias(f'r_squared_{window}')
            ])

        # ========== MACD因子 ==========
        # MACD = EMA(12) - EMA(26)
        df = df.with_columns([
            pl.col('close').ewm_mean(span=12).alias('ema_12'),
            pl.col('close').ewm_mean(span=26).alias('ema_26')
        ])

        df = df.with_columns([
            (pl.col('ema_12') - pl.col('ema_26')).alias('macd_12_26')
        ])

        # MACD Signal = EMA(MACD, 9)
        df = df.with_columns([
            pl.col('macd_12_26').ewm_mean(span=9).alias('macd_signal_9')
        ])

        # MACD Histogram
        df = df.with_columns([
            (pl.col('macd_12_26') - pl.col('macd_signal_9')).alias('macd_histogram')
        ])

        # ========== 多周期综合因子 ==========
        # Multi-Timeframe Trend Alignment
        df = df.with_columns([
            (
                pl.col('roc_60').sign() +
                pl.col('roc_180').sign() +
                pl.col('roc_360').sign()
            ).alias('multi_tf_trend_align')
        ])

        # Trend Strength Composite
        df = df.with_columns([
            (
                (pl.col('adx_60') + pl.col('adx_180') + pl.col('adx_360')) / 3
            ).alias('trend_strength_comp')
        ])

        return df

    def calculate_microstructure_factors(self) -> pl.DataFrame:
        """
        计算市场微观结构因子

        包括：
        - 价格路径因子 (range_utilization, signed_range_util, true_strength_proxy)
        - 价格效率因子 (price_efficiency, price_reversal_ind)
        - 成交量分布因子 (volume_at_high, volume_at_low)

        Returns:
            pl.DataFrame: 添加了市场微观结构因子的DataFrame
        """
        df = self.df
        eps = self.epsilon

        # ========== 价格路径因子 ==========
        # Range Utilization
        df = df.with_columns([
            (
                (pl.col('close') - pl.col('open')).abs() /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('range_utilization')
        ])

        # Signed Range Utilization
        df = df.with_columns([
            (
                (pl.col('close') - pl.col('open')).sign() *
                pl.col('range_utilization')
            ).alias('signed_range_util')
        ])

        # True Strength Proxy
        df = df.with_columns([
            (
                pl.col('signed_range_util') *
                (pl.col('volume') / (pl.col('volume').rolling_mean(20) + eps))
            ).alias('true_strength_proxy')
        ])

        # ========== 价格效率因子 ==========
        # Price Efficiency (same as Range Utilization)
        df = df.with_columns([
            pl.col('range_utilization').alias('price_efficiency')
        ])

        # Price Reversal Indicator
        df = df.with_columns([
            (
                (pl.col('high') + pl.col('low') - pl.col('open') - pl.col('close')) /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('price_reversal_ind')
        ])

        # ========== 成交量分布因子 ==========
        # 这些因子依赖K线形态因子，将在K线形态因子计算后添加
        # Volume at High = KUP × Volume
        # Volume at Low = KLOW × Volume
        # 这里先预留，在calculate_candlestick_factors中计算

        return df

    def calculate_candlestick_factors(self) -> pl.DataFrame:
        """
        计算K线形态因子

        包括：
        - 基础形态特征 (kmid, klen, kup, klow, ksft)
        - 非线性增强特征 (kmid2, kup2, klow2, ksft2)
        - 成交量分布因子 (volume_at_high, volume_at_low)

        Returns:
            pl.DataFrame: 添加了K线形态因子的DataFrame
        """
        df = self.df
        eps = self.epsilon

        # ========== 基础形态特征 ==========
        # KMID - K线中间价位置
        # kmid = (close - open) / (high - low + ε)
        df = df.with_columns([
            (
                (pl.col('close') - pl.col('open')) /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('kmid')
        ])

        # KLEN - K线长度比例
        # klen = (high - low) / (open + ε)
        df = df.with_columns([
            (
                (pl.col('high') - pl.col('low')) /
                (pl.col('open') + eps)
            ).alias('klen')
        ])

        # KUP - 上影线比例
        # kup = (high - max(open, close)) / (high - low + ε)
        df = df.with_columns([
            (
                (pl.col('high') - pl.max_horizontal(['open', 'close'])) /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('kup')
        ])

        # KLOW - 下影线比例
        # klow = (min(open, close) - low) / (high - low + ε)
        df = df.with_columns([
            (
                (pl.min_horizontal(['open', 'close']) - pl.col('low')) /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('klow')
        ])

        # KSFT - K线实体偏移度
        # ksft = (max(open, close) - (high + low)/2) / (high - low + ε)
        df = df.with_columns([
            (
                (pl.max_horizontal(['open', 'close']) - (pl.col('high') + pl.col('low')) / 2) /
                (pl.col('high') - pl.col('low') + eps)
            ).alias('ksft')
        ])

        # ========== 非线性增强特征 ==========
        df = df.with_columns([
            (pl.col('kmid') ** 2).alias('kmid2'),
            (pl.col('kup') ** 2).alias('kup2'),
            (pl.col('klow') ** 2).alias('klow2'),
            (pl.col('ksft') ** 2).alias('ksft2')
        ])

        # ========== 成交量分布因子 ==========
        # Volume at High
        df = df.with_columns([
            (pl.col('kup') * pl.col('volume')).alias('volume_at_high')
        ])

        # Volume at Low
        df = df.with_columns([
            (pl.col('klow') * pl.col('volume')).alias('volume_at_low')
        ])

        return df

    def save_factors(self, output_path: Union[str, Path], format: str = 'feather'):
        """
        保存计算后的因子数据

        Args:
            output_path: 输出文件路径
            format: 输出格式，支持 'feather', 'parquet', 'csv'

        Example:
            >>> calc.save_factors('output/factors.feather', format='feather')
        """
        if self.df is None:
            raise ValueError("没有可保存的数据")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'feather':
            self.df.write_ipc(output_path)
        elif format == 'parquet':
            self.df.write_parquet(output_path)
        elif format == 'csv':
            self.df.write_csv(output_path)
        else:
            raise ValueError(f"不支持的格式: {format}")

        print(f"因子数据已保存到: {output_path}")

    def get_factor_summary(self) -> dict:
        """
        获取因子计算摘要信息

        Returns:
            dict: 包含因子数量、数据行数、列名等信息的字典
        """
        if self.df is None:
            raise ValueError("请先加载数据或计算因子")

        base_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        factor_cols = [col for col in self.df.columns if col not in base_cols]

        summary = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'base_columns': len(base_cols),
            'factor_columns': len(factor_cols),
            'factor_names': factor_cols,
            'null_counts': {
                col: self.df[col].null_count()
                for col in factor_cols[:10]  # 只显示前10个因子的空值统计
            }
        }

        return summary


def main():
    """
    示例：如何使用FactorCalculator
    """
    # 初始化计算器
    calc = FactorCalculator()

    # 加载数据
    df = calc.load_data('data/ohlcv.feather')

    # 计算所有因子
    df_with_factors = calc.calculate_all_factors()

    # 保存结果
    calc.save_factors('output/factors_complete.feather')

    # 查看摘要
    summary = calc.get_factor_summary()
    print("\n因子计算摘要:")
    print(f"  总行数: {summary['total_rows']}")
    print(f"  总列数: {summary['total_columns']}")
    print(f"  基础列数: {summary['base_columns']}")
    print(f"  因子列数: {summary['factor_columns']}")
    print(f"\n前10个因子:")
    for i, name in enumerate(summary['factor_names'][:10], 1):
        print(f"    {i}. {name}")


if __name__ == '__main__':
    main()
