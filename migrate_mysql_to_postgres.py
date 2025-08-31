#!/usr/bin/env python3
"""
Script para migrar dados do MySQL antigo para PostgreSQL
Execute este script para transferir dados do sistema desktop para a versão na nuvem
"""

import mysql.connector
import psycopg2
import logging
from typing import List, Dict, Any
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do MySQL (sistema antigo)
MYSQL_CONFIG = {
    'host': 'reservaai.cgns57eoufkz.us-east-1.rds.amazonaws.com',
    'user': 'robo',
    'password': 'D41D8CD98F00B204E9800998ECF8427E',
    'database': 'boro',
}

# Configurações do PostgreSQL (sistema novo)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'portal_user',
    'password': 'portal_password',
    'database': 'boro_portal',
}


def connect_mysql():
    """Conectar ao MySQL"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        logger.info("Conectado ao MySQL com sucesso")
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar ao MySQL: {e}")
        return None


def connect_postgres():
    """Conectar ao PostgreSQL"""
    try:
        connection = psycopg2.connect(**POSTGRES_CONFIG)
        logger.info("Conectado ao PostgreSQL com sucesso")
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        return None


def migrate_motoristas(mysql_conn, postgres_conn):
    """Migrar tabela de motoristas"""
    try:
        # Buscar dados do MySQL
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM motoristas")
        motoristas = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(motoristas)} motoristas no MySQL")
        
        # Inserir no PostgreSQL
        postgres_cursor = postgres_conn.cursor()
        
        for motorista in motoristas:
            # Adaptar estrutura se necessário
            postgres_cursor.execute("""
                INSERT INTO motoristas (id, placa, cpf, nome, aceita_bobina, situacao, ordem_motorista, placa_carreta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    placa = EXCLUDED.placa,
                    cpf = EXCLUDED.cpf,
                    nome = EXCLUDED.nome,
                    aceita_bobina = EXCLUDED.aceita_bobina,
                    situacao = EXCLUDED.situacao,
                    ordem_motorista = EXCLUDED.ordem_motorista,
                    placa_carreta = EXCLUDED.placa_carreta
            """, motorista)
        
        postgres_conn.commit()
        logger.info("Motoristas migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar motoristas: {e}")
        postgres_conn.rollback()


def migrate_destinos(mysql_conn, postgres_conn):
    """Migrar tabela de destinos"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM destinos")
        destinos = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(destinos)} destinos no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for destino in destinos:
            postgres_cursor.execute("""
                INSERT INTO destinos (id, nome_destino)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome_destino = EXCLUDED.nome_destino
            """, destino)
        
        postgres_conn.commit()
        logger.info("Destinos migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar destinos: {e}")
        postgres_conn.rollback()


def migrate_origens(mysql_conn, postgres_conn):
    """Migrar tabela de origens"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM origens")
        origens = mysql_cursor.fetchall()
        
        logger.info(f"Encontradas {len(origens)} origens no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for origem in origens:
            postgres_cursor.execute("""
                INSERT INTO origens (id, nome_origem)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome_origem = EXCLUDED.nome_origem
            """, origem)
        
        postgres_conn.commit()
        logger.info("Origens migradas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar origens: {e}")
        postgres_conn.rollback()


def migrate_tipo_veiculo(mysql_conn, postgres_conn):
    """Migrar tabela de tipos de veículo"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM tipo_veiculo")
        tipos = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(tipos)} tipos de veículo no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for tipo in tipos:
            postgres_cursor.execute("""
                INSERT INTO tipo_veiculo (id, nome_tipo_veiculo)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome_tipo_veiculo = EXCLUDED.nome_tipo_veiculo
            """, tipo)
        
        postgres_conn.commit()
        logger.info("Tipos de veículo migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar tipos de veículo: {e}")
        postgres_conn.rollback()


def migrate_parametros(mysql_conn, postgres_conn):
    """Migrar tabela de parâmetros"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM parametros")
        parametros = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(parametros)} parâmetros no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for param in parametros:
            # Adaptar estrutura se necessário
            postgres_cursor.execute("""
                INSERT INTO parametros (id, valor_carreta, valor_truck, modo_teste, email_notificacao)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    valor_carreta = EXCLUDED.valor_carreta,
                    valor_truck = EXCLUDED.valor_truck,
                    modo_teste = EXCLUDED.modo_teste,
                    email_notificacao = EXCLUDED.email_notificacao
            """, param)
        
        postgres_conn.commit()
        logger.info("Parâmetros migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar parâmetros: {e}")
        postgres_conn.rollback()


def migrate_login(mysql_conn, postgres_conn):
    """Migrar tabela de login"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM login")
        logins = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(logins)} registros de login no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for login in logins:
            postgres_cursor.execute("""
                INSERT INTO login (id, usuario, senha)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    usuario = EXCLUDED.usuario,
                    senha = EXCLUDED.senha
            """, login)
        
        postgres_conn.commit()
        logger.info("Logins migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar logins: {e}")
        postgres_conn.rollback()


def migrate_rotas(mysql_conn, postgres_conn):
    """Migrar tabela de rotas"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM rotas")
        rotas = mysql_cursor.fetchall()
        
        logger.info(f"Encontradas {len(rotas)} rotas no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for rota in rotas:
            postgres_cursor.execute("""
                INSERT INTO rotas (id, origem_rota, destino_rota, doc_transporte, data_hora_chegada, 
                                 valor_carga, motorista_rota, tipo_veiculo, situacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_transporte) DO UPDATE SET
                    origem_rota = EXCLUDED.origem_rota,
                    destino_rota = EXCLUDED.destino_rota,
                    data_hora_chegada = EXCLUDED.data_hora_chegada,
                    valor_carga = EXCLUDED.valor_carga,
                    motorista_rota = EXCLUDED.motorista_rota,
                    tipo_veiculo = EXCLUDED.tipo_veiculo,
                    situacao = EXCLUDED.situacao
            """, rota)
        
        postgres_conn.commit()
        logger.info("Rotas migradas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar rotas: {e}")
        postgres_conn.rollback()


def migrate_relatorios(mysql_conn, postgres_conn):
    """Migrar tabela de relatórios"""
    try:
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM relatorios")
        relatorios = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(relatorios)} relatórios no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for relatorio in relatorios:
            postgres_cursor.execute("""
                INSERT INTO relatorios (id, origem_rota, destino_rota, doc_transporte, data_hora_chegada,
                                      valor_carga, peso_total, tipo_veiculo, observacoes_rota, prioridade,
                                      clientes, mais_de_um_cliente, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    origem_rota = EXCLUDED.origem_rota,
                    destino_rota = EXCLUDED.destino_rota,
                    doc_transporte = EXCLUDED.doc_transporte,
                    data_hora_chegada = EXCLUDED.data_hora_chegada,
                    valor_carga = EXCLUDED.valor_carga,
                    peso_total = EXCLUDED.peso_total,
                    tipo_veiculo = EXCLUDED.tipo_veiculo,
                    observacoes_rota = EXCLUDED.observacoes_rota,
                    prioridade = EXCLUDED.prioridade,
                    clientes = EXCLUDED.clientes,
                    mais_de_um_cliente = EXCLUDED.mais_de_um_cliente,
                    motivo = EXCLUDED.motivo
            """, relatorio)
        
        postgres_conn.commit()
        logger.info("Relatórios migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar relatórios: {e}")
        postgres_conn.rollback()


def migrate_relationships(mysql_conn, postgres_conn):
    """Migrar tabelas de relacionamento"""
    try:
        # Migrar motorista_destino
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT * FROM motorista_destino")
        motorista_destinos = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(motorista_destinos)} relacionamentos motorista-destino no MySQL")
        
        postgres_cursor = postgres_conn.cursor()
        
        for md in motorista_destinos:
            postgres_cursor.execute("""
                INSERT INTO motorista_destino (motorista_id, destino_id)
                VALUES (%s, %s)
                ON CONFLICT (motorista_id, destino_id) DO NOTHING
            """, md[1:3])  # Pular o ID
        
        # Migrar motorista_origem
        mysql_cursor.execute("SELECT * FROM motorista_origem")
        motorista_origens = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(motorista_origens)} relacionamentos motorista-origem no MySQL")
        
        for mo in motorista_origens:
            postgres_cursor.execute("""
                INSERT INTO motorista_origem (motorista_id, origem_id)
                VALUES (%s, %s)
                ON CONFLICT (motorista_id, origem_id) DO NOTHING
            """, mo[1:3])  # Pular o ID
        
        # Migrar motorista_tipo_veiculo
        mysql_cursor.execute("SELECT * FROM motorista_tipo_veiculo")
        motorista_tipos = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(motorista_tipos)} relacionamentos motorista-tipo_veiculo no MySQL")
        
        for mt in motorista_tipos:
            postgres_cursor.execute("""
                INSERT INTO motorista_tipo_veiculo (motorista_id, tipo_veiculo_id)
                VALUES (%s, %s)
                ON CONFLICT (motorista_id, tipo_veiculo_id) DO NOTHING
            """, mt[1:3])  # Pular o ID
        
        # Migrar motorista_tipo_veiculo_carreta
        mysql_cursor.execute("SELECT * FROM motorista_tipo_veiculo_carreta")
        motorista_tipos_carreta = mysql_cursor.fetchall()
        
        logger.info(f"Encontrados {len(motorista_tipos_carreta)} relacionamentos motorista-tipo_veiculo_carreta no MySQL")
        
        for mtc in motorista_tipos_carreta:
            postgres_cursor.execute("""
                INSERT INTO motorista_tipo_veiculo_carreta (motorista_id, tipo_veiculo_id)
                VALUES (%s, %s)
                ON CONFLICT (motorista_id, tipo_veiculo_id) DO NOTHING
            """, mtc[1:3])  # Pular o ID
        
        postgres_conn.commit()
        logger.info("Relacionamentos migrados com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao migrar relacionamentos: {e}")
        postgres_conn.rollback()


def main():
    """Função principal de migração"""
    logger.info("Iniciando migração de dados do MySQL para PostgreSQL")
    
    # Conectar aos bancos
    mysql_conn = connect_mysql()
    if not mysql_conn:
        logger.error("Não foi possível conectar ao MySQL")
        sys.exit(1)
    
    postgres_conn = connect_postgres()
    if not postgres_conn:
        logger.error("Não foi possível conectar ao PostgreSQL")
        mysql_conn.close()
        sys.exit(1)
    
    try:
        # Executar migrações
        logger.info("Iniciando migração das tabelas...")
        
        migrate_tipo_veiculo(mysql_conn, postgres_conn)
        migrate_destinos(mysql_conn, postgres_conn)
        migrate_origens(mysql_conn, postgres_conn)
        migrate_motoristas(mysql_conn, postgres_conn)
        migrate_parametros(mysql_conn, postgres_conn)
        migrate_login(mysql_conn, postgres_conn)
        migrate_relationships(mysql_conn, postgres_conn)
        migrate_rotas(mysql_conn, postgres_conn)
        migrate_relatorios(mysql_conn, postgres_conn)
        
        logger.info("Migração concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {e}")
    finally:
        # Fechar conexões
        mysql_conn.close()
        postgres_conn.close()
        logger.info("Conexões fechadas")


if __name__ == "__main__":
    main()
