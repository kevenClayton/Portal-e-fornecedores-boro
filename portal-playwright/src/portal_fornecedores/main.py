"""Portal E-Fornecedores v2 — interface por terminal (sem GUI).

No macOS o tkinter do Python do sistema costuma abrir janela vazia.
Por isso a execução padrão é via CLI.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from typing import Optional

from portal_fornecedores.browser.manager import BrowserManager
from portal_fornecedores.browser.pages.cargas_page import CargasPage
from portal_fornecedores.browser.pages.detalhes_carga_page import DetalhesCargaPage
from portal_fornecedores.browser.pages.login_page import LoginPage
from portal_fornecedores.browser.pages.vinculacao_page import VinculacaoPage
from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.repositories.dados_repository import DadosRepository
from portal_fornecedores.models.entidades import ConfiguracaoBusca
from portal_fornecedores.services.email_service import EmailService
from portal_fornecedores.services.rota_service import RotaService
from portal_fornecedores.utils.logging_config import configurar_logging

logger = logging.getLogger(__name__)


class PortalApp:
  def __init__(self, config: ConfiguracaoBusca):
    self._settings = get_settings()
    self._config = config
    self._ativo = True
    self._rota_service: Optional[RotaService] = None
    self._browser: Optional[BrowserManager] = None

  def _status(self, mensagem: str) -> None:
    print(mensagem, flush=True)
    logger.info(mensagem)

  def _iniciar_browser(self) -> RotaService:
    self._browser = BrowserManager(self._settings)
    page = self._browser.start()
    page.on("dialog", lambda dialog: dialog.accept())

    return RotaService(
      login_page=LoginPage(page, self._settings),
      cargas_page=CargasPage(page, self._settings),
      detalhes_page=DetalhesCargaPage(page),
      vinculacao_page=VinculacaoPage(page),
      repository=DadosRepository(),
      email_service=EmailService(self._settings),
      on_status=self._status,
    )

  def parar(self, *_args) -> None:
    print("\nParando... (Ctrl+C)", flush=True)
    self._ativo = False
    if self._rota_service:
      self._rota_service.parar()

  def executar(self) -> None:
    configurar_logging(self._settings.cliente)
    signal.signal(signal.SIGINT, self.parar)
    signal.signal(signal.SIGTERM, self.parar)

    print("=" * 56, flush=True)
    print(" Portal E-Fornecedores v2 - Playwright", flush=True)
    print(f" Cliente : {self._settings.cliente}", flush=True)
    print(f" Banco   : {self._settings.db_name} @ {self._settings.db_host}", flush=True)
    print(f" Espera  : {self._config.tempo_espera_seg}s", flush=True)
    print(f" Valor   : {self._config.verificar_valor_carga}", flush=True)
    print(f" Bobina  : {self._config.verificar_bobina}", flush=True)
    print(f" Destinos: {self._config.verificar_multiplos_destinos}", flush=True)
    print(" Ctrl+C para parar", flush=True)
    print("=" * 56, flush=True)

    try:
      self._rota_service = self._iniciar_browser()
      while self._ativo:
        try:
          self._rota_service.executar_ciclo(self._config)
        except Exception as erro:
          mensagem = str(erro)
          logger.exception("Erro no ciclo de automacao: %s", erro)
          self._status(f"ERRO: {erro}")

          if not self._ativo:
            break

          # Se o Chrome foi fechado, reabre e continua.
          if "has been closed" in mensagem or "TargetClosedError" in mensagem or "Browser/página fechados" in mensagem:
            self._status("Chrome fechou. Reabrindo em 3s... (não feche a janela)")
            try:
              if self._browser:
                self._browser.stop()
            except Exception:
              pass
            time.sleep(3)
            if self._ativo:
              self._rota_service = self._iniciar_browser()
            continue

          time.sleep(5)
    finally:
      if self._browser:
        self._browser.stop()
      print("Encerrado.", flush=True)


def _parse_args() -> ConfiguracaoBusca:
  parser = argparse.ArgumentParser(description="Portal E-Fornecedores v2")
  parser.add_argument(
    "--tempo-espera",
    type=int,
    default=30,
    help="Segundos entre ciclos (padrao: 30)",
  )
  parser.add_argument(
    "--sem-valor",
    action="store_true",
    help="Nao verificar valor da carga",
  )
  parser.add_argument(
    "--sem-bobina",
    action="store_true",
    help="Nao verificar bobina",
  )
  parser.add_argument(
    "--sem-destinos",
    action="store_true",
    help="Nao verificar multiplos destinos",
  )
  args = parser.parse_args()

  tempo = args.tempo_espera if args.tempo_espera >= 1 else 30
  return ConfiguracaoBusca(
    verificar_valor_carga=not args.sem_valor,
    verificar_bobina=not args.sem_bobina,
    verificar_multiplos_destinos=not args.sem_destinos,
    tempo_espera_seg=tempo,
  )


def main() -> None:
  config = _parse_args()
  app = PortalApp(config)
  app.executar()


if __name__ == "__main__":
  main()
