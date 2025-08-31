import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
    
    async def send_email_async(
        self,
        subject: str,
        message: str,
        to_emails: List[str],
        cc_emails: Optional[List[str]] = None
    ) -> bool:
        """Send email asynchronously"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(to_emails)
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email enviado com sucesso: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def send_email_sync(
        self,
        subject: str,
        message: str,
        to_emails: List[str],
        cc_emails: Optional[List[str]] = None
    ) -> bool:
        """Send email synchronously (for compatibility with existing code)"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(to_emails)
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            all_recipients = to_emails + (cc_emails or [])
            server.sendmail(self.smtp_username, all_recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Email enviado com sucesso: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    async def send_route_linked_email(self, motorista_data: dict, document_number: str) -> bool:
        """Send email when a route is successfully linked to a driver"""
        subject = "Carga marcada no portal - SU"
        message = f"""
        Número DOC: {document_number}
        
        Motorista: {motorista_data.get('nome', 'N/A')}
        CPF: {motorista_data.get('cpf', 'N/A')}
        Placa: {motorista_data.get('placa', 'N/A')}
        """
        
        # Get notification email from database or settings
        to_emails = [settings.smtp_username]  # Default fallback
        
        return await self.send_email_async(subject, message, to_emails)
    
    async def send_different_destination_email(self, document_number: str) -> bool:
        """Send email when route has different destinations"""
        subject = "Foi encontrada rota com cidades diferentes"
        message = f"Número DOC: {document_number}"
        
        to_emails = [settings.smtp_username]  # Default fallback
        
        return await self.send_email_async(subject, message, to_emails)
    
    async def send_generic_email(self, subject: str, text: str) -> bool:
        """Send generic email"""
        to_emails = [settings.smtp_username]  # Default fallback
        
        return await self.send_email_async(subject, text, to_emails)
