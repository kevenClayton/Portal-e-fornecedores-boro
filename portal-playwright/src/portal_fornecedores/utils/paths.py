"""Caminhos que funcionam tanto no Python quanto no .exe (PyInstaller)."""

from __future__ import annotations

import sys
from pathlib import Path


def diretorio_base() -> Path:
  """Pasta do .exe (frozen) ou pasta portal-playwright (dev)."""
  if getattr(sys, "frozen", False):
    return Path(sys.executable).resolve().parent
  return Path(__file__).resolve().parents[3]


def caminho_env() -> Path:
  return diretorio_base() / ".env"


def caminho_logs() -> Path:
  pasta = diretorio_base() / "logs"
  pasta.mkdir(exist_ok=True)
  return pasta
