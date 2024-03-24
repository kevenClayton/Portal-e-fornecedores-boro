def Tvalor():
    def urlObs(doc):
        urlDoc = 'https://portal.e-fornecedores.ind.br/Printer.aspx?cmp=SUObsCargaProgramada.ascx&numdoc=00' + doc

        return urlDoc

    htmlObs = driver.get(urlObs('10802952'))

    htmlObs = driver.page_source
    htmlObs = BeautifulSoup(htmlObs, 'lxml')
    htmlObs = htmlObs.pre

    htmlsplit = str(htmlObs).split('<br/>')[0]
    valorCarga = htmlsplit.replace('<pre id="_ctl8_txtObs">Valor da carga:', '')
    valorCarga = valorCarga.replace('R$', '')

    print(valorCarga)

    driver.back()
    return valorCarga