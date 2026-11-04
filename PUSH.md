# Como subir no GitHub

## Opção A — pela página (sem token, mais fácil)

1. Acesse: https://github.com/Theirlbr/trabalho-junior-Problema-3-DlTSP-
2. Clique em **Add file → Upload files**
3. Arraste para a área de upload estes itens da pasta `D:\trabalho junior matematica`:
   - `README.md`, `Roteiro_Apresentacao.md`, `PUSH.md`
   - `solucao_dltsp.py`, `solucao_dltsp_gurobi.py`, `demo_gurobi.py`, `resumo_visual.py`
   - `abrir_gurobi.bat`, `.gitignore`
   - a pasta `Problema 3 (DlTSP)` inteira (inst_*.txt + PDF)
   - `exercisio.png`, `rotas_dltsp.png`
   - `modelo_total.lp`, `modelo_maximo.lp`
   - `resultado_inst9.txt`, `demo_gurobi_log.txt`
4. **NÃO arraste** a pasta `.git` nem nenhum arquivo `.lic` (licença do Gurobi).
5. Em "Commit changes" escreva: `Problema 3 DlTSP: modelo, solucoes, demo, resultados e grafico`
6. Clique em **Commit changes**.

## Opção B — por token (terminal)

1. Crie o token: github.com → Settings → Developer settings →
   Personal access tokens → Tokens (classic) → Generate new token → marque **repo**.
2. Rode na pasta do projeto:

```bash
cd "D:\trabalho junior matematica"
git remote add origin https://github.com/Theirlbr/trabalho-junior-Problema-3-DlTSP-.git
git branch -M main
git push -u origin main
# quando pedir Username: Theirlbr
# quando pedir Password: cole o TOKEN (não a senha da conta)
```

⚠️ Nunca commite o token nem a chave do Gurobi no repositório.
