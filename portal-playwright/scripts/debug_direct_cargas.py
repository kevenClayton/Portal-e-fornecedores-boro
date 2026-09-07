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

  print("AFTER_LOGIN", page.url, "linkPT", page.locator("#ctlLoadedControl_linkPT").count())
  page.goto(settings.url_cargas, wait_until="domcontentloaded")
  login.aceitar_cookies()
  print("AFTER_CARGAS", page.url)
  print("login_fields", page.locator(LoginPage.SELECTOR_USUARIO).count())
  print("empresas", page.locator("#mnuPrincipal_lstEmpresas").count())
  print("pesquisa", page.locator("#ctlLoadedControl_btnPesquisa").count())
  print("linkPT", page.locator("#ctlLoadedControl_linkPT").count())
  page.screenshot(path="/tmp/debug-out/direct-cargas.png", full_page=True)
  open("/tmp/debug-out/direct-cargas.html", "w").write(page.content())
  print("body", re.sub(r"\s+", " ", page.inner_text("body"))[:700])
  browser.stop()


if __name__ == "__main__":
  main()
