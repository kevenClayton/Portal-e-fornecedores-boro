-- Migração de dados do banco legado para o schema v2
-- Ajuste os nomes dos bancos conforme necessário

-- Exemplo: copiar motoristas do banco antigo
-- INSERT INTO portal_fornecedores.motoristas (placa, cpf, nome, aceita_bobina, situacao, ordem_motorista, placa_carreta)
-- SELECT placa, cpf, nome, aceita_bobina, situacao, ordem_motorista, placa_carreta
-- FROM boro.motoristas;

-- Mapeamento de colunas legado → v2:
--
-- parametros[0][1]  → parametros.limite_valor_truck
-- parametros[0][3]  → parametros.limite_valor_carreta
-- parametros[0][4]  → parametros.modo_teste  (0=produção/FALSE, !=0=teste/TRUE)
-- parametros[0][5]  → parametros.email_notificacao
--
-- relatorios.observacoesRota → relatorios.observacoes_rota
-- relatorios.maisDeUmCliente → relatorios.mais_de_um_cliente

-- Script para importar parâmetros do banco legado:
/*
INSERT INTO portal_fornecedores.parametros
  (limite_valor_truck, limite_valor_toco, limite_valor_carreta, modo_teste, email_notificacao)
SELECT
  p.col2,  -- ajustar índice conforme schema legado
  0,
  p.col4,
  CASE WHEN p.col5 = 0 THEN FALSE ELSE TRUE END,
  p.col6
FROM boro.parametros p
LIMIT 1;
*/
