import logging
from typing import Callable, Optional

from portal_fornecedores.browser.pages.cargas_page import CargasPage
from portal_fornecedores.browser.pages.detalhes_carga_page import DetalhesCargaPage
from portal_fornecedores.browser.pages.vinculacao_page import VinculacaoPage
from portal_fornecedores.database.repositories.dados_repository import DadosRepository
from portal_fornecedores.models.entidades import (
  ConfiguracaoBusca,
  DadosMotorista,
  DadosRota,
  ParametrosOperacao,
)
from portal_fornecedores.services.email_service import EmailService

logger = logging.getLogger(__name__)


class VinculacaoService:
  def __init__(
    self,
    cargas_page: CargasPage,
    detalhes_page: DetalhesCargaPage,
    vinculacao_page: VinculacaoPage,
    repository: DadosRepository,
    email_service: EmailService,
    parametros: ParametrosOperacao,
    on_status: Optional[Callable[[str], None]] = None,
  ):
    self._cargas = cargas_page
    self._detalhes = detalhes_page
    self._vinculacao = vinculacao_page
    self._repo = repository
    self._email = email_service
    self._parametros = parametros
    self._on_status = on_status or (lambda msg: None)

  def tentar_vincular(
    self,
    rota: DadosRota,
    destino: str,
    tipo_transporte: str,
  ) -> bool:
    self._status(f"Parâmetros OK: {tipo_transporte} - {rota.valor_carga}")

    if not self._cargas.clicar_vincular(rota.numero_documento):
      return False

    self._repo.marcar_documento_processado(rota.numero_documento)
    motoristas = self._repo.motoristas_disponiveis(rota, destino, tipo_transporte)

    if not motoristas:
      self.registrar_incompativel(rota, destino, "Não tem motorista para rota")
      self._cargas.voltar()
      return False

    for motorista in motoristas:
      if self._vincular_motorista(motorista, rota, destino, tipo_transporte):
        self._cargas.voltar()
        return True

    self.registrar_incompativel(rota, destino, "Não tem motorista para rota")
    self._cargas.voltar()
    return False

  def _vincular_motorista(
    self,
    motorista: DadosMotorista,
    rota: DadosRota,
    destino: str,
    tipo_transporte: str,
  ) -> bool:
    self._status(
      f"Motorista compatível: {motorista.nome} - Placa: {motorista.placa} - CPF: {motorista.cpf}"
    )

    tipos_carreta = self._repo.obter_tipos_veiculo_carreta_motorista(motorista.id_banco)
    self._vinculacao.preencher_veiculo(motorista, tipo_transporte, tipos_carreta)
    self._vinculacao.preencher_motorista(motorista)

    if not self._repo.validar_motorista_destino(motorista.id_banco, destino):
      status = f"Motorista não passou na validação final: {motorista.nome}"
      logger.warning(status)
      self._email.notificar_generico(
        self._parametros.email_notificacao,
        "Motorista não passou na validação final",
        status,
      )
      return False

    if self._parametros.modo_teste:
      self._status(f"Modo teste: não vinculou documento {rota.numero_documento}")
      self._email.notificar_generico(
        self._parametros.email_notificacao,
        "Modo teste habilitado",
        f"Era para vincular doc {rota.numero_documento}, mas está em modo teste.",
      )
      return False

    mensagem, observacao = self._vinculacao.salvar()

    if "CHAPA EXCEDENTE" in observacao:
      self.registrar_incompativel(rota, destino, "Chapa excedente ao vincular")
      self._email.notificar_generico(
        self._parametros.email_notificacao,
        "Chapa excedente",
        f"Doc {rota.numero_documento} - Motorista: {motorista.nome}",
      )
      return False

    if "sucesso" in mensagem.lower():
      self._registrar_sucesso(motorista, rota, destino)
      return True

    self.registrar_incompativel(rota, destino, mensagem)
    self._email.notificar_generico(
      self._parametros.email_notificacao,
      "Erro ao tentar vincular",
      f"{mensagem} - Doc: {rota.numero_documento} - Motorista: {motorista.nome}",
    )
    return False

  def _registrar_sucesso(self, motorista: DadosMotorista, rota: DadosRota, destino: str) -> None:
    logger.info("Vinculação OK: %s - Doc: %s", motorista.nome, rota.numero_documento)
    self._repo.gravar_rota_vinculada(
      rota.planta_origem, destino, rota.numero_documento,
      rota.data, rota.valor_carga, motorista.nome, rota.tipo_transporte,
    )
    self._repo.desativar_motorista(motorista.id_banco)
    self._email.notificar_rota_vinculada(
      self._parametros.email_notificacao, motorista, rota.numero_documento,
    )

  def registrar_incompativel(self, rota: DadosRota, destino: str, motivo: str) -> None:
    self._repo.gravar_relatorio(
      rota.planta_origem, destino, rota.numero_documento, rota.data,
      rota.valor_carga, rota.tipo_transporte, rota.peso_total,
      rota.observacoes, rota.prioridade, rota.clientes_mesmo_destino,
      rota.mais_de_um_destino, motivo,
    )

  def _status(self, mensagem: str) -> None:
    logger.info(mensagem)
    self._on_status(mensagem)
