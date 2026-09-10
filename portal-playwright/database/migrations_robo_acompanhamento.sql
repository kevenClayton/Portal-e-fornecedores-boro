-- Acompanhamento do robô (status + timeline + pedido de screenshot)
-- Uso: mysql -h HOST -u USER -p DB_NAME < database/migrations_robo_acompanhamento.sql

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS robo_acompanhamento (
    id                  TINYINT UNSIGNED NOT NULL PRIMARY KEY DEFAULT 1,
    etapa               VARCHAR(40) NOT NULL DEFAULT 'parado',
    mensagem            VARCHAR(500) NOT NULL DEFAULT '',
    cluster_atual       VARCHAR(255) NULL,
    documento_atual     VARCHAR(100) NULL,
    resumo_ciclo        VARCHAR(255) NULL,
    screenshot_em       DATETIME NULL,
    pedir_screenshot    TINYINT(1) NOT NULL DEFAULT 0,
    atualizado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO robo_acompanhamento (id, etapa, mensagem)
VALUES (1, 'parado', 'Aguardando início')
ON DUPLICATE KEY UPDATE id = id;

CREATE TABLE IF NOT EXISTS robo_eventos (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    etapa               VARCHAR(40) NOT NULL DEFAULT 'info',
    mensagem            VARCHAR(500) NOT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_robo_eventos_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
