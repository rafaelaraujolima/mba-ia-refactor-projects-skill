# task-manager-api

API de Task Manager em Python/Flask. Organizada em camadas MVC (`models/`, `routes/`,
`controllers/`, `config/`, `middlewares/`, `services/`, `utils/`) após a refatoração de
arquitetura descrita em [reports/audit-report.md](reports/audit-report.md).

## Como rodar

### 1. Ambiente virtual e dependências

**Bash (Git Bash / Linux / macOS):**
```bash
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

**PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
# Se der erro de política de execução, rode antes (só nesta sessão do terminal):
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

Copie o `.env.example` para `.env` e ajuste os valores (`SECRET_KEY` é obrigatória — a
aplicação não sobe sem ela):

```bash
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Sim | Chave de assinatura do Flask e dos tokens JWT |
| `FLASK_DEBUG` | Não (default `false`) | Ativa o debugger/reloader do Flask |
| `DATABASE_URI` | Não (default `sqlite:///tasks.db`) | URI do banco |
| `JWT_EXP_HOURS` | Não (default `24`) | Validade do token de login |
| `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASSWORD` | Não | Credenciais de e-mail para `NotificationService`; sem elas, o envio é apenas logado e pulado |

### 3. Popular o banco

```bash
python seed.py
```

Cria 3 usuários, 4 categorias e 10 tasks de exemplo — **rode antes do primeiro boot**, caso
contrário os endpoints vão retornar listas vazias.

| Email | Senha | Role |
|---|---|---|
| joao@email.com | 1234 | admin |
| maria@email.com | abcd | user |
| pedro@email.com | pass | manager |

### 4. Subir a API

```bash
python app.py
```

A aplicação sobe em `http://localhost:5000`.

> Se a porta 5000 já estiver em uso por outro processo (comum quando há vários projetos Flask
> rodando na mesma máquina), a API pode subir normalmente mas suas requisições caírem no
> processo errado, retornando 404 para rotas que deveriam existir. Verifique com
> `netstat -ano | findstr :5000` (PowerShell/cmd) e finalize o processo indevido antes de testar.

## Autenticação

Rotas de leitura (`GET`) são públicas. Rotas de escrita (`POST`/`PUT`/`DELETE`) exigem um token
JWT obtido em `/login`, exceto o registro de usuário (`POST /users`), que continua público.
`DELETE /users/<id>` e `DELETE /categories/<id>` exigem role `admin`.

```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}'

# Usando o token retornado
curl -X POST http://localhost:5000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Nova task","priority":2}'
```
