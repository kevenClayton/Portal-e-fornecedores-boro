#!/usr/bin/env python3
import re

from portal_fornecedores.browser.manager import BrowserManager
from portal_fornecedores.browser.pages.login_page import LoginPage
from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.connection import DatabaseConnection
from portal_fornecedores.database.repositories.dados_repository import DadosRepository


def main() -> None:
  settings = get_settings()
  usuario, senha = DadosRepository(DatabaseConnection()).obter_login()
  browser = BrowserManager(settings)
  page = browser.start()
  login = LoginPage(page, settings)

  login.navegar()
  page.wait_for_selector(LoginPage.SELECTOR_USUARIO, timeout=30_000)
  login.aceitar_cookies()
  page.locator(LoginPage.SELECTOR_USUARIO).fill(usuario)
  page.locator(LoginPage.SELECTOR_SENHA).fill(senha)
  with page.expect_navigation(wait_until="domcontentloaded", timeout=45_000):
    page.locator(LoginPage.SELECTOR_BOTAO).click()

  print("AFTER_LOGIN", page.url)
  print("linkPT", page.locator("#ctlLoadedControl_linkPT").count())
  print("has_doPostBack", page.evaluate("() => typeof __doPostBack"))
  page.screenshot(path="/tmp/debug-out/before-bypass.png", full_page=True)

  try:
    with page.expect_navigation(wait_until="domcontentloaded", timeout=25_000):
      page.evaluate("() => __doPostBack('ctlLoadedControl$linkPT','')")
    print("nav_ok")
  except Exception as erro:
    print("nav_err", type(erro).__name__, erro)
    page.evaluate("() => __doPostBack('ctlLoadedControl$linkPT','')")
    page.wait_for_timeout(3_000)

  print("AFTER_BYPASS", page.url)
  print("linkPT", page.locator("#ctlLoadedControl_linkPT").count())
  print("empresas", page.locator("#mnuPrincipal_lstEmpresas").count())
  page.screenshot(path="/tmp/debug-out/after-bypass.png", full_page=True)
  open("/tmp/debug-out/after-bypass.html", "w").write(page.content())
  print("body", re.sub(r"\s+", " ", page.inner_text("body"))[:600])
  browser.stop()


if __name__ == "__main__":
  main()
