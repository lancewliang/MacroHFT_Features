# https://docs.tardis.dev/historical-data-details/binance-futures

# Downloads sample Binance futures BTCUSDT trades
!wget https://datasets.tardis.dev/v1/binance-futures/trades/2020/02/01/BTCUSDT.csv.gz -O BTCUSDT_trades.csv.gz

# Downloads sample Binance futures BTCUSDT book
!wget https://datasets.tardis.dev/v1/binance-futures/incremental_book_L2/2020/02/01/BTCUSDT.csv.gz -O BTCUSDT_book.csv.gz

tardis例子格式
gzip 解压 gzip -d -c BTCUSDT_trades.csv.gz > BTCUSDT.csv


格式  LEVEL3 数据
exchange,symbol,timestamp,local_timestamp,id,side,price,amount

