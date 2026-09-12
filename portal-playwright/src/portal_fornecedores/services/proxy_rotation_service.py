"""Proxy via API Webshare: escolha inicial, sticky, teste de conectividade e rotação contínua."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ARQUIVO_PROXY = Path("/app/logs/proxy_atual.txt")
URL_LISTA = "https://proxy.webshare.io/api/v2/proxy/list/"
URL_PLANOS = "https://proxy.webshare.io/api/v2/subscription/plan/"
TEMPO_EXPIRACAO_FALHA_SEG = 1800  # 30 minutos de quarentena para IP com falha


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
    self._plan_id = int(plan_id) if plan_id else None
    self._arquivo = arquivo_proxy
    self._slot = max(1, min(3, int(slot or 1)))
    self._cliente = (cliente or "").strip().lower() or "default"
    self._ips_rejeitados: dict[str, float] = {}  # host -> timestamp

  @property
  def habilitado(self) -> bool:
    return bool(self._token)

  def registrar_falha(self, host: Optional[str], motivo: str = "") -> None:
    """Registra IP em quarentena temporária para evitar reuso imediato."""
    host_limpo = self._extrair_host(host)
    if host_limpo:
      self._ips_rejeitados[host_limpo] = time.time()
      logger.info(
        "IP %s colocado em quarentena temporaria (%s). Total em quarentena: %d",
        host_limpo,
        motivo or "falha",
        len(self._ips_rejeitados),
      )

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

  def testar_conectividade(self, item_proxy: dict, timeout_seg: float = 3.5) -> bool:
    """Verifica se o proxy consegue atingir o portal com resposta HTTP válida."""
    host = item_proxy.get("host")
    porta = item_proxy.get("port")
    usuario = item_proxy.get("username")
    senha = item_proxy.get("password")
    if not host or not porta:
      return False

    url_proxy = f"http://{usuario}:{senha}@{host}:{porta}" if usuario and senha else f"http://{host}:{porta}"
    handler = urllib.request.ProxyHandler({"http": url_proxy, "https": url_proxy})
    opener = urllib.request.build_opener(handler)
    requisicao = urllib.request.Request(
      "https://portal.e-fornecedores.ind.br/",
      headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    try:
      with opener.open(requisicao, timeout=timeout_seg) as resposta:
        if resposta.status in (200, 301, 302):
          return True
    except Exception:
      pass
    return False

  def resolver_proxy_inicial(self, proxy_env: Optional[str] = None) -> Optional[str]:
    """
    Prioridade:
      1) API Webshare — reaproveita IP salvo se ainda existir e responder ao portal; senão escolhe outro verificado
      2) PROXY do .env (fallback)
    """
    if self.habilitado:
      host_salvo = self._extrair_host(self.carregar_proxy_salvo())
      escolhido = self._escolher_da_api(preferir_host=host_salvo)
      if escolhido:
        self.salvar_proxy(escolhido)
        host = escolhido.split(":")[0]
        logger.info(
          "Proxy via API Webshare verificado (cliente=%s slot=%s): %s",
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
    """Rotaciona para um novo proxy funcional da Webshare, evitando o atual e os rejeitados."""
    if not self.habilitado:
      logger.warning("WEBSHARE_API_TOKEN nao configurado — sem rotacao automatica")
      return None

    host_atual = self._extrair_host(proxy_atual)
    if host_atual:
      self.registrar_falha(host_atual, motivo="rotacao solicitada")

    novo = self._escolher_da_api(preferir_host=None, evitar_host=host_atual)
    if not novo:
      logger.warning("Nenhum proxy novo funcional retornado pela Webshare")
      return None

    self.salvar_proxy(novo)
    logger.info(
      "Proxy trocado e verificado: %s -> %s",
      host_atual or "(nenhum)",
      novo.split(":")[0],
    )
    return novo

  def _limpar_quarentena_expirada(self) -> None:
    agora = time.time()
    hosts_expirados = [
      host for host, momento in self._ips_rejeitados.items()
      if agora - momento > TEMPO_EXPIRACAO_FALHA_SEG
    ]
    for host in hosts_expirados:
      self._ips_rejeitados.pop(host, None)

  def _obter_lista_planos_para_tentar(self) -> list[int]:
    """Retorna lista de plan_ids para buscar proxies (prioriza ISP, depois shared)."""
    if self._plan_id:
      # Se configurado explicitamente, tenta ele primeiro, mas descobre outros como fallback
      planos_ativos = self._descobrir_todos_planos_ativos()
      outros = [pid for pid in planos_ativos if pid != self._plan_id]
      return [self._plan_id] + outros

    return self._descobrir_todos_planos_ativos()

  def _descobrir_todos_planos_ativos(self) -> list[int]:
    """Retorna planos ativos priorizando ISP/residential, depois shared."""
    dados = self._get_json(URL_PLANOS)
    resultados = (dados or {}).get("results") or []
    planos_isp: list[int] = []
    planos_shared: list[int] = []

    for item in resultados:
      if item.get("status") != "active":
        continue
      plano_id = int(item["id"])
      tipo = (item.get("proxy_type") or "").lower()
      subtipo = (item.get("proxy_subtype") or "").lower()
      if subtipo in ("isp", "residential", "static_residential"):
        planos_isp.append(plano_id)
      elif tipo == "shared":
        planos_shared.append(plano_id)

    # ISP primeiro, depois shared
    return planos_isp + planos_shared

  def _escolher_da_api(
    self,
    preferir_host: Optional[str] = None,
    evitar_host: Optional[str] = None,
  ) -> Optional[str]:
    self._limpar_quarentena_expirada()
    planos = self._obter_lista_planos_para_tentar()
    if not planos:
      logger.warning("Nenhum plano ativo encontrado na Webshare")
      return None

    proxies_totais: list[dict] = []
    for plano_id in planos:
      lista_plano = self._listar_proxies(plano_id)
      if lista_plano:
        proxies_totais.extend(lista_plano)
        # Se achou proxies em plano ISP residencial, não precisa misturar de imediato
        if len(proxies_totais) >= 15:
          break

    if not proxies_totais:
      logger.warning("Lista de proxies vazia em todos os planos da Webshare")
      return None

    # Se preferir_host for especificado e nao estiver em quarentena, testa antes de reutilizar
    if preferir_host and preferir_host != evitar_host and preferir_host not in self._ips_rejeitados:
      for item in proxies_totais:
        if item["host"] == preferir_host:
          if self.testar_conectividade(item, timeout_seg=3.0):
            return self._formatar(item)
          self.registrar_falha(preferir_host, motivo="teste de conectividade falhou")
          break

    # Filtra proxies descartando o host a evitar e os em quarentena
    candidatos = [
      item for item in proxies_totais
      if item["host"] != evitar_host and item["host"] not in self._ips_rejeitados
    ]

    # Se todos estiverem em quarentena, zera a quarentena e tenta novamente
    if not candidatos:
      logger.info("Todos os proxies estao em quarentena — resetando quarentena para tentar novamente")
      self._ips_rejeitados.clear()
      candidatos = [item for item in proxies_totais if item["host"] != evitar_host]
      if not candidatos:
        candidatos = proxies_totais

    # Ordena a lista com offset de cliente e slot para espalhar robos
    indice_inicial = self._indice_cliente_slot(len(candidatos))
    candidatos_ordenados = candidatos[indice_inicial:] + candidatos[:indice_inicial]

    # Itera testando conectividade de cada candidato
    for item in candidatos_ordenados:
      host = item["host"]
      logger.debug("Testando conectividade do proxy %s...", host)
      if self.testar_conectividade(item, timeout_seg=3.0):
        logger.info("Proxy funcional selecionado: %s", host)
        return self._formatar(item)
      self.registrar_falha(host, motivo="sem resposta do portal no teste rapido")

    logger.warning("Nenhum proxy respondeu ao teste rapido de conectividade com o portal")
    # Fallback: retorna o primeiro candidato mesmo sem confirmacao rapida
    if candidatos:
      return self._formatar(candidatos[0])
    return None

  def _offset_cliente(self, total: int) -> int:
    """Espalha clientes no pool (MadeForte no início, Boro na metade, etc.)."""
    if total <= 1:
      return 0
    if "boro" in self._cliente:
      return max(1, total // 2)
    if "madeforte" in self._cliente or "made" in self._cliente:
      return 0
    return sum(ord(caractere) for caractere in self._cliente) % total

  def _indice_cliente_slot(self, total: int) -> int:
    if total <= 0:
      return 0
    return (self._offset_cliente(total) + (self._slot - 1) * 3) % total

  @staticmethod
  def _formatar(item: dict) -> str:
    return f"{item['host']}:{item['port']}:{item['username']}:{item['password']}"

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
      with urllib.request.urlopen(request, timeout=25) as response:
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
