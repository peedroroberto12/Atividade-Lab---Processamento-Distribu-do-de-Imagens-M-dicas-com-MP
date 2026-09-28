#!/bin/bash
cd "$(dirname "$0")"
for c in master worker1 worker2 worker3; do
  docker cp processamento_imagens.py $c:/home/mpiuser/
  docker compose exec -T $c chown mpiuser:mpiuser /home/mpiuser/processamento_imagens.py
  echo "Copiado para $c"
done
