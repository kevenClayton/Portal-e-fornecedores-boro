#!/usr/bin/env python3
"""
Script de teste para verificar envio de emails com caracteres especiais
"""

import enviarEmail
import logging

def test_email_encoding():
    """Testa envio de email com caracteres especiais"""
    print("🧪 Testando envio de email com caracteres especiais...")
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Teste 1: Texto com acentos
    try:
        print("📧 Teste 1: Email com acentos...")
        enviarEmail.enviarEmailGenerico(
            "Teste de Codificação - Acentos", 
            "Este é um teste com acentos: não, está, vinculação, motorista"
        )
        print("✅ Teste 1 passou!")
    except Exception as e:
        print(f"❌ Teste 1 falhou: {e}")
        return False
    
    # Teste 2: Texto sem acentos (como no código corrigido)
    try:
        print("📧 Teste 2: Email sem acentos...")
        enviarEmail.enviarEmailGenerico(
            "Teste de Codificacao - Sem Acentos", 
            "Este e um teste sem acentos: nao, esta, vinculacao, motorista"
        )
        print("✅ Teste 2 passou!")
    except Exception as e:
        print(f"❌ Teste 2 falhou: {e}")
        return False
    
    # Teste 3: Texto com caracteres especiais
    try:
        print("📧 Teste 3: Email com caracteres especiais...")
        enviarEmail.enviarEmailGenerico(
            "Teste de Codificação - Caracteres Especiais", 
            "Teste com caracteres: ç, ã, õ, é, ê, ó, ô, ú, ü"
        )
        print("✅ Teste 3 passou!")
    except Exception as e:
        print(f"❌ Teste 3 falhou: {e}")
        return False
    
    return True

def test_email_functions():
    """Testa todas as funções de email"""
    print("\n🧪 Testando todas as funções de email...")
    
    # Teste enviarEmailRotaVinculada
    try:
        print("📧 Teste: enviarEmailRotaVinculada...")
        motorista_teste = [1, "ABC1234", "123.456.789-00", "João Silva"]
        enviarEmail.enviarEmailRotaVinculada(motorista_teste, "DOC123456")
        print("✅ enviarEmailRotaVinculada passou!")
    except Exception as e:
        print(f"❌ enviarEmailRotaVinculada falhou: {e}")
        return False
    
    # Teste enviarEmailRotaComDestinoDiferente
    try:
        print("📧 Teste: enviarEmailRotaComDestinoDiferente...")
        enviarEmail.enviarEmailRotaComDestinoDiferente("DOC789012")
        print("✅ enviarEmailRotaComDestinoDiferente passou!")
    except Exception as e:
        print(f"❌ enviarEmailRotaComDestinoDiferente falhou: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Teste de Email - Sistema de Rotas")
    print("=" * 50)
    
    # Teste de codificação
    if not test_email_encoding():
        print("\n❌ Testes de codificação falharam!")
        return False
    
    # Teste de funções
    if not test_email_functions():
        print("\n❌ Testes de funções falharam!")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes de email passaram!")
    print("🎯 O problema de codificação foi resolvido.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Dicas para resolver problemas:")
        print("1. Verifique se o servidor SMTP está acessível")
        print("2. Confirme se as credenciais estão corretas")
        print("3. Verifique se o banco de dados está funcionando")
        print("4. Teste a conexão com a internet")
