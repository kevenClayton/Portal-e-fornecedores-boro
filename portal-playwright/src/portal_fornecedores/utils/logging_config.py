import logging
import sys
from datetime import datetime
from pathlib import Path

from portal_fornecedores.utils.paths import caminho_logs


def configurar_logging(nome_cliente: str = "portal") -> Path:
  logs_dir = caminho_logs()
  data_atual = datetime.now().strftime("%d-%m-%Y")
  arquivo_log = logs_dir / f"execucao-{nome_cliente}-{data_atual}.log"

  root = logging.getLogger()
  if root.handlers:
    for handler in list(root.handlers):
      root.removeHandler(handler)

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
      logging.FileHandler(arquivo_log, encoding="utf-8"),
      logging.StreamHandler(sys.stdout),
    ],
  )
  return arquivo_log
