import logging
from typing import List, Optional
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page

from portal_fornecedores.config.settings import Settings, get_settings
from portal_fornecedores.models.entidades import DadosRota

logger = logging.getLogger(__name__)


class CargasPage:
  """Espelha ListandoRotas2.listar_todas_rotas + filtros do legado."""

  SELECTOR_EMPRESA = "#mnuPrincipal_lstEmpresas"
  SELECTOR_PESQUISA = "#ctlLoadedControl_btnPesquisa"
  SELECTOR_CLUSTER = "#ctlLoadedControl_ddlCluster"
  SELECTOR_FILTRAR = "#ctlLoadedControl_btnFiltrar"
  SELECTOR_TABELA = "#ctlLoadedControl_dgRight"

  def __init__(self, page: Page, settings: Optional[Settings] = None):
    self._page = page
    self._settings = settings or get_settings()
    self._quantidade_verificacoes = 0

  def atualizar_page(self, page: Page) -> None:
    self._page = page

  def esta_na_pagina_cargas(self) -> bool:
    query = urlparse(self._page.url).query
    return (
      "cmp=SUCargaProgramadaList.ascx" in query
      or "cmp=SUCargaProgramada.ascx" in query
    )

  def listar_todas_rotas(self, tempo_espera_seg: int = 30, on_status=None) -> None:
    """
    Mesmo fluxo do legado ListandoRotas2.listar_todas_rotas:
    1) Se já está em SUCargaProgramada → espera + refresh e retorna
    2) Senão → empresa 85 → URL cargas → btnPesquisa
    """
    status = on_status or (lambda msg: None)
    status("BUSCANDO TODAS AS ROTAS...")

    query = urlparse(self._page.url).query
    if self._quantidade_verificacoes >= 1 and (
      query == "cmp=SUCargaProgramadaList.ascx" or "cmp=SUCargaProgramada.ascx" in query
    ):
      status(f"Aguardando {tempo_espera_seg}s para verificar novamente...")
      self._page.wait_for_timeout(tempo_espera_seg * 1000)
    else:
      logger.info("Login novamente ou ainda nao verificou todas as cargas")

    self._quantidade_verificacoes += 1

    if self.esta_na_pagina_cargas():
      status("Ja esta na tela correta — recarregando para conferir clusters")
      self._page.reload(wait_until="domcontentloaded")
      self._page.wait_for_timeout(1000)
      return

    status("Selecionando empresa Solucoes Usiminas (85)...")
    self._page.wait_for_selector(self.SELECTOR_EMPRESA, timeout=30_000)
    self._page.locator(self.SELECTOR_EMPRESA).click()
    self._page.wait_for_timeout(200)

    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=15_000):
        self._page.select_option(self.SELECTOR_EMPRESA, value=self._settings.empresa_usiminas_id)
    except Exception:
      self._page.select_option(self.SELECTOR_EMPRESA, value=self._settings.empresa_usiminas_id)
    self._page.wait_for_timeout(500)

    status("Abrindo tela de carga programada...")
    self._page.goto(self._settings.url_cargas, wait_until="domcontentloaded")
    self._page.wait_for_timeout(500)

    if "cmp=login.ascx" in urlparse(self._page.url).query:
      raise RuntimeError("Sessao expirou ao abrir cargas (voltou para login)")

    status("Clicando em Pesquisar...")
    self._page.wait_for_selector(self.SELECTOR_PESQUISA, timeout=20_000)
    self._page.locator(self.SELECTOR_PESQUISA).click()
    self._page.wait_for_load_state("domcontentloaded")
    self._page.wait_for_timeout(1000)

    # Garante que o filtro de cluster apareceu (tela de listagem)
    self._page.wait_for_selector(self.SELECTOR_CLUSTER, timeout=20_000)
    status("Navegacao para cargas concluida")
    logger.info("Navegacao para pagina de rotas concluida")

  def obter_clusters_portal(self) -> List[str]:
    self._page.wait_for_selector(self.SELECTOR_CLUSTER, timeout=15_000)
    options = self._page.locator(f"{self.SELECTOR_CLUSTER} option")
    clusters = []
    for index in range(options.count()):
      texto = options.nth(index).inner_text().strip()
      if texto:
        clusters.append(texto)
    logger.info("Destinos disponiveis no portal: %s", clusters)
    return clusters

  def selecionar_cluster(self, nome_cluster: str) -> bool:
    total = self._page.locator(f"{self.SELECTOR_CLUSTER} option").count()
    for index in range(total):
      opcao = self._page.locator(f"{self.SELECTOR_CLUSTER} option").nth(index)
      if opcao.inner_text().strip().lower() == nome_cluster.strip().lower():
        valor = opcao.get_attribute("value")
        if valor is not None:
          self._page.select_option(self.SELECTOR_CLUSTER, value=valor)
        else:
          self._page.select_option(self.SELECTOR_CLUSTER, label=nome_cluster)
        self._page.wait_for_timeout(1000)
        return True
    return False

  def aplicar_filtro(self) -> None:
    logger.info("Aplicando filtro de rota...")
    self._page.locator(self.SELECTOR_FILTRAR).click()
    self._page.wait_for_load_state("domcontentloaded")
    self._page.wait_for_timeout(500)

  def extrair_rotas_tabela(self) -> List[DadosRota]:
    tabela = self._page.locator(self.SELECTOR_TABELA)
    if tabela.count() == 0:
      logger.warning("Tabela de cargas nao encontrada (#ctlLoadedControl_dgRight)")
      return []

    html_tabela = tabela.evaluate("elemento => elemento.outerHTML")
    dataframe = pd.read_html(html_tabela, skiprows=1)[0]
    dados_tabela = dataframe.to_dict("split")["data"]
    rotas = []

    for linha in dados_tabela:
      if len(linha) < 12:
        continue
      doc = self._limpar_valor(linha[0])
      if not doc:
        continue
      rotas.append(
        DadosRota(
          numero_documento=doc,
          data=self._limpar_valor(linha[3]),
          compartilhado=self._limpar_valor(linha[4]),
          prioridade=self._limpar_valor(linha[5]),
          tipo_transporte=self._limpar_valor(linha[6]),
          peso_total=self._limpar_valor(linha[7]),
          unidade_peso=self._limpar_valor(linha[8]),
          planta_origem=self._limpar_valor(linha[9]),
          cluster=self._limpar_valor(linha[10]),
          estado=self._limpar_valor(linha[11]),
        )
      )

    logger.info("Cargas encontradas na tabela: %s", len(rotas))
    return rotas

  def obter_id_botao_vincular(self, numero_documento: str) -> Optional[str]:
    html = self._page.content()
    soup = BeautifulSoup(html, "lxml")
    tabela = soup.find("table", id="ctlLoadedControl_dgRight")
    if not tabela:
      return None

    for linha in tabela.find_all("tr")[1:]:
      celulas = linha.find_all("td")
      if len(celulas) < 3:
        continue
      doc_linha = celulas[0].get_text(strip=True)
      if doc_linha == str(numero_documento):
        botao = celulas[2].find("input")
        if botao:
          return botao.get("id")
    return None

  def clicar_vincular(self, numero_documento: str) -> bool:
    botao_id = self.obter_id_botao_vincular(numero_documento)
    if not botao_id:
      logger.error("Botao vincular nao encontrado para doc %s", numero_documento)
      return False
    self._page.locator(f"#{botao_id}").click()
    self._page.wait_for_load_state("domcontentloaded")
    self._page.wait_for_timeout(500)
    return True

  def voltar(self) -> None:
    self._page.go_back(wait_until="domcontentloaded")
    self._page.wait_for_timeout(500)

  @staticmethod
  def _limpar_valor(valor) -> str:
    if valor is None:
      return ""
    texto = str(valor).strip()
    if texto.lower() in ("nan", "none", "null", ""):
      return ""
    return texto
