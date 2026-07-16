-- Dados de exemplo para testes locais
USE portal_fornecedores;

INSERT IGNORE INTO destinos (nome_destino) VALUES
  ('São Paulo'),
  ('Belo Horizonte'),
  ('Contagem');

INSERT IGNORE INTO origens (nome_origem) VALUES
  ('Usiminas Ipatinga'),
  ('Usiminas Cubatão');

-- Motorista de exemplo (ajuste conforme necessário)
INSERT IGNORE INTO motoristas (placa, cpf, nome, aceita_bobina, situacao, ordem_motorista)
VALUES ('ABC1D23', '12345678901', 'Motorista Teste', TRUE, TRUE, 1);

-- Vincular motorista ao destino e tipo veículo
INSERT IGNORE INTO motorista_destino (motorista_id, destino_id)
SELECT m.id, d.id FROM motoristas m, destinos d
WHERE m.placa = 'ABC1D23' AND d.nome_destino = 'São Paulo';

INSERT IGNORE INTO motorista_tipo_veiculo (motorista_id, tipo_veiculo_id)
SELECT m.id, tv.id FROM motoristas m, tipo_veiculo tv
WHERE m.placa = 'ABC1D23' AND tv.nome_tipo_veiculo = 'Truck';
