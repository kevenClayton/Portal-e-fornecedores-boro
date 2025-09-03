#!/usr/bin/env python3
"""
Build com --onedir - Resolve problemas de Access Violation
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

def build_onedir():
    """Build com --onedir (não --onefile)"""
    print("\n🚀 Executando build com --onedir...")
    
    # Comando com --onedir (mais estável)
    comando = [
        'pyinstaller',
        '--onedir',
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
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'FreeSimpleGUI',
        '--hidden-import', 'selenium',
        '--hidden-import', 'selenium.webdriver',
        '--hidden-import', 'selenium.webdriver.chrome',
        '--hidden-import', 'selenium.webdriver.common',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'bs4',
        '--hidden-import', 'webdriver_manager',
        '--hidden-import', 'mysql.connector',
        '--hidden-import', 'pymysql',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'requests',
        '--hidden-import', 'lxml',
        '--hidden-import', 'unidecode',
        '--collect-submodules', 'tkinter',
        '--collect-submodules', 'FreeSimpleGUI',
        '--collect-submodules', 'selenium',
        '--collect-submodules', 'pandas',
        '--collect-submodules', 'numpy',
        '--collect-submodules', 'bs4',
        '--collect-submodules', 'webdriver_manager',
        '--collect-submodules', 'mysql.connector',
        '--collect-submodules', 'pymysql',
        '--collect-submodules', 'sqlite3',
        '--collect-submodules', 'requests',
        '--collect-submodules', 'lxml',
        '--collect-submodules', 'unidecode',
        '--collect-all', 'tkinter',
        '--collect-all', 'FreeSimpleGUI',
        '--collect-all', 'selenium',
        '--collect-all', 'pandas',
        '--collect-all', 'numpy',
        '--collect-all', 'bs4',
        '--collect-all', 'webdriver_manager',
        '--collect-all', 'mysql.connector',
        '--collect-all', 'pymysql',
        '--collect-all', 'sqlite3',
        '--collect-all', 'requests',
        '--collect-all', 'lxml',
        '--collect-all', 'unidecode',
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
        
        # Verificar pasta dist
        dist_path = 'dist/madeforte'
        if os.path.exists(dist_path):
            # Contar arquivos
            arquivos = []
            for root, dirs, files in os.walk(dist_path):
                for file in files:
                    arquivos.append(os.path.join(root, file))
            
            print(f"📁 Pasta criada: {dist_path}")
            print(f"📊 Total de arquivos: {len(arquivos)}")
            
            # Verificar executável
            exe_path = os.path.join(dist_path, 'madeforte.exe')
            if os.path.exists(exe_path):
                tamanho = os.path.getsize(exe_path) / (1024*1024)
                print(f"📁 Executável: {exe_path}")
                print(f"📏 Tamanho: {tamanho:.2f} MB")
                
                # Criar launcher
                batch_content = f'''@echo off
title Sistema de Rotas - MadeForte
echo.
echo ========================================
echo Sistema de Rotas - MadeForte
echo ========================================
echo.
echo Iniciando aplicacao...
echo.

cd /d "%~dp0"
start "" "{dist_path}\\madeforte.exe"

pause
'''
                
                with open('executar_madeforte_onedir.bat', 'w', encoding='utf-8') as f:
                    f.write(batch_content)
                
                print("✅ Launcher criado: executar_madeforte_onedir.bat")
                print(f"\n🎯 Para executar:")
                print(f"   1. Clique duplo em executar_madeforte_onedir.bat")
                print(f"   2. Ou execute: {dist_path}\\madeforte.exe")
                print(f"   3. Ou navegue até: {dist_path}")
                
                return True
            else:
                print("❌ Executável não foi criado!")
                return False
        else:
            print("❌ Pasta dist não foi criada!")
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
    print("🚀 Build com --onedir - Sistema de Rotas MadeForte")
    print("=" * 50)
    
    # Limpar builds anteriores
    limpar_builds()
    
    # Verificar PyInstaller
    if not verificar_pyinstaller():
        print("\n❌ PyInstaller não está funcionando!")
        return False
    
    # Executar build
    if not build_onedir():
        print("\n❌ Build falhou!")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Build com --onedir concluído!")
    print("\n💡 Vantagens do --onedir:")
    print("   - Mais estável que --onefile")
    print("   - Menos problemas de Access Violation")
    print("   - Mais fácil de debugar")
    print("   - Melhor compatibilidade com Windows")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build com --onedir falhou!")
            print("🔧 Verifique os erros acima")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

