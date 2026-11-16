#include "nrainhas.h"

static int n_;                
static const int *pi_;         
static int modo_;
static int col[MAXN];         
static int d1[2 * MAXN];     
static int d2[2 * MAXN];       
static int p[MAXN];           
static long long total;
static long long nos;

static int coloca(int i)
{
    nos++;

    if (i == n_) {           
        if (modo_ == MODO_PRIMEIRA)
            return 1;
        total++;
        return 0;
    }

    for (int j = 0; j < n_; j++) {
        int c = pi_[j];
        int a = i + c;
        int b = i - c + n_ - 1;
        if (!col[c] && !d1[a] && !d2[b]) {
            col[c] = d1[a] = d2[b] = 1;     
            p[i] = c;
            if (coloca(i + 1))
                return 1;
            col[c] = d1[a] = d2[b] = 0;    
        }
    }
    return 0;
}

void backtracking(int n, const int *pi, int modo, Resultado *r)
{
    n_ = n;
    pi_ = pi;
    modo_ = modo;
    total = 0;
    nos = 0;
    for (int c = 0; c < n; c++)
        col[c] = 0;
    for (int d = 0; d < 2 * n - 1; d++)
        d1[d] = d2[d] = 0;

    r->achou = coloca(0);
    r->total = total;
    r->contador = nos;
    if (r->achou)
        for (int i = 0; i < n; i++)
            r->p[i] = p[i];
}
