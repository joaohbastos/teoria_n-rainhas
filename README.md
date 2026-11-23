# N-Rainhas: força bruta × backtracking

Projeto de Teoria da Computação (CESAR School, 2026.2, Prof. Daniel Bezerra).

Dois algoritmos para o problema das N-rainhas, cada um implementado em Python e em C, com análise de complexidade teórica e experimental.

| | Algoritmo | Complexidade (busca exaustiva) |
| --- | --- | --- |
| A | Força bruta sobre permutações | Θ(n! · n) |
| B | Backtracking com poda | Θ(n · N(n)), entre Ω(n · Q(n)) e O(n! · n) |

N(n) é o número de nós da árvore de busca e Q(n) é o número de soluções.

## Estrutura

```
c/                    implementações em C
  nrainhas.h            declarações compartilhadas
  forca_bruta.c         algoritmo A
  backtracking.c        algoritmo B
  main.c                lê as entradas, cronometra e imprime CSV
python/               implementações em Python
  forca_bruta.py        algoritmo A
  backtracking.py       algoritmo B
  main.py               lê as entradas, cronometra e imprime CSV
entradas/entradas.txt entradas usadas por todas as implementações
gerar_entradas.py     gera o arquivo de entradas (semente fixa)
testes.py             testes de corretude das quatro implementações
medir.py              medição de tempo
graficos.py           gráficos e tabela-resumo
comum.py              funções usadas por testes.py e medir.py
resultados/           saídas de medir.py e graficos.py
```

Os arquivos do bônus de memória (`c/main_memoria.c`, `medir_memoria.py`, `testes_memoria.py`, `graficos_memoria.py`, `entradas/entradas_memoria.txt`) estão descritos em [Bônus: memória](#bônus-memória).

## Requisitos

- Python 3.10 ou mais novo
- gcc
- matplotlib, só para os gráficos: `pip install matplotlib`

## Como reproduzir

Todos os comandos são executados na raiz do repositório.

```
python gerar_entradas.py
gcc -O2 -std=c11 -Wall -Wextra -o nrainhas c/main.c c/forca_bruta.c c/backtracking.c
python testes.py
python medir.py
python graficos.py
```

1. `gerar_entradas.py` recria `entradas/entradas.txt`. A semente é fixa (42), então o arquivo sai idêntico ao que está no repositório.
2. O `gcc` gera o executável `nrainhas` (`nrainhas.exe` no Windows).
3. `testes.py` confere a corretude e termina com `OK` se tudo passar.
4. `medir.py` grava `medicoes.csv`, `viabilidade.csv` e `ambiente.txt` em `resultados/`. A medição completa leva cerca de 30 a 60 minutos. Para um teste rápido (3 repetições, limite de 5 s): `python medir.py --rapido`.
5. `graficos.py` grava `resumo.csv` e as seis figuras em `resultados/`.

Os tempos dependem da máquina. Os contadores de passos (permutações testadas e nós visitados) e as respostas são sempre os mesmos.

## Formato das entradas

Cada linha de `entradas/entradas.txt` é uma entrada:

```
tipo n pi[0] pi[1] ... pi[n-1]
```

`pi` é uma permutação de 0..n−1 que define a ordem em que as colunas são tentadas.

| Tipo | π | Modo | Caso |
| --- | --- | --- | --- |
| `medio` | sorteada (20 por tamanho) | para na primeira solução | médio |
| `melhor` | já é uma solução | para na primeira solução | melhor |
| `pior` | ordem natural | conta todas as soluções | pior (busca exaustiva) |

O arquivo cobre n de 4 a 17.

## Rodar uma implementação diretamente

```
./nrainhas <forca_bruta|backtracking> <arquivo> [repeticoes] [tipo] [n]
python python/main.py <forca_bruta|backtracking> <arquivo> [repeticoes] [tipo] [n]
```

Exemplo: backtracking em C, 5 repetições, só o pior caso com n = 10:

```
./nrainhas backtracking entradas/entradas.txt 5 pior 10
```

Cada linha da saída é uma medição:

```
linguagem,algoritmo,tipo,n,entrada,repeticao,chamadas,tempo_ns,contador,resultado
```

- `tempo_ns`: tempo de uma chamada do algoritmo, em nanossegundos. Só a chamada é cronometrada; leitura do arquivo e impressão ficam fora.
- `chamadas`: execuções muito rápidas são repetidas até a medição durar cerca de 1 ms, e o tempo é dividido por esse número.
- `contador`: permutações testadas (força bruta) ou nós visitados (backtracking).
- `resultado`: a solução no formato `c0-c1-...`, `sem_solucao`, ou a contagem de soluções.

## Metodologia de medição

- Cada série (implementação e tipo de entrada) avança de n = 4 até o primeiro n que não termina em 60 s. Esse é o maior n viável, registrado em `viabilidade.csv`.
- Melhor e pior caso: 15 execuções da mesma entrada por tamanho.
- Caso médio: as 20 entradas sorteadas de cada tamanho, uma execução cada.
- São reportados média e desvio-padrão por tamanho (`resumo.csv`).

## Testes de corretude

`testes.py` roda as quatro implementações sobre 141 entradas (n de 1 a 9) e confere que:

1. as quatro devolvem exatamente a mesma resposta;
2. o mesmo algoritmo faz o mesmo número de passos em Python e em C;
3. toda solução é válida, por um teste independente que compara todos os pares de rainhas;
4. a contagem de soluções bate com os valores conhecidos (OEIS A000170);
5. no melhor caso a solução devolvida é a própria π;
6. n = 2 e n = 3 não têm solução.

## Bônus: memória

Mede o uso de memória das quatro implementações e compara com a complexidade de espaço teórica, Θ(n) nos dois algoritmos. Não mede tempo, não usa os arquivos de `medir.py` e não muda nenhum arquivo que já existia em `resultados/` (lê `resumo.csv`, só para comparar com o tempo no gráfico).

```
gcc -O2 -std=c11 -Wall -Wextra -DMEDIR_MEMORIA -o nrainhas_mem c/main_memoria.c c/forca_bruta.c c/backtracking.c
python testes_memoria.py
python medir_memoria.py
python graficos_memoria.py
```

1. O `gcc` gera um executável separado, `nrainhas_mem` (`nrainhas_mem.exe` no Windows). A instrumentação fica em macros de `c/nrainhas.h` que só existem com `-DMEDIR_MEMORIA`; na build normal elas viram `((void)0)` e o código de máquina de `nrainhas` é o mesmo de antes.
2. `testes_memoria.py` confere que a profundidade máxima de recursão é n + 1 no backtracking e 0 na força bruta, igual em Python e em C, que `nrainhas_mem` dá as mesmas respostas e contadores que o Python e que a pilha do backtracking em C cresce o mesmo número de bytes por nível. Termina com `OK`.
3. `medir_memoria.py` grava `entradas/entradas_memoria.txt`, `resultados/memoria.csv`, `resultados/memoria_resumo.csv` e `resultados/ambiente_memoria.txt`. Leva menos de 1 minuto. Se `nrainhas_mem` não existir ou não puder ser executado, mede só o Python e avisa.
4. `graficos_memoria.py` grava `resultados/fig7_memoria.png`. Funciona com ou sem as linhas de C.

### O que é medido

- **Python**: pico de memória alocada durante a chamada, com `tracemalloc` (pico menos a memória já alocada antes da chamada), e profundidade máxima de chamadas aninhadas a `coloca`, com `sys.setprofile`. As duas coisas rodam em chamadas separadas, e cada par (algoritmo, entrada) roda num processo Python novo. `python/forca_bruta.py` e `python/backtracking.py` não foram alterados.
- **C**: pilha usada, profundidade máxima de recursão e bytes dos vetores. Uma função-sonda (`mem_sonda`, nunca embutida) devolve o endereço do próprio frame; ela é chamada pelo `main` logo antes do algoritmo (base) e pelas funções mais profundas (`coloca`, `valida`, `proxima_permutacao`). Pilha usada = base − menor endereço visto.

### Entradas

A memória não depende de π, então são usadas entradas de melhor caso (π já é solução), que rodam em microssegundos: n de 4 a 32 (32 é o `MAXN` do C), com π dado pela construção explícita clássica (Hoffman, Loessi e Moore, 1969), conferida por um teste independente de pares de rainhas. Para mostrar a independência de π, n de 4 a 9 também é medido com as 3 primeiras entradas `medio` e com a entrada `pior` de `entradas.txt`. Cada entrada é executada 15 vezes.

### Formato das saídas

`memoria.csv`, uma linha por execução:

```
linguagem,algoritmo,tipo,n,entrada,repeticao,profundidade_max,memoria_bytes,pilha_bytes,estatico_bytes,vetores_bytes,contador,resultado
```

- `profundidade_max`: maior número de chamadas a `coloca` ativas ao mesmo tempo.
- `memoria_bytes`: Python, pico do `tracemalloc`; C, `pilha_bytes + estatico_bytes`.
- `pilha_bytes` (só C): pilha usada pelo algoritmo, incluindo os vetores locais.
- `estatico_bytes` (só C): vetores estáticos, fora da pilha (backtracking: `col`, `d1`, `d2`, `p`; força bruta: nenhum).
- `vetores_bytes` (só C): bytes reservados para todos os vetores do algoritmo. É constante porque o tamanho deles é fixado por `MAXN`.
- `contador` e `resultado`: iguais aos de `medicoes.csv`.
- `entrada`: índice da linha em `entradas/entradas_memoria.txt`.

`memoria_resumo.csv` tem uma linha por linguagem, algoritmo, tipo e n, com média e desvio-padrão de `memoria_bytes`, a profundidade máxima, a pilha média (C) e os bytes dos vetores (C). `ambiente_memoria.txt` registra CPU, RAM, sistema, versão do Python, saída de `gcc --version` e `gcc -dumpmachine` e o comando de compilação.
