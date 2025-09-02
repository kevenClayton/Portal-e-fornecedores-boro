"""
Módulo para lidar com autenticação de proxy no Selenium
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def handle_proxy_auth(driver, proxy_user, proxy_pass, timeout=10):
    """
    Lida automaticamente com a autenticação de proxy
    
    Args:
        driver: WebDriver do Selenium
        proxy_user: Usuário do proxy
        proxy_pass: Senha do proxy
        timeout: Tempo máximo de espera em segundos
    """
    try:
        print(f"🔐 Tentando autenticar proxy com usuário: {proxy_user}")
        
        # Aguardar até que o diálogo de autenticação apareça
        wait = WebDriverWait(driver, timeout)
        
        # Tentar diferentes seletores para o campo de usuário
        username_selectors = [
            "input[name='username']",
            "input[name='user']",
            "input[type='text']",
            "input[id*='user']",
            "input[id*='login']"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Campo de usuário encontrado com seletor: {selector}")
                break
            except TimeoutException:
                continue
        
        if not username_field:
            print("❌ Campo de usuário não encontrado")
            return False
        
        # Tentar diferentes seletores para o campo de senha
        password_selectors = [
            "input[name='password']",
            "input[name='pass']",
            "input[type='password']",
            "input[id*='pass']",
            "input[id*='pwd']"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Campo de senha encontrado com seletor: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not password_field:
            print("❌ Campo de senha não encontrado")
            return False
        
        # Preencher campos
        username_field.clear()
        username_field.send_keys(proxy_user)
        print("✅ Usuário preenchido")
        
        password_field.clear()
        password_field.send_keys(proxy_pass)
        print("✅ Senha preenchida")
        
        # Tentar encontrar e clicar no botão de login
        login_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "button:contains('Login')",
            "button:contains('Fazer login')",
            "input[value*='Login']",
            "input[value*='Entrar']"
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                if "contains" in selector:
                    # Para seletores com texto
                    login_button = driver.find_element(By.XPATH, f"//button[contains(text(), 'Login') or contains(text(), 'Fazer login') or contains(text(), 'Entrar')]")
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Botão de login encontrado com seletor: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if login_button:
            login_button.click()
            print("✅ Botão de login clicado")
            time.sleep(2)  # Aguardar processamento
            return True
        else:
            # Tentar pressionar Enter no campo de senha
            password_field.send_keys("\n")
            print("✅ Enter pressionado no campo de senha")
            time.sleep(2)
            return True
            
    except Exception as e:
        print(f"❌ Erro ao autenticar proxy: {e}")
        return False

def check_proxy_auth_dialog(driver):
    """
    Verifica se há um diálogo de autenticação de proxy ativo
    
    Args:
        driver: WebDriver do Selenium
    
    Returns:
        bool: True se há diálogo de autenticação, False caso contrário
    """
    try:
        # Verificar se há elementos típicos de diálogo de autenticação
        auth_indicators = [
            "input[name='username']",
            "input[name='password']",
            "input[type='password']",
            "//*[contains(text(), 'proxy')]",
            "//*[contains(text(), 'autenticação')]",
            "//*[contains(text(), 'login')]"
        ]
        
        for indicator in auth_indicators:
            try:
                if indicator.startswith("//"):
                    # XPath
                    element = driver.find_element(By.XPATH, indicator)
                else:
                    # CSS Selector
                    element = driver.find_element(By.CSS_SELECTOR, indicator)
                
                if element:
                    return True
            except NoSuchElementException:
                continue
        
        return False
        
    except Exception:
        return False

def auto_handle_proxy_auth(driver, proxy_user, proxy_pass, max_attempts=3):
    """
    Tenta lidar automaticamente com autenticação de proxy várias vezes
    
    Args:
        driver: WebDriver do Selenium
        proxy_user: Usuário do proxy
        proxy_pass: Senha do proxy
        max_attempts: Número máximo de tentativas
    
    Returns:
        bool: True se autenticado com sucesso, False caso contrário
    """
    for attempt in range(max_attempts):
        print(f"🔄 Tentativa {attempt + 1} de autenticação de proxy...")
        
        if check_proxy_auth_dialog(driver):
            if handle_proxy_auth(driver, proxy_user, proxy_pass):
                print("✅ Autenticação de proxy realizada com sucesso!")
                return True
            else:
                print(f"❌ Tentativa {attempt + 1} falhou")
                time.sleep(2)
        else:
            print("ℹ️  Nenhum diálogo de autenticação detectado")
            return True  # Se não há diálogo, considera sucesso
    
    print("❌ Todas as tentativas de autenticação falharam")
    return False
