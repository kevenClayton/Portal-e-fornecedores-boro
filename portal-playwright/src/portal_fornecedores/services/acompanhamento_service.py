"""Publica status/timeline do robô no banco e captura screenshots para o painel."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from playwright.sync_api import Page

from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)
FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

DIR_SCREENSHOTS = Path("/app/logs/screenshots")
MAX_EVENTOS = 80


class AcompanhamentoService:
  def __init__(self, db: Optional[DatabaseConnection] = None, robo_slot: int = 1, cliente_id: Optional[int] = None):
    self._db = db or DatabaseConnection()
    self._page: Optional[Page] = None
    self._ultimo_screenshot_ts = 0.0
    self._publicacoes_desde_limpeza = 0
    self._robo_slot = max(1, min(3, int(robo_slot or 1)))
    self._cliente_id = max(1, int(cliente_id if cliente_id is not None else get_settings().cliente_id or 1))
    self._arquivo_screenshot = DIR_SCREENSHOTS / f"atual_{self._robo_slot}.png"
    # Compat: slot 1 também grava atual.png para o painel legado
    self._arquivo_screenshot_legado = DIR_SCREENSHOTS / "atual.png" if self._robo_slot == 1 else None
    DIR_SCREENSHOTS.mkdir(parents=True, exist_ok=True)

  def definir_page(self, page: Optional[Page]) -> None:
    self._page = page

  def publicar(self, mensagem: str, forcar_screenshot: bool = False) -> None:
    etapa = self._classificar_etapa(mensagem)
    cluster = self._extrair_cluster(mensagem)
    documento = self._extrair_documento(mensagem)
    resumo = self._extrair_resumo(mensagem)

    try:
      self._upsert_status(etapa, mensagem, cluster, documento, resumo)
      self._inserir_evento(etapa, mensagem)
      self._publicacoes_desde_limpeza += 1
      # Limpa a cada 20 publicações (3 robôs + MySQL remoto — evita travar o ciclo)
      if self._publicacoes_desde_limpeza >= 20:
        self._limpar_eventos_antigos()
        self._publicacoes_desde_limpeza = 0
    except Exception as erro:
      logger.warning("Falha ao publicar acompanhamento: %s", erro)

    deve_capturar = forcar_screenshot or etapa == "erro" or self._pedido_screenshot()
    if deve_capturar or self._pode_screenshot_periodico(mensagem):
      self.capturar_screenshot(motivo=mensagem[:80])

  def capturar_screenshot(self, motivo: str = "") -> bool:
    if not self._page:
      return False
    try:
      DIR_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
      self._page.screenshot(path=str(self._arquivo_screenshot), full_page=False)
      if self._arquivo_screenshot_legado:
        self._page.screenshot(path=str(self._arquivo_screenshot_legado), full_page=False)
      agora = datetime.now(FUSO_BRASIL).strftime("%Y-%m-%d %H:%M:%S")
      with self._db.cursor() as cursor:
        cursor.execute(
          """
          UPDATE robo_acompanhamento
          SET screenshot_em = %s, pedir_screenshot = 0
          WHERE cliente_id = %s
          """,
          (agora, self._cliente_id),
        )
      self._ultimo_screenshot_ts = datetime.now().timestamp()
      logger.info("Screenshot atualizado (%s)", motivo or "manual")
      return True
    except Exception as erro:
      logger.warning("Falha ao capturar screenshot: %s", erro)
      return False

  def verificar_e_capturar_pedido(self) -> bool:
    if self._pedido_screenshot():
      return self.capturar_screenshot("pedido do painel")
    return False

  def _pedido_screenshot(self) -> bool:
    try:
      with self._db.cursor() as cursor:
        cursor.execute(
          "SELECT pedir_screenshot FROM robo_acompanhamento WHERE cliente_id = %s LIMIT 1",
          (self._cliente_id,),
        )
        row = cursor.fetchone()
        return bool(row and row[0])
    except Exception:
      return False

  def _pode_screenshot_periodico(self, mensagem: str) -> bool:
    # Atualiza a cada ~20s em marcos do ciclo (não em cada linha de cluster inexistente)
    marcos = (
      "Sessao ativa",
      "Fazendo login",
      "Navegacao para cargas",
      "Serviços",
      "Vincular Documento",
      "Pesquisar",
      "Resumo filtros",
      "Processando doc",
      "Vinculação OK",
      "Aguardando",
      "ERRO",
    )
    if not any(marco.lower() in mensagem.lower() for marco in marcos):
      return False
    agora = datetime.now().timestamp()
    if agora - self._ultimo_screenshot_ts < 20:
      return False
    return True

  def _upsert_status(
    self,
    etapa: str,
    mensagem: str,
    cluster: Optional[str],
    documento: Optional[str],
    resumo: Optional[str],
  ) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        """
        INSERT INTO robo_acompanhamento
          (cliente_id, etapa, mensagem, cluster_atual, documento_atual, resumo_ciclo, atualizado_em)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
          etapa = VALUES(etapa),
          mensagem = VALUES(mensagem),
          cluster_atual = COALESCE(VALUES(cluster_atual), cluster_atual),
          documento_atual = COALESCE(VALUES(documento_atual), documento_atual),
          resumo_ciclo = COALESCE(VALUES(resumo_ciclo), resumo_ciclo),
          atualizado_em = NOW()
        """,
        (self._cliente_id, etapa, mensagem[:500], cluster, documento, resumo),
      )

  def _inserir_evento(self, etapa: str, mensagem: str) -> None:
    # Evita spam: não grava todos os "Cluster nao existente"
    if "Cluster nao existente" in mensagem or "Cluster não existente" in mensagem:
      return
    with self._db.cursor() as cursor:
      cursor.execute(
        "INSERT INTO robo_eventos (etapa, mensagem, created_at, cliente_id) VALUES (%s, %s, NOW(), %s)",
        (etapa, mensagem[:500], self._cliente_id),
      )

  def _limpar_eventos_antigos(self) -> None:
    with self._db.cursor() as cursor:
      cursor.execute(
        "SELECT id FROM robo_eventos WHERE cliente_id = %s ORDER BY id DESC LIMIT 1 OFFSET %s",
        (self._cliente_id, MAX_EVENTOS),
      )
      row = cursor.fetchone()
      if row:
        cursor.execute(
          "DELETE FROM robo_eventos WHERE cliente_id = %s AND id <= %s",
          (self._cliente_id, row[0]),
        )

  @staticmethod
  def _classificar_etapa(mensagem: str) -> str:
    texto = mensagem.lower()
    if texto.startswith("erro") or "captcha" in texto or "bloqueado" in texto:
      return "erro"
    if "login" in texto or "sessao" in texto or "sessão" in texto:
      return "login"
    if "aguardando" in texto or "pesquisar" in texto or "buscando" in texto or "navegacao" in texto or "navegação" in texto:
      return "busca"
    if "cluster" in texto or "destino" in texto or "resumo filtros" in texto:
      return "filtro"
    if "valor" in texto or "bobina" in texto or "detalhe" in texto or "multiplos destinos" in texto:
      return "detalhe"
    if "motorista" in texto or "vincul" in texto or "parâmetros ok" in texto or "parametros ok" in texto:
      return "vinculo"
    return "info"

  @staticmethod
  def _extrair_cluster(mensagem: str) -> Optional[str]:
    match = re.search(r"cluster(?: existente)?:\s*(.+)$", mensagem, re.IGNORECASE)
    if match:
      return match.group(1).strip()[:255]
    match = re.search(r"→\s*([A-Z0-9].+)$", mensagem)
    if match and "Processando" in mensagem:
      return None
    return None

  @staticmethod
  def _extrair_documento(mensagem: str) -> Optional[str]:
    match = re.search(r"doc(?:umento)?\s+(\S+)", mensagem, re.IGNORECASE)
    if match:
      return match.group(1).strip(".,;")[:100]
    return None

  @staticmethod
  def _extrair_resumo(mensagem: str) -> Optional[str]:
    if "Resumo filtros" in mensagem:
      return mensagem[:255]
    return None
