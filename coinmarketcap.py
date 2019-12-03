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

# caching API for 2min
cache = TTLCache(maxsize=1000, ttl=120)

# logging setup
log = logging.getLogger('coinmarketcap-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

cak = os.environ.get('COINMARKETCAP_API_KEY')

class CoinClient():
	def __init__(self):
		self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
		self.headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': cak}
		self.parameters = {'start': '1', 'limit': '5000', 'convert': 'USD'}

	@cached(cache)
	def tickers(self, start):
		session = Session()
		session.headers.update(self.headers)
		r = session.get(self.url, params=self.parameters)
		data = json.loads(r.text)
		print(data)
		return data

class CoinCollector():
	def __init__(self):
		self.client = CoinClient()

	def collect(self):
		with lock:
			log.info('collecting...')
			start = 1
			while True:
				# query the api
				response = self.client.tickers(start)
				if not response['data']:
					break
				metric = Metric('coin_market', 'coinmarketcap metric values', 'gauge')
				for _, value in response['data'].items():
					for that in ['rank', 'total_supply', 'max_supply', 'circulating_supply']:
						coinmarketmetric = '_'.join(['coin_market', that])
						if value[that] is not None:
							metric.add_sample(coinmarketmetric, value=float(value[that]), labels={'id': value['website_slug'], 'name': value['name'], 'symbol': value['symbol']})
					for price in ['USD', 'BTC']:
						for that in ['price', 'volume_24h', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']:
							coinmarketmetric = '_'.join(['coin_market', that, price]).lower()
							if value['quotes'][price] is None:
								continue
							if value['quotes'][price][that] is not None:
								metric.add_sample(coinmarketmetric, value=float(value['quotes'][price][that]), labels={'id': value['website_slug'], 'name': value['name'], 'symbol': value['symbol']})
				yield metric
				start += len(response['data'])

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
