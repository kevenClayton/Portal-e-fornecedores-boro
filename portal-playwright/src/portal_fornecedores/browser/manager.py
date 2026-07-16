import logging
from typing import Callable, Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from portal_fornecedores.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

USER_AGENT_CHROME = (
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
  "AppleWebKit/537.36 (KHTML, like Gecko) "
  "Chrome/122.0.0.0 Safari/537.36"
)

SCRIPT_STEALTH = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = window.chrome || { runtime: {} };
Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
"""


class BrowserManager:
  def __init__(self, settings: Optional[Settings] = None):
    self._settings = settings or get_settings()
    self._playwright: Optional[Playwright] = None
    self._browser: Optional[Browser] = None
    self._context: Optional[BrowserContext] = None
    self._page: Optional[Page] = None

  @property
  def page(self) -> Page:
    if not self._page:
      raise RuntimeError("Browser não iniciado. Chame start() primeiro.")
    return self._page

  def start(self) -> Page:
    self._playwright = sync_playwright().start()
    launch_args = {
      "headless": self._settings.headless,
      "slow_mo": self._settings.slow_mo,
      "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--no-first-run",
        "--no-default-browser-check",
      ],
      "ignore_default_args": ["--enable-automation"],
    }

    self._browser = self._abrir_navegador(launch_args)

    context_options = {
      "user_agent": USER_AGENT_CHROME,
      "viewport": {"width": 1366, "height": 768},
      "locale": "pt-BR",
      "extra_http_headers": {
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
      },
    }
    if self._settings.proxy:
      context_options["proxy"] = self._parse_proxy(self._settings.proxy)

    self._context = self._browser.new_context(**context_options)
    self._context.add_init_script(SCRIPT_STEALTH)
    self._page = self._context.new_page()
    self._page.set_default_timeout(30_000)
    logger.info("Browser Playwright iniciado")
    return self._page

  def _abrir_navegador(self, launch_args: dict) -> Browser:
    # Cliente Windows: Chrome instalado (sem baixar Chromium do Playwright)
    tentativas = [
      ("Google Chrome do sistema", {"channel": "chrome"}),
      ("Microsoft Edge do sistema", {"channel": "msedge"}),
    ]
    if not self._settings.usar_chrome_sistema:
      tentativas.append(("Chromium Playwright", {}))

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
      "Nao foi possivel abrir Google Chrome. "
      "Instale o Chrome e tente novamente. Detalhes: " + " | ".join(erros)
    )

  def stop(self) -> None:
    if self._context:
      self._context.close()
    if self._browser:
      self._browser.close()
    if self._playwright:
      self._playwright.stop()
    logger.info("Browser Playwright encerrado")

  def _parse_proxy(self, proxy_string: str) -> dict:
    partes = proxy_string.split(":")
    if len(partes) == 4:
      return {
        "server": f"http://{partes[0]}:{partes[1]}",
        "username": partes[2],
        "password": partes[3],
      }
    return {"server": f"http://{proxy_string}"}

  def on_dialog(self, handler: Callable) -> None:
    self.page.on("dialog", handler)
