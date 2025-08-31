import logging
import time
from typing import Dict, List, Any, Optional
from celery import current_task
from app.celery_app import celery_app
from app.services.portal_service import PortalService
from app.services.database_service import DatabaseService
from app.services.email_service import EmailService
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_portal_routes(self):
    """Main task to process portal routes"""
    task_id = self.request.id
    logger.info(f"Iniciando processamento de rotas - Task ID: {task_id}")
    
    portal_service = PortalService()
    db_service = DatabaseService()
    email_service = EmailService()
    
    # Create task execution record
    execution_id = db_service.create_task_execution("process_portal_routes")
    
    # Store the Celery task ID in the database record for later reference
    db_service.update_task_execution(execution_id, "running", celery_task_id=task_id)
    
    try:
        # Setup WebDriver
        driver = portal_service.setup_driver()
        
        # Login to portal
        if not portal_service.login():
            error_msg = "Falha no login no portal"
            logger.error(error_msg)
            db_service.update_task_execution(execution_id, "failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        
        # Navigate to routes page
        if not portal_service.navigate_to_routes_page():
            error_msg = "Falha ao navegar para página de rotas"
            logger.error(error_msg)
            db_service.update_task_execution(execution_id, "failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        
        # Get all data from database
        data = db_service.get_all_data()
        if not data:
            error_msg = "Falha ao obter dados do banco"
            logger.error(error_msg)
            db_service.update_task_execution(execution_id, "failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        
        # Process routes
        rotas_processadas = 0
        rotas_vinculadas = 0
        
        # Get available destinations from portal
        available_destinations = portal_service.get_available_destinations()
        
        # Process each destination that exists in our database
        for destino_tuple in data.get('select_destinos_motoristas_ativos', []):
            destino_id, destino_nome = destino_tuple
            
            # Check if destination exists in portal
            if destino_nome not in available_destinations:
                logger.info(f"Destino {destino_nome} não encontrado no portal")
                continue
            
            # Filter by destination
            if not portal_service.filter_by_destination(destino_nome):
                logger.error(f"Falha ao filtrar por destino {destino_nome}")
                continue
            
            # Get routes for this destination
            routes = portal_service.get_routes_table()
            rotas_processadas += len(routes)
            
            # Process each route
            for route in routes:
                try:
                    # Get route details
                    route_details = portal_service.get_route_details(route['numero_documento'])
                    
                    # Process route (this would contain the main logic from the original code)
                    if process_single_route(route, route_details, data, db_service, email_service, portal_service):
                        rotas_vinculadas += 1
                    
                    # Update task progress
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': rotas_processadas,
                            'total': len(routes),
                            'vinculadas': rotas_vinculadas
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Erro ao processar rota {route.get('numero_documento')}: {str(e)}")
                    continue
        
        # Update final status
        db_service.update_task_execution(
            execution_id, 
            "completed", 
            rotas_processadas=rotas_processadas,
            rotas_vinculadas=rotas_vinculadas
        )
        
        logger.info(f"Processamento concluído - Rotas processadas: {rotas_processadas}, Vinculadas: {rotas_vinculadas}")
        
        return {
            "status": "completed",
            "rotas_processadas": rotas_processadas,
            "rotas_vinculadas": rotas_vinculadas
        }
        
    except Exception as e:
        error_msg = f"Erro geral no processamento: {str(e)}"
        logger.error(error_msg)
        db_service.update_task_execution(execution_id, "failed", error_message=error_msg)
        return {"status": "failed", "error": error_msg}
        
    finally:
        # Clean up
        portal_service.close_driver()


def process_single_route(
    route: Dict[str, Any],
    route_details: Dict[str, Any],
    data: Dict[str, Any],
    db_service: DatabaseService,
    email_service: EmailService,
    portal_service: PortalService
) -> bool:
    """Process a single route (main logic from original code)"""
    try:
        numero_documento = route['numero_documento']
        tipo_transporte = route['tipo_transporte']
        cluster = route['cluster']
        planta_origem = route['planta_origem']
        valor_carga = route_details.get('valor_carga', '')
        has_letter_b = route_details.get('has_letter_b', False)
        
        # Check if route meets criteria
        if not check_route_criteria(route, route_details, data):
            # Save to reports
            save_route_report(route, route_details, "Não atende critérios", db_service)
            return False
        
        # Find compatible driver
        compatible_driver = find_compatible_driver(
            route, route_details, data, db_service
        )
        
        if not compatible_driver:
            save_route_report(route, route_details, "Motorista não encontrado", db_service)
            return False
        
        # Link driver to route
        if link_driver_to_route(compatible_driver, route, portal_service):
            # Save successful route
            save_successful_route(compatible_driver, route, db_service)
            
            # Update driver status
            db_service.update_driver_status(compatible_driver['id'])
            
            # Send email notification
            email_service.send_route_linked_email(compatible_driver, numero_documento)
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Erro ao processar rota {route.get('numero_documento')}: {str(e)}")
        return False


def check_route_criteria(route: Dict[str, Any], route_details: Dict[str, Any], data: Dict[str, Any]) -> bool:
    """Check if route meets the criteria for processing"""
    try:
        tipo_transporte = route['tipo_transporte'].lower()
        valor_carga = route_details.get('valor_carga', '0')
        
        # Get parameters
        parametros = data.get('parametros', [])
        if not parametros:
            return False
        
        param = parametros[0]  # Assuming first parameter set
        valor_parametro_carreta = param[3]  # valor_carreta
        valor_parametro_truck = param[1]    # valor_truck
        
        # Convert cargo value to float
        try:
            valor_carga_float = float(valor_carga.replace(".", ""))
        except:
            valor_carga_float = 0
        
        # Check if transport type and value match criteria
        if 'carreta' in tipo_transporte and valor_carga_float <= valor_parametro_carreta:
            return True
        elif 'truck' in tipo_transporte and valor_carga_float <= valor_parametro_truck:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar critérios da rota: {str(e)}")
        return False


def find_compatible_driver(
    route: Dict[str, Any],
    route_details: Dict[str, Any],
    data: Dict[str, Any],
    db_service: DatabaseService
) -> Optional[Dict[str, Any]]:
    """Find a compatible driver for the route"""
    try:
        cluster = route['cluster']
        planta_origem = route['planta_origem']
        tipo_transporte = route['tipo_transporte']
        has_letter_b = route_details.get('has_letter_b', False)
        
        motoristas = data.get('motoristas', [])
        motorista_destinos = data.get('motorista_destino', [])
        motoristas_tipo_veiculo = data.get('motoristas_tipo_veiculo', [])
        
        for motorista_tuple in motoristas:
            motorista_id = motorista_tuple[0]
            placa = motorista_tuple[1]
            cpf = motorista_tuple[2]
            nome = motorista_tuple[3]
            aceita_bobina = motorista_tuple[8]
            situacao = motorista_tuple[9]
            placa_carreta = motorista_tuple[13] if len(motorista_tuple) > 13 else ""
            
            # Check if driver is active
            if not situacao:
                continue
            
            # Check if driver accepts bobina (if route has letter B)
            if has_letter_b and not aceita_bobina:
                continue
            
            # Check if driver serves this destination
            if not check_driver_destination(motorista_id, cluster, motorista_destinos):
                continue
            
            # Check if driver has compatible vehicle type
            if not check_driver_vehicle_type(motorista_id, tipo_transporte, motoristas_tipo_veiculo):
                continue
            
            # Check final validation
            driver_data = db_service.get_driver_data_for_linking(motorista_id, cluster)
            if not driver_data.get('motorista_destino'):
                continue
            
            # Return compatible driver
            return {
                'id': motorista_id,
                'nome': nome,
                'cpf': cpf,
                'placa': placa,
                'placa_carreta': placa_carreta
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao encontrar motorista compatível: {str(e)}")
        return None


def check_driver_destination(motorista_id: int, cluster: str, motorista_destinos: List[tuple]) -> bool:
    """Check if driver serves the given destination"""
    for md_id, destino in motorista_destinos:
        if md_id == motorista_id and destino.lower() == cluster.lower():
            return True
    return False


def check_driver_vehicle_type(motorista_id: int, tipo_transporte: str, motoristas_tipo_veiculo: List[tuple]) -> bool:
    """Check if driver has compatible vehicle type"""
    for mtv_id, tipo_veiculo in motoristas_tipo_veiculo:
        if mtv_id == motorista_id and tipo_veiculo.lower() == tipo_transporte.lower():
            return True
    return False


def link_driver_to_route(driver: Dict[str, Any], route: Dict[str, Any], portal_service: PortalService) -> bool:
    """Link driver to route in the portal"""
    try:
        # This would contain the logic to fill the form and link the driver
        # Implementation would depend on the specific portal interface
        # For now, returning True as placeholder
        logger.info(f"Vinculando motorista {driver['nome']} à rota {route['numero_documento']}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao vincular motorista à rota: {str(e)}")
        return False


def save_route_report(route: Dict[str, Any], route_details: Dict[str, Any], motivo: str, db_service: DatabaseService):
    """Save route to reports table"""
    try:
        report_data = {
            'origem': route.get('planta_origem'),
            'destino': route.get('cluster'),
            'doc_transporte': route.get('numero_documento'),
            'data_hora_chegada': route.get('data'),
            'valor_carga': route_details.get('valor_carga'),
            'peso_total': route.get('peso_total'),
            'tipo_veiculo': route.get('tipo_transporte'),
            'observacoes_rota': route_details.get('observations'),
            'prioridade': route.get('prioridade'),
            'clientes': '',
            'mais_de_um_cliente': False,
            'motivo': motivo
        }
        
        db_service.save_report(report_data)
        
    except Exception as e:
        logger.error(f"Erro ao salvar relatório: {str(e)}")


def save_successful_route(driver: Dict[str, Any], route: Dict[str, Any], db_service: DatabaseService):
    """Save successful route to routes table"""
    try:
        route_data = {
            'origem': route.get('planta_origem'),
            'destino': route.get('cluster'),
            'doc_transporte': route.get('numero_documento'),
            'data_hora_chegada': route.get('data'),
            'valor_carga': route.get('valor_carga'),
            'motorista_rota': driver.get('nome'),
            'tipo_veiculo': route.get('tipo_transporte'),
            'situacao': 'Vinculado'
        }
        
        db_service.save_route(route_data)
        
    except Exception as e:
        logger.error(f"Erro ao salvar rota: {str(e)}")


@celery_app.task
def health_check():
    """Health check task"""
    return {"status": "healthy", "timestamp": time.time()}
