# Sistema de Rotas - Portal E-Fornecedores

Sistema automatizado para vinculação de motoristas às rotas no portal E-Fornecedores da Usiminas.

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Google Chrome instalado
- ChromeDriver compatível com sua versão do Chrome

### Passo a Passo

#### 1. Clone ou baixe o projeto
```bash
cd C:\laragon\www\Portal-e-fornecedores-boro
```

#### 2. Execute o setup automático
```bash
python setup.py
```

#### 3. Teste se tudo está funcionando
```bash
python test_setup.py
```

#### 4. Execute o programa principal
```bash
python main.py
```

## 🔧 Instalação Manual (se necessário)

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Ou instalar individualmente
```bash
pip install PySimpleGUI
pip install selenium
pip install pandas
pip install numpy
pip install unidecode
pip install beautifulsoup4
pip install requests
pip install lxml
```

## 📁 Estrutura do Projeto

```
📁 Portal-e-fornecedores-boro/
├── 📄 main.py                    # Programa principal
├── 📄 config.py                  # Configurações
├── 📄 setup.py                   # Script de setup
├── 📄 test_setup.py              # Script de teste
├── 📄 requirements.txt           # Dependências
├── 📄 proxies.txt                # Lista de proxies
├── 📄 README.md                  # Este arquivo
├── 📁 model/
│   └── 📄 db.py                  # Conexão com banco
├── 📄 fazendoLogin.py            # Módulo de login
├── 📄 ListandoRotas2.py          # Módulo de rotas
└── 📄 SistemaRotasMelhorado.py   # Versão melhorada
```

## 🎯 Como Usar

### Execução Básica
1. Abra o terminal na pasta do projeto
2. Execute: `python main.py`
3. Clique em "Buscar e aceitar rotas" na interface

### Execução com Teste
1. Execute: `python test_setup.py`
2. Se todos os testes passarem, execute: `python main.py`

### Teste de Proxy
1. Execute: `python test_proxy.py` para verificar se o proxy está funcionando
2. Se o teste passar, o proxy está configurado corretamente

### Teste de Email
1. Execute: `python test_email.py` para verificar se o envio de emails está funcionando
2. Testa codificação UTF-8 e caracteres especiais

## 🔐 Configuração de Proxy

### Formato do arquivo proxies.txt
```
IP:PORTA:USUARIO:SENHA
198.23.239.134:6540:zkvxokae:o6h76xcdbpx5
207.244.217.165:6712:zkvxokae:o6h76xcdbpx5
```

### Autenticação Automática
- O sistema agora usa uma extensão do Chrome para autenticação automática
- Não é mais necessário digitar usuário e senha manualmente
- A extensão é criada automaticamente e removida ao final da execução

## 🐛 Solução de Problemas

### Erro: "PySimpleGUI não encontrado"
```bash
pip install PySimpleGUI
```

### Erro: "ChromeDriver não encontrado"
- Baixe o ChromeDriver: https://chromedriver.chromium.org/
- Coloque na mesma pasta do projeto

### Erro: "Arquivo proxies.txt não encontrado"
- Verifique se o arquivo existe na pasta raiz
- Se não existir, crie um arquivo vazio ou adicione seus proxies

### Erro: "Proxy pedindo usuário e senha"
- O sistema agora tem autenticação automática de proxy
- Execute: `python test_proxy.py` para testar a configuração
- Verifique se o formato no proxies.txt está correto: `IP:PORTA:USUARIO:SENHA`

### Erro: "'ascii' codec can't encode character"
- Problema de codificação de caracteres especiais (acentos)
- Execute: `python test_email.py` para testar o envio de emails
- O sistema foi corrigido para usar UTF-8 em todos os emails

### Erro: "Conexão com banco falhou"
- Verifique as configurações em `config.py`
- Confirme se o banco está acessível

## 📊 Funcionalidades

- ✅ Login automático no portal
- ✅ Listagem de rotas disponíveis
- ✅ Validação de critérios
- ✅ Vinculação automática de motoristas
- ✅ Interface gráfica amigável
- ✅ Logs detalhados
- ✅ Tratamento de erros

## 🔄 Atualizações

### Versão Melhorada
O arquivo `SistemaRotasMelhorado.py` contém uma versão refatorada com:
- Melhor estrutura de código
- Tratamento de erros robusto
- Logging detalhado
- Facilidade de manutenção

## 🚀 Build do Executável

### **Scripts de Build Disponíveis**

- **`build_exe.py`** - Build básico com PyInstaller
- **`build_exe_robusto.py`** - Build robusto com dependências automáticas
- **`build_exe_tkinter.py`** - Build específico para resolver problemas de tkinter
- **`build_multi_clientes.py`** - Build automatizado para todos os clientes
- **`build_cliente_rapido.py`** - Build rápido para um cliente específico

### **Build Automático (Recomendado)**

```bash
# Build básico
python build_exe.py

# Build robusto (recomendado)
python build_exe_robusto.py

# Build com tkinter (resolve erro ModuleNotFoundError)
python build_exe_tkinter.py

# Build para todos os clientes
python build_multi_clientes.py

# Build rápido para um cliente específico
python build_cliente_rapido.py madeforte
```

### **Build Multi-Clientes**

O script `build_multi_clientes.py` gera automaticamente:

- ✅ **Executável para cada cliente** com configurações específicas
- ✅ **Cores personalizadas** para cada cliente
- ✅ **Configurações de banco** específicas
- ✅ **Launchers .bat** para cada executável
- ✅ **Relatório completo** do build

**Clientes suportados:**
- 🟢 **MadeForte** - Verde (#2b6600)
- 🔵 **Boro** - Azul escuro (#011a41)
- 🟠 **RT Transportes** - Laranja (#fc9917)
- 🔵 **JS Logística** - Azul escuro (#011a41)

### **Build Manual**

```bash
# Instalar PyInstaller
pip install pyinstaller

# Build com configuração otimizada
pyinstaller --clean madeforte.spec
```

### **Debug do Executável**

```bash
# Identificar problemas
python debug_exe.py

# Testar executável
python debug_executavel.py
```

### **Problemas Comuns**

- **Terminal fecha**: Use `executar_[cliente].bat` ou execute via terminal
- **Dependências faltando**: Execute `python build_exe_robusto.py` para build otimizado
- **Erro tkinter**: Execute `python build_exe_tkinter.py` para resolver
- **Arquivos não encontrados**: Verifique se todos os arquivos estão na pasta correta

## 📞 Suporte

Para problemas ou dúvidas:
1. Execute `python test_setup.py` para diagnosticar
2. Verifique os logs gerados
3. Consulte a documentação dos módulos

## 📝 Logs

O sistema gera logs em:
- `relatorio_execucao-info-*.log` - Logs de informação
- Console - Mensagens em tempo real

---

**Desenvolvido para automatizar o processo de vinculação de motoristas às rotas no portal E-Fornecedores.**

