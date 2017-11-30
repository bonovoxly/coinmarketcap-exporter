from prometheus_client import start_http_server, Metric, REGISTRY
import json
import requests
import sys
import time

class JsonCollector(object):
  def __init__(self, endpoint):
    self._endpoint = endpoint
  def collect(self):
    # Fetch the JSON
    response = json.loads(requests.get(self._endpoint).content.decode('UTF-8'))

    # Convert requests and duration to a summary in seconds
    metric = Metric('svc_requests_duration_seconds',
        'Requests time taken in seconds', 'summary')
    metric.add_sample('svc_requests_duration_seconds_count',
        value=response['requests_handled'], labels={})
    metric.add_sample('svc_requests_duration_seconds_sum',
        value=response['requests_duration_milliseconds'] / 1000.0, labels={})
    yield metric

    # Counter for the failures
    metric = Metric('svc_requests_failed_total',
       'Requests failed', 'summary')
    metric.add_sample('svc_requests_failed_total',
       value=response['request_failures'], labels={})
    yield metric

    # Metrics with labels for the documents loaded
    metric = Metric('svc_documents_loaded', 'Requests failed', 'gauge')
    for k, v in response['documents_loaded'].items():
      metric.add_sample('svc_documentes_loaded', value=v, labels={'repository': k})
    yield metric


if __name__ == '__main__':
  # Usage: json_exporter.py port endpoint
  start_http_server(int(sys.argv[1]))
  REGISTRY.register(JsonCollector(sys.argv[2]))
