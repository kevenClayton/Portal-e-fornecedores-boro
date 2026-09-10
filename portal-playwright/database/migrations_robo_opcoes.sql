-- Opções de ciclo do robô (espera + bobina)
-- Uso: mysql -h HOST -u USER -p DB_NAME < database/migrations_robo_opcoes.sql

SET NAMES utf8mb4;
SET @db_name := DATABASE();

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db_name AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'verificar_bobina'
);
SET @sql_stmt := IF(
  @col_exists = 0,
  'ALTER TABLE parametros ADD COLUMN verificar_bobina BOOLEAN NOT NULL DEFAULT TRUE COMMENT ''Abrir itens da carga e checar letra B''',
  'SELECT 1'
);
PREPARE stmt FROM @sql_stmt; EXECUTE stmt; DEALLOCATE PREPARE stmt;
