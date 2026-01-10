nohup python quick_start.py --input data/ETHUSDT/df_train.feather --output data/ETHUSDT/tmp/df_train.feather >./logs/df_train_factors.log 2>&1 &
nohup python quick_start.py --input data/ETHUSDT/df_test.feather --output data/ETHUSDT/tmp/df_test.feather >./logs/df_test_factors.log 2>&1 &
nohup python quick_start.py --input data/ETHUSDT/df_val.feather --output data/ETHUSDT/tmp/df_val.feather >./logs/df_val_factors.log 2>&1 &
