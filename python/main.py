import sys
import time

from backtracking import backtracking
from forca_bruta import forca_bruta

ALVO_NS = 1_000_000    
MAX_CHAMADAS = 100_000

ALGORITMOS = {"forca_bruta": forca_bruta, "backtracking": backtracking}


def ler_entradas(caminho):
    entradas = []
    with open(caminho) as f:
        for linha in f:
            campos = linha.split()
            if not campos:
                continue
            tipo = campos[0]
            n = int(campos[1])
            pi = [int(c) for c in campos[2:]]
            entradas.append((tipo, n, pi))
    return entradas


def formata_resultado(resultado, modo):
    if modo == "todas":
        return str(resultado)
    if resultado is None:
        return "sem_solucao"
    return "-".join(str(c) for c in resultado)


def main():
    if len(sys.argv) < 3:
        print("uso: main.py <forca_bruta|backtracking> <arquivo> [repeticoes] [tipo] [n]", file=sys.stderr)
        return 1

    nome = sys.argv[1]
    if nome not in ALGORITMOS:
        print(f"algoritmo desconhecido: {nome}", file=sys.stderr)
        return 1
    algoritmo = ALGORITMOS[nome]

    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    filtro_tipo = sys.argv[4] if len(sys.argv) > 4 else "todos"
    filtro_n = int(sys.argv[5]) if len(sys.argv) > 5 else 0

    entradas = ler_entradas(sys.argv[2])
    relogio = time.perf_counter_ns

    for k, (tipo, n, pi) in enumerate(entradas):
        if filtro_tipo != "todos" and filtro_tipo != tipo:
            continue
        if filtro_n != 0 and filtro_n != n:
            continue

        modo = "todas" if tipo == "pior" else "primeira"

        chamadas = 1
        while True:
            inicio = relogio()
            for _ in range(chamadas):
                resultado, contador = algoritmo(n, pi, modo)
            t = relogio() - inicio

            if t >= ALVO_NS or chamadas >= MAX_CHAMADAS:
                break
            chamadas = chamadas * 10 if t <= 0 else chamadas * ALVO_NS // t + 1
            chamadas = min(chamadas, MAX_CHAMADAS)

        for rep in range(reps):
            if not (rep == 0 and chamadas == 1):
                inicio = relogio()
                for _ in range(chamadas):
                    resultado, contador = algoritmo(n, pi, modo)
                t = relogio() - inicio

            tempo = t / chamadas
            print(f"python,{nome},{tipo},{n},{k},{rep},{chamadas},{tempo:.1f},{contador},"
                  f"{formata_resultado(resultado, modo)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())