@echo off
setlocal
rem jp983src, C-F4.6: abre o cliente com o exe compilado e os stubs no modo "continuar".
rem O modo "continuar" vale com o ARQUIVO jp983_stub_continuar.txt na pasta do exe (criado aqui; o VOLTAR apaga) ou
rem com JP983_STUB=continuar no ambiente. Sem ele, o PRIMEIRO stub alcancado mostra a caixa "funcao sem corpo (stub)" e
rem fecha o jogo (o 1o ja roda antes da janela: CContentsDocJp::CreateCreatorList983, num inicializador estatico).
rem Cada stub alcancado vira uma linha em jp983_stubs.log, na pasta do jogo, com o modo em uso. Os "fatais" fecham mesmo assim.
rem Portao A6: o ijl15.dll da pasta tem de ser o ijl15_teste.dll desta entrega (o de terceiro escreve no exe compilado).
rem Ajuste a linha ABRIR se o .bat de abrir tiver outro nome (Parte F do roteiro: servidor escolhido).
set PASTA=E:\dev\pangya-test\JP983
set ABRIR=%PASTA%\ABRIR_JP983_CS.bat
set IJL=%~dp0ijl15_teste.dll
if not exist "%ABRIR%" (echo FALTA: %ABRIR% & goto fim)
if not exist "%IJL%" (echo FALTA: %IJL% & goto fim)
fc /b "%PASTA%\ijl15.dll" "%IJL%" >nul 2>nul || (
  echo PORTAO A6 FECHADO: o ijl15.dll de %PASTA% NAO e o ijl15_teste.dll desta entrega.
  echo O ijl15 de terceiro aplica patches de endereco fixo do exe ORIGINAL e estraga o teste.
  echo Rode USAR_EXE_NOSSO.bat antes. Nada foi aberto.
  goto fim
)
echo continuar> "%PASTA%\jp983_stub_continuar.txt"
set JP983_STUB=continuar
if exist "%PASTA%\jp983_stubs.log" del "%PASTA%\jp983_stubs.log"
if exist "%PASTA%\gglog.txt" del "%PASTA%\gglog.txt"
call "%ABRIR%"
:fim
endlocal
pause
