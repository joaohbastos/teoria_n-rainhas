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
