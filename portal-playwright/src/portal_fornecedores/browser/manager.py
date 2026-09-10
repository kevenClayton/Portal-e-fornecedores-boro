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

    chrome_args = [
      "--disable-blink-features=AutomationControlled",
      "--disable-infobars",
      "--no-first-run",
      "--no-default-browser-check",
    ]
    # Flags necessárias dentro de Docker
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
    # Em Docker preferimos Chrome real: o portal cai em browserinfo.ascx com Chromium Playwright
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
    if len(partes) == 2:
      return {"server": f"http://{partes[0]}:{partes[1]}"}
    return {"server": f"http://{proxy_string}"}

  def on_dialog(self, handler: Callable) -> None:
    self.page.on("dialog", handler)
