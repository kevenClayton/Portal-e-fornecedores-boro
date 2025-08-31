#!/usr/bin/env python3
"""
Script para testar a conexão com o banco MySQL
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/boro')

def test_mysql_connection():
    """Testa a conexão com o banco MySQL"""
    
    print("🔍 Testando conexão com o banco MySQL...")
    print(f"URL: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Testar conexão básica
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Conexão com MySQL estabelecida com sucesso!")
            
            # Verificar se o banco existe
            result = conn.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.scalar()
            print(f"📊 Banco atual: {current_db}")
            
            # Listar tabelas existentes
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tabelas encontradas: {len(tables)}")
            
            # Verificar tabelas principais
            main_tables = ['motoristas', 'destinos', 'origens', 'rotas', 'relatorios', 'parametros']
            for table in main_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} (não encontrada)")
            
            # Verificar se task_executions existe
            if 'task_executions' in tables:
                print("  ✅ task_executions (já existe)")
            else:
                print("  ⚠️  task_executions (será criada automaticamente)")
            
            # Testar consulta em motoristas
            try:
                result = conn.execute(text("SELECT COUNT(*) as total FROM motoristas"))
                total_motoristas = result.scalar()
                print(f"👥 Total de motoristas: {total_motoristas}")
            except Exception as e:
                print(f"⚠️  Erro ao contar motoristas: {str(e)}")
            
            # Testar consulta em destinos
            try:
                result = conn.execute(text("SELECT COUNT(*) as total FROM destinos"))
                total_destinos = result.scalar()
                print(f"📍 Total de destinos: {total_destinos}")
            except Exception as e:
                print(f"⚠️  Erro ao contar destinos: {str(e)}")
            
            return True
            
    except OperationalError as e:
        print(f"❌ Erro de conexão: {str(e)}")
        print("\n💡 Verifique:")
        print("  - Se o MySQL está rodando")
        print("  - Se as credenciais estão corretas")
        print("  - Se o banco 'boro' existe")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Teste de Conexão MySQL - Portal e-Fornecedores")
    print("=" * 50)
    
    if test_mysql_connection():
        print("\n✅ Teste concluído com sucesso!")
        print("🎉 O sistema está pronto para usar o banco MySQL existente!")
    else:
        print("\n❌ Falha no teste de conexão!")
        print("🔧 Verifique as configurações e tente novamente.")
        sys.exit(1)
