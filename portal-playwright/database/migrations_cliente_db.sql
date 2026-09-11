-- Credenciais de banco por cliente (banco próprio)
SET @db := DATABASE();

SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='clientes' AND COLUMN_NAME='db_host'),'SELECT 1','ALTER TABLE clientes ADD COLUMN db_host VARCHAR(255) NULL AFTER containers'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='clientes' AND COLUMN_NAME='db_port'),'SELECT 1','ALTER TABLE clientes ADD COLUMN db_port INT UNSIGNED NULL DEFAULT 3306 AFTER db_host'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='clientes' AND COLUMN_NAME='db_database'),'SELECT 1','ALTER TABLE clientes ADD COLUMN db_database VARCHAR(120) NULL AFTER db_port'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='clientes' AND COLUMN_NAME='db_username'),'SELECT 1','ALTER TABLE clientes ADD COLUMN db_username VARCHAR(120) NULL AFTER db_database'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='clientes' AND COLUMN_NAME='db_password'),'SELECT 1','ALTER TABLE clientes ADD COLUMN db_password TEXT NULL AFTER db_username'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
