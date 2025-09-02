"""
Criação de extensão do Chrome para autenticação automática de proxy
"""

import os
import json
import zipfile
from pathlib import Path

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, extension_dir="proxy_auth_extension"):
    """
    Cria uma extensão do Chrome para autenticação automática de proxy
    
    Args:
        proxy_host: Host do proxy
        proxy_port: Porta do proxy
        proxy_user: Usuário do proxy
        proxy_pass: Senha do proxy
        extension_dir: Diretório para criar a extensão
    
    Returns:
        str: Caminho para o arquivo .crx da extensão
    """
    
    # Criar diretório da extensão
    extension_path = Path(extension_dir)
    extension_path.mkdir(exist_ok=True)
    
    # Manifesto da extensão
    manifest = {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Helper",
        "description": "Automatic proxy authentication",
        "permissions": [
            "proxy",
            "webRequest",
            "webRequestBlocking",
            "<all_urls>"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    
    # Script de background
    background_script = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: {proxy_port}
            }}
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """
    
    # Salvar arquivos
    with open(extension_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    with open(extension_path / "background.js", "w") as f:
        f.write(background_script)
    
    print(f"✅ Extensão de proxy criada em: {extension_path.absolute()}")
    return str(extension_path.absolute())

def setup_proxy_with_extension(driver_options, proxy_host, proxy_port, proxy_user, proxy_pass):
    """
    Configura proxy com extensão de autenticação
    
    Args:
        driver_options: ChromeOptions do Selenium
        proxy_host: Host do proxy
        proxy_port: Porta do proxy
        proxy_user: Usuário do proxy
        proxy_pass: Senha do proxy
    
    Returns:
        ChromeOptions: Opções configuradas
    """
    try:
        # Criar extensão
        extension_path = create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass)
        
        # Adicionar extensão ao Chrome
        driver_options.add_argument(f"--load-extension={extension_path}")
        
        print(f"✅ Extensão de proxy carregada: {extension_path}")
        return driver_options
        
    except Exception as e:
        print(f"❌ Erro ao criar extensão de proxy: {e}")
        return driver_options

def cleanup_proxy_extension(extension_dir="proxy_auth_extension"):
    """
    Remove arquivos da extensão de proxy
    
    Args:
        extension_dir: Diretório da extensão
    """
    try:
        import shutil
        extension_path = Path(extension_dir)
        if extension_path.exists():
            shutil.rmtree(extension_path)
            print(f"✅ Extensão de proxy removida: {extension_path}")
    except Exception as e:
        print(f"❌ Erro ao remover extensão: {e}")
