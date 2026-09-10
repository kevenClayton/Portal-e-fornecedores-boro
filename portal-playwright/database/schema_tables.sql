-- Tabelas do schema v2 (sem CREATE DATABASE — usa o DB atual da conexão)
-- Uso: mysql -h HOST -u USER -p DB_NAME < database/schema_tables.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS login (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    usuario     VARCHAR(100) NOT NULL,
    senha       VARCHAR(255) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS parametros (
    id                      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    limite_valor_truck      DECIMAL(12,2) NOT NULL DEFAULT 0,
    limite_valor_toco       DECIMAL(12,2) NOT NULL DEFAULT 0,
    limite_valor_carreta    DECIMAL(12,2) NOT NULL DEFAULT 0,
    modo_teste              BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'TRUE = não vincula de verdade',
    email_notificacao       VARCHAR(255) NOT NULL DEFAULT '',
    intervalo_espera_seg    INT NOT NULL DEFAULT 30,
    verificar_valor_carga   BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Abrir obs e ler valor da carga',
    verificar_bobina        BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Abrir itens da carga e checar letra B',
    verificar_multiplos_destinos BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Abrir remessas e checar multiplos destinos',
    whatsapp_telefones      TEXT NULL COMMENT 'Telefones WhatsApp (virgula/linha)',
    whatsapp_codigo_estabelecimento INT NULL DEFAULT NULL,
    painel_url_publica      VARCHAR(255) NULL DEFAULT NULL,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notificacoes_carga (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    public_id           CHAR(36) NOT NULL,
    situacao            VARCHAR(40) NOT NULL COMMENT 'aceita | perdida',
    motorista           VARCHAR(200) NOT NULL DEFAULT '',
    numero_documento    VARCHAR(100) NOT NULL,
    motivo              TEXT NULL,
    origem              VARCHAR(255) NULL,
    destino             VARCHAR(255) NULL,
    valor_carga         VARCHAR(50) NULL,
    tipo_transporte     VARCHAR(100) NULL,
    placa               VARCHAR(20) NULL,
    cpf                 VARCHAR(20) NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_notificacoes_carga_public_id (public_id),
    INDEX idx_notificacoes_carga_doc (numero_documento),
    INDEX idx_notificacoes_carga_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS origens (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome_origem VARCHAR(255) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_origens_nome (nome_origem)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS destinos (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome_destino VARCHAR(255) NOT NULL,
    ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_destinos_nome (nome_destino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tipo_veiculo (
    id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome_tipo_veiculo VARCHAR(255) NOT NULL,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tipo_veiculo_nome (nome_tipo_veiculo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS motoristas (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    placa           VARCHAR(20) NOT NULL,
    cpf             VARCHAR(20) NOT NULL,
    nome            VARCHAR(200) NOT NULL,
    aceita_bobina   BOOLEAN NOT NULL DEFAULT FALSE,
    situacao        BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'TRUE = disponível',
    ordem_motorista INT NOT NULL DEFAULT 100,
    placa_carreta   VARCHAR(20) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_motoristas_situacao (situacao, ordem_motorista),
    INDEX idx_motoristas_placa (placa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS motorista_origem (
    motorista_id BIGINT UNSIGNED NOT NULL,
    origem_id    BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (motorista_id, origem_id),
    CONSTRAINT fk_mo_motorista FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    CONSTRAINT fk_mo_origem FOREIGN KEY (origem_id) REFERENCES origens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS motorista_destino (
    motorista_id BIGINT UNSIGNED NOT NULL,
    destino_id   BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (motorista_id, destino_id),
    CONSTRAINT fk_md_motorista FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    CONSTRAINT fk_md_destino FOREIGN KEY (destino_id) REFERENCES destinos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo (
    motorista_id    BIGINT UNSIGNED NOT NULL,
    tipo_veiculo_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (motorista_id, tipo_veiculo_id),
    CONSTRAINT fk_mtv_motorista FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    CONSTRAINT fk_mtv_tipo FOREIGN KEY (tipo_veiculo_id) REFERENCES tipo_veiculo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS motorista_tipo_veiculo_carreta (
    motorista_id    BIGINT UNSIGNED NOT NULL,
    tipo_veiculo_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (motorista_id, tipo_veiculo_id),
    CONSTRAINT fk_mtvc_motorista FOREIGN KEY (motorista_id) REFERENCES motoristas(id) ON DELETE CASCADE,
    CONSTRAINT fk_mtvc_tipo FOREIGN KEY (tipo_veiculo_id) REFERENCES tipo_veiculo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rotas (
    id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    origem_rota        VARCHAR(255) NOT NULL,
    destino_rota       VARCHAR(255) NOT NULL,
    doc_transporte     VARCHAR(100) NOT NULL,
    data_hora_chegada  VARCHAR(100) NOT NULL,
    valor_carga        VARCHAR(50) NOT NULL DEFAULT '',
    motorista_rota     VARCHAR(255) NOT NULL,
    tipo_veiculo       VARCHAR(100) NOT NULL,
    situacao           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_rotas_doc (doc_transporte),
    INDEX idx_rotas_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS relatorios (
    id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    origem_rota        VARCHAR(255) NOT NULL,
    destino_rota       VARCHAR(255) NOT NULL,
    doc_transporte     VARCHAR(100) NOT NULL,
    data_hora_chegada  VARCHAR(100) NOT NULL,
    valor_carga        VARCHAR(50) NOT NULL DEFAULT '',
    peso_total         VARCHAR(50) NOT NULL DEFAULT '',
    tipo_veiculo       VARCHAR(100) NOT NULL,
    observacoes_rota   TEXT,
    prioridade         VARCHAR(100) NOT NULL DEFAULT '',
    clientes           TEXT,
    mais_de_um_cliente BOOLEAN NOT NULL DEFAULT FALSE,
    motivo             TEXT NOT NULL,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_relatorios_doc (doc_transporte),
    INDEX idx_relatorios_motivo (motivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rotas_processadas (
    doc_transporte VARCHAR(50) PRIMARY KEY,
    processado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_processadas_data (processado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
