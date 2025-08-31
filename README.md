# Portal e-Fornecedores Automation

Sistema de automação para o portal e-fornecedores.ind.br que busca rotas automaticamente e vincula motoristas às cargas disponíveis.

## 🚀 Nova Versão na Nuvem

Esta é a versão modernizada do sistema, adaptada para rodar na nuvem com as seguintes melhorias:

### ✨ Principais Melhorias

- **🏗️ Arquitetura Moderna**: FastAPI + Celery + PostgreSQL + Redis
- **☁️ Cloud-Ready**: Containerizado com Docker para fácil deploy
- **📊 API REST**: Interface programática para integração
- **🔄 Processamento Assíncrono**: Tarefas em background com Celery
- **📈 Monitoramento**: Logs estruturados e métricas
- **🔒 Segurança**: Variáveis de ambiente e configurações seguras
- **📱 Interface Web**: Dashboard para monitoramento (Flower)

### 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │  Celery Worker  │    │  Celery Beat    │
│   (Port 8000)   │    │   (Background)  │    │  (Scheduler)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Message Q)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Database)    │
                    └─────────────────┘
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI (Python 3.11)
- **Task Queue**: Celery + Redis
- **Database**: MySQL (existente)
- **Web Scraping**: Selenium + Chrome Headless
- **Containerização**: Docker + Docker Compose
- **Monitoramento**: Flower (Celery UI)

## 📋 Pré-requisitos

- Docker e Docker Compose
- Git
- Credenciais do portal e-fornecedores.ind.br

## 🚀 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <repository-url>
cd Portal-e-fornecedores-boro
```

### 2. Configure as variáveis de ambiente

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configurações do Banco MySQL (Produção)
DATABASE_URL=mysql+pymysql://usuario:senha@servidor:3306/boro

# Configurações do Redis
REDIS_URL=redis://redis:6379/0

# Credenciais do Portal (serão carregadas automaticamente do banco)
# Não é necessário configurar - o sistema pega da tabela 'login'
```

### 3. Teste a conexão e credenciais (Opcional)

```bash
# Testar conexão com MySQL
python test_mysql_connection.py

# Testar credenciais do portal
python testar_credenciais.py
```

### 4. Execute com Docker Compose

```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down
```

### 5. Acesse os serviços

- **API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **Monitoramento Celery**: http://localhost:5555

## 📊 Uso da API

### Endpoints Principais

#### Verificar Saúde do Sistema
```bash
curl http://localhost:8000/saude
```

#### Iniciar Processamento
```bash
curl -X POST http://localhost:8000/tarefas/processar-rotas
```

#### Verificar Status da Tarefa
```bash
curl http://localhost:8000/tarefas/{task_id}
```

#### Estatísticas do Sistema
```bash
curl http://localhost:8000/estatisticas
```

#### Listar Rotas
```bash
curl http://localhost:8000/rotas
```

#### Listar Motoristas
```bash
curl http://localhost:8000/motoristas
```

#### Cancelar Tarefa
```bash
curl -X DELETE http://localhost:8000/tarefas/{task_id}
```

## 🔧 Configuração do Banco de Dados

### Banco MySQL Existente

O sistema utiliza o banco MySQL existente com as seguintes tabelas:

- `motoristas`: Cadastro de motoristas
- `destinos`: Destinos disponíveis
- `origens`: Origem das cargas
- `rotas`: Rotas vinculadas com sucesso
- `relatorios`: Relatórios de rotas não vinculadas
- `parametros`: Configurações do sistema
- `login`: Credenciais de acesso

### Nova Tabela

O sistema criará automaticamente a tabela:

- `task_executions`: Execuções das tarefas (criada automaticamente)

### Criar Tabela Manualmente (Opcional)

Se preferir criar a tabela manualmente:

```sql
-- Execute o script create_task_executions.sql no seu banco MySQL
source create_task_executions.sql;
```

## 🔄 Funcionamento

### Processo Automático

1. **Agendamento**: Celery Beat executa a cada 5 minutos (configurável)
2. **Login**: Sistema faz login no portal automaticamente
3. **Busca**: Navega pelas páginas e busca rotas disponíveis
4. **Filtragem**: Aplica critérios de preço e tipo de veículo
5. **Vinculação**: Encontra motorista compatível e vincula
6. **Notificação**: Envia email de confirmação
7. **Registro**: Salva dados no banco de dados

### Critérios de Vinculação

- **Tipo de Veículo**: Carreta ou Truck
- **Valor da Carga**: Dentro dos limites configurados
- **Destino**: Motorista deve atender o destino
- **Origem**: Motorista deve atender a origem
- **Bobina**: Se a carga tem letra B, motorista deve aceitar bobina

## 📈 Monitoramento

### Logs

Os logs são salvos em:
- `logs/portal_automation.log` (dentro do container)
- Console do Docker Compose

### Métricas

Acesse http://localhost:8000/stats para ver:
- Total de rotas processadas
- Rotas vinculadas hoje
- Motoristas ativos
- Status da última execução

### Flower (Monitoramento Celery)

Acesse http://localhost:5555 para:
- Ver tarefas em execução
- Histórico de execuções
- Métricas do Celery

## 🔧 Configurações Avançadas

### Modo Teste

Para testar sem vincular rotas reais:

```env
MODO_TESTE=true
```

### Intervalo de Execução

Alterar frequência de execução:

```env
TASK_INTERVAL_MINUTES=10
```

### Proxy

Para usar proxy:

```env
PROXY_SERVER=http://proxy:port
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de Login**
   - Verifique credenciais no `.env`
   - Confirme se o portal está acessível

2. **Erro de Selenium**
   - Verifique se o Chrome está funcionando no container
   - Aumente timeouts se necessário

3. **Erro de Banco**
   - Verifique se PostgreSQL está rodando
   - Confirme string de conexão

### Logs de Debug

Para logs mais detalhados:

```env
LOG_LEVEL=DEBUG
```

## 🔒 Segurança

- **Credenciais**: Nunca commite o arquivo `.env`
- **Portas**: Configure firewall para portas necessárias
- **SSL**: Use HTTPS em produção
- **Backup**: Faça backup regular do banco PostgreSQL

## 📝 Desenvolvimento

### Estrutura do Projeto

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configurações
│   ├── database.py          # Conexão DB
│   ├── models.py            # Modelos SQLAlchemy
│   ├── celery_app.py        # Configuração Celery
│   ├── tasks.py             # Tarefas Celery
│   └── services/
│       ├── portal_service.py    # Automação do portal
│       ├── database_service.py  # Operações DB
│       └── email_service.py     # Envio de emails
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── init.sql                 # Script inicial DB
└── README.md
```

### Adicionando Novas Funcionalidades

1. **Novos Endpoints**: Adicione em `app/main.py`
2. **Novas Tarefas**: Adicione em `app/tasks.py`
3. **Novos Modelos**: Adicione em `app/models.py`

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Consulte a documentação da API em `/docs`
- Verifique os logs do sistema

## 📄 Licença

Este projeto é privado e confidencial.

