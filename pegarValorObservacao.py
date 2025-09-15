from bs4 import BeautifulSoup
import time

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