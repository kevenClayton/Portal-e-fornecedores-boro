-- Auditoria leve do robô: decisões por documento + eventos de captcha
-- Retenção sugerida: 15 dias (limpeza automática no ciclo do robô)
-- Uso: mysql ... < database/migrations_robo_auditoria.sql

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS robo_auditoria (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cliente_id          BIGINT UNSIGNED NULL,
    slot                TINYINT UNSIGNED NOT NULL DEFAULT 1,
    tipo_evento         VARCHAR(40) NOT NULL COMMENT 'decisao_carga | captcha',
    doc_transporte      VARCHAR(100) NULL,
    destino             VARCHAR(255) NULL,
    tipo_veiculo        VARCHAR(80) NULL,
    decisao             VARCHAR(40) NULL COMMENT 'vinculado | pulado | rejeitado',
    motivo              VARCHAR(500) NULL,
    origem_captcha      VARCHAR(40) NULL COMMENT 'Login | Pesquisar | Filtrar',
    proxy_host          VARCHAR(80) NULL,
    tentativa           INT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auditoria_doc (doc_transporte),
    INDEX idx_auditoria_created (created_at),
    INDEX idx_auditoria_tipo_created (tipo_evento, created_at),
    INDEX idx_auditoria_cliente_created (cliente_id, created_at),
    INDEX idx_auditoria_decisao_created (decisao, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
