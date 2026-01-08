"""
因子计算配置文件

可以通过修改此文件调整因子计算参数，而无需修改主代码
"""

# ==================== 全局配置 ====================

# 防止除零的极小值
EPSILON = 1e-8

# 趋势因子的标准时间窗口（分钟）
TREND_WINDOWS = {
    'short': 60,    # 1小时
    'medium': 180,  # 3小时
    'long': 360     # 6小时
}

# ==================== 流动性因子配置 ====================

LIQUIDITY_CONFIG = {
    # 成交量Z-Score的窗口大小
    'volume_zscore_windows': [30, 60, 100],

    # 成交金额Z-Score的窗口大小
    'turnover_zscore_windows': [30, 60, 100],

    # 成交量比率配置
    'volume_ratio': {
        'short_windows': [5, 10],
        'long_windows': [30, 60]
    },

    # 成交量加速度的EMA周期
    'volume_acceleration_periods': [20, 60],

    # 量价相关性的窗口大小
    'price_volume_corr_windows': [5, 10, 20]
}

# ==================== 波动性因子配置 ====================

VOLATILITY_CONFIG = {
    # 是否计算扩展的波动率指标
    'calculate_extended_volatility': False,

    # 扩展波动率窗口（如需要）
    'extended_windows': [10, 20, 60]
}

# ==================== 趋势因子配置 ====================

TREND_CONFIG = {
    # 移动平均线窗口
    'ma_windows': [60, 180, 360],

    # 均线斜率计算周期
    'slope_period': 5,

    # MACD参数
    'macd': {
        'fast': 12,
        'slow': 26,
        'signal': 9
    },

    # ADX/DI计算窗口
    'adx_windows': [60, 180, 360],

    # 价格位置因子的检测窗口
    'price_position_check_window': 5,

    # 是否计算线性回归因子
    'calculate_linear_regression': True,
}

# ==================== 微观结构因子配置 ====================

MICROSTRUCTURE_CONFIG = {
    # True Strength Proxy的成交量平均窗口
    'true_strength_volume_window': 20,
}

# ==================== K线形态因子配置 ====================

CANDLESTICK_CONFIG = {
    # 是否计算扩展的K线形态因子
    'calculate_extended_patterns': False,

    # K线形态识别阈值
    'pattern_thresholds': {
        'big_bullish_kmid': 0.7,     # 大阳线阈值
        'big_bearish_kmid': -0.7,    # 大阴线阈值
        'doji_kmid': 0.1,            # 十字星阈值
        'long_shadow': 0.7,          # 长影线阈值
    }
}

# ==================== 数据处理配置 ====================

DATA_CONFIG = {
    # 数据加载时的内存优化
    'use_lazy_loading': False,  # Polars lazy模式（适合超大数据集）

    # 输出格式
    'default_output_format': 'feather',  # 'feather', 'parquet', 'csv'

    # 是否在计算后自动排序
    'auto_sort_by_timestamp': True,

    # 数据验证
    'validate_ohlc': True,  # 是否验证OHLC数据的有效性
}

# ==================== 性能配置 ====================

PERFORMANCE_CONFIG = {
    # Polars线程数（None表示使用所有可用核心）
    'n_threads': None,

    # 是否启用Polars的查询优化
    'optimize_queries': True,

    # 批处理大小（用于超大数据集分批处理）
    'batch_size': 100000,  # 行数

    # 是否显示进度条
    'show_progress': True,
}

# ==================== 因子选择配置 ====================

# 可以通过此配置选择性地计算因子
FACTOR_SELECTION = {
    'calculate_liquidity': True,
    'calculate_volatility': True,
    'calculate_trend': True,
    'calculate_microstructure': True,
    'calculate_candlestick': True,
}

# ==================== 高级配置 ====================

ADVANCED_CONFIG = {
    # 缺失值处理策略
    'null_handling': {
        'strategy': 'keep',  # 'keep', 'forward_fill', 'drop'
        'fill_limit': 5      # 前向填充的最大连续数
    },

    # 异常值处理
    'outlier_handling': {
        'enabled': False,
        'method': 'winsorize',  # 'winsorize', 'clip', 'none'
        'limits': [0.01, 0.01]  # 上下分位数限制
    },

    # 因子标准化
    'standardization': {
        'enabled': False,
        'method': 'zscore',  # 'zscore', 'minmax', 'robust'
        'windows': [60, 180, 360]
    }
}


# ==================== 辅助函数 ====================

def get_all_trend_windows():
    """获取所有趋势窗口配置"""
    return TREND_CONFIG['ma_windows']


def get_volume_zscore_windows():
    """获取所有成交量Z-Score窗口"""
    return LIQUIDITY_CONFIG['volume_zscore_windows']


def get_config_summary():
    """获取配置摘要"""
    summary = {
        'epsilon': EPSILON,
        'trend_windows': TREND_CONFIG['ma_windows'],
        'volume_zscore_windows': LIQUIDITY_CONFIG['volume_zscore_windows'],
        'macd_params': TREND_CONFIG['macd'],
        'output_format': DATA_CONFIG['default_output_format'],
        'factor_selection': FACTOR_SELECTION
    }
    return summary


def print_config():
    """打印当前配置"""
    print("="*60)
    print("因子计算配置")
    print("="*60)

    summary = get_config_summary()

    print(f"\n全局配置:")
    print(f"  Epsilon: {summary['epsilon']}")

    print(f"\n趋势窗口:")
    for window in summary['trend_windows']:
        hours = window / 60
        print(f"  {window}期 ({hours:.1f}小时)")

    print(f"\n成交量Z-Score窗口:")
    for window in summary['volume_zscore_windows']:
        print(f"  {window}期")

    print(f"\nMACD参数:")
    for key, value in summary['macd_params'].items():
        print(f"  {key}: {value}")

    print(f"\n因子选择:")
    for key, value in summary['factor_selection'].items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}")

    print(f"\n输出格式: {summary['output_format']}")
    print("="*60)


if __name__ == '__main__':
    # 显示当前配置
    print_config()
