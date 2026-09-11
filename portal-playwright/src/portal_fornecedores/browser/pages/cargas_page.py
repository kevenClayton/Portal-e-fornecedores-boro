import logging
import random
import re
import time
from typing import List, Optional
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

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
  # Ciclos intermediários: reusa clusters e só Filtra (atualiza cargas nas rotas já conhecidas).
  # A cada N segundos força Pesquisar de novo (captura cluster/carga novos no portal).
  REUSO_PESQUISA_SEG = 180

  def __init__(self, page: Page, settings: Optional[Settings] = None):
    self._page = page
    self._settings = settings or get_settings()
    self._quantidade_verificacoes = 0
    self._ultima_pesquisa_ok_em = 0.0

  def atualizar_page(self, page: Page) -> None:
    self._page = page

  def esta_na_pagina_cargas(self) -> bool:
    query = urlparse(self._page.url).query
    return (
      "cmp=SUCargaProgramadaList.ascx" in query
      or "cmp=SUCargaProgramada.ascx" in query
    )

  def listar_todas_rotas(
    self,
    tempo_espera_seg: int = 30,
    on_status=None,
    on_heartbeat=None,
    robo_quantidade: int = 1,
    robo_slot: int = 1,
  ) -> None:
    """
    Fluxo de listagem de cargas (a cada ciclo):
      1) A partir do 2º ciclo: espera (T * N) com defasagem por slot
         para a frota pesquisar a cada T segundos sem furos
      2) Serviços → Vincular Documento de Transporte → Pesquisar
    """
    status = on_status or (lambda msg: None)
    heartbeat = on_heartbeat or (lambda: None)
    quantidade = max(1, min(3, int(robo_quantidade or 1)))
    slot = max(1, min(3, int(robo_slot or 1)))
    cadencia = max(1, int(tempo_espera_seg or 30))
    espera_individual = cadencia * quantidade
    offset = (slot - 1) * cadencia

    status(f"BUSCANDO TODAS AS ROTAS... (slot {slot}/{quantidade})")

    if self._quantidade_verificacoes == 0 and offset > 0:
      status(f"Defasagem inicial do slot {slot}: aguardando {offset}s...")
      self._aguardar_segundos(offset, heartbeat, on_status=status)

    if self._quantidade_verificacoes >= 1:
      status(
        f"Aguardando {espera_individual}s (frota={quantidade}, cadência={cadencia}s) "
        f"antes da próxima busca do slot {slot}..."
      )
      self._aguardar_segundos(espera_individual, heartbeat, on_status=status)

    self._quantidade_verificacoes += 1
    self._abrir_cargas_e_pesquisar(status)

  def _aguardar_segundos(self, segundos: int, heartbeat, on_status=None) -> None:
    total_seg = max(0, int(segundos))
    restante_ms = total_seg * 1000
    proximo_aviso_em = 15  # segundos decorridos
    while restante_ms > 0:
      passo = min(2000, restante_ms)
      self._page.wait_for_timeout(passo)
      restante_ms -= passo
      try:
        heartbeat()
      except Exception:
        pass
      decorrido = total_seg - (restante_ms // 1000)
      if on_status and decorrido >= proximo_aviso_em and restante_ms > 0:
        on_status(f"Aguardando próximo ciclo... {restante_ms // 1000}s restantes")
        proximo_aviso_em = decorrido + 15

  def _pausar(self, minimo_ms: int = 900, maximo_ms: int = 1800) -> None:
    """Pausa variável para não parecer clique robótico."""
    if maximo_ms < minimo_ms:
      maximo_ms = minimo_ms
    self._page.wait_for_timeout(random.randint(minimo_ms, maximo_ms))

  def _cluster_visivel(self) -> bool:
    try:
      locator = self._page.locator(self.SELECTOR_CLUSTER)
      return locator.count() > 0 and locator.first.is_visible(timeout=1_500)
    except Exception:
      return False

  def _selecionar_empresa_usiminas(self, status) -> None:
    status("Selecionando empresa Solucoes Usiminas...")
    self._page.wait_for_selector(self.SELECTOR_EMPRESA, timeout=30_000)
    self._pausar(700, 1400)
    select = self._page.locator(self.SELECTOR_EMPRESA)
    select.click()
    self._pausar(400, 900)

    valor_config = str(self._settings.empresa_usiminas_id or "85")
    opcoes = select.locator("option")
    valor_escolhido = None
    label_escolhido = ""
    preferidos = (
      "soluções usiminas",
      "solucoes usiminas",
      "soluções usiminas s",
    )
    for index in range(opcoes.count()):
      opcao = opcoes.nth(index)
      label = (opcao.inner_text() or "").strip()
      valor = opcao.get_attribute("value") or ""
      label_norm = label.lower()
      # Evita "Soluções em Aço..." se existir a opção curta SOLUÇÕES USIMINAS
      if any(pref == label_norm or label_norm.startswith(pref) for pref in preferidos):
        if "aço" in label_norm or "aco" in label_norm:
          continue
        valor_escolhido = valor
        label_escolhido = label
        break

    if not valor_escolhido:
      valor_escolhido = valor_config
      try:
        label_escolhido = select.locator(f"option[value='{valor_config}']").inner_text().strip()
      except Exception:
        label_escolhido = valor_config

    logger.info("Empresa selecionada: %s (value=%s)", label_escolhido, valor_escolhido)
    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=15_000):
        select.select_option(value=valor_escolhido)
    except Exception:
      select.select_option(value=valor_escolhido)
    self._pausar(1200, 2200)

  def _fechar_overlays(self) -> None:
    """Cookies/menus sobrepostos quebram o humanize do Cloak (pointer_events)."""
    from portal_fornecedores.browser.pages.login_page import LoginPage

    try:
      LoginPage(self._page, self._settings).aceitar_cookies()
    except Exception:
      pass
    try:
      self._page.evaluate(
        """() => {
          const seletores = [
            '#privacy-tools', '#privacytools', '.privacy-tools',
            '#cookie-banner', '.cookie-banner', '#onetrust-banner-sdk',
            'div[id*="cookie" i]', 'div[class*="cookie" i]',
          ];
          for (const seletor of seletores) {
            document.querySelectorAll(seletor).forEach((el) => {
              el.style.display = 'none';
              el.style.pointerEvents = 'none';
            });
          }
        }"""
      )
    except Exception:
      pass

  def _clicar_seguro(self, locator, timeout: int = 8_000) -> None:
    """Clique compatível com Cloak humanize; se cobrir/falhar, usa click JS."""
    self._fechar_overlays()
    try:
      locator.scroll_into_view_if_needed(timeout=timeout)
    except Exception:
      pass
    try:
      locator.click(timeout=timeout)
      return
    except Exception as erro:
      mensagem = str(erro).lower()
      if not any(
        trecho in mensagem
        for trecho in (
          "pointer_events",
          "covered",
          "not supported",
          "isolated-world",
          "timeout",
          "intercepts",
        )
      ):
        raise
      logger.warning("Clique humanizado falhou (%s) — usando click JS", erro)
    try:
      locator.evaluate("elemento => elemento.click()")
    except Exception:
      # fallback absoluto por id/css se o locator for o botão de pesquisa
      self._page.evaluate(
        """(seletor) => {
          const el = document.querySelector(seletor);
          if (el) el.click();
        }""",
        self.SELECTOR_PESQUISA,
      )

  def _clicar_pesquisar_nativo(self, botao_pesquisa) -> None:
    """Deixa o onsubmit do portal gerar o reCAPTCHA (fluxo mais próximo do humano)."""
    self._fechar_overlays()
    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=45_000):
        self._clicar_seguro(botao_pesquisa)
    except PlaywrightTimeoutError:
      self._clicar_seguro(botao_pesquisa)
      self._page.wait_for_load_state("domcontentloaded")

  def _clicar_pesquisar_com_token(self, login_helper, botao_pesquisa) -> None:
    """Gera token manualmente e desativa onsubmit assíncrono (fallback)."""
    self._fechar_overlays()
    login_helper._preencher_token_recaptcha(botao_selector=self.SELECTOR_PESQUISA)
    self._page.wait_for_timeout(random.randint(120, 280))
    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=45_000):
        self._clicar_seguro(botao_pesquisa)
    except PlaywrightTimeoutError:
      self._clicar_seguro(botao_pesquisa)
      self._page.wait_for_load_state("domcontentloaded")

  def _abrir_cargas_e_pesquisar(self, status) -> None:
    """Refaz o caminho de menu que dispara a busca nova no portal."""
    from portal_fornecedores.browser.pages.login_page import LoginPage

    login_helper = LoginPage(self._page, self._settings)
    login_helper.aceitar_cookies()
    login_helper.contornar_aviso_navegador()

    # Ciclo intermediário: mantém a tela de clusters e só refiltra depois (rota_service).
    # Evita captcha do Pesquisar a cada 15–35s; a cada REUSO_PESQUISA_SEG faz busca cheia.
    idade = time.time() - self._ultima_pesquisa_ok_em if self._ultima_pesquisa_ok_em else 10**9
    if self.REUSO_PESQUISA_SEG > 0 and self._cluster_visivel() and idade < self.REUSO_PESQUISA_SEG:
      restante = int(self.REUSO_PESQUISA_SEG - idade)
      status(
        f"Ciclo intermediario — sem Pesquisar/captcha; "
        f"refiltrando clusters com motorista (busca cheia em ~{restante}s)..."
      )
      return

    self._selecionar_empresa_usiminas(status)

    abriu_menu = self._abrir_via_menu_servicos(status)
    if not abriu_menu:
      status("Menu Serviços falhou — abrindo tela de cargas pela URL...")
      self._page.goto(self._settings.url_cargas, wait_until="domcontentloaded")
      self._pausar(1200, 2200)

    if "cmp=login.ascx" in urlparse(self._page.url).query:
      raise RuntimeError("Sessao expirou ao abrir cargas (voltou para login)")

    # Após abrir o menu, se a lista já veio pronta, registra e segue para Filtrar
    if self._cluster_visivel():
      self._ultima_pesquisa_ok_em = time.time()
      status("Tela de cargas ja com clusters — seguindo para filtros")
      return

    status("Clicando em Pesquisar (busca cheia)...")
    self._page.wait_for_selector(self.SELECTOR_PESQUISA, timeout=20_000)
    self._pausar(1500, 2800)

    max_tentativas = 3
    ultimo_erro = ""
    for tentativa in range(1, max_tentativas + 1):
      if tentativa > 1:
        status(f"Recaptcha na pesquisa falhou — nova tentativa {tentativa}/{max_tentativas} (mesmo IP)...")
        self._pausar(4000, 7000)

      botao_pesquisa = self._page.locator(self.SELECTOR_PESQUISA)
      if botao_pesquisa.count() == 0:
        raise RuntimeError("Botao Pesquisar sumiu da tela de cargas")

      botao_pesquisa.scroll_into_view_if_needed()
      self._pausar(500, 1000)

      # Alterna: nativo (onsubmit do portal) ↔ token manual
      if tentativa % 2 == 1:
        logger.info("Pesquisar tentativa %s: fluxo nativo (onsubmit do portal)", tentativa)
        self._clicar_pesquisar_nativo(botao_pesquisa)
      else:
        logger.info("Pesquisar tentativa %s: token manual reCAPTCHA", tentativa)
        self._clicar_pesquisar_com_token(login_helper, botao_pesquisa)

      self._pausar(1000, 1800)

      mensagem_erro = self._mensagem_erro_portal()
      if mensagem_erro and "captcha" in mensagem_erro.lower():
        ultimo_erro = mensagem_erro
        logger.warning(
          "Captcha rejeitado ao pesquisar (tentativa %s/%s): %s",
          tentativa,
          max_tentativas,
          mensagem_erro,
        )
        continue

      try:
        self._page.wait_for_selector(self.SELECTOR_CLUSTER, timeout=20_000)
      except PlaywrightTimeoutError:
        detalhe = mensagem_erro or self._mensagem_erro_portal() or "cluster nao apareceu apos Pesquisar"
        if "captcha" in detalhe.lower():
          ultimo_erro = detalhe
          logger.warning(
            "Cluster ausente com indício de captcha (tentativa %s/%s): %s",
            tentativa,
            max_tentativas,
            detalhe,
          )
          continue
        raise RuntimeError(f"Falha apos Pesquisar: {detalhe}")

      self._ultima_pesquisa_ok_em = time.time()
      status("Navegacao para cargas concluida")
      logger.info(
        "Navegacao para pagina de rotas concluida (menu=%s, tentativa captcha=%s)",
        abriu_menu,
        tentativa,
      )
      return

    raise RuntimeError(
      f"Captcha rejeitado ao pesquisar cargas apos {max_tentativas} tentativas "
      f"({ultimo_erro or 'Captcha inválido'})"
    )

  def _abrir_via_menu_servicos(self, status) -> bool:
    """
    Caminho humano do portal:
      Serviços → Vincular Documento de Transporte
    """
    try:
      status("Abrindo menu Serviços...")
      link_servicos = self._localizar_link_menu(
        padroes=[r"^Serviços$", r"^Servicos$", r"Serviços", r"Servicos"]
      )
      if not link_servicos:
        logger.warning("Link Serviços nao encontrado no menu")
        return False

      link_servicos.scroll_into_view_if_needed()
      self._pausar(600, 1200)
      self._fechar_overlays()
      # Pode ser dropdown (hover) ou ir para a página de Serviços
      try:
        link_servicos.hover(timeout=5_000)
      except Exception:
        pass
      self._pausar(700, 1300)
      try:
        with self._page.expect_navigation(wait_until="domcontentloaded", timeout=12_000):
          self._clicar_seguro(link_servicos, timeout=8_000)
        self._pausar(1200, 2200)
      except PlaywrightTimeoutError:
        # Sem navegação: provavelmente abriu submenu flutuante
        self._clicar_seguro(link_servicos, timeout=8_000)
        self._pausar(1000, 1800)
        try:
          link_servicos.hover(timeout=5_000)
        except Exception:
          pass
        self._pausar(800, 1500)

      status("Selecionando Vincular Documento de Transporte...")
      link_vincular = self._localizar_item_vincular_documento()
      if not link_vincular:
        logger.warning(
          "Item Vincular Documento nao encontrado. Links visiveis: %s",
          self._textos_menu_visiveis()[:20],
        )
        return False

      self._pausar(700, 1400)
      href = ""
      try:
        href = (link_vincular.get_attribute("href") or "").strip()
      except Exception:
        pass

      # Submenu SoftArtisans fica oculto no DOM; clique JS após abrir Serviços
      try:
        with self._page.expect_navigation(wait_until="domcontentloaded", timeout=30_000):
          clicou = self._page.evaluate(
            """() => {
              const seletores = [
                "a.menu_subitem[href*='SUCargaProgramada.ascx']",
                "a[href*='SUCargaProgramada.ascx'][href*='tipo=vnc']",
                "a[href*='SUCargaProgramada.ascx']",
              ];
              for (const seletor of seletores) {
                const link = document.querySelector(seletor);
                if (link) {
                  link.click();
                  return true;
                }
              }
              return false;
            }"""
          )
          if not clicou and href:
            alvo = href
            if not href.startswith("http"):
              base = self._settings.portal_url.rstrip("/")
              alvo = f"{base}/{href.lstrip('/')}"
            self._page.goto(alvo, wait_until="domcontentloaded")
      except PlaywrightTimeoutError:
        if href:
          base = self._settings.portal_url.rstrip("/")
          alvo = href if href.startswith("http") else f"{base}/{href.lstrip('/')}"
          logger.info("Navegacao pelo submenu sem evento — indo ao href: %s", alvo)
          self._page.goto(alvo, wait_until="domcontentloaded")
        else:
          raise
      self._pausar(1400, 2600)

      self._page.wait_for_selector(self.SELECTOR_PESQUISA, timeout=20_000)
      logger.info("Menu Serviços → Vincular Documento concluido")
      return True
    except Exception as erro:
      logger.warning("Falha ao navegar pelo menu Serviços: %s", erro)
      return False

  def _localizar_item_vincular_documento(self):
    """Prioriza href do portal; depois texto do menu."""
    candidatos_href = [
      self._page.locator("a[href*='SUCargaProgramada.ascx']"),
      self._page.locator("a[href*='SUCargaProgramada']"),
      self._page.locator("a[href*='cmp=SUCargaProgramada']"),
    ]
    for locator in candidatos_href:
      try:
        total = locator.count()
      except Exception:
        continue
      for indice in range(total):
        item = locator.nth(indice)
        try:
          # Submenu flyout às vezes está no DOM sem is_visible=True
          if item.count() == 0:
            continue
          href = (item.get_attribute("href") or "").lower()
          texto = (item.inner_text(timeout=1_000) or "").strip().lower()
          if "sucargaprogramada" in href or "vincular documento" in texto:
            box = item.bounding_box()
            if box or "sucargaprogramada" in href:
              return item
        except Exception:
          continue

    return self._localizar_link_menu(
      padroes=[
        r"Vincular Documento de Transporte",
        r"Vincular Documento",
      ],
      exigir_visivel=False,
    )

  def _textos_menu_visiveis(self) -> List[str]:
    textos: List[str] = []
    try:
      links = self._page.locator("a")
      total = min(links.count(), 80)
      for indice in range(total):
        try:
          texto = (links.nth(indice).inner_text(timeout=300) or "").strip()
          if texto:
            textos.append(texto[:80])
        except Exception:
          continue
    except Exception:
      pass
    return textos

  def _localizar_link_menu(self, padroes: List[str], exigir_visivel: bool = True):
    """Retorna o primeiro link que casa com algum padrão.

    Cloak humanize não aceita get_by_role / .filter() / locators encadeados —
    usa CSS :has-text e XPath simples.
    """
    for padrao in padroes:
      # remove âncoras ^$ para :has-text; mantém no xpath
      texto_livre = padrao.strip("^$").replace("\\", "")
      candidatos = [
        f'a:has-text("{texto_livre}")',
        f'#mnuPrincipal a:has-text("{texto_livre}")',
        f'td a:has-text("{texto_livre}")',
        f'xpath=//a[contains(normalize-space(.), "{texto_livre}")]',
        f'xpath=//*[@id="mnuPrincipal"]//a[contains(normalize-space(.), "{texto_livre}")]',
      ]
      for seletor in candidatos:
        try:
          locator = self._page.locator(seletor)
          total = locator.count()
        except Exception:
          continue
        for indice in range(total):
          item = locator.nth(indice)
          try:
            texto = (item.inner_text(timeout=500) or "").strip()
            if not re.search(padrao, texto, re.IGNORECASE):
              continue
            if exigir_visivel:
              if item.is_visible(timeout=800):
                return item
            else:
              return item
          except Exception:
            continue
    return None

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

  def _mensagem_erro_portal(self) -> str:
    for seletor in ("#ctlLoadedControl_strMessage", "#ctlLoadedControl_lblMessage", ".erro", ".error"):
      try:
        locator = self._page.locator(seletor)
        if locator.count() == 0:
          continue
        texto = (locator.first.inner_text(timeout=1_000) or "").strip()
        if texto:
          return texto
      except Exception:
        continue
    return ""

  def aplicar_filtro(self) -> None:
    """Aplica filtro do cluster. Preferência: clique nativo; token só se grecaptcha estiver pronto."""
    logger.info("Aplicando filtro de rota...")
    from portal_fornecedores.browser.pages.login_page import LoginPage

    botao = self._page.locator(self.SELECTOR_FILTRAR)
    botao.scroll_into_view_if_needed()
    self._pausar(300, 700)

    # Filtrar nem sempre exige token; não pode derrubar o ciclo se grecaptcha sumiu
    LoginPage(self._page, self._settings)._preencher_token_recaptcha(
      botao_selector=self.SELECTOR_FILTRAR,
      obrigatorio=False,
    )
    self._page.wait_for_timeout(200)
    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=30_000):
        self._clicar_seguro(botao)
    except PlaywrightTimeoutError:
      self._clicar_seguro(botao)
      self._page.wait_for_load_state("domcontentloaded")
    self._page.wait_for_timeout(500)

    mensagem = self._mensagem_erro_portal()
    if mensagem and "captcha" in mensagem.lower():
      raise RuntimeError(f"Captcha rejeitado ao filtrar cluster ({mensagem})")

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
