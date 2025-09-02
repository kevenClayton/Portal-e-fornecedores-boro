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
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

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

class ControleRotas:
    """Classe para controle de rotas já processadas."""
    
    def __init__(self):
        self.rotas_processadas = set()
        self.ultima_rota_email = None
        self.ultima_rota_vincular = None
    
    def ja_processou_rota(self, numero_documento: str) -> bool:
        """Verifica se a rota já foi processada."""
        return numero_documento in self.rotas_processadas
    
    def marcar_rota_processada(self, numero_documento: str) -> None:
        """Marca uma rota como processada."""
        self.rotas_processadas.add(numero_documento)
        self.ultima_rota_vincular = numero_documento
    
    def ja_enviou_email_destino_diferente(self, numero_documento: str) -> bool:
        """Verifica se já foi enviado email para rota com destino diferente."""
        if numero_documento == self.ultima_rota_email:
            return True
        else:
            self.ultima_rota_email = numero_documento
            return False

class GerenciadorRotas:
    """Classe principal para gerenciamento de rotas e vinculação de motoristas."""
    
    def __init__(self, driver: WebDriver, window=None):
        self.driver = driver
        self.window = window
        self.dados = None
        self.controle_rotas = ControleRotas()
        self.carregar_dados()
        
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
    
    def listar_todas_rotas(self) -> None:
        """Navega para a página de listagem de rotas e configura filtros iniciais."""
        try:
            self.atualizar_interface('BUSCANDO TODAS AS ROTAS...')
            
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
            
            for destino in opcoes:
                destino_limpo = destino.strip()
                if destino_limpo in array_destinos:
                    status = f"Verificando cluster existente: {destino_limpo}"
                    self.atualizar_interface(status)
                    
                    select = Select(self.driver.find_element('id', id_select_cluster))
                    select.select_by_value(destino_limpo)
                    time.sleep(1)
                    
                    self.aplicar_filtro()
                    self.processar_resultados_rota(destino_limpo)
                    return
                else:
                    status = f"Cluster não existente na base: {destino_limpo}"
                    self.atualizar_interface(status)
                    
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
                rota = self.criar_objeto_rota(rota_dados)
                
                if self.controle_rotas.ja_processou_rota(rota.numero_documento):
                    logging.info(f"Rota já processada: {rota.numero_documento}")
                    continue
                
                self.processar_rota_individual(rota, destino)
                
        except Exception as e:
            logging.error(f"Erro ao processar resultados: {e}")
            raise
    
    def criar_objeto_rota(self, dados_rota: List) -> DadosRota:
        """Cria objeto DadosRota a partir dos dados da tabela."""
        try:
            rota = DadosRota(
                numero_documento=dados_rota[0],
                data=dados_rota[3],
                compartilhado=dados_rota[4],
                prioridade=dados_rota[5],
                tipo_transporte=dados_rota[7],
                peso_total=dados_rota[8],
                unidade_peso=dados_rota[9],
                planta_origem=dados_rota[10],
                cluster=dados_rota[11],
                estado=dados_rota[12]
            )
            
            # Obter dados adicionais
            time.sleep(1)
            rota.observacoes = validarLetraProduto.pegarObservacoesRota(self.driver, rota.numero_documento)
            rota.valor_carga = pegarValorObservacao.tratarValorNoCampoObservacao(self.driver, rota.numero_documento).strip().split(',')[0]
            rota.tem_letra_b = validarLetraProduto.verificarTemLetraB(self.driver, rota.numero_documento)
            
            dados_destinos = validarLetraProduto.verificarMultiplosDestinos(self.driver, rota.numero_documento)
            rota.clientes_mesmo_destino = dados_destinos[1]
            rota.mais_de_um_destino = dados_destinos[2] > 1
            
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
            
            # Obter ID do botão vincular
            html_prod = self.driver.page_source
            soup = BeautifulSoup(html_prod, 'lxml')
            tabela = soup.find('table', id='ctlLoadedControl_dgRight')
            linhas = tabela.findChildren('tr')
            
            id_botao_vincular = self.obter_id_botao_vincular(linhas, rota.numero_documento)
            
            if not id_botao_vincular:
                logging.error(f"Botão vincular não encontrado para documento: {rota.numero_documento}")
                return
            
            # Clicar no botão vincular
            self.driver.find_element("id", id_botao_vincular).click()
            logging.info(f'Clicou no botão vincular para rota: {rota.numero_documento}')
            
            # Processar vinculação
            self.processar_vinculacao_motorista(rota, destino, tipo_transporte)
            
            time.sleep(0.2)
            self.driver.back()
            
        except Exception as e:
            logging.error(f"Erro ao tentar vincular motorista: {e}")
            raise
    
    def obter_id_botao_vincular(self, linhas, numero_documento: str) -> str:
        """Obtém o ID do botão vincular para um documento específico."""
        try:
            for i, linha in enumerate(linhas):
                if i == 0:  # Pular cabeçalho
                    continue
                    
                celulas = linha.findChildren('td')
                if len(celulas) >= 3:
                    numero_documento_linha = celulas[0].text.strip()
                    if str(numero_documento) == numero_documento_linha:
                        inputs = celulas[2].findChildren('input')
                        if inputs:
                            return inputs[0].get('id')
            
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
    
    def validar_compatibilidade_motorista(self, motorista: DadosMotorista, rota: DadosRota, 
                                        destino: str, tipo_transporte: str) -> bool:
        """Valida se o motorista é compatível com a rota."""
        try:
            # Verificar destino
            array_motorista_destinos = np.array(self.dados['motorista_destino'])
            array_motorista_origens = np.array(self.dados['origens'])
            
            origem_upper = rota.planta_origem.upper()
            
            if destino not in array_motorista_destinos or origem_upper not in array_motorista_origens:
                return False
            
            # Verificar se motorista atende ao destino
            destinos_motorista = np.where(array_motorista_destinos == destino)[0]
            
            for idx in destinos_motorista:
                if int(array_motorista_destinos[idx][0]) == motorista.id_banco:
                    destino_motorista = array_motorista_destinos[idx][1].lower()
                    if destino.lower() == destino_motorista:
                        # Verificar tipo de veículo
                        for motorista_tipo_veiculo in self.dados['motoristas_tipo_veiculo']:
                            if (motorista_tipo_veiculo[0] == motorista.id_banco and 
                                motorista_tipo_veiculo[1].lower() == tipo_transporte.lower()):
                                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao validar compatibilidade do motorista: {e}")
            return False
    
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
            self.driver.back()
            status = f'Modo teste: Não vinculou documento {rota.numero_documento}'
            logging.info(status)
            self.atualizar_interface(f'Era para vincular, mas está no modo teste. NÃO VINCULADO!')
            enviarEmail.enviarEmailGenerico("Modo teste habilitado", status)
            return False
            
        except Exception as e:
            logging.error(f"Erro na vinculação teste: {e}")
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
        gravarRotas(rota.planta_origem, destino, rota.numero_documento, rota.data, 
                   rota.valor_carga, motorista.nome, rota.tipo_transporte, motorista.situacao)
        
        # Atualizar situação do motorista
        atualizarSituacaoMotorista(motorista.id_banco)
        
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
            gravarRotasRelatorio(
                rota.planta_origem, destino, rota.numero_documento, rota.data,
                rota.valor_carga, rota.tipo_transporte, rota.peso_total, rota.observacoes,
                rota.prioridade, rota.clientes_mesmo_destino, rota.mais_de_um_destino, motivo
            )
        except Exception as e:
            logging.error(f"Erro ao registrar rota incompatível: {e}")


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


# Funções de compatibilidade com código existente
def listarTodasRotas(driver, window):
    """Função de compatibilidade com código existente."""
    gerenciador = GerenciadorRotas(driver, window)
    gerenciador.listar_todas_rotas()

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
    gerenciador.processar_vinculacao_motorista(rota, destino, transporteSelecionado)

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

# Variáveis globais para compatibilidade
gravarRotas = db.gravarRotas
gravarRotasRelatorio = db.gravarRotasRelatorio
atualizarSituacaoMotorista = db.atualizarSituacaoMotorista

# Variáveis de controle globais (mantidas para compatibilidade)
ehMesmoDestinoCodigo = 0
ehMesmoDestinoCodigoVincular = 0
