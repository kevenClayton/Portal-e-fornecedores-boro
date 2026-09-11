import logging
import os
import re
import shutil
import subprocess
from typing import Callable, Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from portal_fornecedores.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


def _user_agent_chrome() -> str:
  """Alinha o UA com a versão real do Chrome — mismatch derruba score do reCAPTCHA."""
  versao = "131.0.0.0"
  for comando in (
    ["google-chrome", "--version"],
    ["google-chrome-stable", "--version"],
    ["chromium-browser", "--version"],
  ):
    if not shutil.which(comando[0]):
      continue
    try:
      saida = subprocess.check_output(comando, text=True, stderr=subprocess.DEVNULL, timeout=5)
      match = re.search(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", saida)
      if match:
        versao = f"{match.group(1)}.0.0.0"
        break
    except Exception:
      continue
  return (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    f"Chrome/{versao} Safari/537.36"
  )


SCRIPT_STEALTH = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = window.chrome || { runtime: {} };
Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
"""


class BrowserManager:
  def __init__(self, settings: Optional[Settings] = None):
    self._settings = settings or get_settings()
    self._playwright: Optional[Playwright] = None
    self._browser: Optional[Browser] = None
    self._context: Optional[BrowserContext] = None
    self._page: Optional[Page] = None
    self._usa_cloak = False

  @property
  def page(self) -> Page:
    if not self._page:
      raise RuntimeError("Browser não iniciado. Chame start() primeiro.")
    return self._page

  def start(self) -> Page:
    if self._deve_usar_cloak():
      try:
        return self._iniciar_cloak()
      except Exception as erro:
        logger.exception("Falha ao iniciar CloakBrowser — fallback Playwright/Chrome: %s", erro)

    return self._iniciar_playwright_classico()

  def _deve_usar_cloak(self) -> bool:
    if not getattr(self._settings, "usar_cloakbrowser", True):
      return False
    chave = self._license_key()
    if not chave:
      logger.warning("CLOAKBROWSER_LICENSE_KEY vazia — usando Playwright/Chrome")
      return False
    try:
      import cloakbrowser  # noqa: F401
    except ImportError:
      logger.warning("Pacote cloakbrowser nao instalado — usando Playwright/Chrome")
      return False
    return True

  def _license_key(self) -> str:
    bruto = (
      getattr(self._settings, "cloakbrowser_license_key", None)
      or os.getenv("CLOAKBROWSER_LICENSE_KEY")
      or ""
    )
    # E-mails/tradutores às vezes inserem espaços no meio da chave
    return "".join(str(bruto).split())

  def _iniciar_cloak(self) -> Page:
    from cloakbrowser import launch

    self._usa_cloak = True
    chave = self._license_key()
    proxy_url = self._proxy_url(self._settings.proxy) if self._settings.proxy else None

    chrome_args = [
      "--no-first-run",
      "--no-default-browser-check",
    ]
    if os.getenv("DOCKER", "").lower() in ("1", "true", "yes"):
      chrome_args.extend(
        [
          "--no-sandbox",
          "--disable-dev-shm-usage",
        ]
      )

    humanize = bool(getattr(self._settings, "cloak_humanize", True))
    human_preset = getattr(self._settings, "cloak_human_preset", None) or "careful"
    geoip = bool(getattr(self._settings, "cloak_geoip", True)) and bool(proxy_url)

    logger.info(
      "Iniciando CloakBrowser (headless=%s humanize=%s preset=%s geoip=%s proxy=%s)",
      self._settings.headless,
      humanize,
      human_preset if humanize else "-",
      geoip,
      (self._settings.proxy or "").split(":")[0] if self._settings.proxy else "(nenhum)",
    )

    def _montar_kwargs(usar_geoip: bool) -> dict:
      kwargs = {
        "headless": self._settings.headless,
        "license_key": chave,
        "humanize": humanize,
        "args": list(chrome_args),
        "geoip": usar_geoip,
      }
      if humanize:
        kwargs["human_preset"] = human_preset
      if proxy_url:
        kwargs["proxy"] = proxy_url
      if not usar_geoip:
        kwargs["timezone"] = "America/Sao_Paulo"
        kwargs["locale"] = "pt-BR"
      if self._settings.slow_mo:
        kwargs["slow_mo"] = self._settings.slow_mo
      return kwargs

    try:
      self._browser = launch(**_montar_kwargs(geoip))
    except Exception as erro:
      mensagem = str(erro).lower()
      if geoip and ("geoip" in mensagem or "timed out" in mensagem):
        logger.warning(
          "CloakBrowser geoip falhou (%s) — tentando de novo com timezone/locale fixos BR",
          erro,
        )
        self._browser = launch(**_montar_kwargs(False))
      else:
        raise

    # Cloak já cuida do fingerprint — não forçar UA/stealth JS (conflita com o binário)
    self._page = self._browser.new_page()
    self._page.set_default_timeout(30_000)
    logger.info("CloakBrowser iniciado")
    return self._page

  def _iniciar_playwright_classico(self) -> Page:
    self._usa_cloak = False
    self._playwright = sync_playwright().start()

    chrome_args = [
      "--disable-blink-features=AutomationControlled",
      "--disable-infobars",
      "--no-first-run",
      "--no-default-browser-check",
    ]
    if os.getenv("DOCKER", "").lower() in ("1", "true", "yes") or not self._settings.usar_chrome_sistema:
      chrome_args.extend(
        [
          "--no-sandbox",
          "--disable-dev-shm-usage",
          "--disable-gpu",
        ]
      )

    launch_args = {
      "headless": self._settings.headless,
      "slow_mo": self._settings.slow_mo,
      "args": chrome_args,
      "ignore_default_args": ["--enable-automation"],
    }

    self._browser = self._abrir_navegador(launch_args)

    user_agent = _user_agent_chrome()
    context_options = {
      "user_agent": user_agent,
      "viewport": {"width": 1366, "height": 768},
      "locale": "pt-BR",
      "timezone_id": "America/Sao_Paulo",
      "extra_http_headers": {
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      },
    }
    logger.info("User-Agent: %s", user_agent)
    if self._settings.proxy:
      context_options["proxy"] = self._parse_proxy(self._settings.proxy)
      logger.info("Proxy configurado: %s", self._settings.proxy.split(":")[0])

    self._context = self._browser.new_context(**context_options)
    self._context.add_init_script(SCRIPT_STEALTH)
    self._page = self._context.new_page()
    self._page.set_default_timeout(30_000)
    logger.info("Browser Playwright iniciado (headless=%s)", self._settings.headless)
    return self._page

  def _abrir_navegador(self, launch_args: dict) -> Browser:
    preferir_chrome = (
      self._settings.usar_chrome_sistema
      or os.getenv("DOCKER", "").lower() in ("1", "true", "yes")
    )
    if preferir_chrome:
      tentativas = [
        ("Google Chrome do sistema", {"channel": "chrome"}),
        ("Microsoft Edge do sistema", {"channel": "msedge"}),
        ("Chromium Playwright", {}),
      ]
    else:
      tentativas = [
        ("Chromium Playwright", {}),
        ("Google Chrome do sistema", {"channel": "chrome"}),
      ]

    erros = []
    for nome, extras in tentativas:
      try:
        browser = self._playwright.chromium.launch(**launch_args, **extras)
        logger.info("Usando %s", nome)
        return browser
      except Exception as erro:
        erros.append(f"{nome}: {erro}")
        logger.warning("Nao foi possivel abrir %s: %s", nome, erro)

    raise RuntimeError(
      "Nao foi possivel abrir o navegador. Detalhes: " + " | ".join(erros)
    )

  def stop(self) -> None:
    try:
      if self._page and not self._page.is_closed():
        self._page.close()
    except Exception:
      pass
    self._page = None

    if self._usa_cloak:
      # close() do Cloak também encerra o Playwright interno
      if self._browser:
        try:
          self._browser.close()
        except Exception as erro:
          logger.warning("Erro ao fechar CloakBrowser: %s", erro)
      self._browser = None
      self._context = None
      self._playwright = None
      logger.info("CloakBrowser encerrado")
      return

    if self._context:
      try:
        self._context.close()
      except Exception:
        pass
      self._context = None
    if self._browser:
      try:
        self._browser.close()
      except Exception:
        pass
      self._browser = None
    if self._playwright:
      try:
        self._playwright.stop()
      except Exception:
        pass
      self._playwright = None
    logger.info("Browser Playwright encerrado")

  def _proxy_url(self, proxy_string: str) -> str:
    """Converte host:porta:user:pass → http://user:pass@host:porta (formato Cloak)."""
    partes = proxy_string.split(":")
    if len(partes) == 4:
      host, porta, usuario, senha = partes
      return f"http://{usuario}:{senha}@{host}:{porta}"
    if len(partes) == 2:
      return f"http://{partes[0]}:{partes[1]}"
    if "://" in proxy_string:
      return proxy_string
    return f"http://{proxy_string}"

  def _parse_proxy(self, proxy_string: str) -> dict:
    partes = proxy_string.split(":")
    if len(partes) == 4:
      return {
        "server": f"http://{partes[0]}:{partes[1]}",
        "username": partes[2],
        "password": partes[3],
      }
    if len(partes) == 2:
      return {"server": f"http://{partes[0]}:{partes[1]}"}
    return {"server": f"http://{proxy_string}"}

  def on_dialog(self, handler: Callable) -> None:
    self.page.on("dialog", handler)
