# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada para uma estrutura MVC seguindo a skill `refactor-arch`.

## Como rodar

Pré-requisito: Node.js 18+.

### Linux / macOS

```bash
cp .env.example .env
npm install
npm start
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
npm install
npm start
```

> `bcrypt` e `sqlite3` têm dependências nativas. Se o `npm install` reportar scripts de instalação
> pendentes, rode `npm approve-scripts bcrypt sqlite3` seguido de `npm rebuild bcrypt sqlite3`.

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot (usuário admin `leonan@fullcycle.com.br` / senha `123`).

### Testando rapidamente

```bash
curl http://localhost:3000/api/login -X POST -H "Content-Type: application/json" -d '{"email":"leonan@fullcycle.com.br","password":"123"}'
```

No PowerShell, use `Invoke-RestMethod` no lugar de `curl`:

```powershell
Invoke-RestMethod -Method Post http://localhost:3000/api/login -ContentType "application/json" -Body '{"email":"leonan@fullcycle.com.br","password":"123"}'
```

Copie o `token` retornado e use no header `Authorization: Bearer <token>` para acessar
`GET /api/admin/financial-report` e `DELETE /api/users/:id`.

Mais exemplos de requisições estão em `api.http`, incluindo login e uso do token JWT nos endpoints
protegidos.

## Estrutura (pós-refatoração MVC)

Este projeto foi auditado e refatorado pela skill `refactor-arch` (`.claude/skills/refactor-arch/`).
O relatório de auditoria está em [`reports/audit-report.md`](reports/audit-report.md).

```text
src/
├── config/
│   ├── settings.js       # variáveis de ambiente (único lugar que lê segredos)
│   └── db.js             # conexão sqlite promisificada + schema + seed
├── models/                # acesso a dados por domínio (user, course, enrollment, payment, auditLog)
├── controllers/           # lógica de negócio por domínio + autenticação
├── routes/                # registro de todas as rotas
├── middlewares/
│   ├── auth.js            # requireAuth (JWT)
│   └── errorHandler.js    # AppError + tratamento de erro centralizado
├── utils/logger.js
└── app.js                 # composition root
```
