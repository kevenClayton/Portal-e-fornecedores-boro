-- WhatsApp + página pública de detalhes da carga
-- Uso: mysql -h HOST -u USER -p DB_NAME < database/migrations_whatsapp.sql

SET NAMES utf8mb4;

-- Colunas em parametros (idempotente via information_schema)
SET @db_name := DATABASE();

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'whatsapp_telefones'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN whatsapp_telefones TEXT NULL COMMENT ''Telefones WhatsApp (virgula/linha)''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'whatsapp_codigo_estabelecimento'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN whatsapp_codigo_estabelecimento INT NULL DEFAULT NULL',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'painel_url_publica'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN painel_url_publica VARCHAR(255) NULL DEFAULT NULL COMMENT ''Ex: https://madeforte.reservaai.com.br''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;

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

-- Default útil para MadeForte (ajuste no painel se necessário)
UPDATE parametros
SET painel_url_publica = COALESCE(NULLIF(painel_url_publica, ''), 'https://madeforte.reservaai.com.br')
WHERE id > 0;
