-- Flags de abertura de detalhes da carga
-- Uso: mysql -h HOST -u USER -p DB_NAME < database/migrations_detalhes_flags.sql

SET NAMES utf8mb4;
SET @db_name := DATABASE();

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'verificar_valor_carga'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN verificar_valor_carga BOOLEAN NOT NULL DEFAULT TRUE COMMENT ''Abrir obs e ler valor da carga''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'verificar_multiplos_destinos'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN verificar_multiplos_destinos BOOLEAN NOT NULL DEFAULT TRUE COMMENT ''Abrir remessas e checar multiplos destinos''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- garantir bobina (caso migration anterior nao tenha rodado)
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'verificar_bobina'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN verificar_bobina BOOLEAN NOT NULL DEFAULT TRUE COMMENT ''Abrir itens e checar letra B''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;
