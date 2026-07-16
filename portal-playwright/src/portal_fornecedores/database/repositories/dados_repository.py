from typing import List, Optional, Tuple

from portal_fornecedores.database.connection import DatabaseConnection
from portal_fornecedores.models.entidades import DadosMotorista, DadosRota, ParametrosOperacao


class DadosRepository:
  def __init__(self, db: Optional[DatabaseConnection] = None):
    self._db = db or DatabaseConnection()

  def obter_login(self) -> Tuple[str, str]:
    with self._db.cursor() as cursor:
      cursor.execute("SELECT usuario, senha FROM login WHERE ativo = TRUE LIMIT 1")
      row = cursor.fetchone()
      if not row:
        raise ValueError("Nenhuma credencial ativa encontrada na tabela login")
      return row[0], row[1]

  def obter_parametros(self) -> ParametrosOperacao:
    with self._db.cursor(dictionary=True) as cursor:
      cursor.execute("SELECT * FROM parametros ORDER BY id LIMIT 1")
      row = cursor.fetchone()
      if not row:
        raise ValueError("Parâmetros não configurados")
      return ParametrosOperacao(
        limite_valor_truck=float(row["limite_valor_truck"]),
        limite_valor_toco=float(row["limite_valor_toco"]),
        limite_valor_carreta=float(row["limite_valor_carreta"]),
        modo_teste=bool(row["modo_teste"]),
        email_notificacao=row["email_notificacao"],
        intervalo_espera_seg=int(row["intervalo_espera_seg"]),
      )

  def obter_destinos_motoristas_ativos(self) -> List[str]:
    query = """
      SELECT DISTINCT LOWER(d.nome_destino) AS nome_destino
      FROM destinos d
      INNER JOIN motorista_destino md ON d.id = md.destino_id
      INNER JOIN motoristas m ON md.motorista_id = m.id
      WHERE m.situacao = TRUE AND d.ativo = TRUE
      ORDER BY d.nome_destino
    """
    with self._db.cursor() as cursor:
      cursor.execute(query)
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo(self) -> List[str]:
    with self._db.cursor() as cursor:
      cursor.execute("SELECT nome_tipo_veiculo FROM tipo_veiculo ORDER BY id")
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo_carreta_motorista(self, motorista_id: int) -> List[str]:
    query = """
      SELECT tv.nome_tipo_veiculo
      FROM motorista_tipo_veiculo_carreta mtc
      INNER JOIN tipo_veiculo tv ON mtc.tipo_veiculo_id = tv.id
      WHERE mtc.motorista_id = %s
    """
    with self._db.cursor() as cursor:
      cursor.execute(query, (motorista_id,))
      return [row[0] for row in cursor.fetchall()]

  def motoristas_disponiveis(
    self,
    rota: DadosRota,
    destino: str,
    tipo_transporte: str,
  ) -> List[DadosMotorista]:
    condicao_bobina = "AND m.aceita_bobina = TRUE" if rota.tem_letra_b else ""
    query = f"""
      SELECT DISTINCT m.*
      FROM motoristas m
      INNER JOIN motorista_destino md ON m.id = md.motorista_id
      INNER JOIN destinos d ON md.destino_id = d.id
      INNER JOIN motorista_tipo_veiculo mtv ON mtv.motorista_id = m.id
      INNER JOIN tipo_veiculo tv ON tv.id = mtv.tipo_veiculo_id
      WHERE m.situacao = TRUE
      {condicao_bobina}
      AND LOWER(d.nome_destino) = LOWER(%s)
      AND LOWER(tv.nome_tipo_veiculo) = LOWER(%s)
      ORDER BY m.ordem_motorista
    """
    with self._db.cursor(dictionary=True) as cursor:
      cursor.execute(query, (destino, tipo_transporte))
      return [
        DadosMotorista(
          id_banco=row["id"],
          placa=row["placa"],
          cpf=row["cpf"],
          nome=row["nome"],
          aceita_bobina=bool(row["aceita_bobina"]),
          situacao=bool(row["situacao"]),
          ordem_motorista=row["ordem_motorista"],
          placa_carreta=row["placa_carreta"] or "",
        )
        for row in cursor.fetchall()
      ]

  def validar_motorista_destino(self, motorista_id: int, destino: str) -> bool:
    query = """
      SELECT 1
      FROM motorista_destino md
      INNER JOIN destinos d ON md.destino_id = d.id
      WHERE md.motorista_id = %s AND LOWER(d.nome_destino) = LOWER(%s)
      LIMIT 1
    """
    with self._db.cursor() as cursor:
      cursor.execute(query, (motorista_id, destino))
      return cursor.fetchone() is not None

  def gravar_rota_vinculada(
    self,
    origem: str,
    destino: str,
    doc_transporte: str,
    data_hora_chegada: str,
    valor_carga: str,
    motorista_nome: str,
    tipo_veiculo: str,
  ) -> None:
    query = """
      INSERT INTO rotas
        (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
         valor_carga, motorista_rota, tipo_veiculo, situacao)
      VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
    """
    with self._db.cursor() as cursor:
      cursor.execute(
        query,
        (origem, destino, doc_transporte, data_hora_chegada,
         valor_carga, motorista_nome, tipo_veiculo),
      )

  def gravar_relatorio(
    self,
    origem: str,
    destino: str,
    doc_transporte: str,
    data_hora_chegada: str,
    valor_carga: str,
    tipo_veiculo: str,
    peso_total: str,
    observacoes: str,
    prioridade: str,
    clientes: str,
    mais_de_um_cliente: bool,
    motivo: str,
  ) -> bool:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT 1 FROM relatorios WHERE doc_transporte = %s UNION "
        "SELECT 1 FROM rotas WHERE doc_transporte = %s LIMIT 1",
        (doc_transporte, doc_transporte),
      )
      if cursor.fetchone():
        return False

    query = """
      INSERT INTO relatorios
        (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
         valor_carga, peso_total, tipo_veiculo, observacoes_rota,
         prioridade, clientes, mais_de_um_cliente, motivo)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with self._db.cursor() as cursor:
      cursor.execute(
        query,
        (origem, destino, doc_transporte, data_hora_chegada,
         valor_carga, peso_total, tipo_veiculo, observacoes,
         prioridade, clientes, mais_de_um_cliente, motivo),
      )
    return True

  def desativar_motorista(self, motorista_id: int) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        "UPDATE motoristas SET situacao = FALSE, ordem_motorista = 10000 WHERE id = %s",
        (motorista_id,),
      )

  def marcar_documento_processado(self, doc_transporte: str) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        """
        INSERT INTO rotas_processadas (doc_transporte)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE processado_em = CURRENT_TIMESTAMP
        """,
        (doc_transporte,),
      )

  def documento_ja_processado(self, doc_transporte: str) -> bool:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT 1 FROM rotas_processadas WHERE doc_transporte = %s",
        (doc_transporte,),
      )
      return cursor.fetchone() is not None

  def limpar_processados_antigos(self, horas: int = 24) -> int:
    with self._db.cursor() as cursor:
      cursor.execute(
        "DELETE FROM rotas_processadas WHERE processado_em < NOW() - INTERVAL %s HOUR",
        (horas,),
      )
      return cursor.rowcount
