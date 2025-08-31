import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import SessionLocal
from app.models import (
    Motorista, Destino, Origem, TipoVeiculo, MotoristaDestino,
    MotoristaOrigem, MotoristaTipoVeiculo, MotoristaTipoVeiculoCarreta,
    Parametro, Login, Rota, Relatorio, TaskExecution
)

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all data from database (similar to original DADOS function)"""
        try:
            data = {}
            
            # Get destinations
            destinos = self.db.query(Destino).all()
            data['destinos'] = [(d.id, d.nome_destino) for d in destinos]
            
            # Get active drivers
            motoristas = self.db.query(Motorista).filter(Motorista.situacao == True).order_by(Motorista.ordem_motorista).all()
            data['motoristas'] = [
                (m.id, m.placa, m.cpf, m.nome, None, None, None, None, m.aceita_bobina, m.situacao, None, None, None, m.placa_carreta)
                for m in motoristas
            ]
            
            # Get driver destinations
            motorista_destinos = self.db.query(MotoristaDestino).join(Destino).join(Motorista).filter(Motorista.situacao == True).all()
            data['motorista_destino'] = [
                (md.motorista_id, d.nome_destino) 
                for md in motorista_destinos 
                for d in [md.destino] 
                for m in [md.motorista]
            ]
            
            # Get origins
            origens = self.db.query(Origem).all()
            data['origens'] = [(o.id, o.nome_origem) for o in origens]
            
            # Get parameters
            parametros = self.db.query(Parametro).all()
            data['parametros'] = [
                (p.id, p.valor_truck, None, p.valor_carreta, p.modo_teste, p.email_notificacao)
                for p in parametros
            ]
            
            # Get vehicle types
            tipo_veiculos = self.db.query(TipoVeiculo).all()
            data['tipo_veiculo'] = [(tv.id, tv.nome_tipo_veiculo) for tv in tipo_veiculos]
            
            # Get login credentials
            login = self.db.query(Login).all()
            data['login'] = [(l.id, l.login, l.senha) for l in login]
            
            # Get driver vehicle types
            motoristas_tipo_veiculo = self.db.query(MotoristaTipoVeiculo).join(TipoVeiculo).join(Motorista).filter(Motorista.situacao == True).all()
            data['motoristas_tipo_veiculo'] = [
                (mtv.motorista_id, tv.nome_tipo_veiculo)
                for mtv in motoristas_tipo_veiculo
                for tv in [mtv.tipo_veiculo]
                for m in [mtv.motorista]
            ]
            
            # Get driver carreta vehicle types
            motoristas_tipo_veiculo_carreta = self.db.query(MotoristaTipoVeiculoCarreta).join(TipoVeiculo).join(Motorista).filter(Motorista.situacao == True).all()
            data['motoristas_tipo_veiculo_carreta'] = [
                (mtvc.motorista_id, tv.nome_tipo_veiculo)
                for mtvc in motoristas_tipo_veiculo_carreta
                for tv in [mtvc.tipo_veiculo]
                for m in [mtvc.motorista]
            ]
            
            # Get active destinations (destinations that have active drivers)
            select_destinos_motoristas_ativos = self.db.query(Destino).join(MotoristaDestino).join(Motorista).filter(Motorista.situacao == True).group_by(Destino.id).all()
            data['select_destinos_motoristas_ativos'] = [(d.id, d.nome_destino) for d in select_destinos_motoristas_ativos]
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do banco: {str(e)}")
            return {}
    
    def save_route(self, route_data: Dict[str, Any]) -> bool:
        """Save a new route"""
        try:
            rota = Rota(
                origem_rota=route_data.get('origem'),
                destino_rota=route_data.get('destino'),
                doc_transporte=route_data.get('doc_transporte'),
                data_hora_chegada=route_data.get('data_hora_chegada'),
                valor_carga=route_data.get('valor_carga'),
                motorista_rota=route_data.get('motorista_rota'),
                tipo_veiculo=route_data.get('tipo_veiculo'),
                situacao=route_data.get('situacao')
            )
            
            self.db.add(rota)
            self.db.commit()
            logger.info(f"Rota salva com sucesso: {route_data.get('doc_transporte')}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao salvar rota: {str(e)}")
            return False
    
    def save_report(self, report_data: Dict[str, Any]) -> bool:
        """Save a new report entry"""
        try:
            # Check if report already exists
            existing_report = self.db.query(Relatorio).filter(
                Relatorio.doc_transporte == report_data.get('doc_transporte')
            ).first()
            
            if existing_report:
                logger.info(f"Relatório já existe para documento: {report_data.get('doc_transporte')}")
                return False
            
            # Check if route already exists
            existing_route = self.db.query(Rota).filter(
                Rota.doc_transporte == report_data.get('doc_transporte')
            ).first()
            
            if existing_route:
                logger.info(f"Rota já existe para documento: {report_data.get('doc_transporte')}")
                return False
            
            relatorio = Relatorio(
                origem_rota=report_data.get('origem'),
                destino_rota=report_data.get('destino'),
                doc_transporte=report_data.get('doc_transporte'),
                data_hora_chegada=report_data.get('data_hora_chegada'),
                valor_carga=report_data.get('valor_carga'),
                peso_total=report_data.get('peso_total'),
                tipo_veiculo=report_data.get('tipo_veiculo'),
                observacoes_rota=report_data.get('observacoes_rota'),
                prioridade=report_data.get('prioridade'),
                clientes=report_data.get('clientes'),
                mais_de_um_cliente=report_data.get('mais_de_um_cliente', False),
                motivo=report_data.get('motivo')
            )
            
            self.db.add(relatorio)
            self.db.commit()
            logger.info(f"Relatório salvo com sucesso: {report_data.get('doc_transporte')}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao salvar relatório: {str(e)}")
            return False
    
    def update_driver_status(self, driver_id: int) -> bool:
        """Update driver status to inactive and set order to 10000"""
        try:
            driver = self.db.query(Motorista).filter(Motorista.id == driver_id).first()
            if driver:
                driver.situacao = False
                driver.ordem_motorista = 10000
                self.db.commit()
                logger.info(f"Status do motorista {driver_id} atualizado")
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar status do motorista: {str(e)}")
            return False
    
    def obter_credenciais_portal(self) -> Dict[str, str]:
        """Obter credenciais do portal da tabela login"""
        try:
            login = self.db.query(Login).first()
            if login:
                return {
                    "usuario": login.login,
                    "senha": login.senha
                }
            else:
                logger.warning("Nenhuma credencial encontrada na tabela login")
                return {}
        except Exception as e:
            logger.error(f"Erro ao obter credenciais do portal: {str(e)}")
            return {}
    
    def get_driver_data_for_linking(self, driver_id: int, destination: str = "") -> Dict[str, Any]:
        """Get driver data for linking (similar to dadosDBParaVincular)"""
        try:
            data = {}
            
            # Get driver destinations
            motorista_destinos = self.db.query(MotoristaDestino).join(Destino).filter(
                and_(
                    MotoristaDestino.motorista_id == driver_id,
                    Destino.nome_destino == destination.lower()
                )
            ).all()
            data['motorista_destino'] = [
                (md.motorista_id, d.nome_destino)
                for md in motorista_destinos
                for d in [md.destino]
            ]
            
            # Get driver origins
            motorista_origens = self.db.query(MotoristaOrigem).filter(
                MotoristaOrigem.motorista_id == driver_id
            ).all()
            data['motorista_origem'] = [
                (mo.motorista_id, o.nome_origem)
                for mo in motorista_origens
                for o in [mo.origem]
            ]
            
            # Get driver vehicle types
            motoristas_tipo_veiculo = self.db.query(MotoristaTipoVeiculo).join(TipoVeiculo).filter(
                MotoristaTipoVeiculo.motorista_id == driver_id
            ).all()
            data['motoristas_tipo_veiculo'] = [
                (mtv.motorista_id, tv.nome_tipo_veiculo)
                for mtv in motoristas_tipo_veiculo
                for tv in [mtv.tipo_veiculo]
            ]
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do motorista para vinculação: {str(e)}")
            return {}
    
    def create_task_execution(self, task_name: str) -> int:
        """Create a new task execution record"""
        try:
            task_execution = TaskExecution(
                task_name=task_name,
                status="running"
            )
            self.db.add(task_execution)
            self.db.commit()
            return task_execution.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar execução de tarefa: {str(e)}")
            return 0
    
    def update_task_execution(self, task_id: int, status: str, **kwargs) -> bool:
        """Update task execution status and details"""
        try:
            task_execution = self.db.query(TaskExecution).filter(TaskExecution.id == task_id).first()
            if task_execution:
                task_execution.status = status
                if status in ["completed", "failed"]:
                    task_execution.completed_at = func.now()
                if "error_message" in kwargs:
                    task_execution.error_message = kwargs["error_message"]
                if "rotas_processadas" in kwargs:
                    task_execution.rotas_processadas = kwargs["rotas_processadas"]
                if "rotas_vinculadas" in kwargs:
                    task_execution.rotas_vinculadas = kwargs["rotas_vinculadas"]
                if "celery_task_id" in kwargs:
                    task_execution.celery_task_id = kwargs["celery_task_id"]
                
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar execução de tarefa: {str(e)}")
            return False
