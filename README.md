# Problema 3 — DlTSP (Caixeiro Viajante com Prazos e Multa por Atraso)

Trabalho de Otimização — veículo parte de um ponto inicial, visita `n`
localidades e retorna. Cada localidade tem **prazo limite (deadline)** e
**tempo de serviço**; atrasos são permitidos com multa proporcional.
O tempo de percurso é a distância euclidiana.

## Objetivos resolvidos

- **(a)** rota que minimiza o **atraso total**: `min Σ Lᵢ`
- **(b)** rota que minimiza o **atraso máximo**: `min Z, Z ≥ tᵢ − dᵢ ∀i`

## Arquivos

| Arquivo | Descrição |
|---|---|
| `solucao_dltsp_gurobi.py` | Solução com **Gurobi** + gráfico das rotas (`rotas_dltsp.png`) |
| `solucao_dltsp.py` | Mesma solução com **PuLP/CBC** (gratuito, sem licença) |
| `Roteiro_Apresentacao.md` | Roteiro da apresentação (modelo matemático + código) |
| `Problema 3 (DlTSP)/` | Instâncias de teste (`inst_*.txt`) e resumo do formato |

## Como rodar

```bash
pip install gurobipy matplotlib        # ou: pip install pulp  (versão gratuita)
python solucao_dltsp_gurobi.py "Problema 3 (DlTSP)/inst_9.txt"
```

## Formato das instâncias

```
9              <- total de vértices (ponto de partida + localidades)
27  45         <- x y do ponto de partida
 5  96   9 430 <- localidade: x y tempo_de_serviço prazo_limite
 ...
```

## Modelo (resumo)

- `xᵢⱼ ∈ {0,1}` — arco i→j usado
- `tᵢ ≥ 0` — instante de início do atendimento em i
- `Lᵢ ≥ 0` — atraso em i (`Lᵢ = max(0, tᵢ − dᵢ)`)

Restrições: fluxo (1 arco entra/sai de cada vértice), propagação do tempo
`tⱼ ≥ tᵢ + sᵢ + cᵢⱼ − M(1−xᵢⱼ)`, definição do atraso e eliminação de
sub-rotas (MTZ).

## Exemplo de resultado (inst_9.txt)

- (a) atraso total ótimo = **147.76** → rota `0→2→7→5→3→8→1→4→6→0`
- (b) atraso máximo ótimo = **116.87** → rota `0→2→7→8→1→4→5→3→6→0`
