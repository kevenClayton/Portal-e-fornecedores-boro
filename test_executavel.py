#!/usr/bin/env python3
"""
Script de teste específico para o executável
"""

import os
import sys
import subprocess
import time
import traceback

def test_executavel_basico():
    """Testa se o executável existe e pode ser executado"""
    print("🧪 Testando executável básico...")
    
    exe_path = "dist/madeforte.exe"
    
    if not os.path.exists(exe_path):
        print(f"❌ Executável não encontrado: {exe_path}")
        return False
    
    print(f"✅ Executável encontrado: {exe_path}")
    print(f"   Tamanho: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
    
    return True

def test_executavel_execucao():
    """Testa execução do executável com timeout"""
    print("\n🚀 Testando execução do executável...")
    
    exe_path = "dist/madeforte.exe"
    
    try:
        print("   Iniciando executável...")
        
        # Executar com timeout de 30 segundos
        processo = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("   Aguardando 30 segundos para ver se inicia...")
        time.sleep(30)
        
        # Verificar se ainda está rodando
        if processo.poll() is None:
            print("   ✅ Executável ainda está rodando (bom sinal)")
            processo.terminate()
            time.sleep(2)
            if processo.poll() is None:
                processo.kill()
            return True
        else:
            # Processo terminou, verificar saída
            stdout, stderr = processo.communicate()
            print(f"   ❌ Executável terminou com código: {processo.returncode}")
            if stdout:
                print(f"   STDOUT: {stdout[:500]}...")
            if stderr:
                print(f"   STDERR: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao executar: {e}")
        traceback.print_exc()
        return False

def test_executavel_dependencias():
    """Testa se todas as dependências estão no executável"""
    print("\n🔍 Verificando dependências no executável...")
    
    exe_path = "dist/madeforte.exe"
    
    try:
        # Verificar se o executável contém strings importantes
        with open(exe_path, 'rb') as f:
            conteudo = f.read()
        
        dependencias_test = [
            b'PySimpleGUI',
            b'selenium',
            b'pandas',
            b'numpy',
            b'beautifulsoup4',
            b'requests',
            b'lxml',
            b'smtplib',
            b'threading',
            b'datetime',
            b'logging',
            b'mysql',
            b'pymysql',
        ]
        
        for dep in dependencias_test:
            if dep in conteudo:
                print(f"   ✅ {dep.decode()}")
            else:
                print(f"   ❌ {dep.decode()} - NÃO ENCONTRADO")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar dependências: {e}")
        return False

def test_executavel_arquivos():
    """Testa se todos os arquivos necessários estão incluídos"""
    print("\n📁 Verificando arquivos incluídos...")
    
    exe_path = "dist/madeforte.exe"
    
    try:
        # Verificar se o executável contém referências aos arquivos
        with open(exe_path, 'rb') as f:
            conteudo = f.read()
        
        arquivos_test = [
            b'config.py',
            b'proxies.txt',
            b'model/db.py',
            b'fazendoLogin.py',
            b'ListandoRotas2.py',
            b'enviarEmail.py',
            b'pegarValorObservacao.py',
            b'validarLetraProduto.py',
        ]
        
        for arquivo in arquivos_test:
            if arquivo in conteudo:
                print(f"   ✅ {arquivo.decode()}")
            else:
                print(f"   ❌ {arquivo.decode()} - NÃO ENCONTRADO")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar arquivos: {e}")
        return False

def criar_script_test_simples():
    """Cria um script de teste simples para verificar funcionalidades básicas"""
    print("\n📝 Criando script de teste simples...")
    
    script_content = '''#!/usr/bin/env python3
"""
Script de teste simples para verificar funcionalidades básicas
"""

import sys
import traceback

def main():
    print("🚀 Teste Simples - Sistema de Rotas")
    print("=" * 40)
    
    try:
        # Teste 1: Importações básicas
        print("\\n🔍 Teste 1: Importações básicas...")
        
        import os
        print("   ✅ os")
        
        import sys
        print("   ✅ sys")
        
        import time
        print("   ✅ time")
        
        import threading
        print("   ✅ threading")
        
        import datetime
        print("   ✅ datetime")
        
        import random
        print("   ✅ random")
        
        # Teste 2: PySimpleGUI
        print("\\n🖥️  Teste 2: PySimpleGUI...")
        try:
            import PySimpleGUI as sg
            print("   ✅ PySimpleGUI importado")
            print(f"      Versão: {sg.version}")
        except Exception as e:
            print(f"   ❌ PySimpleGUI: {e}")
            return False
        
        # Teste 3: Selenium
        print("\\n🌐 Teste 3: Selenium...")
        try:
            from selenium import webdriver
            print("   ✅ Selenium importado")
        except Exception as e:
            print(f"   ❌ Selenium: {e}")
            return False
        
        # Teste 4: Outras dependências
        print("\\n📦 Teste 4: Outras dependências...")
        try:
            import pandas as pd
            print("   ✅ pandas")
            
            import numpy as np
            print("   ✅ numpy")
            
            from bs4 import BeautifulSoup
            print("   ✅ BeautifulSoup")
            
            import requests
            print("   ✅ requests")
            
            import lxml
            print("   ✅ lxml")
        except Exception as e:
            print(f"   ❌ Dependências: {e}")
            return False
        
        # Teste 5: Módulos locais
        print("\\n🏠 Teste 5: Módulos locais...")
        try:
            import config
            print("   ✅ config")
            
            import enviarEmail
            print("   ✅ enviarEmail")
            
            import fazendoLogin
            print("   ✅ fazendoLogin")
            
            import ListandoRotas2
            print("   ✅ ListandoRotas2")
        except Exception as e:
            print(f"   ❌ Módulos locais: {e}")
            return False
        
        # Teste 6: Banco de dados
        print("\\n🗄️  Teste 6: Banco de dados...")
        try:
            import model.db as db
            dados = db.DADOS()
            print("   ✅ Banco de dados")
        except Exception as e:
            print(f"   ❌ Banco de dados: {e}")
            return False
        
        print("\\n" + "=" * 40)
        print("✅ Todos os testes passaram!")
        print("🎯 O executável está funcionando corretamente.")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Erro durante teste: {e}")
        print("\\n🔍 Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\\n❌ Teste falhou!")
        input("Pressione Enter para sair...")
        sys.exit(1)
    else:
        input("\\n✅ Teste concluído! Pressione Enter para sair...")
'''
    
    with open('teste_simples.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script teste_simples.py criado")

def main():
    """Função principal"""
    print("🚀 Teste do Executável - MadeForte")
    print("=" * 50)
    
    # Verificar se o executável existe
    if not test_executavel_basico():
        print("\n❌ Executável não encontrado!")
        print("🔧 Execute primeiro: python build_exe.py")
        return False
    
    # Testar dependências
    test_executavel_dependencias()
    
    # Testar arquivos incluídos
    test_executavel_arquivos()
    
    # Testar execução
    execucao_ok = test_executavel_execucao()
    
    # Criar script de teste simples
    criar_script_test_simples()
    
    print("\n" + "=" * 50)
    if execucao_ok:
        print("✅ Executável parece estar funcionando!")
        print("🎯 Teste com: python teste_simples.py")
    else:
        print("❌ Executável não está funcionando!")
        print("\n🔧 Para resolver:")
        print("1. Execute: python build_exe.py")
        print("2. Verifique se há erros durante o build")
        print("3. Teste com: python teste_simples.py")
        print("4. Verifique logs em dist/")
    
    return execucao_ok

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Teste falhou!")
        sys.exit(1)
