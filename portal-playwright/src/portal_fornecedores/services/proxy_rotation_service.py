"""Proxy via API Webshare: escolha inicial, sticky e rotação quando o reCAPTCHA rejeita o IP."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ARQUIVO_PROXY = Path("/app/logs/proxy_atual.txt")
URL_LISTA = "https://proxy.webshare.io/api/v2/proxy/list/"
URL_PLANOS = "https://proxy.webshare.io/api/v2/subscription/plan/"


class ProxyRotationService:
  def __init__(
    self,
    api_token: str = "",
    plan_id: Optional[int] = None,
    arquivo_proxy: Path = ARQUIVO_PROXY,
    slot: int = 1,
    cliente: str = "",
  ):
    self._token = (api_token or "").strip()
    self._plan_id = plan_id
    self._arquivo = arquivo_proxy
    self._slot = max(1, min(3, int(slot or 1)))
    self._cliente = (cliente or "").strip().lower() or "default"

  @property
  def habilitado(self) -> bool:
    return bool(self._token)

  def carregar_proxy_salvo(self) -> Optional[str]:
    try:
      if self._arquivo.exists():
        valor = self._arquivo.read_text(encoding="utf-8").strip()
        if valor and ":" in valor:
          return valor
    except Exception as erro:
      logger.warning("Falha ao ler proxy salvo: %s", erro)
    return None

  def salvar_proxy(self, proxy: str) -> None:
    try:
      self._arquivo.parent.mkdir(parents=True, exist_ok=True)
      self._arquivo.write_text(proxy.strip() + "\n", encoding="utf-8")
    except Exception as erro:
      logger.warning("Falha ao salvar proxy atual: %s", erro)

  def resolver_proxy_inicial(self, proxy_env: Optional[str] = None) -> Optional[str]:
    """
    Prioridade:
      1) API Webshare — reaproveita IP salvo se ainda existir no plano; senão escolhe outro
      2) PROXY do .env (fallback)
    Assim, replace/IP novo no painel Webshare entra sem editar o servidor.
    """
    if self.habilitado:
      escolhido = self._escolher_da_api(preferir_host=self._extrair_host(self.carregar_proxy_salvo()))
      if escolhido:
        self.salvar_proxy(escolhido)
        host = escolhido.split(":")[0]
        logger.info(
          "Proxy via API Webshare (cliente=%s slot=%s): %s",
          self._cliente,
          self._slot,
          host,
        )
        return escolhido
      logger.warning("API Webshare sem proxy utilizavel — tentando PROXY do .env")

    fallback = (proxy_env or "").strip()
    if fallback and ":" in fallback:
      self.salvar_proxy(fallback)
      logger.info("Usando PROXY do .env: %s", fallback.split(":")[0])
      return fallback
    return None

  def trocar_proxy(self, proxy_atual: Optional[str]) -> Optional[str]:
    if not self.habilitado:
      logger.warning("WEBSHARE_API_TOKEN nao configurado — sem rotacao automatica")
      return None

    host_atual = self._extrair_host(proxy_atual)
    novo = self._escolher_da_api(preferir_host=None, evitar_host=host_atual)
    if not novo:
      return None

    self.salvar_proxy(novo)
    logger.info(
      "Proxy trocado: %s -> %s",
      host_atual or "(nenhum)",
      novo.split(":")[0],
    )
    return novo

  def _escolher_da_api(
    self,
    preferir_host: Optional[str] = None,
    evitar_host: Optional[str] = None,
  ) -> Optional[str]:
    plan_id = self._plan_id or self._descobrir_plan_isp()
    if not plan_id:
      logger.warning("Nenhum plano ISP/residential ativo encontrado na Webshare")
      return None

    proxies = self._listar_proxies(plan_id)
    if not proxies:
      logger.warning("Lista de proxies vazia (plan_id=%s)", plan_id)
      return None

    # Sticky: se o IP salvo ainda está na lista (após replace some), renova user/senha da API
    if preferir_host:
      for item in proxies:
        if item["host"] == preferir_host:
          return self._formatar(item)

    candidatos = [item for item in proxies if item["host"] != evitar_host]
    if not candidatos:
      candidatos = proxies

    indice = self._indice_cliente_slot(len(candidatos))
    if evitar_host:
      # ao rotacionar, anda a partir do IP atual + offset do cliente
      for posicao, item in enumerate(proxies):
        if item["host"] == evitar_host:
          indice = (posicao + self._slot + self._offset_cliente(len(proxies))) % len(candidatos)
          break

    escolhido = candidatos[indice % len(candidatos)]
    if evitar_host and escolhido["host"] == evitar_host and len(candidatos) > 1:
      for item in candidatos:
        if item["host"] != evitar_host:
          escolhido = item
          break

    return self._formatar(escolhido)

  def _offset_cliente(self, total: int) -> int:
    """Espalha clientes no pool (MadeForte no início, Boro na metade, etc.)."""
    if total <= 1:
      return 0
    if "boro" in self._cliente:
      return max(1, total // 2)
    if "madeforte" in self._cliente or "made" in self._cliente:
      return 0
    # outros clientes: hash estável
    return sum(ord(caractere) for caractere in self._cliente) % total

  def _indice_cliente_slot(self, total: int) -> int:
    if total <= 0:
      return 0
    return (self._offset_cliente(total) + self._slot - 1) % total

  @staticmethod
  def _formatar(item: dict) -> str:
    return f"{item['host']}:{item['port']}:{item['username']}:{item['password']}"

  def _descobrir_plan_isp(self) -> Optional[int]:
    dados = self._get_json(URL_PLANOS)
    resultados = (dados or {}).get("results") or []
    for item in resultados:
      if item.get("status") != "active":
        continue
      subtype = (item.get("proxy_subtype") or "").lower()
      if subtype in ("isp", "residential", "static_residential"):
        return int(item["id"])
    for item in resultados:
      if item.get("status") == "active" and (item.get("proxy_type") or "").lower() == "shared":
        if (item.get("proxy_subtype") or "").lower() != "default":
          return int(item["id"])
    return None

  def _listar_proxies(self, plan_id: int) -> list[dict]:
    proxies: list[dict] = []
    pagina = 1
    while pagina <= 10:
      query = urllib.parse.urlencode(
        {
          "mode": "direct",
          "page": pagina,
          "page_size": 100,
          "plan_id": plan_id,
        }
      )
      dados = self._get_json(f"{URL_LISTA}?{query}")
      if not dados:
        break
      for item in dados.get("results") or []:
        if not item.get("valid", True):
          continue
        if (item.get("country_code") or "").upper() not in ("BR", ""):
          continue
        host = item.get("proxy_address")
        porta = item.get("port")
        usuario = item.get("username")
        senha = item.get("password")
        if not host or not porta or not usuario or not senha:
          continue
        proxies.append(
          {
            "host": str(host),
            "port": int(porta),
            "username": str(usuario),
            "password": str(senha),
            "cidade": item.get("city_name"),
            "asn": item.get("asn_name"),
          }
        )
      if not dados.get("next"):
        break
      pagina += 1
    return proxies

  def _get_json(self, url: str) -> Optional[dict]:
    request = urllib.request.Request(
      url,
      headers={
        "Authorization": f"Token {self._token}",
        "Accept": "application/json",
      },
    )
    try:
      with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
      corpo = erro.read().decode("utf-8", errors="replace")[:300]
      logger.warning("Webshare HTTP %s: %s", erro.code, corpo)
    except Exception as erro:
      logger.warning("Falha na API Webshare: %s", erro)
    return None

  @staticmethod
  def _extrair_host(proxy: Optional[str]) -> Optional[str]:
    if not proxy:
      return None
    texto = proxy.strip()
    if "://" in texto:
      sem_scheme = texto.split("://", 1)[1]
      if "@" in sem_scheme:
        sem_scheme = sem_scheme.split("@", 1)[1]
      return sem_scheme.split(":")[0]
    return texto.split(":")[0]
