#!/usr/bin/env python3
"""
Script de build específico para resolver problema do tkinter
"""

import os
import sys
import subprocess
import shutil
import time
import traceback

def verificar_tkinter():
    """Verifica se tkinter está disponível"""
    print("🔍 Verificando tkinter...")
    
    try:
        import tkinter
        print("✅ tkinter encontrado")
        
        # Testar criação de janela básica
        root = tkinter.Tk()
        root.withdraw()  # Não mostrar a janela
        root.destroy()
        print("✅ tkinter funcionando")
        return True
        
    except ImportError as e:
        print(f"❌ tkinter não encontrado: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar tkinter: {e}")
        return False

def instalar_tkinter():
    """Tenta instalar tkinter"""
    print("📦 Tentando instalar tkinter...")
    
    try:
        # No Windows, tkinter geralmente vem com Python
        # Mas vamos tentar instalar via pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tk'])
        print("✅ tk instalado")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar tk: {e}")
        return False

def verificar_dependencias_completas():
    """Verifica todas as dependências incluindo tkinter"""
    print("🔍 Verificando dependências completas...")
    
    dependencias = [
        'tkinter',
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
            if dep == 'tkinter':
                import tkinter
                print(f"✅ {dep}")
            else:
                __import__(dep.lower().replace('-', '_'))
                print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO ENCONTRADO")
            dependencias_faltando.append(dep)
    
    if dependencias_faltando:
        print(f"\n⚠️  Dependências faltando: {', '.join(dependencias_faltando)}")
        return False
    
    return True

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

def criar_arquivo_spec_tkinter():
    """Cria arquivo .spec com tkinter explicitamente incluído"""
    print("📝 Criando arquivo .spec com tkinter...")
    
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
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'tkinter.commondialog',
        'tkinter.constants',
        'tkinter.dnd',
        'tkinter.font',
        'tkinter.scrolledtext',
        'tkinter.tix',
        'tkinter.turtle',
        '_tkinter',
        'tkinter._tkinter',
        'tkinter.tkinter',
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
    
    with open('madeforte_tkinter.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo madeforte_tkinter.spec criado")

def executar_pyinstaller_tkinter():
    """Executa PyInstaller com configurações para tkinter"""
    print("\n🚀 Executando PyInstaller com tkinter...")
    
    try:
        # Verificar se PyInstaller está instalado
        try:
            import PyInstaller
            print(f"✅ PyInstaller encontrado: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller não encontrado. Instalando...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        # Usar arquivo .spec com tkinter
        comando = [
            'pyinstaller',
            '--clean',
            '--log-level=DEBUG',
            'madeforte_tkinter.spec'
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

def testar_executavel_tkinter():
    """Testa o executável criado especificamente para tkinter"""
    print("\n🧪 Testando executável com tkinter...")
    
    exe_path = "dist/madeforte.exe"
    
    if not os.path.exists(exe_path):
        print("❌ Executável não encontrado para teste")
        return False
    
    try:
        print("   Iniciando teste de execução...")
        
        # Executar com timeout de 15 segundos
        processo = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("   Aguardando 15 segundos...")
        time.sleep(15)
        
        # Verificar se ainda está rodando
        if processo.poll() is None:
            print("   ✅ Executável está rodando (tkinter funcionando!)")
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
    print("🚀 Build com Tkinter - Sistema de Rotas MadeForte")
    print("=" * 60)
    
    # Verificar tkinter primeiro
    if not verificar_tkinter():
        print("\n⚠️  Tkinter não encontrado, tentando instalar...")
        if not instalar_tkinter():
            print("❌ Não foi possível instalar tkinter")
            print("🔧 Tkinter deve vir com Python. Verifique sua instalação.")
            return False
        
        # Verificar novamente
        if not verificar_tkinter():
            print("❌ Tkinter ainda não está funcionando")
            return False
    
    # Verificar todas as dependências
    if not verificar_dependencias_completas():
        print("\n❌ Algumas dependências estão faltando")
        return False
    
    # Limpar builds anteriores
    limpar_builds_anteriores()
    
    # Criar arquivo .spec com tkinter
    criar_arquivo_spec_tkinter()
    
    # Executar PyInstaller
    if not executar_pyinstaller_tkinter():
        print("\n❌ Build falhou!")
        return False
    
    # Testar executável
    if not testar_executavel_tkinter():
        print("\n⚠️  Executável pode ter problemas com tkinter")
    else:
        print("\n✅ Executável testado com sucesso! Tkinter funcionando!")
    
    print("\n" + "=" * 60)
    print("✅ Build com tkinter concluído!")
    print("\n🎯 Arquivos criados:")
    print("   📄 dist/madeforte.exe - Executável com tkinter")
    print("   📄 madeforte_tkinter.spec - Configuração com tkinter")
    print("\n💡 Para executar:")
    print("   1. Clique duplo em dist\\madeforte.exe")
    print("   2. Ou execute via terminal: dist\\madeforte.exe")
    print("   3. Ou teste com: python test_executavel.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build com tkinter falhou!")
            print("🔧 Verifique os erros acima e tente novamente")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Build interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)

