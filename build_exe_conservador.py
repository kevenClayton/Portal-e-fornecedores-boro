#!/usr/bin/env python3
"""
Build conservador - Abordagem mais simples para resolver problemas de dependências
"""

import os
import sys
import subprocess
import shutil

def limpar_builds():
    """Remove builds anteriores"""
    print("🧹 Limpando builds anteriores...")
    
    pastas_para_remover = ['build', 'dist', '__pycache__']
    
    for pasta in pastas_para_remover:
        if os.path.exists(pasta):
            try:
                shutil.rmtree(pasta)
                print(f"✅ {pasta} removida")
            except Exception as e:
                print(f"⚠️  Não foi possível remover {pasta}: {e}")

def verificar_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    print("🔍 Verificando PyInstaller...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller encontrado: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller instalado")
            return True
        except Exception as e:
            print(f"❌ Erro ao instalar PyInstaller: {e}")
            return False

def build_conservador():
    """Build conservador com PyInstaller"""
    print("\n🚀 Executando build conservador...")
    
    # Comando mais simples e direto
    comando = [
        'pyinstaller',
        '--onefile',
        '--name', 'madeforte',
        '--icon', 'icone.ico',
        '--add-data', 'config.py;.',
        '--add-data', 'proxies.txt;.',
        '--add-data', 'model;model',
        '--add-data', 'fazendoLogin.py;.',
        '--add-data', 'ListandoRotas2.py;.',
        '--add-data', 'enviarEmail.py;.',
        '--add-data', 'pegarValorObservacao.py;.',
        '--add-data', 'validarLetraProduto.py;.',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'PySimpleGUI',
        '--hidden-import', 'selenium',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'beautifulsoup4',
        '--hidden-import', 'webdriver_manager',
        '--hidden-import', 'mysql.connector',
        '--hidden-import', 'pymysql',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'sqlalchemy',
        '--hidden-import', 'psycopg2',
        '--hidden-import', 'cx_Oracle',
        '--hidden-import', 'pkg_resources',
        '--hidden-import', 'setuptools',
        '--hidden-import', 'distutils',
        '--hidden-import', 'encodings',
        '--hidden-import', 'codecs',
        '--hidden-import', 'locale',
        '--hidden-import', 'gettext',
        '--hidden-import', 'weakref',
        '--hidden-import', 'collections',
        '--hidden-import', 'itertools',
        '--hidden-import', 'functools',
        '--hidden-import', 'operator',
        '--hidden-import', 'types',
        '--hidden-import', 'builtins',
        '--hidden-import', 'importlib',
        '--hidden-import', 'importlib.machinery',
        '--hidden-import', 'importlib.util',
        '--hidden-import', 'importlib.abc',
        '--collect-submodules', 'tkinter',
        '--collect-submodules', 'PySimpleGUI',
        '--collect-submodules', 'selenium',
        '--collect-submodules', 'pandas',
        '--collect-submodules', 'numpy',
        '--collect-submodules', 'beautifulsoup4',
        '--collect-submodules', 'webdriver_manager',
        '--collect-submodules', 'mysql.connector',
        '--collect-submodules', 'pymysql',
        '--collect-submodules', 'sqlite3',
        '--collect-submodules', 'sqlalchemy',
        '--collect-submodules', 'psycopg2',
        '--collect-submodules', 'cx_Oracle',
        '--collect-submodules', 'pkg_resources',
        '--collect-submodules', 'setuptools',
        '--collect-submodules', 'distutils',
        '--collect-submodules', 'encodings',
        '--collect-submodules', 'codecs',
        '--collect-submodules', 'locale',
        '--collect-submodules', 'gettext',
        '--collect-submodules', 'weakref',
        '--collect-submodules', 'collections',
        '--collect-submodules', 'itertools',
        '--collect-submodules', 'functools',
        '--collect-submodules', 'operator',
        '--collect-submodules', 'types',
        '--collect-submodules', 'builtins',
        '--collect-submodules', 'importlib',
        '--collect-submodules', 'importlib.machinery',
        '--collect-submodules', 'importlib.util',
        '--collect-submodules', 'importlib.abc',
        '--collect-all', 'tkinter',
        '--collect-all', 'PySimpleGUI',
        '--collect-all', 'selenium',
        '--collect-all', 'pandas',
        '--collect-all', 'numpy',
        '--collect-all', 'beautifulsoup4',
        '--collect-all', 'webdriver_manager',
        '--collect-all', 'mysql.connector',
        '--collect-all', 'pymysql',
        '--collect-all', 'sqlite3',
        '--collect-all', 'sqlalchemy',
        '--collect-all', 'psycopg2',
        '--collect-all', 'cx_Oracle',
        '--collect-all', 'pkg_resources',
        '--collect-all', 'setuptools',
        '--collect-all', 'distutils',
        '--collect-all', 'encodings',
        '--collect-all', 'codecs',
        '--collect-all', 'locale',
        '--collect-all', 'gettext',
        '--collect-all', 'weakref',
        '--collect-all', 'collections',
        '--collect-all', 'itertools',
        '--collect-all', 'functools',
        '--collect-all', 'operator',
        '--collect-all', 'types',
        '--collect-all', 'builtins',
        '--collect-all', 'importlib',
        '--collect-all', 'importlib.machinery',
        '--collect-all', 'importlib.util',
        '--collect-all', 'importlib.abc',
        '--debug', 'all',
        '--log-level', 'DEBUG',
        '--noconfirm',
        '--clean',
        'main.py'
    ]
    
    print(f"Comando: {' '.join(comando)}")
    print("⚠️  Este processo pode demorar vários minutos...")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        
        # Verificar executável
        exe_path = 'dist/madeforte.exe'
        if os.path.exists(exe_path):
            tamanho = os.path.getsize(exe_path) / (1024*1024)
            print(f"📁 Executável criado: {exe_path}")
            print(f"📏 Tamanho: {tamanho:.2f} MB")
            
            # Criar launcher
            batch_content = '''@echo off
title Sistema de Rotas - MadeForte
echo.
echo ========================================
echo Sistema de Rotas - MadeForte
echo ========================================
echo.
echo Iniciando aplicacao...
echo.

cd /d "%~dp0"
start "" "dist\\madeforte.exe"

pause
'''
            
            with open('executar_madeforte.bat', 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            print("✅ Launcher criado: executar_madeforte.bat")
            print(f"\n🎯 Para executar:")
            print(f"   1. Clique duplo em executar_madeforte.bat")
            print(f"   2. Ou execute: dist\\madeforte.exe")
            
            return True
        else:
            print("❌ Executável não foi criado!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no PyInstaller: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Build Conservador - Sistema de Rotas MadeForte")
    print("=" * 50)
    
    # Limpar builds anteriores
    limpar_builds()
    
    # Verificar PyInstaller
    if not verificar_pyinstaller():
        print("\n❌ PyInstaller não está funcionando!")
        return False
    
    # Executar build
    if not build_conservador():
        print("\n❌ Build falhou!")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Build conservador concluído!")
    print("\n💡 Se ainda houver problemas:")
    print("   1. Execute: python teste_main_simples.py")
    print("   2. Verifique se o tkinter está funcionando")
    print("   3. Considere reinstalar o Python")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build conservador falhou!")
            print("🔧 Verifique os erros acima")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

