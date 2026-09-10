import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from portal_fornecedores.utils.paths import caminho_logs

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


class FormatterBrasil(logging.Formatter):
  def formatTime(self, record, datefmt=None):
    momento = datetime.fromtimestamp(record.created, tz=FUSO_BRASIL)
    if datefmt:
      return momento.strftime(datefmt)
    return momento.strftime("%Y-%m-%d %H:%M:%S")


def configurar_logging(nome_cliente: str = "portal") -> Path:
  # Garante timezone do processo (Docker costuma ficar em UTC)
  os.environ.setdefault("TZ", "America/Sao_Paulo")
  try:
    time.tzset()
  except AttributeError:
    pass

  logs_dir = caminho_logs()
  data_atual = datetime.now(FUSO_BRASIL).strftime("%d-%m-%Y")
  arquivo_log = logs_dir / f"execucao-{nome_cliente}-{data_atual}.log"

  root = logging.getLogger()
  if root.handlers:
    for handler in list(root.handlers):
      root.removeHandler(handler)

  formatter = FormatterBrasil("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
  handlers = [
    logging.FileHandler(arquivo_log, encoding="utf-8"),
    logging.StreamHandler(sys.stdout),
  ]
  for handler in handlers:
    handler.setFormatter(formatter)
    root.addHandler(handler)
  root.setLevel(logging.INFO)

  return arquivo_log
