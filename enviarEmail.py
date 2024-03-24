import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import model.db as db


def enviarEmailRotaVinculada(motorista, numeroDocumento):
    print(motorista)
    msg = MIMEMultipart()
    mensagem = "Numero DOC: "+ str(numeroDocumento) +"\n\n Motorista: "+motorista[3]+"\n\n CPF: "+motorista[2]+"\n\n Placa: "+motorista[1]+""

    msg['Assunto'] = "Carga marcada no portal - SU"
    msg["Mensagem"] = 'Subject: {}\n\n{}'.format(msg['Assunto'], mensagem)  # subject of your email
    msg['Mensagem'] = mensagem.encode('utf-8')
    #message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)


    server = smtplib.SMTP('smtp.uni5.net', 587)
    server.ehlo()
    server.starttls
    server.login("envio@maranatatecnologia.com.br", 'Secpol@2')
    parametros = db.PARAMETROS()

    msg["From"] = "envio@maranatatecnologia.com.br"
    msg["To"] =  parametros[0][5]
    msg["Cc"] = ""

    server.sendmail(msg["From"], msg["To"].split(","), msg['Mensagem'])

    server.quit()

def enviarEmailRotaComDestinoDiferente(numeroDocumento):
    print(numeroDocumento)
    msg = MIMEMultipart()
    mensagem = "Numero DOC: "+ str(numeroDocumento) +""

    msg['Assunto'] = "Foi encontrada rota com cidades diferentes"
    msg["Mensagem"] = 'Subject: {}\n\n{}'.format(msg['Assunto'], mensagem)  # subject of your email
    msg['Mensagem'] = mensagem.encode('utf-8')
    #message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)


    server = smtplib.SMTP('smtp.uni5.net', 587)
    server.ehlo()
    server.starttls
    server.login("envio@maranatatecnologia.com.br", 'Secpol@2')

    parametros = db.PARAMETROS()

    msg["From"] = "envio@maranatatecnologia.com.br"
    msg["To"] =  parametros[0][5]
    msg["Cc"] = ""

    server.sendmail(msg["From"], msg["To"].split(","), msg['Mensagem'])

    server.quit()

def enviarEmailGenerico(assunto = "", texto = ""):

    msg = MIMEMultipart()
    mensagem = texto

    msg['Assunto'] = assunto
    msg["Mensagem"] = 'Subject: {}\n\n{}'.format(msg['Assunto'], mensagem)  # subject of your email
    msg['Mensagem'] = mensagem.encode('utf-8')
    # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    server = smtplib.SMTP('smtp.uni5.net', 587)
    server.ehlo()
    server.starttls
    server.login("envio@maranatatecnologia.com.br", 'Secpol@2')

    parametros = db.PARAMETROS()

    msg["From"] = "envio@maranatatecnologia.com.br"
    msg["To"] =  parametros[0][5]
    msg["Cc"] = ""

    server.sendmail(msg["From"], msg["To"].split(","), msg['Mensagem'])

    server.quit()

