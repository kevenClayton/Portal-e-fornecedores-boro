-- Agenda ligar/desligar do robô (horário America/Sao_Paulo no painel)
-- Uso: mysql ... < database/migrations_robo_agenda.sql

SET NAMES utf8mb4;

-- MySQL 8 / MariaDB: ignore duplicate column errors if already applied
SET @db := DATABASE();

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE parametros ADD COLUMN robo_agenda_ativa TINYINT(1) NOT NULL DEFAULT 0',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'robo_agenda_ativa'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE parametros ADD COLUMN robo_hora_ligar TIME NULL DEFAULT ''06:00:00''',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'robo_hora_ligar'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE parametros ADD COLUMN robo_hora_desligar TIME NULL DEFAULT ''22:00:00''',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'robo_hora_desligar'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
