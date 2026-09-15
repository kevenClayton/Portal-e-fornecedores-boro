import logging
from typing import List, Optional, Tuple

from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.connection import DatabaseConnection
from portal_fornecedores.models.entidades import DadosMotorista, DadosRota, ParametrosOperacao

logger = logging.getLogger(__name__)


def _flag(row: dict, campo: str, padrao: bool = True) -> bool:
  if campo not in row or row[campo] is None:
    return padrao
  return bool(row[campo])


class DadosRepository:
  def __init__(self, db: Optional[DatabaseConnection] = None, cliente_id: Optional[int] = None):
    self._db = db or DatabaseConnection()
    raw = cliente_id if cliente_id is not None else get_settings().cliente_id
    # 0 = banco single-tenant (sem coluna/filtro cliente_id)
    self._cliente_id = max(0, int(raw or 0))
    self._multi_tenant = self._cliente_id > 0

  def obter_login(self) -> Tuple[str, str]:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "SELECT usuario, senha FROM login WHERE ativo = TRUE AND cliente_id = %s LIMIT 1",
          (self._cliente_id,),
        )
      else:
        cursor.execute(
          "SELECT usuario, senha FROM login WHERE COALESCE(ativo, 1) = 1 LIMIT 1",
        )
      row = cursor.fetchone()
      if not row:
        raise ValueError("Nenhuma credencial ativa encontrada na tabela login")
      return row[0], row[1]

  def obter_parametros(self) -> ParametrosOperacao:
    with self._db.cursor(dictionary=True) as cursor:
      if self._multi_tenant:
        cursor.execute(
          "SELECT * FROM parametros WHERE cliente_id = %s ORDER BY id LIMIT 1",
          (self._cliente_id,),
        )
      else:
        cursor.execute("SELECT * FROM parametros ORDER BY id LIMIT 1")
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
    if self._multi_tenant:
      query = """
        SELECT DISTINCT LOWER(d.nome_destino) AS nome_destino
        FROM destinos d
        INNER JOIN motorista_destino md ON d.id = md.destino_id
        INNER JOIN motoristas m ON md.motorista_id = m.id
        WHERE m.situacao = TRUE AND d.ativo = TRUE
          AND m.cliente_id = %s AND d.cliente_id = %s
        ORDER BY d.nome_destino
      """
      params = (self._cliente_id, self._cliente_id)
    else:
      query = """
        SELECT DISTINCT LOWER(d.nome_destino) AS nome_destino
        FROM destinos d
        INNER JOIN motorista_destino md ON d.id = md.destino_id
        INNER JOIN motoristas m ON md.motorista_id = m.id
        WHERE m.situacao = TRUE AND COALESCE(d.ativo, 1) = 1
        ORDER BY d.nome_destino
      """
      params = ()
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo(self) -> List[str]:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "SELECT nome_tipo_veiculo FROM tipo_veiculo WHERE cliente_id = %s ORDER BY id",
          (self._cliente_id,),
        )
      else:
        cursor.execute("SELECT nome_tipo_veiculo FROM tipo_veiculo ORDER BY id")
      return [row[0] for row in cursor.fetchall()]

  def obter_tipos_veiculo_carreta_motorista(self, motorista_id: int) -> List[str]:
    query = """
      SELECT tv.nome_tipo_veiculo
      FROM motorista_tipo_veiculo_carreta mtc
      INNER JOIN tipo_veiculo tv ON mtc.tipo_veiculo_id = tv.id
      WHERE mtc.motorista_id = %s
    """
    params: tuple = (motorista_id,)
    if self._multi_tenant:
      query += " AND tv.cliente_id = %s"
      params = (motorista_id, self._cliente_id)
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
      return [row[0] for row in cursor.fetchall()]

  def existe_motorista_destino_tipo(self, destino: str, tipo_transporte: str) -> bool:
    """Há motorista ativo no destino com o tipo de veículo da carga (sem filtro de bobina)."""
    filtro_cliente = "AND m.cliente_id = %s AND d.cliente_id = %s" if self._multi_tenant else ""
    query = f"""
      SELECT 1
      FROM motoristas m
      INNER JOIN motorista_destino md ON m.id = md.motorista_id
      INNER JOIN destinos d ON md.destino_id = d.id
      INNER JOIN motorista_tipo_veiculo mtv ON mtv.motorista_id = m.id
      INNER JOIN tipo_veiculo tv ON tv.id = mtv.tipo_veiculo_id
      WHERE m.situacao = TRUE
      {filtro_cliente}
      AND LOWER(d.nome_destino) = LOWER(%s)
      AND LOWER(tv.nome_tipo_veiculo) = LOWER(%s)
      LIMIT 1
    """
    if self._multi_tenant:
      params: tuple = (self._cliente_id, self._cliente_id, destino, tipo_transporte)
    else:
      params = (destino, tipo_transporte)
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
      return cursor.fetchone() is not None

  def motoristas_disponiveis(
    self,
    rota: DadosRota,
    destino: str,
    tipo_transporte: str,
  ) -> List[DadosMotorista]:
    condicao_bobina = "AND m.aceita_bobina = TRUE" if rota.tem_letra_b else ""
    filtro_cliente = "AND m.cliente_id = %s AND d.cliente_id = %s" if self._multi_tenant else ""
    query = f"""
      SELECT DISTINCT m.*
      FROM motoristas m
      INNER JOIN motorista_destino md ON m.id = md.motorista_id
      INNER JOIN destinos d ON md.destino_id = d.id
      INNER JOIN motorista_tipo_veiculo mtv ON mtv.motorista_id = m.id
      INNER JOIN tipo_veiculo tv ON tv.id = mtv.tipo_veiculo_id
      WHERE m.situacao = TRUE
      {filtro_cliente}
      {condicao_bobina}
      AND LOWER(d.nome_destino) = LOWER(%s)
      AND LOWER(tv.nome_tipo_veiculo) = LOWER(%s)
      ORDER BY m.ordem_motorista
    """
    params: tuple
    if self._multi_tenant:
      params = (self._cliente_id, self._cliente_id, destino, tipo_transporte)
    else:
      params = (destino, tipo_transporte)
    with self._db.cursor(dictionary=True) as cursor:
      cursor.execute(query, params)
      return [
        DadosMotorista(
          id_banco=row["id"],
          placa=row["placa"],
          cpf=row["cpf"],
          nome=row["nome"],
          aceita_bobina=bool(row["aceita_bobina"]),
          situacao=bool(row["situacao"]),
          ordem_motorista=row["ordem_motorista"],
          placa_carreta=row.get("placa_carreta") or "",
        )
        for row in cursor.fetchall()
      ]

  def validar_motorista_destino(self, motorista_id: int, destino: str) -> bool:
    if self._multi_tenant:
      query = """
        SELECT 1
        FROM motorista_destino md
        INNER JOIN destinos d ON md.destino_id = d.id
        WHERE md.motorista_id = %s AND LOWER(d.nome_destino) = LOWER(%s)
          AND d.cliente_id = %s
        LIMIT 1
      """
      params = (motorista_id, destino, self._cliente_id)
    else:
      query = """
        SELECT 1
        FROM motorista_destino md
        INNER JOIN destinos d ON md.destino_id = d.id
        WHERE md.motorista_id = %s AND LOWER(d.nome_destino) = LOWER(%s)
        LIMIT 1
      """
      params = (motorista_id, destino)
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
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
    if self._multi_tenant:
      query = """
        INSERT INTO rotas
          (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
           valor_carga, motorista_rota, tipo_veiculo, situacao, cliente_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
      """
      params = (origem, destino, doc_transporte, data_hora_chegada,
                valor_carga, motorista_nome, tipo_veiculo, self._cliente_id)
    else:
      query = """
        INSERT INTO rotas
          (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
           valor_carga, motorista_rota, tipo_veiculo, situacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
      """
      params = (origem, destino, doc_transporte, data_hora_chegada,
                valor_carga, motorista_nome, tipo_veiculo)
    with self._db.cursor() as cursor:
      cursor.execute(query, params)

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
      if self._multi_tenant:
        cursor.execute(
          "SELECT 1 FROM relatorios WHERE doc_transporte = %s AND cliente_id = %s UNION "
          "SELECT 1 FROM rotas WHERE doc_transporte = %s AND cliente_id = %s LIMIT 1",
          (doc_transporte, self._cliente_id, doc_transporte, self._cliente_id),
        )
      else:
        cursor.execute(
          "SELECT 1 FROM relatorios WHERE doc_transporte = %s UNION "
          "SELECT 1 FROM rotas WHERE doc_transporte = %s LIMIT 1",
          (doc_transporte, doc_transporte),
        )
      if cursor.fetchone():
        return False

    if self._multi_tenant:
      query = """
        INSERT INTO relatorios
          (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
           valor_carga, peso_total, tipo_veiculo, observacoes_rota,
           prioridade, clientes, mais_de_um_cliente, motivo, cliente_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """
      params = (origem, destino, doc_transporte, data_hora_chegada,
                valor_carga, peso_total, tipo_veiculo, observacoes,
                prioridade, clientes, mais_de_um_cliente, motivo, self._cliente_id)
    else:
      query = """
        INSERT INTO relatorios
          (origem_rota, destino_rota, doc_transporte, data_hora_chegada,
           valor_carga, peso_total, tipo_veiculo, observacoes_rota,
           prioridade, clientes, mais_de_um_cliente, motivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """
      params = (origem, destino, doc_transporte, data_hora_chegada,
                valor_carga, peso_total, tipo_veiculo, observacoes,
                prioridade, clientes, mais_de_um_cliente, motivo)
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
    return True

  def desativar_motorista(self, motorista_id: int) -> None:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "UPDATE motoristas SET situacao = FALSE, ordem_motorista = 10000 "
          "WHERE id = %s AND cliente_id = %s",
          (motorista_id, self._cliente_id),
        )
      else:
        cursor.execute(
          "UPDATE motoristas SET situacao = FALSE, ordem_motorista = 10000 WHERE id = %s",
          (motorista_id,),
        )

  def marcar_documento_processado(self, doc_transporte: str) -> None:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          """
          INSERT INTO rotas_processadas (cliente_id, doc_transporte)
          VALUES (%s, %s)
          ON DUPLICATE KEY UPDATE processado_em = CURRENT_TIMESTAMP
          """,
          (self._cliente_id, doc_transporte),
        )
      else:
        cursor.execute(
          """
          INSERT INTO rotas_processadas (doc_transporte)
          VALUES (%s)
          ON DUPLICATE KEY UPDATE processado_em = CURRENT_TIMESTAMP
          """,
          (doc_transporte,),
        )

  def tentar_reservar_documento(self, doc_transporte: str) -> bool:
    """Reserva atômica — evita dois robôs processarem o mesmo doc."""
    with self._db.cursor() as cursor:
      try:
        if self._multi_tenant:
          cursor.execute(
            "INSERT INTO rotas_processadas (cliente_id, doc_transporte) VALUES (%s, %s)",
            (self._cliente_id, doc_transporte),
          )
        else:
          cursor.execute(
            "INSERT INTO rotas_processadas (doc_transporte) VALUES (%s)",
            (doc_transporte,),
          )
        return cursor.rowcount == 1
      except Exception:
        return False

  def documento_ja_processado(self, doc_transporte: str) -> bool:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "SELECT 1 FROM rotas_processadas WHERE doc_transporte = %s AND cliente_id = %s",
          (doc_transporte, self._cliente_id),
        )
      else:
        cursor.execute(
          "SELECT 1 FROM rotas_processadas WHERE doc_transporte = %s",
          (doc_transporte,),
        )
      return cursor.fetchone() is not None

  def limpar_processados_antigos(self, horas: int = 24) -> int:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "DELETE FROM rotas_processadas WHERE cliente_id = %s "
          "AND processado_em < NOW() - INTERVAL %s HOUR",
          (self._cliente_id, horas),
        )
      else:
        cursor.execute(
          "DELETE FROM rotas_processadas WHERE processado_em < NOW() - INTERVAL %s HOUR",
          (horas,),
        )
      return cursor.rowcount

  def registrar_auditoria_decisao(
    self,
    *,
    slot: int,
    doc_transporte: str,
    destino: str,
    tipo_veiculo: str,
    decisao: str,
    motivo: str = "",
  ) -> None:
    """1 linha por decisão de carga (não por ciclo) — impacto mínimo no banco."""
    try:
      if self._multi_tenant:
        query = """
          INSERT INTO robo_auditoria
            (cliente_id, slot, tipo_evento, doc_transporte, destino, tipo_veiculo, decisao, motivo)
          VALUES (%s, %s, 'decisao_carga', %s, %s, %s, %s, %s)
        """
        params = (
          self._cliente_id,
          max(1, min(3, int(slot or 1))),
          (doc_transporte or "")[:100],
          (destino or "")[:255] or None,
          (tipo_veiculo or "")[:80] or None,
          (decisao or "")[:40],
          (motivo or "")[:500] or None,
        )
      else:
        query = """
          INSERT INTO robo_auditoria
            (slot, tipo_evento, doc_transporte, destino, tipo_veiculo, decisao, motivo)
          VALUES (%s, 'decisao_carga', %s, %s, %s, %s, %s)
        """
        params = (
          max(1, min(3, int(slot or 1))),
          (doc_transporte or "")[:100],
          (destino or "")[:255] or None,
          (tipo_veiculo or "")[:80] or None,
          (decisao or "")[:40],
          (motivo or "")[:500] or None,
        )
      with self._db.cursor() as cursor:
        cursor.execute(query, params)
    except Exception as erro:
      logger.warning("Falha ao gravar auditoria de decisao: %s", erro)

  def registrar_auditoria_captcha(
    self,
    *,
    slot: int,
    origem: str,
    proxy_host: str = "",
    tentativa: int = 1,
    motivo: str = "",
  ) -> None:
    """1 linha por rejeição de captcha (volume baixo)."""
    try:
      if self._multi_tenant:
        query = """
          INSERT INTO robo_auditoria
            (cliente_id, slot, tipo_evento, origem_captcha, proxy_host, tentativa, motivo)
          VALUES (%s, %s, 'captcha', %s, %s, %s, %s)
        """
        params = (
          self._cliente_id,
          max(1, min(3, int(slot or 1))),
          (origem or "Login")[:40],
          (proxy_host or "")[:80] or None,
          int(tentativa or 1),
          (motivo or "")[:500] or None,
        )
      else:
        query = """
          INSERT INTO robo_auditoria
            (slot, tipo_evento, origem_captcha, proxy_host, tentativa, motivo)
          VALUES (%s, 'captcha', %s, %s, %s, %s)
        """
        params = (
          max(1, min(3, int(slot or 1))),
          (origem or "Login")[:40],
          (proxy_host or "")[:80] or None,
          int(tentativa or 1),
          (motivo or "")[:500] or None,
        )
      with self._db.cursor() as cursor:
        cursor.execute(query, params)
    except Exception as erro:
      logger.warning("Falha ao gravar auditoria de captcha: %s", erro)

  def limpar_auditoria_antiga(self, dias: int = 15) -> int:
    with self._db.cursor() as cursor:
      if self._multi_tenant:
        cursor.execute(
          "DELETE FROM robo_auditoria WHERE cliente_id = %s "
          "AND created_at < NOW() - INTERVAL %s DAY",
          (self._cliente_id, max(1, int(dias))),
        )
      else:
        cursor.execute(
          "DELETE FROM robo_auditoria WHERE created_at < NOW() - INTERVAL %s DAY",
          (max(1, int(dias)),),
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
    if self._multi_tenant:
      query = """
        INSERT INTO notificacoes_carga
          (public_id, situacao, motorista, numero_documento, motivo,
           origem, destino, valor_carga, tipo_transporte, placa, cpf, cliente_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """
      params = (
        public_id, situacao, motorista or "", numero_documento, motivo or None,
        origem or None, destino or None, valor_carga or None,
        tipo_transporte or None, placa or None, cpf or None, self._cliente_id,
      )
    else:
      query = """
        INSERT INTO notificacoes_carga
          (public_id, situacao, motorista, numero_documento, motivo,
           origem, destino, valor_carga, tipo_transporte, placa, cpf)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """
      params = (
        public_id, situacao, motorista or "", numero_documento, motivo or None,
        origem or None, destino or None, valor_carga or None,
        tipo_transporte or None, placa or None, cpf or None,
      )
    with self._db.cursor() as cursor:
      cursor.execute(query, params)
    return public_id
