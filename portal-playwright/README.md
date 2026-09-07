# Portal E-Fornecedores v2

Automação do portal E-Fornecedores com **Playwright** + MySQL + painel Laravel.

## Desenvolvimento (Mac/Linux) — robô

```bash
cd portal-playwright
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure DB_*
python run.py
```

## Painel admin (Laravel)

O painel fica em `painel/` e usa o **mesmo banco** do robô (`madeforte01`).

```bash
cd portal-playwright/painel
cp .env.example .env
# preencha DB_* , APP_KEY (php artisan key:generate)
# ADMIN_EMAIL / ADMIN_PASSWORD
composer install
php artisan migrate --force
php artisan db:seed --force
npm install && npm run build
php artisan serve
```

Acesse `http://127.0.0.1:8000` → login com `ADMIN_EMAIL` / `ADMIN_PASSWORD`.

Telas: Dashboard, Motoristas, Parâmetros, Rotas, Relatórios, Robô (start/stop/logs).

Controle do robô:
- Na mesma máquina do Docker: `ROBO_USAR_DOCKER_CLI=true`
- Remoto via Portainer: preencha `ROBO_PORTAINER_URL` + `ROBO_PORTAINER_API_KEY` e `ROBO_USAR_DOCKER_CLI=false`

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

## Guia do cliente

Uma página para entregar ao cliente (acesso, cadastro, start/stop, problemas comuns):

→ [`COMO-USAR-CLIENTE.md`](COMO-USAR-CLIENTE.md)

## Subir no Portainer

Arquivos prontos:
- `Dockerfile` (robô)
- `painel/Dockerfile` (painel admin)
- `docker-compose.yml` (robô + painel)
- `.env.portainer.example`
- guia: `PORTAINER.md`

Resumo rápido:
1. Portainer → **Stacks → Add stack → Repository**
2. Compose path: `portal-playwright/docker-compose.yml`
3. Env: `DB_*` + `PROXY` (BR se AWS for EUA) + `PAINEL_APP_KEY` + `ADMIN_*`
4. Deploy → painel em `:8080` · robô no container `portal-fornecedores`
5. No painel: **Robô** → Start/Stop (com `ROBO_USAR_DOCKER_CLI=true` na mesma EC2)

Gere a key do painel:
```bash
cd portal-playwright/painel && php artisan key:generate --show
```
Use o valor em `PAINEL_APP_KEY`.
