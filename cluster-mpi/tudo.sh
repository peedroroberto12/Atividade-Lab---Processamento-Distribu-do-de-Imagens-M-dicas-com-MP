#!/bin/bash
# Sobe o cluster, configura SSH, copia o script e roda um teste com 4 processos
cd "$(dirname "$0")"
chmod +x *.sh
./start_cluster.sh && ./setup_ssh.sh && ./deploy.sh && ./rodar.sh 4
