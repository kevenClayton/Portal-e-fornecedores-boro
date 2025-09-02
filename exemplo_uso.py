"""
Exemplo de Uso do Sistema de Rotas Melhorado
============================================

Este arquivo demonstra como usar o sistema refatorado de gerenciamento de rotas.
"""

from SistemaRotasMelhorado import (
    executar_sistema_rotas,
    GerenciadorRotas,
    DadosRota,
    DadosMotorista
)
import logging

def exemplo_uso_basico():
    """Exemplo básico de uso do sistema."""
    print("=== Exemplo de Uso Básico ===")
    
    # Configurar logging para debug
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Simular driver e window (em uso real, seriam objetos reais)
    driver = None  # WebDriver real
    window = None  # Interface real
    
    try:
        # Executar sistema completo
        executar_sistema_rotas(driver, window, interface_ativa=True)
        print("✅ Sistema executado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        logging.error(f"Erro detalhado: {e}")

def exemplo_uso_avancado():
    """Exemplo avançado usando as classes diretamente."""
    print("\n=== Exemplo de Uso Avançado ===")
    
    # Simular driver e window
    driver = None
    window = None
    
    try:
        # Criar gerenciador
        gerenciador = GerenciadorRotas(driver, window)
        
        # Executar operações específicas
        print("1. Listando rotas...")
        gerenciador.listar_todas_rotas()
        
        print("2. Selecionando origens e destinos...")
        gerenciador.selecionar_origem_destino(interface_ativa=True)
        
        print("✅ Operações concluídas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro nas operações: {e}")
        logging.error(f"Erro detalhado: {e}")

def exemplo_criacao_objetos():
    """Exemplo de criação e uso dos objetos de dados."""
    print("\n=== Exemplo de Criação de Objetos ===")
    
    # Criar objeto de rota
    rota = DadosRota(
        numero_documento="12345",
        data="2024-01-15",
        compartilhado="N",
        prioridade="1",
        tipo_transporte="Carreta",
        peso_total="25.5",
        unidade_peso="TON",
        planta_origem="Santa Luzia",
        cluster="Betim",
        estado="MG",
        observacoes="Carga especial",
        valor_carga="1500.00",
        tem_letra_b=True,
        clientes_mesmo_destino=["Cliente A", "Cliente B"],
        mais_de_um_destino=True
    )
    
    print(f"Rota criada: {rota.numero_documento}")
    print(f"Origem: {rota.planta_origem} -> Destino: {rota.cluster}")
    print(f"Tipo: {rota.tipo_transporte} - Valor: R$ {rota.valor_carga}")
    
    # Criar objeto de motorista
    motorista = DadosMotorista(
        id_banco=1,
        placa="ABC1234",
        cpf="123.456.789-00",
        nome="João Silva",
        aceita_bobina=True,
        situacao=1,
        placa_carreta="XYZ5678"
    )
    
    print(f"\nMotorista: {motorista.nome}")
    print(f"Placa: {motorista.placa}")
    print(f"Aceita bobina: {'Sim' if motorista.aceita_bobina else 'Não'}")

def exemplo_debugging():
    """Exemplo de técnicas de debugging."""
    print("\n=== Exemplo de Debugging ===")
    
    # Configurar logging detalhado
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )
    
    driver = None
    window = None
    
    try:
        # Criar gerenciador com logging detalhado
        gerenciador = GerenciadorRotas(driver, window)
        
        # Simular operação com validações
        print("Executando operações com validações...")
        
        # Exemplo de validação de dados
        dados_teste = ["12345", "", "", "2024-01-15", "N", "1", "", "Carreta", "25.5", "TON", "Santa Luzia", "Betim", "MG"]
        
        try:
            rota = gerenciador.criar_objeto_rota(dados_teste)
            print(f"✅ Objeto rota criado: {rota.numero_documento}")
        except Exception as e:
            print(f"❌ Erro ao criar objeto: {e}")
            logging.error(f"Erro na criação do objeto: {e}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        logging.error(f"Erro geral no sistema: {e}")

def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros específicos."""
    print("\n=== Exemplo de Tratamento de Erros ===")
    
    driver = None
    window = None
    
    try:
        gerenciador = GerenciadorRotas(driver, window)
        
        # Simular diferentes cenários de erro
        cenarios = [
            "dados_invalidos",
            "conexao_falhou", 
            "timeout",
            "elemento_nao_encontrado"
        ]
        
        for cenario in cenarios:
            try:
                print(f"Testando cenário: {cenario}")
                
                if cenario == "dados_invalidos":
                    # Simular dados inválidos
                    raise ValueError("Dados de entrada inválidos")
                elif cenario == "conexao_falhou":
                    # Simular falha de conexão
                    raise ConnectionError("Falha na conexão com o portal")
                elif cenario == "timeout":
                    # Simular timeout
                    raise TimeoutError("Timeout na operação")
                elif cenario == "elemento_nao_encontrado":
                    # Simular elemento não encontrado
                    raise NoSuchElementException("Elemento não encontrado na página")
                    
            except ValueError as e:
                print(f"❌ Erro de dados: {e}")
                logging.warning(f"Dados inválidos detectados: {e}")
            except ConnectionError as e:
                print(f"❌ Erro de conexão: {e}")
                logging.error(f"Falha de conexão: {e}")
            except TimeoutError as e:
                print(f"❌ Erro de timeout: {e}")
                logging.warning(f"Timeout detectado: {e}")
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                logging.error(f"Erro não tratado: {e}")
                
    except Exception as e:
        print(f"❌ Erro crítico: {e}")

def main():
    """Função principal com todos os exemplos."""
    print("🚀 Sistema de Rotas Melhorado - Exemplos de Uso")
    print("=" * 50)
    
    # Executar exemplos
    exemplo_uso_basico()
    exemplo_uso_avancado()
    exemplo_criacao_objetos()
    exemplo_debugging()
    exemplo_tratamento_erros()
    
    print("\n" + "=" * 50)
    print("✅ Todos os exemplos executados!")
    print("\n📝 Para usar em produção:")
    print("1. Substitua 'None' pelos objetos reais (driver, window)")
    print("2. Configure o logging conforme necessário")
    print("3. Implemente tratamento de erros específico")
    print("4. Teste em ambiente de desenvolvimento primeiro")

if __name__ == "__main__":
    main()
