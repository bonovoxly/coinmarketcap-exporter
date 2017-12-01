# coinmarketcap-exporter

A prometheus exporter for <https://coinmarketcap.com/>.

Just a fun little demo, to both get more familiar with the Prometheus Exporter code and track some metrics on Bitcoin and Cryptocurrencies. 

# Developing

- Build the image:

```
docker build -t coinmarketcap-exporter:latest .
```

- Run it while listening on localhost:9100:

```
docker run --rm -p 127.0.0.1:9101:9101 coinmarketcap-exporter:latest
```

- Run it interactively:

```
docker run --rm -it --entrypoint=/bin/bash -p 127.0.0.1:9101:9101 -v ${PWD}:/opt/coinmarketcap-exporter coinmarketcap-exporter:latest
```

# Thanks and Links

- Coinmarketcap API link - <https://coinmarketcap.com/api/>
- Prometheus exporters - <https://prometheus.io/docs/instrumenting/writing_exporters/>
- Writing JSON exporters in Python from Robust Perception - <https://www.robustperception.io/writing-json-exporters-in-python/>

If you find this useful and want to contribute:

- BTC: `161a2z4A5J5ndVyytBXroN8hGcf6Cc8RA5`
- Ethereum: `0x9de200ba61af4a58c9fced2c1334110087a75f51`
- Litecoin: `LMGHysobMGv9dWUg1s6CDYP78HSasX8gTp`
