#!/bin/bash
# wait a few seconds for grafana to start...
echo "Waiting a few seconds to let Grafana start..."
sleep 10
# create prometheus datasource
echo "Creating the datasource..."
curl -u admin:admin 'http://grafana:3000/api/datasources' -XPOST -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"name":"prometheus","type":"prometheus","typeLogoUrl":"public/app/plugins/datasource/prometheus/img/prometheus_logo.svg","access":"proxy","url":"http://prometheus:9090","password":"","user":"","database":"","basicAuth":false,"isDefault":true,"jsonData":{},"message":"created via curl."}'

# sleep infinity
sleep infinity
