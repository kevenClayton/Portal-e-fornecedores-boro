from selenium.webdriver.chrome.options import Options
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

def verificarTemLetraB(driver, numeroDocumento):
    def urlprodduto(doc):
        urlproduto = 'https://portal.e-fornecedores.ind.br/Printer.aspx?cmp=SUItemCargaProgramada.ascx&numdoc=00'+doc

        return urlproduto


    htmlprod = driver.get(urlprodduto(str(numeroDocumento)))

    htmlprod = driver.page_source
    htmlprod = BeautifulSoup(htmlprod, 'lxml')
    htmlprod = htmlprod.find('table', class_='titulo')
    tabelacompleta = pd.read_html(str(htmlprod), skiprows=1)[0]
    tabelafull = tabelacompleta.to_dict('list')[1]
    contemLetraB = False

    for produto in tabelafull:
        #print(produto.split()[0][0])
        if produto.split()[0][0] == 'B':
            contemLetraB = True


    driver.back()
    return contemLetraB

def verificarMultiplosDestinos(driver, numeroDocumento):
    def urlClientes(doc):
        urlCliente = 'https://portal.e-fornecedores.ind.br/Printer.aspx?cmp=SURemessaCargaProgramada.ascx&numdoc=00'+doc

        return urlCliente

    htmlClientes = driver.get(urlClientes(str(numeroDocumento)))

    htmlClientes = driver.page_source
    htmlClientes = BeautifulSoup(htmlClientes, 'lxml')
    htmlClientes = htmlClientes.find('table', class_='titulo')

    tabelacompleta = pd.read_html(str(htmlClientes), skiprows=1)[0]
    tabelafull = tabelacompleta.to_dict('list')[4]
    ehMesmoDestino = True
    contador = 0
    municipios = ""
    for nomeDestino in tabelafull:
        nomeDestino = str(nomeDestino)
        municipios += str(contador)+'- ' +nomeDestino+', '
        if contador == 0:
            nomeAtual = nomeDestino

        if nomeDestino.lower() != nomeAtual.lower():
            ehMesmoDestino = False

        contador += 1
        nomeAtual = nomeDestino

    driver.back()
    cidadeEMesmoDestino = [
        (ehMesmoDestino),
        (municipios),
        (contador)

    ]
    return cidadeEMesmoDestino

def pegarObservacoesRota(driver, numeroDocumento):
    def urlClientes(doc):
        urlCliente = 'https://portal.e-fornecedores.ind.br/Printer.aspx?cmp=SUObsCargaProgramada.ascx&numdoc=00' + doc

        return urlCliente

    htmlClientes = driver.get(urlClientes(str(numeroDocumento)))

    htmlClientes = driver.page_source
    htmlClientes = BeautifulSoup(htmlClientes, 'lxml')
    htmlClientes = htmlClientes.find('pre')

    if htmlClientes:
        for br in htmlClientes.find_all('br'):
            br.replace_with(' | ')
        observacao = htmlClientes.get_text()
        print(observacao)
    else:
        print('pre tag não encontrada')


    driver.back()

    return observacao