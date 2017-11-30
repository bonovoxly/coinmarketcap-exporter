from prometheus_client import start_http_server, Metric, REGISTRY
import argparse
import json
import logging
import requests
import sys
import time

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
    self.endpoint = 'https://api.coinmarketcap.com/v1/ticker/'

  def collect(self):
    # Get the API data
    #requests.get("http://127.0.0.1").elapsed.total_seconds()
    #response = json.loads(requests.get(self.endpoint).content.decode('UTF-8'))
    r = requests.get(self.endpoint)
    request_time = r.elapsed.total_seconds()
    log.info('elapsed time -' + str(request_time))
    response = json.loads(r.content.decode('UTF-8'))
    metric = Metric('coinmarketcap_response_time', 'Total time for the coinmarketcap API to respond.', 'summary')
    metric.add_sample('coinmarketcap_response_time', value=float(request_time), labels={'name': 'coinmarketcap.com'})
    yield metric
    for each in response:
      coin = '_'.join(['coin_market', each['symbol']]) 
      description = 'The market statistics of: ' + each['name']
      metric = Metric(coin, description, 'summary')
      for that in ['price_usd', 'price_btc', '24h_volume_usd', 'market_cap_usd', 'available_supply', 'total_supply', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']:
        metric.add_sample('_'.join([coin, that]), value=float(each[that]), labels={'id': each['id'], 'name': each['name'], 'symbol': each['symbol']})
      yield metric

#    # Get the requests duration
#    metric = Metric('svc_requests_duration_seconds',
#      'Requests time taken in seconds', 'summary')
#    metric.add_sample('svc_requests_duration_seconds_count',
#      value=response['requests_handled'], labels={})
#    metric.add_sample('svc_requests_duration_seconds_sum',
#      value=response['requests_duration_milliseconds'] / 1000.0, labels={})
#    yield metric

if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on.  Defaults to 9101.', default=9101)
    args = parser.parse_args()
    log.info(args.port)
  
    REGISTRY.register(CoinCollector())
    start_http_server(int(args.port))
    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)
