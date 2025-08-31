import time
import logging
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from unidecode import unidecode

from app.config import settings
from app.services.email_service import EmailService
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class PortalService:
    def __init__(self):
        self.driver = None
        self.email_service = EmailService()
        self.db_service = DatabaseService()
        self.wait_timeout = settings.selenium_timeout
        
    def configurar_driver(self) -> webdriver.Chrome:
        """Configurar e retornar Chrome WebDriver"""
        chrome_options = Options()
        
        if settings.chrome_headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Adicionar proxy se configurado
        if hasattr(settings, 'proxy_server') and settings.proxy_server:
            chrome_options.add_argument(f'--proxy-server={settings.proxy_server}')
        
        # Usar webdriver-manager para obter a versão correta do ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(settings.selenium_implicit_wait)
        self.driver.set_page_load_timeout(self.wait_timeout)
        
        return self.driver
    
    def login(self) -> bool:
        """Fazer login no portal usando credenciais do banco"""
        try:
            logger.info("Iniciando login no portal")
            
            # Obter credenciais do banco
            credenciais = self.db_service.obter_credenciais_portal()
            if not credenciais:
                logger.error("Credenciais não encontradas no banco de dados")
                return False
            
            usuario = credenciais.get("usuario")
            senha = credenciais.get("senha")
            
            if not usuario or not senha:
                logger.error("Usuário ou senha não encontrados no banco")
                return False
            
            self.driver.get(settings.portal_url)
            
            # Aguardar formulário de login
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctlLoadedControl_txtLogin"))
            )
            
            # Preencher formulário
            username_field.click()
            username_field.send_keys(usuario)
            
            password_field = self.driver.find_element(By.ID, "ctlLoadedControl_txtSenha")
            password_field.click()
            password_field.send_keys(senha)
            
            # Enviar formulário
            login_button = self.driver.find_element(By.ID, "ctlLoadedControl_btnOK")
            login_button.click()
            
            # Aguardar login completar
            time.sleep(3)
            
            # Verificar se login foi bem-sucedido
            if self.esta_logado():
                logger.info("Login realizado com sucesso")
                return True
            else:
                logger.error("Falha no login")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante login: {str(e)}")
            return False
    
    def esta_logado(self) -> bool:
        """Verificar se o usuário está logado"""
        try:
            current_url = self.driver.current_url
            if current_url == "data:,":
                return False
            
            # Check if we're on an error page
            if "cmp=Error.ascx" in current_url:
                return False
            
            # Check if we have any parameters in URL (indicates logged in)
            if "?" in current_url and "cmp=" in current_url:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar login: {str(e)}")
            return False
    
    def navegar_para_pagina_rotas(self) -> bool:
        """Navegar para a página de rotas"""
        try:
            logger.info("Navegando para página de rotas")
            
            # Selecionar empresa
            company_select = self.driver.find_element(By.ID, "mnuPrincipal_lstEmpresas")
            company_select.click()
            time.sleep(0.2)
            
            # Selecionar empresa com valor 85 (Soluções Usiminas)
            company_select.send_keys("85")
            time.sleep(0.2)
            
            select = Select(company_select)
            select.select_by_value("85")
            time.sleep(0.2)
            
            # Navegar para página de rotas
            routes_url = "https://portal.e-fornecedores.ind.br/Default.aspx?cmp=SUCargaProgramada.ascx&tipo=vnc&menu=yes"
            self.driver.get(routes_url)
            time.sleep(0.2)
            
            # Clicar no botão de pesquisa
            search_button = self.driver.find_element(By.ID, "ctlLoadedControl_btnPesquisa")
            search_button.click()
            time.sleep(1)
            
            logger.info("Navegação para página de rotas concluída")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao navegar para página de rotas: {str(e)}")
            return False
    
    def obter_destinos_disponiveis(self) -> List[str]:
        """Obter lista de destinos disponíveis no portal"""
        try:
            destination_select = self.driver.find_element(By.ID, "ctlLoadedControl_ddlCluster")
            options = destination_select.text.split('\n')
            return [opt.strip() for opt in options if opt.strip()]
        except Exception as e:
            logger.error(f"Erro ao obter destinos disponíveis: {str(e)}")
            return []
    
    def filtrar_por_destino(self, destino: str) -> bool:
        """Filtrar rotas por destino"""
        try:
            destination_select = Select(self.driver.find_element(By.ID, "ctlLoadedControl_ddlCluster"))
            destination_select.select_by_value(destino)
            time.sleep(1)
            
            # Clicar no botão de filtrar
            filter_button = self.driver.find_element(By.ID, "ctlLoadedControl_btnFiltrar")
            filter_button.click()
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao filtrar por destino {destino}: {str(e)}")
            return False
    
    def obter_tabela_rotas(self) -> List[Dict]:
        """Extrair rotas da tabela"""
        try:
            # Aguardar tabela carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctlLoadedControl_dgRight"))
            )
            
            # Obter HTML da tabela
            table_element = self.driver.find_element(By.ID, "ctlLoadedControl_dgRight")
            html_content = table_element.get_attribute('outerHTML')
            
            # Fazer parse com BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            table = soup.find('table')
            
            if not table:
                return []
            
            # Converter para pandas DataFrame
            df = pd.read_html(str(table), skiprows=1)[0]
            routes_data = df.to_dict('split')['data']
            
            # Converter para lista de dicionários
            routes = []
            for route in routes_data:
                if len(route) >= 13:  # Garantir que temos colunas suficientes
                    routes.append({
                        'numero_documento': route[0],
                        'data': route[3],
                        'compartilhado': route[4],
                        'prioridade': route[5],
                        'tipo_transporte': route[7],
                        'peso_total': route[8],
                        'unidade_peso': route[9],
                        'planta_origem': route[10],
                        'cluster': route[11],
                        'estado': route[12]
                    })
            
            return routes
            
        except Exception as e:
            logger.error(f"Erro ao extrair tabela de rotas: {str(e)}")
            return []
    
    def obter_detalhes_rota(self, numero_documento: str) -> Dict:
        """Obter informações detalhadas de uma rota específica"""
        try:
            # Encontrar e clicar no botão de vincular para esta rota
            button_id = self._obter_id_botao_vincular(numero_documento)
            if not button_id:
                return {}
            
            # Clicar no botão para abrir detalhes da rota
            vincular_button = self.driver.find_element(By.ID, button_id)
            vincular_button.click()
            time.sleep(1)
            
            # Extrair observações e outros detalhes
            observations = self._obter_observacoes_rota()
            valor_carga = self._obter_valor_carga()
            has_letter_b = self._verificar_tem_letra_b()
            multiple_destinations = self._verificar_multiplos_destinos()
            
            # Voltar para lista de rotas
            self.driver.back()
            time.sleep(1)
            
            return {
                'observations': observations,
                'valor_carga': valor_carga,
                'has_letter_b': has_letter_b,
                'multiple_destinations': multiple_destinations
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da rota {numero_documento}: {str(e)}")
            return {}
    
    def _obter_id_botao_vincular(self, document_number: str) -> Optional[str]:
        """Obter o ID do botão vincular para um documento específico"""
        try:
            table_element = self.driver.find_element(By.ID, "ctlLoadedControl_dgRight")
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            
            for row in rows[1:]:  # Pular linha do cabeçalho
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    doc_cell = cells[0].text.strip()
                    if doc_cell == str(document_number):
                        button = cells[2].find_element(By.TAG_NAME, "input")
                        return button.get_attribute('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter ID do botão vincular: {str(e)}")
            return None
    
    def _obter_observacoes_rota(self) -> str:
        """Obter observações da rota da página de detalhes"""
        try:
            obs_element = self.driver.find_element(By.ID, "ctlLoadedControl_txtObs")
            return obs_element.text
        except:
            return ""
    
    def _obter_valor_carga(self) -> str:
        """Obter valor da carga das observações"""
        try:
            obs_element = self.driver.find_element(By.ID, "ctlLoadedControl_txtObs")
            obs_text = obs_element.text
            # Extrair valor das observações (implementar baseado na lógica original)
            # Esta é uma versão simplificada - você pode precisar adaptar a lógica original
            return obs_text.split(',')[0] if ',' in obs_text else obs_text
        except:
            return ""
    
    def _verificar_tem_letra_b(self) -> bool:
        """Verificar se a rota tem letra B nas observações"""
        try:
            obs_element = self.driver.find_element(By.ID, "ctlLoadedControl_txtObs")
            obs_text = obs_element.text.lower()
            return 'b' in obs_text
        except:
            return False
    
    def _verificar_multiplos_destinos(self) -> Tuple[bool, List[str], int]:
        """Verificar se a rota tem múltiplos destinos"""
        try:
            # Isso precisaria ser implementado baseado na lógica original
            # Por enquanto, retornando valores padrão
            return False, [], 0
        except:
            return False, [], 0
    
    def fechar_driver(self):
        """Fechar o WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
