import os, sys, re, shutil
import json
import hashlib
from pathlib import Path
from datetime import *
import time as time_module
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from enums import *

def get_destination_dir(file_url, folder=None):
  store_directory = os.environ.get('STORE_DIRECTORY')
  if folder:
    store_directory = folder
  if not store_directory:
    store_directory = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(store_directory, file_url)

def get_download_url(file_url):
  return "{}{}".format(BASE_URL, file_url)

def calculate_sha256(file_path):
  """Calculate SHA256 hash of a file"""
  sha256_hash = hashlib.sha256()
  with open(file_path, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
      sha256_hash.update(byte_block)
  return sha256_hash.hexdigest()

def verify_checksum(file_path, checksum_file_path):
  """Verify file integrity using checksum file"""
  if not os.path.exists(checksum_file_path):
    print("\nChecksum file not found: {}".format(checksum_file_path))
    return False

  try:
    # Read expected checksum from file
    with open(checksum_file_path, 'r') as f:
      expected_checksum = f.read().strip().split()[0]  # Get first token (hash value)

    # Calculate actual checksum
    actual_checksum = calculate_sha256(file_path)

    if actual_checksum.lower() == expected_checksum.lower():
      print("\nChecksum verification passed: {}".format(file_path))
      return True
    else:
      print("\nChecksum verification FAILED: {}".format(file_path))
      print("Expected: {}".format(expected_checksum))
      print("Actual: {}".format(actual_checksum))
      return False
  except Exception as e:
    print("\nChecksum verification error: {}".format(str(e)))
    return False

def get_all_symbols(type):
  if type == 'um':
    response = urllib.request.urlopen("https://fapi.binance.com/fapi/v1/exchangeInfo").read()
  elif type == 'cm':
    response = urllib.request.urlopen("https://dapi.binance.com/dapi/v1/exchangeInfo").read()
  else:
    response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
  return list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))

def download_file(base_path, file_name, date_range=None, folder=None, checksum_file_path=None):
  download_path = "{}{}".format(base_path, file_name)
  if folder:
    base_path = os.path.join(folder, base_path)
  if date_range:
    date_range = date_range.replace(" ","_")
    base_path = os.path.join(base_path, date_range)
  save_path = get_destination_dir(os.path.join(base_path, file_name), folder)


  if os.path.exists(save_path):
    # If checksum verification is enabled, verify existing file
    if checksum_file_path and os.path.exists(checksum_file_path):
      if verify_checksum(save_path, checksum_file_path):
        print("\nfile already exists and verified! {}".format(save_path))
        return True
      else:
        print("\nExisting file failed checksum verification, re-downloading...")
        os.remove(save_path)
    else:
      print("\nfile already exists! {}".format(save_path))
      return True

  # make the directory
  if not os.path.exists(base_path):
    Path(get_destination_dir(base_path)).mkdir(parents=True, exist_ok=True)

  download_url = get_download_url(download_path)
  max_retries = 3

  for attempt in range(max_retries):
    try:
      print(download_url)
      dl_file = urllib.request.urlopen(download_url)
      length = dl_file.getheader('content-length')
      if length:
        length = int(length)
        blocksize = max(4096,length//100)

      with open(save_path, 'wb') as out_file:
        dl_progress = 0
        print("\nStart File Download: {}".format(save_path))
        while True:
          buf = dl_file.read(blocksize)
          if not buf:
            break
          dl_progress += len(buf)
          out_file.write(buf)
          done = int(50 * dl_progress / length)
          sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50-done)) )
          sys.stdout.flush()
        print("\nFile Download: {} complete!".format(save_path))

      # Verify checksum if provided
      if checksum_file_path and os.path.exists(checksum_file_path):
        if not verify_checksum(save_path, checksum_file_path):
          # Checksum verification failed
          if os.path.exists(save_path):
            os.remove(save_path)
          if attempt < max_retries - 1:
            print("Retrying download due to checksum mismatch...")
            time_module.sleep(2)
            continue
          else:
            print("\nFile download failed after {} attempts due to checksum mismatch".format(max_retries))
            return False

      # Download successful, break out of retry loop
      return True

    except urllib.error.HTTPError as e:
      # Don't retry if file not found (404 error)
      if e.code == 404:
        print("\nFile not found: {}".format(download_url))
        # Clean up partial download if exists
        if os.path.exists(save_path):
          os.remove(save_path)
        return False

      # Retry for other HTTP errors (5xx server errors, etc.)
      if attempt < max_retries - 1:
        print("\nDownload failed with HTTP error {} (attempt {}/{}): {}".format(e.code, attempt + 1, max_retries, download_url))
        print("Retrying in 2 seconds...")
        time_module.sleep(2)
      else:
        print("\nFile download failed after {} attempts: {}".format(max_retries, download_url))

      # Clean up partial download if exists
      if os.path.exists(save_path):
        os.remove(save_path)

    except Exception as e:
      if attempt < max_retries - 1:
        print("\nDownload error (attempt {}/{}): {}".format(attempt + 1, max_retries, str(e)))
        print("Retrying in 2 seconds...")
        time_module.sleep(2)
      else:
        print("\nFile download failed after {} attempts: {}".format(max_retries, str(e)))

      # Clean up partial download if exists
      if os.path.exists(save_path):
        os.remove(save_path)

  return False

def convert_to_date_object(d):
  year, month, day = [int(x) for x in d.split('-')]
  date_obj = date(year, month, day)
  return date_obj

def get_start_end_date_objects(date_range):
  start, end = date_range.split()
  start_date = convert_to_date_object(start)
  end_date = convert_to_date_object(end)
  return start_date, end_date

def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
  if not pat.match(arg_value):
    raise ArgumentTypeError
  return arg_value

def check_directory(arg_value):
  if os.path.exists(arg_value):
    while True:
      option = input('Folder already exists! Do you want to overwrite it? y/n  ')
      if option != 'y' and option != 'n':
        print('Invalid Option!')
        continue
      elif option == 'y':
        shutil.rmtree(arg_value)
        break
      else:
        break
  return arg_value

def raise_arg_error(msg):
  raise ArgumentTypeError(msg)

def get_path(trading_type, market_data_type, time_period, symbol, interval=None):
  trading_type_path = 'data/spot'
  if trading_type != 'spot':
    trading_type_path = f'data/futures/{trading_type}'
  if interval is not None:
    path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/{interval}/'
  else:
    path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/'
  return path

def get_parser(parser_type):
  parser = ArgumentParser(description=("This is a script to download historical {} data").format(parser_type), formatter_class=RawTextHelpFormatter)
  parser.add_argument(
      '-s', dest='symbols', nargs='+',
      help='Single symbol or multiple symbols separated by space')
  parser.add_argument(
      '-y', dest='years', default=YEARS, nargs='+', choices=YEARS,
      help='Single year or multiple years separated by space\n-y 2019 2021 means to download {} from 2019 and 2021'.format(parser_type))
  parser.add_argument(
      '-m', dest='months', default=MONTHS,  nargs='+', type=int, choices=MONTHS,
      help='Single month or multiple months separated by space\n-m 2 12 means to download {} from feb and dec'.format(parser_type))
  parser.add_argument(
      '-d', dest='dates', nargs='+', type=match_date_regex,
      help='Date to download in [YYYY-MM-DD] format\nsingle date or multiple dates separated by space\ndownload from 2020-01-01 if no argument is parsed')
  parser.add_argument(
      '-startDate', dest='startDate', type=match_date_regex,
      help='Starting date to download in [YYYY-MM-DD] format')
  parser.add_argument(
      '-endDate', dest='endDate', type=match_date_regex,
      help='Ending date to download in [YYYY-MM-DD] format')
  parser.add_argument(
      '-folder', dest='folder', type=check_directory,
      help='Directory to store the downloaded data')
  parser.add_argument(
      '-skip-monthly', dest='skip_monthly', default=0, type=int, choices=[0, 1],
      help='1 to skip downloading of monthly data, default 0')
  parser.add_argument(
      '-skip-daily', dest='skip_daily', default=0, type=int, choices=[0, 1],
      help='1 to skip downloading of daily data, default 0')
  parser.add_argument(
      '-c', dest='checksum', default=0, type=int, choices=[0,1],
      help='1 to download checksum file, default 0')
  parser.add_argument(
      '-t', dest='type', required=True, choices=TRADING_TYPE,
      help='Valid trading types: {}'.format(TRADING_TYPE))

  if parser_type == 'klines':
    parser.add_argument(
      '-i', dest='intervals', default=INTERVALS, nargs='+', choices=INTERVALS,
      help='single kline interval or multiple intervals separated by space\n-i 1m 1w means to download klines interval of 1minute and 1week')


  return parser


