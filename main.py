import time
import threading
import fazendoLogin
import ListandoRotas2
import FreeSimpleGUI as sg
from selenium import webdriver
from datetime import datetime
import unidecode
import enviarEmail
import model.db as db
import requests
from config import fundo
from selenium.webdriver.chrome.service import Service
import random

from fazendoLogin import verificandoSeTaLogado
from proxy_auth_handler import auto_handle_proxy_auth
from proxy_extension import setup_proxy_with_extension, cleanup_proxy_extension


dados = db.DADOS()
login = dados['login']
#======ARQUIVOS=========


# Define the window's contents
layout = [[sg.Text("Buscar e aceitar rotas no e-Fornecedor")],
[sg.Text("Tempo de espera (segundos):"), sg.Input('30', key='-TEMPO_ESPERA-', size=(10,1))],
[sg.Text(size=(40,2), key='-OUTPUT-')],

[sg.Button('Buscar e aceitar rotas'), sg.Button('Parar e sair do programa')]]

# Create the window
window = sg.Window('Buscar e aceitar rotas no e-Fornecedor', layout, background_color= fundo)

# Display and interact with the Window using an Event Loop
global interface
interface = False

global valid
global ambienteDesenvolvimento
global tempo_espera
valid = 0
ambienteDesenvolvimento = False
tempo_espera = 30

def teste():
    global valid
    global interface
    global tempo_espera
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Parar e sair do programa':
            valid = 1
            interface = False
            now = datetime.now()
            current_time = now.strftime("%d-%m-%Y, %H:%M:%S")
            print("Hora clicou em fechar =", current_time)


            # time.sleep(3)
            break
        elif event == 'Buscar e aceitar rotas':
            valid = 0
            interface = True
            # Capturar o tempo de espera configurado pelo usuário
            try:
                tempo_espera = int(values['-TEMPO_ESPERA-'])
                if tempo_espera < 1:
                    tempo_espera = 30
                    window['-TEMPO_ESPERA-'].update('30')
                print(f"Tempo de espera configurado: {tempo_espera} segundos")
            except ValueError:
                tempo_espera = 30
                window['-TEMPO_ESPERA-'].update('30')
                print("Valor inválido para tempo de espera, usando padrão: 30 segundos")
            
            if ambienteDesenvolvimento == False:
                now = datetime.now()
                current_time = now.strftime("%d-%m-%Y, %H:%M:%S")
                print("Hora clicou em buscar = ", current_time)
                current_time = unidecode.unidecode(current_time)
                enviarEmail.enviarEmailGenerico('Foi clicado em buscar rota','Horario que clicou em buscar rotas pelo programa: ' + current_time)



# Carregar proxies com tratamento de erro
try:
    with open('proxies.txt') as f:
        proxies = [line.strip() for line in f if line.strip()]
    if proxies:
        proxy = random.choice(proxies)
        print(f"Proxy selecionado: {proxy.split(':')[0] if ':' in proxy else proxy}")
    else:
        proxy = None
        print("Arquivo de proxies vazio ou não encontrado")
except FileNotFoundError:
    proxy = None
    print("Arquivo proxies.txt não encontrado - executando sem proxy")
except Exception as e:
    proxy = None
    print(f"Erro ao carregar proxies: {e} - executando sem proxy")

threading.Thread(target=teste).start()
option = webdriver.ChromeOptions()
option.headless = False

# Configurar proxy com autenticação
if proxy:
    if ':' in proxy:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:  # IP:PORTA:USUARIO:SENHA
            proxy_host = proxy_parts[0]
            proxy_port = proxy_parts[1]
            proxy_user = proxy_parts[2]
            proxy_pass = proxy_parts[3]
            
            # Configurar proxy com extensão de autenticação
            option = setup_proxy_with_extension(option, proxy_host, proxy_port, proxy_user, proxy_pass)
            print(f"Proxy configurado com extensão: {proxy_host}:{proxy_port}")
        else:
            option.add_argument(f'--proxy-server=http://{proxy}')
            print(f"Proxy configurado: {proxy}")
    else:
        option.add_argument(f'--proxy-server=http://{proxy}')
        print(f"Proxy configurado: {proxy}")
else:
    print("Executando sem proxy")

service = Service()


#servico = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=option)

# Verificar se proxy foi configurado com sucesso
if proxy and len(proxy.split(':')) == 4:
    proxy_parts = proxy.split(':')
    print(f"🔐 Proxy configurado automaticamente:")
    print(f"   Host: {proxy_parts[0]}")
    print(f"   Porta: {proxy_parts[1]}")
    print(f"   Usuário: {proxy_parts[2]}")
    print(f"   Senha: {'*' * len(proxy_parts[3])}")


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

                        ListandoRotas2.listarTodasRotas(driver, window, tempo_espera)
                    else:
                        break
                    if interface == True:
                        # ListandoRotas2.selecionarOrigemDestino(driver,window,interface)
                        ListandoRotas2.verificarSeExisteDestinoEFiltrar(driver, window)

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
                        ListandoRotas2.listarTodasRotas(driver, window, tempo_espera)
                    else:
                        break

                    if interface == True:
                        ListandoRotas2.verificarSeExisteDestinoEFiltrar(driver, window)
                    else:
                        break
            else:
                window['-OUTPUT-'].update('SELECIONE PARA INICIAR.')
                # time.sleep(1)

                if valid == 1:
                    break
        except Exception as e:
            import traceback
            print('=' * 50)
            print('ERRO CRÍTICO NA APLICAÇÃO:')
            print('ERRO: ' + str(e))
            print('TIPO DO ERRO: ' + str(type(e).__name__))
            print('LOCALIZAÇÃO DO ERRO:')
            traceback.print_exc()
            print('=' * 50)
            
            # Tentar identificar onde está o erro
            if "'NoneType' object has no attribute 'findChildren'" in str(e):
                print('ERRO IDENTIFICADO: Tabela HTML não encontrada ou elemento None')
                print('POSSÍVEIS CAUSAS:')
                print('- Página não carregou completamente')
                print('- Elemento da tabela não existe na página')
                print('- Mudança na estrutura HTML da página')
                print('- Problema de conexão com o portal')
            
            # Tentar verificar se ainda está logado
            try:
                fazendoLogin.verificandoSeTaLogado(driver)
                print('Verificação de login realizada')
            except Exception as login_error:
                print(f'Erro ao verificar login: {login_error}')
            
            print('Aplicação continuando...')
            pass



# Output a message to the window

# Finish up by removing from the screen
window.close()

# Limpar extensão de proxy se foi criada
if proxy and len(proxy.split(':')) == 4:
    cleanup_proxy_extension()

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
