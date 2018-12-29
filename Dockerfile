FROM python:3.6
COPY ./requirements.txt /opt/coinmarketcap-exporter/requirements.txt
WORKDIR /opt/coinmarketcap-exporter
RUN pip install -r requirements.txt
COPY ./coinmarketcap.py /opt/coinmarketcap-exporter/

ENTRYPOINT ["python3", "coinmarketcap.py"]
