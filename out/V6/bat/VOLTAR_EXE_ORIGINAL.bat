@echo off
setlocal
rem jp983src, tarefa V6 (C-F4.6): devolve o exe ORIGINAL e o ijl15.dll ORIGINAL do cliente JP 983 de teste
rem (guardados em <exe>.orig e ijl15.dll.orig pelo USAR_EXE_NOSSO.bat) e apaga a chave do modo "continuar".
set PASTA=E:\dev\pangya-test\JP983
set EXE=ProjectG.exe

tasklist /fi "imagename eq %EXE%" 2>nul | find /i "%EXE%" >nul && (echo O jogo esta aberto. Feche antes de trocar. & goto fim)
if not exist "%PASTA%\%EXE%.orig" (
  echo Nao ha %EXE%.orig em %PASTA%: o exe em uso ja deve ser o original.
) else (
  copy /b /y "%PASTA%\%EXE%.orig" "%PASTA%\%EXE%" >nul || (echo ERRO ao devolver o exe original. & goto fim)
  echo Exe original devolvido ^(o %EXE%.orig continua guardado^).
)
if not exist "%PASTA%\ijl15.dll.orig" (
  echo Nao ha ijl15.dll.orig em %PASTA%: o ijl15.dll em uso ja deve ser o original.
) else (
  copy /b /y "%PASTA%\ijl15.dll.orig" "%PASTA%\ijl15.dll" >nul || (echo ERRO ao devolver o ijl15.dll original. & goto fim)
  echo ijl15.dll original devolvido ^(o ijl15.dll.orig continua guardado^).
)
if exist "%PASTA%\jp983_stub_continuar.txt" del "%PASTA%\jp983_stub_continuar.txt"
echo md5 do exe em uso ^(dump do 983 = 8c76194bf825391f63fc951d3d4b09da^):
if exist "%PASTA%\%EXE%" certutil -hashfile "%PASTA%\%EXE%" MD5 | find /v "CertUtil"
echo Lembrete: se voce mexeu no rugburn.json para o teste, devolva a copia guardada.
:fim
endlocal
pause
