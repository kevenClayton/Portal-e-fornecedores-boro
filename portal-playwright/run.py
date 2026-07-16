#!/usr/bin/env python3
"""Ponto de entrada do Portal E-Fornecedores v2."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
  sys.path.insert(0, str(SRC))

from portal_fornecedores.main import main

if __name__ == "__main__":
  main()
