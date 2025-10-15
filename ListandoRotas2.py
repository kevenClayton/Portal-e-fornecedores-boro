"""
Sistema de Gerenciamento de Rotas - Portal E-Fornecedores
========================================================

Este módulo automatiza o processo de vinculação de motoristas às rotas
no portal E-Fornecedores da Usiminas.

Funcionalidades principais:
- Listagem de rotas disponíveis
- Validação de critérios de compatibilidade
- Vinculação automática de motoristas
- Geração de relatórios e logs
- Envio de notificações por email

Autor: Sistema de Automação
Data: 2024
"""

import logging
import sys
import os
import time
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import fazendoLogin
import pandas as pd
import numpy as np
import unidecode
from bs4 import BeautifulSoup
from selenium.webdriver import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Módulos locais
import pegarValorObservacao
import validarLetraProduto
import enviarEmail
import model.db as db
global quantidadeVerificouRota
quantidadeVerificouRota = 0
# Configuração de logging
def configurar_logging(nome_arquivo: str) -> None:
    """Configura o sistema de logging para o arquivo."""
    data_atual = datetime.now().strftime('%d-%m-%Y')
    hora_atual = datetime.now().time()
    
    # Log de informações
    logging.basicConfig(
        filename=f'relatorio_execucao-info-{data_atual}-{nome_arquivo}.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    
    logging.info(f'Iniciando execução do programa: {nome_arquivo} - Data/Hora: {hora_atual}')

# Classes de dados
@dataclass
class DadosRota:
    """Estrutura de dados para informações de uma rota."""
    numero_documento: str
    data: str
    compartilhado: str
    prioridade: str
    tipo_transporte: str
    peso_total: str
    unidade_peso: str
    planta_origem: str
    cluster: str
    estado: str
    observacoes: str = ""
    valor_carga: str = ""
    tem_letra_b: bool = False
    clientes_mesmo_destino: List[str] = None
    mais_de_um_destino: bool = False

@dataclass
class DadosMotorista:
    """Estrutura de dados para informações de um motorista."""
    id_banco: int
    placa: str
    cpf: str
    nome: str
    aceita_bobina: bool
    situacao: int
    placa_carreta: str = ""

class GerenciadorRotas:
    """Classe principal para gerenciamento de rotas e vinculação de motoristas."""
    
    def __init__(self, driver: WebDriver, window=None):
        self.driver = driver
        self.window = window
        self.dados = None
        self.controle_rotas = ControleRotas()
        self.carregar_dados()
        
        # Configurações dos checkboxes
        self.verificar_valor_carga = True
        self.verificar_bobina = True
        self.verificar_multiplos_destinos = True
        
        # Limpar rotas antigas automaticamente (mais de 7 dias)
        self.controle_rotas.limpar_rotas_antigas(7)
        
        # Mostrar estatísticas das rotas processadas
        stats = self.controle_rotas.obter_estatisticas()
        logging.info(f"Controle de rotas inicializado: {stats['total_rotas']} rotas já processadas")
        if stats['ultima_rota']:
            logging.info(f"Última rota processada: {stats['ultima_rota']}")
        
    def carregar_dados(self) -> None:
        """Carrega dados do banco de dados."""
        try:
            self.dados = db.DADOS()
            logging.info("Dados carregados com sucesso do banco de dados")
        except Exception as e:
            logging.error(f"Erro ao carregar dados do banco: {e}")
            raise
    
    def atualizar_interface(self, mensagem: str) -> None:
        """Atualiza a interface do usuário com mensagem de status."""
        if self.window:
            self.window['-OUTPUT-'].update(mensagem)
        print(mensagem)
    
    def mostrar_status_rotas_processadas(self) -> None:
        """Mostra o status das rotas já processadas na interface."""
        try:
            stats = self.controle_rotas.obter_estatisticas()
            proxima_limpeza = self.controle_rotas.obter_proxima_limpeza()
            
            status_msg = f"Rotas processadas: {stats['total_rotas']}"
            if stats['ultima_rota']:
                status_msg += f" | Última: {stats['ultima_rota']}"
            status_msg += f" | Próxima limpeza: {proxima_limpeza}"
            
            self.atualizar_interface(status_msg)
            logging.info(status_msg)
        except Exception as e:
            logging.error(f"Erro ao mostrar status das rotas: {e}")
    
    def listar_todas_rotas(self, tempo_espera: int = 30, verificar_valor_carga: bool = True, verificar_bobina: bool = True, verificar_multiplos_destinos: bool = True) -> None:
        """Navega para a página de listagem de rotas e configura filtros iniciais."""
        global quantidadeVerificouRota
        try:
            # Configurar as opções dos checkboxes
            self.verificar_valor_carga = verificar_valor_carga
            self.verificar_bobina = verificar_bobina
            self.verificar_multiplos_destinos = verificar_multiplos_destinos
            
            logging.info(f"Configurações: Verificar valor da carga: {verificar_valor_carga}")
            logging.info(f"Configurações: Verificar bobina: {verificar_bobina}")
            logging.info(f"Configurações: Verificar múltiplos destinos: {verificar_multiplos_destinos}")
            
            # Mostrar status das rotas já processadas
            self.mostrar_status_rotas_processadas()
            urlAtual = self.driver.current_url

            parsed_url = urlparse(urlAtual)
            parametros = parsed_url.query
           
            self.atualizar_interface('BUSCANDO TODAS AS ROTAS...')
            if quantidadeVerificouRota >= 1 and parametros =='cmp=SUCargaProgramadaList.ascx' or parametros.__contains__("cmp=SUCargaProgramada.ascx"):
                self.atualizar_interface(f'Aguardando {tempo_espera}s para verificar novamente...')
                time.sleep(tempo_espera)
            else:
                print("Login novamente ou não verificou todas cargas")

            quantidadeVerificouRota = quantidadeVerificouRota + 1
            urlAtual = self.driver.current_url
            parsed_url = urlparse(urlAtual)
            parametros = parsed_url.query
            if parametros =='cmp=SUCargaProgramadaList.ascx' or parametros.__contains__("cmp=SUCargaProgramada.ascx"):
                self.atualizar_interface(f'Já está na tela correta, e já verificou novos cluester, só recarregar pra conferir')
                self.driver.refresh()
                return

            # Selecionar empresa
            self.driver.find_element("id", "mnuPrincipal_lstEmpresas").click()
            time.sleep(0.2)
            
            # Selecionar empresa Soluções Usiminas (valor 85)
            select_empresa = Select(self.driver.find_element("id", "mnuPrincipal_lstEmpresas"))
            select_empresa.select_by_value("85")
            time.sleep(0.2)
            
            # Navegar para página de rotas
            url_rotas = 'https://portal.e-fornecedores.ind.br/Default.aspx?cmp=SUCargaProgramada.ascx&tipo=vnc&menu=yes'
            self.driver.get(url_rotas)
            time.sleep(0.2)
            
            # Clicar em pesquisar
            self.driver.find_element("id", "ctlLoadedControl_btnPesquisa").click()
            time.sleep(1)
            
            logging.info("Navegação para página de rotas concluída")
            
        except Exception as e:
            logging.error(f"Erro ao listar rotas: {e}")
            self.atualizar_interface(f"ERRO: {e}")
            urlAtual = self.driver.current_url
            parsed_url = urlparse(urlAtual)
            parametros = parsed_url.query
            if parametros == 'cmp=login.ascx':
                print("Caiu no loging, refazendo login")
                fazendoLogin.fazendoLogin(self.driver, self.dados['login'])
            else:
                print("Erro ao listar rotas")
            raise
    
    def validar_opcao_select(self, id_select: str, valor_desejado: str) -> bool:
        """Valida se uma opção existe em um elemento select."""
        try:
            options = self.driver.find_element("id", id_select).text
            logging.info(f"Opções disponíveis no select {id_select}: {options}")
            
            opcoes = options.split('\n')
            valor_desejado = valor_desejado.strip()
            
            for opcao in opcoes:
                if valor_desejado == opcao.strip():
                    logging.info(f'Opção encontrada: {opcao}')
                    return True
            
            logging.warning(f'Opção não encontrada: {valor_desejado}')
            return False
            
        except Exception as e:
            logging.error(f"Erro ao validar opção no select: {e}")
            return False
    
    def selecionar_origem_destino(self, interface_ativa: bool = True) -> None:
        """Processa todas as origens e destinos configurados."""
        for origem in self.dados['origens']:
            if not interface_ativa:
                break
                
            valor_origem = origem[1]
            id_select_origem = 'ctlLoadedControl_ddlOrigem'
            
            # Validação da origem (comentada no código original)
            existe_origem = True  # self.validar_opcao_select(id_select_origem, valor_origem)
            
            if existe_origem:
                logging.info(f"Processando origem: {valor_origem}")
                self.verificar_destinos_e_filtrar()
            else:
                status = f"Origem não encontrada no filtro: {valor_origem}"
                self.atualizar_interface(status)
    
    def verificar_destinos_e_filtrar(self) -> None:
        """Verifica destinos disponíveis e aplica filtros."""
        try:
            array_destinos = np.array(self.dados['select_destinos_motoristas_ativos'])
            id_select_cluster = 'ctlLoadedControl_ddlCluster'
            
            options = self.driver.find_element("id", id_select_cluster).text
            logging.info(f"Destinos disponíveis no portal: {options}")
            
            opcoes = options.split('\n')
            opcoesIndex = 0
            opcoesIndexInexistente = 0
            opcoesIndexExistente = 0
            clusterSelecionado = Select(self.driver.find_element('id', id_select_cluster)).first_selected_option.text
            for destino in opcoes:
                primeiraOpcao = opcoes[0]
                destino_limpo = destino.strip()
                opcoesIndex = opcoesIndex + 1
                if destino_limpo in array_destinos:
                    if clusterSelecionado == destino_limpo:
                        # Selecionar o proximo destino
                        self.atualizar_interface("Cluster ja foi verificado, verificando os proximos")
                        select = Select(self.driver.find_element('id', id_select_cluster))                    
                        select.select_by_value(primeiraOpcao.strip())
                        clusterSelecionado = Select(self.driver.find_element('id', id_select_cluster)).first_selected_option.text
                        time.sleep(2)
                        self.aplicar_filtro()
                        continue
                    status = f"Verificando cluster existente: {destino_limpo}"
                    self.atualizar_interface(status)
                    select = Select(self.driver.find_element('id', id_select_cluster))
                    select.select_by_value(destino_limpo)                    
                    time.sleep(1)
                    opcoesIndexExistente = opcoesIndexExistente + 1
                    self.aplicar_filtro()
                    self.processar_resultados_rota(destino_limpo)
                    continue
                else:
                    status = f"Cluster não existente na base: {destino_limpo}"
                    self.atualizar_interface(status)
                    opcoesIndexInexistente = opcoesIndexInexistente + 1
                    status = f"Total de opções existentes: {opcoesIndexExistente}"
                    logging.info(status)
                    self.atualizar_interface(status)
                    status = f"Total de opções inexistentes: {opcoesIndexInexistente}"
                    self.atualizar_interface(status)
                    status = f"Total de opções: {opcoesIndex}"
                    self.atualizar_interface(status)
                    if(len(opcoes) == opcoesIndexInexistente):
                        status = f"Não foi encontrada nenhum planta que é atendida por nenhum motorista."
                        self.atualizar_interface(status)
                        logging.info(status)
                        self.atualizar_interface(status)
                        return
                    continue
        except Exception as e:
            logging.error(f"Erro ao verificar destinos: {e}")
            raise
    
    def aplicar_filtro(self) -> None:
        """Aplica o filtro de pesquisa."""
        try:
            print("Aplicando filtro de rota...")
            self.driver.find_element("id", "ctlLoadedControl_btnFiltrar").click()
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Erro ao aplicar filtro: {e}")
            raise
    
    def processar_resultados_rota(self, destino: str) -> None:
        """Processa os resultados das rotas encontradas."""
        try:
            html_prod = self.driver.page_source
            soup = BeautifulSoup(html_prod, 'lxml')
            tabela = soup.find('table', id='ctlLoadedControl_dgRight')
            
            if not tabela:
                logging.warning("Tabela de resultados não encontrada")
                return
            
            linhas = tabela.findChildren('tr')
            tabela_completa = pd.read_html(str(tabela), skiprows=1)[0]
            dados_tabela = tabela_completa.to_dict('split')['data']
            
            for rota_dados in dados_tabela:

                if self.controle_rotas.ja_processou_rota(str(rota_dados[0])):
                    self.atualizar_interface(f"Já entrou nessa rota, não vai entrar de novo, documento: {rota_dados[0]}")
                    logging.info(f"Rota já processada: {rota_dados[0]}")
                    time.sleep(1)
                    continue

                rota = self.criar_objeto_rota(rota_dados)
                self.processar_rota_individual(rota, destino)
                
        except Exception as e:
            logging.error(f"Erro ao processar resultados: {e}")
            raise
    
    def criar_objeto_rota(self, dados_rota: List) -> DadosRota:
        """Cria objeto DadosRota a partir dos dados da tabela."""
        try:
            rota = DadosRota(
                numero_documento=self._tratar_valor_nan(dados_rota[0]),
                data=self._tratar_valor_nan(dados_rota[3]),
                compartilhado=self._tratar_valor_nan(dados_rota[4]),
                prioridade=self._tratar_valor_nan(dados_rota[5]),
                tipo_transporte=self._tratar_valor_nan(dados_rota[6]),
                peso_total=self._tratar_valor_nan(dados_rota[7]),
                unidade_peso=self._tratar_valor_nan(dados_rota[8]),
                planta_origem=self._tratar_valor_nan(dados_rota[9]),
                cluster=self._tratar_valor_nan(dados_rota[10]),
                estado=self._tratar_valor_nan(dados_rota[11])
            )
            
            # Obter dados adicionais baseado nas configurações dos checkboxes
            # rota.observacoes = validarLetraProduto.pegarObservacoesRota(self.driver, rota.numero_documento)
            
            # Verificar valor da carga (condicional)
            if self.verificar_valor_carga:
                try:
                    valor_carga_raw = pegarValorObservacao.tratarValorNoCampoObservacao(self.driver, rota.numero_documento)
                    if valor_carga_raw and str(valor_carga_raw).lower() != 'nan':
                        rota.valor_carga = valor_carga_raw.strip().split(',')[0]
                    else:
                        rota.valor_carga = ""
                except Exception as e:
                    logging.warning(f"Erro ao obter valor da carga para documento {rota.numero_documento}: {e}")
                    rota.valor_carga = ""
            else:
                rota.valor_carga = ""
                logging.info(f"Verificação de valor da carga desabilitada para documento {rota.numero_documento}")
            
            # Verificar bobina (condicional)
            if self.verificar_bobina:
                try:
                    rota.tem_letra_b = validarLetraProduto.verificarTemLetraB(self.driver, rota.numero_documento)
                except Exception as e:
                    logging.warning(f"Erro ao verificar bobina para documento {rota.numero_documento}: {e}")
                    rota.tem_letra_b = False
            else:
                rota.tem_letra_b = False
                logging.info(f"Verificação de bobina desabilitada para documento {rota.numero_documento}")
            
            # Verificar múltiplos destinos (condicional)
            if self.verificar_multiplos_destinos:
                try:
                    dados_destinos = validarLetraProduto.verificarMultiplosDestinos(self.driver, rota.numero_documento)
                    if dados_destinos and len(dados_destinos) > 2:
                        rota.clientes_mesmo_destino = self._tratar_valor_nan(dados_destinos[1])
                        rota.mais_de_um_destino = bool(dados_destinos[2]) if dados_destinos[2] is not None else False
                    else:
                        rota.clientes_mesmo_destino = ""
                        rota.mais_de_um_destino = False
                except Exception as e:
                    logging.warning(f"Erro ao verificar múltiplos destinos para documento {rota.numero_documento}: {e}")
                    rota.clientes_mesmo_destino = ""
                    rota.mais_de_um_destino = False
            else:
                rota.clientes_mesmo_destino = ""
                rota.mais_de_um_destino = False
                logging.info(f"Verificação de múltiplos destinos desabilitada para documento {rota.numero_documento}")
            
            return rota
            
        except Exception as e:
            logging.error(f"Erro ao criar objeto rota: {e}")
            raise
    
    def processar_rota_individual(self, rota: DadosRota, destino: str) -> None:
        """Processa uma rota individual verificando compatibilidade."""
        try:
            for tipo_veiculo in self.dados['tipo_veiculo']:
                tipo_veiculo_valor = tipo_veiculo[1]
                print(f'TIPO: {tipo_veiculo_valor}')
                
                self.atualizar_interface('VALIDANDO RESULTADOS...')
                
                if self.validar_compatibilidade_transporte(rota, tipo_veiculo_valor):
                    self.tentar_vincular_motorista(rota, destino, tipo_veiculo_valor)
                    break
                else:
                    self.registrar_rota_incompativel(rota, destino, "Não possui tipo veículo")
                    
        except Exception as e:
            logging.error(f"Erro ao processar rota individual: {e}")
            raise
    
    def validar_compatibilidade_transporte(self, rota: DadosRota, tipo_veiculo: str) -> bool:
        """Valida se o tipo de transporte é compatível e atende aos parâmetros de valor."""
        try:
            if tipo_veiculo.lower() != rota.tipo_transporte.lower():
                return False
            
            if self.verificar_valor_carga == False:                
                return True

            valor_carga_formatado = float(rota.valor_carga.replace(".", ""))
            valor_parametro_carreta = round(self.dados['parametros'][0][3], 2)
            valor_parametro_truck = round(self.dados['parametros'][0][1], 2)
            
            if (rota.tipo_transporte.lower().__contains__('carreta') and 
                valor_carga_formatado <= valor_parametro_carreta):
                return True
            elif (rota.tipo_transporte.lower().__contains__('truck') and 
                  valor_carga_formatado <= valor_parametro_truck):
                return True
            
            self.registrar_rota_incompativel(rota, rota.cluster, "Valor maior que o configurado")
            return False
            
        except Exception as e:
            logging.error(f"Erro ao validar compatibilidade: {e}")
            return False
    
    def tentar_vincular_motorista(self, rota: DadosRota, destino: str, tipo_transporte: str) -> None:
        """Tenta vincular um motorista à rota."""
        try:
            self.atualizar_interface(f'Parâmetros OK: {tipo_transporte} - {rota.valor_carga}')
            
            # Debug da página antes de processar
            self._debug_pagina_atual()
            
            # Verificar se a página está carregada corretamente
            if not self._verificar_pagina_carregada('ctlLoadedControl_dgRight', 'Tabela de resultados'):
                logging.error(f"Página não carregada corretamente para documento: {rota.numero_documento}")
                self.atualizar_interface(f"ERRO: Página não carregada para documento {rota.numero_documento}")
                return
            
            # Obter ID do botão vincular
            html_prod = self.driver.page_source
            soup = BeautifulSoup(html_prod, 'lxml')
            tabela = soup.find('table', id='ctlLoadedControl_dgRight')
            
            # Verificar se a tabela foi encontrada
            if not tabela:
                logging.error(f"Tabela de resultados não encontrada para documento: {rota.numero_documento}")
                self.atualizar_interface(f"ERRO: Tabela não encontrada para documento {rota.numero_documento}")
                return
            
            linhas = tabela.findChildren('tr')
            
            if not linhas:
                logging.error(f"Nenhuma linha encontrada na tabela para documento: {rota.numero_documento}")
                self.atualizar_interface(f"ERRO: Nenhuma linha encontrada para documento {rota.numero_documento}")
                return
            
            id_botao_vincular = self.obter_id_botao_vincular(linhas, rota.numero_documento)
            
            if not id_botao_vincular:
                logging.error(f"Botão vincular não encontrado para documento: {rota.numero_documento}")
                return
            
            # Clicar no botão vincular
            self.driver.find_element("id", id_botao_vincular).click()
            logging.info(f'Clicou no botão vincular para rota: {rota.numero_documento}')
            
            # Processar vinculação
            self.processar_vinculacao_motorista2(rota, destino, tipo_transporte)
            
            time.sleep(0.2)
            self.driver.back()
            
        except Exception as e:
            logging.error(f"Erro ao tentar vincular motorista: {e}")
            # Debug adicional em caso de erro
            self._debug_pagina_atual()
            raise
    
    def obter_id_botao_vincular(self, linhas, numero_documento: str) -> str:
        """Obtém o ID do botão vincular para um documento específico."""
        try:
            if not linhas:
                logging.warning("Lista de linhas vazia ao buscar botão vincular")
                return ""
            
            for i, linha in enumerate(linhas):
                if i == 0:  # Pular cabeçalho
                    continue
                
                if not linha:
                    logging.warning(f"Linha {i} é None ao buscar botão vincular")
                    continue
                    
                try:
                    celulas = linha.findChildren('td')
                    if len(celulas) >= 3:
                        numero_documento_linha = celulas[0].text.strip()
                        if str(numero_documento) == numero_documento_linha:
                            inputs = celulas[2].findChildren('input')
                            if inputs:
                                return inputs[0].get('id')
                except AttributeError as e:
                    logging.warning(f"Erro ao processar linha {i}: {e}")
                    continue
                except Exception as e:
                    logging.warning(f"Erro inesperado ao processar linha {i}: {e}")
                    continue
            
            return ""
            
        except Exception as e:
            logging.error(f"Erro ao obter ID do botão vincular: {e}")
            return ""
    
    def processar_vinculacao_motorista(self, rota: DadosRota, destino: str, tipo_transporte: str) -> None:
        """Processa a vinculação de motorista à rota."""
        try:
            self.controle_rotas.marcar_rota_processada(rota.numero_documento)
            
            for motorista_dados in self.dados['motoristas']:
                motorista = self.criar_objeto_motorista(motorista_dados)
                
                if not self.validar_motorista_basico(motorista, rota):
                    continue
                
                if self.validar_compatibilidade_motorista(motorista, rota, destino, tipo_transporte):
                    if self.realizar_vinculacao(motorista, rota, destino, tipo_transporte):
                        return
            
            # Se chegou aqui, não encontrou motorista compatível
            self.registrar_rota_incompativel(rota, destino, "Não tem motorista para rota")
            
        except Exception as e:
            logging.error(f"Erro ao processar vinculação: {e}")
            raise
    
    def processar_vinculacao_motorista2(self, rota: DadosRota, destino: str, tipo_transporte: str) -> None:
        """Processa a vinculação de motorista à rota."""
        try:
            self.controle_rotas.marcar_rota_processada(rota.numero_documento)
            motoristasDisponivelParaVinculacao = db.motoristasDisponivelParaVinculacao(rota, destino, tipo_transporte)
            if len(motoristasDisponivelParaVinculacao) == 0:
                self.registrar_rota_incompativel(rota, destino, "Não tem motorista para rota")
                self.atualizar_interface(f"Não tem motorista para rota: {rota.numero_documento}")
                logging.info(f"Não tem motorista para rota: {rota.numero_documento}")                
                return

            for motorista_dados in motoristasDisponivelParaVinculacao:
                motorista = self.criar_objeto_motorista(motorista_dados)

                if self.realizar_vinculacao(motorista, rota, destino, tipo_transporte):
                    return
            
            # Se chegou aqui, não encontrou motorista compatível
            self.registrar_rota_incompativel(rota, destino, "Não tem motorista para rota")
            
        except Exception as e:
            logging.error(f"Erro ao processar vinculação: {e}")
            raise
    
    def criar_objeto_motorista(self, dados_motorista: List) -> DadosMotorista:
        """Cria objeto DadosMotorista a partir dos dados do banco."""
        try:
            motorista = DadosMotorista(
                id_banco=dados_motorista[0],
                placa=dados_motorista[1],
                cpf=dados_motorista[2],
                nome=dados_motorista[3],
                aceita_bobina=dados_motorista[8] == 1,
                situacao=dados_motorista[9],
                placa_carreta=dados_motorista[13] if len(dados_motorista) > 13 else ""
            )
            return motorista
            
        except Exception as e:
            logging.error(f"Erro ao criar objeto motorista: {e}")
            raise
    
    def validar_motorista_basico(self, motorista: DadosMotorista, rota: DadosRota) -> bool:
        """Validações básicas do motorista."""
        if rota.tem_letra_b and not motorista.aceita_bobina:
            print(f"Motorista não aceita bobina: {motorista.nome}")
            return False
        
        if motorista.situacao != 1:
            print(f"Motorista desativado: {motorista.nome}")
            return False
        
        return True

    def realizar_vinculacao(self, motorista: DadosMotorista, rota: DadosRota, 
                          destino: str, tipo_transporte: str) -> bool:
        """Realiza a vinculação efetiva do motorista à rota."""
        try:
            status = f'Motorista compatível: {motorista.nome} - Placa: {motorista.placa} - CPF: {motorista.cpf}'
            self.atualizar_interface(status)
            
            # Preencher dados do veículo
            self.preencher_dados_veiculo(motorista, tipo_transporte)
            
            # Preencher dados do motorista
            self.preencher_dados_motorista(motorista)
            
            # Validar dados finais
            if not self.validar_dados_finais(motorista, destino):
                return False
            
            # Executar vinculação
            if self.dados['parametros'][0][4] == 0:  # Modo produção
                return self.executar_vinculacao_producao(motorista, rota, destino, tipo_transporte)
            else:  # Modo teste
                return self.executar_vinculacao_teste(motorista, rota)
                
        except Exception as e:
            logging.error(f"Erro ao realizar vinculação: {e}")
            return False
    
    def preencher_dados_veiculo(self, motorista: DadosMotorista, tipo_transporte: str) -> None:
        """Preenche os dados do veículo no formulário."""
        try:
            # Placa principal
            campo_placa = self.driver.find_element("id", "ctlLoadedControl_txtPlaca1")
            campo_placa.clear()
            campo_placa.send_keys(motorista.placa)
            
            # Placa da carreta (se aplicável)
            array_motorista_tipo_veiculo_carreta = np.array(self.dados['motoristas_tipo_veiculo_carreta'])
            if (tipo_transporte in array_motorista_tipo_veiculo_carreta and 
                motorista.placa_carreta):
                campo_placa_carreta = self.driver.find_element("id", "ctlLoadedControl_txtPlaca2")
                campo_placa_carreta.clear()
                campo_placa_carreta.send_keys(motorista.placa_carreta)
            
            # Buscar veículo
            self.driver.find_element("id", "ctlLoadedControl_btnBuscarVeiculo").click()
            time.sleep(0.5)
            
            # Tratar alertas
            self.tratar_alerta("veículo")
            
        except Exception as e:
            logging.error(f"Erro ao preencher dados do veículo: {e}")
            raise
    
    def preencher_dados_motorista(self, motorista: DadosMotorista) -> None:
        """Preenche os dados do motorista no formulário."""
        try:
            campo_cpf = self.driver.find_element("id", "ctlLoadedControl_txtCPF")
            campo_cpf.clear()
            campo_cpf.send_keys(motorista.cpf)
            
            self.driver.find_element("id", "ctlLoadedControl_btnBuscarMotorista").click()
            time.sleep(0.5)
            
            # Tratar alertas
            self.tratar_alerta("motorista")
            
        except Exception as e:
            logging.error(f"Erro ao preencher dados do motorista: {e}")
            raise
    
    def tratar_alerta(self, tipo: str) -> None:
        """Trata alertas do navegador."""
        try:
            alert = self.driver.switch_to.alert
            logging.warning(f'Alerta {tipo}: {alert.text}')
            alert.accept()
        except:
            logging.info(f'Não há alerta para {tipo}')
    
    def validar_dados_finais(self, motorista: DadosMotorista, destino: str) -> bool:
        """Validação final dos dados antes da vinculação."""
        try:
            dados_db = db.dadosDBParaVincular(motorista.id_banco, destino)
            motoristas_destino = dados_db['motorista_destino']
            
            if len(motoristas_destino) == 0:
                status = f'Motorista não passou na validação final: {motorista.nome} - CPF: {motorista.cpf}'
                logging.warning(status)
                enviarEmail.enviarEmailGenerico("Motorista não passou na validação final", status)
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Erro na validação final: {e}")
            return False
    
    def executar_vinculacao_producao(self, motorista: DadosMotorista, rota: DadosRota, 
                                   destino: str, tipo_transporte: str) -> bool:
        """Executa a vinculação em modo produção."""
        try:
            # Clicar em salvar
            self.driver.find_element("id", "ctlLoadedControl_btnSalvar").click()
            
            # Tratar alertas
            self.tratar_alerta("vinculação")
            
            # Verificar resultado
            texto_resultado = self.driver.find_element("id", "ctlLoadedControl_lblMessage").text
            texto_observacao = self.driver.find_element("id", "ctlLoadedControl_txtObs").text
            time.sleep(2)
            if "CHAPA EXCEDENTE" in texto_observacao:
                self.registrar_chapa_excedente(motorista, rota, destino, tipo_transporte)
                return False
            
            if "sucesso" in texto_resultado.lower():
                self.registrar_vinculacao_sucesso(motorista, rota, destino, tipo_transporte)
                return True
            else:
                self.registrar_erro_vinculacao(motorista, rota, destino, tipo_transporte, texto_resultado)
                return False
                
        except Exception as e:
            logging.error(f"Erro na vinculação produção: {e}")
            return False
    
    def executar_vinculacao_teste(self, motorista: DadosMotorista, rota: DadosRota) -> bool:
        """Executa a vinculação em modo teste."""
        try:
            time.sleep(2)
            self.driver.back()
            status = f"Modo teste: Nao vinculou documento {rota.numero_documento}"
            logging.info(status)
            self.atualizar_interface('Era para vincular, mas esta no modo teste. NAO VINCULADO!')
            enviarEmail.enviarEmailGenerico("Modo teste habilitado", status)
            return False
            
        except Exception as e:
            logging.error(f"Erro na vinculacao teste: {e}")
            return False
    
    def registrar_chapa_excedente(self, motorista: DadosMotorista, rota: DadosRota, 
                                destino: str, tipo_transporte: str) -> None:
        """Registra erro de chapa excedente."""
        status = f'Chapa excedente: Doc {rota.numero_documento} - Motorista: {motorista.nome}'
        logging.warning(status)
        enviarEmail.enviarEmailGenerico("Chapa excedente", status)
        self.registrar_rota_incompativel(rota, destino, "Chapa excedente ao vincular")
    
    def registrar_vinculacao_sucesso(self, motorista: DadosMotorista, rota: DadosRota, 
                                   destino: str, tipo_transporte: str) -> None:
        """Registra sucesso na vinculação."""
        logging.info(f'Vinculação realizada com sucesso: {motorista.nome} - Doc: {rota.numero_documento}')
        enviarEmail.enviarEmailRotaVinculada([motorista.id_banco, motorista.placa, motorista.cpf, motorista.nome], rota.numero_documento)
        
        # Gravar no banco
        db.gravarRotas(rota.planta_origem, destino, rota.numero_documento, rota.data,
                   rota.valor_carga, motorista.nome, rota.tipo_transporte, motorista.situacao)
        
        # Atualizar situação do motorista
        db.atualizarSituacaoMotorista(motorista.id_banco)
        
        # Recarregar dados
        self.carregar_dados()
        
        # Continuar processamento
        self.listar_todas_rotas()
        self.verificar_destinos_e_filtrar()
    
    def registrar_erro_vinculacao(self, motorista: DadosMotorista, rota: DadosRota, 
                                destino: str, tipo_transporte: str, erro: str) -> None:
        """Registra erro na vinculação."""
        self.driver.back()
        status = f'Erro na vinculação: {erro} - Doc: {rota.numero_documento} - Motorista: {motorista.nome}'
        logging.error(status)
        self.atualizar_interface(status)
        enviarEmail.enviarEmailGenerico("Erro ao tentar vincular", status)
        self.registrar_rota_incompativel(rota, destino, erro)
    
    def registrar_rota_incompativel(self, rota: DadosRota, destino: str, motivo: str) -> None:
        """Registra rota incompatível no relatório."""
        try:
            # Tratar valores NaN antes de enviar para o banco
            planta_origem = self._tratar_valor_nan(rota.planta_origem)
            destino_limpo = self._tratar_valor_nan(destino)
            numero_documento = self._tratar_valor_nan(rota.numero_documento)
            data = self._tratar_valor_nan(rota.data)
            valor_carga = self._tratar_valor_nan(rota.valor_carga)
            tipo_transporte = self._tratar_valor_nan(rota.tipo_transporte)
            peso_total = self._tratar_valor_nan(rota.peso_total)
            observacoes = self._tratar_valor_nan(rota.observacoes)
            prioridade = self._tratar_valor_nan(rota.prioridade)
            clientes = self._tratar_valor_nan(rota.clientes_mesmo_destino)
            mais_de_um_destino = self._tratar_valor_nan(rota.mais_de_um_destino)
            motivo_limpo = self._tratar_valor_nan(motivo)
            
            gravarRotasRelatorio(
                planta_origem, destino_limpo, numero_documento, data,
                valor_carga, tipo_transporte, peso_total, observacoes,
                prioridade, clientes, mais_de_um_destino, motivo_limpo
            )
        except Exception as e:
            logging.error(f"Erro ao registrar rota incompatível: {e}")
    
    def _tratar_valor_nan(self, valor) -> str:
        """Trata valores NaN convertendo para string vazia."""
        if valor is None:
            return ""
        
        # Converter para string primeiro
        valor_str = str(valor)
        
        # Verificar se é NaN (pandas) ou 'nan' (string)
        if (valor_str.lower() == 'nan' or 
            valor_str.lower() == 'none' or 
            valor_str.lower() == 'null' or
            valor_str.strip() == ''):
            return ""
        
        return valor_str.strip()
    
    def _verificar_pagina_carregada(self, elemento_id: str, descricao: str = "") -> bool:
        """Verifica se a página está carregada corretamente verificando um elemento específico."""
        try:
            # Aguardar um pouco para a página carregar
            time.sleep(1)
            
            # Verificar se o elemento existe
            elemento = self.driver.find_element("id", elemento_id)
            if elemento:
                logging.info(f"Elemento {elemento_id} ({descricao}) encontrado - Página carregada")
                return True
            else:
                logging.warning(f"Elemento {elemento_id} ({descricao}) não encontrado")
                return False
                
        except Exception as e:
            logging.error(f"Erro ao verificar elemento {elemento_id} ({descricao}): {e}")
            return False
    
    def _debug_pagina_atual(self) -> None:
        """Função de debug para verificar o estado atual da página."""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            page_source_length = len(self.driver.page_source)
            
            logging.info(f"DEBUG - URL atual: {current_url}")
            logging.info(f"DEBUG - Título da página: {page_title}")
            logging.info(f"DEBUG - Tamanho do HTML: {page_source_length} caracteres")
            
            # Verificar elementos importantes
            elementos_importantes = [
                ('ctlLoadedControl_dgRight', 'Tabela de resultados'),
                ('mnuPrincipal_lstEmpresas', 'Lista de empresas'),
                ('ctlLoadedControl_ddlCluster', 'Select de cluster')
            ]
            
            for elemento_id, descricao in elementos_importantes:
                self._verificar_pagina_carregada(elemento_id, descricao)
                
        except Exception as e:
            logging.error(f"Erro no debug da página: {e}")


class ControleRotas:
    """Classe para controle de rotas já processadas."""
    
    def __init__(self):
        self.arquivo_rotas_processadas = 'rotas_processadas.txt'
        self.rotas_processadas = self._carregar_rotas_processadas()
        self.ultima_rota_email = None
        self.ultima_rota_vincular = None
        self.quantidadeVerificouRota = 0
        
        # Controle de limpeza automática
        self.ultima_limpeza = datetime.now()
        self.intervalo_limpeza_minutos = 1  # Limpar a cada 5 minutos
    
    def ja_processou_rota(self, numero_documento: str) -> bool:
        """Verifica se a rota já foi processada."""
        return numero_documento in self.rotas_processadas
    
    def _carregar_rotas_processadas(self) -> set:
        """Carrega rotas processadas do arquivo."""
        try:
            if os.path.exists(self.arquivo_rotas_processadas):
                with open(self.arquivo_rotas_processadas, 'r', encoding='utf-8') as f:
                    rotas = set(line.strip() for line in f if line.strip())
                logging.info(f"Carregadas {len(rotas)} rotas processadas do arquivo")
                return rotas
            else:
                logging.info("Arquivo de rotas processadas não encontrado, iniciando com set vazio")
                return set()
        except Exception as e:
            logging.error(f"Erro ao carregar rotas processadas: {e}")
            return set()
    
    def _salvar_rotas_processadas(self) -> None:
        """Salva rotas processadas no arquivo."""
        try:
            with open(self.arquivo_rotas_processadas, 'w', encoding='utf-8') as f:
                for rota in sorted(self.rotas_processadas):
                    f.write(f"{rota}\n")
            logging.info(f"Salvas {len(self.rotas_processadas)} rotas processadas no arquivo")
        except Exception as e:
            logging.error(f"Erro ao salvar rotas processadas: {e}")
    
    def marcar_rota_processada(self, numero_documento: str) -> None:
        """Marca uma rota como processada."""
        self.rotas_processadas.add(numero_documento)
        self.ultima_rota_vincular = numero_documento
        # Salvar automaticamente após marcar
        self._salvar_rotas_processadas()
        
        # Verificar se é hora de fazer limpeza automática
        self.verificar_limpeza_automatica()       
    
    def ja_enviou_email_destino_diferente(self, numero_documento: str) -> bool:
        """Verifica se já foi enviado email para rota com destino diferente."""
        if numero_documento == self.ultima_rota_email:
            return True
        else:
            self.ultima_rota_email = numero_documento
            return False
    
    def limpar_rotas_antigas(self, dias_limpeza: int = 7) -> None:
        """Remove rotas processadas mais antigas que X dias."""
        try:
            from datetime import datetime, timedelta
            data_limite = datetime.now() - timedelta(days=dias_limpeza)
            
            rotas_para_remover = set()
            for rota in self.rotas_processadas:
                # Tentar extrair data da rota (assumindo formato DD/MM/AAAA)
                try:
                    if '/' in rota:
                        partes = rota.split('/')
                        if len(partes) == 3:
                            data_rota = datetime.strptime(f"{partes[2]}-{partes[1]}-{partes[0]}", "%Y-%m-%d")
                            if data_rota < data_limite:
                                rotas_para_remover.add(rota)
                except:
                    continue
            
            if rotas_para_remover:
                self.rotas_processadas -= rotas_para_remover
                self._salvar_rotas_processadas()
                logging.info(f"Removidas {len(rotas_para_remover)} rotas antigas (mais de {dias_limpeza} dias)")
                
        except Exception as e:
            logging.error(f"Erro ao limpar rotas antigas: {e}")
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas das rotas processadas."""
        return {
            'total_rotas': len(self.rotas_processadas),
            'ultima_rota': self.ultima_rota_vincular,
            'arquivo': self.arquivo_rotas_processadas,
            'intervalo_limpeza_minutos': self.intervalo_limpeza_minutos,
            'proxima_limpeza': self.obter_proxima_limpeza(),
            'ultima_limpeza': self.ultima_limpeza.strftime('%H:%M:%S') if self.ultima_limpeza else 'Nunca'
        }
    
    def limpar_todas_rotas_processadas(self) -> None:
        """Limpa todas as rotas processadas (útil para resetar o sistema)."""
        try:
            self.rotas_processadas.clear()
            self.ultima_rota_vincular = None
            self._salvar_rotas_processadas()
            self.ultima_limpeza = datetime.now()  # Resetar timer de limpeza
            logging.info("Todas as rotas processadas foram limpas")
        except Exception as e:
            logging.error(f"Erro ao limpar rotas processadas: {e}")
    
    def forcar_limpeza_agora(self) -> None:
        """Força a limpeza das rotas processadas imediatamente."""
        try:
            logging.info("Forçando limpeza manual das rotas processadas")
            self.limpar_todas_rotas_processadas()
            self.ultima_limpeza = datetime.now()
        except Exception as e:
            logging.error(f"Erro ao forçar limpeza: {e}")
    
    def adicionar_rota_processada_manual(self, numero_documento: str) -> None:
        """Adiciona manualmente uma rota como processada."""
        try:
            self.rotas_processadas.add(numero_documento)
            self._salvar_rotas_processadas()
            logging.info(f"Rota {numero_documento} adicionada manualmente como processada")
        except Exception as e:
            logging.error(f"Erro ao adicionar rota manualmente: {e}")
    
    def verificar_limpeza_automatica(self) -> bool:
        """Verifica se é hora de fazer limpeza automática das rotas processadas."""
        try:
            tempo_atual = datetime.now()
            tempo_desde_ultima_limpeza = tempo_atual - self.ultima_limpeza
            minutos_desde_ultima_limpeza = tempo_desde_ultima_limpeza.total_seconds() / 60
            
            if minutos_desde_ultima_limpeza >= self.intervalo_limpeza_minutos:
                logging.info(f"Executando limpeza automática após {minutos_desde_ultima_limpeza:.1f} minutos")
                self.limpar_todas_rotas_processadas()
                self.ultima_limpeza = tempo_atual
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao verificar limpeza automática: {e}")
            return False
    
    def configurar_intervalo_limpeza(self, minutos: int) -> None:
        """Configura o intervalo de limpeza automática em minutos."""
        try:
            if minutos < 1:
                minutos = 1
            self.intervalo_limpeza_minutos = minutos
            logging.info(f"Intervalo de limpeza automática configurado para {minutos} minutos")
        except Exception as e:
            logging.error(f"Erro ao configurar intervalo de limpeza: {e}")
    
    def obter_proxima_limpeza(self) -> str:
        """Retorna quando será a próxima limpeza automática."""
        try:
            tempo_atual = datetime.now()
            tempo_desde_ultima_limpeza = tempo_atual - self.ultima_limpeza
            minutos_desde_ultima_limpeza = tempo_desde_ultima_limpeza.total_seconds() / 60
            minutos_restantes = self.intervalo_limpeza_minutos - minutos_desde_ultima_limpeza
            
            if minutos_restantes <= 0:
                return "Agora"
            elif minutos_restantes < 1:
                segundos_restantes = int(minutos_restantes * 60)
                return f"Em {segundos_restantes} segundos"
            else:
                return f"Em {minutos_restantes:.1f} minutos"
                
        except Exception as e:
            logging.error(f"Erro ao calcular próxima limpeza: {e}")
            return "Desconhecido"


# Função principal
def executar_sistema_rotas(driver: WebDriver, window=None, interface_ativa: bool = True) -> None:
    """Função principal para executar o sistema de rotas."""
    try:
        nome_arquivo = os.path.basename(sys.argv[0])
        configurar_logging(nome_arquivo)
        
        gerenciador = GerenciadorRotas(driver, window)
        gerenciador.listar_todas_rotas()
        gerenciador.selecionar_origem_destino(interface_ativa)
        
        logging.info("Execução do sistema concluída com sucesso")
        
    except Exception as e:
        logging.error(f"Erro na execução do sistema: {e}")
        if window:
            window['-OUTPUT-'].update(f"ERRO CRÍTICO: {e}")
        raise


# Manter compatibilidade com código existente
def listarTodasRotas(driver, window, tempo_espera=30, verificar_valor_carga=True, verificar_bobina=True, verificar_multiplos_destinos=True):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    gerenciador.listar_todas_rotas(tempo_espera, verificar_valor_carga, verificar_bobina, verificar_multiplos_destinos)

def selecionarOrigemDestino(driver, window, interface):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    gerenciador.selecionar_origem_destino(interface)

def verificarSeExisteDestinoEFiltrar(driver, window):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    gerenciador.verificar_destinos_e_filtrar()

def vincularMotoristaNaRota(transporteSelecionado, destino, temLetraB, numeroDocumento, driver, data, valorCarga, tpTransporte, origem, obervacoes, pesoTotal, todosDestinos, maiorQueUmDestinos, prioridade, window):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    # Criar objeto rota para compatibilidade
    rota = DadosRota(
        numero_documento=numeroDocumento,
        data=data,
        compartilhado="",
        prioridade=prioridade,
        tipo_transporte=tpTransporte,
        peso_total=pesoTotal,
        unidade_peso="",
        planta_origem=origem,
        cluster=destino,
        estado="",
        observacoes=obervacoes,
        valor_carga=valorCarga,
        tem_letra_b=temLetraB,
        clientes_mesmo_destino=todosDestinos,
        mais_de_um_destino=maiorQueUmDestinos
    )
    gerenciador.processar_vinculacao_motorista2(rota, destino, transporteSelecionado)

def pegandoIdBotaoVincular(linhas, numeroDocumento):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(None, None)
    return gerenciador.obter_id_botao_vincular(linhas, numeroDocumento)

def saberUltimaRotaEnviouEmail(codigo):
    """Função de compatibilidade com código existente."""
    controle = ControleRotas()
    return controle.ja_enviou_email_destino_diferente(codigo)

def saberUltimaRotaEntrouVincular(codigo):
    """Função de compatibilidade com código existente."""
    controle = ControleRotas()
    return controle.ja_processou_rota(codigo)

def filtrar(driver):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, None)
    gerenciador.aplicar_filtro()

def verificarCadaResultadoRota(driver, window, destino):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    gerenciador.processar_resultados_rota(destino)

def ValidarSelect(driver, IdSelect, destino):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, None)
    return gerenciador.validar_opcao_select(IdSelect, destino)

# Funções de compatibilidade para controle de rotas
def limparRotasProcessadas():
    """Função de compatibilidade para limpar todas as rotas processadas."""
    controle = ControleRotas()
    controle.limpar_todas_rotas_processadas()
    return True

def adicionarRotaProcessada(numero_documento):
    """Função de compatibilidade para adicionar rota como processada."""
    controle = ControleRotas()
    controle.adicionar_rota_processada_manual(numero_documento)
    return True

def obterEstatisticasRotas():
    """Função de compatibilidade para obter estatísticas das rotas."""
    controle = ControleRotas()
    return controle.obter_estatisticas()

def configurarIntervaloLimpeza(minutos: int):
    """Função de compatibilidade para configurar intervalo de limpeza automática."""
    controle = ControleRotas()
    controle.configurar_intervalo_limpeza(minutos)
    return True

def obterProximaLimpeza():
    """Função de compatibilidade para obter quando será a próxima limpeza."""
    controle = ControleRotas()
    return controle.obter_proxima_limpeza()

def forcarLimpezaAgora():
    """Função de compatibilidade para forçar limpeza imediata das rotas."""
    controle = ControleRotas()
    controle.forcar_limpeza_agora()
    return True

gravarRotasRelatorio = db.gravarRotasRelatorio

