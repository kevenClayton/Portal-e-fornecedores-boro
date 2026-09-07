# Subir no Portainer

## Opção A — Stack a partir do Git (recomendado)

1. Suba este repositório no GitHub (sem `.env`).
2. No Portainer: **Stacks → Add stack**
3. Escolha **Repository**
4. Preencha:
   - Repository URL: `https://github.com/kevenClayton/Portal-e-fornecedores-boro.git`
   - Compose path: `docker-compose.portainer.yml`
   - Branch: `main`
5. Em **Environment variables**, adicione (modelo em `portal-playwright/.env.portainer.example`):

```
CLIENTE=madeforte
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=madeforte01
PROXY=IP:PORTA:USER:SENHA
HEADLESS=true
```

6. **Deploy the stack**

Build pode demorar na primeira vez (baixa imagem Playwright ~1GB+).

## Opção B — Build local na AWS e só rodar a imagem

No servidor:

```bash
cd portal-playwright
docker compose build
docker compose up -d
```

Depois no Portainer a stack aparece / você controla start-stop.

## Uso no dia a dia

| Ação | Onde |
|------|------|
| Iniciar robô | Painel → **Robô** → Start (ou Portainer → container `portal-fornecedores` → Start) |
| Parar | Painel → **Robô** → Stop |
| Ver status | Painel → Dashboard / Robô → Logs |
| Configurar motoristas/destinos | Painel → Motoristas / Parâmetros |
| Trocar proxy/banco | Edit stack → Environment variables → Update |

O painel sobe no serviço `painel` (porta `PAINEL_PORT`, padrão 8080).
Login inicial: `ADMIN_EMAIL` / `ADMIN_PASSWORD` (seed automático).


## Importante

- `USAR_CHROME_SISTEMA=false` — usa Chromium do Playwright dentro do container
- `HEADLESS=true` — padrão no servidor
- `shm_size: 512mb` — evita crash do Chrome
- **Só 1 réplica** (mesmo login no portal)
- Com AWS nos EUA, configure **PROXY** BR

## Testar se o proxy está ok

Nos logs, o robô deve iniciar sem erro de browser.  
Se quiser validar IP: temporariamente adicione um print/navigate para `https://api.ipify.org` (ou peça para eu incluir um check no boot).
