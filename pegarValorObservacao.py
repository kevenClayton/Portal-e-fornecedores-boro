import time
import lxml
import re
import requests
import html5lib
import pegarValorObservacao
import validarLetraProduto
import fazendoLogin
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

def tratarValorNoCampoObservacao(driver, numeroDocumento):
    def urlObs(numeroDoc):
        urlDoc = 'https://portal.e-fornecedores.ind.br/Printer.aspx?cmp=SUObsCargaProgramada.ascx&numdoc=00' + numeroDoc

        return urlDoc

    htmlObs = driver.get(urlObs(str(numeroDocumento)))

    htmlObs = driver.page_source
    htmlObs = BeautifulSoup(htmlObs, 'lxml')
    htmlObs = htmlObs.pre

    htmlsplit = str(htmlObs).split('<br/>')[0]
    valorCarga = htmlsplit.replace('<pre id="_ctl8_txtObs">Valor da carga:', '')
    valorCarga = valorCarga.replace('R$', '')


    driver.back()
    return valorCarga