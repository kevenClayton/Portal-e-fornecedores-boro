import logging
from typing import Optional
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from portal_fornecedores.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class LoginPage:
  SELECTOR_USUARIO = "#ctlLoadedControl_txtLogin"
  SELECTOR_SENHA = "#ctlLoadedControl_txtSenha"
  SELECTOR_BOTAO = "#ctlLoadedControl_btnOK"

  def __init__(self, page: Page, settings: Optional[Settings] = None):
    self._page = page
    self._settings = settings or get_settings()

  def atualizar_page(self, page: Page) -> None:
    self._page = page

  def _pagina_aberta(self) -> bool:
    try:
      _ = self._page.url
      return not self._page.is_closed()
    except Exception:
      return False

  def navegar(self) -> None:
    if not self._pagina_aberta():
      raise PlaywrightError("Browser/página fechados. Reinicie o robô e não feche a janela do Chrome.")

    self._page.goto(self._settings.portal_url, wait_until="domcontentloaded")
    self.contornar_aviso_navegador()

  def contornar_aviso_navegador(self) -> bool:
    """Contorna telas de 'Sites Confiáveis' / navegador inapropriado."""
    if not self._pagina_aberta():
      return False

    conteudo = self._page.content()
    avisos = (
      "não está corretamente configurado",
      "not correctly configured",
      "Sites Confiáveis",
      "Trusted Sites",
      "navegador é inapropriado",
      "browser is unappropriate",
      "Utilize Microsoft Internet Explorer ou Google Chrome",
      "Use Microsoft Internet Explorer or Google Chrome",
    )
    if not any(aviso.lower() in conteudo.lower() for aviso in avisos):
      return False

    logger.warning("Tela de bloqueio do navegador detectada — tentando contornar")

    candidatos = [
      self._page.locator("a:has-text('clique aqui')"),
      self._page.locator("a:has-text('click here')"),
      self._page.locator("a:has-text('Clique aqui')"),
      self._page.locator("a:has-text('Click here')"),
      self._page.locator("a:has-text('aqui')"),
      self._page.locator("a[href*='Default.aspx']"),
      self._page.locator("a[href*='login']"),
    ]

    for locator in candidatos:
      try:
        if locator.count() > 0 and locator.first.is_visible():
          locator.first.click()
          self._page.wait_for_load_state("domcontentloaded")
          logger.info("Aviso do navegador contornado")
          return True
      except Exception:
        continue

    try:
      self._page.reload(wait_until="domcontentloaded")
    except Exception:
      return False
    return "ctlLoadedControl_txtLogin" in self._page.content()

  def fazer_login(self, usuario: str, senha: str) -> None:
    self.navegar()
    self._page.wait_for_selector(self.SELECTOR_USUARIO, timeout=30_000)
    self._page.locator(self.SELECTOR_USUARIO).fill(usuario)
    self._page.locator(self.SELECTOR_SENHA).fill(senha)
    self._page.locator(self.SELECTOR_BOTAO).click()
    self._page.wait_for_load_state("domcontentloaded")
    self.contornar_aviso_navegador()
    logger.info("Login realizado")

  def esta_logado(self) -> bool:
    if not self._pagina_aberta():
      return False

    url_atual = self._page.url
    # Na primeira execução a página está em about:blank — não dá reload nela.
    if url_atual in ("about:blank", "data:,", "") or not url_atual.startswith("http"):
      self.navegar()
    else:
      try:
        self._page.reload(wait_until="domcontentloaded")
      except PlaywrightError as erro:
        logger.warning("Falha ao recarregar página: %s", erro)
        self.navegar()

    self.contornar_aviso_navegador()

    if not self._pagina_aberta():
      return False

    conteudo = self._page.content()
    if "Violacao" in conteudo:
      logger.warning("Violação detectada — aguardando 10s")
      self._page.wait_for_timeout(10_000)
      self._page.reload(wait_until="domcontentloaded")

    url_atual = self._page.url
    parametros = urlparse(url_atual).query

    if parametros == "cmp=Error.ascx":
      self.navegar()
      return False

    if self._page.locator(self.SELECTOR_USUARIO).count() > 0:
      return False

    if parametros == "cmp=login.ascx":
      return False

    return parametros != ""

  def garantir_sessao(self, usuario: str, senha: str) -> None:
    if not self.esta_logado():
      self.fazer_login(usuario, senha)
