import logging
from typing import Tuple

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

BASE_PRINTER = "https://portal.e-fornecedores.ind.br/Printer.aspx"


class DetalhesCargaPage:
  def __init__(self, page: Page):
    self._page = page

  def atualizar_page(self, page: Page) -> None:
    self._page = page

  def _url_detalhe(self, componente: str, numero_documento: str) -> str:
    return f"{BASE_PRINTER}?cmp={componente}&numdoc=00{numero_documento}"

  def obter_valor_carga(self, numero_documento: str) -> str:
    self._page.goto(
      self._url_detalhe("SUObsCargaProgramada.ascx", numero_documento),
      wait_until="domcontentloaded",
    )
    soup = BeautifulSoup(self._page.content(), "lxml")
    pre_tag = soup.find("pre")
    if not pre_tag:
      self._page.go_back(wait_until="domcontentloaded")
      return ""

    primeira_linha = str(pre_tag).split("<br/>")[0]
    valor = primeira_linha.replace('<pre id="_ctl8_txtObs">Valor da carga:', "")
    valor = valor.replace("R$", "").strip()
    self._page.go_back(wait_until="domcontentloaded")
    return valor.split(",")[0] if valor else ""

  def verificar_tem_bobina(self, numero_documento: str) -> bool:
    self._page.goto(
      self._url_detalhe("SUItemCargaProgramada.ascx", numero_documento),
      wait_until="domcontentloaded",
    )
    soup = BeautifulSoup(self._page.content(), "lxml")
    tabela = soup.find("table", class_="titulo")
    tem_bobina = False

    if tabela:
      try:
        dataframe = pd.read_html(str(tabela), skiprows=1)[0]
        produtos = dataframe.to_dict("list").get(1, [])
        for produto in produtos:
          texto = str(produto).strip()
          if texto and texto.split()[0][0].upper() == "B":
            tem_bobina = True
            break
      except Exception as erro:
        logger.warning("Erro ao verificar bobina doc %s: %s", numero_documento, erro)

    self._page.go_back(wait_until="domcontentloaded")
    return tem_bobina

  def verificar_multiplos_destinos(self, numero_documento: str) -> Tuple[bool, str, int]:
    self._page.goto(
      self._url_detalhe("SURemessaCargaProgramada.ascx", numero_documento),
      wait_until="domcontentloaded",
    )
    soup = BeautifulSoup(self._page.content(), "lxml")
    tabela = soup.find("table", class_="titulo")
    mesmo_destino = True
    municipios = ""
    contador = 0
    nome_anterior = ""

    if tabela:
      try:
        dataframe = pd.read_html(str(tabela), skiprows=1)[0]
        destinos = dataframe.to_dict("list").get(4, [])
        for nome_destino in destinos:
          nome_destino = str(nome_destino).strip()
          municipios += f"{contador}- {nome_destino}, "
          if contador > 0 and nome_destino.lower() != nome_anterior.lower():
            mesmo_destino = False
          nome_anterior = nome_destino
          contador += 1
      except Exception as erro:
        logger.warning("Erro ao verificar destinos doc %s: %s", numero_documento, erro)

    self._page.go_back(wait_until="domcontentloaded")
    return mesmo_destino, municipios, contador

  def obter_observacoes(self, numero_documento: str) -> str:
    self._page.goto(
      self._url_detalhe("SUObsCargaProgramada.ascx", numero_documento),
      wait_until="domcontentloaded",
    )
    soup = BeautifulSoup(self._page.content(), "lxml")
    pre_tag = soup.find("pre")
    observacao = ""
    if pre_tag:
      for br in pre_tag.find_all("br"):
        br.replace_with(" | ")
      observacao = pre_tag.get_text()
    self._page.go_back(wait_until="domcontentloaded")
    return observacao
