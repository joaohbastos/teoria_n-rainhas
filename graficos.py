"""Gera os graficos e a tabela-resumo a partir de resultados/medicoes.csv.

Saidas, na pasta resultados/:
  resumo.csv                   -- media e desvio-padrao por serie e tamanho
  fig1_teorico_vs_medido.png   -- razao T(n) / f(n)
  fig2_algoritmos.png          -- tempo da busca exaustiva, 4 implementacoes
  fig3_linguagens.png          -- quantas vezes o C e mais rapido que o Python
  fig4_casos.png               -- melhor, medio e pior caso
  fig5_espaco_de_busca.png     -- permutacoes, nos visitados e solucoes
  fig6_caso_medio.png          -- passos ate a primeira solucao

Uso: python graficos.py      (precisa de: pip install matplotlib)
"""

import csv
import math
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(RAIZ, "resultados")

# Cores: uma por algoritmo (ou por caso, na figura 4). A linguagem e
# diferenciada pelo traco e pelo marcador, nao pela cor.
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
COR_ALG = {"forca_bruta": AZUL, "backtracking": LARANJA}
COR_CASO = {"melhor": AZUL, "medio": LARANJA, "pior": VERDE}
TRACO = {"c": "-", "python": "--"}
MARCA = {"c": "o", "python": "s"}
NOME_ALG = {"forca_bruta": "Força bruta", "backtracking": "Backtracking"}
NOME_LING = {"c": "C", "python": "Python"}
NOME_CASO = {"melhor": "Melhor caso", "medio": "Caso médio", "pior": "Pior caso"}
TEXTO, MUDO, GRADE = "#0b0b0b", "#898781", "#e1e0d9"

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e",
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": TEXTO,
    "xtick.color": MUDO, "ytick.color": MUDO, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRADE,
    "grid.linewidth": 0.6, "lines.linewidth": 2, "lines.markersize": 6,
    "legend.frameon": False, "figure.dpi": 100, "savefig.dpi": 200,
})


# ---------------------------------------------------------------- dados

def carrega():
    """Le medicoes.csv e agrupa por (linguagem, algoritmo, tipo, n).

    Devolve dados[chave] = {"tempos": [...ns], "contadores": [...],
    "resultados": [...]}.
    """
    dados = {}
    with open(os.path.join(PASTA, "medicoes.csv"), newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            chave = (linha["linguagem"], linha["algoritmo"], linha["tipo"], int(linha["n"]))
            grupo = dados.setdefault(chave, {"tempos": [], "contadores": [], "resultados": []})
            grupo["tempos"].append(float(linha["tempo_ns"]))
            grupo["contadores"].append(int(linha["contador"]))
            grupo["resultados"].append(linha["resultado"])
    return dados


def serie(dados, linguagem, algoritmo, tipo):
    """Devolve (ns, medias_ns, desvios_ns, contadores_medios) em ordem de n."""
    ns = sorted(n for (l, a, t, n) in dados if (l, a, t) == (linguagem, algoritmo, tipo))
    medias, desvios, contadores = [], [], []
    for n in ns:
        grupo = dados[(linguagem, algoritmo, tipo, n)]
        medias.append(statistics.mean(grupo["tempos"]))
        desvios.append(statistics.stdev(grupo["tempos"]) if len(grupo["tempos"]) > 1 else 0.0)
        contadores.append(statistics.mean(grupo["contadores"]))
    return ns, medias, desvios, contadores


def grava_resumo(dados):
    with open(os.path.join(PASTA, "resumo.csv"), "w", newline="", encoding="utf-8") as f:
        saida = csv.writer(f)
        saida.writerow(["linguagem", "algoritmo", "tipo", "n", "execucoes",
                        "media_ms", "desvio_ms", "contador_medio"])
        for (linguagem, algoritmo, tipo, n) in sorted(dados):
            grupo = dados[(linguagem, algoritmo, tipo, n)]
            tempos = grupo["tempos"]
            desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
            saida.writerow([linguagem, algoritmo, tipo, n, len(tempos),
                            f"{statistics.mean(tempos) / 1e6:.6f}", f"{desvio / 1e6:.6f}",
                            f"{statistics.mean(grupo['contadores']):.1f}"])


# ------------------------------------------------------------- utilidades

def eixo_n(ax, ns):
    ax.set_xlabel("n (tamanho do tabuleiro)")
    ax.set_xticks(range(min(ns), max(ns) + 1))


def rotulo_final(ax, x, y, texto, cor):
    """Escreve o nome da serie ao lado do ultimo ponto."""
    ax.annotate(texto, (x, y), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=9, color=TEXTO)


def salva(fig, nome):
    fig.savefig(os.path.join(PASTA, nome), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("gravado:", nome)


# --------------------------------------------------------------- figuras

def fig1_teorico_vs_medido(dados):
    """Razao T(n) / f(n). Se f(n) e a complexidade correta, a razao tende
    a uma constante (linha horizontal)."""
    paineis = [
        ("forca_bruta", "Força bruta:  T(n) / (n! · n)", lambda n, cont: math.factorial(n) * n, False),
        ("backtracking", "Backtracking:  T(n) / (n · N(n))", lambda n, cont: n * cont, False),
        ("backtracking", "Backtracking:  T(n) / (n! · n)", lambda n, cont: math.factorial(n) * n, True),
    ]
    fig, eixos = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, (algoritmo, titulo, f, log) in zip(eixos, paineis):
        todos_ns = []
        for linguagem in ("c", "python"):
            ns, medias, _, contadores = serie(dados, linguagem, algoritmo, "pior")
            if not ns:
                continue
            razoes = [t / f(n, c) for n, t, c in zip(ns, medias, contadores)]
            # Normaliza pela media dos 3 maiores n, para C e Python caberem
            # no mesmo eixo: o que importa e a forma da curva.
            base = statistics.mean(razoes[-3:])
            razoes = [r / base for r in razoes]
            ax.plot(ns, razoes, TRACO[linguagem], marker=MARCA[linguagem],
                    color=COR_ALG[algoritmo], label=NOME_LING[linguagem])
            todos_ns += ns
        if not log:
            ax.axhline(1, color=MUDO, linewidth=1, linestyle=":")
            ax.set_ylim(bottom=0)
        else:
            ax.set_yscale("log")
        ax.set_title(titulo, loc="left")
        ax.set_ylabel("razão normalizada")
        eixo_n(ax, todos_ns)
        ax.legend()
    fig.suptitle("Teórico × medido (busca exaustiva): a razão fica constante quando f(n) é a complexidade correta",
                 x=0.01, ha="left", fontsize=11, color=TEXTO)
    fig.tight_layout()
    salva(fig, "fig1_teorico_vs_medido.png")


def fig2_algoritmos(dados, limite_s=60):
    """Tempo da busca exaustiva nas quatro implementacoes, em escala log."""
    fig, ax = plt.subplots(figsize=(8.5, 5))
    todos_ns = []
    for algoritmo in ("forca_bruta", "backtracking"):
        for linguagem in ("c", "python"):
            ns, medias, desvios, _ = serie(dados, linguagem, algoritmo, "pior")
            if not ns:
                continue
            seg = [t / 1e9 for t in medias]
            erro = [d / 1e9 for d in desvios]
            nome = f"{NOME_ALG[algoritmo]} ({NOME_LING[linguagem]})"
            ax.errorbar(ns, seg, yerr=erro, fmt=TRACO[linguagem], marker=MARCA[linguagem],
                        color=COR_ALG[algoritmo], capsize=2, elinewidth=1, label=nome)
            todos_ns += ns
    ax.axhline(limite_s, color=MUDO, linewidth=1, linestyle=":")
    ax.annotate(f"limite de {limite_s} s", (min(todos_ns), limite_s), xytext=(0, 4),
                textcoords="offset points", fontsize=9, color="#52514e")
    ax.set_yscale("log")
    ax.set_ylabel("tempo médio (s), escala log")
    ax.set_title("Busca exaustiva: força bruta × backtracking, em Python e em C", loc="left")
    eixo_n(ax, todos_ns)
    ax.legend(loc="lower right")
    fig.tight_layout()
    salva(fig, "fig2_algoritmos.png")


def fig3_linguagens(dados):
    """Quantas vezes o C e mais rapido que o Python, por tamanho."""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    todos_ns = []
    for algoritmo in ("forca_bruta", "backtracking"):
        ns_c, t_c, _, _ = serie(dados, "c", algoritmo, "pior")
        ns_p, t_p, _, _ = serie(dados, "python", algoritmo, "pior")
        comuns = [n for n in ns_c if n in ns_p]
        razoes = [t_p[ns_p.index(n)] / t_c[ns_c.index(n)] for n in comuns]
        if not comuns:
            continue
        ax.plot(comuns, razoes, "-", marker="o", color=COR_ALG[algoritmo], label=NOME_ALG[algoritmo])
        rotulo_final(ax, comuns[-1], razoes[-1], NOME_ALG[algoritmo], COR_ALG[algoritmo])
        todos_ns += comuns
    ax.set_ylim(bottom=0)
    ax.set_ylabel("tempo Python / tempo C")
    ax.set_title("Python × C na busca exaustiva: quantas vezes o C é mais rápido", loc="left")
    eixo_n(ax, todos_ns)
    ax.set_xlim(right=max(todos_ns) + 1.6)
    ax.legend(loc="upper right")
    fig.tight_layout()
    salva(fig, "fig3_linguagens.png")


def fig4_casos(dados):
    """Melhor, medio e pior caso de cada implementacao."""
    fig, eixos = plt.subplots(2, 2, figsize=(11, 7.5), sharey=True)
    for i, linguagem in enumerate(("c", "python")):
        for j, algoritmo in enumerate(("forca_bruta", "backtracking")):
            ax = eixos[i][j]
            todos_ns = []
            for tipo in ("melhor", "medio", "pior"):
                ns, medias, desvios, _ = serie(dados, linguagem, algoritmo, tipo)
                if not ns:
                    continue
                seg = [t / 1e9 for t in medias]
                ax.plot(ns, seg, "-", marker="o", color=COR_CASO[tipo], label=NOME_CASO[tipo])
                todos_ns += ns
            ax.set_yscale("log")
            ax.set_title(f"{NOME_ALG[algoritmo]} ({NOME_LING[linguagem]})", loc="left")
            if j == 0:
                ax.set_ylabel("tempo médio (s), escala log")
            eixo_n(ax, todos_ns)
            ax.legend(loc="upper left")
    fig.tight_layout()
    salva(fig, "fig4_casos.png")


def fig5_espaco_de_busca(dados):
    """Quanto cada algoritmo percorre na busca exaustiva. Os contadores nao
    dependem da linguagem; usa-se a que foi mais longe em cada algoritmo."""
    def mais_longa(algoritmo):
        opcoes = [serie(dados, l, algoritmo, "pior") for l in ("c", "python")]
        return max(opcoes, key=lambda s: len(s[0]))

    ns_fb, _, _, perms = mais_longa("forca_bruta")
    ns_bt, _, _, nos = mais_longa("backtracking")
    linguagem_bt = "c" if dados.get(("c", "backtracking", "pior", ns_bt[-1])) else "python"
    solucoes = [int(dados[(linguagem_bt, "backtracking", "pior", n)]["resultados"][0]) for n in ns_bt]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ns_fat = ns_bt
    ax.plot(ns_fat, [math.factorial(n) for n in ns_fat], ":", color=AZUL, linewidth=1.5)
    ax.plot(ns_fb, perms, "-", marker="o", color=AZUL, label="Permutações testadas (força bruta) = n!")
    ax.plot(ns_bt, nos, "-", marker="o", color=LARANJA, label="Nós visitados (backtracking) = N(n)")
    ax.plot(ns_bt, [max(s, 0.5) for s in solucoes], "-", marker="o", color=VERDE, label="Soluções = Q(n)")
    rotulo_final(ax, ns_fat[-1], math.factorial(ns_fat[-1]), "n!", AZUL)
    rotulo_final(ax, ns_bt[-1], nos[-1], "N(n)", LARANJA)
    rotulo_final(ax, ns_bt[-1], solucoes[-1], "Q(n)", VERDE)
    ax.set_yscale("log")
    ax.set_ylabel("quantidade, escala log")
    ax.set_title("Espaço de busca: o que a poda elimina", loc="left")
    eixo_n(ax, ns_bt)
    ax.set_xlim(right=max(ns_bt) + 1)
    ax.legend(loc="upper left")
    fig.tight_layout()
    salva(fig, "fig5_espaco_de_busca.png")


def fig6_caso_medio(dados):
    """Passos ate a primeira solucao no caso medio, contra a estimativa
    (n! + 1) / (Q(n) + 1) para a forca bruta."""
    def mais_longa(algoritmo, tipo):
        opcoes = [serie(dados, l, algoritmo, tipo) for l in ("c", "python")]
        return max(opcoes, key=lambda s: len(s[0]))

    ns_fb, _, _, k_medio = mais_longa("forca_bruta", "medio")
    ns_bt, _, _, nos_medio = mais_longa("backtracking", "medio")
    ns_q, _, _, _ = mais_longa("backtracking", "pior")
    linguagem_q = "c" if dados.get(("c", "backtracking", "pior", ns_q[-1])) else "python"
    q = {n: int(dados[(linguagem_q, "backtracking", "pior", n)]["resultados"][0]) for n in ns_q}
    ns_est = [n for n in ns_fb if n in q]
    estimativa = [(math.factorial(n) + 1) / (q[n] + 1) for n in ns_est]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.plot(ns_fb, k_medio, "-", marker="o", color=AZUL, label="Força bruta: permutações testadas (média)")
    ax.plot(ns_est, estimativa, ":", marker="s", color=AZUL, linewidth=1.5,
            label="Força bruta: estimativa (n! + 1) / (Q(n) + 1)")
    ax.plot(ns_bt, nos_medio, "-", marker="o", color=LARANJA, label="Backtracking: nós visitados (média)")
    ax.set_yscale("log")
    ax.set_ylabel("passos até a primeira solução, escala log")
    ax.set_title("Caso médio: passos até a primeira solução (20 ordens sorteadas por n)", loc="left")
    eixo_n(ax, ns_bt)
    ax.legend(loc="upper left")
    fig.tight_layout()
    salva(fig, "fig6_caso_medio.png")


def main():
    dados = carrega()
    grava_resumo(dados)
    print("gravado: resumo.csv")
    fig1_teorico_vs_medido(dados)
    fig2_algoritmos(dados)
    fig3_linguagens(dados)
    fig4_casos(dados)
    fig5_espaco_de_busca(dados)
    fig6_caso_medio(dados)


if __name__ == "__main__":
    main()
