-- Alinha schema legado do Boro ao painel/robô v2
-- Host: reservaai-data.... / database: boro

SET @db := DATABASE();

-- login: usuario + ativo
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='login' AND COLUMN_NAME='usuario'),'SELECT 1','ALTER TABLE login ADD COLUMN usuario VARCHAR(100) NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
UPDATE login SET usuario = `login` WHERE (usuario IS NULL OR usuario = '') AND `login` IS NOT NULL;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='login' AND COLUMN_NAME='ativo'),'SELECT 1','ALTER TABLE login ADD COLUMN ativo TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- parametros: colunas novas + migração dos nomes legados
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='limite_valor_truck'),'SELECT 1','ALTER TABLE parametros ADD COLUMN limite_valor_truck DECIMAL(12,2) NOT NULL DEFAULT 0'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='limite_valor_toco'),'SELECT 1','ALTER TABLE parametros ADD COLUMN limite_valor_toco DECIMAL(12,2) NOT NULL DEFAULT 0'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='limite_valor_carreta'),'SELECT 1','ALTER TABLE parametros ADD COLUMN limite_valor_carreta DECIMAL(12,2) NOT NULL DEFAULT 0'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='modo_teste'),'SELECT 1','ALTER TABLE parametros ADD COLUMN modo_teste TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='email_notificacao'),'SELECT 1','ALTER TABLE parametros ADD COLUMN email_notificacao VARCHAR(255) NOT NULL DEFAULT \"\"'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='intervalo_espera_seg'),'SELECT 1','ALTER TABLE parametros ADD COLUMN intervalo_espera_seg INT NOT NULL DEFAULT 30'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='verificar_valor_carga'),'SELECT 1','ALTER TABLE parametros ADD COLUMN verificar_valor_carga TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='verificar_bobina'),'SELECT 1','ALTER TABLE parametros ADD COLUMN verificar_bobina TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='verificar_multiplos_destinos'),'SELECT 1','ALTER TABLE parametros ADD COLUMN verificar_multiplos_destinos TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='whatsapp_telefones'),'SELECT 1','ALTER TABLE parametros ADD COLUMN whatsapp_telefones TEXT NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='whatsapp_codigo_estabelecimento'),'SELECT 1','ALTER TABLE parametros ADD COLUMN whatsapp_codigo_estabelecimento INT NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='painel_url_publica'),'SELECT 1','ALTER TABLE parametros ADD COLUMN painel_url_publica VARCHAR(255) NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='robo_agenda_ativa'),'SELECT 1','ALTER TABLE parametros ADD COLUMN robo_agenda_ativa TINYINT(1) NOT NULL DEFAULT 0'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='robo_hora_ligar'),'SELECT 1','ALTER TABLE parametros ADD COLUMN robo_hora_ligar TIME NULL DEFAULT \"06:00:00\"'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='robo_hora_desligar'),'SELECT 1','ALTER TABLE parametros ADD COLUMN robo_hora_desligar TIME NULL DEFAULT \"22:00:00\"'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='parametros' AND COLUMN_NAME='robo_quantidade'),'SELECT 1','ALTER TABLE parametros ADD COLUMN robo_quantidade TINYINT UNSIGNED NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Copia valores legados → novos (quando existirem)
UPDATE parametros SET
  limite_valor_truck = COALESCE(NULLIF(limite_valor_truck, 0), valor_maximo_carga_truck, 0),
  limite_valor_toco = COALESCE(NULLIF(limite_valor_toco, 0), valor_maximo_carga_bi_truck, 0),
  limite_valor_carreta = COALESCE(NULLIF(limite_valor_carreta, 0), valor_maximo_carga_carreta_truck, 0),
  modo_teste = COALESCE(moto_teste, modo_teste, 0),
  email_notificacao = COALESCE(NULLIF(email_notificacao, ''), emails_notificacao, '')
WHERE id > 0;

-- destinos.ativo / origens.ativo
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='destinos' AND COLUMN_NAME='ativo'),'SELECT 1','ALTER TABLE destinos ADD COLUMN ativo TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='origens' AND COLUMN_NAME='ativo'),'SELECT 1','ALTER TABLE origens ADD COLUMN ativo TINYINT(1) NOT NULL DEFAULT 1'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- motoristas.placa_carreta
SET @sql := (SELECT IF(EXISTS(SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='motoristas' AND COLUMN_NAME='placa_carreta'),'SELECT 1','ALTER TABLE motoristas ADD COLUMN placa_carreta VARCHAR(10) NULL'));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Tabelas do robô / painel novo
CREATE TABLE IF NOT EXISTS rotas_processadas (
  doc_transporte VARCHAR(100) NOT NULL PRIMARY KEY,
  processado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS robo_acompanhamento (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  etapa VARCHAR(40) NOT NULL DEFAULT 'parado',
  mensagem VARCHAR(500) NOT NULL DEFAULT '',
  cluster_atual VARCHAR(255) NULL,
  documento_atual VARCHAR(100) NULL,
  resumo_ciclo VARCHAR(255) NULL,
  screenshot_em DATETIME NULL,
  pedir_screenshot TINYINT(1) NOT NULL DEFAULT 0,
  atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO robo_acompanhamento (id, etapa, mensagem)
SELECT 1, 'parado', 'Aguardando início'
WHERE NOT EXISTS (SELECT 1 FROM robo_acompanhamento LIMIT 1);

CREATE TABLE IF NOT EXISTS robo_eventos (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  etapa VARCHAR(40) NOT NULL DEFAULT 'info',
  mensagem VARCHAR(500) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_robo_eventos_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notificacoes_carga (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  public_id CHAR(36) NOT NULL,
  situacao VARCHAR(40) NOT NULL,
  motorista VARCHAR(200) NOT NULL DEFAULT '',
  numero_documento VARCHAR(100) NOT NULL,
  motivo TEXT NULL,
  origem VARCHAR(255) NULL,
  destino VARCHAR(255) NULL,
  valor_carga VARCHAR(50) NULL,
  tipo_transporte VARCHAR(100) NULL,
  placa VARCHAR(20) NULL,
  cpf VARCHAR(20) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_notificacoes_carga_public_id (public_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
