# Portal MadeForte — Como usar (cliente)

Guia rápido do painel e do robô que pega cargas no Portal E-Fornecedores.

---

## 1. Acessar o painel

1. Abra no navegador: **`https://madeforte.reservaai.com.br`**
2. Entre com o usuário e senha que você recebeu.
3. **Troque a senha** no primeiro acesso (perfil / senha), se ainda for a provisória.

Não é necessário instalar nada no PC. O robô roda no servidor.

---

## 2. O que o sistema faz

O robô, com o Chrome no servidor:

1. Entra no Portal E-Fornecedores  
2. Lista as cargas programadas  
3. Compara com **destinos** e **motoristas** cadastrados no painel  
4. Quando bate, tenta **vincular** placa/CPF  

Se o destino do portal não existir no cadastro (com o **mesmo texto** do cluster), a carga é ignorada.

---

## 3. Menu do painel

| Tela | Para quê |
|------|----------|
| **Dashboard** | Visão geral |
| **Motoristas** | Cadastrar / editar motoristas, placa, CPF, tipos de veículo |
| **Ordem / Gerenciar** | Definir prioridade entre motoristas |
| **Parâmetros** | Login do portal, destinos, origens, WhatsApp, valores |
| **Rotas** | Histórico de rotas tratadas |
| **Relatórios** | Consultas / exportação |
| **Robô** | Ligar, desligar e ver logs |

---

## 4. Cadastro essencial (faça antes de esperar vínculo)

### 4.1 Login do portal
Em **Parâmetros** → login do E-Fornecedores: usuário e senha **ativos**.

### 4.2 Destinos
Cadastre o destino **igual ao cluster do portal**, por exemplo:

- Certo: `SLU -> SP-VALENTIM GENTIL`  
- Certo: `MCA -> SP-GUARULHOS`  
- Errado: só `sp-guarulhos` ou um apelido interno diferente  

O robô compara o texto do portal com o que está no banco.

### 4.3 Motoristas
Para cada motorista ativo:

- Nome, CPF, placa  
- Tipos de veículo compatíveis com as cargas  
- Destinos / rotas que ele pode pegar  
- Status **ativo**

### 4.4 Ordem
Em **Gerenciar / Ordem**, coloque primeiro quem deve ter prioridade na vinculação.

### 4.5 WhatsApp
Em **Parâmetros** → seção WhatsApp:

- **Telefones** que recebem alerta quando a carga for **aceita** ou **perdida**
- **Código do estabelecimento** (API ReservaAI)
- **URL pública do painel** (ex.: `https://madeforte.reservaai.com.br`)

O botão “Ver detalhes” do WhatsApp abre a página pública `/carga/{id}` com o resumo da ocorrência.

---

## 5. Ligar e desligar o robô

1. Abra **Robô** no menu.  
2. **Start** — inicia a varredura.  
3. **Stop** — para o robô.  
4. Em **Logs**, confira se está saudável.

Sinais de que está ok:

- `Login realizado`  
- `Navegacao para cargas concluida`  
- `Aguardando 30s para verificar novamente...` (ciclo normal)

Sinais de problema (avise o suporte):

- `Captcha inválido` (várias vezes seguidas)  
- `Login bloqueado` / Sites Confiáveis  
- Container parado / Start não responde  

**Importante:** deixe só **1** robô ligado (mesmo login no portal).

---

## 6. Rotina do dia a dia

1. Manter motoristas e destinos atualizados.  
2. Deixar o robô em **Start** no horário combinado.  
3. Conferir **Rotas** / **Relatórios** se vinculou.  
4. Se não vincular nada: primeiro cheque se o **nome do destino** bate com o portal.

---

## 7. Problemas comuns

| Situação | O que fazer |
|----------|-------------|
| Robô “roda” mas não pega carga | Conferir destinos = clusters do portal; motorista ativo e tipo de veículo |
| Não entra no painel | VPN / IP liberado? URL e porta 8080 corretas? |
| Login do portal falha | Senha do portal em Parâmetros; avisar suporte (proxy/captcha) |
| Quer pausar | **Robô → Stop** |

---

## 8. Suporte

- Contato: _______________________  
- Horário: _______________________  
- Envie, se possível: print da tela **Robô → Logs** e horário do problema  

---

*Documento para o cliente MadeForte — painel + robô Portal E-Fornecedores.*
