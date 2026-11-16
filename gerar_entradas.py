import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
from backtracking import backtracking  # usado so para montar o melhor caso

SEED = 42
NS = list(range(4, 18))     
REPS = 20                     
SAIDA = os.path.join("entradas", "entradas.txt")


def linha(tipo, n, pi):
    return f"{tipo} {n} " + " ".join(str(c) for c in pi)


def main():
    rng = random.Random(SEED)
    linhas = []

    for n in NS:
        for _ in range(REPS):
            pi = list(range(n))
            rng.shuffle(pi)
            linhas.append(linha("medio", n, pi))

        base = list(range(n))
        rng.shuffle(base)
        solucao, _ = backtracking(n, base, "primeira")
        linhas.append(linha("melhor", n, solucao))

        linhas.append(linha("pior", n, list(range(n))))

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w") as f:
        f.write("\n".join(linhas) + "\n")

    print(f"{len(linhas)} entradas gravadas em {SAIDA}")

if __name__ == "__main__":
    main()
