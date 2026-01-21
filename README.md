需要我的账号是否支持通过wss 获取trades的条件单推送

步骤

- 下载 trades 文件和book depth  
  - https://github.com/binance/binance-public-data  代码仓库提供了下载代码
- 数据加工
  - 生成marcohft训练文件
  - 将文件加工成tardis 格式
- 用hftbacktest回测
  - tardis 格式，确保数据可用
  - 用hftbacktest回测，marcohft 模型. 集成测试模型
- 用freqtrade回测
