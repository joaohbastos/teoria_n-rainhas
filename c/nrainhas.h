#ifndef NRAINHAS_H
#define NRAINHAS_H

#define MAXN 32           

#define MODO_PRIMEIRA 0    
#define MODO_TODAS    1   

typedef struct {
    int achou;           
    int p[MAXN];        
    long long total;      
    long long contador;   
} Resultado;

void forca_bruta(int n, const int *pi, int modo, Resultado *r);

void backtracking(int n, const int *pi, int modo, Resultado *r);

#endif
