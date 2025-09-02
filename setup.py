#!/usr/bin/env python3
"""
Script de setup para instalar dependências e configurar o ambiente
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências do requirements.txt"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_python_version():
    """Verifica a versão do Python"""
    print(f"🐍 Versão do Python: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário")
        return False
    
    print("✅ Versão do Python compatível!")
    return True

def check_files():
    """Verifica se os arquivos necessários existem"""
    print("\n📁 Verificando arquivos...")
    
    required_files = [
        'main.py',
        'config.py',
        'proxies.txt',
        'model/db.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NÃO ENCONTRADO")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os arquivos necessários encontrados!")
    return True

def main():
    """Função principal de setup"""
    print("🚀 Setup do Sistema de Rotas")
    print("=" * 40)
    
    # Verificar versão do Python
    if not check_python_version():
        return False
    
    # Verificar arquivos
    if not check_files():
        print("\n⚠️  Alguns arquivos estão faltando. Verifique se está na pasta correta.")
        return False
    
    # Instalar dependências
    if not install_requirements():
        return False
    
    print("\n" + "=" * 40)
    print("✅ Setup concluído com sucesso!")
    print("\n🎯 Próximos passos:")
    print("1. Execute: python test_setup.py")
    print("2. Se tudo estiver OK, execute: python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
