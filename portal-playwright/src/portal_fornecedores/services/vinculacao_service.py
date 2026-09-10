import logging
from typing import Callable, Optional, Set

from portal_fornecedores.browser.pages.cargas_page import CargasPage
from portal_fornecedores.browser.pages.detalhes_carga_page import DetalhesCargaPage
from portal_fornecedores.browser.pages.vinculacao_page import VinculacaoPage
from portal_fornecedores.config.settings import get_settings
from portal_fornecedores.database.repositories.dados_repository import DadosRepository
from portal_fornecedores.models.entidades import (
  DadosMotorista,
  DadosRota,
  ParametrosOperacao,
)
from portal_fornecedores.services.email_service import EmailService
from portal_fornecedores.services.whatsapp_service import WhatsAppService

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
    whatsapp_service: Optional[WhatsAppService] = None,
  ):
    self._cargas = cargas_page
    self._detalhes = detalhes_page
    self._vinculacao = vinculacao_page
    self._repo = repository
    self._email = email_service
    self._parametros = parametros
    self._whatsapp = whatsapp_service or WhatsAppService()
    self._on_status = on_status or (lambda msg: None)
    self._docs_notificados: Set[str] = set()

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
      self.registrar_incompativel(
        rota, destino, "Chapa excedente ao vincular", motorista=motorista
      )
      self._email.notificar_generico(
        self._parametros.email_notificacao,
        "Chapa excedente",
        f"Doc {rota.numero_documento} - Motorista: {motorista.nome}",
      )
      return False

    if "sucesso" in mensagem.lower():
      self._registrar_sucesso(motorista, rota, destino)
      return True

    self.registrar_incompativel(rota, destino, mensagem or "Erro ao vincular", motorista=motorista)
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
    self._notificar_whatsapp(
      situacao="aceita",
      rota=rota,
      destino=destino,
      motivo="",
      motorista=motorista,
    )

  def registrar_incompativel(
    self,
    rota: DadosRota,
    destino: str,
    motivo: str,
    motorista: Optional[DadosMotorista] = None,
  ) -> None:
    self._repo.gravar_relatorio(
      rota.planta_origem, destino, rota.numero_documento, rota.data,
      rota.valor_carga, rota.tipo_transporte, rota.peso_total,
      rota.observacoes, rota.prioridade, rota.clientes_mesmo_destino,
      rota.mais_de_um_destino, motivo,
    )
    self._notificar_whatsapp(
      situacao="perdida",
      rota=rota,
      destino=destino,
      motivo=motivo,
      motorista=motorista,
    )

  def _notificar_whatsapp(
    self,
    situacao: str,
    rota: DadosRota,
    destino: str,
    motivo: str = "",
    motorista: Optional[DadosMotorista] = None,
  ) -> None:
    chave = f"{situacao}:{rota.numero_documento}"
    if chave in self._docs_notificados:
      return
    self._docs_notificados.add(chave)

    nome_motorista = motorista.nome if motorista else ""
    placa = motorista.placa if motorista else ""
    cpf = motorista.cpf if motorista else ""

    try:
      public_id = self._repo.gravar_notificacao_carga(
        situacao=situacao,
        numero_documento=rota.numero_documento,
        motorista=nome_motorista,
        motivo=motivo,
        origem=rota.planta_origem,
        destino=destino or rota.cluster,
        valor_carga=str(rota.valor_carga or ""),
        tipo_transporte=rota.tipo_transporte,
        placa=placa,
        cpf=cpf,
      )
    except Exception as erro:
      logger.error("Falha ao gravar notificacao_carga: %s", erro)
      return

    settings = get_settings()
    base_url = (
      (self._parametros.painel_url_publica or "").rstrip("/")
      or (settings.painel_url_publica or "").rstrip("/")
    )
    if not base_url:
      logger.warning("WhatsApp: painel_url_publica vazio — sem link de detalhes")
      return

    url_detalhes = f"{base_url}/carga/{public_id}"
    telefones = self._whatsapp.telefones_validos(self._parametros.whatsapp_telefones)

    self._whatsapp.notificar_carga(
      telefones=telefones,
      situacao=situacao,
      motorista=nome_motorista or "-",
      numero_documento=rota.numero_documento,
      url_detalhes=url_detalhes,
      motivo=motivo,
      codigo_estabelecimento=self._parametros.whatsapp_codigo_estabelecimento or 9,
    )
    self._status(f"WhatsApp {situacao}: doc {rota.numero_documento} → {url_detalhes}")

  def _status(self, mensagem: str) -> None:
    logger.info(mensagem)
    self._on_status(mensagem)
