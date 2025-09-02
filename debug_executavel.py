#!/usr/bin/env python3
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
        print("\n🖥️  Testando PySimpleGUI...")
        import PySimpleGUI as sg
        print("✅ PySimpleGUI importado")
        print(f"   Versão: {sg.version}")
        
        # Testar Selenium
        print("\n🌐 Testando Selenium...")
        from selenium import webdriver
        print("✅ Selenium importado")
        
        # Testar outras dependências
        print("\n📦 Testando outras dependências...")
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
        print("\n🏠 Testando módulos locais...")
        
        import config
        print("✅ config")
        
        import enviarEmail
        print("✅ enviarEmail")
        
        import fazendoLogin
        print("✅ fazendoLogin")
        
        import ListandoRotas2
        print("✅ ListandoRotas2")
        
        # Testar banco de dados
        print("\n🗄️  Testando banco de dados...")
        import model.db as db
        dados = db.DADOS()
        print("✅ Banco de dados")
        
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram!")
        print("🎯 O executável está funcionando corretamente.")
        
    except Exception as e:
        print(f"\n❌ Erro durante debug: {e}")
        print("\n🔍 Traceback completo:")
        traceback.print_exc()
        
        print("\n🔧 Dicas para resolver:")
        print("1. Verifique se todas as dependências estão instaladas")
        print("2. Confirme se os arquivos estão na pasta correta")
        print("3. Verifique se o banco de dados está acessível")
        print("4. Teste a conexão com a internet")
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Debug falhou!")
        input("Pressione Enter para sair...")
        sys.exit(1)
    else:
        input("\n✅ Debug concluído! Pressione Enter para sair...")
