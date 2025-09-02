#!/usr/bin/env python3
"""
Script de teste para verificar se todas as dependências estão funcionando
"""

import sys
import traceback

def test_imports():
    """Testa todas as importações necessárias"""
    print("🔍 Testando importações...")
    
    # Teste PySimpleGUI
    try:
        import PySimpleGUI as sg
        print("✅ PySimpleGUI importado com sucesso!")
        print(f"   Versão: {sg.version}")
        
        # Teste básico de elementos
        text = sg.Text("Teste")
        button = sg.Button("OK")
        print("✅ Elementos PySimpleGUI criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no PySimpleGUI: {e}")
        return False
    
    # Teste Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        print("✅ Selenium importado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no Selenium: {e}")
        return False
    
    # Teste outras dependências
    try:
        import pandas as pd
        import numpy as np
        import unidecode
        from bs4 import BeautifulSoup
        import requests
        print("✅ Todas as outras dependências importadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro em outras dependências: {e}")
        return False
    
    return True

def test_config():
    """Testa a configuração do projeto"""
    print("\n🔍 Testando configuração...")
    
    # Teste arquivo config.py
    try:
        from config import fundo, cliente
        print(f"✅ Config carregada - Cliente: {cliente}, Fundo: {fundo}")
    except Exception as e:
        print(f"❌ Erro ao carregar config: {e}")
        return False
    
    # Teste arquivo proxies.txt
    try:
        with open('proxies.txt') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"✅ Proxies carregados: {len(proxies)} proxies encontrados")
    except FileNotFoundError:
        print("⚠️  Arquivo proxies.txt não encontrado")
    except Exception as e:
        print(f"❌ Erro ao carregar proxies: {e}")
    
    return True

def test_database():
    """Testa conexão com banco de dados"""
    print("\n🔍 Testando banco de dados...")
    
    try:
        import model.db as db
        dados = db.DADOS()
        print("✅ Conexão com banco estabelecida!")
        print(f"   Login configurado: {'login' in dados}")
        print(f"   Origens: {len(dados.get('origens', []))}")
        print(f"   Motoristas: {len(dados.get('motoristas', []))}")
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False
    
    return True

def test_gui():
    """Testa interface gráfica"""
    print("\n🔍 Testando interface gráfica...")
    
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

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema...")
    print("=" * 50)
    
    # Testar importações
    if not test_imports():
        print("\n❌ Falha nos testes de importação")
        return False
    
    # Testar configuração
    if not test_config():
        print("\n❌ Falha nos testes de configuração")
        return False
    
    # Testar banco de dados
    if not test_database():
        print("\n❌ Falha nos testes de banco de dados")
        return False
    
    # Testar interface gráfica
    if not test_gui():
        print("\n❌ Falha nos testes de interface gráfica")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram! Sistema pronto para uso.")
    print("\n🎯 Para executar o programa principal:")
    print("   python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
