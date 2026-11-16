#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "nrainhas.h"

#ifdef _WIN32
#include <windows.h>
#endif

#define MAX_ENTRADAS 4096
#define ALVO_NS 1000000LL    
#define MAX_CHAMADAS 100000

typedef void (*Algoritmo)(int, const int *, int, Resultado *);

typedef struct {
    char tipo[16];
    int n;
    int pi[MAXN];
} Entrada;

static Entrada entradas[MAX_ENTRADAS];

static long long agora_ns(void)
{
#ifdef _WIN32
    LARGE_INTEGER freq, cont;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&cont);
    long long seg = cont.QuadPart / freq.QuadPart;
    long long resto = cont.QuadPart % freq.QuadPart;
    return seg * 1000000000LL + resto * 1000000000LL / freq.QuadPart;
#else
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (long long)t.tv_sec * 1000000000LL + t.tv_nsec;
#endif
}

static int ler_entradas(const char *caminho)
{
    FILE *f = fopen(caminho, "r");
    if (!f)
        return -1;

    int qtd = 0;
    while (qtd < MAX_ENTRADAS) {
        Entrada *e = &entradas[qtd];
        if (fscanf(f, "%15s %d", e->tipo, &e->n) != 2)
            break;
        if (e->n < 1 || e->n > MAXN) {
            fclose(f);
            return -1;
        }
        for (int i = 0; i < e->n; i++) {
            if (fscanf(f, "%d", &e->pi[i]) != 1) {
                fclose(f);
                return -1;
            }
        }
        qtd++;
    }
    fclose(f);
    return qtd;
}

static void imprime_resultado(const Resultado *r, int n, int modo)
{
    if (modo == MODO_TODAS) {
        printf("%lld", r->total);
    } else if (!r->achou) {
        printf("sem_solucao");
    } else {
        for (int i = 0; i < n; i++)
            printf(i ? "-%d" : "%d", r->p[i]);
    }
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "uso: %s <forca_bruta|backtracking> <arquivo> [repeticoes] [tipo] [n]\n", argv[0]);
        return 1;
    }

    const char *nome = argv[1];
    Algoritmo algoritmo;
    if (strcmp(nome, "forca_bruta") == 0)
        algoritmo = forca_bruta;
    else if (strcmp(nome, "backtracking") == 0)
        algoritmo = backtracking;
    else {
        fprintf(stderr, "algoritmo desconhecido: %s\n", nome);
        return 1;
    }

    int reps = argc > 3 ? atoi(argv[3]) : 1;
    const char *filtro_tipo = argc > 4 ? argv[4] : "todos";
    int filtro_n = argc > 5 ? atoi(argv[5]) : 0;

    int qtd = ler_entradas(argv[2]);
    if (qtd < 0) {
        fprintf(stderr, "erro ao ler %s\n", argv[2]);
        return 1;
    }

    for (int k = 0; k < qtd; k++) {
        Entrada *e = &entradas[k];
        if (strcmp(filtro_tipo, "todos") != 0 && strcmp(filtro_tipo, e->tipo) != 0)
            continue;
        if (filtro_n != 0 && filtro_n != e->n)
            continue;

        int modo = strcmp(e->tipo, "pior") == 0 ? MODO_TODAS : MODO_PRIMEIRA;
        Resultado r;

        long long chamadas = 1;
        long long inicio, t;
        for (;;) {
            inicio = agora_ns();
            for (long long c = 0; c < chamadas; c++)
                algoritmo(e->n, e->pi, modo, &r);
            t = agora_ns() - inicio;

            if (t >= ALVO_NS || chamadas >= MAX_CHAMADAS)
                break;
            chamadas = t <= 0 ? chamadas * 10 : chamadas * ALVO_NS / t + 1;
            if (chamadas > MAX_CHAMADAS)
                chamadas = MAX_CHAMADAS;
        }

        for (int rep = 0; rep < reps; rep++) {
            if (!(rep == 0 && chamadas == 1)) {
                inicio = agora_ns();
                for (long long c = 0; c < chamadas; c++)
                    algoritmo(e->n, e->pi, modo, &r);
                t = agora_ns() - inicio;
            }

            double tempo = (double)t / (double)chamadas;
            printf("c,%s,%s,%d,%d,%d,%lld,%.1f,%lld,", nome, e->tipo, e->n, k, rep, chamadas, tempo, r.contador);
            imprime_resultado(&r, e->n, modo);
            printf("\n");
        }
        fflush(stdout);
    }
    return 0;
}