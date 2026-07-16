@echo off
REM Gera PortalFornecedores.exe (rode isto no Windows)
cd /d "%~dp0"

python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-build.txt
pip install playwright

echo.
echo Gerando executavel...
pyinstaller --noconfirm portal.spec

echo.
echo ========================================
echo Pronto!
echo Arquivo: dist\PortalFornecedores.exe
echo.
echo Para o cliente, envie a pasta com:
echo   - PortalFornecedores.exe
echo   - .env  (credenciais do banco)
echo   - LEIA-ME-CLIENTE.txt
echo.
echo O cliente precisa ter Google Chrome instalado.
echo ========================================
pause
