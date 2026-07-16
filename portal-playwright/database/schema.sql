-- Schema do Portal E-Fornecedores v2
-- Execute: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS portal_fornecedores
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE portal_fornecedores;

-- Credenciais do portal
CREATE TABLE IF NOT EXISTS login (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    usuario     VARCHAR(100) NOT NULL,
    senha       VARCHAR(255) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Parâmetros de operação
CREATE TABLE IF NOT EXISTS parametros (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    limite_valor_truck      DECIMAL(12,2) NOT NULL DEFAULT 0,
    limite_valor_toco       DECIMAL(12,2) NOT NULL DEFAULT 0,
    limite_valor_carreta    DECIMAL(12,2) NOT NULL DEFAULT 0,
    modo_teste              BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'TRUE = não vincula de verdade',
    email_notificacao       VARCHAR(255) NOT NULL DEFAULT '',
    intervalo_espera_seg    INT NOT NULL DEFAULT 30,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Plantas de origem
CREATE TABLE IF NOT EXISTS origens (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome_origem VARCHAR(150) NOT NULL UNIQUE,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Clusters / destinos
CREATE TABLE IF NOT EXISTS destinos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome_destino VARCHAR(150) NOT NULL UNIQUE,
    ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tipos de veículo
CREATE TABLE IF NOT EXISTS tipo_veiculo (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    nome_tipo_veiculo VARCHAR(50) NOT NULL UNIQUE,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Motoristas
CREATE TABLE IF NOT EXISTS motoristas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    placa           VARCHAR(10) NOT NULL,
    cpf             VARCHAR(14) NOT NULL,
    nome            VARCHAR(200) NOT NULL,
    aceita_bobina   BOOLEAN NOT NULL DEFAULT FALSE,
    situacao        BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'TRUE = disponível',
    ordem_motorista INT NOT NULL DEFAULT 100,
    placa_carreta   VARCHAR(10) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_motoristas_situacao (situacao, ordem_motorista),
    INDEX idx_motoristas_placa (placa)
) ENGINE=InnoDB;

-- Relacionamentos N:N
CREATE TABLE IF NOT EXISTS motorista_origem (
    motorista_id INT NOT NULL,
    origem_id    INT NOT NULL,
    PRIMARY KEY (motorista_id, origem_id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    FOREIGN KEY (origem_id) REFERENCES origens(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motorista_destino (
    motorista_id INT NOT NULL,
    destino_id   INT NOT NULL,
    PRIMARY KEY (motorista_id, destino_id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    FOREIGN KEY (destino_id) REFERENCES destinos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo (
    motorista_id    INT NOT NULL,
    tipo_veiculo_id INT NOT NULL,
    PRIMARY KEY (motorista_id, tipo_veiculo_id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_veiculo_id) REFERENCES tipo_veiculo(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo_carreta (
    motorista_id    INT NOT NULL,
    tipo_veiculo_id INT NOT NULL,
    PRIMARY KEY (motorista_id, tipo_veiculo_id),
    FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_veiculo_id) REFERENCES tipo_veiculo(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Cargas vinculadas com sucesso
CREATE TABLE IF NOT EXISTS rotas (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    origem_rota        VARCHAR(150) NOT NULL,
    destino_rota       VARCHAR(150) NOT NULL,
    doc_transporte     VARCHAR(50) NOT NULL UNIQUE,
    data_hora_chegada  VARCHAR(50) NOT NULL,
    valor_carga        VARCHAR(30) NOT NULL DEFAULT '',
    motorista_rota     VARCHAR(200) NOT NULL,
    tipo_veiculo       VARCHAR(50) NOT NULL,
    situacao           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rotas_doc (doc_transporte),
    INDEX idx_rotas_created (created_at)
) ENGINE=InnoDB;

-- Cargas rejeitadas / incompatíveis
CREATE TABLE IF NOT EXISTS relatorios (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    origem_rota        VARCHAR(150) NOT NULL,
    destino_rota       VARCHAR(150) NOT NULL,
    doc_transporte     VARCHAR(50) NOT NULL UNIQUE,
    data_hora_chegada  VARCHAR(50) NOT NULL,
    valor_carga        VARCHAR(30) NOT NULL DEFAULT '',
    peso_total         VARCHAR(30) NOT NULL DEFAULT '',
    tipo_veiculo       VARCHAR(50) NOT NULL,
    observacoes_rota   TEXT,
    prioridade         VARCHAR(30) NOT NULL DEFAULT '',
    clientes           TEXT,
    mais_de_um_cliente BOOLEAN NOT NULL DEFAULT FALSE,
    motivo             VARCHAR(255) NOT NULL,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_relatorios_doc (doc_transporte),
    INDEX idx_relatorios_motivo (motivo)
) ENGINE=InnoDB;

-- Controle de documentos já processados na sessão
CREATE TABLE IF NOT EXISTS rotas_processadas (
    doc_transporte VARCHAR(50) PRIMARY KEY,
    processado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_processadas_data (processado_em)
) ENGINE=InnoDB;

-- Dados iniciais de exemplo
INSERT INTO parametros (limite_valor_truck, limite_valor_toco, limite_valor_carreta, modo_teste, email_notificacao)
VALUES (5000.00, 3000.00, 8000.00, TRUE, 'operacao@exemplo.com');

INSERT INTO tipo_veiculo (nome_tipo_veiculo) VALUES
    ('Truck'),
    ('Carreta'),
    ('Toco');

INSERT INTO login (usuario, senha) VALUES ('seu_usuario', 'sua_senha');
