from sqlalchemy import Column, BigInteger, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Motorista(Base):
    __tablename__ = "motoristas"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    placa = Column(String(255), nullable=False)
    cpf = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    celular = Column(String(255), nullable=False)
    regiao_motorista = Column(String(255), nullable=True)
    regioes_origem = Column(String(255), nullable=False)
    regioes_cluster = Column(String(255), nullable=False)
    aceita_bobina = Column(Boolean, default=False)
    situacao = Column(Boolean, default=True)
    ordem_motorista = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Destino(Base):
    __tablename__ = "destinos"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nome_destino = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Origem(Base):
    __tablename__ = "origens"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nome_origem = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class TipoVeiculo(Base):
    __tablename__ = "tipo_veiculo"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nome_tipo_veiculo = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class MotoristaDestino(Base):
    __tablename__ = "motorista_destino"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(BigInteger, ForeignKey("motoristas.id"))
    destino_id = Column(BigInteger, ForeignKey("destinos.id"))
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class MotoristaOrigem(Base):
    __tablename__ = "motorista_origem"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(BigInteger, ForeignKey("motoristas.id"))
    origem_id = Column(BigInteger, ForeignKey("origens.id"))
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class MotoristaTipoVeiculo(Base):
    __tablename__ = "motorista_tipo_veiculo"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(BigInteger, ForeignKey("motoristas.id"))
    tipo_veiculo_id = Column(BigInteger, ForeignKey("tipo_veiculo.id"))
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class MotoristaTipoVeiculoCarreta(Base):
    __tablename__ = "motorista_tipo_veiculo_carreta"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    motorista_id = Column(BigInteger, ForeignKey("motoristas.id"))
    tipo_veiculo_id = Column(BigInteger, ForeignKey("tipo_veiculo.id"))
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Parametro(Base):
    __tablename__ = "parametros"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    valor_maximo_carga_truck = Column(Float, nullable=False, default=150.00)
    valor_maximo_carga_bi_truck = Column(Float, nullable=False, default=150.00)
    valor_maximo_carga_carreta_truck = Column(Float, nullable=False, default=300.00)
    moto_teste = Column(Boolean, default=False)
    emails_notificacao = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Login(Base):
    __tablename__ = "login"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    login = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Rota(Base):
    __tablename__ = "rotas"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    origem_rota = Column(String(255), nullable=False)
    destino_rota = Column(String(255), nullable=False)
    doc_transporte = Column(String(255), nullable=False)
    data_hora_chegada = Column(String(255), nullable=False)
    valor_carga = Column(String(255), nullable=False)
    motorista_rota = Column(String(255), nullable=False)
    tipo_veiculo = Column(String(255), nullable=False)
    situacao = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class Relatorio(Base):
    __tablename__ = "relatorios"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    origem_rota = Column(String(255), nullable=False)
    destino_rota = Column(String(255), nullable=False)
    doc_transporte = Column(String(255), nullable=False)
    data_hora_chegada = Column(String(255), nullable=False)
    valor_carga = Column(String(255), nullable=False)
    pesoTotal = Column(String(255), nullable=False)
    tipo_veiculo = Column(String(255), nullable=False)
    observacoesRota = Column(Text, nullable=False)
    prioridade = Column(String(255), nullable=False)
    clientes = Column(String(255), nullable=False)
    maisDeUmCliente = Column(Boolean, nullable=False)
    motivo = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    task_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # running, completed, failed, cancelled
    celery_task_id = Column(String(100), nullable=True)  # Store Celery task ID for reference
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    rotas_processadas = Column(BigInteger, default=0)
    rotas_vinculadas = Column(BigInteger, default=0)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
