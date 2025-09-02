@echo off
title Sistema de Rotas - MadeForte (Robusto)
echo ========================================
echo    Sistema de Rotas - MadeForte
echo ========================================
echo.
echo Iniciando sistema...
echo.
echo Se houver erros, eles aparecerao abaixo:
echo.

cd /d "%~dp0"

REM Verificar se o executável existe
if not exist "dist\madeforte.exe" (
    echo ❌ ERRO: Executavel nao encontrado!
    echo Verifique se o build foi concluido corretamente.
    pause
    exit /b 1
)

REM Executar com tratamento de erro
echo ✅ Executavel encontrado, iniciando...
echo.

"dist\madeforte.exe"

REM Verificar código de saída
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERRO: Programa terminou com codigo %ERRORLEVEL%
    echo.
) else (
    echo.
    echo ✅ Programa finalizado com sucesso!
    echo.
)

echo Pressione qualquer tecla para fechar...
pause >nul
