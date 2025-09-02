#!/usr/bin/env python3
"""
Script de build otimizado para PyInstaller
Resolve problemas de dependências e terminal fechando
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def limpar_builds_anteriores():
    """Remove builds e dists anteriores"""
    print("🧹 Limpando builds anteriores...")
    
    pastas_para_remover = ['build', 'dist', '__pycache__']
    
    for pasta in pastas_para_remover:
        if os.path.exists(pasta):
            shutil.rmtree(pasta)
            print(f"✅ {pasta} removida")
    
    # Remover arquivos .spec
    for arquivo in os.listdir('.'):
        if arquivo.endswith('.spec'):
            os.remove(arquivo)
            print(f"✅ {arquivo} removido")

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
        'lxml'
    ]
    
    for dep in dependencias:
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Instalando...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])

def criar_arquivo_spec():
    """Cria arquivo .spec personalizado para PyInstaller"""
    print("📝 Criando arquivo .spec personalizado...")
    
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    
    with open('madeforte.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo madeforte.spec criado")

def executar_pyinstaller():
    """Executa PyInstaller com configurações otimizadas"""
    print("🚀 Executando PyInstaller...")
    
    try:
        # Usar arquivo .spec personalizado
        comando = [
            'pyinstaller',
            '--clean',
            'madeforte.spec'
        ]
        
        print(f"Comando: {' '.join(comando)}")
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ PyInstaller executado com sucesso!")
            print("📁 Executável criado em: dist/madeforte.exe")
        else:
            print("❌ Erro no PyInstaller:")
            print(resultado.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        
        # Tentar novamente
        return executar_pyinstaller()
    
    return True

def criar_launcher_bat():
    """Cria arquivo .bat para executar o programa com terminal aberto"""
    print("📝 Criando launcher .bat...")
    
    bat_content = '''@echo off
title Sistema de Rotas - MadeForte
echo ========================================
echo    Sistema de Rotas - MadeForte
echo ========================================
echo.
echo Iniciando sistema...
echo.
echo Pressione qualquer tecla para fechar...
echo.

cd /d "%~dp0"
"madeforte.exe"

echo.
echo Programa finalizado.
pause
'''
    
    with open('executar_madeforte.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ Launcher executar_madeforte.bat criado")

def verificar_arquivos_necessarios():
    """Verifica se todos os arquivos necessários existem"""
    print("🔍 Verificando arquivos necessários...")
    
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
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"\n⚠️  Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Build Otimizado - Sistema de Rotas MadeForte")
    print("=" * 50)
    
    # Verificar arquivos
    if not verificar_arquivos_necessarios():
        print("\n❌ Não é possível continuar sem todos os arquivos necessários")
        return False
    
    # Limpar builds anteriores
    limpar_builds_anteriores()
    
    # Verificar dependências
    verificar_dependencias()
    
    # Criar arquivo .spec
    criar_arquivo_spec()
    
    # Executar PyInstaller
    if not executar_pyinstaller():
        return False
    
    # Criar launcher
    criar_launcher_bat()
    
    print("\n" + "=" * 50)
    print("✅ Build concluído com sucesso!")
    print("\n🎯 Arquivos criados:")
    print("   📄 dist/madeforte.exe - Executável principal")
    print("   📄 executar_madeforte.bat - Launcher com terminal")
    print("\n💡 Para executar:")
    print("   1. Use executar_madeforte.bat (recomendado)")
    print("   2. Ou clique duplo em madeforte.exe")
    print("   3. Ou execute via terminal: madeforte.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Build falhou!")
        print("🔧 Verifique os erros acima e tente novamente")
        sys.exit(1)
