import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
EXE_C = os.path.join(RAIZ, "nrainhas.exe" if os.name == "nt" else "nrainhas")
MAIN_PY = os.path.join(RAIZ, "python", "main.py")

LINGUAGENS = ["python", "c"]
ALGORITMOS = ["forca_bruta", "backtracking"]

COLUNAS = ["linguagem", "algoritmo", "tipo", "n", "entrada", "repeticao",
           "chamadas", "tempo_ns", "contador", "resultado"]

COMPILAR = "gcc -O2 -std=c11 -Wall -Wextra -o nrainhas c/main.c c/forca_bruta.c c/backtracking.c"


def confere_executavel():
    if not os.path.exists(EXE_C):
        sys.exit(f"Executavel C nao encontrado. Compile antes com:\n  {COMPILAR}")


def executa(linguagem, algoritmo, arquivo, reps=1, tipo="todos", n=0, limite=None):
    if linguagem == "c":
        cmd = [EXE_C]
    else:
        cmd = [sys.executable, MAIN_PY]
    cmd += [algoritmo, arquivo, str(reps), tipo, str(n)]

    try:
        saida = subprocess.run(cmd, capture_output=True, text=True, timeout=limite, check=True)
    except subprocess.TimeoutExpired:
        return None
    return [linha.split(",") for linha in saida.stdout.splitlines() if linha]
