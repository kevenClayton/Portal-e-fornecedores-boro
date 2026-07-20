from functools import lru_cache
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from portal_fornecedores.utils.paths import caminho_env

try:
  from portal_fornecedores.config.embedded import EMBEDDED
except ImportError:
  EMBEDDED = {}


def _model_config() -> SettingsConfigDict:
  env_path = caminho_env()
  if env_path.exists():
    return SettingsConfigDict(
      env_file=str(env_path),
      env_file_encoding="utf-8",
      extra="ignore",
    )
  return SettingsConfigDict(extra="ignore")


class Settings(BaseSettings):
  model_config = _model_config()

  cliente: str = "madeforte"

  db_host: str = "localhost"
  db_port: int = 3306
  db_user: str = "portal_user"
  db_password: str = ""
  db_name: str = "portal_fornecedores"

  legacy_db_host: Optional[str] = None
  legacy_db_port: int = 3306
  legacy_db_user: Optional[str] = None
  legacy_db_password: Optional[str] = None
  legacy_db_name: Optional[str] = None

  portal_url: str = "https://portal.e-fornecedores.ind.br/"

  smtp_host: str = "smtpi.uni5.net"
  smtp_port: int = 587
  smtp_user: str = ""
  smtp_password: str = ""
  smtp_from: str = ""

  proxy: Optional[str] = Field(default=None, description="host:porta ou host:porta:user:pass")

  headless: bool = False
  slow_mo: int = 0
  usar_chrome_sistema: bool = True
  empresa_usiminas_id: str = "85"

  url_cargas: str = (
    "https://portal.e-fornecedores.ind.br/"
    "Default.aspx?cmp=SUCargaProgramada.ascx&tipo=vnc&menu=yes"
  )

  @property
  def db_config(self) -> dict:
    return {
      "host": self.db_host,
      "port": self.db_port,
      "user": self.db_user,
      "password": self.db_password,
      "database": self.db_name,
    }

  @property
  def legacy_db_config(self) -> Optional[dict]:
    if not self.legacy_db_host or not self.legacy_db_user or not self.legacy_db_name:
      return None
    return {
      "host": self.legacy_db_host,
      "port": self.legacy_db_port,
      "user": self.legacy_db_user,
      "password": self.legacy_db_password or "",
      "database": self.legacy_db_name,
    }


@lru_cache
def get_settings() -> Settings:
  base = Settings()
  if not EMBEDDED:
    return base
  dados = base.model_dump()
  dados.update(EMBEDDED)
  return Settings(**dados)
