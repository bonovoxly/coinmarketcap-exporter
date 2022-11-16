from prometheus_client import start_http_server, Metric, REGISTRY
from threading import Lock
from cachetools import cached, TTLCache
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import argparse
import json
import logging
import os
import sys
import time

# lock of the collect method
lock = Lock()

# logging setup
log = logging.getLogger('coinmarketcap-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

currency = os.environ.get('CURRENCY', 'USD')
cak = os.environ.get('COINMARKETCAP_API_KEY')
# caching API for 170min (every 3 hours)
# Note the api limits: https://pro.coinmarketcap.com/features
cache_ttl = int(os.environ.get('CACHE_TTL', 10200))
cache_max_size = int(os.environ.get('CACHE_MAX_SIZE', 10000))
cache = TTLCache(maxsize=cache_max_size, ttl=cache_ttl)

class CoinClient():
  def __init__(self):

    self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    self.headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': cak}
    self.parameters = {'start': '1', 'limit': '5000', 'convert': currency}

  @cached(cache)
  def tickers(self):
    log.info('Fetching data from the API')
    session = Session()
    session.headers.update(self.headers)
    r = session.get(self.url, params=self.parameters)
    data = json.loads(r.text)
    if 'data' not in data:
      log.error('No data in response. Is your API key set?')
      log.info(data)
    return data

class CoinCollector():
  def __init__(self):
    self.client = CoinClient()

  def collect(self):
    with lock:
      log.info('collecting...')
      # query the api
      response = self.client.tickers()
      metric = Metric('coin_market', 'coinmarketcap metric values', 'gauge')
      if 'data' not in response:
        log.error('No data in response. Is your API key set?')
      else:
        for value in response['data']:
          for that in ['cmc_rank', 'total_supply', 'max_supply', 'circulating_supply']:
            coinmarketmetric = '_'.join(['coin_market', that])
            if value[that] is not None:
              metric.add_sample(coinmarketmetric, value=float(value[that]), labels={'id': value['slug'], 'name': value['name'], 'symbol': value['symbol']})
          for price in [currency]:
            for that in ['price', 'volume_24h', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']:
              coinmarketmetric = '_'.join(['coin_market', that, price]).lower()
              if value['quote'][price] is None:
                continue
              if value['quote'][price][that] is not None:
                metric.add_sample(coinmarketmetric, value=float(value['quote'][price][that]), labels={'id': value['slug'], 'name': value['name'], 'symbol': value['symbol']})
      yield metric

if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on', default=9101)
    parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='The interface to bind to', default='0.0.0.0')
    args = parser.parse_args()
    log.info('listening on http://%s:%d/metrics' % (args.addr, args.port))

    REGISTRY.register(CoinCollector())
    start_http_server(int(args.port), addr=args.addr)

    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)
