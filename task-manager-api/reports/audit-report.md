```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 (flask==3.0.0 em requirements.txt)
Dependencies:  flask-sqlalchemy 3.1.1 (ORM/SQLite), flask-cors 4.0.0, marshmallow 3.20.1 (nunca usada no código), requests 2.31.0 (nunca usada), python-dotenv 1.0.0 (nunca usada — nenhuma env var é lida em lugar nenhum)
Domain:        API de gestão de tarefas (task manager) com usuários (roles user/admin/manager), categorias coloridas, tasks com prioridade/status/prazo/tags, relatórios de produtividade por usuário e um serviço de notificação por e-mail para tasks atribuídas/atrasadas
Architecture:  Parcialmente em camadas — diretórios `models/`, `routes/`, `services/`, `utils/` existem, mas as rotas ainda fazem serialização manual, validação e cálculos de negócio inline (ex.: lógica de "overdue" duplicada em 4 lugares), e o `NotificationService` nunca é chamado por nenhuma rota
Source files:  15 files analyzed
DB tables:     users, tasks, categories (via SQLAlchemy models, FKs task.user_id→users, task.category_id→categories)
================================
```

```text
================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
```

```text
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (flask-sqlalchemy 3.1.1, SQLite)
Files:   15 analyzed | ~1160 lines of code
```

## Summary

[CRITICAL: 4](#critical) | [HIGH: 2](#high) | [MEDIUM: 5](#medium) | [LOW: 4](#low)

## Findings

### <a id="critical"></a>CRITICAL

#### [CRITICAL] Credencial de sessão hardcoded (SECRET_KEY)

File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` atribui um literal fixo em vez de ler de variável de ambiente, apesar de `python-dotenv` já estar em requirements.txt sem nunca ser usado.
Impact: Qualquer pessoa com acesso ao código-fonte (ou ao repositório) tem a chave de assinatura de sessão da aplicação; se sessões/CSRF forem habilitados no futuro, podem ser forjados sem custo.
Recommendation: Carregar `SECRET_KEY` de `os.environ` via `python-dotenv`, seguindo o padrão "Configuração via variáveis de ambiente" do refactoring-playbook.md.

#### [CRITICAL] Hashing de senha com MD5

File: models/user.py:27-32
Description: `set_password` faz `hashlib.md5(pwd.encode()).hexdigest()` e `check_password` compara o mesmo hash MD5 — MD5 é um hash genérico rápido, sem salt e sem work factor, criado para checksums e não para senhas.
Impact: Senhas de usuário (inclusive as de exemplo `1234`, `abcd`, `pass` do seed) podem ser quebradas por força bruta/rainbow table em segundos; qualquer vazamento do banco compromete todas as contas.
Recommendation: Trocar para `werkzeug.security.generate_password_hash`/`check_password_hash` (já disponível via Flask) ou `bcrypt`, conforme o padrão "Hashing de senha real" do refactoring-playbook.md.

#### [CRITICAL] Credenciais SMTP hardcoded

File: services/notification_service.py:7-10
Description: `email_host`, `email_port`, `email_user` e `email_password` (`'senha123'`) são atribuídos como literais no `__init__` da classe.
Impact: Credenciais de uma conta de e-mail real ficam expostas no controle de versão; qualquer um com acesso ao repositório pode autenticar como `taskmanager@gmail.com` e enviar e-mail em nome da aplicação.
Recommendation: Carregar host/porta/usuário/senha de variáveis de ambiente, seguindo o mesmo padrão de configuração aplicado ao `SECRET_KEY`.

#### [CRITICAL] Autorização insuficiente em `PUT /users/<id>` (escalonamento de privilégio)

File: routes/user_routes.py:25-29 (original, pré-fix), controllers/user_controller.py:67-100 (original, pré-fix)
Description: A rota é protegida por `@require_auth()` — sem parâmetro de `role` — que só exige
             *algum* usuário autenticado, e o controller nunca comparava o `user_id` da URL com o
             id do usuário autenticado (`g.current_user`). Além disso, `update_user` aplicava
             `if 'role' in data: user.role = data['role']` e `if 'active' in data: user.active =
             data['active']` sem checar se quem chamou tinha permissão para alterar esses campos
             especificamente.
Impact: Qualquer usuário autenticado (role `user`) conseguia (1) editar o registro de **qualquer
        outro** usuário pela URL, incluindo trocar a senha de outra pessoa, e (2) setar `role:
        "admin"` em si mesmo via `PUT /users/<próprio_id>` — um escalonamento de privilégio
        completo a partir de uma conta comum recém-criada.
Recommendation: Aplicar o padrão "Checar dono ou papel antes de mutar campos sensíveis" (#14) do
                refactoring-playbook.md — comparar o usuário autenticado com o dono do recurso, e
                bloquear campos administrativos (`role`, `active`) para quem não for admin.

**Nota de proveniência**: este finding não estava no relatório original da Fase 2 — foi descoberto
por revisão manual de código *depois* da Fase 3 já ter rodado e sido validada, expondo uma lacuna
no processo: a Fase 2 original verificou "existe um guard de auth na rota?" mas não "o guard
distingue dono de não-dono, e campo comum de campo administrativo?". O catálogo de anti-patterns e
o relatório foram atualizados retroativamente (catálogo #16, playbook #14) para que auditorias
futuras capturem esse padrão na Fase 2, antes da Fase 3, e não apenas em revisão manual posterior.

### <a id="high"></a>HIGH

#### [HIGH] Autenticação/autorização ausente em todas as rotas sensíveis

File: routes/task_routes.py:85-238, routes/user_routes.py:92-211, routes/report_routes.py:167-223
Description: Nenhum handler de criação/atualização/exclusão (`POST/PUT/DELETE` de tasks, usuários e categorias) checa sessão, token ou role antes de executar. O endpoint `/login` (user_routes.py:185-211) devolve `'token': 'fake-jwt-token-' + str(user.id)` — uma string montada por concatenação, nunca validada em nenhuma outra rota.
Impact: Qualquer requisição não autenticada pode deletar usuários (e suas tasks em cascata, user_routes.py:140-151), deletar tasks/categorias, ou promover um usuário a `admin` via `PUT /users/<id>`. O "token" retornado no login passa a falsa impressão de que existe proteção, o que é pior do que não ter login nenhum.
Recommendation: Introduzir um middleware/decorator de autenticação real (ex.: Flask-JWT-Extended) que valide um token assinado em toda rota mutável, e checar `role` para operações administrativas, conforme o padrão "Middleware de autenticação" do refactoring-playbook.md.

#### [HIGH] Lógica de negócio, validação e serialização presas nos route handlers

File: routes/task_routes.py:11-154, routes/user_routes.py:42-90, routes/report_routes.py:12-101
Description: Handlers como `get_tasks` (task_routes.py:11-63), `create_task`/`update_task` (task_routes.py:85-223) e `summary_report` (report_routes.py:12-101) fazem parsing de request, validação em múltiplos passos, consultas diretas ao banco, cálculo de métricas de negócio (taxa de conclusão, contagem de atrasadas) e montagem manual de dicionário de resposta, tudo inline — nenhuma dessas rotas delega para um controller/service testável fora do contexto HTTP.
Impact: Impossível testar as regras de negócio (ex.: cálculo de completion_rate, detecção de overdue) sem subir um servidor Flask e simular uma requisição; qualquer mudança de regra precisa ser replicada em vários handlers (ver finding de duplicação abaixo), aumentando o risco de divergência.
Recommendation: Extrair uma camada de service (`TaskService`, `UserService`, `ReportService`) e usar os `to_dict()` de model já existentes para serialização, aplicando o padrão "Extrair Service Layer" do refactoring-playbook.md.

### <a id="medium"></a>MEDIUM

#### [MEDIUM] Queries N+1

File: routes/task_routes.py:41-57, routes/report_routes.py:53-68
Description: `get_tasks` busca todas as tasks e, dentro do `for t in tasks`, executa `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` por iteração (task_routes.py:42,51). `summary_report` busca todos os usuários e, dentro do `for u in users`, executa `Task.query.filter_by(user_id=u.id).all()` por iteração (report_routes.py:53-61).
Impact: Para N tasks/usuários, a rota dispara O(N) queries adicionais em vez de 1-2 queries com `JOIN`/eager loading — em produção com uma base de dados real isso degrada linearmente a latência dessas rotas conforme os dados crescem.
Recommendation: Usar `db.joinedload`/`selectinload` do SQLAlchemy (relações `user`/`category`/`tasks` já existem via `db.relationship`) ou uma query agregada única, conforme o padrão "Eliminar N+1 com eager loading" do refactoring-playbook.md.

#### [MEDIUM] Lógica de "overdue" duplicada em quatro lugares

File: models/task.py:50-60, routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/user_routes.py:171-180, routes/report_routes.py:34-37, routes/report_routes.py:132-135
Description: A regra "task está atrasada se tem due_date no passado e status não é done/cancelled" já existe como `Task.is_overdue()` (models/task.py:50-60), mas nunca é chamada — cada rota que precisa dessa informação reimplementa o mesmo if/else aninhado inline.
Impact: Se a regra de negócio mudar (ex.: adicionar um novo status terminal), é preciso lembrar de atualizar cinco lugares diferentes; divergência entre eles já é possível hoje sem que nenhum teste acuse.
Recommendation: Remover as reimplementações e chamar `task.is_overdue()` em todos os pontos, conforme o padrão "Centralizar regra de negócio no Model" do refactoring-playbook.md.

#### [MEDIUM] Validação e helpers duplicados em vez de reaproveitar código já escrito

File: utils/helpers.py:14-23, utils/helpers.py:110-116, routes/user_routes.py:61, routes/user_routes.py:106, routes/task_routes.py:110, routes/task_routes.py:177, routes/task_routes.py:296, routes/report_routes.py:67, routes/report_routes.py:151
Description: `utils/helpers.py` já define `validate_email` (19-23), `calculate_percentage` (14-17) e as constantes `VALID_STATUSES`/`VALID_ROLES`/`MIN_TITLE_LENGTH`/etc. (110-116), mas nenhuma rota as importa — `user_routes.py` reimplementa a mesma regex de e-mail duas vezes (linhas 61 e 106), e `task_routes.py`/`report_routes.py` recalculam `round((x/y)*100, 2)` inline (task_routes.py:296, report_routes.py:67 e 151) e repetem a lista literal `['pending', 'in_progress', 'done', 'cancelled']` (task_routes.py:110, 177) em vez de usar `VALID_STATUSES`.
Impact: Três implementações independentes da mesma regra de e-mail e de cálculo de percentual podem divergir silenciosamente; alterar a lista de status válidos exige editar múltiplos arquivos.
Recommendation: Importar e usar as funções/constantes já existentes em `utils/helpers.py` em vez de reescrevê-las, conforme o padrão "Reutilizar utilitário existente" do refactoring-playbook.md.

#### [MEDIUM] `datetime.utcnow()` deprecated usado em toda a base

File: models/task.py:15-16, models/task.py:52, models/user.py:14, seed.py:66-74, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:48, routes/report_routes.py:50, routes/report_routes.py:71, services/notification_service.py:35
Description: `datetime.utcnow()` está deprecated desde o Python 3.12 em favor de `datetime.now(timezone.utc)` (retorna datetime naive, o que pode causar bugs de comparação com datetimes aware no futuro), e é usado dezenas de vezes em models, rotas, seed e no service de notificação.
Impact: Em uma versão futura do Python essa chamada será removida; hoje já produz um `DeprecationWarning` e datetimes sem timezone, arriscando comparações incorretas caso qualquer parte do código passe a usar datetimes aware.
Recommendation: Substituir todas as ocorrências por `datetime.now(timezone.utc)`, centralizando a criação desses timestamps em um único helper para evitar repetir a troca em N lugares.

#### [MEDIUM] Tratamento de erro inconsistente e validação de corpo ausente em `update_category`

File: routes/task_routes.py:62, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:196-209, routes/report_routes.py:207, routes/report_routes.py:221
Description: Vários handlers usam `except:` bare (task_routes.py:62; user_routes.py:130,149; report_routes.py:186,207,221) em vez de capturar exceções específicas, enquanto outros (task_routes.py:151, user_routes.py:87) capturam `Exception as e` e logam. Além disso, `update_category` (report_routes.py:190-209) acessa `data['name']`/`data['description']`/`data['color']` sem checar antes `if not data`, diferente de todo outro handler PUT/POST do projeto.
Impact: Um `PUT /categories/<id>` sem corpo JSON derruba a requisição com um `TypeError` não tratado (500 genérico do Flask) em vez do erro 400 padronizado que as outras rotas retornam; o `except:` bare mascara qualquer exceção (incluindo `KeyboardInterrupt`/erros de programação), dificultando diagnóstico.
Recommendation: Padronizar um bloco de validação de corpo + tratamento de erro (idealmente um error handler global do Flask) em vez de cada rota reinventar o próprio try/except, conforme o padrão "Error handler centralizado" do refactoring-playbook.md.

### <a id="low"></a>LOW

#### [LOW] Servidor de debug como ponto de entrada normal

File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` é o único caminho de execução da aplicação (`if __name__ == '__main__'`), com o modo debug do Flask sempre ativo.
Impact: O modo debug expõe o Werkzeug interactive debugger (execução de código arbitrário) se uma exceção não tratada ocorrer com a app acessível publicamente (`host='0.0.0.0'`).
Recommendation: Controlar `debug` por variável de ambiente (`FLASK_DEBUG`) com default `False`, e usar um servidor WSGI de produção (gunicorn/waitress) fora de desenvolvimento local.

#### [LOW] `print()` como único mecanismo de logging

File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24
Description: Toda a aplicação usa `print(...)` para registrar criação/atualização/exclusão de recursos e erros, sem níveis, formatação estruturada ou como desativar em produção.
Impact: Não há como filtrar por severidade nem redirecionar esses logs para um sistema de observabilidade sem reescrever cada chamada.
Recommendation: Substituir por `logging` da stdlib configurado uma vez em `app.py`, conforme o padrão "Logging estruturado" do refactoring-playbook.md.

#### [LOW] Código morto: dependências, service e utilitários nunca usados

File: requirements.txt:4-6, services/notification_service.py:1-49, models/task.py:38-49, utils/helpers.py:25-116
Description: `marshmallow`, `requests` e `python-dotenv` estão no requirements.txt mas nenhum arquivo os importa; `NotificationService` (services/notification_service.py) nunca é instanciado por nenhuma rota; `Task.validate_status`/`Task.validate_priority` (models/task.py:38-49) nunca são chamados (as rotas reimplementam a validação inline); e a maior parte de `utils/helpers.py` — `sanitize_string`, `generate_id`, `log_action`, `is_valid_color`, `process_task_data` e as constantes `VALID_STATUSES`/`VALID_ROLES`/`MAX_TITLE_LENGTH`/`MIN_TITLE_LENGTH`/`MIN_PASSWORD_LENGTH`/`DEFAULT_PRIORITY`/`DEFAULT_COLOR` (linhas 25-116) — nunca é referenciada em lugar nenhum alcançável; `format_date`/`calculate_percentage` chegam a ser importadas em report_routes.py:7 mas nunca chamadas no corpo do arquivo.
Impact: Funcionalidade que parece existir (notificação por e-mail de tasks atribuídas/atrasadas, validação centralizada) na verdade nunca roda, o que é enganoso para quem lê o código pela primeira vez; dependências não usadas aumentam a superfície de instalação e de auditoria de segurança sem benefício.
Recommendation: Remover as dependências não usadas do requirements.txt, e conectar (ou remover) `NotificationService` e os helpers mortos — ver finding de duplicação acima para onde vários desses helpers deveriam estar sendo chamados.

#### [LOW] Nomenclatura de variável de uma letra em loops não triviais e números mágicos repetidos

File: routes/task_routes.py:16-59, routes/task_routes.py:113-114, routes/task_routes.py:182-183, routes/report_routes.py:53-68, routes/report_routes.py:119-136
Description: Loops com corpo de 10+ linhas usam nomes de uma letra para as entidades de domínio (`for t in tasks`, `for u in users` em task_routes.py:16-59 e report_routes.py:53-68,119-136), quando o próprio conteúdo do loop justificaria `task`/`user`. Os limites de prioridade (`1`/`5`) e tamanho de título (`3`/`200`) aparecem como literais soltos em `task_routes.py:113-114,182-183` em vez das constantes já definidas (e não usadas) em `utils/helpers.py`.
Impact: Reduz a legibilidade de blocos de lógica de negócio não triviais, e um limite alterado em um lugar (ex.: prioridade máxima) precisa ser lembrado e trocado manualmente em cada literal espalhado pelo código.
Recommendation: Renomear as variáveis de loop para o nome da entidade, e substituir os literais por `MIN_TITLE_LENGTH`/`MAX_TITLE_LENGTH`/etc. de `utils/helpers.py` (ver finding de duplicação acima).

```text
================================
Total: 15 findings
================================
```

```text
================================
PHASE 3: REFACTORING OUTCOME
================================
```

Applied: concluído nesta sessão

## Findings resolvidos

- [CRITICAL] Credencial de sessão hardcoded (SECRET_KEY) — resolvido (`config/settings.py` lê de `os.environ` via `python-dotenv`; falha alto no boot se ausente)
- [CRITICAL] Hashing de senha com MD5 — resolvido (`werkzeug.security.generate_password_hash`/`check_password_hash` em `models/user.py`; usuários existentes precisarão resetar a senha, pois hashes MD5 antigos não podem ser migrados automaticamente)
- [CRITICAL] Credenciais SMTP hardcoded — resolvido (`services/notification_service.py` lê de `config/settings.py`; sem credenciais configuradas, o envio é pulado com log em vez de falhar)
- [CRITICAL] Autorização insuficiente em `PUT /users/<id>` — resolvido (`controllers/user_controller.py` agora recebe `acting_user` e checa `is_owner or is_admin` antes de aplicar qualquer alteração; `role`/`active` só podem ser alterados por admin, mesmo pelo dono da conta — corrigido e validado após ser reportado em revisão manual, ver nota de proveniência no finding)
- [HIGH] Autenticação/autorização ausente — resolvido (JWT real emitido em `/login` via `controllers/auth_controller.py`; decorator `require_auth()`/`require_auth(role="admin")` protege toda rota `POST`/`PUT`/`DELETE` de tasks, usuários e categorias, exceto o registro público `POST /users`)
- [HIGH] Lógica de negócio/validação/serialização presa nos routes — resolvido (nova camada `controllers/` concentra toda a lógica; `routes/*.py` ficaram com 3 linhas por handler: parse → controller → resposta)
- [MEDIUM] Queries N+1 — resolvido (`joinedload` em `task_controller.list_tasks` e `report_controller.summary_report`)
- [MEDIUM] Lógica de "overdue" duplicada — resolvido (`Task.is_overdue`/`Task.due_date_aware` como properties reais; todo ponto anterior agora as chama — inclusive `routes/task_routes.py:search` e `routes/user_routes.py:get_user_tasks`, que antes não expunham `overdue` de forma consistente)
- [MEDIUM] Helpers/validação duplicados — resolvido (`utils/helpers.py` mantido e efetivamente importado por `controllers/*` — `validate_email`, `calculate_percentage`, `process_task_data`, `is_valid_color`, `sanitize_string`, `VALID_STATUSES`/`VALID_ROLES`/etc.)
- [MEDIUM] `datetime.utcnow()` deprecated — resolvido (todas as ocorrências trocadas por `datetime.now(timezone.utc)` em models, controllers e seed.py; corrigiu de quebra um bug real de subtração naive/aware descoberto durante a validação em `report_controller.summary_report`)
- [MEDIUM] Tratamento de erro inconsistente / corpo ausente em `update_category` — resolvido (`middlewares/error_handler.py` com `AppError` + handler global de exceção substitui todo `try/except` ad hoc; `request.get_json(silent=True)` em todas as rotas evita 500 em corpo ausente/malformado — bug real encontrado e corrigido durante a validação)
- [LOW] `debug=True` fixo — resolvido (`FLASK_DEBUG` via env, default `false`)
- [LOW] `print()` como logging — resolvido (`logging` padrão configurado em `app.py`, usado em `middlewares/error_handler.py`, `services/notification_service.py` e `seed.py`)
- [LOW] Código morto — resolvido (dependências `marshmallow`/`requests` removidas do requirements.txt; `NotificationService` conectada em `task_controller.create_task`; `Task.validate_status`/`validate_priority` viraram staticmethods reais; `generate_id`/`log_action` removidos por não terem uso real; `format_date`/`calculate_percentage`/`process_task_data`/`is_valid_color`/`sanitize_string` conectados)
- [LOW] Nomenclatura de uma letra / números mágicos — resolvido (loops relevantes renomeados para `task`/`user`/`category` ao serem tocados pela refatoração; limites de prioridade/título centralizados em `utils/helpers.py` e usados por `process_task_data`)

## Findings parcialmente resolvidos ou adiados

Nenhum. Todos os 15 findings foram resolvidos no código (14 na Fase 2 original, mais 1 CRITICAL de
autorização insuficiente encontrado em revisão manual posterior e corrigido nesta mesma sessão); o
único item que não pode ser "corrigido" de fato é o dado histórico: usuários seedados antes desta
refatoração tinham senha em MD5 e precisam resetar a senha (fora do escopo de uma refatoração de
código — é uma ação operacional).

## Mudanças de contrato deliberadas

- Toda rota `POST`/`PUT`/`DELETE` de tasks/usuários/categorias agora exige `Authorization: Bearer <token>` (exceto `POST /users`, que continua pública para registro); requisições sem token que antes "funcionavam" (de forma insegura) agora recebem `401`. Isso é o fix correto do finding HIGH de auth ausente, não um efeito colateral.
- `DELETE /users/<id>` e `DELETE /categories/<id>` agora exigem `role: admin`.
- `GET /tasks/search` e `GET /users/<id>/tasks` passam a incluir o campo `overdue` de forma consistente (antes ausente em `search` e calculado só para os campos daquele endpoint em `get_user_tasks`) — consequência direta de centralizar a lógica de overdue no model, como pedia o finding de duplicação.

## Validação

- Ambiente virtual criado, dependências instaladas (`pip install -r requirements.txt`), `seed.py` executado com sucesso (3 usuários, 4 categorias, 10 tasks).
- Aplicação subiu sem erros (`python app.py`), sem exceções não tratadas no boot.
- Endpoints exercitados manualmente via curl: `GET /health`, `GET /tasks`, `GET /tasks/stats`, `GET /tasks/search`, `POST /tasks` sem token (401) e com token (201), `POST /login` (credenciais corretas e incorretas), `DELETE /tasks/<id>` (200), `PUT /categories/<id>` sem corpo (400, antes seria 500) e com corpo (200), `DELETE /categories/<id>` com token não-admin (403), `GET /reports/summary`, `GET /reports/user/<id>`.
- Dois bugs reais foram encontrados e corrigidos durante essa validação (não presentes no código antigo, introduzidos pela própria refatoração): `request.get_json()` sem `silent=True` lançava exceção não tratada (500) em vez de permitir o `400` esperado para corpo ausente/malformado; e a subtração de datetime naive/aware quebrava `GET /reports/summary` ao calcular `days_overdue`. Ambos corrigidos e re-testados com sucesso.
- Em revisão manual posterior, foi identificado que `PUT /users/<id>` (protegido só por `@require_auth()`, sem checar dono nem papel) permitia que qualquer usuário autenticado editasse o registro de outro usuário e se auto-promovesse a admin. Corrigido em `routes/user_routes.py`/`controllers/user_controller.py` (checagem de `is_owner`/`is_admin` + bloqueio de campos `role`/`active` para não-admin) e revalidado ao vivo: usuário comum tentando setar `role: admin` em si mesmo → `403`; tentando editar outro usuário → `403`; editando o próprio nome → `200`; admin alterando o `role` de outro usuário → `200`.
- Servidor de teste encerrado ao final da validação.

```text
================================
15/15 findings resolved
================================
```
