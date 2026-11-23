"""Medicao de memoria (bonus). Nao mede tempo e nao altera os resultados de
medir.py: so grava arquivos novos.

Saidas:
  entradas/entradas_memoria.txt  entradas usadas (melhor caso de n = 4 a 32 por
                                 construcao explicita + algumas medio e pior
                                 de entradas.txt para n = 4 a 9)
  resultados/memoria.csv         uma linha por execucao
  resultados/memoria_resumo.csv  media e desvio por implementacao, tipo e n
  resultados/ambiente_memoria.txt

Python: pico de memoria com tracemalloc e profundidade maxima de recursao
de `coloca` com sys.setprofile, em chamadas separadas.
C: executavel nrainhas_mem (compilado com -DMEDIR_MEMORIA), que mede a pilha
usada, a profundidade maxima e o tamanho dos vetores.

Uso: python medir_memoria.py
"""

import csv
import os
import platform
import statistics
import subprocess
import sys
import tracemalloc

from comum import RAIZ
from medir import nome_cpu, ram_gb

sys.path.insert(0, os.path.join(RAIZ, "python"))
import backtracking as mod_bt   # noqa: E402
import forca_bruta as mod_fb    # noqa: E402

EXE_MEM = os.path.join(RAIZ, "nrainhas_mem.exe" if os.name == "nt" else "nrainhas_mem")
ENTRADAS = os.path.join(RAIZ, "entradas", "entradas.txt")
ENTRADAS_MEM = os.path.join(RAIZ, "entradas", "entradas_memoria.txt")
PASTA = os.path.join(RAIZ, "resultados")

COMPILAR_MEM = ("gcc -O2 -std=c11 -Wall -Wextra -DMEDIR_MEMORIA -o nrainhas_mem "
                "c/main_memoria.c c/forca_bruta.c c/backtracking.c")

REPS = 15
NS_MELHOR = range(4, 33)        # MAXN = 32 no C
NS_PI = range(4, 10)            # n pequeno: tambem medio e pior
MEDIOS_POR_N = 3

ALGORITMOS = {"forca_bruta": mod_fb.forca_bruta, "backtracking": mod_bt.backtracking}

COLUNAS = ["linguagem", "algoritmo", "tipo", "n", "entrada", "repeticao",
           "profundidade_max", "memoria_bytes", "pilha_bytes", "estatico_bytes",
           "vetores_bytes", "contador", "resultado"]


# ------------------------------------------------------------- entradas

def construcao(n):
    """Solucao explicita das n-rainhas (Hoffman, Loessi e Moore, 1969), na
    forma de listas de pares e impares. Vale para n >= 4. Sem busca."""
    pares = list(range(2, n + 1, 2))
    impares = list(range(1, n + 1, 2))
    if n % 6 == 2:
        impares = [3, 1] + impares[3:] + [5]       # troca 1 e 3, 5 vai para o fim
    elif n % 6 == 3:
        pares = pares[1:] + [2]                    # 2 vai para o fim
        impares = impares[2:] + [1, 3]             # 1 e 3 vao para o fim
    return [x - 1 for x in pares + impares]        # linha i -> coluna p[i], base 0


def sem_ataques(p):
    """Teste independente: compara todos os pares de rainhas."""
    n = len(p)
    if sorted(p) != list(range(n)):
        return False
    return all(abs(p[i] - p[j]) != j - i for i in range(n) for j in range(i + 1, n))


def gera_entradas():
    linhas = []
    for n in NS_MELHOR:
        p = construcao(n)
        if not sem_ataques(p):
            sys.exit(f"construcao invalida para n = {n}: {p}")
        linhas.append(f"melhor {n} " + " ".join(map(str, p)))

    medios = {n: 0 for n in NS_PI}
    with open(ENTRADAS) as f:
        for linha in f:
            campos = linha.split()
            if not campos or int(campos[1]) not in NS_PI:
                continue
            tipo, n = campos[0], int(campos[1])
            if tipo == "medio" and medios[n] < MEDIOS_POR_N:
                medios[n] += 1
                linhas.append(linha.strip())
            elif tipo == "pior":
                linhas.append(linha.strip())

    with open(ENTRADAS_MEM, "w") as f:
        f.write("\n".join(linhas) + "\n")
    return [(c[0], int(c[1]), [int(x) for x in c[2:]]) for c in (l.split() for l in linhas)]


# --------------------------------------------------------------- Python

def pico_tracemalloc(algoritmo, n, pi, modo):
    """Pico de memoria alocada durante a chamada, descontada a base."""
    tracemalloc.reset_peak()
    base = tracemalloc.get_traced_memory()[0]
    resultado, contador = algoritmo(n, pi, modo)
    pico = tracemalloc.get_traced_memory()[1] - base
    return pico, resultado, contador


def profundidade_coloca(algoritmo, n, pi, modo):
    """Profundidade maxima de chamadas aninhadas a `coloca`."""
    atual = maximo = 0
    arquivo_bt = mod_bt.__file__

    def gancho(frame, evento, arg):
        nonlocal atual, maximo
        codigo = frame.f_code
        if codigo.co_name != "coloca" or codigo.co_filename != arquivo_bt:
            return
        if evento == "call":
            atual += 1
            maximo = max(maximo, atual)
        elif evento == "return":
            atual -= 1

    sys.setprofile(gancho)
    try:
        algoritmo(n, pi, modo)
    finally:
        sys.setprofile(None)
    return maximo


def formata(resultado, modo):
    if modo == "todas":
        return str(resultado)
    if resultado is None:
        return "sem_solucao"
    return "-".join(map(str, resultado))


def mede_uma(nome, k):
    """Mede a entrada k de entradas_memoria.txt com um algoritmo Python.
    Roda num processo novo (ver mede_python) e imprime linhas CSV."""
    algoritmo = ALGORITMOS[nome]
    with open(ENTRADAS_MEM) as f:
        campos = [l.split() for l in f if l.strip()][k]
    tipo, n, pi = campos[0], int(campos[1]), [int(x) for x in campos[2:]]
    modo = "todas" if tipo == "pior" else "primeira"

    # Fase 1: so tracemalloc (sem gancho de profiling ligado).
    tracemalloc.start()
    algoritmo(n, pi, modo)                     # aquecimento, nao registrado
    picos = [pico_tracemalloc(algoritmo, n, pi, modo) for _ in range(REPS)]
    tracemalloc.stop()

    # Fase 2: so o contador de profundidade.
    profs = [profundidade_coloca(algoritmo, n, pi, modo) for _ in range(REPS)]

    saida = csv.writer(sys.stdout, lineterminator="\n")
    for rep, ((pico, resultado, contador), prof) in enumerate(zip(picos, profs)):
        saida.writerow(["python", nome, tipo, n, k, rep, prof, pico, "", "", "",
                        contador, formata(resultado, modo)])


def mede_python(entradas):
    """Cada (algoritmo, entrada) roda num processo Python novo. No mesmo
    processo, objetos que sobram nas listas livres (freelists) do CPython de
    uma medicao para a outra mudam o pico visto pelo tracemalloc."""
    linhas = []
    for nome in ALGORITMOS:
        for k, (tipo, n, _) in enumerate(entradas):
            saida = subprocess.run([sys.executable, os.path.abspath(__file__), "--uma", nome, str(k)],
                                   capture_output=True, text=True, check=True)
            for campos in csv.reader(saida.stdout.splitlines()):
                linhas.append(campos[:3] + [int(c) for c in campos[3:8]] + ["", "", "",
                              int(campos[11]), campos[12]])
            print(f"python {nome:12} {tipo:6} n={n:2}  pico {linhas[-1][7]:6} B  prof {linhas[-1][6]}")
    return linhas


# -------------------------------------------------------------------- C

def mede_c():
    if not os.path.exists(EXE_MEM):
        print(f"\nAVISO: {EXE_MEM} nao encontrado; parte em C pulada. Compile com:\n  {COMPILAR_MEM}\n")
        return []
    linhas = []
    for nome in ALGORITMOS:
        try:
            saida = subprocess.run([EXE_MEM, nome, ENTRADAS_MEM, str(REPS)],
                                   capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError) as erro:
            print(f"\nAVISO: falha ao executar {EXE_MEM} ({erro}); parte em C pulada.\n")
            return []
        for texto in saida.stdout.splitlines():
            (ling, alg, tipo, n, k, rep, prof, pilha, estatico, vetores,
             contador, resultado) = texto.split(",")
            memoria = int(pilha) + int(estatico)
            linhas.append([ling, alg, tipo, int(n), int(k), int(rep), int(prof), memoria,
                           int(pilha), int(estatico), int(vetores), int(contador), resultado])
        print(f"c      {nome:12} {len(saida.stdout.splitlines())} execucoes")
    return linhas


# --------------------------------------------------------------- saidas

def grava_resumo(linhas):
    grupos = {}
    for l in linhas:
        grupos.setdefault((l[0], l[1], l[2], l[3]), []).append(l)
    with open(os.path.join(PASTA, "memoria_resumo.csv"), "w", newline="", encoding="utf-8") as f:
        saida = csv.writer(f)
        saida.writerow(["linguagem", "algoritmo", "tipo", "n", "execucoes",
                        "memoria_media_bytes", "memoria_desvio_bytes",
                        "profundidade_max", "pilha_media_bytes", "vetores_bytes"])
        for chave in sorted(grupos):
            g = grupos[chave]
            mem = [l[7] for l in g]
            profs = sorted({l[6] for l in g})
            pilha = [l[8] for l in g if l[8] != ""]
            vetores = sorted({l[10] for l in g if l[10] != ""})
            saida.writerow(list(chave) + [
                len(g), f"{statistics.mean(mem):.1f}",
                f"{statistics.stdev(mem) if len(mem) > 1 else 0.0:.1f}",
                "/".join(map(str, profs)),
                f"{statistics.mean(pilha):.1f}" if pilha else "",
                "/".join(map(str, vetores))])


def comando(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "desconhecido"


def grava_ambiente():
    linhas = [
        f"CPU: {nome_cpu()}",
        f"Nucleos logicos: {os.cpu_count()}",
        f"RAM: {ram_gb()}",
        f"Sistema operacional: {platform.system()} {platform.release()} ({platform.version()})",
        f"Python: {platform.python_implementation()} {platform.python_version()} "
        f"({platform.architecture()[0]})",
        "gcc --version:",
        *("  " + l for l in comando(["gcc", "--version"]).splitlines() if l.strip()),
        f"gcc -dumpmachine: {comando(['gcc', '-dumpmachine'])}",
        f"Compilacao: {COMPILAR_MEM}",
        f"Repeticoes: {REPS} por entrada; Python: tracemalloc e sys.setprofile em chamadas separadas",
    ]
    with open(os.path.join(PASTA, "ambiente_memoria.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas) + "\n")


def main():
    os.makedirs(PASTA, exist_ok=True)
    grava_ambiente()
    entradas = gera_entradas()
    print(f"{len(entradas)} entradas em {ENTRADAS_MEM}\n")

    linhas = mede_c() + mede_python(entradas)

    with open(os.path.join(PASTA, "memoria.csv"), "w", newline="", encoding="utf-8") as f:
        saida = csv.writer(f)
        saida.writerow(COLUNAS)
        saida.writerows(linhas)
    grava_resumo(linhas)
    print("\ngravado: memoria.csv, memoria_resumo.csv, ambiente_memoria.txt")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--uma":
        mede_uma(sys.argv[2], int(sys.argv[3]))
    else:
        main()
