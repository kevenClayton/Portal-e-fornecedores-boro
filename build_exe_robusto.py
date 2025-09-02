#!/usr/bin/env python3
"""
Script de build robusto para PyInstaller
Inclui tratamento de erros detalhado e verificações adicionais
"""

import os
import sys
import subprocess
import shutil
import time
import traceback
from pathlib import Path

def limpar_builds_anteriores():
    """Remove builds e dists anteriores"""
    print("🧹 Limpando builds anteriores...")
    
    pastas_para_remover = ['build', 'dist', '__pycache__']
    
    for pasta in pastas_para_remover:
        if os.path.exists(pasta):
            try:
                shutil.rmtree(pasta)
                print(f"✅ {pasta} removida")
            except Exception as e:
                print(f"⚠️  Não foi possível remover {pasta}: {e}")
    
    # Remover arquivos .spec
    for arquivo in os.listdir('.'):
        if arquivo.endswith('.spec'):
            try:
                os.remove(arquivo)
                print(f"✅ {arquivo} removido")
            except Exception as e:
                print(f"⚠️  Não foi possível remover {arquivo}: {e}")

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    dependencias = [
        'PySimpleGUI',
        'selenium',
        'pandas',
        'numpy',
        'unidecode',
        'beautifulsoup4',
        'requests',
        'lxml',
        'webdriver_manager'
    ]
    
    dependencias_faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO ENCONTRADO")
            dependencias_faltando.append(dep)
    
    if dependencias_faltando:
        print(f"\n⚠️  Dependências faltando: {', '.join(dependencias_faltando)}")
        print("Instalando dependências faltantes...")
        
        for dep in dependencias_faltando:
            try:
                print(f"📦 Instalando {dep}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"✅ {dep} instalado")
            except Exception as e:
                print(f"❌ Erro ao instalar {dep}: {e}")
                return False
    
    return True

def verificar_arquivos_necessarios():
    """Verifica se todos os arquivos necessários existem"""
    print("\n🔍 Verificando arquivos necessários...")
    
    arquivos_necessarios = [
        'main.py',
        'config.py',
        'proxies.txt',
        'model/db.py',
        'fazendoLogin.py',
        'ListandoRotas2.py',
        'enviarEmail.py',
        'pegarValorObservacao.py',
        'validarLetraProduto.py'
    ]
    
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            try:
                # Tentar abrir o arquivo para verificar se é legível
                with open(arquivo, 'r', encoding='utf-8') as f:
                    f.read(100)
                print(f"✅ {arquivo}")
            except Exception as e:
                print(f"❌ {arquivo} - ERRO AO LER: {e}")
                arquivos_faltando.append(arquivo)
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"\n❌ Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    
    return True

def criar_arquivo_spec_robusto():
    """Cria arquivo .spec robusto para PyInstaller"""
    print("\n📝 Criando arquivo .spec robusto...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('proxies.txt', '.'),
        ('model', 'model'),
        ('fazendoLogin.py', '.'),
        ('ListandoRotas2.py', '.'),
        ('enviarEmail.py', '.'),
        ('pegarValorObservacao.py', '.'),
        ('validarLetraProduto.py', '.'),
        ('icone.ico', '.'),
    ],
    hiddenimports=[
        'PySimpleGUI',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support',
        'selenium.common.exceptions',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.support.wait',
        'pandas',
        'numpy',
        'unidecode',
        'bs4',
        'beautifulsoup4',
        'requests',
        'lxml',
        'email.mime.multipart',
        'email.mime.text',
        'email.mime.image',
        'smtplib',
        'ssl',
        'threading',
        'datetime',
        'time',
        'logging',
        'sys',
        'os',
        'random',
        'urllib.parse',
        'pathlib',
        'shutil',
        'subprocess',
        'traceback',
        'zipfile',
        'json',
        'webdriver_manager',
        'webdriver_manager.chrome',
        'mysql.connector',
        'pymysql',
        'sqlite3',
        'sqlalchemy',
        'psycopg2',
        'cx_Oracle',
        'pkg_resources',
        'setuptools',
        'distutils',
        'encodings',
        'codecs',
        'locale',
        'gettext',
        'weakref',
        'collections',
        'itertools',
        'functools',
        'operator',
        'types',
        'builtins',
        'importlib',
        'importlib.machinery',
        'importlib.util',
        'importlib.abc',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'unittest',
        'doctest',
        'test',
        'tests',
        'testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='madeforte',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icone.ico'
)
'''
    
    with open('madeforte_robusto.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo madeforte_robusto.spec criado")

def executar_pyinstaller_robusto():
    """Executa PyInstaller com configurações robustas"""
    print("\n🚀 Executando PyInstaller robusto...")
    
    try:
        # Verificar se PyInstaller está instalado
        try:
            import PyInstaller
            print(f"✅ PyInstaller encontrado: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller não encontrado. Instalando...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        # Usar arquivo .spec robusto
        comando = [
            'pyinstaller',
            '--clean',
            '--log-level=DEBUG',
            'madeforte_robusto.spec'
        ]
        
        print(f"Comando: {' '.join(comando)}")
        print("⚠️  Este processo pode demorar vários minutos...")
        
        resultado = subprocess.run(
            comando, 
            capture_output=True, 
            text=True,
            timeout=1800  # 30 minutos de timeout
        )
        
        if resultado.returncode == 0:
            print("✅ PyInstaller executado com sucesso!")
            print("📁 Executável criado em: dist/madeforte.exe")
            
            # Verificar se o executável foi criado
            if os.path.exists('dist/madeforte.exe'):
                tamanho = os.path.getsize('dist/madeforte.exe') / (1024*1024)
                print(f"📏 Tamanho do executável: {tamanho:.2f} MB")
                return True
            else:
                print("❌ Executável não foi criado!")
                return False
        else:
            print("❌ Erro no PyInstaller:")
            print("STDOUT:", resultado.stdout)
            print("STDERR:", resultado.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PyInstaller demorou muito (timeout de 30 minutos)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar PyInstaller: {e}")
        traceback.print_exc()
        return False

def criar_launcher_robusto():
    """Cria launcher robusto para executar o programa"""
    print("\n📝 Criando launcher robusto...")
    
    bat_content = '''@echo off
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
if not exist "dist\\madeforte.exe" (
    echo ❌ ERRO: Executavel nao encontrado!
    echo Verifique se o build foi concluido corretamente.
    pause
    exit /b 1
)

REM Executar com tratamento de erro
echo ✅ Executavel encontrado, iniciando...
echo.

"dist\\madeforte.exe"

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
'''
    
    with open('executar_madeforte_robusto.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ Launcher executar_madeforte_robusto.bat criado")

def testar_executavel():
    """Testa o executável criado"""
    print("\n🧪 Testando executável criado...")
    
    exe_path = "dist/madeforte.exe"
    
    if not os.path.exists(exe_path):
        print("❌ Executável não encontrado para teste")
        return False
    
    try:
        print("   Iniciando teste de execução...")
        
        # Executar com timeout de 10 segundos
        processo = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("   Aguardando 10 segundos...")
        time.sleep(10)
        
        # Verificar se ainda está rodando
        if processo.poll() is None:
            print("   ✅ Executável está rodando (bom sinal)")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
            return True
        else:
            stdout, stderr = processo.communicate()
            print(f"   ❌ Executável terminou com código: {processo.returncode}")
            if stderr:
                print(f"   STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Build Robusto - Sistema de Rotas MadeForte")
    print("=" * 60)
    
    # Verificar arquivos
    if not verificar_arquivos_necessarios():
        print("\n❌ Não é possível continuar sem todos os arquivos necessários")
        return False
    
    # Limpar builds anteriores
    limpar_builds_anteriores()
    
    # Verificar dependências
    if not verificar_dependencias():
        print("\n❌ Erro ao verificar/instalar dependências")
        return False
    
    # Criar arquivo .spec robusto
    criar_arquivo_spec_robusto()
    
    # Executar PyInstaller
    if not executar_pyinstaller_robusto():
        print("\n❌ Build falhou!")
        return False
    
    # Criar launcher robusto
    criar_launcher_robusto()
    
    # Testar executável
    if not testar_executavel():
        print("\n⚠️  Executável pode ter problemas")
    else:
        print("\n✅ Executável testado com sucesso!")
    
    print("\n" + "=" * 60)
    print("✅ Build robusto concluído!")
    print("\n🎯 Arquivos criados:")
    print("   📄 dist/madeforte.exe - Executável principal")
    print("   📄 executar_madeforte_robusto.bat - Launcher robusto")
    print("\n💡 Para executar:")
    print("   1. Use executar_madeforte_robusto.bat (recomendado)")
    print("   2. Ou execute via terminal: dist\\madeforte.exe")
    print("   3. Ou teste com: python test_executavel.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build robusto falhou!")
            print("🔧 Verifique os erros acima e tente novamente")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Build interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)
