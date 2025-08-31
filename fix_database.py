#!/usr/bin/env python3
"""
Script para verificar e corrigir a estrutura da tabela task_executions
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://portal_user:portal_password@localhost:5432/boro_portal')

def check_and_fix_table():
    """Verifica e corrige a estrutura da tabela task_executions"""
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar se a tabela existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'task_executions'
                );
            """))
            
            if not result.scalar():
                print("❌ Tabela task_executions não existe!")
                return False
            
            print("✅ Tabela task_executions existe")
            
            # Verificar se o campo celery_task_id existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'task_executions' 
                    AND column_name = 'celery_task_id'
                );
            """))
            
            if not result.scalar():
                print("⚠️  Campo celery_task_id não existe. Adicionando...")
                
                # Adicionar o campo
                conn.execute(text("""
                    ALTER TABLE task_executions 
                    ADD COLUMN celery_task_id VARCHAR(100);
                """))
                
                # Adicionar índice
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_task_executions_celery_task_id 
                    ON task_executions(celery_task_id);
                """))
                
                conn.commit()
                print("✅ Campo celery_task_id adicionado com sucesso!")
            else:
                print("✅ Campo celery_task_id já existe")
            
            # Mostrar estrutura da tabela
            print("\n📋 Estrutura da tabela task_executions:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'task_executions'
                ORDER BY ordinal_position;
            """))
            
            for row in result:
                print(f"  - {row.column_name}: {row.data_type} ({'NULL' if row.is_nullable == 'YES' else 'NOT NULL'})")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando e corrigindo estrutura da tabela task_executions...")
    
    if check_and_fix_table():
        print("\n✅ Verificação concluída com sucesso!")
    else:
        print("\n❌ Falha na verificação!")
        sys.exit(1)
