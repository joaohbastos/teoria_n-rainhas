#include "nrainhas.h"

static int proxima_permutacao(int *a, int n)
{
    int i = n - 2;
    MEM_PILHA();
    while (i >= 0 && a[i] >= a[i + 1])
        i--;
    if (i < 0)
        return 0;

    int j = n - 1;
    while (a[j] <= a[i])
        j--;
    int tmp = a[i];
    a[i] = a[j];
    a[j] = tmp;

    int esq = i + 1, dir = n - 1;
    while (esq < dir) {
        tmp = a[esq];
        a[esq] = a[dir];
        a[dir] = tmp;
        esq++;
        dir--;
    }
    return 1;
}

static int valida(const int *p, int n)
{
    int d1[2 * MAXN];        
    int d2[2 * MAXN];        
    int ok = 1;

    MEM_PILHA();
    for (int d = 0; d < 2 * n - 1; d++)   
        d1[d] = d2[d] = 0;

    for (int i = 0; i < n; i++) {
        int a = i + p[i];
        int b = i - p[i] + n - 1;
        if (d1[a] || d2[b])
            ok = 0;
        d1[a] = 1;
        d2[b] = 1;
    }
    return ok;
}

void forca_bruta(int n, const int *pi, int modo, Resultado *r)
{
    int idx[MAXN];   
    int p[MAXN];

    MEM_INICIO();
    /* tudo na pilha: idx e p aqui, d1 e d2 em valida */
    MEM_VETORES(0, sizeof idx + sizeof p + 2 * sizeof(int[2 * MAXN]));
    for (int i = 0; i < n; i++)
        idx[i] = i;

    r->achou = 0;
    r->total = 0;
    r->contador = 0;

    do {
        for (int i = 0; i < n; i++)
            p[i] = pi[idx[i]];
        r->contador++;

        if (valida(p, n)) {
            if (modo == MODO_PRIMEIRA) {
                r->achou = 1;
                for (int i = 0; i < n; i++)
                    r->p[i] = p[i];
                return;
            }
            r->total++;
        }
    } while (proxima_permutacao(idx, n));
}
