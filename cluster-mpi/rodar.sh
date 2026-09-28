#!/bin/bash
# uso: ./rodar.sh <processos> [linhas] [fator_atraso]
cd "$(dirname "$0")"
NP=${1:-4}; LIN=${2:-2000}; ATR=${3:-0.3}
docker compose exec -T master su - mpiuser -c \
  "mpirun --hostfile hosts --oversubscribe -np $NP python3 processamento_imagens.py $LIN $ATR"
