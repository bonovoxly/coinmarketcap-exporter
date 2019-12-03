FROM python:3.7
WORKDIR /opt/coinmarketcap-exporter
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./coinmarketcap.py .

ENTRYPOINT ["python3", "coinmarketcap.py"]
