#!/bin/bash
# Gera a tabela de desempenho do lab de uma vez.
# uso: bash bench.sh [repeticoes]   (padrão: 3)
cd "$(dirname "$0")"
REPS=${1:-3}
TAMANHOS="2000 4000"
PROCS="1 2 4 8"
ATRASOS="0.3 0"
PEQUENO=500
BRUTO=resultados_brutos.csv
TABELA=tabela.md

echo "linhas;atraso;procs;rep;tempo_ms" > $BRUTO

executa() {  # $1=linhas $2=atraso $3=procs $4=rep
  T=$(bash rodar.sh $3 $1 $2 2>/dev/null | grep "Tempo Total" | grep -oE "[0-9]+\.[0-9]+")
  [ -z "$T" ] && T="ERRO"
  echo "$1;$2;$3;$4;$T" >> $BRUTO
  printf "  %5s linhas | atraso %-3s | %d procs | rep %d -> %s ms\n" $1 $2 $3 $4 $T
}

TOTAL=$(( $(echo $TAMANHOS | wc -w) * $(echo $ATRASOS | wc -w) * $(echo $PROCS | wc -w) * REPS + $(echo $PROCS | wc -w) * REPS ))
echo "Executando $TOTAL rodadas ($REPS repetições cada)..."
for L in $TAMANHOS; do for A in $ATRASOS; do for P in $PROCS; do for R in $(seq 1 $REPS); do
  executa $L $A $P $R
done; done; done; done
for P in $PROCS; do for R in $(seq 1 $REPS); do
  executa $PEQUENO 0 $P $R
done; done

# ---------- Estatística e tabelas ----------
awk -F';' -v tams="$TAMANHOS" -v procs="$PROCS" -v atrs="$ATRASOS" -v peq="$PEQUENO" -v reps="$REPS" '
NR > 1 && $5 != "ERRO" {
  k = $1 SUBSEP $2 SUBSEP $3
  n[k]++; s[k] += $5; q[k] += $5 * $5
}
function media(k) { return n[k] ? s[k] / n[k] : -1 }
function desvio(k,  m) { if (n[k] < 2) return 0; m = media(k); v = (q[k] - n[k]*m*m) / (n[k]-1); return v > 0 ? sqrt(v) : 0 }
function linha_det(L, A, P,   k, b, m, sp, ef) {
  k = L SUBSEP A SUBSEP P; b = L SUBSEP A SUBSEP 1
  m = media(k)
  if (m < 0) { printf "| %s | %s | %s | ERRO | - | - | - |\n", L, (A == 0 ? "não" : A " s × rank"), P; return }
  sp = (media(b) > 0) ? media(b) / m : 0
  ef = sp / P * 100
  printf "| %s×%s | %s | %d | %.2f | %.2f | %.2f | %.1f%% |\n", L, L, (A == 0 ? "não" : A " s × rank"), P, m, desvio(k), sp, ef
}
END {
  nt = split(tams, T, " "); np = split(procs, P, " "); na = split(atrs, A, " ")

  print "# Tabela de Desempenho – Processamento Distribuído de Imagens com MPI\n"
  print "Média de " reps " execuções por configuração. Tempo medido pelo processo root (inclui a geração da imagem, conforme o template).\n"

  for (a = 1; a <= na; a++) {
    print "## Tempo médio (ms) – " (A[a] == 0 ? "SEM atraso artificial" : "COM atraso artificial (" A[a] " s × rank nos ranks ímpares)") "\n"
    printf "| Processos |"; for (t = 1; t <= nt; t++) printf " N = %s |", T[t]; print ""
    printf "|---|"; for (t = 1; t <= nt; t++) printf "---|"; print ""
    for (p = 1; p <= np; p++) {
      printf "| %s |", P[p]
      for (t = 1; t <= nt; t++) { m = media(T[t] SUBSEP A[a] SUBSEP P[p]); if (m < 0) printf " ERRO |"; else printf " %.2f |", m }
      print ""
    }
    print ""
  }

  print "## Detalhamento com speedup e eficiência\n"
  print "Speedup = T(1 processo) / T(p processos). Eficiência = Speedup / p.\n"
  print "| Imagem | Atraso | Processos | Média (ms) | Desvio (ms) | Speedup | Eficiência |"
  print "|---|---|---|---|---|---|---|"
  for (t = 1; t <= nt; t++) for (a = 1; a <= na; a++) for (p = 1; p <= np; p++) linha_det(T[t], A[a], P[p])
  print ""
  print "## Imagem pequena (" peq "×" peq ", sem atraso) – Questão 6\n"
  print "| Imagem | Atraso | Processos | Média (ms) | Desvio (ms) | Speedup | Eficiência |"
  print "|---|---|---|---|---|---|---|"
  for (p = 1; p <= np; p++) linha_det(peq, 0, P[p])
}' $BRUTO > $TABELA

echo
cat $TABELA
echo
echo "Arquivos gerados: $TABELA (tabela pronta) e $BRUTO (dados brutos)"
