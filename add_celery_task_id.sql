-- Script para adicionar o campo celery_task_id na tabela task_executions
-- Execute este script se a tabela já existir sem o campo

-- Verificar se o campo celery_task_id existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'task_executions' 
        AND column_name = 'celery_task_id'
    ) THEN
        -- Adicionar o campo se não existir
        ALTER TABLE task_executions ADD COLUMN celery_task_id VARCHAR(100);
        
        -- Adicionar índice para melhor performance
        CREATE INDEX IF NOT EXISTS idx_task_executions_celery_task_id ON task_executions(celery_task_id);
        
        RAISE NOTICE 'Campo celery_task_id adicionado com sucesso na tabela task_executions';
    ELSE
        RAISE NOTICE 'Campo celery_task_id já existe na tabela task_executions';
    END IF;
END $$;
