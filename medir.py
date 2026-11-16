import csv
import os
import platform
import subprocess
import sys
import time

from comum import (ALGORITMOS, COLUNAS, COMPILAR, LINGUAGENS, RAIZ,
                   confere_executavel, executa)

ARQUIVO = os.path.join(RAIZ, "entradas", "entradas.txt")
PASTA = os.path.join(RAIZ, "resultados")
TIPOS = ["melhor", "medio", "pior"]

RAPIDO = "--rapido" in sys.argv
REPS = 3 if RAPIDO else 15        
LIMITE_S = 5 if RAPIDO else 60    


def tamanhos_no_arquivo():
    ns = set()
    with open(ARQUIVO) as f:
        for linha in f:
            campos = linha.split()
            if campos:
                ns.add(int(campos[1]))
    return sorted(ns)


def nome_cpu():
    if os.name == "nt":
        try:
            import winreg
            chave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                   r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            return winreg.QueryValueEx(chave, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    try:
        with open("/proc/cpuinfo") as f:
            for linha in f:
                if linha.startswith("model name"):
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconhecida"


def ram_gb():
    try:
        if os.name == "nt":
            import ctypes

            class Memoria(ctypes.Structure):
                _fields_ = [("tamanho", ctypes.c_ulong), ("carga", ctypes.c_ulong),
                            ("total", ctypes.c_ulonglong), ("livre", ctypes.c_ulonglong),
                            ("r1", ctypes.c_ulonglong), ("r2", ctypes.c_ulonglong),
                            ("r3", ctypes.c_ulonglong), ("r4", ctypes.c_ulonglong),
                            ("r5", ctypes.c_ulonglong)]

            m = Memoria()
            m.tamanho = ctypes.sizeof(Memoria)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return f"{m.total / 2**30:.1f} GB"
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return f"{total / 2**30:.1f} GB"
    except (OSError, ValueError, AttributeError):
        return "desconhecida"


def versao_gcc():
    try:
        saida = subprocess.run(["gcc", "--version"], capture_output=True, text=True)
        return saida.stdout.splitlines()[0]
    except (OSError, IndexError):
        return "desconhecida"


def grava_ambiente():
    linhas = [
        f"CPU: {nome_cpu()}",
        f"Nucleos logicos: {os.cpu_count()}",
        f"RAM: {ram_gb()}",
        f"Sistema operacional: {platform.system()} {platform.release()} ({platform.version()})",
        f"Python: {platform.python_implementation()} {platform.python_version()}",
        f"Compilador C: {versao_gcc()}",
        f"Compilacao: {COMPILAR}",
        f"Repeticoes: {REPS}; limite de viabilidade: {LIMITE_S} s",
    ]
    with open(os.path.join(PASTA, "ambiente.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))


def main():
    confere_executavel()
    os.makedirs(PASTA, exist_ok=True)
    grava_ambiente()

    ns = tamanhos_no_arquivo()
    viabilidade = []
    inicio_geral = time.time()

    with open(os.path.join(PASTA, "medicoes.csv"), "w", newline="", encoding="utf-8") as f:
        saida = csv.writer(f)
        saida.writerow(COLUNAS)

        for linguagem in LINGUAGENS:
            for algoritmo in ALGORITMOS:
                for tipo in TIPOS:
                    maior_viavel = 0
                    primeiro_inviavel = ""

                    for n in ns:
                        linhas = executa(linguagem, algoritmo, ARQUIVO, 1, tipo, n, LIMITE_S)
                        if linhas is None:
                            primeiro_inviavel = n
                            print(f"{linguagem:6} {algoritmo:12} {tipo:6} n={n:2}  passou de {LIMITE_S} s: serie encerrada")
                            break

                        if tipo != "medio":
                            linhas = executa(linguagem, algoritmo, ARQUIVO, REPS, tipo, n)

                        saida.writerows(linhas)
                        f.flush()
                        maior_viavel = n
                        media_ms = sum(float(l[7]) for l in linhas) / len(linhas) / 1e6
                        print(f"{linguagem:6} {algoritmo:12} {tipo:6} n={n:2}  {len(linhas):2} medicoes, media {media_ms:.4f} ms")

                    viabilidade.append([linguagem, algoritmo, tipo, maior_viavel, primeiro_inviavel])

    with open(os.path.join(PASTA, "viabilidade.csv"), "w", newline="", encoding="utf-8") as f:
        saida = csv.writer(f)
        saida.writerow(["linguagem", "algoritmo", "tipo", "maior_n_viavel", "primeiro_n_inviavel"])
        saida.writerows(viabilidade)

    print(f"\nPronto em {(time.time() - inicio_geral) / 60:.1f} min. Resultados em {PASTA}")


if __name__ == "__main__":
    main()
