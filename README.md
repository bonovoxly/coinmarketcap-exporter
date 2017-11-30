# coinmarketcap-exporter

A prometheus exporter for <https://coinmarketcap.com/>.

# Developing

- Build the image:

```
docker build -t coinmarketcap-exporter:latest .
```

- Run it while listening on localhost:9100:

```
docker run --rm coinmarketcap-exporter:latest
```

- Run it interactively:

```
docker run --rm -it --entrypoint=/bin/bash -v ${PWD}:/opt/coinmarketcap-exporter coinmarketcap-exporter:latest
```
