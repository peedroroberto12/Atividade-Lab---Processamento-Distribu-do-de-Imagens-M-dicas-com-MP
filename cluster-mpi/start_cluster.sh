#!/bin/bash
cd "$(dirname "$0")"
docker compose build
docker compose up -d
for n in master worker1 worker2 worker3; do docker compose exec -T $n service ssh start; done
docker ps
echo "Cluster iniciado."
