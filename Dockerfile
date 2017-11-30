FROM python:3.6
RUN pip install prometheus_client requests
RUN mkdir -p /opt/coinmarketcap-exporter
COPY ./ /opt/coinmarketcap-exporter/
WORKDIR /opt/coinmarketcap-exporter

ENTRYPOINT ["python3", "coinmarketcap.py"]
