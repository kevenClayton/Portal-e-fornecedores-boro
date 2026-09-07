import logging
from typing import Optional
from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from portal_fornecedores.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class LoginPage:
  SELECTOR_USUARIO = "#ctlLoadedControl_txtLogin"
  SELECTOR_SENHA = "#ctlLoadedControl_txtSenha"
  SELECTOR_BOTAO = "#ctlLoadedControl_btnOK"
  SELECTOR_EMPRESAS = "#mnuPrincipal_lstEmpresas"

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

  def _esta_na_tela_login(self) -> bool:
    if not self._pagina_aberta():
      return False
    if self._page.locator(self.SELECTOR_USUARIO).count() > 0:
      return True
    return "cmp=login.ascx" in urlparse(self._page.url).query

  def navegar(self) -> None:
    if not self._pagina_aberta():
      raise PlaywrightError("Browser/página fechados. Reinicie o robô e não feche a janela do Chrome.")

    self._page.goto(self._settings.portal_url, wait_until="domcontentloaded")
    self.aceitar_cookies()
    self.contornar_aviso_navegador()

  def aceitar_cookies(self) -> None:
    """Fecha banner de cookies Privacy Tools, se aparecer."""
    if not self._pagina_aberta():
      return

    # Privacy Tools carrega o banner de forma assíncrona
    try:
      self._page.wait_for_selector(
        "#privacytools-banner-consent, a.cc-btn.cc-dismiss, .cc-window",
        timeout=5_000,
        state="visible",
      )
    except PlaywrightTimeoutError:
      pass

    # API oficial do banner Privacy Tools
    try:
      aceito = self._page.evaluate(
        """() => {
          if (typeof enableAllCookies === 'function') {
            enableAllCookies();
            return true;
          }
          return false;
        }"""
      )
      if aceito:
        self._page.wait_for_timeout(400)
        logger.info("Banner de cookies aceito (enableAllCookies)")
        return
    except Exception:
      pass

    candidatos = [
      self._page.locator("a.cc-btn.cc-dismiss"),
      self._page.locator("#privacytools-banner-consent a.cc-btn.cc-dismiss"),
      self._page.locator("a[onclick*='enableAllCookies']"),
      self._page.locator("div.dp-bar-dismiss:has-text('Aceitar')"),
      self._page.locator("button:has-text('Aceitar')"),
      self._page.locator("a:has-text('Aceitar')"),
      self._page.locator("[id*='accept' i]"),
      self._page.locator("[class*='accept' i]:has-text('Aceitar')"),
    ]
    for locator in candidatos:
      try:
        if locator.count() > 0 and locator.first.is_visible(timeout=1_500):
          locator.first.click(timeout=2_000)
          self._page.wait_for_timeout(300)
          logger.info("Banner de cookies aceito")
          return
      except Exception:
        continue

  def _esta_no_aviso_navegador(self) -> bool:
    if not self._pagina_aberta():
      return False
    # Preferir seletores — o HTML de todas as páginas menciona browserinfo.ascx no JS
    if self._page.locator("#ctlLoadedControl_linkPT").count() > 0:
      return True
    if self._page.locator("#ctlLoadedControl_tbPT").count() > 0:
      return True
    return False

  def contornar_aviso_navegador(self) -> bool:
    """Contorna telas de 'Sites Confiáveis' / navegador inapropriado."""
    if not self._pagina_aberta():
      return False

    for _tentativa in range(12):
      if self._esta_no_aviso_navegador():
        break
      self._page.wait_for_timeout(500)
    else:
      return False

    logger.warning("Tela de bloqueio do navegador detectada — tentando contornar")
    self.aceitar_cookies()

    # Garante cookie de check (o portal redireciona para browserinfo se document.cookie == "")
    try:
      self._page.evaluate("() => { document.cookie = 'check=true; path=/'; }")
    except Exception:
      pass

    alvo = self._page.locator("#ctlLoadedControl_linkPT").first
    try:
      alvo.wait_for(state="visible", timeout=10_000)
      try:
        with self._page.expect_navigation(wait_until="domcontentloaded", timeout=25_000):
          alvo.click(force=True)
      except PlaywrightTimeoutError:
        self._page.evaluate("() => __doPostBack('ctlLoadedControl$linkPT','')")
        self._page.wait_for_load_state("domcontentloaded")
      self.aceitar_cookies()
      self._page.wait_for_timeout(1_000)

      if self._page.locator(self.SELECTOR_EMPRESAS).count() > 0:
        logger.info("Aviso do navegador contornado (menu empresas visivel)")
        return True

      if self._esta_na_tela_login():
        logger.warning("Link 'aqui' voltou para login — aviso nao liberou a sessao")
        return False

      if not self._esta_no_aviso_navegador():
        logger.info("Aviso do navegador contornado")
        return True
    except Exception as erro:
      logger.warning("Falha ao clicar no link do aviso: %s", erro)

    logger.error("Nao foi possivel contornar aviso do navegador")
    return False

  def _obter_acao_recaptcha(self) -> str:
    classe = self._page.locator(self.SELECTOR_BOTAO).get_attribute("class") or ""
    marcador = "captcha"
    indice = classe.lower().find(marcador)
    if indice < 0:
      return "LOGIN"
    acao = classe[indice + len(marcador) :].lstrip("-").strip().split(" ")[0]
    return acao or "LOGIN"

  def _preencher_token_recaptcha(self) -> bool:
    """Gera token reCAPTCHA v3 (WAF session) antes do postback do login."""
    if self._page.locator("#reCaptcha_Key").count() == 0:
      return False

    chave = self._page.locator("#reCaptcha_Key").input_value()
    if not chave:
      return False

    acao = self._obter_acao_recaptcha()
    logger.info("Gerando token reCAPTCHA (action=%s)...", acao)

    try:
      self._page.wait_for_function("() => typeof grecaptcha !== 'undefined' && !!grecaptcha.execute", timeout=20_000)
    except PlaywrightTimeoutError as erro:
      raise RuntimeError("reCAPTCHA nao carregou a tempo") from erro

    token = self._page.evaluate(
      """async ({ siteKey, action }) => {
        await new Promise((resolve) => grecaptcha.ready(resolve));
        return await grecaptcha.execute(siteKey, { action });
      }""",
      {"siteKey": chave, "action": acao},
    )
    if not token:
      raise RuntimeError("Falha ao gerar token reCAPTCHA")

    self._page.evaluate(
      """({ token, action }) => {
        const campoToken = document.getElementById('reCaptcha_Token');
        const campoAcao = document.getElementById('reCaptcha_Action');
        if (campoToken) campoToken.value = token;
        if (campoAcao) campoAcao.value = action;
        // Evita o handler assíncrono disparar de novo sem submitter no postback ASP.NET
        if (document.forms[0]) {
          document.forms[0].onsubmit = null;
        }
      }""",
      {"token": token, "action": acao},
    )
    logger.info("Token reCAPTCHA preenchido")
    return True

  def _mensagem_erro_login(self) -> str:
    try:
      locator = self._page.locator("#ctlLoadedControl_strMessage")
      if locator.count() > 0:
        texto = (locator.first.inner_text(timeout=1_000) or "").strip()
        if texto:
          return texto
    except Exception:
      pass
    return ""

  def fazer_login(self, usuario: str, senha: str) -> None:
    self.navegar()
    self._page.wait_for_selector(self.SELECTOR_USUARIO, timeout=30_000)
    self.aceitar_cookies()
    self._page.locator(self.SELECTOR_USUARIO).fill(usuario)
    self._page.locator(self.SELECTOR_SENHA).fill(senha)

    try:
      self._page.evaluate(
        """() => {
          const campo = document.getElementById('txtScriptEnabled');
          if (campo) campo.value = 'true';
          document.cookie = 'check=true; path=/';
        }"""
      )
    except Exception:
      pass

    # Pré-gera o token (mais estável no Docker) e evita o handler async do ASP.NET
    self._preencher_token_recaptcha()
    try:
      with self._page.expect_navigation(wait_until="domcontentloaded", timeout=45_000):
        self._page.locator(self.SELECTOR_BOTAO).click()
    except PlaywrightTimeoutError:
      self._page.wait_for_load_state("domcontentloaded")

    self.aceitar_cookies()
    self.contornar_aviso_navegador()
    self._page.wait_for_timeout(1_000)

    if self._esta_no_aviso_navegador():
      raise RuntimeError("Login bloqueado na tela de configuracao do navegador (Sites Confiaveis).")

    if self._esta_na_tela_login():
      detalhe = self._mensagem_erro_login() or "credencial invalida, reCAPTCHA/WAF ou bloqueio do portal"
      raise RuntimeError(f"Login nao concluiu: ainda na tela de login ({detalhe}).")

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

    self.aceitar_cookies()
    self.contornar_aviso_navegador()

    if not self._pagina_aberta():
      return False

    conteudo = self._page.content()
    if "Violacao" in conteudo:
      logger.warning("Violação detectada — aguardando 10s")
      self._page.wait_for_timeout(10_000)
      self._page.reload(wait_until="domcontentloaded")

    if self._esta_na_tela_login():
      return False

    if self._page.locator(self.SELECTOR_EMPRESAS).count() > 0:
      return True

    url_atual = self._page.url
    parametros = urlparse(url_atual).query

    if parametros == "cmp=Error.ascx":
      self.navegar()
      return False

    return parametros != ""

  def garantir_sessao(self, usuario: str, senha: str) -> None:
    if not self.esta_logado():
      self.fazer_login(usuario, senha)
