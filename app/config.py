from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://root:@localhost:3306/boro"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    # Portal credentials (serão carregadas do banco)
    portal_username: str = ""
    portal_password: str = ""
    portal_url: str = "https://portal.e-fornecedores.ind.br/"
    
    # Email settings
    smtp_server: str = "smtpi.uni5.net"
    smtp_port: int = 587
    smtp_username: str = "envio@keven.dev.br"
    smtp_password: str = "Secpol@2"
    
    # Selenium settings
    chrome_headless: bool = True
    selenium_timeout: int = 30
    selenium_implicit_wait: int = 10
    
    # Task settings
    task_interval_minutes: int = 5
    max_concurrent_tasks: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/portal_automation.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)
