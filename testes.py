import os
import sys
import tempfile

from comum import ALGORITMOS, LINGUAGENS, RAIZ, confere_executavel, executa

ARQUIVO = os.path.join(RAIZ, "entradas", "entradas.txt")
N_MAX = 9  

Q = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352, 10: 724}

EXTRAS = [
    "medio 1 0", "pior 1 0",
    "medio 2 0 1", "medio 2 1 0", "pior 2 0 1",
    "medio 3 0 1 2", "medio 3 2 0 1", "medio 3 1 2 0", "pior 3 0 1 2",
]

falhas = 0


def confere(condicao, mensagem):
    global falhas
    if not condicao:
        falhas += 1
        print("FALHOU:", mensagem)


def solucao_valida(p, n):
    """Teste independente: compara todos os pares de rainhas."""
    if sorted(p) != list(range(n)):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if abs(p[i] - p[j]) == j - i:
                return False
    return True


def main():
    confere_executavel()

    linhas = list(EXTRAS)
    with open(ARQUIVO) as f:
        for linha in f:
            campos = linha.split()
            if campos and int(campos[1]) <= N_MAX:
                linhas.append(linha.strip())

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
        tmp.write("\n".join(linhas) + "\n")
        caminho = tmp.name

    try:
        saidas = {}
        for linguagem in LINGUAGENS:
            for algoritmo in ALGORITMOS:
                saidas[(linguagem, algoritmo)] = executa(linguagem, algoritmo, caminho)
    finally:
        os.remove(caminho)

    referencia = saidas[("python", "forca_bruta")]
    confere(len(referencia) == len(linhas), "numero de linhas de saida diferente do numero de entradas")

    for k, entrada in enumerate(linhas):
        campos = entrada.split()
        tipo, n = campos[0], int(campos[1])
        pi = [int(c) for c in campos[2:]]
        resultado = referencia[k][9]

        for chave, saida in saidas.items():
            confere(saida[k][9] == resultado, f"{chave} deu {saida[k][9]}, esperado {resultado}: {entrada}")

        for algoritmo in ALGORITMOS:
            confere(saidas[("python", algoritmo)][k][8] == saidas[("c", algoritmo)][k][8],
                    f"{algoritmo}: contador diferente entre Python e C: {entrada}")

        if tipo == "pior":
            confere(int(resultado) == Q[n], f"contagem {resultado}, esperado {Q[n]}: {entrada}")
        elif n in (2, 3):
            confere(resultado == "sem_solucao", f"n={n} nao deveria ter solucao: {entrada}")
        else:
            p = [int(c) for c in resultado.split("-")]
            confere(solucao_valida(p, n), f"solucao invalida {p}: {entrada}")
            if tipo == "melhor":
                confere(p == pi, f"melhor caso deveria devolver pi: {entrada}")

    total = len(linhas) * len(saidas)
    if falhas:
        print(f"\n{falhas} falha(s) em {len(linhas)} entradas x {len(saidas)} implementacoes.")
        return 1
    print(f"OK: {len(linhas)} entradas x {len(saidas)} implementacoes = {total} execucoes conferidas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
