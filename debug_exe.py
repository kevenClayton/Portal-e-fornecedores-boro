#!/usr/bin/env python3
"""
Script de debug para identificar problemas no executável
"""

import os
import sys
import subprocess
import traceback

def test_imports():
    """Testa todas as importações necessárias"""
    print("🧪 Testando importações...")
    
    imports_to_test = [
        ('PySimpleGUI', 'PySimpleGUI'),
        ('selenium', 'selenium'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('unidecode', 'unidecode'),
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests'),
        ('lxml', 'lxml'),
        ('smtplib', 'smtplib'),
        ('email.mime.multipart', 'email.mime.multipart'),
        ('email.mime.text', 'email.mime.text'),
        ('threading', 'threading'),
        ('datetime', 'datetime'),
        ('logging', 'logging'),
        ('urllib.parse', 'urllib.parse'),
        ('pathlib', 'pathlib'),
        ('shutil', 'shutil'),
        ('subprocess', 'subprocess'),
        ('zipfile', 'zipfile'),
        ('json', 'json'),
    ]
    
    failed_imports = []
    
    for module_name, package_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name}: {e}")
            failed_imports.append(package_name)
    
    return failed_imports

def test_file_access():
    """Testa acesso aos arquivos necessários"""
    print("\n🔍 Testando acesso aos arquivos...")
    
    files_to_test = [
        'config.py',
        'proxies.txt',
        'model/db.py',
        'fazendoLogin.py',
        'ListandoRotas2.py',
        'enviarEmail.py',
        'pegarValorObservacao.py',
        'validarLetraProduto.py'
    ]
    
    failed_files = []
    
    for file_path in files_to_test:
        try:
            if os.path.exists(file_path):
                # Tentar abrir o arquivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Ler apenas 100 caracteres
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - NÃO ENCONTRADO")
                failed_files.append(file_path)
        except Exception as e:
            print(f"❌ {file_path} - ERRO AO LER: {e}")
            failed_files.append(file_path)
    
    return failed_files

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n🗄️  Testando conexão com banco...")
    
    try:
        import model.db as db
        dados = db.DADOS()
        print("✅ Conexão com banco estabelecida!")
        print(f"   Login configurado: {'login' in dados}")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        traceback.print_exc()
        return False

def test_gui_creation():
    """Testa criação da interface gráfica"""
    print("\n🖥️  Testando criação da interface...")
    
    try:
        import PySimpleGUI as sg
        
        # Layout simples
        layout = [
            [sg.Text("Teste de Interface")],
            [sg.Button("OK"), sg.Button("Cancelar")]
        ]
        
        # Criar janela
        window = sg.Window("Teste", layout, finalize=True)
        
        # Simular evento
        event, values = window.read(timeout=1000)
        
        # Fechar janela
        window.close()
        
        print("✅ Interface gráfica funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na interface gráfica: {e}")
        traceback.print_exc()
        return False

def test_selenium_components():
    """Testa componentes do Selenium"""
    print("\n🌐 Testando componentes Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print("✅ Componentes Selenium importados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos componentes Selenium: {e}")
        traceback.print_exc()
        return False

def test_email_functionality():
    """Testa funcionalidade de email"""
    print("\n📧 Testando funcionalidade de email...")
    
    try:
        import enviarEmail
        print("✅ Módulo de email importado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no módulo de email: {e}")
        traceback.print_exc()
        return False

def create_debug_script():
    """Cria script de debug para executar no executável"""
    print("\n📝 Criando script de debug...")
    
    debug_content = '''#!/usr/bin/env python3
"""
Script de debug para executável
"""

import sys
import traceback

def main():
    print("🚀 Debug do Executável - Sistema de Rotas")
    print("=" * 50)
    
    try:
        # Testar importações básicas
        print("🔍 Testando importações básicas...")
        
        import os
        print("✅ os")
        
        import sys
        print("✅ sys")
        
        import time
        print("✅ time")
        
        import threading
        print("✅ threading")
        
        import datetime
        print("✅ datetime")
        
        import random
        print("✅ random")
        
        # Testar PySimpleGUI
        print("\\n🖥️  Testando PySimpleGUI...")
        import PySimpleGUI as sg
        print("✅ PySimpleGUI importado")
        print(f"   Versão: {sg.version}")
        
        # Testar Selenium
        print("\\n🌐 Testando Selenium...")
        from selenium import webdriver
        print("✅ Selenium importado")
        
        # Testar outras dependências
        print("\\n📦 Testando outras dependências...")
        import pandas as pd
        print("✅ pandas")
        
        import numpy as np
        print("✅ numpy")
        
        import unidecode
        print("✅ unidecode")
        
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup")
        
        import requests
        print("✅ requests")
        
        import lxml
        print("✅ lxml")
        
        # Testar módulos locais
        print("\\n🏠 Testando módulos locais...")
        
        import config
        print("✅ config")
        
        import enviarEmail
        print("✅ enviarEmail")
        
        import fazendoLogin
        print("✅ fazendoLogin")
        
        import ListandoRotas2
        print("✅ ListandoRotas2")
        
        # Testar banco de dados
        print("\\n🗄️  Testando banco de dados...")
        import model.db as db
        dados = db.DADOS()
        print("✅ Banco de dados")
        
        print("\\n" + "=" * 50)
        print("✅ Todos os testes passaram!")
        print("🎯 O executável está funcionando corretamente.")
        
    except Exception as e:
        print(f"\\n❌ Erro durante debug: {e}")
        print("\\n🔍 Traceback completo:")
        traceback.print_exc()
        
        print("\\n🔧 Dicas para resolver:")
        print("1. Verifique se todas as dependências estão instaladas")
        print("2. Confirme se os arquivos estão na pasta correta")
        print("3. Verifique se o banco de dados está acessível")
        print("4. Teste a conexão com a internet")
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\\n❌ Debug falhou!")
        input("Pressione Enter para sair...")
        sys.exit(1)
    else:
        input("\\n✅ Debug concluído! Pressione Enter para sair...")
'''
    
    with open('debug_executavel.py', 'w', encoding='utf-8') as f:
        f.write(debug_content)
    
    print("✅ Script debug_executavel.py criado")

def main():
    """Função principal"""
    print("🚀 Debug do Sistema - MadeForte")
    print("=" * 50)
    
    # Testar importações
    failed_imports = test_imports()
    
    # Testar acesso aos arquivos
    failed_files = test_file_access()
    
    # Testar banco de dados
    db_ok = test_database_connection()
    
    # Testar interface gráfica
    gui_ok = test_gui_creation()
    
    # Testar Selenium
    selenium_ok = test_selenium_components()
    
    # Testar email
    email_ok = test_email_functionality()
    
    # Criar script de debug
    create_debug_script()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"   Importações: {'❌' if failed_imports else '✅'}")
    print(f"   Arquivos: {'❌' if failed_files else '✅'}")
    print(f"   Banco de dados: {'❌' if not db_ok else '✅'}")
    print(f"   Interface gráfica: {'❌' if not gui_ok else '✅'}")
    print(f"   Selenium: {'❌' if not selenium_ok else '✅'}")
    print(f"   Email: {'❌' if not email_ok else '✅'}")
    
    if failed_imports or failed_files or not all([db_ok, gui_ok, selenium_ok, email_ok]):
        print("\n❌ Alguns testes falharam!")
        print("\n🔧 Para resolver:")
        print("1. Execute: python debug_executavel.py")
        print("2. Verifique os erros específicos")
        print("3. Use o script build_exe.py para build otimizado")
        return False
    else:
        print("\n✅ Todos os testes passaram!")
        print("🎯 O sistema está pronto para build!")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Debug falhou!")
        sys.exit(1)
