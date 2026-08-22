```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, usuários, pedidos) with an admin panel that can reset
               the database and execute arbitrary SQL
Architecture:  Monolítica — tudo em 4 arquivos (app.py, controllers.py, models.py, database.py),
               sem separação de camadas; models.py age como model + repository para 4 domínios
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```text
================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
```

```text
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code
```

## Summary
[CRITICAL: 5](#critical) | [HIGH: 3](#high) | [MEDIUM: 4](#medium) | [LOW: 3](#low)

## Findings

### <a id="critical"></a>CRITICAL

#### [CRITICAL] God Class / God File
File: models.py:1-315
Description: Um único arquivo contém toda a lógica de acesso a dados (SQL bruto), formatação de
             resposta e regras de negócio para 4 domínios não relacionados — produtos, usuários,
             pedidos e relatórios de vendas.
Impact: Impossível testar cada domínio isoladamente; qualquer alteração em um domínio arrisca
        quebrar os outros três, já que tudo compartilha o mesmo arquivo e as mesmas convenções
        implícitas.
Recommendation: Separar em um model por domínio (playbook #3), cada um responsável apenas pelo
                acesso a dados da própria entidade.

#### [CRITICAL] SQL Injection sistêmica via concatenação de string
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155-166, 174, 187-198,
      206, 219-231, 280, 289-297
Description: Praticamente toda função em models.py monta a query SQL concatenando strings/valores
             recebidos diretamente do usuário (ex.: `"SELECT * FROM produtos WHERE id = " +
             str(id)`, `"...VALUES ('" + nome + "', ...")`), sem nenhum uso de placeholders (`?`).
             Isso atinge todas as operações de produtos, usuários (incluindo login) e pedidos.
Impact: Qualquer parâmetro de rota, query string ou corpo de requisição pode ser usado para alterar
        a query executada — leitura, alteração ou exclusão de dados arbitrários, e em alguns casos
        bypass de autenticação (login_usuario concatena a senha diretamente na query).
Recommendation: Substituir toda concatenação por queries parametrizadas com `?` (playbook #2). É a
                mudança de maior impacto de todo o relatório — corrigi-la remove a maior parte do
                risco do sistema de uma só vez.

#### [CRITICAL] Endpoint de execução de SQL arbitrário, sem autenticação
File: app.py:59-78
Description: A rota `POST /admin/query` recebe uma string SQL livre no corpo da requisição
             (`dados.get("sql", "")`) e a executa diretamente via `cursor.execute(query)`, sem
             nenhuma verificação de autenticação, autorização, ou sanitização.
Impact: Qualquer pessoa com acesso à API pode ler, alterar ou apagar qualquer dado do banco, ou
        executar comandos administrativos do SQLite — é injection por design, não um bug de
        implementação.
Recommendation: Remover completamente o endpoint (playbook #2 e #6) — não existe forma segura de
                manter "executar SQL arbitrário vindo do cliente" como funcionalidade de produto.

#### [CRITICAL] Chave secreta hardcoded e vazada via API
File: app.py:7; controllers.py:285-290
Description: `SECRET_KEY` é definida como literal (`"minha-chave-super-secreta-123"`) em app.py, e
             o mesmo valor literal é devolvido no corpo da resposta do endpoint público
             `GET /health` (`"secret_key": "minha-chave-super-secreta-123"`), junto com
             `"debug": True`.
Impact: A chave usada para assinar sessões/tokens está no código-fonte (logo em qualquer clone do
        repositório) e é ativamente exposta a qualquer chamador do endpoint de health check, sem
        nenhuma autenticação.
Recommendation: Mover para variável de ambiente (playbook #1) e nunca incluir a chave — nem
                qualquer outro segredo — no corpo de uma resposta HTTP.

#### [CRITICAL] Senhas armazenadas e comparadas em texto puro
File: models.py:105-120 (login_usuario), 122-131 (criar_usuario)
Description: `login_usuario` compara a senha recebida diretamente com a coluna `senha` via SQL
             (`WHERE email = '...' AND senha = '...'`), e `criar_usuario` insere a senha recebida
             sem qualquer hashing. A tabela `usuarios` guarda senha em texto puro por design.
Impact: Um vazamento do banco de dados expõe as senhas de todos os usuários diretamente, sem
        precisar quebrar hash nenhum; qualquer pessoa com acesso de leitura ao banco tem as
        credenciais de login de todos os usuários.
Recommendation: Hash com `werkzeug.security.generate_password_hash` / `check_password_hash`
                (playbook #4), migrando o schema para `senha_hash` e forçando reset de senha nos
                usuários existentes (o texto puro atual não pode ser "convertido" em hash com
                segurança).

### <a id="high"></a>HIGH

#### [HIGH] Endpoint administrativo destrutivo sem autenticação
File: app.py:47-57
Description: `POST /admin/reset-db` apaga todas as linhas de `itens_pedido`, `pedidos`,
             `produtos` e `usuarios` sem checar se quem chamou tem qualquer permissão.
Impact: Qualquer chamador pode zerar o banco de dados de produção em uma única requisição.
Recommendation: Adicionar guard de autenticação/autorização de admin (playbook #6) antes de
                qualquer operação destrutiva.

#### [HIGH] Lógica de negócio duplicada entre funções de listagem de pedidos
File: models.py:171-201 (get_pedidos_usuario) vs. models.py:203-233 (get_todos_pedidos)
Description: As duas funções implementam, de forma quase idêntica linha a linha, a mesma lógica de
             montar um pedido com seus itens (incluindo o mesmo padrão de N+1 — ver finding
             separado), diferindo apenas no filtro inicial.
Impact: Qualquer correção de bug ou mudança de formato de resposta precisa ser replicada
        manualmente nos dois lugares — já não estão sincronizadas em termos de manutenção, o que é
        uma fonte comum de regressões silenciosas.
Recommendation: Extrair a lógica de montagem de pedido+itens para uma única função reutilizável
                (playbook #10), parametrizada pelo filtro.

#### [HIGH] Acoplamento forte à conexão global de banco (sem injeção de dependência)
File: database.py:4, 7-11
Description: `db_connection` é um global mutável, e `get_db()` o inicializa lazily na primeira
             chamada; toda função de todo o projeto acessa esse global diretamente via `get_db()`
             em vez de receber a conexão como parâmetro.
Impact: Impossível testar qualquer função de model isoladamente com um banco de teste/mock — o
        estado global é compartilhado entre todas as chamadas e não pode ser substituído.
Recommendation: Criar a conexão uma vez no composition root (`app.py`) e injetá-la explicitamente
                onde for necessária (playbook #7).

### <a id="medium"></a>MEDIUM

#### [MEDIUM] N+1 queries na montagem de pedidos com itens
File: models.py:187-198, 219-231
Description: Para cada pedido, o código executa uma query para buscar os itens, e para cada item,
             mais uma query para buscar o nome do produto — três níveis de query aninhada dentro de
             loops (`cursor` → `cursor2` → `cursor3`).
Impact: Uma listagem com 50 pedidos e 3 itens cada dispara ~150+ queries onde uma única consulta
        com JOIN resolveria o mesmo resultado, degradando a performance conforme o volume de dados
        cresce.
Recommendation: Substituir por uma busca em lote com `WHERE ... IN (...)` ou um JOIN único
                (playbook #9).

#### [MEDIUM] Queries dentro de loop em criar_pedido
File: models.py:139-166
Description: `criar_pedido` executa uma query de produto por item para validar estoque, e depois
             repete a mesma busca de produto por item mais uma vez para pegar o preço, dentro do
             mesmo loop.
Impact: Duplica o número de queries desnecessariamente mesmo antes de considerar o padrão N+1 mais
        amplo — o preço já foi lido na primeira query e poderia ser reaproveitado.
Recommendation: Buscar todos os produtos do pedido em uma única query antes do loop e reutilizar o
                resultado (playbook #9).

#### [MEDIUM] Validação duplicada entre criar_produto e atualizar_produto
File: controllers.py:28-54 vs. controllers.py:72-90
Description: Os mesmos blocos de validação (nome obrigatório, preço obrigatório e não-negativo,
             estoque obrigatório e não-negativo) são reescritos quase identicamente nas duas
             funções.
Impact: Uma regra de validação alterada em um lugar (ex.: tamanho máximo do nome) facilmente fica
        esquecida no outro, gerando comportamento inconsistente entre criar e atualizar.
Recommendation: Extrair a validação para uma função/model compartilhado (playbook #10) chamado por
                ambos os controllers.

#### [MEDIUM] Modo debug ativo e dados de configuração expostos como se fosse produção
File: app.py:8, 88; controllers.py:285-289
Description: `app.config["DEBUG"] = True` e `app.run(..., debug=True)` estão sempre ativos, e o
             endpoint `/health` retorna `"ambiente": "producao"` junto com `"debug": True` e a
             secret key (ver finding CRITICAL relacionado).
Impact: O servidor Werkzeug de debug não é apto para produção (pode expor um console interativo em
        erros não tratados), e o próprio endpoint de health check confirma publicamente que debug
        está ligado.
Recommendation: Controlar debug via variável de ambiente e nunca deixar `True` fixo no código
                (playbook #1); remover completamente esses campos da resposta do `/health`.

### <a id="low"></a>LOW

#### [LOW] Uso de print() como único mecanismo de logging
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 248, 250
Description: Toda mensagem operacional (sucesso, erro, eventos de negócio) é emitida via `print()`
             em vez de um logger configurável.
Impact: Não há níveis de log, não há como desativar/redirecionar em produção, e mensagens de erro
        e de negócio ficam misturadas na mesma saída sem estrutura.
Recommendation: Substituir por um logger padrão (`logging.getLogger`) configurado por ambiente
                (playbook #13).

#### [LOW] Números mágicos nas faixas de desconto do relatório de vendas
File: models.py:256-262
Description: Os limites de faturamento (`10000`, `5000`, `1000`) e os percentuais de desconto
             (`0.1`, `0.05`, `0.02`) estão soltos como literais dentro de uma cadeia de if/elif.
Impact: O significado de negócio de cada faixa não está nomeado em lugar nenhum — alterar uma
        regra de desconto exige entender o código antes de saber o que mudar.
Recommendation: Extrair para uma constante nomeada (ex.: `DISCOUNT_TIERS`) no início do módulo ou
                em `config/` (playbook #13).

#### [LOW] Nomenclatura inconsistente entre português e inglês
File: controllers.py (geral, ex.: linhas 14, 64, 98 — parâmetro `id` em inglês dentro de funções
      com nomes e mensagens em português)
Description: O projeto mistura identificadores em português (`nome`, `preco`, `estoque`,
             `sucesso`) com identificadores em inglês (`id`) sem um padrão consistente.
Impact: Aumenta a carga cognitiva de leitura e revisão de código, e dificulta buscas/refatorações
        automatizadas que assumem um idioma único.
Recommendation: Padronizar um único idioma para identificadores em todo o projeto (mantendo
                mensagens de usuário em português, se for esse o requisito de produto).

## Deprecated API Check
Item #11 do catálogo foi verificado explicitamente. O uso do Flask 3.1.1 neste projeto não depende
de nenhuma API deprecated (sem `before_first_request`, sem imports removidos do Werkzeug, sem
chamadas deprecated de `datetime`) — nenhum finding de API deprecated se aplica a este projeto.

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
- [CRITICAL] God Class / God File — resolvido (models.py dividido em produto_model.py,
  usuario_model.py, pedido_model.py, relatorio_model.py, cada um com seu controller)
- [CRITICAL] SQL Injection sistêmica via concatenação de string — resolvido (todas as queries
  parametrizadas com `?`)
- [CRITICAL] Endpoint de execução de SQL arbitrário, sem autenticação — resolvido (endpoint
  `/admin/query` removido por completo, não apenas protegido)
- [CRITICAL] Chave secreta hardcoded e vazada via API — resolvido (SECRET_KEY via variável de
  ambiente; campos secret_key/debug removidos da resposta de `/health`)
- [CRITICAL] Senhas armazenadas e comparadas em texto puro — resolvido (hash real via
  `werkzeug.security`, coluna `senha_hash`)
- [HIGH] Endpoint administrativo destrutivo sem autenticação — resolvido (`/admin/reset-db` agora
  exige JWT com role `admin`; login passou a emitir um token real)
- [HIGH] Lógica de negócio duplicada entre funções de listagem de pedidos — resolvido (unificado em
  `pedido_model.list_pedidos(usuario_id=None)`)
- [HIGH] Acoplamento forte à conexão global de banco — resolvido (conexão por requisição via
  `flask.g`, criada no composition root em vez de um global mutável)
- [MEDIUM] N+1 queries na montagem de pedidos com itens — resolvido (busca em lote com `IN (...)`)
- [MEDIUM] Queries dentro de loop em criar_pedido — resolvido (produtos buscados em uma única query
  antes do loop)
- [MEDIUM] Validação duplicada entre criar_produto e atualizar_produto — resolvido (extraída para
  `produto_model.validate_payload`, usada pelos dois controllers)
- [MEDIUM] Modo debug ativo e dados de configuração expostos como se fosse produção — resolvido
  (DEBUG controlado por variável de ambiente; campos removidos de `/health`)
- [LOW] Uso de print() como único mecanismo de logging — resolvido (substituído por `logging`)
- [LOW] Números mágicos nas faixas de desconto do relatório de vendas — resolvido (constante
  `DISCOUNT_TIERS` nomeada)

## Findings parcialmente resolvidos ou adiados
- [LOW] Nomenclatura inconsistente entre português e inglês — parcialmente resolvido. Os parâmetros
  de rota ganharam nomes mais claros (`produto_id`, `usuario_id`, `pedido_id` em vez de `id`
  genérico), mas não foi feito um rename completo de todos os identificadores do projeto para um
  único idioma — é uma mudança de alto churn e baixo valor fora do escopo desta refatoração.

```text
================================
14/15 findings resolved
================================
```
