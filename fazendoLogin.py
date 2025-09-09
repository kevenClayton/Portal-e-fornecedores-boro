import time
from urllib.parse import urlparse
import ListandoRotas2
from selenium.webdriver.chrome.options import Options


def fazendoLogin(driver,login):
    url = 'https://portal.e-fornecedores.ind.br/'

    #
    option = Options()
    option.headless = True
    # webdriver

    usuario = login[0][1]
    senha = login[0][2]

    #driver = webdriver.Chrome('./chromedriver')
    # abre o navegador na pagina selecionada.
    driver.get(url)
    #execulta um click no input e depois preenche com o usuario
    driver.find_element("id", "ctlLoadedControl_txtLogin").click()
    driver.find_element("id", "ctlLoadedControl_txtLogin").send_keys(usuario)

    # execulta um click no input e depois preenche com a senha.
    driver.find_element("id", "ctlLoadedControl_txtSenha").click()
    driver.find_element("id", "ctlLoadedControl_txtSenha").send_keys(senha)
    #clica em logar
    driver.find_element("id","ctlLoadedControl_btnOK").click()

def verificandoSeTaLogado(driver):    
    time.sleep(1)
    driver.refresh()
    logado = False

    urlAtual = driver.current_url

    if(urlAtual == "data:,"):
        return logado

    if(verificarViolacao(driver)):
        return verificarViolacao(driver)

    parsed_url = urlparse(urlAtual)
    parametros = parsed_url.query
    print(logado)

    if parametros =='cmp=Error.ascx':
        driver.get('https://portal.e-fornecedores.ind.br/')

    if parametros == 'cmp=login.ascx':
        logado = False

    if(parametros != ""):
        logado = True

    return logado

def verifcaPaginaAcessoSimultaneo(driver):
    time.sleep(2)
    driver.refresh()
    logado = False

    urlAtual = driver.current_url

    if(urlAtual == "data:,"):
        return logado

    parsed_url = urlparse(urlAtual)
    parametros = parsed_url.query
    print(logado)

    if parametros =='cmp=Error.ascx':
        driver.get('https://portal.e-fornecedores.ind.br/')

    if(parametros != ""):
        logado = True

    return logado

def verificarViolacao(driver):
    if(driver.page_source.__contains__('Violacao')):
        time.sleep(10)
        driver.refresh()
        return True
    else:
        return False


