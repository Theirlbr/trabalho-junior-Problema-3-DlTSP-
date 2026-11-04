# -*- coding: utf-8 -*-
"""
DEMO INTERATIVA DO GUROBI - Problema 3 DlTSP
=============================================
Mostra "por dentro" o que acontece no Gurobi:
  1. monta o modelo e imprime o resumo (variaveis/restricoes)
  2. exporta o modelo em formato .lp (legivel) e mostra um trecho
  3. liga o log completo do solver (OutputFlag=1) -> branch-and-bound ao vivo
  4. resolve os dois objetivos e mostra a solucao otima

Uso:
    python demo_gurobi.py "Problema 3 (DlTSP)/inst_9.txt"
"""

import math
import sys

from gurobipy import Model, GRB, quicksum


def ler_instancia(caminho):
    with open(caminho, encoding="utf-8") as f:
        linhas = [ln.split() for ln in f if ln.strip()]
    N = int(linhas[0][0])                       # total de vertices (deposito incluso)
    coords = [(float(linhas[1][0]), float(linhas[1][1]))]   # deposito = 0
    serv = [0.0]
    dead = [0.0]
    for i in range(1, N):
        x, y, s, d = (float(v) for v in linhas[1 + i][:4])
        coords.append((x, y))
        serv.append(s)
        dead.append(d)
    return N, coords, serv, dead


def montar_modelo(caminho, objetivo):
    """Monta o modelo exatamente como a formulacao geral (secoes 1-4)."""
    N, coords, s, d = ler_instancia(caminho)
    V = range(N)                    # V = {0,...,N-1}, 0 = deposito
    C = range(1, N)                 # localidades
    m = N - 1                       # |C|
    t = {(i, j): math.hypot(coords[i][0] - coords[j][0],
                            coords[i][1] - coords[j][1])
         for i in V for j in V if i != j}

    # big-M seguro (secao 2 da formulacao)
    tmax = max(t.values())
    H = sum(s[i] for i in C) + N * tmax
    M = {(i, j): H + s[i] + t[(i, j)] for i in V for j in V if i != j}

    mod = Model(f"DlTSP_{objetivo}")
    mod.Params.OutputFlag = 1      # << LOG COMPLETO DO SOLVER (branch-and-bound)

    # --- variaveis de decisao (secao 3) ---
    X = mod.addVars(V, V, vtype=GRB.BINARY, name="X")
    a = mod.addVars(V, lb=0, ub=H, name="a")          # chegada/inicio do servico
    mod.addConstr(a[0] == 0, name="a0_fixo")          # a0 = 0 (partida no instante 0)
    r = mod.addVar(lb=0, ub=H, name="r")              # retorno ao deposito
    T = mod.addVars(C, lb=0, name="T")                # atraso em cada localidade

    if objetivo == "total":
        mod.setObjective(quicksum(T[i] for i in C), GRB.MINIMIZE)
    else:
        Tmax = mod.addVar(lb=0, name="Tmax")
        mod.setObjective(Tmax, GRB.MINIMIZE)
        for i in C:
            mod.addConstr(Tmax >= T[i], name=f"Tmax_{i}")

    # --- 4.1 e 4.2: grau (uma saida e uma entrada em cada vertice) ---
    for i in V:
        mod.addConstr(quicksum(X[i, j] for j in V if j != i) == 1, name=f"sai_{i}")
        mod.addConstr(quicksum(X[j, i] for j in V if j != i) == 1, name=f"entra_{i}")

    # --- 4.3: MTZ (eliminacao de sub-rotas) ---
    u = mod.addVars(C, lb=1, ub=m, vtype=GRB.INTEGER, name="u")
    for i in C:
        for j in C:
            if i != j:
                mod.addConstr(u[i] - u[j] + m * X[i, j] <= m - 1, name=f"mtz_{i}_{j}")

    # --- 4.4: propagacao dos tempos (j so em C; a0 = 0 fixo) ---
    for i in V:
        for j in C:
            if i != j:
                mod.addConstr(a[j] >= a[i] + s[i] + t[(i, j)] - M[(i, j)] * (1 - X[i, j]),
                              name=f"chega_{i}_{j}")

    # --- 4.5: retorno ao deposito ---
    for i in C:
        mod.addConstr(r >= a[i] + s[i] + t[(i, 0)] - M[(i, 0)] * (1 - X[i, 0]),
                      name=f"retorno_{i}")

    # --- 4.7: definicao do atraso (deadline vs chegada) ---
    for i in C:
        mod.addConstr(T[i] >= a[i] - d[i], name=f"atraso_{i}")

    return mod, X, a, r, T, t, coords, d, s, N


def mostrar_modelo(mod, objetivo):
    """Imprime resumo e exporta o .lp para inspecao."""
    mod.update()
    print("\n" + "=" * 70)
    print(f"MODELO '{mod.ModelName}' dentro do Gurobi")
    print("=" * 70)
    print(f"  variaveis : {mod.NumVars}  ({mod.NumBinVars} binarias, "
          f"{mod.NumIntVars} inteiras, {mod.NumVars - mod.NumIntVars} continuas)")
    print(f"  restricoes: {mod.NumConstrs}")
    print(f"  nao-nulos : {mod.NumNZs}")
    arquivo = f"modelo_{objetivo}.lp"
    mod.write(arquivo)
    print(f"  modelo exportado em formato LP: {arquivo}")
    with open(arquivo, encoding="utf-8") as f:
        linhas = f.readlines()
    print("  --- trecho do arquivo LP (inicio) ---")
    for ln in linhas[:12]:
        print("   ", ln.rstrip())
    print("   ...")


def extrair_solucao(mod, X, a, r, T, N):
    rota = [0]
    atual = 0
    while True:
        prox = next(j for j in range(N) if j != atual and X[atual, j].X > 0.5)
        if prox == 0:
            break
        rota.append(prox)
        atual = prox
    rota.append(0)
    return rota


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "Problema 3 (DlTSP)/inst_9.txt"
    for objetivo in ("total", "maximo"):
        print("\n" + "#" * 70)
        print(f"# RESOLVENDO OBJETIVO: {objetivo.upper()}")
        print("#" * 70)
        mod, X, a, r, T, t, coords, d, s, N = montar_modelo(caminho, objetivo)
        mostrar_modelo(mod, objetivo)
        print("\n>>> chamando mod.optimize() — log do Gurobi abaixo:")
        mod.optimize()
        rota = extrair_solucao(mod, X, a, r, T, N)
        print("\n" + "=" * 70)
        print(f"SOLUCAO OTIMA ({objetivo}): valor = {mod.ObjVal:.2f}")
        print(f"  rota: {' -> '.join(map(str, rota))}")
        print(f"  retorno ao deposito r = {r.X:.2f}")
        for i in range(1, N):
            print(f"  local {i}: chegada a={a[i].X:8.2f} | servico s={s[i]:.0f} "
                  f"| prazo d={d[i]:6.1f} | atraso T={T[i].X:8.2f}")
