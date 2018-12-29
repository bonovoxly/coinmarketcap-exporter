from prometheus_client import start_http_server, Metric, REGISTRY
import argparse
import json
import logging
import requests
import sys
import time
from threading import Lock

lock = Lock()

# logging setup
log = logging.getLogger('coinmarketcap-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class CoinCollector():
  def __init__(self):
    self.endpoint = 'https://api.coinmarketcap.com/v2/ticker/'

  def collect(self):
	with lock:
		start = 1
		while True:
			# query the api
			print('starting with %d' % (start))
			r = requests.get('%s?convert=BTC&start=%d' % (self.endpoint, start))
			request_time = r.elapsed.total_seconds()
			log.info('elapsed time -' + str(request_time))
			response = json.loads(r.content.decode('UTF-8'))
			if not response['data']:
				break
			# setup the metric
			metric = Metric('coinmarketcap_response_time', 'Total time for the coinmarketcap API to respond.', 'summary')
			# add the response time as a metric
			metric.add_sample('coinmarketcap_response_time', value=float(request_time), labels={'name': 'coinmarketcap.com'})
			yield metric
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
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on.  Defaults to 9101.', default=9101)
    args = parser.parse_args()
    print('listening on ::%d' % (args.port))

    REGISTRY.register(CoinCollector())
    start_http_server(int(args.port))

    while True:
        time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)
