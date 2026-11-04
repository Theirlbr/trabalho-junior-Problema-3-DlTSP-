# -*- coding: utf-8 -*-
"""
PROBLEMA 3 - DlTSP com Gurobi + visualizacao grafica
====================================================
Resolve com gurobipy (mostrando o log do solver) e plota a rota otima:

  a) minimiza o ATRASO TOTAL
  b) minimiza o ATRASO MAXIMO

Uso:
    pip install gurobipy matplotlib
    python solucao_dltsp_gurobi.py "Problema 3 (DlTSP)/inst_9.txt"

Observacao: se nao tiver licenca do Gurobi, o programa avisa e sugere
rodar a versao PuLP (solucao_dltsp.py), que usa o solver gratuito CBC.
"""

import math
import sys

import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum


# ----------------------------------------------------------------------------
# Leitura da instancia (mesmo formato dos arquivos inst_*.txt)
# ----------------------------------------------------------------------------
def ler_instancia(caminho):
    """Formato (ver 'Resumo das instancias.pdf'):
    1a linha = total de vertices (ponto de partida + localidades);
    2a linha = x y do ponto de partida;
    demais linhas = x y tempo_de_servico prazo_limite(deadline) de cada localidade."""
    with open(caminho, encoding="utf-8") as f:
        linhas = [ln.split() for ln in f if ln.strip()]
    nv = int(linhas[0][0])                                 # total de vertices
    n = nv - 1                                             # numero de localidades
    pontos = [(float(linhas[1][0]), float(linhas[1][1]))]   # deposito = 0
    servicos = [0.0]                                       # deposito nao tem servico
    prazos = [0.0]                                         # deposito nao tem prazo
    for i in range(1, nv):                                 # localidades 1..n
        x, y, s, d = (float(v) for v in linhas[1 + i][:4])
        pontos.append((x, y))
        servicos.append(s)
        prazos.append(d)
    return n, pontos, servicos, prazos


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ----------------------------------------------------------------------------
# Modelo em Gurobi. O mesmo modelo serve para os dois objetivos:
#   objetivo="total"  -> min soma dos atrasos
#   objetivo="maximo" -> min Z, Z >= atraso de cada localidade
# ----------------------------------------------------------------------------
def resolver_gurobi(caminho, objetivo="total"):
    n, pontos, servicos, prazos = ler_instancia(caminho)
    V = range(n + 1)
    c = {(i, j): dist(pontos[i], pontos[j]) for i in V for j in V if i != j}
    M = 1e6

    m = Model(f"DlTSP_{objetivo}")
    # m.Params.OutputFlag = 1  # descomente para ver o log completo do Gurobi

    # --- variaveis ---
    x = m.addVars(V, V, vtype=GRB.BINARY, name="x")
    t = m.addVars(V, lb=0, name="t")
    L = m.addVars(range(1, n + 1), lb=0, name="L")

    # --- objetivo ---
    if objetivo == "total":
        m.setObjective(quicksum(L[i] for i in range(1, n + 1)), GRB.MINIMIZE)
    else:
        Z = m.addVar(lb=0, name="Z")
        m.setObjective(Z, GRB.MINIMIZE)
        for i in range(1, n + 1):
            m.addConstr(Z >= t[i] - prazos[i], name=f"minimax_{i}")

    # --- (1) fluxo ---
    for i in V:
        m.addConstr(quicksum(x[i, j] for j in V if j != i) == 1, name=f"sai_{i}")
        m.addConstr(quicksum(x[j, i] for j in V if j != i) == 1, name=f"entra_{i}")

    # --- (2) propagacao do tempo (inclui tempo de servico s[i] em cada parada) ---
    # Obs.: j != 0 porque o deposito (0) aparece no inicio E no fim da rota,
    # mas t[0] e uma unica variavel (tempo de partida). O arco de retorno
    # nao restringe t[0].
    for i in V:
        for j in V:
            if i != j and j != 0:
                m.addConstr(t[j] >= t[i] + servicos[i] + c[(i, j)] - M * (1 - x[i, j]),
                            name=f"tempo_{i}_{j}")

    # --- (3) atraso ---
    if objetivo == "total":
        for i in range(1, n + 1):
            m.addConstr(L[i] >= t[i] - prazos[i], name=f"atraso_{i}")

    # --- (4) eliminacao de sub-rotas (MTZ) ---
    u = m.addVars(range(1, n + 1), lb=2, ub=n + 1, name="u")
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j:
                m.addConstr(u[i] - u[j] + (n + 1) * x[i, j] <= n,
                            name=f"mtz_{i}_{j}")

    m.optimize()

    # --- extrai resultado ---
    rota = [0]
    atual = 0
    while True:
        prox = next(j for j in V if j != atual and x[atual, j].X > 0.5)
        if prox == 0:
            break
        rota.append(prox)
        atual = prox
    rota.append(0)

    tempos = {i: t[i].X for i in V}
    atrasos = {i: max(0.0, tempos[i] - prazos[i]) for i in range(1, n + 1)}
    dist_total = sum(c[(rota[k], rota[k + 1])] for k in range(len(rota) - 1))

    print(f"\n=== Gurobi | {caminho} | objetivo: {objetivo} ===")
    print(f"Status: {m.Status} (2 = otimo) | valor otimo = {m.ObjVal:.2f}")
    print(f"Rota: {' -> '.join(map(str, rota))}")
    print(f"Tempo total de percurso: {dist_total:.2f}")
    for i in range(1, n + 1):
        print(f"  local {i:2d}: chegada t={tempos[i]:8.2f} | prazo={prazos[i]:6.1f}"
              f" | atraso={atrasos[i]:8.2f}")
    if objetivo == "total":
        print(f">>> ATRASO TOTAL  = {sum(atrasos.values()):.2f}")
    else:
        print(f">>> ATRASO MÁXIMO = {max(atrasos.values()):.2f}")

    return rota, pontos, prazos, tempos, atrasos, objetivo


# ----------------------------------------------------------------------------
# Grafico da rota
# ----------------------------------------------------------------------------
def plotar(rotas, pontos, prazos, titulo_extra=""):
    cores = {"total": "tab:blue", "maximo": "tab:red"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (rota, tempos, atrasos, objetivo) in zip(
            axes, rotas):
        cor = cores[objetivo]
        # arcos da rota
        for k in range(len(rota) - 1):
            i, j = rota[k], rota[k + 1]
            ax.annotate("", xy=pontos[j], xytext=pontos[i],
                        arrowprops=dict(arrowstyle="->", color=cor, lw=1.5))
        # pontos
        xs = [p[0] for p in pontos]
        ys = [p[1] for p in pontos]
        ax.scatter(xs[1:], ys[1:], c="white", edgecolors=cor, s=120, zorder=3,
                   label="localidades")
        ax.scatter([xs[0]], [ys[0]], c="black", marker="s", s=150, zorder=4,
                   label="depósito (0)")
        # rótulos: índice, prazo e atraso
        for i in range(1, len(pontos)):
            ax.annotate(f"{i}\n(d={prazos[i]:.0f}, atraso={atrasos[i]:.1f})",
                        (xs[i], ys[i]), textcoords="offset points",
                        xytext=(8, 8), fontsize=8)
        ax.annotate("0", (xs[0], ys[0]), textcoords="offset points",
                    xytext=(8, 8), fontsize=9, fontweight="bold")
        soma = sum(atrasos.values())
        mx = max(atrasos.values())
        rotulo = ("atraso TOTAL" if objetivo == "total" else "atraso MÁXIMO")
        ax.set_title(f"Rota ({rotulo} = {soma if objetivo=='total' else mx:.2f})\n"
                     f"{' -> '.join(map(str, rota))}", fontsize=10)
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    fig.suptitle(f"DlTSP — solução ótima por objetivo {titulo_extra}", fontsize=12)
    plt.tight_layout()
    fig.savefig("rotas_dltsp.png", dpi=150)   # salva a figura como imagem
    print("Gráfico salvo em rotas_dltsp.png")
    plt.show()


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "Problema 3 (DlTSP)/inst_9.txt"
    try:
        r1 = resolver_gurobi(caminho, objetivo="total")
        r2 = resolver_gurobi(caminho, objetivo="maximo")
        plotar([(r1[0], r1[3], r1[4], "total"),
                (r2[0], r2[3], r2[4], "maximo")],
               r1[1], r1[2], titulo_extra=f"({caminho})")
    except Exception as e:
        print(f"\n[!] Nao foi possivel rodar com Gurobi: {e}")
        print("    -> Se nao tiver licenca, use a versao gratuita: "
              "python solucao_dltsp.py")
