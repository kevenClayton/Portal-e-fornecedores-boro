import logging
import smtplib
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from portal_fornecedores.config.settings import Settings, get_settings
from portal_fornecedores.models.entidades import DadosMotorista

logger = logging.getLogger(__name__)


class EmailService:
  def __init__(self, settings: Optional[Settings] = None):
    self._settings = settings or get_settings()

  def _enviar(self, destinatario: str, assunto: str, corpo: str) -> None:
    if not destinatario or not self._settings.smtp_user:
      logger.warning("Email não configurado — ignorando envio: %s", assunto)
      return

    mensagem = MIMEMultipart()
    mensagem["Subject"] = assunto
    mensagem["From"] = self._settings.smtp_from or self._settings.smtp_user
    mensagem["To"] = destinatario
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
      with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.login(self._settings.smtp_user, self._settings.smtp_password)
        servidor.send_message(mensagem)
      logger.info("Email enviado: %s", assunto)
    except Exception as erro:
      logger.error("Falha ao enviar email '%s': %s", assunto, erro)

  def notificar_rota_vinculada(
    self,
    destinatario: str,
    motorista: DadosMotorista,
    numero_documento: str,
  ) -> None:
    corpo = (
      f"Numero DOC: {numero_documento}\n\n"
      f"Motorista: {motorista.nome}\n\n"
      f"CPF: {motorista.cpf}\n\n"
      f"Placa: {motorista.placa}"
    )
    self._enviar(destinatario, "Carga marcada no portal - SU", corpo)

  def notificar_generico(self, destinatario: str, assunto: str, texto: str) -> None:
    self._enviar(destinatario, assunto, texto)
