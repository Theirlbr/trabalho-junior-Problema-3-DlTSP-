@echo off
chcp 65001 >nul
cd /d "D:\trabalho junior matematica"

:MENU
cls
echo ============================================
echo   PROBLEMA 3 - DlTSP no GUROBI
echo ============================================
echo.
echo   1 - RESUMO VISUAL (instantaneo: modelo + 2 solucoes + abre grafico)
echo   2 - Demo com LOG do solver na inst_9 (branch-and-bound ao vivo)
echo   3 - Resumo visual de outra instancia (voce digita o nome)
echo   4 - Rodar as 8 instancias e mostrar tabela resumo
echo   5 - Abrir o grafico rotas_dltsp.png
echo   6 - Abrir esta pasta no Explorer
echo   0 - Sair
echo.
set /p opcao=Escolha uma opcao:

if "%opcao%"=="1" goto RESUMO
if "%opcao%"=="2" goto LOG
if "%opcao%"=="3" goto RESUMO_OUTRA
if "%opcao%"=="4" goto TODAS
if "%opcao%"=="5" goto GRAFICO
if "%opcao%"=="6" goto PASTA
if "%opcao%"=="0" exit
goto MENU

:RESUMO
cls
echo.
python resumo_visual.py "Problema 3 (DlTSP)\inst_9.txt"
echo.
pause
goto MENU

:LOG
cls
echo.
echo >>> Log completo do Gurobi (pode rolar a tela) ...
python demo_gurobi.py "Problema 3 (DlTSP)\inst_9.txt"
echo.
pause
goto MENU

:RESUMO_OUTRA
cls
echo.
set /p inst=Nome do arquivo (ex: inst_24.txt):
python resumo_visual.py "Problema 3 (DlTSP)\%inst%"
echo.
pause
goto MENU

:TODAS
cls
echo.
echo >>> Rodando as 8 instancias ...
for %%F in ("Problema 3 (DlTSP)\inst_9.txt" "Problema 3 (DlTSP)\inst_11.txt" "Problema 3 (DlTSP)\inst_14.txt" "Problema 3 (DlTSP)\inst_16.txt" "Problema 3 (DlTSP)\inst_19.txt" "Problema 3 (DlTSP)\inst_21.txt" "Problema 3 (DlTSP)\inst_24.txt" "Problema 3 (DlTSP)\inst_29.txt") do (
    echo.
    echo ===== %%~nxF =====
    python resumo_visual.py "%%~fF"
)
echo.
pause
goto MENU

:GRAFICO
start "" rotas_dltsp.png
echo Grafico aberto em outra janela.
timeout /t 2 >nul
goto MENU

:PASTA
start "" "D:\trabalho junior matematica"
echo Pasta aberta em outra janela.
timeout /t 2 >nul
goto MENU
