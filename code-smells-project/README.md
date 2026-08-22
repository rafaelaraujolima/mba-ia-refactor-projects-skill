# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

Pré-requisito: Python 3.10+.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env   # gera um SECRET_KEY real

python run.py
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
"SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")" | Add-Content .env

python run.py
```

> Se `Activate.ps1` for bloqueado por política de execução, rode direto sem ativar o venv:
> `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e
> `.\.venv\Scripts\python.exe run.py`.

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no
primeiro boot, já com produtos e usuários de exemplo (`admin@loja.com` / `admin123`,
`joao@email.com` / `123456`, `maria@email.com` / `senha123`). Para parar o servidor, `Ctrl+C`.

### Testando rapidamente

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@loja.com","senha":"admin123"}'
```

No PowerShell, use `Invoke-RestMethod` no lugar de `curl`:

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod -Method Post http://localhost:5000/login -ContentType "application/json" -Body '{"email":"admin@loja.com","senha":"admin123"}'
```

## Estrutura (pós-refatoração MVC)

Este projeto foi auditado e refatorado pela skill `refactor-arch` (`.claude/skills/refactor-arch/`).
O relatório de auditoria está em [`reports/audit-report.md`](reports/audit-report.md).

```
src/
├── config/settings.py       # variáveis de ambiente (SECRET_KEY, DEBUG, DB_PATH)
├── models/                  # acesso a dados por domínio (produto, usuario, pedido, relatorio)
├── controllers/             # lógica de negócio por domínio + autenticação
├── routes/routes.py         # registro de todas as rotas
├── middlewares/error_handler.py
└── app.py                   # composition root (create_app)
run.py                       # ponto de entrada
```
