FROM python:3.6
RUN pip install prometheus_client requests cachetools
RUN mkdir -p /opt/coinmarketcap-exporter
COPY ./coinmarketcap.py /opt/coinmarketcap-exporter/
WORKDIR /opt/coinmarketcap-exporter

ENTRYPOINT ["python3", "coinmarketcap.py"]
