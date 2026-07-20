@echo off
REM Gera PortalFornecedores.exe COM config embutida (sem .env no cliente)
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-build.txt

echo.
echo Gerando config embutida a partir do .env ...
python scripts\gerar_config_embutida.py --env-file .env
if errorlevel 1 (
  echo ERRO: nao foi possivel gerar config embutida. Confira o .env
  pause
  exit /b 1
)

echo.
echo Gerando executavel com PyInstaller...
pyinstaller --noconfirm portal.spec

echo.
echo ========================================
echo Pronto: dist\PortalFornecedores.exe
echo.
echo Envie SOMENTE o .exe para o cliente.
echo A config do banco ja esta dentro do executavel.
echo Cliente precisa ter Google Chrome instalado.
echo ========================================
pause
