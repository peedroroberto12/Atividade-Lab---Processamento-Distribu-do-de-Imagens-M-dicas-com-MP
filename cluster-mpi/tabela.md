# Tabela de Desempenho – Processamento Distribuído de Imagens com MPI

Média de 3 execuções por configuração. Tempo medido pelo processo root (inclui a geração da imagem, conforme o template).

## Tempo médio (ms) – COM atraso artificial (0.3 s × rank nos ranks ímpares)

| Processos | N = 2000 | N = 4000 |
|---|---|---|
| 1 | 59.79 | 162.34 |
| 2 | 352.56 | 487.70 |
| 4 | 1051.56 | 1257.67 |
| 8 | 2503.51 | 2891.01 |

## Tempo médio (ms) – SEM atraso artificial

| Processos | N = 2000 | N = 4000 |
|---|---|---|
| 1 | 69.20 | 160.61 |
| 2 | 47.23 | 266.79 |
| 4 | 129.45 | 367.91 |
| 8 | 389.25 | 816.47 |

## Detalhamento com speedup e eficiência

Speedup = T(1 processo) / T(p processos). Eficiência = Speedup / p.

| Imagem | Atraso | Processos | Média (ms) | Desvio (ms) | Speedup | Eficiência |
|---|---|---|---|---|---|---|
| 2000×2000 | 0.3 s × rank | 1 | 59.79 | 10.18 | 1.00 | 100.0% |
| 2000×2000 | 0.3 s × rank | 2 | 352.56 | 6.18 | 0.17 | 8.5% |
| 2000×2000 | 0.3 s × rank | 4 | 1051.56 | 30.19 | 0.06 | 1.4% |
| 2000×2000 | 0.3 s × rank | 8 | 2503.51 | 55.28 | 0.02 | 0.3% |
| 2000×2000 | não | 1 | 69.20 | 26.98 | 1.00 | 100.0% |
| 2000×2000 | não | 2 | 47.23 | 0.33 | 1.47 | 73.3% |
| 2000×2000 | não | 4 | 129.45 | 16.82 | 0.53 | 13.4% |
| 2000×2000 | não | 8 | 389.25 | 24.26 | 0.18 | 2.2% |
| 4000×4000 | 0.3 s × rank | 1 | 162.34 | 14.25 | 1.00 | 100.0% |
| 4000×4000 | 0.3 s × rank | 2 | 487.70 | 9.98 | 0.33 | 16.6% |
| 4000×4000 | 0.3 s × rank | 4 | 1257.67 | 25.28 | 0.13 | 3.2% |
| 4000×4000 | 0.3 s × rank | 8 | 2891.01 | 135.06 | 0.06 | 0.7% |
| 4000×4000 | não | 1 | 160.61 | 9.17 | 1.00 | 100.0% |
| 4000×4000 | não | 2 | 266.79 | 67.33 | 0.60 | 30.1% |
| 4000×4000 | não | 4 | 367.91 | 33.53 | 0.44 | 10.9% |
| 4000×4000 | não | 8 | 816.47 | 65.58 | 0.20 | 2.5% |

## Imagem pequena (500×500, sem atraso) – Questão 6

| Imagem | Atraso | Processos | Média (ms) | Desvio (ms) | Speedup | Eficiência |
|---|---|---|---|---|---|---|
| 500×500 | não | 1 | 3.03 | 0.12 | 1.00 | 100.0% |
| 500×500 | não | 2 | 9.07 | 9.31 | 0.33 | 16.7% |
| 500×500 | não | 4 | 120.62 | 108.09 | 0.03 | 0.6% |
| 500×500 | não | 8 | 228.49 | 80.09 | 0.01 | 0.2% |
