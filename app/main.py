import logging
import structlog
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import time

from app.config import settings
from app.database import engine, Base
from app.celery_app import celery_app
from app.tasks import process_portal_routes, health_check
from app.services.database_service import DatabaseService
from app.models import TaskExecution

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Iniciando aplicação Portal e-Fornecedores")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados criadas/verificadas")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação Portal e-Fornecedores")


# Create FastAPI app
app = FastAPI(
    title="Portal e-Fornecedores - Automação",
    description="API para automação do portal e-fornecedores.ind.br",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Portal e-Fornecedores - Automação",
        "version": "1.0.0",
        "status": "executando"
    }


@app.get("/saude")
async def verificar_saude():
    """Verificar saúde do sistema"""
    try:
        # Verificar conexão com banco
        db_service = DatabaseService()
        data = db_service.get_all_data()
        
        # Verificar Celery
        celery_task = health_check.delay()
        celery_result = celery_task.get(timeout=10)
        
        return {
            "status": "saudavel",
            "banco_dados": "conectado",
            "celery": "conectado",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Verificação de saúde falhou: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Serviço não saudável: {str(e)}")


@app.post("/tarefas/processar-rotas")
async def iniciar_processamento_rotas(background_tasks: BackgroundTasks):
    """Iniciar tarefa de processamento de rotas"""
    try:
        # Verificar se já existe uma tarefa em execução
        db_service = DatabaseService()
        tarefa_rodando = db_service.db.query(TaskExecution).filter(
            TaskExecution.status == "running"
        ).first()
        
        if tarefa_rodando:
            # Verificar se a tarefa está realmente rodando no Celery
            try:
                celery_task_id = tarefa_rodando.celery_task_id if tarefa_rodando.celery_task_id else str(tarefa_rodando.id)
                celery_task = celery_app.AsyncResult(celery_task_id)
                if celery_task.state in ['PENDING', 'STARTED', 'PROGRESS']:
                    return {
                        "mensagem": "Já existe uma tarefa em execução",
                        "id_tarefa": tarefa_rodando.id,
                        "iniciada_em": tarefa_rodando.started_at.isoformat(),
                        "estado_celery": celery_task.state
                    }
                else:
                    # Tarefa não está realmente rodando, marcar como falhada
                    db_service.update_task_execution(
                        tarefa_rodando.id, 
                        "failed", 
                        error_message=f"Tarefa interrompida ou falhou (estado Celery: {celery_task.state})"
                    )
                    logger.info(f"Tarefa travada {tarefa_rodando.id} (Celery: {celery_task_id}) marcada como falhada")
            except Exception as e:
                logger.warning(f"Erro ao verificar tarefa Celery: {str(e)}")
                # Marcar como falhada se não conseguir verificar
                db_service.update_task_execution(
                    tarefa_rodando.id, 
                    "failed", 
                    error_message="Erro ao verificar status da tarefa"
                )
        
        # Iniciar nova tarefa
        task = process_portal_routes.delay()
        
        logger.info(f"Nova tarefa de processamento iniciada: {task.id}")
        
        return {
            "mensagem": "Tarefa de processamento iniciada",
            "id_tarefa": task.id,
            "status": "iniciada"
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar processamento: {str(e)}")


@app.get("/tarefas/{task_id}")
async def obter_status_tarefa(task_id: str):
    """Obter status e resultado da tarefa"""
    try:
        # Obter tarefa do Celery
        task = celery_app.AsyncResult(task_id)
        
        # Também obter execução da tarefa do banco
        db_service = DatabaseService()
        execucao_tarefa = db_service.db.query(TaskExecution).filter(
            TaskExecution.celery_task_id == task_id
        ).first()
        
        # Se não encontrado por celery_task_id, tentar por ID de execução
        if not execucao_tarefa:
            try:
                execution_id = int(task_id)
                execucao_tarefa = db_service.db.query(TaskExecution).filter(
                    TaskExecution.id == execution_id
                ).first()
            except ValueError:
                execucao_tarefa = None
        
        response = {
            'id_tarefa': task_id,
            'estado_celery': task.state,
            'info_celery': task.info if task.info else {}
        }
        
        # Adicionar informações do banco se disponível
        if execucao_tarefa:
            response.update({
                'id_execucao': execucao_tarefa.id,
                'nome_tarefa': execucao_tarefa.task_name,
                'status_banco': execucao_tarefa.status,
                'iniciada_em': execucao_tarefa.started_at.isoformat() if execucao_tarefa.started_at else None,
                'concluida_em': execucao_tarefa.completed_at.isoformat() if execucao_tarefa.completed_at else None,
                'rotas_processadas': execucao_tarefa.rotas_processadas,
                'rotas_vinculadas': execucao_tarefa.rotas_vinculadas,
                'mensagem_erro': execucao_tarefa.error_message
            })
        
        # Adicionar informações específicas do Celery
        if task.state == 'PENDING':
            response['status'] = 'Tarefa aguardando...'
        elif task.state == 'PROGRESS':
            response.update({
                'status': task.info.get('status', ''),
                'atual': task.info.get('current', 0),
                'total': task.info.get('total', 0),
                'vinculadas': task.info.get('vinculadas', 0)
            })
        elif task.state == 'SUCCESS':
            response['resultado'] = task.result
        elif task.state == 'FAILURE':
            response['erro'] = str(task.info)
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao obter status da tarefa {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter status da tarefa: {str(e)}")


@app.get("/tarefas")
async def listar_tarefas():
    """Listar execuções recentes de tarefas"""
    try:
        db_service = DatabaseService()
        tarefas = db_service.db.query(TaskExecution).order_by(
            TaskExecution.created_at.desc()
        ).limit(10).all()
        
        return [
            {
                "id": tarefa.id,
                "id_tarefa_celery": tarefa.celery_task_id,
                "nome_tarefa": tarefa.task_name,
                "status": tarefa.status,
                "iniciada_em": tarefa.started_at.isoformat() if tarefa.started_at else None,
                "concluida_em": tarefa.completed_at.isoformat() if tarefa.completed_at else None,
                "rotas_processadas": tarefa.rotas_processadas,
                "rotas_vinculadas": tarefa.rotas_vinculadas,
                "mensagem_erro": tarefa.error_message
            }
            for tarefa in tarefas
        ]
        
    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar tarefas: {str(e)}")


@app.get("/rotas")
async def obter_rotas():
    """Obter rotas recentes"""
    try:
        db_service = DatabaseService()
        rotas = db_service.db.query(Rota).order_by(
            Rota.created_at.desc()
        ).limit(50).all()
        
        return [
            {
                "id": rota.id,
                "origem": rota.origem_rota,
                "destino": rota.destino_rota,
                "documento_transporte": rota.doc_transporte,
                "motorista": rota.motorista_rota,
                "tipo_veiculo": rota.tipo_veiculo,
                "valor_carga": rota.valor_carga,
                "criada_em": rota.created_at.isoformat()
            }
            for rota in rotas
        ]
        
    except Exception as e:
        logger.error(f"Erro ao obter rotas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter rotas: {str(e)}")


@app.get("/reports")
async def get_reports():
    """Get recent reports"""
    try:
        db_service = DatabaseService()
        reports = db_service.db.query(Relatorio).order_by(
            Relatorio.created_at.desc()
        ).limit(50).all()
        
        return [
            {
                "id": report.id,
                "origem": report.origem_rota,
                "destino": report.destino_rota,
                "doc_transporte": report.doc_transporte,
                "tipo_veiculo": report.tipo_veiculo,
                "valor_carga": report.valor_carga,
                "motivo": report.motivo,
                "created_at": report.created_at.isoformat()
            }
            for report in reports
        ]
        
    except Exception as e:
        logger.error(f"Erro ao obter relatórios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter relatórios: {str(e)}")


@app.get("/motoristas")
async def obter_motoristas():
    """Obter motoristas ativos"""
    try:
        db_service = DatabaseService()
        motoristas = db_service.db.query(Motorista).filter(
            Motorista.situacao == True
        ).order_by(Motorista.ordem_motorista).all()
        
        return [
            {
                "id": motorista.id,
                "nome": motorista.nome,
                "cpf": motorista.cpf,
                "placa": motorista.placa,
                "celular": motorista.celular,
                "aceita_bobina": motorista.aceita_bobina,
                "ordem_motorista": motorista.ordem_motorista
            }
            for motorista in motoristas
        ]
        
    except Exception as e:
        logger.error(f"Erro ao obter motoristas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter motoristas: {str(e)}")


@app.get("/estatisticas")
async def obter_estatisticas():
    """Obter estatísticas do sistema"""
    try:
        db_service = DatabaseService()
        
        # Contar rotas
        total_rotas = db_service.db.query(Rota).count()
        rotas_hoje = db_service.db.query(Rota).filter(
            Rota.created_at >= time.time() - 86400  # Últimas 24 horas
        ).count()
        
        # Contar relatórios
        total_relatorios = db_service.db.query(Relatorio).count()
        relatorios_hoje = db_service.db.query(Relatorio).filter(
            Relatorio.created_at >= time.time() - 86400  # Últimas 24 horas
        ).count()
        
        # Contar motoristas ativos
        motoristas_ativos = db_service.db.query(Motorista).filter(
            Motorista.situacao == True
        ).count()
        
        # Obter status da tarefa recente
        tarefa_recente = db_service.db.query(TaskExecution).order_by(
            TaskExecution.created_at.desc()
        ).first()
        
        return {
            "rotas": {
                "total": total_rotas,
                "hoje": rotas_hoje
            },
            "relatorios": {
                "total": total_relatorios,
                "hoje": relatorios_hoje
            },
            "motoristas_ativos": motoristas_ativos,
            "ultima_execucao": {
                "status": tarefa_recente.status if tarefa_recente else None,
                "iniciada_em": tarefa_recente.started_at.isoformat() if tarefa_recente else None,
                "rotas_processadas": tarefa_recente.rotas_processadas if tarefa_recente else 0,
                "rotas_vinculadas": tarefa_recente.rotas_vinculadas if tarefa_recente else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@app.post("/tasks/clear-stuck")
async def clear_stuck_tasks():
    """Clear stuck tasks that are marked as running but not actually running"""
    try:
        db_service = DatabaseService()
        
        # Find all running tasks
        running_tasks = db_service.db.query(TaskExecution).filter(
            TaskExecution.status == "running"
        ).all()
        
        cleared_count = 0
        
        for task in running_tasks:
            try:
                # Use celery_task_id if available, otherwise use task.id
                celery_task_id = task.celery_task_id if task.celery_task_id else str(task.id)
                celery_task = celery_app.AsyncResult(celery_task_id)
                
                if celery_task.state not in ['PENDING', 'STARTED', 'PROGRESS']:
                    # Task is not actually running, mark it as failed
                    db_service.update_task_execution(
                        task.id, 
                        "failed", 
                        error_message=f"Tarefa travada - limpa automaticamente (Celery state: {celery_task.state})"
                    )
                    cleared_count += 1
                    logger.info(f"Tarefa travada {task.id} (Celery: {celery_task_id}) marcada como falhada")
            except Exception as e:
                logger.warning(f"Erro ao verificar tarefa {task.id}: {str(e)}")
                # Mark as failed if we can't check
                db_service.update_task_execution(
                    task.id, 
                    "failed", 
                    error_message="Erro ao verificar status - marcada como falhada"
                )
                cleared_count += 1
        
        return {
            "message": f"Limpeza concluída",
            "tarefas_limpas": cleared_count,
            "total_verificadas": len(running_tasks)
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar tarefas travadas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar tarefas travadas: {str(e)}")


@app.delete("/tarefas/{task_id}")
async def cancelar_tarefa(task_id: str):
    """Cancelar uma tarefa em execução"""
    try:
        # Tentar revogar a tarefa no Celery
        celery_app.control.revoke(task_id, terminate=True)
        
        # Atualizar status da tarefa no banco por celery_task_id
        db_service = DatabaseService()
        tarefa = db_service.db.query(TaskExecution).filter(TaskExecution.celery_task_id == task_id).first()
        
        if tarefa:
            db_service.update_task_execution(
                tarefa.id,  # Usar o ID inteiro do banco
                "cancelled", 
                error_message="Tarefa cancelada pelo usuário"
            )
            return {
                "mensagem": "Tarefa cancelada com sucesso",
                "id_tarefa": task_id,
                "id_execucao": tarefa.id
            }
        else:
            # Se não encontrado por celery_task_id, tentar por ID de execução (se task_id for numérico)
            try:
                execution_id = int(task_id)
                tarefa = db_service.db.query(TaskExecution).filter(TaskExecution.id == execution_id).first()
                if tarefa:
                    db_service.update_task_execution(
                        execution_id,
                        "cancelled", 
                        error_message="Tarefa cancelada pelo usuário"
                    )
                    return {
                        "mensagem": "Tarefa cancelada com sucesso",
                        "id_tarefa": task_id,
                        "id_execucao": execution_id
                    }
            except ValueError:
                pass
            
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
    except Exception as e:
        logger.error(f"Erro ao cancelar tarefa {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar tarefa: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
