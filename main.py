import time
import threading
import fazendoLogin
import ListandoRotas2
import PySimpleGUI as sg
from selenium import webdriver
from datetime import datetime
import unidecode
import enviarEmail
import model.db as db
import requests
from config import fundo
from selenium.webdriver.chrome.service import Service


dados = db.DADOS()
login = dados['login']
#======ARQUIVOS=========


# Define the window's contents
layout = [[sg.Text("Buscar e aceitar rotas no e-Fornecedor")],
# [sg.Input(key='-INPUT-')],
[sg.Text(size=(40,2), key='-OUTPUT-')],

[sg.Button('Buscar e aceitar rotas'), sg.Button('Parar e sair do programa')]]

# Create the window
window = sg.Window('Buscar e aceitar rotas no e-Fornecedor', layout, background_color= fundo)

# Display and interact with the Window using an Event Loop
global interface
interface = False

global valid
global ambienteDesenvolvimento
valid = 0
ambienteDesenvolvimento = False

def teste():
    global valid
    global interface

    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Parar e sair do programa':
            valid = 1
            interface = False
            now = datetime.now()
            current_time = now.strftime("%d-%m-%Y, %H:%M:%S")
            print("Hora clicou em fechar =", current_time)


            time.sleep(3)
            break
        elif event == 'Buscar e aceitar rotas':
            valid = 0
            interface = True
            if ambienteDesenvolvimento == False:
                now = datetime.now()
                current_time = now.strftime("%d-%m-%Y, %H:%M:%S")
                print("Hora clicou em buscar = ", current_time)
                current_time = unidecode.unidecode(current_time)
                enviarEmail.enviarEmailGenerico('Foi clicado em buscar rota','Horario que clicou em buscar rotas pelo programa: ' + current_time)




threading.Thread(target=teste).start()
option = webdriver.ChromeOptions()
option.headless = False
service = Service()


#servico = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=option)


while True:
        try:
            # Valida se usuario clicou em iniciar(TRUE0) ou para (FALSE)
            # se for positivo, roda o programa, se for negativo fecha o programa por inteiro
            if interface == True:
                valid = 1

                #Iniciando WebDriver


                #Veirificando se esta logado.
                logado = fazendoLogin.verificandoSeTaLogado(driver)

                #Valida se o robo esta logado ou não.
                if(logado == True):

                    #valida se o usuario clicou em para o programa antes de execultar a função.
                    #se Tiver parado, pula a execulção da função e para o programa.
                    if interface == True:

                        ListandoRotas2.listarTodasRotas(driver,window)
                    else:
                        break
                    if interface == True:
                        ListandoRotas2.selecionarOrigemDestino(driver,window,interface)
                    else:
                        break
                else:

                    # valida se o usuario clicou em para o programa antes de execultar a função.
                    # se Tiver parado, pula a execulção da função e para o programa.
                    if interface == True:
                        window['-OUTPUT-'].update('Fazendo login...')
                        fazendoLogin.fazendoLogin(driver, login)
                    else:
                        break
                    if interface == True:
                        ListandoRotas2.listarTodasRotas(driver,window)
                    else:
                        break

                    if interface == True:
                        ListandoRotas2.selecionarOrigemDestino(driver,window,interface)
                    else:
                        break
            else:
                window['-OUTPUT-'].update('SELECIONE PARA INICIAR.')
                time.sleep(1)

                if valid == 1:
                    break
        except Exception as e:
            print('Deu erro aplicação, mas está continuando')
            print('ERRO: ' + str(e))
            pass



# Output a message to the window

# Finish up by removing from the screen
window.close()

#print(validarProduto())


#driver.back()


#driver.back()

#POSSIVEL SOLUÇÂO.
#DESENHAR A TELA ANTES DO IF CASO A SELEÇÃO SEJA EXECULTAR ROTINA, O PROGRAMA VAI DESENHAR UMA NOVA JANELA COM O BOTÃO APENA DE BLOQUIO.


#====================================JAVASCRIPT===========================================
#cod = (scripts.scripts())
#print(cod)
#para xecultar o script só é preciso Usar esse comando e colocar dentro das aspas o valor.
#driver.execute_script("console.log('teste de script')")
#driver.execute_script("alert('script_execute')")
#execultando script que esta em arquivo separado, para não misturar python com Js
#driver.execute_script(cod)
#====================================END-JAVASCRIPT===========================================

#time.sleep(10)

#pega o html da tabela
# element = driver.find_element('id' , 'ctlLoadedControl_dgRight')
#
# html_content = element.get_attribute('outerHTML')

#trata o html

# soup = BeautifulSoup(html_content, 'lxml')
# print(soup.a)

#nomeia a tabela
# table = soup.find(name='table')
#converte em string
# tableS = str(table)

#trata o html e transforme em uma tabela.
# df_full = pd.read_html(tableS)[0]

#print(df_full)

#formato em que o dicionario ficara.
# dados_full = df_full.to_dict('list')

# o numero de resultados da tabela diminuido pelo indice ta tabela, que é onde fica as informações.
#resultados = len(dados_full - 1)
#print(len(dados_full))

#print(dados_full)

# time.sleep(1)

# driver.quit()
