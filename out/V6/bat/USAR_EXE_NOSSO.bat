@echo off
setlocal
rem jp983src, tarefa V6 (C-F4.6): poe o exe COMPILADO e o ijl15 DE TESTE no lugar dos do cliente JP 983 de teste.
rem Guarda os originais em <exe>.orig e ijl15.dll.orig (so na primeira vez; nunca sobrescreve um .orig).
rem O ijl15.dll da pasta do cliente e um rugburn MODIFICADO DE TERCEIRO, com patches em enderecos fixos do exe ORIGINAL:
rem com o exe compilado ele escreve lixo no codigo/dados. O ijl15_teste.dll e o rugburn PUBLICO so com ganchos de API.
rem Ajuste as linhas abaixo se a pasta ou os nomes forem outros.
set PASTA=E:\dev\pangya-test\JP983
set EXE=ProjectG.exe
set NOSSO=%~dp0ProjectG_nosso.exe
set IJL=%~dp0ijl15_teste.dll

if not exist "%PASTA%\%EXE%" (echo FALTA: %PASTA%\%EXE% & goto fim)
if not exist "%NOSSO%" (echo FALTA: %NOSSO% ^(copie o exe compilado para ca com esse nome^) & goto fim)
if not exist "%IJL%" (echo FALTA: %IJL% ^(vem na mesma pasta da entrega^) & goto fim)
tasklist /fi "imagename eq %EXE%" 2>nul | find /i "%EXE%" >nul && (echo O jogo esta aberto. Feche antes de trocar. & goto fim)

if not exist "%PASTA%\%EXE%.orig" (
  copy /b "%PASTA%\%EXE%" "%PASTA%\%EXE%.orig" >nul || (echo ERRO ao guardar o exe original. Nada foi trocado. & goto fim)
  echo Original guardado em %PASTA%\%EXE%.orig
) else (
  echo Ja existe %EXE%.orig ^(original guardado antes^); mantido.
)
if exist "%PASTA%\ijl15.dll" if not exist "%PASTA%\ijl15.dll.orig" (
  copy /b "%PASTA%\ijl15.dll" "%PASTA%\ijl15.dll.orig" >nul || (echo ERRO ao guardar o ijl15.dll original. Nada foi trocado. & goto fim)
  echo ijl15.dll original guardado em %PASTA%\ijl15.dll.orig
)
copy /b /y "%NOSSO%" "%PASTA%\%EXE%" >nul || (echo ERRO ao copiar o exe compilado. & goto fim)
copy /b /y "%IJL%" "%PASTA%\ijl15.dll" >nul || (echo ERRO ao copiar o ijl15_teste.dll. Rode VOLTAR_EXE_ORIGINAL.bat. & goto fim)

echo.
echo md5 do exe em uso ^(deve ser o do exe compilado, MD5.txt^):
certutil -hashfile "%PASTA%\%EXE%" MD5 | find /v "CertUtil"
echo md5 do original guardado ^(dump do 983 = 8c76194bf825391f63fc951d3d4b09da^):
certutil -hashfile "%PASTA%\%EXE%.orig" MD5 | find /v "CertUtil"
fc /b "%PASTA%\ijl15.dll" "%IJL%" >nul && (echo ijl15.dll em uso = ijl15_teste.dll ^(portao A6 ok^)) || (echo ERRO: ijl15.dll em uso NAO e o de teste.)

if exist "%PASTA%\rugburn.json" (
  findstr /i "PatchAddress" "%PASTA%\rugburn.json" >nul && (
    echo.
    echo Aviso: o rugburn.json tem "PatchAddress" ^(enderecos do exe ORIGINAL^). O ijl15_teste.dll IGNORA essa parte
    echo ^(anota no gglog.txt^); nao precisa mexer no json.
  )
)
echo.
echo Pronto. Abrir: ABRIR_COM_STUBS.bat. Para voltar: VOLTAR_EXE_ORIGINAL.bat
:fim
endlocal
pause
