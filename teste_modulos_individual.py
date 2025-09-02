#!/usr/bin/env python3
"""
Teste individual de cada módulo - Identifica qual está falhando
"""

import sys
import os

def testar_modulo(nome_modulo, descricao):
    """Testa um módulo específico"""
    try:
        __import__(nome_modulo)
        print(f"✅ {descricao}")
        return True
    except ImportError as e:
        print(f"❌ {descricao} - {e}")
        return False
    except Exception as e:
        print(f"❌ {descricao} - Erro: {e}")
        return False

def main():
    """Testa cada módulo individualmente"""
    print("🔍 Teste Individual de Módulos")
    print("=" * 40)
    
    modulos = [
        ('tkinter', 'Tkinter (Interface)'),
        ('FreeSimpleGUI', 'FreeSimpleGUI'),
        ('selenium', 'Selenium (WebDriver)'),
        ('pandas', 'Pandas (Dados)'),
        ('numpy', 'NumPy (Matemática)'),
        ('bs4', 'BeautifulSoup (HTML)'),
        ('webdriver_manager', 'WebDriver Manager'),
        ('mysql.connector', 'MySQL Connector'),
        ('pymysql', 'PyMySQL'),
        ('sqlite3', 'SQLite3'),
        ('requests', 'Requests (HTTP)'),
        ('lxml', 'LXML (Parser)'),
        ('unidecode', 'Unidecode'),
    ]
    
    sucessos = 0
    total = len(modulos)
    
    for nome_modulo, descricao in modulos:
        if testar_modulo(nome_modulo, descricao):
            sucessos += 1
    
    print(f"\n📊 Resultado: {sucessos}/{total} módulos funcionando")
    
    if sucessos == total:
        print("✅ Todos os módulos estão funcionando!")
        print("💡 O problema está no PyInstaller")
    else:
        print("❌ Alguns módulos falharam!")
        print("💡 Instale os módulos faltando primeiro")

if __name__ == "__main__":
    main()
