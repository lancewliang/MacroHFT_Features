#!/usr/bin/env python

"""
  script to download klines.
  set the absolute path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""
import sys
from datetime import *
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
  get_path


def download_monthly_klines(trading_type, symbols, num_symbols, intervals, years, months, start_date, end_date, folder, checksum):
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

  if not start_date:
    start_date = START_DATE
  else:
    start_date = convert_to_date_object(start_date)

  if not end_date:
    end_date = END_DATE
  else:
    end_date = convert_to_date_object(end_date)

  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download monthly {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for year in years:
        for month in months:
          current_date = convert_to_date_object('{}-{}-01'.format(year, month))
          if current_date >= start_date and current_date <= end_date:
            path = get_path(trading_type, "klines", "monthly", symbol, interval)
            file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))

            checksum_file_path = None

            # If checksum verification is enabled, download checksum file first
            if checksum == 1:
              checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
              checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year, '{:02d}'.format(month))

              # Download checksum file
              checksum_success = download_file(checksum_path, checksum_file_name, date_range, folder)

              if checksum_success:
                # Build the full path to the checksum file
                import os
                base_path = checksum_path
                if folder:
                  base_path = os.path.join(folder, base_path)
                if date_range:
                  date_range_str = date_range.replace(" ", "_")
                  base_path = os.path.join(base_path, date_range_str)
                from utility import get_destination_dir
                checksum_file_path = get_destination_dir(os.path.join(base_path, checksum_file_name), folder)

                # Verify checksum file is valid (should contain SHA256 hash)
                if os.path.exists(checksum_file_path):
                  try:
                    with open(checksum_file_path, 'r') as f:
                      checksum_content = f.read().strip()
                      # Basic validation: SHA256 hash should be 64 hex characters
                      hash_value = checksum_content.split()[0]
                      if len(hash_value) != 64 or not all(c in '0123456789abcdefABCDEF' for c in hash_value):
                        print("\nWarning: Checksum file appears to be invalid: {}".format(checksum_file_path))
                        checksum_file_path = None
                  except Exception as e:
                    print("\nWarning: Failed to validate checksum file: {}".format(str(e)))
                    checksum_file_path = None

            # Download the data file with checksum verification
            download_file(path, file_name, date_range, folder, checksum_file_path)

    current += 1

def download_daily_klines(trading_type, symbols, num_symbols, intervals, dates, start_date, end_date, folder, checksum):
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

  if not start_date:
    start_date = START_DATE
  else:
    start_date = convert_to_date_object(start_date)

  if not end_date:
    end_date = END_DATE
  else:
    end_date = convert_to_date_object(end_date)

  #Get valid intervals for daily
  intervals = list(set(intervals) & set(DAILY_INTERVALS))
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download daily {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for date in dates:
        current_date = convert_to_date_object(date)
        if current_date >= start_date and current_date <= end_date:
          path = get_path(trading_type, "klines", "daily", symbol, interval)
          file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)

          checksum_file_path = None

          # If checksum verification is enabled, download checksum file first
          if checksum == 1:
            checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
            checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)

            # Download checksum file
            checksum_success = download_file(checksum_path, checksum_file_name, date_range, folder)

            if checksum_success:
              # Build the full path to the checksum file
              import os
              base_path = checksum_path
              if folder:
                base_path = os.path.join(folder, base_path)
              if date_range:
                date_range_str = date_range.replace(" ", "_")
                base_path = os.path.join(base_path, date_range_str)
              from utility import get_destination_dir
              checksum_file_path = get_destination_dir(os.path.join(base_path, checksum_file_name), folder)

              # Verify checksum file is valid (should contain SHA256 hash)
              if os.path.exists(checksum_file_path):
                try:
                  with open(checksum_file_path, 'r') as f:
                    checksum_content = f.read().strip()
                    # Basic validation: SHA256 hash should be 64 hex characters
                    hash_value = checksum_content.split()[0]
                    if len(hash_value) != 64 or not all(c in '0123456789abcdefABCDEF' for c in hash_value):
                      print("\nWarning: Checksum file appears to be invalid: {}".format(checksum_file_path))
                      checksum_file_path = None
                except Exception as e:
                  print("\nWarning: Failed to validate checksum file: {}".format(str(e)))
                  checksum_file_path = None

          # Download the data file with checksum verification
          download_file(path, file_name, date_range, folder, checksum_file_path)

    current += 1

if __name__ == "__main__":
    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
      print("fetching all symbols from exchange")
      symbols = get_all_symbols(args.type)
      num_symbols = len(symbols)
    else:
      symbols = args.symbols
      num_symbols = len(symbols)

    if args.dates:
      dates = args.dates
    else:
      period = convert_to_date_object(datetime.today().strftime('%Y-%m-%d')) - convert_to_date_object(
        PERIOD_START_DATE)
      dates = pd.date_range(end=datetime.today(), periods=period.days + 1).to_pydatetime().tolist()
      dates = [date.strftime("%Y-%m-%d") for date in dates]
      if args.skip_monthly == 0:
        download_monthly_klines(args.type, symbols, num_symbols, args.intervals, args.years, args.months, args.startDate, args.endDate, args.folder, args.checksum)
    if args.skip_daily == 0:
      download_daily_klines(args.type, symbols, num_symbols, args.intervals, dates, args.startDate, args.endDate, args.folder, args.checksum)

