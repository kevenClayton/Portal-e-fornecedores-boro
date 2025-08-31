#!/bin/bash

# Script de Deploy - Portal e-Fornecedores Automation
# Este script automatiza o processo de instalação e configuração

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} Portal e-Fornecedores Automation${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar se Docker está instalado
check_docker() {
    print_message "Verificando se Docker está instalado..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    print_message "Docker e Docker Compose encontrados!"
}

# Configurar arquivo de ambiente
setup_env() {
    print_message "Configurando arquivo de ambiente..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_message "Arquivo .env criado a partir do exemplo"
            print_warning "IMPORTANTE: Edite o arquivo .env com suas credenciais reais!"
        else
            print_error "Arquivo env.example não encontrado!"
            exit 1
        fi
    else
        print_message "Arquivo .env já existe"
    fi
}

# Verificar credenciais
check_credentials() {
    print_message "Verificando configurações..."
    
    if [ -f .env ]; then
        source .env
        
        if [ -z "$PORTAL_USERNAME" ] || [ "$PORTAL_USERNAME" = "seu_usuario" ]; then
            print_warning "Credenciais do portal não configuradas no .env"
            print_warning "Por favor, edite o arquivo .env com suas credenciais reais"
        fi
        
        if [ -z "$PORTAL_PASSWORD" ] || [ "$PORTAL_PASSWORD" = "sua_senha" ]; then
            print_warning "Senha do portal não configurada no .env"
            print_warning "Por favor, edite o arquivo .env com sua senha real"
        fi
    fi
}

# Construir e iniciar containers
start_services() {
    print_message "Construindo e iniciando serviços..."
    
    # Parar containers existentes
    docker-compose down 2>/dev/null || true
    
    # Construir imagens
    print_message "Construindo imagens Docker..."
    docker-compose build
    
    # Iniciar serviços
    print_message "Iniciando serviços..."
    docker-compose up -d
    
    # Aguardar serviços ficarem prontos
    print_message "Aguardando serviços ficarem prontos..."
    sleep 30
}

# Verificar saúde dos serviços
check_health() {
    print_message "Verificando saúde dos serviços..."
    
    # Verificar API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_message "✅ API está funcionando"
    else
        print_error "❌ API não está respondendo"
        return 1
    fi
    
    # Verificar PostgreSQL
    if docker-compose exec -T postgres pg_isready -U portal_user > /dev/null 2>&1; then
        print_message "✅ PostgreSQL está funcionando"
    else
        print_error "❌ PostgreSQL não está respondendo"
        return 1
    fi
    
    # Verificar Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_message "✅ Redis está funcionando"
    else
        print_error "❌ Redis não está respondendo"
        return 1
    fi
}

# Migrar dados (opcional)
migrate_data() {
    print_message "Deseja migrar dados do sistema antigo? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Iniciando migração de dados..."
        
        # Verificar se o script de migração existe
        if [ -f migrate_mysql_to_postgres.py ]; then
            # Instalar dependências necessárias
            pip install mysql-connector-python psycopg2-binary
            
            # Executar migração
            python migrate_mysql_to_postgres.py
            
            if [ $? -eq 0 ]; then
                print_message "✅ Migração concluída com sucesso!"
            else
                print_error "❌ Erro durante a migração"
            fi
        else
            print_error "Script de migração não encontrado!"
        fi
    else
        print_message "Migração pulada"
    fi
}

# Mostrar informações finais
show_info() {
    print_message "Deploy concluído com sucesso!"
    echo ""
    echo -e "${BLUE}=== URLs de Acesso ===${NC}"
    echo -e "API: ${GREEN}http://localhost:8000${NC}"
    echo -e "Documentação: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "Monitoramento: ${GREEN}http://localhost:5555${NC}"
    echo ""
    echo -e "${BLUE}=== Comandos Úteis ===${NC}"
    echo -e "Ver logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "Parar serviços: ${YELLOW}docker-compose down${NC}"
    echo -e "Reiniciar: ${YELLOW}docker-compose restart${NC}"
    echo ""
    echo -e "${BLUE}=== Próximos Passos ===${NC}"
    echo "1. Configure suas credenciais no arquivo .env"
    echo "2. Acesse http://localhost:8000/docs para testar a API"
    echo "3. Configure o agendamento das tarefas se necessário"
    echo ""
}

# Função principal
main() {
    print_header
    
    print_message "Iniciando deploy do Portal e-Fornecedores Automation..."
    
    # Verificações
    check_docker
    setup_env
    check_credentials
    
    # Deploy
    start_services
    
    # Verificações pós-deploy
    if check_health; then
        print_message "Todos os serviços estão funcionando!"
        
        # Migração opcional
        migrate_data
        
        # Informações finais
        show_info
    else
        print_error "Alguns serviços não estão funcionando corretamente"
        print_message "Verifique os logs com: docker-compose logs"
        exit 1
    fi
}

# Executar função principal
main "$@"
