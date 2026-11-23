"""Testes da instrumentacao de memoria (bonus). Nao substitui testes.py.

Confere que:
1. a construcao explicita gera solucoes validas para n = 4 a 32;
2. a profundidade maxima de `coloca` e n + 1 no backtracking e 0 na forca
   bruta, em Python e em C, e e igual nas duas linguagens;
3. o executavel instrumentado (nrainhas_mem) devolve a mesma resposta e o
   mesmo contador que a implementacao Python, ou seja, a instrumentacao nao
   mudou o algoritmo;
4. em C, a pilha do backtracking cresce o mesmo numero de bytes a cada nivel
   e a da forca bruta nao depende de n.

Uso: python testes_memoria.py   (precisa de nrainhas_mem; ver README)
"""

import os
import subprocess
import sys
import tempfile

from medir_memoria import (ALGORITMOS, COMPILAR_MEM, EXE_MEM, ENTRADAS, construcao,
                           formata, profundidade_coloca, sem_ataques)

N_MAX_PI = 8      # medio e pior so ate aqui, para o teste ser rapido

falhas = 0


def confere(condicao, mensagem):
    global falhas
    if not condicao:
        falhas += 1
        print("FALHOU:", mensagem)


def entradas_de_teste():
    linhas = [f"melhor {n} " + " ".join(map(str, construcao(n))) for n in range(4, 33)]
    with open(ENTRADAS) as f:
        for linha in f:
            campos = linha.split()
            if campos and campos[0] in ("medio", "pior") and int(campos[1]) <= N_MAX_PI:
                linhas.append(linha.strip())
    return linhas


def main():
    if not os.path.exists(EXE_MEM):
        sys.exit(f"Executavel nao encontrado. Compile antes com:\n  {COMPILAR_MEM}")

    for n in range(4, 33):
        confere(sem_ataques(construcao(n)), f"construcao invalida para n = {n}")

    linhas = entradas_de_teste()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
        tmp.write("\n".join(linhas) + "\n")
        caminho = tmp.name
    try:
        saida_c = {}
        for nome in ALGORITMOS:
            saida = subprocess.run([EXE_MEM, nome, caminho, "1"],
                                   capture_output=True, text=True, check=True)
            saida_c[nome] = [l.split(",") for l in saida.stdout.splitlines()]
    finally:
        os.remove(caminho)

    pilha_melhor = {nome: {} for nome in ALGORITMOS}
    for nome, algoritmo in ALGORITMOS.items():
        confere(len(saida_c[nome]) == len(linhas), f"{nome}: numero de linhas do C")
        esperado = (lambda n: n + 1) if nome == "backtracking" else (lambda n: 0)
        for entrada, c in zip(linhas, saida_c[nome]):
            campos = entrada.split()
            tipo, n, pi = campos[0], int(campos[1]), [int(x) for x in campos[2:]]
            modo = "todas" if tipo == "pior" else "primeira"

            prof_py = profundidade_coloca(algoritmo, n, pi, modo)
            resultado, contador = algoritmo(n, pi, modo)
            prof_c = int(c[6])

            confere(prof_py == esperado(n), f"{nome} Python: profundidade {prof_py}, esperado {esperado(n)}: {entrada}")
            confere(prof_c == esperado(n), f"{nome} C: profundidade {prof_c}, esperado {esperado(n)}: {entrada}")
            confere(prof_py == prof_c, f"{nome}: profundidade Python {prof_py} != C {prof_c}: {entrada}")
            confere(c[11] == formata(resultado, modo), f"{nome}: resposta C {c[11]} != Python: {entrada}")
            confere(int(c[10]) == contador, f"{nome}: contador C {c[10]} != Python {contador}: {entrada}")
            if tipo == "melhor":
                pilha_melhor[nome][n] = int(c[7])

    bt = pilha_melhor["backtracking"]
    passos = {bt[n + 1] - bt[n] for n in range(4, 32)}
    confere(len(passos) == 1 and passos.pop() > 0, f"pilha do backtracking nao cresce linearmente: {bt}")
    fb = pilha_melhor["forca_bruta"]
    confere(len(set(fb.values())) == 1, f"pilha da forca bruta varia com n: {fb}")

    total = len(linhas) * len(ALGORITMOS)
    if falhas:
        print(f"\n{falhas} falha(s).")
        return 1
    print(f"OK: {len(linhas)} entradas x {len(ALGORITMOS)} algoritmos x 2 linguagens "
          f"({total * 2} execucoes) conferidas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
