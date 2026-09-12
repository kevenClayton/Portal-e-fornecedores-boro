import logging
from typing import Tuple

from playwright.sync_api import Page

from portal_fornecedores.models.entidades import DadosMotorista
from portal_fornecedores.utils.modo_horario import intervalo_aleatorio_ms

logger = logging.getLogger(__name__)


class VinculacaoPage:
  SELECTOR_PLACA1 = "#ctlLoadedControl_txtPlaca1"
  SELECTOR_PLACA2 = "#ctlLoadedControl_txtPlaca2"
  SELECTOR_CPF = "#ctlLoadedControl_txtCPF"
  SELECTOR_BUSCAR_VEICULO = "#ctlLoadedControl_btnBuscarVeiculo"
  SELECTOR_BUSCAR_MOTORISTA = "#ctlLoadedControl_btnBuscarMotorista"
  SELECTOR_SALVAR = "#ctlLoadedControl_btnSalvar"
  SELECTOR_MENSAGEM = "#ctlLoadedControl_lblMessage"
  SELECTOR_OBS = "#ctlLoadedControl_txtObs"

  def __init__(self, page: Page):
    self._page = page

  def atualizar_page(self, page: Page) -> None:
    self._page = page

  def preencher_veiculo(self, motorista: DadosMotorista, tipo_transporte: str, tipos_carreta: list) -> None:
    self._page.locator(self.SELECTOR_PLACA1).fill(motorista.placa)

    if tipo_transporte in tipos_carreta and motorista.placa_carreta:
      self._page.locator(self.SELECTOR_PLACA2).fill(motorista.placa_carreta)

    self._page.locator(self.SELECTOR_BUSCAR_VEICULO).click()
    self._page.wait_for_timeout(intervalo_aleatorio_ms(500, 900))

  def preencher_motorista(self, motorista: DadosMotorista) -> None:
    self._page.locator(self.SELECTOR_CPF).fill(motorista.cpf)
    self._page.locator(self.SELECTOR_BUSCAR_MOTORISTA).click()
    self._page.wait_for_timeout(intervalo_aleatorio_ms(500, 900))

  def salvar(self) -> Tuple[str, str]:
    self._page.locator(self.SELECTOR_SALVAR).click()
    self._page.wait_for_timeout(intervalo_aleatorio_ms(2000, 3200))
    mensagem = self._page.locator(self.SELECTOR_MENSAGEM).inner_text()
    observacao = self._page.locator(self.SELECTOR_OBS).inner_text()
    return mensagem, observacao
