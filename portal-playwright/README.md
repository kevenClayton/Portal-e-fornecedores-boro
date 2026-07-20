# Portal E-Fornecedores v2

Automação do portal E-Fornecedores com **Playwright** + MySQL.

## Desenvolvimento (Mac/Linux)

```bash
cd portal-playwright
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure DB_*
python run.py
```

## Entregar SÓ o .exe para o cliente (sem .env)

Você está no Mac e o cliente no Windows: o build do `.exe` roda no **GitHub Actions** (Windows na nuvem). A config do banco entra **dentro** do executável — o cliente não vê `.env`.

### 1) Configurar Secrets no GitHub

No repositório: **Settings → Secrets and variables → Actions** e crie:

- `DB_HOST`
- `DB_PORT` (ex.: `3306`)
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `PORTAL_URL` (opcional)
- SMTP_* (opcional)

### 2) Rodar o build

1. Aba **Actions**
2. Workflow **Build Windows EXE**
3. **Run workflow**
4. Informe o `cliente` (ex.: `madeforte`)
5. Baixe o artefato `PortalFornecedores-madeforte.exe`

### 3) Enviar ao cliente

Mande **apenas** o `.exe`.  
Ele precisa ter **Google Chrome** instalado e dar dois cliques. Nada de Python, `.env` ou instalação.

> Igual ao modelo antigo com `config.py` dentro do PyInstaller: a senha fica no binário (dá para extrair com esforço). Não é cofre, mas a experiência do cliente é só o `.exe`.

## Build manual (se tiver um Windows)

```bat
cd portal-playwright
build_windows.bat
```

Isso lê o `.env` local, embute no código e gera `dist\PortalFornecedores.exe`.

## Subir no Portainer

Arquivos prontos:
- `Dockerfile`
- `docker-compose.yml`
- `.env.portainer.example`
- guia: `PORTAINER.md`

Resumo rápido:
1. Portainer → **Stacks → Add stack → Repository**
2. Compose path: `portal-playwright/docker-compose.yml`
3. Env: `DB_*` + `PROXY` (BR se AWS for EUA)
4. Deploy → Start/Stop pelos logs do container `portal-fornecedores`
