-- Multi-tenant: clientes + cliente_id + super admin
-- Idempotente para MySQL 8 / MariaDB

SET @db := DATABASE();

-- 1) Tabela clientes
CREATE TABLE IF NOT EXISTS clientes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  slug VARCHAR(80) NOT NULL,
  cor_primaria VARCHAR(7) NOT NULL DEFAULT '#0d7a6f',
  cor_accent VARCHAR(7) NOT NULL DEFAULT '#0a635a',
  max_robos TINYINT UNSIGNED NOT NULL DEFAULT 1,
  containers VARCHAR(500) NULL COMMENT 'CSV nomes docker, ex: portal-fornecedores,portal-fornecedores-2',
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NULL,
  updated_at DATETIME NULL,
  UNIQUE KEY uq_clientes_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO clientes (id, nome, slug, cor_primaria, cor_accent, max_robos, containers, ativo, created_at, updated_at)
SELECT 1, 'MadeForte', 'madeforte', '#0d7a6f', '#0a635a', 2,
       'portal-fornecedores,portal-fornecedores-2,portal-fornecedores-3', 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM clientes WHERE id = 1);

-- 2) users
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='users' AND COLUMN_NAME='is_super_admin'),
    'SELECT 1',
    'ALTER TABLE users ADD COLUMN is_super_admin TINYINT(1) NOT NULL DEFAULT 0 AFTER password'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='users' AND COLUMN_NAME='cliente_id'),
    'SELECT 1',
    'ALTER TABLE users ADD COLUMN cliente_id BIGINT UNSIGNED NULL AFTER is_super_admin'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 3) Helper procedure-like adds for cliente_id on tables
-- parametros
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE parametros ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE parametros SET cliente_id = 1 WHERE cliente_id IS NULL;

-- login
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='login' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE login ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE login SET cliente_id = 1 WHERE cliente_id IS NULL;

-- motoristas
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='motoristas' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE motoristas ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE motoristas SET cliente_id = 1 WHERE cliente_id IS NULL;

-- origens
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='origens' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE origens ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE origens SET cliente_id = 1 WHERE cliente_id IS NULL;

-- destinos
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='destinos' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE destinos ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE destinos SET cliente_id = 1 WHERE cliente_id IS NULL;

-- tipo_veiculo
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='tipo_veiculo' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE tipo_veiculo ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE tipo_veiculo SET cliente_id = 1 WHERE cliente_id IS NULL;

-- rotas
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='rotas' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE rotas ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE rotas SET cliente_id = 1 WHERE cliente_id IS NULL;

-- relatorios
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='relatorios' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE relatorios ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE relatorios SET cliente_id = 1 WHERE cliente_id IS NULL;

-- notificacoes_carga
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='notificacoes_carga' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE notificacoes_carga ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE notificacoes_carga SET cliente_id = 1 WHERE cliente_id IS NULL;

-- robo_eventos
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='robo_eventos' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE robo_eventos ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE robo_eventos SET cliente_id = 1 WHERE cliente_id IS NULL;

-- robo_acompanhamento
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='robo_acompanhamento' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE robo_acompanhamento ADD COLUMN cliente_id BIGINT UNSIGNED NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE robo_acompanhamento SET cliente_id = 1 WHERE cliente_id IS NULL;

-- robo_acompanhamento: id auto + 1 linha por cliente
-- (antes era TINYINT PK fixo = 1)
SET @sql := (
  SELECT IF(
    EXISTS(
      SELECT 1 FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA=@db AND TABLE_NAME='robo_acompanhamento'
        AND COLUMN_NAME='id' AND EXTRA LIKE '%auto_increment%'
    ),
    'SELECT 1',
    'ALTER TABLE robo_acompanhamento MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='robo_acompanhamento' AND INDEX_NAME='uq_robo_acompanhamento_cliente'),
    'SELECT 1',
    'ALTER TABLE robo_acompanhamento ADD UNIQUE KEY uq_robo_acompanhamento_cliente (cliente_id)'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rotas_processadas
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='rotas_processadas' AND COLUMN_NAME='cliente_id'),'SELECT 1','ALTER TABLE rotas_processadas ADD COLUMN cliente_id BIGINT UNSIGNED NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE rotas_processadas SET cliente_id = 1 WHERE cliente_id IS NULL;

-- rotas_processadas: PK composta (cliente_id, doc_transporte)
SET @pk := (
  SELECT GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA=@db AND TABLE_NAME='rotas_processadas' AND INDEX_NAME='PRIMARY'
);
SET @sql := IF(
  @pk = 'doc_transporte',
  'ALTER TABLE rotas_processadas DROP PRIMARY KEY, ADD PRIMARY KEY (cliente_id, doc_transporte)',
  'SELECT 1'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
