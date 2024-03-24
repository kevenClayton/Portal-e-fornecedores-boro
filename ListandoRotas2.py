import pegarValorObservacao
import validarLetraProduto
import enviarEmail
import pandas as pd
import numpy as np
import unidecode
import time
from bs4 import BeautifulSoup
from selenium.webdriver import Keys
from selenium.webdriver.support.select import Select
import logging
import sys
import os
from datetime import datetime

# <== PEGANDO DADOS DO BANDO DE DADOS ==>.
import model.db as db

gravarRotas = db.gravarRotas
gravarRotasRelatorio = db.gravarRotasRelatorio
atualizarSituacaoMotorista = db.atualizarSituacaoMotorista

dados = db.DADOS()
origens = dados['origens']
destinos = dados['select_destinos_motoristas_ativos']
tipoVeiculos = dados['tipo_veiculo']
parametros = dados['parametros']
motoristas = dados['motoristas']
motoristas_destinos = dados['motorista_destino']
motoristas_tipo_veiculo = dados['motoristas_tipo_veiculo']
ehMesmoDestinoCodigo = 0

nome_arquivo = os.path.basename(sys.argv[0])
data_atual = datetime.now().strftime('%d-%m-%Y')
hora_atual = datetime.now().time()

logging.basicConfig(filename='relatario_execucao-info-'+data_atual+'-'+nome_arquivo+'.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logging.info('Clicou em abrir o programa: '+nome_arquivo+' data e hora: ' + str(hora_atual))
# logging.basicConfig(filename='relatario_execucao-debug-'+data_atual+'-'+nome_arquivo+'.log', level=logging.DEBUG,
#                     format='%(asctime)s:%(levelname)s:%(message)s')


def saberUltimaRotaEnviouEmail(codigo):
    global ehMesmoDestinoCodigo
    if codigo == ehMesmoDestinoCodigo:
        return True
    else:
        ehMesmoDestinoCodigo = codigo
        return False

def listarTodasRotas(driver,window):

    window['-OUTPUT-'].update('BUSCANDO TODAS AS ROTAS...')
    #clicar em selecionar empresa
    driver.find_element("id","mnuPrincipal_lstEmpresas").click()

    time.sleep(0.5)

    #seleciona a empresa soluções usiminas que tem o valor 85
    driver.find_element("id", "mnuPrincipal_lstEmpresas").send_keys("85", Keys.ARROW_DOWN)
    time.sleep(0.2)
    select = Select(driver.find_element("id", 'mnuPrincipal_lstEmpresas'))
    select.select_by_value("85")

    time.sleep(0.5)

    #redireciona para a pagina que esta na url
    driver.get('https://portal.e-fornecedores.ind.br/Default.aspx?cmp=SUCargaProgramada.ascx&tipo=vnc&menu=yes')
    time.sleep(0.5)
    #clica no botão pesquisar
    driver.find_element("id", "ctlLoadedControl_btnPesquisa").click()

#pausa
time.sleep(0.3)

def ValidarSelect(driver,IdSelect,destino):
    existe = False

    options = driver.find_element("id", IdSelect).text
    logging.info(options)
    logging.info('Lista origensExistentes no portal')
    options = options.split('\n')
    # Configuração básica do logger


    # Registra uma mensagem de informação




    for option in options:
        if destino == option.strip():
            existe = True
            logging.info('origem existe')
            logging.info(option)
            break

    if existe == True:

        return True
    else:
        False

#->ORIGEM->SÒ SANTA LUZIA E BETIM
def selecionarOrigemDestino(driver,window,interface):

    #seleciona a origem.
    for origem in origens:
        # caso o cliente clique em finalizar, ele para o loop
        if interface == False:
            break

        #PEGANDO O VALUE DA ORIGEM QUE FICA NA POSIÇÃO 1
        origem = origem[1]

        #SETANDO O ID DO SELECT DE ORIGEM
        IdSelectOrigem = 'ctlLoadedControl_ddlOrigem'

        #VALIDANDO SE EXISTEM OS VALUE DA ORIGEM DENTRO DO SELECT
        ExisteOrigem = ValidarSelect(driver, IdSelectOrigem, origem)

        if ExisteOrigem == True:
            #CASO EXISTA OS VALUES DENTRO ELE SELECIONA O VALOR
            select = Select(driver.find_element("id", 'ctlLoadedControl_ddlOrigem'))
            select.select_by_value(origem)
            logging.info('Clicou na origem')
            logging.info(origem)

            verificarSeExisteDestinoEFiltrar(driver, window, origem)

        else:
            status = ('Origem não encontrada no filtro, ORIGEM: ' + origem )
            print(status)
            window['-OUTPUT-'].update(status)

def verificarSeExisteDestinoEFiltrar(driver,window, origem):
    arrayDestinos = np.array(destinos)
    existe = False
    select ='ctlLoadedControl_ddlCluster'

    # logging.info('Todas rotas presentes:')
    # logging.info(tabelafull)

    options = driver.find_element("id", select).text
    logging.info('Todos destinos no filtro no portal:')
    logging.info(options)
    options = options.split('\n')




    for destino in options:
        if destino.strip() in arrayDestinos:
            status = ('Verificando cluster existente em nossa base de dados: ' + destino)
            print(status)
            window['-OUTPUT-'].update(status)
            select = Select(driver.find_element('id', select))
            select.select_by_value(destino.strip())
            filtrar(driver)
            verificarCadaResultadoRota(driver, window, origem, destino)
            existe = True
            logging.info('Existe o destino')
            logging.info(destino)
            return existe
        else:
            status = ('Cluster não existente em nossa base de dados: ' + destino)
            print(status)
            window['-OUTPUT-'].update(status)


def filtrar(driver):
    # execulta o filtro.
    print("Clicando em filtrar rota")
    driver.find_element("id", "ctlLoadedControl_btnFiltrar").click()

def verificarCadaResultadoRota(driver,window, origem, destino):
    htmlprod = driver.page_source
    htmlprod = BeautifulSoup(htmlprod, 'lxml')
    htmlprod = htmlprod.find('table', id='ctlLoadedControl_dgRight')
    linhas = htmlprod.findChildren('tr')
    tabelacompleta = pd.read_html(str(htmlprod), skiprows=1)[0]
    tabelafull = tabelacompleta.to_dict('split')['data']



    for rota in tabelafull:
        numeroDocumento = rota[0]
        data = rota[3]
        compartilhado = rota[4]
        prioridade = rota[5]
        tpTransporte = rota[7]
        pesoTotal = rota[8]
        unidadePeso = rota[9]
        plantaOrigem = rota[10]
        cluster = rota[11]
        estado = rota[12]
        obervacoes = validarLetraProduto.pegarObservacoesRota(driver, numeroDocumento)
        valorCarga =  pegarValorObservacao.tratarValorNoCampoObservacao(driver, numeroDocumento).strip().split(',')[0]
        temLetraB = validarLetraProduto.verificarTemLetraB(driver, numeroDocumento)
        clientesComMesmoDestino = validarLetraProduto.verificarMultiplosDestinos(driver, numeroDocumento)
        maisDeUmDestino = clientesComMesmoDestino[2]
        todosDestinos = clientesComMesmoDestino[1]
        maiorQueUmDestinos = False
        clientesComMesmoDestino[0] = True

        if (maisDeUmDestino > 1):
            maiorQueUmDestinos = True

        for tipoVeiculo in tipoVeiculos:

            # PEGA O DESTINO QUE FICA NA POSIÇÃO 1
            tipoVeiculo = tipoVeiculo[1]
            print('TIPO: ', tipoVeiculo)

            window['-OUTPUT-'].update('VALIDANDO RESULTADOS...')

            # VALIDA SE O VALUE EXISTE NO SELECT CLUSTER
            if tipoVeiculo.lower() == tpTransporte.lower():
                tipoTransporteSelecionado = tpTransporte
                valorParametroCarreta = round(parametros[0][3], 2)
                valorParametroTruck = round(parametros[0][1], 2)
                valorCargaFormatado = float(valorCarga.replace(".", ""))
                if tpTransporte.lower().__contains__('carreta') and  valorCargaFormatado <= valorParametroCarreta or tpTransporte.lower().__contains__('truck') and valorCargaFormatado <= valorParametroTruck:
                    window['-OUTPUT-'].update('Parametro preço e tipo ok: '+ tpTransporte + valorCarga)
                    print('Parametro preço e tipo ok: ', tpTransporte)
                    idBotaoVincular = pegandoIdBotaoVincular(linhas, numeroDocumento)


                    if clientesComMesmoDestino[0] == True:
                        driver.find_element("id", idBotaoVincular).click()
                        logging.info('Clicou no botao vincular veiculo na listagem:')
                        logging.info(rota)
                        vincularMotoristaNaRota(tipoTransporteSelecionado, cluster, temLetraB, numeroDocumento,driver,data,valorCarga, tpTransporte,plantaOrigem,obervacoes, pesoTotal,todosDestinos,maiorQueUmDestinos,prioridade,  window)
                    else:
                        retornoMesmoDestinoEmail = saberUltimaRotaEnviouEmail(numeroDocumento)
                        if retornoMesmoDestinoEmail == True:
                            print('Rota encontrada com destino diferente, porém já enviou o e-mail 1x')
                        else:
                            # enviarEmail.enviarEmailRotaComDestinoDiferente(numeroDocumento)
                            gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte,pesoTotal, obervacoes, prioridade, todosDestinos, maiorQueUmDestinos,"Rota com destino diferente")
                            status = 'Rota encontrada com destino diferente, dados: origem: ' + plantaOrigem + ' cluster: ' + clientesComMesmoDestino[1] + 'estado:' + estado + ' valor carga: ' + valorCarga + ' tptransporte:' + tpTransporte + ' peso: ' + str(pesoTotal) + ' doc:' + str(numeroDocumento) + ''
                            status = unidecode.unidecode(status)
                            print(status)
                            window['-OUTPUT-'].update(status)
                            enviarEmail.enviarEmailGenerico("Rota destinos diferentes", status)


                    time.sleep(0.2)
                    driver.back()
                # Valor maiior
                else:
                    gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte, pesoTotal,obervacoes, prioridade, todosDestinos, maiorQueUmDestinos, "Valor maior que o configurado")
            # não atende tipo veiculo
            else:
                gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte, pesoTotal, obervacoes, prioridade, todosDestinos, maiorQueUmDestinos, "Não possui tipo veículo")







def vincularMotoristaNaRota(transporteSelecionado, destino, temLetraB, numeroDocumento,driver,data,valorCarga, tpTransporte,origem,obervacoes, pesoTotal,todosDestinos,maiorQueUmDestinos,prioridade, window):

    global dados
    global origens
    global destinos
    global tipoVeiculos
    global parametros
    global motoristas
    global motoristas_destinos
    global motoristas_tipo_veiculo
    global ehMesmoDestinoCodigo

    logging.info('@vincularMotoristaNaRota')
    logging.info(destino)

    dados = db.DADOS(cliente)
    motoristas = dados['motoristas']
    motoristas_destinos = dados['motorista_destino']

    logging.info('@motoristas')
    logging.info(motoristas)

    for motorista in motoristas:
        print(motorista)
        idNoBanco = motorista[0]
        placa = motorista[1]
        cpf = motorista[2]

        nome = motorista[3]
        aceitaBobina = motorista[8]
        situacao = motorista[9]

        if temLetraB == True and aceitaBobina != 1:
            print("motorista não aceita bobina", nome)
            continue
        elif situacao == 1:
            print("situacao motorista ok!")
            arrayMotoristaDestinos = np.array(motoristas_destinos)
            if destino in arrayMotoristaDestinos:
                destinoMotoristaEncontrado = np.where(arrayMotoristaDestinos == destino)[0]
                # indexMotoristaEncontrado = np.where(arrayMotoristaDestinos == idNoBanco)[0]
                #
                # indexMotoristaEncontrado = np.where(destinoMotoristaEncontrado == indexMotoristaEncontrado)
                #
                #
                # if(len(indexMotoristaEncontrado[0]) > 0 ):
                #     destinoMotoristaEncontrado = arrayMotoristaDestinos[indexMotoristaEncontrado]
                #
                for motoristaIndex in destinoMotoristaEncontrado:
                    if int(arrayMotoristaDestinos[motoristaIndex][0]) == idNoBanco:
                        motoristaCerto = True
                        destinoCerto = arrayMotoristaDestinos[motoristaIndex][1].lower()
                        break
                    else:
                        motoristaCerto = False
                        destinoCerto = False

                if motoristaCerto == True and destino.lower() == destinoCerto:
                    #Motorista aceita a rota
                    print('Motorista ' + nome + ' é compatível com o destino, verificar agora o tipo de veículo...')

                    for motorista_tipo_veiculo in motoristas_tipo_veiculo:
                        if idNoBanco == motorista_tipo_veiculo[0] and transporteSelecionado.lower() == motorista_tipo_veiculo[1].lower():
                            status = 'Destino, origem e tipo de veículo compatível como motorista, pode vincular', 'nome: ',  nome, 'placa: ', placa, 'CPF: ', cpf
                            print(status)
                            window['-OUTPUT-'].update(status)
                            #=========AGORA PREENCHER OS DADOS E VINCULAR==========
                            #PREENCHE A PLACA DO VEICULO
                            driver.find_element("id", "ctlLoadedControl_txtPlaca1").clear()
                            driver.find_element("id", "ctlLoadedControl_txtPlaca1").send_keys(placa)
                            driver.find_element("id", "ctlLoadedControl_btnBuscarVeiculo").click()
                            time.sleep(0.5)
                            try:
                                alert = driver.switch_to.alert  # This .alert will work For Python
                                print('Alerta texto: ' + alert.text)
                                alert.accept()
                                continue
                            except:
                                print('Não tem alerta placa, continuando...')


                            #CLICA EM BUSCAR DADOS VEICULO
                            # PREENCHE O CPF DO MOTORISTA
                            driver.find_element("id", "ctlLoadedControl_txtCPF").clear()
                            driver.find_element("id", "ctlLoadedControl_txtCPF").send_keys(cpf)
                            driver.find_element("id", "ctlLoadedControl_btnBuscarMotorista").click()
                            time.sleep(0.5)
                            try:
                                alert = driver.switch_to.alert  # This .alert will work For Python
                                print('Alerta texto: ' + alert.text)
                                alert.accept()
                                continue
                            except:
                                print('Não tem alerta motorista, continuando...')

                            #CLICA EM BUSCAR DADOS DO MOTORISTA

                            dadosDBParaVincular = db.dadosDBParaVincular(idNoBanco, destino)

                            validandoSeMotoristaAtendeDestino = len(dadosDBParaVincular['motorista_destino'])
                            if(validandoSeMotoristaAtendeDestino == 0):
                                logging.info('Motorista não passou na validação final de destino:')
                                logging.info(motorista)
                                logging.info(numeroDocumento)
                                logging.info(destino)
                                status = 'Nao validou o motorista com o destino, era pra vincular, mas no final, ao conferir o motorista, ele nao atende o destino. doc: ' + str(numeroDocumento) + ' motorista: ' + nome + ' cpf motorista:' + cpf + ' placa: ' + placa + ' tptransporte:' + tpTransporte + ' cluster: ' + destino + ' valor:' + valorCarga + ''
                                status = unidecode.unidecode(status)
                                print(status)
                                enviarEmail.enviarEmailGenerico("Motorista nao passou na validacao final de destino", status)
                                gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte, pesoTotal, obervacoes, prioridade, todosDestinos, maiorQueUmDestinos, "Não encontrou motorista")
                                continue

                            if parametros[0][4] == 0: #Se é modo teste ou não
                                #===================BOTÃO VINCULAR====================
                                driver.find_element("id", "ctlLoadedControl_btnSalvar").click()
                                textoAoClicarVincular = driver.find_element("id", "ctlLoadedControl_lblMessage").text
                                textoObservacao = driver.find_element("id", "ctlLoadedControl_txtObs").text

                                logging.info('Clicou em vincular')
                                logging.info(motorista)

                                if("CHAPA EXCEDENTE" in textoObservacao):
                                    status = 'Não vinculou, pois contém texto chapa excedente na observação: doc: ' + str(numeroDocumento) + ' motorista: ' + nome + ' cpf motorista:' + cpf + ' placa: ' + placa + ' tptransporte:' + tpTransporte + ' cluster: ' + destino + ' valor:' + valorCarga + ''

                                    logging.info(status)
                                    logging.info(motorista)
                                    logging.info(numeroDocumento)
                                    logging.info(destino)

                                    status = unidecode.unidecode(status)
                                    print(status)
                                    enviarEmail.enviarEmailGenerico("Chapa excedente", status)
                                    gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga,
                                                         tpTransporte, pesoTotal, obervacoes, prioridade, todosDestinos,
                                                         maiorQueUmDestinos, "Chapa excedente ao vincular")
                                    continue

                                if "sucesso" in textoAoClicarVincular:

                                    logging.info('Sucesso ao clicar em vincular rota ao motorista')
                                    logging.info(motorista)
                                    logging.info(numeroDocumento)
                                    logging.info(destino)

                                    enviarEmail.enviarEmailRotaVinculada(motorista, numeroDocumento)
                                    gravarRotas(origem, destino, numeroDocumento, data, valorCarga, nome, tpTransporte,situacao)
                                    atualizarSituacaoMotorista(idNoBanco)

                                    dados = db.DADOS()
                                    origens = dados['origens']
                                    destinos = dados['select_destinos_motoristas_ativos']
                                    tipoVeiculos = dados['tipo_veiculo']
                                    parametros = dados['parametros']
                                    motoristas = dados['motoristas']
                                    motoristas_destinos = dados['motorista_destino']
                                    motoristas_tipo_veiculo = dados['motoristas_tipo_veiculo']

                                    #driver.back()
                                    listarTodasRotas(driver, window)
                                    selecionarOrigemDestino(driver, window, True)
                                    break
                                else:
                                    driver.back()

                                    status = 'Erro quando clicado ao vincular: ' + textoAoClicarVincular + ' doc: ' +str(numeroDocumento)+' motorista: '+nome+' cpf motorista:'+cpf+' placa: '+placa+' tptransporte:'+tpTransporte+' cluster: '+destino+' valor:'+valorCarga+''
                                    logging.info(status)
                                    logging.info(motorista)
                                    logging.info(numeroDocumento)
                                    logging.info(destino)

                                    status = unidecode.unidecode(status)

                                    print(status)
                                    window['-OUTPUT-'].update(status)
                                    enviarEmail.enviarEmailGenerico("Erro ao tentar vincular", status)
                                    gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga,
                                                         tpTransporte, pesoTotal, obervacoes, prioridade, todosDestinos,
                                                         maiorQueUmDestinos, textoAoClicarVincular)
                                    continue

                            else:
                                driver.back()


                                status = 'Nao vinculou, pois esta no modo teste, doc: '+str(numeroDocumento)+''
                                logging.info(status)
                                logging.info(motorista)
                                logging.info(numeroDocumento)
                                logging.info(destino)
                                enviarEmail.enviarEmailGenerico("Modo teste habilitado", status)
                                print(status)

                                window['-OUTPUT-'].update('Era pra vincular, mas está no modo teste. NÃO VINCULADO!'+status)
                                continue
            #não tem motorista pra rota
            else:
                gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte, pesoTotal,obervacoes, prioridade, todosDestinos, maiorQueUmDestinos,"Não tem motorista pra rota ao vincular")
        else:
            print("motorista desativado:", nome)
            #continue

        print(motorista)
    else:
        gravarRotasRelatorio(origem, destino, numeroDocumento, data, valorCarga, tpTransporte, pesoTotal, obervacoes,prioridade, todosDestinos, maiorQueUmDestinos, "Motorista tem motorista para o destino")
        listarTodasRotas(driver, window)
        selecionarOrigemDestino(driver, window, True)
def pegandoIdBotaoVincular(linhas, numeroDocumento):
    idBotao = ''
    quantLinhas = len(linhas)
    #APARENTEMENTE ESTA PULANDO O PRIMEIRO ITEM DA TABELA
    for i in range(quantLinhas):

        if i != 0:
            numeroDocumentoLinha = linhas[i].findChildren('td')[0].text.strip()
            idBotaoLinha = linhas[i].findChildren('td')[2].findChildren('input')[0].get('id')
            if str(numeroDocumento) == numeroDocumentoLinha:
                idBotao = idBotaoLinha
                return idBotao
                break

    return idBotao

