import logging
import random
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

  def _obter_acao_recaptcha(self, botao_selector: Optional[str] = None) -> str:
    seletor = botao_selector or self.SELECTOR_BOTAO
    classe = ""
    try:
      if self._page.locator(seletor).count() > 0:
        classe = self._page.locator(seletor).first.get_attribute("class") or ""
    except Exception:
      classe = ""
    marcador = "captcha"
    indice = classe.lower().find(marcador)
    if indice < 0:
      return "LOGIN" if seletor == self.SELECTOR_BOTAO else "SUBMIT"
    acao = classe[indice + len(marcador) :].lstrip("-").strip().split(" ")[0]
    return acao or ("LOGIN" if seletor == self.SELECTOR_BOTAO else "SUBMIT")

  def _aquecer_interacao_humana(self) -> None:
    """Pequenos movimentos/scroll antes do execute — ajuda o score do reCAPTCHA v3."""
    try:
      viewport = self._page.viewport_size or {"width": 1366, "height": 768}
      for _ in range(3):
        pos_x = random.randint(80, max(120, viewport["width"] - 80))
        pos_y = random.randint(80, max(120, viewport["height"] - 80))
        self._page.mouse.move(pos_x, pos_y, steps=random.randint(8, 18))
        self._page.wait_for_timeout(random.randint(80, 220))
      self._page.mouse.wheel(0, random.randint(40, 120))
      self._page.wait_for_timeout(random.randint(150, 400))
    except Exception:
      pass

  def _preencher_token_recaptcha(
    self,
    botao_selector: Optional[str] = None,
    obrigatorio: bool = True,
  ) -> bool:
    """Gera token reCAPTCHA v3 (WAF session) imediatamente antes do postback ASP.NET.

    Se obrigatorio=False, falhas de carga do grecaptcha só retornam False
    (útil no Filtrar, onde o portal às vezes não exige token).
    """
    if self._page.locator("#reCaptcha_Key").count() == 0:
      return False

    chave = self._page.locator("#reCaptcha_Key").input_value()
    if not chave:
      return False

    acao = self._obter_acao_recaptcha(botao_selector=botao_selector)
    logger.info("Gerando token reCAPTCHA (action=%s)...", acao)

    try:
      self._page.wait_for_function(
        "() => typeof grecaptcha !== 'undefined' && !!grecaptcha.execute",
        timeout=8_000 if not obrigatorio else 20_000,
      )
    except PlaywrightTimeoutError as erro:
      if not obrigatorio:
        logger.warning("reCAPTCHA nao disponivel — seguindo sem token manual")
        return False
      raise RuntimeError("reCAPTCHA nao carregou a tempo") from erro

    self._aquecer_interacao_humana()

    token = self._page.evaluate(
      """async ({ siteKey, action }) => {
        await new Promise((resolve) => grecaptcha.ready(resolve));
        // Pequena espera após ready — tokens gerados no instante do load costumam ter score pior
        await new Promise((resolve) => setTimeout(resolve, 400 + Math.floor(Math.random() * 500)));
        return await grecaptcha.execute(siteKey, { action });
      }""",
      {"siteKey": chave, "action": acao},
    )
    if not token:
      if not obrigatorio:
        logger.warning("Falha ao gerar token reCAPTCHA — seguindo sem token manual")
        return False
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

  @staticmethod
  def _parece_credencial_invalida(detalhe: str) -> bool:
    texto = (detalhe or "").lower()
    if not texto:
      return False
    # Captcha/WAF não é senha — deixa o fluxo de rotação de proxy tratar
    if "captcha" in texto or "recaptcha" in texto:
      return False
    marcadores = (
      "senha",
      "usuário",
      "usuario",
      "login",
      "credencial",
      "incorret",
      "inválid",
      "invalid",
      "não confere",
      "nao confere",
      "autentica",
      "acesso negado",
    )
    return any(marcador in texto for marcador in marcadores)

  def fazer_login(self, usuario: str, senha: str) -> None:
    self.navegar()
    self._page.wait_for_selector(self.SELECTOR_USUARIO, timeout=30_000)
    self.aceitar_cookies()
    self._page.wait_for_timeout(800)

    campo_usuario = self._page.locator(self.SELECTOR_USUARIO)
    campo_senha = self._page.locator(self.SELECTOR_SENHA)
    campo_usuario.click()
    campo_usuario.fill(usuario)
    self._page.wait_for_timeout(350)
    campo_senha.click()
    campo_senha.fill(senha)
    self._page.wait_for_timeout(500)

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

    # Token gerado imediatamente antes do clique — tokens velhos / score baixo viram "Captcha inválido"
    self._preencher_token_recaptcha()
    self._page.wait_for_timeout(400)
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
      from portal_fornecedores.errors import CredencialPortalInvalida

      detalhe = self._mensagem_erro_login() or "credencial invalida, reCAPTCHA/WAF ou bloqueio do portal"
      if self._parece_credencial_invalida(detalhe):
        raise CredencialPortalInvalida(
          f"Usuário ou senha do portal incorretos ({detalhe}). "
          "Corrija em Parâmetros e inicie a frota novamente."
        )
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
