#!/usr/bin/env python3
"""
Script para testar se as credenciais do portal estão sendo carregadas do banco
"""

import os
import sys
from app.services.database_service import DatabaseService

def testar_credenciais_portal():
    """Testar se as credenciais do portal estão sendo carregadas do banco"""
    
    print("🔍 Testando carregamento de credenciais do portal...")
    
    try:
        db_service = DatabaseService()
        
        # Obter credenciais do banco
        credenciais = db_service.obter_credenciais_portal()
        
        if not credenciais:
            print("❌ Nenhuma credencial encontrada na tabela 'login'")
            print("\n💡 Verifique:")
            print("  - Se a tabela 'login' existe no banco")
            print("  - Se há registros na tabela 'login'")
            print("  - Se os campos 'login' e 'senha' estão preenchidos")
            return False
        
        usuario = credenciais.get("usuario")
        senha = credenciais.get("senha")
        
        print(f"✅ Credenciais carregadas com sucesso!")
        print(f"👤 Usuário: {usuario}")
        print(f"🔒 Senha: {'*' * len(senha) if senha else 'Não informada'}")
        
        if not usuario:
            print("⚠️  Usuário não encontrado no banco")
            return False
        
        if not senha:
            print("⚠️  Senha não encontrada no banco")
            return False
        
        print("\n✅ Credenciais válidas encontradas!")
        print("🎉 O sistema está pronto para fazer login no portal!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar credenciais: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Teste de Credenciais - Portal e-Fornecedores")
    print("=" * 50)
    
    if testar_credenciais_portal():
        print("\n✅ Teste concluído com sucesso!")
        print("🚀 O sistema pode fazer login no portal automaticamente!")
    else:
        print("\n❌ Falha no teste de credenciais!")
        print("🔧 Verifique a tabela 'login' no banco de dados.")
        sys.exit(1)
