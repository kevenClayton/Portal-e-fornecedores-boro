# Portal E-Fornecedores v2

Automação do portal E-Fornecedores da Usiminas usando **Playwright**, com arquitetura modular e banco MySQL reformulado.

## Instalação (desenvolvimento)

```bash
cd portal-playwright
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais
python run.py
```

O robô usa o **Google Chrome instalado** no PC (não precisa de `playwright install` no cliente).

## Gerar .exe para Windows (cliente)

O build precisa ser feito **em um Windows** (PyInstaller não gera `.exe` a partir do Mac).

Para o cliente fica o mais simples possível:
- 1 arquivo `PortalFornecedores.exe`
- 1 arquivo `.env` ao lado
- Google Chrome instalado
- **Não** precisa Python nem Playwright

### No PC Windows de build

```bat
cd portal-playwright
build_windows.bat
```

Saída: `dist\PortalFornecedores.exe`

### O que enviar ao cliente

Pasta exemplo `Portal-MadeForte`:

```
PortalFornecedores.exe
.env
LEIA-ME-CLIENTE.txt
```

Use `.env.cliente.example` como modelo do `.env`.

### No PC do cliente

1. Instalar Google Chrome  
2. Abrir `PortalFornecedores.exe`  
3. Não fechar a janela do Chrome  
4. Parar com `Ctrl+C` no terminal  

## Fluxo

1. Login no portal  
2. Empresa Usiminas (id 85)  
3. `SUCargaProgramada.ascx` → Pesquisar  
4. Filtrar clusters do banco  
5. Detalhes (valor/bobina/destinos) → validar → vincular  
6. Gravar `rotas` / `relatorios` + e-mail  
