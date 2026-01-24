1）读取orderbookdepth， 以分钟为单位读取。 生成新的dataframe，
biance_example/bookdepth.csv 是数据例子
2）通过orderbookdepth，生成factor的一行。 
3）kline 中一行是一分钟的数据1分钟的数据，也是用来生成factor的一行。Open-High-Low-Close price就是从kline中获取。
biance_example/kline.csv 是数据例子
4) 生成factor的一行。
5) 最终生成的数据集应该包含factor的所有列，以及kline的Open-High-Low-Close price列。 factor.md是因子的公式说明
6）使用Polars代替pandas