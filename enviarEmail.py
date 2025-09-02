import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import model.db as db


def enviarEmailRotaVinculada(motorista, numeroDocumento):
    """Envia email quando rota é vinculada com sucesso."""
    try:
        print(f"Enviando email de rota vinculada: {motorista}")
        msg = MIMEMultipart()
        
        mensagem = f"Numero DOC: {numeroDocumento}\n\n Motorista: {motorista[3]}\n\n CPF: {motorista[2]}\n\n Placa: {motorista[1]}"

        # Configurar cabeçalhos do email
        msg['Subject'] = "Carga marcada no portal - SU"
        msg['From'] = "envio@keven.dev.br"
        
        parametros = db.PARAMETROS()
        msg['To'] = parametros[0][5]
        msg['Cc'] = ""

        # Criar parte de texto com codificação UTF-8
        text_part = MIMEText(mensagem, 'plain', 'utf-8')
        msg.attach(text_part)

        # Configurar servidor SMTP
        server = smtplib.SMTP('smtpi.uni5.net', 587)
        server.ehlo()
        server.starttls()
        server.login("envio@keven.dev.br", 'Secpol@2')

        # Enviar email
        server.send_message(msg)
        server.quit()
        
        print("✅ Email de rota vinculada enviado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar email de rota vinculada: {e}")
        import logging
        logging.error(f"Erro ao enviar email de rota vinculada: {e}")

def enviarEmailRotaComDestinoDiferente(numeroDocumento):
    """Envia email quando rota tem destinos diferentes."""
    try:
        print(f"Enviando email de rota com destino diferente: {numeroDocumento}")
        msg = MIMEMultipart()
        
        mensagem = f"Numero DOC: {numeroDocumento}"

        # Configurar cabeçalhos do email
        msg['Subject'] = "Foi encontrada rota com cidades diferentes"
        msg['From'] = "envio@keven.dev.br"
        
        parametros = db.PARAMETROS()
        msg['To'] = parametros[0][5]
        msg['Cc'] = ""

        # Criar parte de texto com codificação UTF-8
        text_part = MIMEText(mensagem, 'plain', 'utf-8')
        msg.attach(text_part)

        # Configurar servidor SMTP
        server = smtplib.SMTP('smtpi.uni5.net', 587)
        server.ehlo()
        server.starttls()
        server.login("envio@keven.dev.br", 'Secpol@2')

        # Enviar email
        server.send_message(msg)
        server.quit()
        
        print("✅ Email de rota com destino diferente enviado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar email de rota com destino diferente: {e}")
        import logging
        logging.error(f"Erro ao enviar email de rota com destino diferente: {e}")

def enviarEmailGenerico(assunto = "", texto = ""):
    """Envia email genérico com tratamento de codificação UTF-8."""
    try:
        msg = MIMEMultipart()
        
        # Tratar codificação do texto
        if isinstance(texto, str):
            mensagem = texto
        else:
            mensagem = str(texto)

        # Configurar cabeçalhos do email
        msg['Subject'] = assunto
        msg['From'] = "envio@reservaai.com.br"
        
        parametros = db.PARAMETROS()
        msg['To'] = parametros[0][5]
        msg['Cc'] = ''

        # Criar parte de texto com codificação UTF-8
        text_part = MIMEText(mensagem, 'plain', 'utf-8')
        msg.attach(text_part)

        # Configurar servidor SMTP
        server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
        server.ehlo()
        server.starttls()
        server.login("AKIAWBJVNC74NXWWOF5G", 'BP2ANJyd6nwAlPHlJ8x+hRx3XvJF3N79rX0RTka0CbEQ')

        # Enviar email
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email enviado com sucesso: {assunto}")
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        # Log do erro para debug
        import logging
        logging.error(f"Erro ao enviar email - Assunto: {assunto}, Erro: {e}")

