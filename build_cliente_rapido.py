#!/usr/bin/env python3
"""
Script de build rápido para um cliente específico
Uso: python build_cliente_rapido.py [nome_do_cliente]
"""

import os
import sys
import subprocess
import shutil
import time

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

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("🚀 Build Cliente Rápido - Sistema de Rotas")
        print("=" * 50)
        print("Uso: python build_cliente_rapido.py [cliente]")
        print("\nClientes disponíveis:")
        for cliente, nome in NOMES_CLIENTES.items():
            cor = CORES_CLIENTES.get(cliente, '#000000')
            print(f"   • {nome} ({cliente}) - Cor: {cor}")
        print("\nExemplo: python build_cliente_rapido.py madeforte")
        return
    
    cliente = sys.argv[1].lower()
    
    if cliente not in CORES_CLIENTES:
        print(f"❌ Cliente '{cliente}' não encontrado!")
        print("Clientes disponíveis:", ", ".join(CORES_CLIENTES.keys()))
        return
    
    print(f"🚀 Build Rápido para {NOMES_CLIENTES[cliente]} ({cliente})")
    print("=" * 50)
    
    # Criar config específico
    config_content = f'''global cliente
global fundo

cliente = '{cliente}'
fundo = '{CORES_CLIENTES[cliente]}'

conexoes = {{
    '{cliente}': {{
        'host': 'mysql.{cliente}.maranatatecnologia.com.br' if cliente in ['madeforte', 'rttransportes'] else 'reservaai.cgns57eoufkz.us-east-1.rds.amazonaws.com',
        'user': '{cliente}' if cliente in ['madeforte', 'rttransportes'] else 'robo',
        'password': 'Secpol2' if cliente in ['madeforte', 'rttransportes'] else 'D41D8CD98F00B204E9800998ECF8427E',
        'database': '{cliente}',
    }}
}}
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Config criado para {cliente}")
    
    # Executar PyInstaller
    print(f"\n🚀 Executando PyInstaller para {cliente}...")
    
    comando = [
        'pyinstaller',
        '--onefile',
        '--name', cliente,
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
        'main.py'
    ]
    
    print(f"Comando: {' '.join(comando)}")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print(f"✅ Build concluído para {cliente}!")
        
        # Verificar executável
        exe_path = f'dist/{cliente}.exe'
        if os.path.exists(exe_path):
            tamanho = os.path.getsize(exe_path) / (1024*1024)
            print(f"📁 Executável criado: {exe_path}")
            print(f"📏 Tamanho: {tamanho:.2f} MB")
            
            # Criar launcher
            batch_content = f'''@echo off
title Sistema de Rotas - {NOMES_CLIENTES[cliente]}
echo.
echo ========================================
echo Sistema de Rotas - {NOMES_CLIENTES[cliente]}
echo ========================================
echo.
echo Iniciando aplicacao...
echo.

cd /d "%~dp0"
start "" "dist\\{cliente}.exe"
'''
            
            batch_path = f'executar_{cliente}.bat'
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            print(f"✅ Launcher criado: {batch_path}")
            print(f"\n🎯 Para executar:")
            print(f"   1. Clique duplo em {batch_path}")
            print(f"   2. Ou execute: dist\\{cliente}.exe")
            
        else:
            print(f"❌ Executável não foi criado!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no PyInstaller: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()

