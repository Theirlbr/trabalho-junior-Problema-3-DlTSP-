# -*- coding: utf-8 -*-
"""
PROBLEMA 3 - DlTSP (TSP com prazos limites e multa por atraso)
==============================================================
Um veículo parte do depósito (ponto 0), visita n localidades e retorna.
Cada localidade i tem um prazo limite d_i. Atrasos são permitidos, mas
pagam multa proporcional ao tempo de atraso. O tempo de percurso entre
locais é a distância euclidiana.

Este código resolve as duas formulações do exercício:

  a) minimiza o ATRASO TOTAL  (soma dos atrasos)
  b) minimiza o ATRASO MÁXIMO (minimax)

Uso:
    python solucao_dltsp.py "Problema 3 (DlTSP)/inst_9.txt"

Requisitos:
    pip install pulp
"""

import math
import sys
import pulp


# ----------------------------------------------------------------------------
# Leitura da instância no formato dos arquivos inst_*.txt
#   linha 1      : n (número de localidades)
#   linha 2      : x y do depósito (índice 0)
#   linhas 3..n+2: x y d  de cada localidade (coordenadas + prazo limite)
# ----------------------------------------------------------------------------
def ler_instancia(caminho):
    """Formato (ver 'Resumo das instancias.pdf'):
    1a linha = total de vertices (ponto de partida + localidades);
    2a linha = x y do ponto de partida;
    demais linhas = x y tempo_de_servico prazo_limite(deadline) de cada localidade."""
    with open(caminho, encoding="utf-8") as f:
        linhas = [ln.split() for ln in f if ln.strip()]
    nv = int(linhas[0][0])                                  # total de vertices
    n = nv - 1                                              # numero de localidades
    pontos = [(float(linhas[1][0]), float(linhas[1][1]))]   # depósito = 0
    servicos = [0.0]                                        # depósito não tem serviço
    prazos = [0.0]                                          # depósito não tem prazo
    for i in range(1, nv):                                  # localidades 1..n
        x, y, s, d = (float(v) for v in linhas[1 + i][:4])
        pontos.append((x, y))
        servicos.append(s)
        prazos.append(d)
    return n, pontos, servicos, prazos


def distancia_euclidiana(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ----------------------------------------------------------------------------
# Modelo de otimização (comum às duas objetivos)
#
#   x[i,j] ∈ {0,1} : 1 se o veículo vai de i para j
#   t[i]   ≥ 0     : instante em que o atendimento COMEÇA na localidade i
#   L[i]   ≥ 0     : atraso na localidade i  (L[i] = max(0, t[i] - d[i]))
#
#   (a) min  Σ L[i]
#   (b) min  Z   com  Z ≥ t[i] - d[i]  para todo i   (minimax)
# ----------------------------------------------------------------------------
def resolver(caminho, objetivo="total", verbose=True):
    n, pontos, servicos, prazos = ler_instancia(caminho)
    V = range(n + 1)                                   # vértices 0..n
    C = {(i, j): distancia_euclidiana(pontos[i], pontos[j])
         for i in V for j in V if i != j}              # tempo de percurso c_ij
    M = 10 ** 6                                        # constante "grande M"

    nome = f"DlTSP_{objetivo}_{caminho}"
    prob = pulp.LpProblem(nome, pulp.LpMinimize)

    # --- variáveis de decisão ---
    x = pulp.LpVariable.dicts("x", (V, V), cat="Binary")
    t = pulp.LpVariable.dicts("t", V, lowBound=0)
    L = pulp.LpVariable.dicts("L", range(1, n + 1), lowBound=0)

    # --- função objetivo ---
    if objetivo == "total":                            # (a) atraso total
        prob += pulp.lpSum(L[i] for i in range(1, n + 1)), "atraso_total"
    else:                                              # (b) atraso máximo
        Z = pulp.LpVariable("Z", lowBound=0)
        prob += Z, "atraso_maximo"
        for i in range(1, n + 1):
            prob += Z >= t[i] - prazos[i], f"minimax_{i}"

    # --- (1) fluxo: exatamente um arco sai e um entra em cada vértice ---
    for i in V:
        prob += pulp.lpSum(x[i][j] for j in V if j != i) == 1, f"sai_{i}"
        prob += pulp.lpSum(x[j][i] for j in V if j != i) == 1, f"entra_{i}"

    # --- (2) propagação do tempo (inclui tempo de serviço s[i] em cada parada) ---
    # Obs.: j != 0 porque o depósito (0) aparece no início E no fim da rota,
    # mas t[0] é uma única variável (tempo de partida).
    for i in V:
        for j in V:
            if i != j and j != 0:
                prob += (t[j] >= t[i] + servicos[i] + C[(i, j)] - M * (1 - x[i][j]),
                         f"tempo_{i}_{j}")

    # --- (3) definição do atraso L[i] = max(0, t[i] - d[i]) ---
    if objetivo == "total":
        for i in range(1, n + 1):
            prob += L[i] >= t[i] - prazos[i], f"atraso_{i}"

    # --- (4) eliminación de sub-rotas (formulação MTZ) ---
    u = pulp.LpVariable.dicts("u", range(1, n + 1), lowBound=2, upBound=n + 1)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                prob += u[i] - u[j] + (n + 1) * x[i][j] <= n, f"mtz_{i}_{j}"

    # --- resolve ---
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    status = pulp.LpStatus[prob.status]

    # --- extrai a rota a partir de x ---
    rota = [0]
    atual = 0
    while True:
        prox = next(j for j in V if j != atual and pulp.value(x[atual][j]) > 0.5)
        if prox == 0:
            break
        rota.append(prox)
        atual = prox
    rota.append(0)

    tempos = {i: pulp.value(t[i]) for i in V}
    atrasos = {i: max(0.0, tempos[i] - prazos[i]) for i in range(1, n + 1)}
    distancia_total = sum(C[(rota[k], rota[k + 1])] for k in range(len(rota) - 1))

    if verbose:
        print(f"\n=== Instância: {caminho} | objetivo: {objetivo} ===")
        print(f"Status: {status}")
        print(f"Rota: {' -> '.join(map(str, rota))}")
        print(f"Distância/tempo total do percurso: {distancia_total:.2f}")
        print("Detalhe por localidade (chegada, prazo, atraso):")
        for i in range(1, n + 1):
            print(f"  local {i:2d}: t = {tempos[i]:8.2f} | prazo = {prazos[i]:6.1f}"
                  f" | atraso = {atrasos[i]:8.2f}")
        if objetivo == "total":
            print(f">>> ATRASO TOTAL = {sum(atrasos.values()):.2f}")
        else:
            print(f">>> ATRASO MÁXIMO = {max(atrasos.values()):.2f}")

    return {
        "status": status, "rota": rota, "tempos": tempos,
        "atrasos": atrasos, "distancia": distancia_total,
        "valor": pulp.value(prob.objective),
    }


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "Problema 3 (DlTSP)/inst_9.txt"
    print("################ (a) MINIMIZAR ATRASO TOTAL ################")
    resolver(caminho, objetivo="total")
    print("\n################ (b) MINIMIZAR ATRASO MÁXIMO ################")
    resolver(caminho, objetivo="maximo")
