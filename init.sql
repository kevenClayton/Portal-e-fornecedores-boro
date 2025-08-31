-- Script de inicialização do banco de dados PostgreSQL
-- Portal e-Fornecedores Automation

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de motoristas
CREATE TABLE IF NOT EXISTS motoristas (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(20) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    aceita_bobina BOOLEAN DEFAULT FALSE,
    situacao BOOLEAN DEFAULT TRUE,
    ordem_motorista INTEGER DEFAULT 0,
    placa_carreta VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de destinos
CREATE TABLE IF NOT EXISTS destinos (
    id SERIAL PRIMARY KEY,
    nome_destino VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de origens
CREATE TABLE IF NOT EXISTS origens (
    id SERIAL PRIMARY KEY,
    nome_origem VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de tipos de veículo
CREATE TABLE IF NOT EXISTS tipo_veiculo (
    id SERIAL PRIMARY KEY,
    nome_tipo_veiculo VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relacionamento motorista-destino
CREATE TABLE IF NOT EXISTS motorista_destino (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER REFERENCES motoristas(id) ON DELETE CASCADE,
    destino_id INTEGER REFERENCES destinos(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(motorista_id, destino_id)
);

-- Tabela de relacionamento motorista-origem
CREATE TABLE IF NOT EXISTS motorista_origem (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER REFERENCES motoristas(id) ON DELETE CASCADE,
    origem_id INTEGER REFERENCES origens(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(motorista_id, origem_id)
);

-- Tabela de relacionamento motorista-tipo_veiculo
CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER REFERENCES motoristas(id) ON DELETE CASCADE,
    tipo_veiculo_id INTEGER REFERENCES tipo_veiculo(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(motorista_id, tipo_veiculo_id)
);

-- Tabela de relacionamento motorista-tipo_veiculo_carreta
CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo_carreta (
    id SERIAL PRIMARY KEY,
    motorista_id INTEGER REFERENCES motoristas(id) ON DELETE CASCADE,
    tipo_veiculo_id INTEGER REFERENCES tipo_veiculo(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(motorista_id, tipo_veiculo_id)
);

-- Tabela de parâmetros
CREATE TABLE IF NOT EXISTS parametros (
    id SERIAL PRIMARY KEY,
    valor_carreta DECIMAL(10,2) NOT NULL,
    valor_truck DECIMAL(10,2) NOT NULL,
    modo_teste BOOLEAN DEFAULT TRUE,
    email_notificacao VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de login
CREATE TABLE IF NOT EXISTS login (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL,
    senha VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de rotas
CREATE TABLE IF NOT EXISTS rotas (
    id SERIAL PRIMARY KEY,
    origem_rota VARCHAR(100) NOT NULL,
    destino_rota VARCHAR(100) NOT NULL,
    doc_transporte VARCHAR(50) NOT NULL UNIQUE,
    data_hora_chegada VARCHAR(50),
    valor_carga VARCHAR(50),
    motorista_rota VARCHAR(100),
    tipo_veiculo VARCHAR(50),
    situacao VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relatórios
CREATE TABLE IF NOT EXISTS relatorios (
    id SERIAL PRIMARY KEY,
    origem_rota VARCHAR(100),
    destino_rota VARCHAR(100),
    doc_transporte VARCHAR(50),
    data_hora_chegada VARCHAR(50),
    valor_carga VARCHAR(50),
    peso_total VARCHAR(50),
    tipo_veiculo VARCHAR(50),
    observacoes_rota TEXT,
    prioridade VARCHAR(50),
    clientes VARCHAR(200),
    mais_de_um_cliente BOOLEAN DEFAULT FALSE,
    motivo VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de execuções de tarefas
CREATE TABLE IF NOT EXISTS task_executions (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    celery_task_id VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    rotas_processadas INTEGER DEFAULT 0,
    rotas_vinculadas INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_motoristas_situacao ON motoristas(situacao);
CREATE INDEX IF NOT EXISTS idx_motoristas_ordem ON motoristas(ordem_motorista);
CREATE INDEX IF NOT EXISTS idx_rotas_doc_transporte ON rotas(doc_transporte);
CREATE INDEX IF NOT EXISTS idx_rotas_created_at ON rotas(created_at);
CREATE INDEX IF NOT EXISTS idx_relatorios_doc_transporte ON relatorios(doc_transporte);
CREATE INDEX IF NOT EXISTS idx_relatorios_created_at ON relatorios(created_at);
CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions(status);
CREATE INDEX IF NOT EXISTS idx_task_executions_created_at ON task_executions(created_at);

-- Dados iniciais de exemplo (opcional)
INSERT INTO parametros (valor_carreta, valor_truck, modo_teste, email_notificacao) 
VALUES (5000.00, 3000.00, TRUE, 'admin@exemplo.com')
ON CONFLICT DO NOTHING;

INSERT INTO tipo_veiculo (nome_tipo_veiculo) VALUES 
('Carreta'), ('Truck')
ON CONFLICT DO NOTHING;

-- Comentários das tabelas
COMMENT ON TABLE motoristas IS 'Tabela de motoristas cadastrados no sistema';
COMMENT ON TABLE destinos IS 'Tabela de destinos disponíveis';
COMMENT ON TABLE origens IS 'Tabela de origens disponíveis';
COMMENT ON TABLE tipo_veiculo IS 'Tabela de tipos de veículo';
COMMENT ON TABLE rotas IS 'Tabela de rotas vinculadas com sucesso';
COMMENT ON TABLE relatorios IS 'Tabela de relatórios de rotas não vinculadas';
COMMENT ON TABLE task_executions IS 'Tabela de execuções de tarefas do sistema';
