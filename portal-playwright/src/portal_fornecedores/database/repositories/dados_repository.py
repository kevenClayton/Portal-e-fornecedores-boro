from typing import List, Optional, Tuple

from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.connection import DatabaseConnection
from portal_fornecedores.models.entidades import DadosMotorista, DadosRota, ParametrosOperacao


def _flag(row: dict, campo: str, padrao: bool = True) -> bool:
  if campo not in row or row[campo] is None:
    return padrao
  return bool(row[campo])


class DadosRepository:
  def __init__(self, db: Optional[DatabaseConnection] = None, cliente_id: Optional[int] = None):
    self._db = db or DatabaseConnection()
    self._cliente_id = max(1, int(cliente_id if cliente_id is not None else get_settings().cliente_id or 1))

  def obter_login(self) -> Tuple[str, str]:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT usuario, senha FROM login WHERE ativo = TRUE AND cliente_id = %s LIMIT 1",
        (self._cliente_id,),
      )
      row = cursor.fetchone()
      if not row:
        raise ValueError("Nenhuma credencial ativa encontrada na tabela login")
      return row[0], row[1]

  def obter_parametros(self) -> ParametrosOperacao:
    with self._db.cursor(dictionary=True) as cursor:
      cursor.execute(
        "SELECT * FROM parametros WHERE cliente_id = %s ORDER BY id LIMIT 1",
        (self._cliente_id,),
      )
      row = cursor.fetchone()
      if not row:
        raise ValueError("Parâmetros não configurados")
      codigo = row.get("whatsapp_codigo_estabelecimento")
      return ParametrosOperacao(
        limite_valor_truck=float(row["limite_valor_truck"]),
        limite_valor_toco=float(row["limite_valor_toco"]),
        limite_valor_carreta=float(row["limite_valor_carreta"]),
        modo_teste=bool(row["modo_teste"]),
        email_notificacao=row["email_notificacao"] or "",
        intervalo_espera_seg=int(row.get("intervalo_espera_seg") or 30),
        verificar_valor_carga=_flag(row, "verificar_valor_carga", True),
        verificar_bobina=_flag(row, "verificar_bobina", True),
        verificar_multiplos_destinos=_flag(row, "verificar_multiplos_destinos", True),
        whatsapp_telefones=row.get("whatsapp_telefones") or "",
        whatsapp_codigo_estabelecimento=int(codigo) if codigo is not None else None,
        painel_url_publica=(row.get("painel_url_publica") or "").rstrip("/"),
        robo_quantidade=max(1, min(3, int(row.get("robo_quantidade") or 1))),
      )

  def obter_destinos_motoristas_ativos(self) -> List[str]:
    query = """
      SELECT DISTINCT LOWER(d.nome_destino) AS nome_destino
      FROM destinos d
      INNER JOIN motorista_destino md ON d.id = md.destino_id
      INNER JOIN motoristas m ON md.motorista_id = m.id
      WHERE m.situacao = TRUE AND d.ativo = TRUE
        AND m.cliente_id = %s AND d.cliente_id = %s
      ORDER BY d.nome_destino
    """
    with self._db.cursor() as cursor:
      cursor.execute(query, (self._cliente_id, self._cliente_id))
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo(self) -> List[str]:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT nome_tipo_veiculo FROM tipo_veiculo WHERE cliente_id = %s ORDER BY id",
        (self._cliente_id,),
      )
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo_carreta_motorista(self, motorista_id: int) -> List[str]:
    query = """
      SELECT tv.nome_tipo_veiculo
      FROM motorista_tipo_veiculo_carreta mtc
      INNER JOIN tipo_veiculo tv ON mtc.tipo_veiculo_id = tv.id
      WHERE mtc.motorista_id = %s AND tv.cliente_id = %s
    """
    with self._db.cursor() as cursor:
      cursor.execute(query, (motorista_id, self._cliente_id))
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
        AND m.cliente_id = %s
        AND d.cliente_id = %s
      {condicao_bobina}
      AND LOWER(d.nome_destino) = LOWER(%s)
      AND LOWER(tv.nome_tipo_veiculo) = LOWER(%s)
      ORDER BY m.ordem_motorista
    """
    with self._db.cursor(dictionary=True) as cursor:
      cursor.execute(query, (self._cliente_id, self._cliente_id, destino, tipo_transporte))
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
        AND d.cliente_id = %s
      LIMIT 1
    """
    with self._db.cursor() as cursor:
      cursor.execute(query, (motorista_id, destino, self._cliente_id))
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
         valor_carga, motorista_rota, tipo_veiculo, situacao, cliente_id)
      VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
    """
    with self._db.cursor() as cursor:
      cursor.execute(
        query,
        (origem, destino, doc_transporte, data_hora_chegada,
         valor_carga, motorista_nome, tipo_veiculo, self._cliente_id),
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
        "SELECT 1 FROM relatorios WHERE doc_transporte = %s AND cliente_id = %s UNION "
        "SELECT 1 FROM rotas WHERE doc_transporte = %s AND cliente_id = %s LIMIT 1",
        (doc_transporte, self._cliente_id, doc_transporte, self._cliente_id),
      )
      if cursor.fetchone():
        return False

    query = """
      INSERT INTO relatorios
        (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
         valor_carga, peso_total, tipo_veiculo, observacoes_rota,
         prioridade, clientes, mais_de_um_cliente, motivo, cliente_id)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with self._db.cursor() as cursor:
      cursor.execute(
        query,
        (origem, destino, doc_transporte, data_hora_chegada,
         valor_carga, peso_total, tipo_veiculo, observacoes,
         prioridade, clientes, mais_de_um_cliente, motivo, self._cliente_id),
      )
    return True

  def desativar_motorista(self, motorista_id: int) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        "UPDATE motoristas SET situacao = FALSE, ordem_motorista = 10000 "
        "WHERE id = %s AND cliente_id = %s",
        (motorista_id, self._cliente_id),
      )

  def marcar_documento_processado(self, doc_transporte: str) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        """
        INSERT INTO rotas_processadas (cliente_id, doc_transporte)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE processado_em = CURRENT_TIMESTAMP
        """,
        (self._cliente_id, doc_transporte),
      )

  def tentar_reservar_documento(self, doc_transporte: str) -> bool:
    """Reserva atômica — evita dois robôs processarem o mesmo doc."""
    with self._db.cursor() as cursor:
      try:
        cursor.execute(
          "INSERT INTO rotas_processadas (cliente_id, doc_transporte) VALUES (%s, %s)",
          (self._cliente_id, doc_transporte),
        )
        return cursor.rowcount == 1
      except Exception:
        return False

  def documento_ja_processado(self, doc_transporte: str) -> bool:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT 1 FROM rotas_processadas WHERE doc_transporte = %s AND cliente_id = %s",
        (doc_transporte, self._cliente_id),
      )
      return cursor.fetchone() is not None

  def limpar_processados_antigos(self, horas: int = 24) -> int:
    with self._db.cursor() as cursor:
      cursor.execute(
        "DELETE FROM rotas_processadas WHERE cliente_id = %s "
        "AND processado_em < NOW() - INTERVAL %s HOUR",
        (self._cliente_id, horas),
      )
      return cursor.rowcount

  def gravar_notificacao_carga(
    self,
    situacao: str,
    numero_documento: str,
    motorista: str = "",
    motivo: str = "",
    origem: str = "",
    destino: str = "",
    valor_carga: str = "",
    tipo_transporte: str = "",
    placa: str = "",
    cpf: str = "",
  ) -> str:
    """Persiste evento para página pública e retorna public_id (UUID)."""
    import uuid

    public_id = str(uuid.uuid4())
    query = """
      INSERT INTO notificacoes_carga
        (public_id, situacao, motorista, numero_documento, motivo,
         origem, destino, valor_carga, tipo_transporte, placa, cpf, cliente_id)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with self._db.cursor() as cursor:
      cursor.execute(
        query,
        (
          public_id,
          situacao,
          motorista or "",
          numero_documento,
          motivo or None,
          origem or None,
          destino or None,
          valor_carga or None,
          tipo_transporte or None,
          placa or None,
          cpf or None,
          self._cliente_id,
        ),
      )
    return public_id
