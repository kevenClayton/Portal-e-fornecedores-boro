"""Rotação de proxy Webshare quando o reCAPTCHA rejeita o IP atual."""

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
  ):
    self._token = (api_token or "").strip()
    self._plan_id = plan_id
    self._arquivo = arquivo_proxy
    self._slot = max(1, min(3, int(slot or 1)))

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

  def trocar_proxy(self, proxy_atual: Optional[str]) -> Optional[str]:
    if not self.habilitado:
      logger.warning("WEBSHARE_API_TOKEN nao configurado — sem rotacao automatica")
      return None

    host_atual = self._extrair_host(proxy_atual)
    plan_id = self._plan_id or self._descobrir_plan_isp()
    if not plan_id:
      logger.warning("Nenhum plano ISP/residential ativo encontrado na Webshare")
      return None

    proxies = self._listar_proxies(plan_id)
    if not proxies:
      logger.warning("Lista de proxies vazia (plan_id=%s)", plan_id)
      return None

    candidatos = [item for item in proxies if item["host"] != host_atual]
    if not candidatos:
      candidatos = proxies

    # Preferir o próximo da lista após o IP atual; defasa por slot da frota
    indice = (self._slot - 1) % len(proxies)
    if host_atual:
      for posicao, item in enumerate(proxies):
        if item["host"] == host_atual:
          indice = (posicao + self._slot) % len(proxies)
          break
    escolhido = proxies[indice]
    if escolhido["host"] == host_atual and len(candidatos) > 1:
      for item in candidatos:
        if item["host"] != host_atual:
          escolhido = item
          break

    novo = f"{escolhido['host']}:{escolhido['port']}:{escolhido['username']}:{escolhido['password']}"
    self.salvar_proxy(novo)
    logger.info(
      "Proxy trocado: %s -> %s (%s)",
      host_atual or "(nenhum)",
      escolhido["host"],
      escolhido.get("cidade") or escolhido.get("asn") or "",
    )
    return novo

  def _descobrir_plan_isp(self) -> Optional[int]:
    dados = self._get_json(URL_PLANOS)
    resultados = (dados or {}).get("results") or []
    # Preferência: ISP/residential ativo; evita o plano datacenter "default"
    for item in resultados:
      if item.get("status") != "active":
        continue
      subtype = (item.get("proxy_subtype") or "").lower()
      if subtype in ("isp", "residential", "static_residential"):
        return int(item["id"])
    for item in resultados:
      if item.get("status") == "active" and (item.get("proxy_type") or "").lower() == "shared":
        # fallback: não usar se for o único e subtype default — ainda assim evita ficar sem opções
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
      # http://user:pass@host:port
      sem_scheme = texto.split("://", 1)[1]
      if "@" in sem_scheme:
        sem_scheme = sem_scheme.split("@", 1)[1]
      return sem_scheme.split(":")[0]
    return texto.split(":")[0]
