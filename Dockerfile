FROM python:3.7-alpine
WORKDIR /opt/coinmarketcap-exporter
COPY ./requirements.txt .
RUN apk --no-cache add --virtual build-dependencies python-dev build-base \
    && pip install -r requirements.txt \
    && apk del build-dependencies
COPY ./coinmarketcap.py .

ENTRYPOINT ["python3", "coinmarketcap.py"]
