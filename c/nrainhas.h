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

/* Instrumentacao de memoria (bonus). So existe quando compilado com
 * -DMEDIR_MEMORIA (executavel nrainhas_mem, ver main_memoria.c). Na build
 * normal todas as macros abaixo viram ((void)0) e o codigo gerado nao muda.
 *
 *   MEM_INICIO()      na entrada do algoritmo: zera a profundidade e chama
 *                     MEM_PILHA().
 *   MEM_PILHA()       chama a sonda mem_sonda(), que devolve o endereco do
 *                     proprio frame. Como a sonda e uma funcao separada (nao
 *                     embutida), o frame dela fica logo abaixo do frame
 *                     inteiro de quem chamou, vetores locais inclusive.
 *                     Guarda o menor endereco visto. O main_memoria.c chama
 *                     a mesma sonda antes do algoritmo para obter a base;
 *                     pilha usada = base - menor endereco.
 *   MEM_ENTRA()       MEM_PILHA() + profundidade de recursao + 1.
 *   MEM_SAI()         profundidade de recursao - 1.
 *   MEM_VETORES(e, t) e = bytes de vetores estaticos (fora da pilha);
 *                     t = bytes de todos os vetores do algoritmo.
 */
#ifdef MEDIR_MEMORIA
#include <stddef.h>
#include <stdint.h>

extern uintptr_t mem_base;
extern uintptr_t mem_min;
extern int mem_prof;
extern int mem_prof_max;
extern size_t mem_estatico;
extern size_t mem_vetores;
uintptr_t mem_sonda(void);

#define MEM_PILHA() \
    do { \
        uintptr_t mem_end_ = mem_sonda(); \
        if (mem_end_ < mem_min) \
            mem_min = mem_end_; \
    } while (0)
#define MEM_INICIO() \
    do { \
        mem_prof = mem_prof_max = 0; \
        MEM_PILHA(); \
    } while (0)
#define MEM_ENTRA() \
    do { \
        MEM_PILHA(); \
        if (++mem_prof > mem_prof_max) \
            mem_prof_max = mem_prof; \
    } while (0)
#define MEM_SAI() (mem_prof--)
#define MEM_VETORES(e, t) (mem_estatico = (e), mem_vetores = (t))

#else
#define MEM_INICIO() ((void)0)
#define MEM_PILHA() ((void)0)
#define MEM_ENTRA() ((void)0)
#define MEM_SAI() ((void)0)
#define MEM_VETORES(e, t) ((void)0)
#endif

#endif
