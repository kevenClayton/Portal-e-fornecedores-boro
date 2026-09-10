-- Quantidade de robôs simultâneos (1–3) + defasagem de ciclo
SET NAMES utf8mb4;

SET @db := DATABASE();

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE parametros ADD COLUMN robo_quantidade TINYINT UNSIGNED NOT NULL DEFAULT 1',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @db AND TABLE_NAME = 'parametros' AND COLUMN_NAME = 'robo_quantidade'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
