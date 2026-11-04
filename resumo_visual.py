# -*- coding: utf-8 -*-
"""
RESUMO VISUAL INSTANTANEO - Problema 3 DlTSP
Imprime na tela o modelo e as duas solucoes otivmas, e abre o grafico.
Roda em segundos.
"""
import os
import subprocess
import sys

from demo_gurobi import montar_modelo, extrair_solucao


def linha(t=""):
    print("=" * 64)
    if t:
        print(t)
        print("=" * 64)


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "Problema 3 (DlTSP)/inst_9.txt"
    linha(f"  PROBLEMA 3 - DlTSP   |   instancia: {os.path.basename(caminho)}")
    print()

    for objetivo, titulo in (("total", "(a) MINIMIZAR ATRASO TOTAL"),
                             ("maximo", "(b) MINIMIZAR ATRASO MAXIMO")):
        mod, X, a, r, T, t, coords, d, s, N = montar_modelo(caminho, objetivo)
        mod.Params.OutputFlag = 0     # silencioso pra nao poluir a tela
        mod.optimize()
        rota = extrair_solucao(mod, X, a, r, T, N)

        print(f">>> {titulo}")
        print(f"    modelo no Gurobi : {mod.NumVars} variaveis, "
              f"{mod.NumConstrs} restricoes")
        print(f"    status           : {'OTIMO' if mod.Status == 2 else mod.Status}"
              f"  |  valor otimo = {mod.ObjVal:.2f}")
        print(f"    rota otima       : {' -> '.join(map(str, rota))}")
        print(f"    retorno ao dep.  : r = {r.X:.2f}")
        print("    detalhe das localidades:")
        for i in range(1, N):
            atraso_real = max(0.0, a[i].X - d[i])
            marca = "  <-- ATRASOU" if atraso_real > 1e-6 else ""
            print(f"      local {i}: chegada {a[i].X:7.2f} | prazo {d[i]:6.1f}"
                  f" | atraso {atraso_real:7.2f}{marca}")
        print()

    linha("  ABRINDO O GRAFICO DAS ROTAS ...")
    caminho_png = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "rotas_dltsp.png")
    if os.path.exists(caminho_png):
        if sys.platform.startswith("win"):
            os.startfile(caminho_png)          # abre a imagem no Windows
        else:
            subprocess.Popen(["xdg-open", caminho_png])
        print(f"  grafico aberto: {caminho_png}")
    else:
        print("  (rode solucao_dltsp_gurobi.py antes para gerar rotas_dltsp.png)")
    linha("  FIM DO RESUMO")


if __name__ == "__main__":
    main()
