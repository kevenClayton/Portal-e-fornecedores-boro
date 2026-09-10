"""Cliente da API ReservaAI para notificação WhatsApp de cargas."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Iterable, List, Optional

from portal_fornecedores.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

CODIGO_ESTABELECIMENTO_PADRAO = 9


class WhatsAppService:
  def __init__(self, settings: Optional[Settings] = None):
    self._settings = settings or get_settings()

  def telefones_validos(self, bruto: str) -> List[str]:
    if not bruto:
      return []
    partes = re.split(r"[\s,;]+", bruto.strip())
    telefones = []
    for parte in partes:
      digits = re.sub(r"\D", "", parte)
      if len(digits) < 10:
        continue
      if not digits.startswith("55") and len(digits) in (10, 11):
        digits = "55" + digits
      telefones.append(digits)
    vistos = set()
    unicos = []
    for telefone in telefones:
      if telefone not in vistos:
        vistos.add(telefone)
        unicos.append(telefone)
    return unicos

  def notificar_carga(
    self,
    telefones: Iterable[str],
    situacao: str,
    motorista: str,
    numero_documento: str,
    url_detalhes: str,
    motivo: str = "",
    codigo_estabelecimento: Optional[int] = None,
  ) -> None:
    lista = [telefone for telefone in telefones if telefone]
    if not lista:
      logger.info("WhatsApp: nenhum telefone configurado — pulando notificação")
      return

    token = (self._settings.whatsapp_api_token or "").strip()
    if not token:
      logger.error("WhatsApp: WHATSAPP_API_TOKEN vazio — não envia sem Bearer")
      return

    base = (self._settings.whatsapp_api_url or "").rstrip("/")
    if not base:
      logger.warning("WhatsApp: WHATSAPP_API_URL vazio — pulando")
      return

    motorista_envio = (motorista or "").strip()[:60]
    documento_envio = str(numero_documento or "").strip()[:40]
    url_envio = (url_detalhes or "").strip()

    if not motorista_envio or not documento_envio or not url_envio:
      logger.error(
        "WhatsApp: faltam campos obrigatórios (motorista/documento/url) — pulando"
      )
      return

    if not url_envio.startswith("https://"):
      logger.error("WhatsApp: url_detalhes precisa ser https — pulando (%s)", url_envio)
      return

    codigo = int(codigo_estabelecimento) if codigo_estabelecimento is not None else CODIGO_ESTABELECIMENTO_PADRAO
    situacao_envio = (situacao or "aceita").strip().lower() or "aceita"
    motivo_envio = (motivo or "").strip() or "-"

    # Rota de envio (template carga_aceita já existe — não criar template)
    endpoint = f"{base}/whatsapp/externo/carga-aceita"

    for telefone in lista:
      payload = {
        "telefone": telefone,
        "motorista": motorista_envio,
        "numero_documento": documento_envio,
        "url_detalhes": url_envio,
        "codigo_estabelecimento": codigo,
        "situacao": situacao_envio,
        "motivo": motivo_envio,
      }
      self._post(endpoint, payload, token)

  def _post(self, endpoint: str, payload: dict, token: str) -> None:
    corpo = json.dumps(payload).encode("utf-8")
    headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Authorization": f"Bearer {token}",
    }

    request = urllib.request.Request(endpoint, data=corpo, headers=headers, method="POST")
    try:
      with urllib.request.urlopen(request, timeout=20) as resposta:
        corpo_resposta = resposta.read().decode("utf-8", errors="replace")
        status = getattr(resposta, "status", 200)
        self._tratar_sucesso(status, corpo_resposta, payload)
    except urllib.error.HTTPError as erro:
      detalhe = erro.read().decode("utf-8", errors="replace")[:500]
      if erro.code == 401:
        logger.error("WhatsApp 401: token inválido | %s", detalhe)
      elif erro.code == 422:
        logger.error("WhatsApp 422: payload inválido | %s | payload=%s", detalhe, payload)
      elif erro.code >= 500:
        logger.error("WhatsApp %s: não foi possível enviar | %s", erro.code, detalhe)
      else:
        logger.error("WhatsApp HTTP %s: %s | payload=%s", erro.code, detalhe, payload)
    except Exception as erro:
      logger.error("WhatsApp falhou: %s | payload=%s", erro, payload)

  def _tratar_sucesso(self, status: int, corpo: str, payload: dict) -> None:
    enviado = False
    try:
      dados = json.loads(corpo) if corpo else {}
      enviado = bool(dados.get("enviado")) if isinstance(dados, dict) else False
    except json.JSONDecodeError:
      dados = corpo

    if status == 200 and enviado:
      logger.info(
        "WhatsApp enviado com sucesso doc=%s telefone=%s situacao=%s",
        payload.get("numero_documento"),
        payload.get("telefone"),
        payload.get("situacao"),
      )
      return

    logger.warning(
      "WhatsApp HTTP %s sem confirmação enviado=true | resposta=%s | payload=%s",
      status,
      str(dados)[:300],
      payload,
    )
