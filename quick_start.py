#!/usr/bin/env python3
"""
快速启动脚本

一键运行完整的因子计算流程
"""

import sys
from pathlib import Path
from factor_calculator import FactorCalculator
from example_usage import create_sample_data


def quick_start(data_path: str = None, output_path: str = 'output/factors_quick_start.feather'):
    """
    快速启动因子计算

    Args:
        data_path: 输入数据路径，如果为None则生成样本数据
        output_path: 输出数据路径
    """
    print("\n" + "="*70)
    print(" MacroHFT Features - 因子计算器快速启动")
    print("="*70)

    # Step 1: 数据准备
    if data_path is None or not Path(data_path).exists():
        print("\n[步骤 1/4] 生成样本数据...")
        print("  注意: 未提供数据路径，将生成30天的样本数据用于演示")
        data_path = 'data/sample_ohlcv_quick_start.feather'
        create_sample_data(data_path, n_days=30)
    else:
        print(f"\n[步骤 1/4] 使用提供的数据: {data_path}")

    # Step 2: 初始化计算器
    print("\n[步骤 2/4] 初始化因子计算器...")
    calc = FactorCalculator()

    # Step 3: 加载数据
    print("\n[步骤 3/4] 加载OHLCV数据...")
    try:
        calc.load_data(data_path)
        print(f"  ✓ 数据加载成功")
    except Exception as e:
        print(f"  ✗ 数据加载失败: {e}")
        sys.exit(1)

    # Step 4: 计算因子
    print("\n[步骤 4/4] 计算所有因子...")
    print("  这可能需要一些时间，请稍候...")

    try:
        df_with_factors = calc.calculate_all_factors()
        print(f"  ✓ 因子计算完成")
    except Exception as e:
        print(f"  ✗ 因子计算失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 5: 保存结果
    print("\n[步骤 5/5] 保存计算结果...")
    try:
        calc.save_factors(output_path)
        print(f"  ✓ 结果已保存到: {output_path}")
    except Exception as e:
        print(f"  ✗ 保存失败: {e}")
        sys.exit(1)

    # 显示摘要
    print("\n" + "="*70)
    print(" 计算摘要")
    print("="*70)

    summary = calc.get_factor_summary()
    print(f"\n数据概况:")
    print(f"  • 总行数: {summary['total_rows']:,}")
    print(f"  • 总列数: {summary['total_columns']}")
    print(f"  • 基础列数: {summary['base_columns']}")
    print(f"  • 因子列数: {summary['factor_columns']}")

    # 按类别统计因子
    factor_names = summary['factor_names']

    liquidity_factors = [f for f in factor_names if
                        'volume' in f or 'wap' in f or 'turnover' in f or 'price_volume' in f]
    volatility_factors = [f for f in factor_names if
                         'volatility' in f or 'range' in f or 'liquidity_cost' in f]
    trend_factors = [f for f in factor_names if
                    'sma' in f or 'ema' in f or 'roc' in f or 'momentum' in f or
                    'adx' in f or 'di_' in f or 'macd' in f or 'trend' in f or
                    'lr_' in f or 'r_squared' in f or 'price_position' in f or
                    'higher_high' in f or 'lower_low' in f]
    microstructure_factors = [f for f in factor_names if
                             'range_util' in f or 'strength_proxy' in f or
                             'efficiency' in f or 'reversal' in f]
    candlestick_factors = [f for f in factor_names if
                          'kmid' in f or 'klen' in f or 'kup' in f or
                          'klow' in f or 'ksft' in f]

    print(f"\n因子分类统计:")

    print(f"\n  • 流动性因子 ({len(liquidity_factors)}个):")
    for i, factor in enumerate(liquidity_factors, 1):
        print(f"    {i:2d}. {factor}")

    print(f"\n  • 波动性因子 ({len(volatility_factors)}个):")
    for i, factor in enumerate(volatility_factors, 1):
        print(f"    {i:2d}. {factor}")

    print(f"\n  • 趋势因子 ({len(trend_factors)}个):")
    for i, factor in enumerate(trend_factors, 1):
        print(f"    {i:2d}. {factor}")

    print(f"\n  • 微观结构因子 ({len(microstructure_factors)}个):")
    for i, factor in enumerate(microstructure_factors, 1):
        print(f"    {i:2d}. {factor}")

    print(f"\n  • K线形态因子 ({len(candlestick_factors)}个):")
    for i, factor in enumerate(candlestick_factors, 1):
        print(f"    {i:2d}. {factor}")

    # 数据质量检查
    print(f"\n数据质量:")
    null_summary = summary.get('null_counts', {})
    if null_summary:
        total_nulls = sum(null_summary.values())
        print(f"  • 空值总数: {total_nulls:,}")
        if total_nulls > 0:
            print(f"  • 前10个因子的空值数:")
            for col, count in list(null_summary.items())[:10]:
                pct = count / summary['total_rows'] * 100
                print(f"    - {col}: {count} ({pct:.1f}%)")
    else:
        print(f"  • 空值检查: 未统计")

    # 示例因子值
    print(f"\n示例因子值 (最后一行):")
    last_row = df_with_factors.tail(1)

    example_factors = [
        'close', 'volume',
        'roc_60', 'adx_60', 'sma_60',
        'volume_zscore_60', 'kmid'
    ]

    for factor in example_factors:
        if factor in last_row.columns:
            value = last_row[factor][0]
            if value is not None:
                print(f"  • {factor}: {value:.6f}" if isinstance(value, float) else f"  • {factor}: {value}")

    print("\n" + "="*70)
    print(" 完成! ")
    print("="*70)

    print(f"\n后续步骤:")
    print(f"  1. 查看输出文件: {output_path}")
    print(f"  2. 使用Polars或Pandas加载分析:")
    print(f"     import polars as pl")
    print(f"     df = pl.read_ipc('{output_path}')")
    print(f"  3. 查看示例代码: python example_usage.py")
    print(f"  4. 运行测试: pytest test_factor_calculator.py -v")
    print()

    return df_with_factors


def main():
    """
    主函数 - 解析命令行参数
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='MacroHFT Features - 因子计算器快速启动',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用样本数据
  python quick_start.py

  # 使用自己的数据
  python quick_start.py --input data/my_ohlcv.feather --output output/my_factors.feather

  # 仅生成样本数据
  python quick_start.py --sample-only
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        default=None,
        help='输入OHLCV数据路径（feather格式）'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output/factors_quick_start.feather',
        help='输出因子数据路径（默认: output/factors_quick_start.feather）'
    )

    parser.add_argument(
        '--sample-only',
        action='store_true',
        help='仅生成样本数据，不计算因子'
    )

    parser.add_argument(
        '--sample-days',
        type=int,
        default=30,
        help='样本数据天数（默认: 30）'
    )

    args = parser.parse_args()

    # 仅生成样本数据
    if args.sample_only:
        print("\n生成样本数据...")
        output_path = args.input or 'data/sample_ohlcv.feather'
        create_sample_data(output_path, n_days=args.sample_days)
        print(f"样本数据已保存到: {output_path}")
        return

    # 运行完整流程
    quick_start(data_path=args.input, output_path=args.output)


if __name__ == '__main__':
    main()
