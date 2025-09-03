#!/usr/bin/env python3
"""
Script de build automatizado para múltiplos clientes
Gera um executável para cada cliente com configurações específicas
"""

import os
import sys
import subprocess
import shutil
import time
import traceback
import json
from pathlib import Path

# Cores dos clientes
CORES_CLIENTES = {
    'madeforte': '#2b6600',      # Verde
    'boro': '#011a41',           # Azul escuro
    'rttransportes': '#fc9917',  # Laranja
    'jslogistica': '#011a41',    # Azul escuro
}

# Nomes de exibição dos clientes
NOMES_CLIENTES = {
    'madeforte': 'MadeForte',
    'boro': 'Boro',
    'rttransportes': 'RT Transportes',
    'jslogistica': 'JS Logística',
}

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
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

def criar_config_cliente(cliente, cor):
    """Cria arquivo config.py específico para o cliente"""
    print(f"📝 Criando config.py para {cliente}...")
    
    config_content = f'''global cliente
global fundo

cliente = '{cliente}'
fundo = '{cor}'

conexoes = {{
    '{cliente}': {{
        'host': 'mysql.{cliente}.maranatatecnologia.com.br' if cliente in ['madeforte', 'rttransportes'] else 'reservaai.cgns57eoufkz.us-east-1.rds.amazonaws.com',
        'user': '{cliente}' if cliente in ['madeforte', 'rttransportes'] else 'robo',
        'password': 'Secpol2' if cliente in ['madeforte', 'rttransportes'] else 'D41D8CD98F00B204E9800998ECF8427E',
        'database': '{cliente}',
    }}
}}

# Configuração específica para {cliente}
print(f"🚀 Iniciando sistema para cliente: {{NOMES_CLIENTES.get(cliente, cliente)}}")
print(f"🎨 Cor do tema: {{cor}}")
'''
    
    config_path = f'config_{cliente}.py'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ {config_path} criado")
    return config_path

def criar_main_cliente(cliente, config_path):
    """Cria arquivo main.py específico para o cliente"""
    print(f"📝 Criando main.py para {cliente}...")
    
    # Ler o main.py original
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Substituir import do config
    main_content = main_content.replace('import config', f'import {config_path.replace(".py", "")}')
    
    # Adicionar informações do cliente no título
    nome_cliente = NOMES_CLIENTES.get(cliente, cliente.title())
    main_content = main_content.replace(
        'sg.Text("Buscar e aceitar rotas no e-Fornecedor")',
        f'sg.Text("Buscar e aceitar rotas no e-Fornecedor - {nome_cliente}")'
    )
    
    main_path = f'main_{cliente}.py'
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print(f"✅ {main_path} criado")
    return main_path

def criar_spec_cliente(cliente, main_path, config_path):
    """Cria arquivo .spec específico para o cliente"""
    print(f"📝 Criando .spec para {cliente}...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_path}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{config_path}', '.'),
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
    hooksconfig={{}},
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
    name='{cliente}',
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
    
    spec_path = f'{cliente}.spec'
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ {spec_path} criado")
    return spec_path

def executar_pyinstaller_cliente(cliente, spec_path):
    """Executa PyInstaller para o cliente específico"""
    print(f"\n🚀 Executando PyInstaller para {cliente}...")
    
    try:
        # Verificar se PyInstaller está instalado
        try:
            import PyInstaller
            print(f"✅ PyInstaller encontrado: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller não encontrado. Instalando...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        comando = [
            'pyinstaller',
            '--clean',
            '--log-level=INFO',
            spec_path
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
            print(f"✅ PyInstaller executado com sucesso para {cliente}!")
            
            # Verificar se o executável foi criado
            exe_path = f'dist/{cliente}.exe'
            if os.path.exists(exe_path):
                tamanho = os.path.getsize(exe_path) / (1024*1024)
                print(f"📏 Tamanho do executável: {tamanho:.2f} MB")
                return True
            else:
                print(f"❌ Executável não foi criado para {cliente}!")
                return False
        else:
            print(f"❌ Erro no PyInstaller para {cliente}:")
            if resultado.stderr:
                print(f"STDERR: {resultado.stderr[:500]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ PyInstaller demorou muito para {cliente} (timeout de 30 minutos)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar PyInstaller para {cliente}: {e}")
        return False

def limpar_arquivos_temporarios(cliente):
    """Remove arquivos temporários criados para o cliente"""
    print(f"🧹 Limpando arquivos temporários de {cliente}...")
    
    arquivos_para_remover = [
        f'config_{cliente}.py',
        f'main_{cliente}.py',
        f'{cliente}.spec'
    ]
    
    for arquivo in arquivos_para_remover:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"✅ {arquivo} removido")
            except Exception as e:
                print(f"⚠️  Não foi possível remover {arquivo}: {e}")

def criar_launcher_batch(cliente):
    """Cria arquivo .bat para executar o cliente"""
    print(f"📝 Criando launcher para {cliente}...")
    
    batch_content = f'''@echo off
title Sistema de Rotas - {NOMES_CLIENTES.get(cliente, cliente.title())}
echo.
echo ========================================
echo Sistema de Rotas - {NOMES_CLIENTES.get(cliente, cliente.title())}
echo ========================================
echo.
echo Iniciando aplicacao...
echo.
echo Pressione qualquer tecla para fechar...
echo.

cd /d "%~dp0"
start "" "dist\\{cliente}.exe"

pause
'''
    
    batch_path = f'executar_{cliente}.bat'
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ {batch_path} criado")

def criar_relatorio_build(clientes_processados):
    """Cria relatório do build"""
    print("\n📊 Criando relatório do build...")
    
    relatorio_content = f'''# Relatório de Build - Sistema de Rotas
Data: {time.strftime('%d/%m/%Y %H:%M:%S')}

## Clientes Processados

'''
    
    for cliente, status in clientes_processados.items():
        nome_cliente = NOMES_CLIENTES.get(cliente, cliente.title())
        cor = CORES_CLIENTES.get(cliente, '#000000')
        status_texto = "✅ SUCESSO" if status else "❌ FALHOU"
        
        relatorio_content += f'''### {nome_cliente} ({cliente})
- **Status**: {status_texto}
- **Cor do tema**: {cor}
- **Executável**: dist/{cliente}.exe
- **Launcher**: executar_{cliente}.bat

'''
    
    relatorio_content += f'''
## Instruções de Uso

1. **Executar via launcher**: Clique duplo em `executar_[cliente].bat`
2. **Executar direto**: Clique duplo em `dist/[cliente].exe`
3. **Via terminal**: `dist\\[cliente].exe`

## Arquivos Gerados

- `dist/` - Pasta com todos os executáveis
- `executar_[cliente].bat` - Launchers para cada cliente
- `build/` - Arquivos temporários do build (pode ser removida)

## Observações

- Cada executável é independente e configurado para seu cliente
- As cores e configurações são específicas de cada cliente
- Todos os executáveis incluem tkinter e dependências necessárias
'''
    
    relatorio_path = 'RELATORIO_BUILD.md'
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write(relatorio_content)
    
    print(f"✅ {relatorio_path} criado")

def main():
    """Função principal"""
    print("🚀 Build Multi-Clientes - Sistema de Rotas")
    print("=" * 60)
    
    # Verificar dependências
    if not verificar_dependencias():
        print("\n❌ Dependências faltando!")
        return False
    
    # Limpar builds anteriores
    limpar_builds_anteriores()
    
    # Lista de clientes para processar
    clientes = list(CORES_CLIENTES.keys())
    clientes_processados = {}
    
    print(f"\n🎯 Processando {len(clientes)} clientes:")
    for cliente in clientes:
        nome = NOMES_CLIENTES.get(cliente, cliente.title())
        cor = CORES_CLIENTES.get(cliente, '#000000')
        print(f"   • {nome} ({cliente}) - Cor: {cor}")
    
    print("\n" + "=" * 60)
    
    # Processar cada cliente
    for i, cliente in enumerate(clientes, 1):
        print(f"\n🔄 [{i}/{len(clientes)}] Processando {cliente}...")
        print("-" * 40)
        
        try:
            # Criar arquivos específicos do cliente
            config_path = criar_config_cliente(cliente, CORES_CLIENTES[cliente])
            main_path = criar_main_cliente(cliente, config_path)
            spec_path = criar_spec_cliente(cliente, main_path, config_path)
            
            # Executar PyInstaller
            sucesso = executar_pyinstaller_cliente(cliente, spec_path)
            clientes_processados[cliente] = sucesso
            
            if sucesso:
                # Criar launcher
                criar_launcher_batch(cliente)
                print(f"✅ {cliente} processado com sucesso!")
            else:
                print(f"❌ {cliente} falhou no build!")
            
            # Limpar arquivos temporários
            limpar_arquivos_temporarios(cliente)
            
        except Exception as e:
            print(f"❌ Erro ao processar {cliente}: {e}")
            clientes_processados[cliente] = False
            traceback.print_exc()
        
        print("-" * 40)
    
    # Criar relatório
    criar_relatorio_build(clientes_processados)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 BUILD MULTI-CLIENTES CONCLUÍDO!")
    print("\n📊 Resumo:")
    
    sucessos = sum(clientes_processados.values())
    total = len(clientes_processados)
    
    for cliente, status in clientes_processados.items():
        nome = NOMES_CLIENTES.get(cliente, cliente.title())
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {nome} ({cliente})")
    
    print(f"\n📈 Resultado: {sucessos}/{total} clientes com sucesso")
    
    if sucessos == total:
        print("🎉 Todos os clientes foram processados com sucesso!")
    else:
        print("⚠️  Alguns clientes falharam. Verifique os erros acima.")
    
    print("\n💡 Para executar:")
    print("   1. Use os arquivos .bat criados")
    print("   2. Ou execute diretamente os .exe em dist/")
    print("   3. Consulte o RELATORIO_BUILD.md para detalhes")
    
    return sucessos == total

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build multi-clientes falhou!")
            print("🔧 Verifique os erros acima e tente novamente")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Build interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)

