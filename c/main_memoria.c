/* Medicao de memoria (bonus). Executavel separado, compilado com
 * -DMEDIR_MEMORIA; nao cronometra nada. Ver "Bonus: memoria" no README.
 *
 * uso: nrainhas_mem <forca_bruta|backtracking> <arquivo> [repeticoes] [tipo] [n]
 *
 * Cada linha da saida e uma execucao:
 *   linguagem,algoritmo,tipo,n,entrada,repeticao,profundidade_max,
 *   pilha_bytes,estatico_bytes,vetores_bytes,contador,resultado
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "nrainhas.h"

#ifndef MEDIR_MEMORIA
#error "compile com -DMEDIR_MEMORIA"
#endif

uintptr_t mem_base;
uintptr_t mem_min;
int mem_prof;
int mem_prof_max;
size_t mem_estatico;
size_t mem_vetores;

/* Sonda de pilha: devolve o endereco do proprio frame. noinline e definida
 * em outro arquivo, entao nunca e embutida no algoritmo. */
__attribute__((noinline)) uintptr_t mem_sonda(void)
{
    return (uintptr_t)__builtin_frame_address(0);
}

#define MAX_ENTRADAS 4096

typedef void (*Algoritmo)(int, const int *, int, Resultado *);

typedef struct {
    char tipo[16];
    int n;
    int pi[MAXN];
} Entrada;

static Entrada entradas[MAX_ENTRADAS];

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

        for (int rep = 0; rep < reps; rep++) {
            mem_base = mem_min = mem_sonda();   /* mesma profundidade da chamada abaixo */
            algoritmo(e->n, e->pi, modo, &r);
            unsigned long long pilha = (unsigned long long)(mem_base - mem_min);

            printf("c,%s,%s,%d,%d,%d,%d,%llu,%llu,%llu,%lld,", nome, e->tipo, e->n, k, rep,
                   mem_prof_max, pilha, (unsigned long long)mem_estatico,
                   (unsigned long long)mem_vetores, r.contador);
            imprime_resultado(&r, e->n, modo);
            printf("\n");
        }
        fflush(stdout);
    }
    return 0;
}
