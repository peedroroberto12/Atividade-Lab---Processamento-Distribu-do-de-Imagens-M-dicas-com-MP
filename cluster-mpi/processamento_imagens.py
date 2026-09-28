from mpi4py import MPI
import numpy as np
import time
import random
import sys  # pra ler o tamanho e o atraso pela linha de comando

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Parâmetros padrão de teste
# deixei o tamanho e o atraso configuráveis pra conseguir testar 2000 e 4000
# sem ficar editando o código toda hora
# uso: python3 processamento_imagens.py [linhas] [fator_atraso]
# sem argumentos roda igual ao template (2000x2000 e atraso 0.3)
LINHAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
COLUNAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000  # imagem sempre quadrada
FATOR_ATRASO = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
LIMIAR_SUSPEITO = 200
LIMIAR_ALTO = 230
PCT_CRITICO = 5.0 # percentual em %
PCT_ALTO_CRITICO = 1.0  # se passar de 1% de pixels muito claros, a faixa já vira crítica

imagem_completa = None
parametros = None
t_inicio = time.time()

# Etapa 2 & 3: Processo 0 gera radiografia e define configuracoes
if rank == 0:
    print(f"[Master] Inicializando análise com {size} processos MPI...")
    # Geração simulada da radiografia (só ruído escuro, tipo um pulmão "normal")
    imagem_completa = np.random.randint(30, 90, size=(LINHAS, COLUNAS), dtype=np.uint8)
    # Injeção de foco suspeito artificial no pulmão direito
    # o template tinha as coordenadas fixas, e com 500x500 o foco ficava fora da imagem.
    # Agora é proporcional: no 2000x2000 dá exatamente o [600:900, 1200:1600] original
    l0, l1 = int(LINHAS * 0.30), int(LINHAS * 0.45)
    c0, c1 = int(COLUNAS * 0.60), int(COLUNAS * 0.80)
    imagem_completa[l0:l1, c0:c1] = np.random.randint(180, 245, size=(l1 - l0, c1 - c0), dtype=np.uint8)
    parametros = {
        'linhas': LINHAS,
        'colunas': COLUNAS,
        'limiar_suspeito': LIMIAR_SUSPEITO,
        'limiar_alto': LIMIAR_ALTO,
        'pct_critico': PCT_CRITICO,
        'pct_alto_critico': PCT_ALTO_CRITICO,  # os workers precisam saber disso também
        'fator_atraso': FATOR_ATRASO           # idem, é usado na Etapa 8
    }

# Etapa 3: Difusão dos parâmetros via Broadcast
# todo mundo precisa dos mesmos parâmetros, então manda igual pra todos
parametros = comm.bcast(parametros, root=0)

# Etapa 4: Sincronização inicial
comm.Barrier()

# Etapa 5: Divisão e distribuição da imagem via Scatter
# o np.split do template só funciona se a divisão for exata.
# Testei com 2003 linhas e 4 processos e ele quebrou, então troquei pelo np.array_split,
# que joga as linhas que sobram nos primeiros processos (fica 501, 501, 501, 500)
linhas_por_proc = parametros['linhas'] // size
resto = parametros['linhas'] % size
qtd_linhas = [linhas_por_proc + (1 if r < resto else 0) for r in range(size)]  # quantas linhas cada um recebe
linha_inicio_local = sum(qtd_linhas[:rank])                                     # onde começa a faixa de cada um
bloco_local = np.empty((qtd_linhas[rank], parametros['colunas']), dtype=np.uint8)
blocos_divididos = None
if rank == 0:
    blocos_divididos = np.array_split(imagem_completa, size, axis=0)
bloco_local = comm.scatter(blocos_divididos, root=0)

# Etapa 6 & 7: Processamento e classificação local
# essa parte estava vazia no template
total_local = bloco_local.size
soma_local = int(np.sum(bloco_local, dtype=np.int64))  # int64 pra soma não estourar em imagem grande
max_local = int(np.max(bloco_local))
# divide a faixa ao meio pelas colunas: metade da esquerda e metade da direita
# funciona porque cada processo recebe as linhas inteiras, então a coluna não muda
col_meio = parametros['colunas'] // 2
esq_mask = bloco_local[:, :col_meio] > parametros['limiar_suspeito']
dir_mask = bloco_local[:, col_meio:] > parametros['limiar_suspeito']
suspeitos_esq = int(np.sum(esq_mask))
suspeitos_dir = int(np.sum(dir_mask))
suspeitos_local = suspeitos_esq + suspeitos_dir
altamente_suspeitos_local = int(np.sum(bloco_local > parametros['limiar_alto']))

# Classificação da faixa
pct_suspeito = (suspeitos_local / total_local) * 100.0
pct_alto = (altamente_suspeitos_local / total_local) * 100.0
# o enunciado da Etapa 7 fala em "presença expressiva de pixels altamente suspeitos",
# então a faixa vira crítica por qualquer um dos dois critérios
if pct_suspeito >= parametros['pct_critico'] or pct_alto >= parametros['pct_alto_critico']:
    classificacao_local = "CRÍTICA"
elif pct_suspeito >= 1.0:
    classificacao_local = "ATENÇÃO"
else:
    classificacao_local = "NORMAL"

# Etapa 8: Simulação de heterogeneidade de nós
# os ranks ímpares fingem ser máquinas lentas (quanto maior o rank, mais demora)
if rank % 2 != 0:
    time.sleep(parametros['fator_atraso'] * rank)  # fator vem da linha de comando (0 = sem atraso)

# Etapa 9: Sincronização pré-consolidação
# aqui todo mundo fica esperando o mais lento chegar
comm.Barrier()

# Etapa 10: Consolidação numérica com MPI_Reduce
# números que dá pra somar (ou pegar o máximo) vão direto pro processo 0
total_pixels_global = comm.reduce(total_local, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_local, op=MPI.SUM, root=0)
max_global = comm.reduce(max_local, op=MPI.MAX, root=0)
suspeitos_global = comm.reduce(suspeitos_local, op=MPI.SUM, root=0)
altos_global = comm.reduce(altamente_suspeitos_local, op=MPI.SUM, root=0)
esq_global = comm.reduce(suspeitos_esq, op=MPI.SUM, root=0)
dir_global = comm.reduce(suspeitos_dir, op=MPI.SUM, root=0)

# Etapa 11: Coleta de estatísticas por processo com MPI_Gather
# o relatório de cada faixa não dá pra somar, então junta tudo numa lista
relatorio_local = {
    'rank': rank,
    'linhas_inicio': linha_inicio_local,                         # com o array_split a conta do template errava
    'linhas_fim': linha_inicio_local + bloco_local.shape[0] - 1,
    'pixels': total_local,
    'suspeitos': suspeitos_local,
    'classificacao': classificacao_local,
    'max_local': max_local
}
todos_relatorios = comm.gather(relatorio_local, root=0)

# Etapa 12: Relatório final emitido pelo processo 0
if rank == 0:
    t_total = (time.time() - t_inicio) * 1000.0
    media_intensidade = soma_global / total_pixels_global
    taxa_comprometida = (suspeitos_global / total_pixels_global) * 100.0
    print("\n" + "="*60)
    print(" RELATÓRIO CONSOLIDADO DE TRIAGEM DISTRIBUÍDA")
    print("="*60)
    print(f"Dimensões do Exame : {LINHAS} x {COLUNAS} pixels")
    print(f"Processos MPI Utilizados: {size}")
    # a Etapa 12 pede pra mostrar os limiares usados
    print(f"Limiares Adotados : suspeito > {LIMIAR_SUSPEITO} | alto > {LIMIAR_ALTO} | crítico >= {PCT_CRITICO}%")
    print(f"Tempo Total de Execução : {t_total:.2f} ms")
    print(f"Intensidade Média Global: {media_intensidade:.2f} (Máxima: {max_global})")
    print(f"Total de Pixels Suspeitos: {suspeitos_global} ({taxa_comprometida:.2f}%)")
    print(f"Pixels Altamente Suspeitos: {altos_global}")
    print(f" - Pulmão Esquerdo : {esq_global} suspeitos")
    print(f" - Pulmão Direito : {dir_global} suspeitos")
    lado_critico = "Direito" if dir_global > esq_global else "Esquerdo" if esq_global > dir_global else "Equilibrado"
    print(f"Maior Concentração : Pulmão {lado_critico}")
    print("\n--- Auditoria por Processo (Faixas) ---")
    for rel in todos_relatorios:
        print(f"Processo {rel['rank']:02d} | Linhas [{rel['linhas_inicio']:04d}-{rel['linhas_fim']:04d}] | "
              f"Suspeitos: {rel['suspeitos']:05d} | Máx: {rel['max_local']:03d} | Faixa: {rel['classificacao']}")

    # a Etapa 12 também pede uma classificação geral do exame
    # se tiver qualquer faixa crítica, o exame todo já é tratado como crítico
    n_criticas = sum(1 for rel in todos_relatorios if rel['classificacao'] == "CRÍTICA")
    n_atencao = sum(1 for rel in todos_relatorios if rel['classificacao'] == "ATENÇÃO")
    if taxa_comprometida >= PCT_CRITICO or n_criticas > 0:
        diagnostico = "Quadro Crítico / Alta Concentração de Alterações"
    elif taxa_comprometida >= 1.0 or n_atencao > 0:
        diagnostico = "Atenção Clínica"
    else:
        diagnostico = "Sem Indícios Relevantes"
    print("\n--- Classificação Geral da Radiografia ---")
    print(f">>> {diagnostico} ({n_criticas} faixa(s) crítica(s), {n_atencao} em atenção)")
    print("="*60 + "\n")