-- Script para criar a tabela task_executions no banco MySQL existente
-- Esta tabela não existe no banco atual e será criada para o sistema de automação

CREATE TABLE IF NOT EXISTS `task_executions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `task_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `celery_task_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` timestamp NULL DEFAULT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci,
  `rotas_processadas` bigint unsigned DEFAULT '0',
  `rotas_vinculadas` bigint unsigned DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_task_executions_status` (`status`),
  KEY `idx_task_executions_created_at` (`created_at`),
  KEY `idx_task_executions_celery_task_id` (`celery_task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comentário da tabela
ALTER TABLE `task_executions` COMMENT = 'Tabela de execuções de tarefas do sistema de automação';
