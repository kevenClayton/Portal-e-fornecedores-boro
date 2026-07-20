#!/usr/bin/env python3
"""Gera config embutida para o .exe a partir de variaveis de ambiente / .env.

Uso (no build, antes do PyInstaller):
  python scripts/gerar_config_embutida.py
  python scripts/gerar_config_embutida.py --env-file .env.madeforte

Assim o cliente recebe SO o .exe, sem arquivo .env.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / "src" / "portal_fornecedores" / "config" / "embedded.py"

CAMPOS = [
  "CLIENTE",
  "DB_HOST",
  "DB_PORT",
  "DB_USER",
  "DB_PASSWORD",
  "DB_NAME",
  "PORTAL_URL",
  "SMTP_HOST",
  "SMTP_PORT",
  "SMTP_USER",
  "SMTP_PASSWORD",
  "SMTP_FROM",
  "PROXY",
  "HEADLESS",
  "SLOW_MO",
  "USAR_CHROME_SISTEMA",
  "EMPRESA_USIMINAS_ID",
]


def carregar_valores(env_file: Path | None) -> dict:
  valores = {}
  if env_file and env_file.exists():
    valores.update(
      {chave: valor for chave, valor in dotenv_values(env_file).items() if valor is not None}
    )
  elif env_file and not env_file.exists():
    print(f"Aviso: {env_file} nao encontrado — usando so variaveis de ambiente")

  import os

  for campo in CAMPOS:
    if os.getenv(campo):
      valores[campo] = os.environ[campo]
  return valores


def normalizar(valores: dict) -> dict:
  saida = {}
  mapa = {
    "CLIENTE": "cliente",
    "DB_HOST": "db_host",
    "DB_PORT": "db_port",
    "DB_USER": "db_user",
    "DB_PASSWORD": "db_password",
    "DB_NAME": "db_name",
    "PORTAL_URL": "portal_url",
    "SMTP_HOST": "smtp_host",
    "SMTP_PORT": "smtp_port",
    "SMTP_USER": "smtp_user",
    "SMTP_PASSWORD": "smtp_password",
    "SMTP_FROM": "smtp_from",
    "PROXY": "proxy",
    "HEADLESS": "headless",
    "SLOW_MO": "slow_mo",
    "USAR_CHROME_SISTEMA": "usar_chrome_sistema",
    "EMPRESA_USIMINAS_ID": "empresa_usiminas_id",
  }
  for origem, destino in mapa.items():
    if origem not in valores or valores[origem] in (None, ""):
      continue
    valor = valores[origem]
    if destino in ("db_port", "smtp_port", "slow_mo"):
      saida[destino] = int(valor)
    elif destino in ("headless", "usar_chrome_sistema"):
      saida[destino] = str(valor).strip().lower() in ("1", "true", "yes", "sim")
    else:
      saida[destino] = valor

  # Defaults seguros para cliente Windows
  saida.setdefault("usar_chrome_sistema", True)
  saida.setdefault("headless", False)
  return saida


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
  args = parser.parse_args()

  valores = normalizar(carregar_valores(args.env_file))
  obrigatorios = ["db_host", "db_user", "db_password", "db_name"]
  faltando = [campo for campo in obrigatorios if campo not in valores]
  if faltando:
    raise SystemExit(f"Faltam campos para embutir no exe: {', '.join(faltando)}")

  conteudo = (
    '"""Config embutida gerada automaticamente — nao editar a mao."""\n\n'
    f"EMBEDDED = {repr(valores)}\n"
  )
  DESTINO.write_text(conteudo, encoding="utf-8")
  print(f"Config embutida gerada em {DESTINO}")
  print(f"Cliente/banco: {valores.get('cliente')} / {valores.get('db_name')} @ {valores.get('db_host')}")


if __name__ == "__main__":
  main()
