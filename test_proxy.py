#!/usr/bin/env python3
"""
Script de teste para verificar configuração de proxy
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from proxy_extension import setup_proxy_with_extension, cleanup_proxy_extension

def test_proxy_connection():
    """Testa conexão com proxy"""
    print("🔍 Testando configuração de proxy...")
    
    # Carregar proxy
    try:
        with open('proxies.txt') as f:
            proxies = [line.strip() for line in f if line.strip()]
        
        if not proxies:
            print("❌ Nenhum proxy encontrado no arquivo proxies.txt")
            return False
        
        proxy = random.choice(proxies)
        print(f"📡 Proxy selecionado: {proxy.split(':')[0] if ':' in proxy else proxy}")
        
        if len(proxy.split(':')) != 4:
            print("❌ Formato de proxy inválido. Esperado: IP:PORTA:USUARIO:SENHA")
            return False
        
        proxy_parts = proxy.split(':')
        proxy_host = proxy_parts[0]
        proxy_port = proxy_parts[1]
        proxy_user = proxy_parts[2]
        proxy_pass = proxy_parts[3]
        
        print(f"   Host: {proxy_host}")
        print(f"   Porta: {proxy_port}")
        print(f"   Usuário: {proxy_user}")
        print(f"   Senha: {'*' * len(proxy_pass)}")
        
    except FileNotFoundError:
        print("❌ Arquivo proxies.txt não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar proxy: {e}")
        return False
    
    # Configurar Chrome
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Configurar proxy com extensão
    options = setup_proxy_with_extension(options, proxy_host, proxy_port, proxy_user, proxy_pass)
    
    driver = None
    try:
        print("🚀 Iniciando Chrome com proxy...")
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        
        # Testar conexão
        print("🌐 Testando conexão...")
        driver.get("https://httpbin.org/ip")
        time.sleep(3)
        
        # Verificar se a página carregou
        if "origin" in driver.page_source.lower():
            print("✅ Conexão com proxy estabelecida com sucesso!")
            
            # Mostrar IP atual
            try:
                ip_element = driver.find_element("tag name", "pre")
                print(f"📡 IP atual: {ip_element.text}")
            except:
                print("ℹ️  Não foi possível obter o IP atual")
            
            return True
        else:
            print("❌ Falha ao carregar página de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False
    finally:
        if driver:
            driver.quit()
        cleanup_proxy_extension()

def main():
    """Função principal"""
    print("🚀 Teste de Proxy - Sistema de Rotas")
    print("=" * 40)
    
    success = test_proxy_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Teste de proxy concluído com sucesso!")
        print("🎯 O proxy está funcionando corretamente.")
    else:
        print("❌ Teste de proxy falhou!")
        print("🔧 Verifique:")
        print("   - Arquivo proxies.txt existe e tem formato correto")
        print("   - Credenciais do proxy estão corretas")
        print("   - Conexão com internet está funcionando")
    
    return success

if __name__ == "__main__":
    main()
