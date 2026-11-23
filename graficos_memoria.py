"""Grafico do bonus de memoria a partir de resultados/memoria.csv.

Saida: resultados/fig7_memoria.png
  (a) memoria M(n) x n em escala linear, com ajuste linear e R2;
  (b) razao M(n) / n;
  (c) tempo da busca exaustiva (lido de resultados/resumo.csv, so leitura)
      e memoria, normalizados por n = 4, em escala log.

Funciona com ou sem as linhas de C em memoria.csv.

Uso: python graficos_memoria.py      (precisa de: pip install matplotlib)
"""

import csv
import os
import statistics

from graficos import COR_ALG, MARCA, MUDO, NOME_ALG, NOME_LING, PASTA, TEXTO, TRACO, plt, salva

ORDEM = [(a, l) for a in ("forca_bruta", "backtracking") for l in ("c", "python")]


def carrega_memoria():
    """dados[(linguagem, algoritmo)][n] = lista de memoria_bytes (melhor caso)."""
    dados = {}
    with open(os.path.join(PASTA, "memoria.csv"), newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["tipo"] != "melhor":
                continue
            chave = (linha["linguagem"], linha["algoritmo"])
            dados.setdefault(chave, {}).setdefault(int(linha["n"]), []).append(int(linha["memoria_bytes"]))
    return dados


def carrega_tempo():
    """tempo[(linguagem, algoritmo)][n] = media_ms da busca exaustiva (pior caso)."""
    tempo = {}
    with open(os.path.join(PASTA, "resumo.csv"), newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["tipo"] == "pior":
                tempo.setdefault((linha["linguagem"], linha["algoritmo"]), {})[int(linha["n"])] = float(linha["media_ms"])
    return tempo


def ajuste_linear(xs, ys):
    """Minimos quadrados: devolve (a, b, r2) de y = a + b x. r2 = None se y e constante."""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    if ss_tot == 0:
        return a, b, None
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return a, b, 1 - ss_res / ss_tot


def nome(algoritmo, linguagem):
    return f"{NOME_ALG[algoritmo]} ({NOME_LING[linguagem]})"


def main():
    memoria = carrega_memoria()
    tempo = carrega_tempo()
    series = [(a, l) for a, l in ORDEM if (l, a) in memoria]

    fig, (ax_a, ax_b, ax_c) = plt.subplots(1, 3, figsize=(15, 4.6))

    print(f"{'implementacao':28} {'a (B)':>9} {'b (B/n)':>9} {'R2':>8}")
    for algoritmo, linguagem in series:
        por_n = memoria[(linguagem, algoritmo)]
        ns = sorted(por_n)
        m = [statistics.mean(por_n[n]) for n in ns]
        estilo = dict(color=COR_ALG[algoritmo], marker=MARCA[linguagem], markersize=4)

        a, b, r2 = ajuste_linear(ns, m)
        texto_r2 = "constante" if r2 is None else f"R² = {r2:.4f}"
        print(f"{nome(algoritmo, linguagem):28} {a:9.1f} {b:9.2f} {texto_r2:>8}")
        ax_a.plot(ns, m, TRACO[linguagem], linewidth=1.5,
                  label=f"{nome(algoritmo, linguagem)}: {b:.1f} B/n, {texto_r2}", **estilo)
        ax_a.plot(ns, [a + b * n for n in ns], ":", color=MUDO, linewidth=1)

        ax_b.plot(ns, [y / n for y, n in zip(m, ns)], TRACO[linguagem], linewidth=1.5,
                  label=nome(algoritmo, linguagem), **estilo)
        ax_b.axhline(b, color=COR_ALG[algoritmo], linestyle=":", linewidth=1, alpha=0.6)

        t = tempo.get((linguagem, algoritmo), {})
        ns_t = sorted(n for n in t if n in por_n)
        if ns_t:
            n0 = ns_t[0]
            ax_c.plot(ns_t, [t[n] / t[n0] for n in ns_t], TRACO[linguagem], linewidth=1.5,
                      label=f"tempo: {nome(algoritmo, linguagem)}", **estilo)
            ax_c.plot(ns_t, [statistics.mean(por_n[n]) / statistics.mean(por_n[n0]) for n in ns_t],
                      TRACO[linguagem], linewidth=1, alpha=0.45, **estilo)

    ax_a.set_title("(a) Memória M(n), escala linear", loc="left")
    ax_a.set_ylabel("bytes")
    ax_a.set_ylim(bottom=0)
    ax_a.legend(fontsize=7.5, loc="upper left")

    ax_b.set_title("(b) Razão M(n) / n  (pontilhado: inclinação b)", loc="left")
    ax_b.set_ylabel("bytes por unidade de n")
    ax_b.set_ylim(bottom=0)
    ax_b.legend(fontsize=8)

    ax_c.set_yscale("log")
    ax_c.set_title("(c) Tempo (busca exaustiva) × memória", loc="left")
    ax_c.set_ylabel("valor / valor em n = 4, escala log")
    ax_c.plot([], [], "-", color=MUDO, linewidth=1, alpha=0.45, label="memória (linhas claras)")
    ax_c.legend(fontsize=7.5, loc="upper left")

    for ax in (ax_a, ax_b, ax_c):
        ax.set_xlabel("n (tamanho do tabuleiro)")

    fig.suptitle("Uso de memória: cresce em linha reta (Θ(n)), enquanto o tempo da busca exaustiva explode",
                 x=0.01, ha="left", fontsize=11, color=TEXTO)
    fig.tight_layout()
    salva(fig, "fig7_memoria.png")


if __name__ == "__main__":
    main()
