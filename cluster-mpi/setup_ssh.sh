#!/bin/bash
cd "$(dirname "$0")"
echo "Gerando chave no master..."
docker compose exec -T -u mpiuser master bash -c \
  'test -f ~/.ssh/id_rsa || ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa'
PUBKEY=$(docker compose exec -T master cat /home/mpiuser/.ssh/id_rsa.pub)
for node in master worker1 worker2 worker3; do
  echo "Configurando $node..."
  echo "$PUBKEY" | docker compose exec -T $node bash -c "
    mkdir -p /home/mpiuser/.ssh &&
    cat > /home/mpiuser/.ssh/authorized_keys &&
    chown -R mpiuser:mpiuser /home/mpiuser/.ssh &&
    chmod 700 /home/mpiuser/.ssh &&
    chmod 600 /home/mpiuser/.ssh/authorized_keys"
done
echo "Criando hostfile e config do SSH..."
docker compose exec -T -u mpiuser master bash -c '
printf "master slots=2\nworker1 slots=2\nworker2 slots=2\nworker3 slots=2\n" > ~/hosts
printf "Host master worker1 worker2 worker3\n  StrictHostKeyChecking no\n" > ~/.ssh/config
chmod 600 ~/.ssh/config'
echo "Testando..."
docker compose exec -T master su - mpiuser -c "mpirun --hostfile hosts -np 8 hostname"
echo "SSH configurado."
