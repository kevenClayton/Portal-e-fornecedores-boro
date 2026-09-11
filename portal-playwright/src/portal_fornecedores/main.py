"""Portal E-Fornecedores v2 — interface por terminal (sem GUI).

No macOS o tkinter do Python do sistema costuma abrir janela vazia.
Por isso a execução padrão é via CLI.
"""

from __future__ import annotations

import argparse
import logging
import signal
import time
from pathlib import Path
from typing import Optional

from portal_fornecedores.browser.manager import BrowserManager
from portal_fornecedores.browser.pages.cargas_page import CargasPage
from portal_fornecedores.browser.pages.detalhes_carga_page import DetalhesCargaPage
from portal_fornecedores.browser.pages.login_page import LoginPage
from portal_fornecedores.browser.pages.vinculacao_page import VinculacaoPage
from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.repositories.dados_repository import DadosRepository
from portal_fornecedores.errors import CredencialPortalInvalida
from portal_fornecedores.models.entidades import ConfiguracaoBusca
from portal_fornecedores.services.acompanhamento_service import AcompanhamentoService
from portal_fornecedores.services.email_service import EmailService
from portal_fornecedores.services.proxy_rotation_service import ProxyRotationService
from portal_fornecedores.services.rota_service import RotaService
from portal_fornecedores.utils.logging_config import configurar_logging

logger = logging.getLogger(__name__)

MAX_FALHAS_CAPTCHA = 3


class PortalApp:
  def __init__(self, config: ConfiguracaoBusca):
    self._settings = get_settings()
    self._config = config
    self._config.robo_slot = max(1, min(3, int(self._settings.robo_slot or 1)))
    self._ativo = True
    self._aguardando_acao_manual = False
    self._rota_service: Optional[RotaService] = None
    self._browser: Optional[BrowserManager] = None
    self._acompanhamento = AcompanhamentoService(robo_slot=self._config.robo_slot)
    self._falhas_captcha = 0
    self._proxy_rotation = ProxyRotationService(
      api_token=self._settings.webshare_api_token,
      plan_id=self._settings.webshare_plan_id,
      arquivo_proxy=Path(f"/app/logs/proxy_atual_{self._config.robo_slot}.txt"),
      slot=self._config.robo_slot,
      cliente=self._settings.cliente,
    )
    # API Webshare é a fonte; PROXY/.env só entra se a API falhar
    proxy_resolvido = self._proxy_rotation.resolver_proxy_inicial(self._settings.proxy)
    if proxy_resolvido:
      self._settings.proxy = proxy_resolvido
      print(
        f"Proxy: {proxy_resolvido.split(':')[0]} "
        f"(cliente={self._settings.cliente}, slot={self._config.robo_slot}, fonte=Webshare API)",
        flush=True,
      )

  def _status(self, mensagem: str) -> None:
    texto = f"[R{self._config.robo_slot}] {mensagem}"
    print(texto, flush=True)
    logger.info(texto)
    forcar = mensagem.upper().startswith("ERRO") or "incorret" in mensagem.lower()
    try:
      self._acompanhamento.publicar(texto, forcar_screenshot=forcar)
    except Exception:
      pass

  def _iniciar_browser(self) -> RotaService:
    self._browser = BrowserManager(self._settings)
    page = self._browser.start()
    page.on("dialog", lambda dialog: dialog.accept())
    self._acompanhamento.definir_page(page)
    self._status("Chrome iniciado — acompanhando operação")

    return RotaService(
      login_page=LoginPage(page, self._settings),
      cargas_page=CargasPage(page, self._settings),
      detalhes_page=DetalhesCargaPage(page),
      vinculacao_page=VinculacaoPage(page),
      repository=DadosRepository(),
      email_service=EmailService(self._settings),
      on_status=self._status,
      on_heartbeat=self._heartbeat,
    )

  def _heartbeat(self) -> None:
    try:
      self._acompanhamento.verificar_e_capturar_pedido()
    except Exception:
      pass

  def _encerrar_browser(self) -> None:
    try:
      if self._browser:
        self._browser.stop()
    except Exception:
      pass
    self._browser = None
    self._rota_service = None
    self._acompanhamento.definir_page(None)

  def _aguardar_novo_start(self, motivo: str) -> None:
    """Para o ciclo e fica idle até o painel dar stop (SIGTERM). Evita restart loop do Docker."""
    self._aguardando_acao_manual = True
    self._status(motivo)
    self._encerrar_browser()
    try:
      self._acompanhamento.publicar(
        f"[R{self._config.robo_slot}] PARADO — corrija usuário/senha em Parâmetros e use Parar + Iniciar frota.",
        forcar_screenshot=True,
      )
    except Exception:
      pass
    while self._ativo:
      time.sleep(15)

  def _reiniciar_browser(self, espera_seg: int = 3) -> None:
    self._encerrar_browser()
    fim = time.time() + max(0, espera_seg)
    while self._ativo and time.time() < fim:
      self._heartbeat()
      time.sleep(min(2, max(0, fim - time.time())))
    if self._ativo and not self._aguardando_acao_manual:
      self._rota_service = self._iniciar_browser()

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
    print(f" Slot    : {self._config.robo_slot}", flush=True)
    print(f" Banco   : {self._settings.db_name} @ {self._settings.db_host}", flush=True)
    print(f" Cadência: {self._config.tempo_espera_seg}s (frota)", flush=True)
    print(f" Valor   : {self._config.verificar_valor_carga}", flush=True)
    print(f" Bobina  : {self._config.verificar_bobina}", flush=True)
    print(f" Destinos: {self._config.verificar_multiplos_destinos}", flush=True)
    print(" Ctrl+C para parar", flush=True)
    print("=" * 56, flush=True)

    try:
      self._rota_service = self._iniciar_browser()
      while self._ativo:
        if self._aguardando_acao_manual:
          time.sleep(15)
          continue
        try:
          self._rota_service.executar_ciclo(self._config)
          self._falhas_captcha = 0
        except CredencialPortalInvalida as erro:
          logger.exception("Credencial do portal invalida: %s", erro)
          self._aguardar_novo_start(
            f"ERRO: {erro}"
          )
        except Exception as erro:
          mensagem = str(erro)
          logger.exception("Erro no ciclo de automacao: %s", erro)
          self._status(f"ERRO: {erro}")

          if not self._ativo:
            break

          if "has been closed" in mensagem or "TargetClosedError" in mensagem or "Browser/página fechados" in mensagem:
            self._status("Chrome fechou. Reabrindo em 3s... (não feche a janela)")
            self._reiniciar_browser(espera_seg=3)
            continue

          if "captcha" in mensagem.lower():
            # Timeout de script ≠ rejeição do portal — não gasta rotação/parada por isso
            if "nao carregou" in mensagem.lower() or "não carregou" in mensagem.lower():
              self._status("reCAPTCHA indisponivel na pagina — repetindo ciclo em 8s...")
              time.sleep(8)
              continue

            captcha_na_pesquisa = "pesquisar cargas" in mensagem.lower() or "filtrar cluster" in mensagem.lower()

            # Após esgotar tentativas no Pesquisar, troca IP na hora (soft retry no IP queimado não ajuda)
            self._falhas_captcha += 1
            if self._falhas_captcha >= MAX_FALHAS_CAPTCHA:
              self._aguardar_novo_start(
                f"ERRO: Captcha falhou {self._falhas_captcha}x. "
                "Troque/reponha IPs ISP na Webshare e use Parar + Iniciar frota."
              )
              continue

            host_antes = (self._settings.proxy or "").split(":")[0] or "(nenhum)"
            novo_proxy = None
            try:
              novo_proxy = self._proxy_rotation.trocar_proxy(self._settings.proxy)
            except Exception as erro_rotacao:
              logger.warning("Falha ao rotacionar proxy: %s", erro_rotacao)

            if novo_proxy:
              self._settings.proxy = novo_proxy
              host_novo = novo_proxy.split(":")[0]
              espera = min(180, 45 * self._falhas_captcha)
              origem = "Pesquisar" if captcha_na_pesquisa else "Login"
              self._status(
                f"Captcha ({origem}) rejeitado no IP {host_antes}. "
                f"Trocando para {host_novo} e aguardando {espera}s "
                f"(tentativa {self._falhas_captcha}/{MAX_FALHAS_CAPTCHA})."
              )
            else:
              espera = min(900, 180 * self._falhas_captcha)
              self._status(
                f"Captcha rejeitado (tentativa {self._falhas_captcha}/{MAX_FALHAS_CAPTCHA}). "
                f"Sem IP novo — aguardando {espera // 60} min. Configure WEBSHARE_API_TOKEN."
              )
            self._reiniciar_browser(espera_seg=espera)
            continue

          time.sleep(5)
    finally:
      self._encerrar_browser()
      if not self._aguardando_acao_manual:
        try:
          self._acompanhamento.publicar("Robô encerrado", forcar_screenshot=False)
        except Exception:
          pass
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
  try:
    parametros = DadosRepository().obter_parametros()
    config.tempo_espera_seg = max(1, int(parametros.intervalo_espera_seg or config.tempo_espera_seg))
    config.verificar_valor_carga = bool(parametros.verificar_valor_carga)
    config.verificar_bobina = bool(parametros.verificar_bobina)
    config.verificar_multiplos_destinos = bool(parametros.verificar_multiplos_destinos)
  except Exception as erro:
    logger.warning("Nao foi possivel carregar parametros do banco no boot: %s", erro)

  app = PortalApp(config)
  app.executar()


if __name__ == "__main__":
  main()
