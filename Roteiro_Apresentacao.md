# Problema 3 — DlTSP: Caixeiro Viajante com Prazos e Multa por Atraso

## 1. Enunciado resumido

Um veículo parte de um ponto inicial (depósito), deve visitar **n localidades** e
retornar ao ponto de partida. Cada localidade possui um **prazo limite** para
receber a visita. Atrasos são permitidos, porém geram **multa proporcional ao
tempo de atraso**. O tempo de percurso entre localidades é a **distância
euclidiana** entre elas.

**Perguntas:**
- **a)** rota que minimiza o **atraso total** nas visitas;
- **b)** rota que minimiza o **atraso máximo**.

## 2. Formato dos dados (arquivos `inst_*.txt`)

```
9            <- total de vértices (ponto de partida + localidades)
27  45       <- coordenadas (x, y) do ponto de partida (depósito = 0)
 5  96   9 430  <- localidade 1: x=5, y=96, tempo de serviço s=9, prazo d=430
 4  87   7  17  <- localidade 2: x=4, y=87, s=7, d=17
 ...
```

## 3. Modelo matemático

### Conjuntos, parâmetros e variáveis

| Símbolo | Significado |
|---|---|
| V = {0, 1, ..., n} | vértices; 0 é o depósito |
| cᵢⱼ = √((xᵢ−xⱼ)² + (yᵢ−yⱼ)²) | tempo de percurso entre i e j |
| sᵢ | tempo de serviço na localidade i |
| dᵢ | prazo limite da localidade i |
| xᵢⱼ ∈ {0,1} | 1 se o veículo vai de i para j |
| tᵢ ≥ 0 | instante em que o atendimento inicia em i |
| Lᵢ ≥ 0 | atraso em i, com Lᵢ = max(0, tᵢ − dᵢ) |

### Restrições comuns

1. **Fluxo** (entra e sai um arco em cada vértice):
   Σⱼ xᵢⱼ = 1  e  Σᵢ xᵢⱼ = 1  para todo vértice.
2. **Propagação do tempo** (inclui o tempo de serviço sᵢ; o arco de retorno
   ao depósito não restringe t₀, pois o depósito aparece no início e no fim):
   tⱼ ≥ tᵢ + sᵢ + cᵢⱼ − M·(1 − xᵢⱼ),  com M grande, para j ≠ 0.
3. **Definição do atraso:**
   Lᵢ ≥ tᵢ − dᵢ,  Lᵢ ≥ 0.
4. **Eliminação de sub-rotas (MTZ):**
   uᵢ − uⱼ + (n+1)·xᵢⱼ ≤ n,  com 2 ≤ uᵢ ≤ n+1.

### Objetivos

- **(a) Atraso total:**  min  Σᵢ Lᵢ
- **(b) Atraso máximo (minimax):**  min  Z,  com  Z ≥ tᵢ − dᵢ  para todo i.

## 4. Implementação

- Linguagem: **Python 3**
- Duas versões do mesmo modelo:
  - `solucao_dltsp_gurobi.py` — usa **Gurobi** (`gurobipy`) + gráfico com `matplotlib`
  - `solucao_dltsp.py` — usa **PuLP/CBC** (gratuito, sem licença) como alternativa

### Como rodar (versão Gurobi — a da apresentação)

```bash
pip install gurobipy matplotlib
python solucao_dltsp_gurobi.py "Problema 3 (DlTSP)/inst_9.txt"
```

### Como rodar (versão gratuita, sem licença do Gurobi)

```bash
pip install pulp
python solucao_dltsp.py "Problema 3 (DlTSP)/inst_9.txt"
```

Ambas leem a instância, montam o modelo, resolvem **os dois casos (a) e (b)**
e imprimem: status, rota ótima, tempo de chegada em cada localidade, prazo,
atraso individual e o valor ótimo de cada objetivo. A versão Gurobi ainda
**abre uma janela com o gráfico das duas rotas ótimas** (azul = atraso total,
vermelho = atraso máximo), com o depósito, os prazos e os atrasos de cada
localidade.

### Trecho-chave do código (propagação do tempo)

```python
for i in V:
    for j in V:
        if i != j and j != 0:   # j != 0: o depósito não tem prazo nem serviço
            prob += t[j] >= t[i] + servicos[i] + C[(i, j)] - M * (1 - x[i][j])
```

> Ideia: se o arco i→j **não** é usado (xᵢⱼ = 0), a restrição vira
> tⱼ ≥ tᵢ + sᵢ + cᵢⱼ − M, que é inócua porque M é enorme. Se o arco é usado,
> vale tⱼ ≥ tᵢ + sᵢ + cᵢⱼ.

## 5. Resultados (exemplo real: inst_9.txt)

Rodando `python solucao_dltsp_gurobi.py "Problema 3 (DlTSP)/inst_9.txt"`:

- **Caso (a) — atraso total ótimo = 147.76**
  rota `0→2→7→5→3→8→1→4→6→0` (atrasos: local 2 = 30.89, local 7 = 116.87, demais 0)
- **Caso (b) — atraso máximo ótimo = 116.87**
  rota `0→2→7→8→1→4→5→3→6→0` (atraso máximo = 116.87 no local 7)

Os dois valores ótimos **diferem** e as rotas também mudam — bom ponto para
discutir na apresentação: minimizar a soma aceita vários atrasos pequenos,
enquanto o minimax impede que qualquer localidade espere demais.

## 6. Dicas para a apresentação oral

1. Comece pelo contexto: TSP clássico + prazos = problema real de entregas.
2. Mostre o desenho: depósito no centro, localidades com prazos diferentes.
3. Explique as variáveis x (rota) e t (tempo) — a "ponte" entre elas é a
   restrição de propagação de tempo.
4. Mostre a diferença entre os objetivos (a) soma vs (b) máximo.
5. Rode o código ao vivo no terminal e mostre a saída.
6. **No Gurobi**, tire o comentário de `m.Params.OutputFlag = 1` para mostrar
   o **log do solver** (progresso do branch-and-bound, bound inferior,
   gap de otimalidade) — isso impressiona e mostra que a solução é ótima.
7. Mostre a **janela do gráfico** gerada pelo matplotlib comparando as rotas
   dos dois objetivos lado a lado.

## 7. Referências / material de apoio

- Winston, *Operations Research* — modelo MTZ para TSP.
- Documentação do PuLP: https://coin-or.github.io/pulp/
- Instâncias usadas: pasta `Problema 3 (DlTSP)/` (arquivos `inst_*.txt`).
