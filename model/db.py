#PARA INSTALAR A BIBLIOTECA
# pip install mysql-connector-python
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from config import conexoes
from config import cliente

def DADOS():
	dados = {}

	try:
		#CONECTANDO COM O BANCO DE DADOS.
		db_connection = mysql.connector.connect \
		(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
		#SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
		cursor = db_connection.cursor()
		print("Database connection!")

		#BUSCANDO TABELAS
		destinos = ("SELECT * FROM destinos")
		motoristas = ("SELECT * FROM motoristas where situacao = 1 ORDER BY ordem_motorista")
		motorista_destino = ("SELECT motorista_id, nome_destino FROM motorista_destino md INNER JOIN destinos d ON md.destino_id = d.id INNER JOIN  motoristas m ON md.motorista_id = m.id where m.situacao = 1")
		motorista_origem = ("SELECT * FROM motorista_origem")
		origens = ("SELECT * FROM origens")
		parametros = ("SELECT * FROM parametros")
		motoristas_tipo_veiculo = ("SELECT motorista_id, nome_tipo_veiculo FROM motorista_tipo_veiculo mtv INNER JOIN tipo_veiculo tv ON mtv.tipo_veiculo_id = tv.id inner join motoristas m on m.id = mtv.motorista_id where m.situacao = 1")
		motoristas_tipo_veiculo_carreta = ("SELECT motorista_id, nome_tipo_veiculo FROM motorista_tipo_veiculo_carreta mtv INNER JOIN tipo_veiculo tv ON mtv.tipo_veiculo_id = tv.id inner join motoristas m on m.id = mtv.motorista_id where m.situacao = 1")
		tipo_veiculo = ("SELECT * FROM tipo_veiculo")
		login = ("SELECT * FROM login")
		select_destinos_motoristas_ativos = ("SELECT d.id, nome_destino  FROM destinos d INNER JOIN motorista_destino md ON   d.id  = md.destino_id INNER JOIN motoristas m on md.motorista_id = m.id where m.situacao = 1 group by destino_id")

		#ATRIBUINDO DADOS DA TABELA AO DICIONARIO DADOS
		cursor.execute(destinos)
		dados['destinos'] = cursor.fetchall()

		cursor.execute(select_destinos_motoristas_ativos)
		dados['select_destinos_motoristas_ativos'] = cursor.fetchall()

		cursor.execute(motoristas)
		dados['motoristas'] = cursor.fetchall()

		cursor.execute(motorista_destino)
		dados['motorista_destino'] = cursor.fetchall()

		cursor.execute(motorista_origem)
		dados['motorista_origem'] = cursor.fetchall()

		cursor.execute(origens)
		dados['origens'] = cursor.fetchall()

		cursor.execute(parametros)
		dados['parametros'] = cursor.fetchall()

		cursor.execute(motoristas_tipo_veiculo)
		dados['motoristas_tipo_veiculo'] = cursor.fetchall()
		cursor.execute(motoristas_tipo_veiculo_carreta)
		dados['motoristas_tipo_veiculo_carreta'] = cursor.fetchall()

		cursor.execute(tipo_veiculo)
		dados['tipo_veiculo'] = cursor.fetchall()

		cursor.execute(login)
		dados['login'] = cursor.fetchall()





		#Execultar  = "INSERT INTO `Teste` (`Nome`, `Email`)  VALUES ('Daywison', 'Daywison@daywison.com.br');"

		#cursor.execute("INSERT INTO `Teste` (`Nome`, `Email`)  VALUES ('Daywison', 'Daywison@daywison.com.br');")



	#EXIBE OS PROBLEMA CASO TENHA ERRO NO MYSQL
	except mysql.connector.Error as error:
		if error.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database doesn't exist")
		elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("User name or password is wrong")
		else:
			print(error)
	else:
		db_connection.close()

	return dados
def PARAMETROS():
	parametros = ""

	try:
		#CONECTANDO COM O BANCO DE DADOS.
		db_connection = mysql.connector.connect \
		(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
		#SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
		cursor = db_connection.cursor()
		print("Database connection!")

		#BUSCANDO TABELAS
		
		query = ("SELECT * FROM parametros")
		cursor.execute(query)
		parametros = cursor.fetchall()

	#EXIBE OS PROBLEMA CASO TENHA ERRO NO MYSQL
	except mysql.connector.Error as error:
		if error.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database doesn't exist")
		elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("User name or password is wrong")
		else:
			print(error)
	else:
		db_connection.close()

	return parametros


def dadosDBParaVincular(id, destino = ""):
	dadosDBParaVincular = {}
	try:
		#CONECTANDO COM O BANCO DE DADOS.
		db_connection = mysql.connector.connect \
		(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
		#SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
		cursor = db_connection.cursor()
		print("Database connection!")

		#BUSCANDO TABELAS
		motoristas = ("SELECT * FROM motoristas where situacao = 1")
		motorista_destino = ("SELECT * FROM motorista_destino md INNER JOIN destinos d ON md.destino_id = d.id WHERE d.nome_destino = "+ "'"+ destino.lower() + "'" + " and motorista_id = "+str(id)+"")
		motorista_origem = ("SELECT * FROM motorista_origem WHERE motorista_id = "+str(id)+"")
		motoristas_tipo_veiculo = ("SELECT * FROM motorista_tipo_veiculo mtv INNER JOIN tipo_veiculo tv ON mtv.tipo_veiculo_id = tv.id WHERE motorista_id = "+str(id)+"")

		#ATRIBUINDO DADOS DA TABELA AO DICIONARIO DADOS
		cursor.execute(motorista_destino)
		dadosDBParaVincular['motorista_destino'] = cursor.fetchall()

		cursor.execute(motorista_origem)
		dadosDBParaVincular['motorista_origem'] = cursor.fetchall()

		cursor.execute(motoristas_tipo_veiculo)
		dadosDBParaVincular['motoristas_tipo_veiculo'] = cursor.fetchall()



		#Execultar  = "INSERT INTO `Teste` (`Nome`, `Email`)  VALUES ('Daywison', 'Daywison@daywison.com.br');"

		#cursor.execute("INSERT INTO `Teste` (`Nome`, `Email`)  VALUES ('Daywison', 'Daywison@daywison.com.br');")



	#EXIBE OS PROBLEMA CASO TENHA ERRO NO MYSQL
	except mysql.connector.Error as error:
		if error.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database doesn't exist")
		elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("User name or password is wrong")
		else:
			print(error)
	else:
		db_connection.close()

	return dadosDBParaVincular

def motoristasDisponivelParaVinculacao(dadosRota, destino, tipoTransporte):
	dadosDBParaVincular = {}
	try:
		#CONECTANDO COM O BANCO DE DADOS.
		db_connection = mysql.connector.connect \
		(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
		#SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
		cursor = db_connection.cursor()
		print("Database connection!")

		if dadosRota.tem_letra_b:
			cond_bobina = "AND mt.aceita_bobina = 1"
		else:
			cond_bobina = ""

		query = f"""
        SELECT DISTINCT mt.*
        FROM motoristas mt
        INNER JOIN motorista_destino md ON mt.id = md.motorista_id
        INNER JOIN destinos dt ON md.destino_id = dt.id
        INNER JOIN motorista_tipo_veiculo mtp ON mtp.motorista_id = mt.id
        INNER JOIN tipo_veiculo tv ON tv.id = mtp.tipo_veiculo_id
        WHERE mt.situacao = TRUE
        {cond_bobina}
        AND LOWER(dt.nome_destino) = '{destino.lower()}'
        AND LOWER(tv.nome_tipo_veiculo) = '{tipoTransporte.lower()}'
        ORDER BY ordem_motorista
        """		
		cursor.execute(query)
		dadosDBParaVincular = cursor.fetchall()


	#EXIBE OS PROBLEMA CASO TENHA ERRO NO MYSQL
	except mysql.connector.Error as error:
		if error.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database doesn't exist")
		elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("User name or password is wrong")
		else:
			print(error)
	else:
		db_connection.close()

	return dadosDBParaVincular


def gravarRotas(origem, destino, doc_transporte, data_hora_chegada, valor_carga, motorista_rota, tipo_veiculo,situacao):
	# CONECTANDO COM O BANCO DE DADOS.
	db_connection = mysql.connector.connect \
			(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
	# SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
	cursor = db_connection.cursor()
	print("Database connection!")

	current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	INSERIR = (origem, destino, doc_transporte, data_hora_chegada, valor_carga, motorista_rota, tipo_veiculo, situacao, current_time, current_time)
	gravar = "INSERT INTO `rotas` (`origem_rota`, `destino_rota`,`doc_transporte`,`data_hora_chegada`,`valor_carga`,`motorista_rota`,`tipo_veiculo`,`situacao`, created_at, updated_at)  VALUES {};".format(INSERIR)

	cursor.execute(gravar)
	db_connection.commit()

def gravarRotasRelatorio(origem, destino, doc_transporte, data_hora_chegada, valor_carga, tipo_veiculo, pesoTotal, observacoesRota, prioridade, clientes, maisDeUmCliente, motivo):
	# CONECTANDO COM O BANCO DE DADOS.
	db_connection = mysql.connector.connect \
			(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
	# SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
	cursor = db_connection.cursor()
	print("Database connection!")

	cursor.execute("SELECT * FROM relatorios WHERE doc_transporte = %s", (doc_transporte,))
	relatorio_existente = cursor.fetchone()

	if relatorio_existente:
		print("Já existe uma rota com o código {}.".format(doc_transporte))
		return False


	cursor.execute("SELECT * FROM rotas WHERE doc_transporte = %s", (doc_transporte,))
	rota_existente = cursor.fetchone()


	if rota_existente:
		print("Já existe uma rota com o código {}.".format(doc_transporte))
		return False
	current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	INSERIR = (origem, destino, doc_transporte, data_hora_chegada, valor_carga, pesoTotal, tipo_veiculo, observacoesRota,	prioridade, clientes, maisDeUmCliente, current_time, current_time, motivo)
	gravar = "INSERT INTO relatorios (origem_rota, destino_rota, doc_transporte, data_hora_chegada, valor_carga, pesoTotal, tipo_veiculo, observacoesRota, prioridade, clientes, maisDeUmCliente, created_at, updated_at, motivo) VALUES {};".format(INSERIR)

	cursor.execute(gravar)
	db_connection.commit()
def atualizarSituacaoMotorista(idMotorista):
	# CONECTANDO COM O BANCO DE DADOS.
	db_connection = mysql.connector.connect \
			(
			host=conexoes[cliente]['host'],
			user=conexoes[cliente]['user'],
			password=conexoes[cliente]['password'],
			database=conexoes[cliente]['database']
		)
	# SETANDO VARIAVER PRINCIPAL DA BIBLIOTECA.
	cursor = db_connection.cursor()
	print("Conectando no banco")
	gravar = " UPDATE `motoristas` set `situacao` = 0, ordem_motorista = 10000 where id = "+str(idMotorista)+""

	cursor.execute(gravar)
	db_connection.commit()
