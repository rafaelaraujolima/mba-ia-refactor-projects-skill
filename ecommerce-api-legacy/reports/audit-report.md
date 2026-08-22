```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  express (^4.18.2), sqlite3 (^5.1.6, API baseada em callback, banco em memória)
Domain:        Plataforma de cursos (LMS) com fluxo de checkout — compra de curso com cartão de crédito, matrícula (enrollment), registro de pagamento e relatório financeiro administrativo
Architecture:  Multi-arquivo ad hoc, sem camadas — AppManager.js é uma God Class que monta o schema do banco, registra as rotas Express e contém toda a lógica de negócio/acesso a dados inline; utils.js mistura config (com segredos hardcoded) e helpers não relacionados (cache global, "cripto" caseira)
Source files:  3 files analyzed (src/app.js, src/AppManager.js, src/utils.js)
DB tables:     users, courses, enrollments, payments, audit_logs
================================
```

```text
================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
```

```text
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) / Express ^4.18.2
Files:   3 analyzed | ~180 lines of code
```

## Summary
[CRITICAL: 4](#critical) | [HIGH: 7](#high) | [MEDIUM: 3](#medium) | [LOW: 3](#low)

## Findings

### <a id="critical"></a>CRITICAL

#### [CRITICAL] Credenciais e Segredos Hardcoded
File: src/utils.js:1-7
Description: O objeto `config` define `dbUser`, `dbPass`, `paymentGatewayKey` e `smtpUser` como
             strings literais direto no código-fonte, sem nenhuma leitura de `process.env` em
             lugar nenhum do projeto.
Impact: Qualquer pessoa com acesso ao repositório (incluindo histórico de git) tem a chave de
        produção do gateway de pagamento e credenciais de banco/SMTP. Rotacionar essas credenciais
        exige um novo deploy de código em vez de só trocar uma variável de ambiente.
Recommendation: Aplicar o padrão "Extrair segredos hardcoded para config baseada em variáveis de
                ambiente" do refactoring-playbook.md — mover todos os campos de `config` para
                `process.env`, adicionar um `.env.example` com placeholders, e falhar o boot se um
                valor obrigatório estiver ausente.

#### [CRITICAL] Chave de Gateway de Pagamento e Número de Cartão Logados em Texto Puro
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` imprime
             o número completo do cartão de crédito enviado pelo cliente junto com a chave secreta
             do gateway de pagamento, sem nenhum mascaramento.
Impact: Esses dados ficam persistidos em qualquer agregador de log/stdout do processo — um vazamento
        ativo de dado sensível de titular de cartão (PCI) e de uma credencial de produção, pior do
        que apenas tê-los hardcoded, porque agora são escritos repetidamente em texto puro a cada
        checkout.
Recommendation: Remover esse log por completo (ou logar apenas os últimos 4 dígitos do cartão e
                nunca a chave do gateway), como parte da mesma limpeza do padrão #1 do playbook, e
                trocar por um logger estruturado (padrão #13) que nunca recebe segredos como
                argumento.

#### [CRITICAL] God Class / God File
File: src/AppManager.js:1-141
Description: A classe `AppManager` sozinha define a conexão e o schema do banco (`initDb`,
             linhas 10-23), registra todas as rotas HTTP (`setupRoutes`, linha 25), e contém a
             lógica de negócio completa de checkout, relatório financeiro e exclusão de usuário
             como métodos dela mesma — sem nenhuma separação entre model, controller e roteamento.
Impact: Não existe uma unidade testável isoladamente: para testar qualquer regra de negócio é
        preciso subir um app Express inteiro com um banco real. Qualquer mudança em uma entidade
        (ex.: `courses`) arrisca quebrar lógica não relacionada (ex.: `users`) porque tudo vive no
        mesmo arquivo/classe. Alterações simples exigem navegar um arquivo de 141 linhas que
        mistura quatro responsabilidades diferentes, aumentando o custo cognitivo de toda mudança.
Recommendation: Aplicar o padrão "Dividir um God File em Models e Controllers por domínio" do
                refactoring-playbook.md — extrair `models/db.js` (conexão/schema),
                `models/courseModel.js`, `models/userModel.js`, `models/enrollmentModel.js`,
                `models/paymentModel.js`, e controllers/rotas correspondentes por domínio.

#### [CRITICAL] Hashing de Senha Caseiro (Fraco)
File: src/utils.js:17-23
Description: `badCrypto()` implementa uma "criptografia" caseira: repete 10.000 vezes uma
             codificação Base64 do texto puro e concatena os dois primeiros caracteres de cada
             rodada, cortando o resultado para 10 caracteres. Não é um algoritmo de hash real; é
             totalmente reversível (Base64 é uma codificação, não um hash) e usado para armazenar a
             senha do usuário em `src/AppManager.js:68-71`.
Impact: Senhas de usuário ficam armazenadas de forma que pode ser trivialmente revertida, e ainda
        por cima o "hash" caseiro é de comprimento fixo curto (10 chars) — colisões e reversão são
        praticamente garantidas. Isso equivale a armazenar senha em texto puro para fins de
        segurança real.
Recommendation: Aplicar o padrão "Substituir tratamento de senha fraco/texto puro por um hash de
                verdade" do refactoring-playbook.md — trocar `badCrypto` por `bcrypt.hash`/
                `bcrypt.compare`. Linhas de usuário já semeadas com este hash (incluindo o usuário
                seed 'Leonan' em `src/AppManager.js:18`) precisarão de reset de senha, já que o
                valor caseiro não pode ser convertido retroativamente em um hash bcrypt válido.

### <a id="high"></a>HIGH

#### [HIGH] Lógica de Negócio Presa em Route Handler — Checkout
File: src/AppManager.js:28-78
Description: O handler `POST /api/checkout` faz parsing do body, validação, três consultas
             sequenciais ao banco, decisão de criação de usuário, "processamento" de pagamento
             (linha 46), inserção de matrícula, inserção de pagamento, inserção de log de auditoria
             e formatação da resposta — tudo inline dentro da função de rota, sem delegar nada a um
             controller/service/model.
Impact: Nenhuma dessas regras (ex.: "cartão começando com 4 é aprovado") pode ser testada sem
        simular uma requisição HTTP completa contra um banco real; qualquer novo canal de checkout
        (ex.: um job assíncrono) precisaria duplicar toda essa lógica.
Recommendation: Aplicar "Mover lógica de negócio de Controllers/Routes para Models/Services" —
                extrair um `checkoutController.checkout()` que orquestra chamadas a
                `courseModel`, `userModel`, `enrollmentModel` e `paymentModel`, deixando a rota com
                apenas parsing + chamada ao controller + resposta.

#### [HIGH] Lógica de Negócio Presa em Route Handler — Relatório Financeiro
File: src/AppManager.js:80-129
Description: O handler `GET /api/admin/financial-report` monta manualmente uma estrutura de
             relatório por curso, soma receita, e junta dados de três tabelas dentro do próprio
             route handler, incluindo os contadores de pendência (`coursesPending`, `enrPending`)
             usados para saber quando a resposta pode ser enviada.
Impact: A regra de negócio "receita de um curso = soma dos pagamentos PAID de suas matrículas" só
        existe presa a este endpoint HTTP específico — não pode ser reaproveitada por, por exemplo,
        um relatório em CSV ou um job agendado, sem copiar o bloco inteiro.
Recommendation: Mesmo padrão do finding acima — mover o cálculo para um
                `reportService.buildFinancialReport()` (ou método estático no model), deixando a
                rota apenas chamar o service e devolver o JSON.

#### [HIGH] Endpoint Administrativo Sem Autenticação
File: src/AppManager.js:80
Description: `GET /api/admin/financial-report` expõe receita, nomes e e-mails de todos os alunos e
             valores pagos por curso sem nenhum middleware ou checagem de sessão/token antes de
             executar a query.
Impact: Qualquer pessoa na rede que alcance a API consegue ler dados financeiros e pessoais de
        todos os usuários só por saber a URL — não existe superfície "admin" de fato, é uma rota
        pública disfarçada de admin pelo nome do path.
Recommendation: Aplicar "Adicionar autenticação/autorização de verdade" do refactoring-playbook.md
                — emitir um token de verdade (JWT) no login e proteger esta rota com um middleware
                `requireAuth({ role: 'admin' })`.

#### [HIGH] Endpoint Destrutivo Sem Autenticação
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` executa a exclusão do usuário direto do `id` da URL, sem
             nenhuma checagem de autenticação/autorização, e sem confirmar que quem chama tem
             permissão para deletar aquele usuário (ou qualquer usuário).
Impact: Qualquer cliente não autenticado pode apagar qualquer conta de usuário do sistema
        informando um ID sequencial adivinhável.
Recommendation: Mesmo padrão do finding acima — proteger a rota com `requireAuth`, exigindo no
                mínimo que o usuário autenticado seja o dono da conta ou tenha papel admin.

#### [HIGH] Forte Acoplamento / Ausência de Injeção de Dependência
File: src/AppManager.js:5-8; src/utils.js:9,12-15
Description: O construtor de `AppManager` cria sua própria conexão de banco internamente
             (`this.db = new sqlite3.Database(':memory:')`, linha 7) em vez de recebê-la como
             parâmetro; `src/utils.js:9` declara `globalCache = {}` em nível de módulo, mutado
             diretamente por `logAndCache` (linhas 12-15) e importado como estado compartilhado.
Impact: Não é possível instanciar `AppManager` com um banco de teste isolado (ex.: um mock ou uma
        segunda conexão em memória) sem alterar a classe; `globalCache` é um singleton mutável
        global que qualquer módulo futuro pode ler/escrever de forma imprevisível, dificultando
        raciocinar sobre o estado da aplicação.
Recommendation: Aplicar "Substituir estado global mutável por injeção de dependência" — criar a
                conexão uma vez no composition root (`src/app.js`) e passá-la para os models;
                substituir `globalCache` por uma instância de cache passada explicitamente a quem
                precisar dela (ou remover, já que hoje nada a lê — ver finding de código morto).

#### [HIGH] Fluxo Assíncrono Desestruturado — Checkout ("Callback Hell")
File: src/AppManager.js:37-77
Description: O handler de checkout aninha cinco níveis de callbacks (`db.get` → `db.get` →
             `processPaymentAndEnroll` → `db.run` → `db.run` → `db.run`), com tratamento de erro
             inconsistente entre eles (alguns branches checam `err` e retornam 500, o branch final
             do `db.run` de audit log na linha 57 ignora `err` completamente).
Impact: O fluxo de controle é difícil de acompanhar e propenso a bugs de "callback esquecido"; um
        erro não tratado em qualquer nível intermediário deixa a requisição pendurada sem resposta.
Recommendation: Aplicar "Converter pirâmides de callback em async/await" — promisificar o driver
                `sqlite3` (`util.promisify`) ou trocar pelo pacote `sqlite` baseado em Promise (ver
                também o finding de API deprecated abaixo), e reescrever o fluxo com `async/await`
                dentro do controller extraído.

#### [HIGH] Fluxo Assíncrono Desestruturado — Relatório Financeiro ("Callback Hell")
File: src/AppManager.js:83-127
Description: O handler de relatório usa contadores manuais de pendência (`coursesPending`,
             `enrPending`, linhas 86,93,97-98,117-121) para detectar quando todas as operações
             assíncronas paralelas terminaram, em vez de `Promise.all`, com callbacks aninhados em
             até 4 níveis (`db.all` → `db.all` → `db.get` → `db.get`).
Impact: A lógica de "quando enviar a resposta" depende de decrementar contadores manualmente em
        múltiplos pontos — fácil de descalibrar ao adicionar/remover um passo, causando respostas
        nunca enviadas (requisição pendurada) ou enviadas mais de uma vez.
Recommendation: Mesmo padrão do finding acima — trocar os contadores manuais por
                `await Promise.all(courses.map(...))` com o driver promisificado.

### <a id="medium"></a>MEDIUM

#### [MEDIUM] Queries N+1 no Relatório Financeiro
File: src/AppManager.js:83-124
Description: Para cada curso, executa uma query de matrículas (linha 92); para cada matrícula,
             executa uma query de usuário (linha 104) e uma query de pagamento (linha 106) — uma
             cadeia de consultas por item em vez de buscar tudo em lote.
Impact: Com C cursos e E matrículas por curso, o endpoint dispara `1 + C + C*E*2` queries
        separadas — a latência do relatório cresce linearmente com o número de matrículas em vez de
        ser praticamente constante.
Recommendation: Aplicar "Corrigir queries N+1 com uma busca em lote" — buscar todas as matrículas
                com `WHERE course_id IN (...)`, todos os usuários e pagamentos relacionados com
                `WHERE id IN (...)`, e juntar as três coleções em memória por id.

#### [MEDIUM] API Deprecated — Driver sqlite3 em Estilo Callback
File: src/AppManager.js:1-141; package.json:11
Description: O projeto depende de `sqlite3` (^5.1.6) e usa exclusivamente sua API baseada em
             callback (`db.get(..., callback)`, `db.run(..., callback)`, `db.all(...,
             callback)`) em toda a classe, quando o mesmo ecossistema já oferece o pacote `sqlite`
             (wrapper baseado em Promise sobre `sqlite3`) como estilo recomendado atual.
Impact: Força a codebase inteira para o padrão de callback aninhado (ver os dois findings de
        "Callback Hell" acima) em vez de permitir `async/await` direto, e mistura mal com o resto
        do ecossistema Express 4.16+, que já assume handlers assíncronos baseados em Promise.
Recommendation: Aplicar "Substituir APIs deprecated pelo equivalente moderno" — migrar para o
                pacote `sqlite` (ou `util.promisify` sobre o driver atual) como parte da mesma
                refatoração que converte os callbacks em async/await.

#### [MEDIUM] Validação/Tratamento de Erro Inconsistente Entre Rotas
File: src/AppManager.js:35,38,41,48,51,55,64,70,84,95,133-136
Description: Não existe middleware de erro centralizado. Cada handler responde erros de forma
             diferente: texto puro (`res.status(400).send("Bad Request")`, linha 35) em alguns
             pontos, e nenhuma resposta de erro específica em outros (o `db.all` de matrículas na
             linha 92-95 não checa `err` antes de seguir). O caso mais grave é o `DELETE
             /api/users/:id` (linhas 133-136): o callback recebe `err` como parâmetro mas nunca o
             verifica, sempre respondendo 200 com a mensagem "Usuário deletado, mas as matrículas e
             pagamentos ficaram sujos no banco." — inclusive quando a exclusão falha, e mesmo
             quando ela funciona, deixando órfãs as linhas de `enrollments`/`payments`
             referenciando o `user_id` deletado.
Impact: Clientes da API não conseguem tratar erros de forma programática (formas de resposta
        inconsistentes), e o endpoint de exclusão de usuário corrompe silenciosamente a
        integridade referencial do banco por design, sem sequer confirmar que a exclusão de fato
        ocorreu.
Recommendation: Aplicar "Centralizar o tratamento de erro" do refactoring-playbook.md — uma classe
                `AppError` + middleware `app.errorhandler`/`app.use((err, req, res, next) => ...)`
                único; e corrigir a exclusão de usuário para checar `err`, retornar o status
                correto, e (se apagar o usuário for mesmo o comportamento desejado) apagar ou
                reatribuir em cascata as linhas relacionadas em vez de deixá-las órfãs por design.

### <a id="low"></a>LOW

#### [LOW] Nomenclatura Ruim / Números Mágicos
File: src/AppManager.js:29-33; src/utils.js:19,22
Description: O handler de checkout usa `u`, `e`, `p`, `cid`, `cc` para `usuário`, `email`,
             `senha`, `courseId` e `número do cartão` (linhas 29-33). `badCrypto` usa os literais
             soltos `10000` (linha 19) e `0, 2`/`0, 10` (linhas 20,22) sem nenhuma constante
             nomeada explicando o que representam.
Impact: Um leitor precisa inferir o significado de cada variável de uma letra a partir do uso
        posterior em vez do nome; os números mágicos em `badCrypto` não comunicam por que aquelas
        contagens específicas foram escolhidas.
Recommendation: Renomear para `username`, `email`, `password`, `courseId`, `cardNumber` como parte
                da extração do controller de checkout (finding HIGH acima); remover os números
                mágicos junto com a própria função `badCrypto` ao trocá-la por `bcrypt`.

#### [LOW] Logging Orientado a Debug via console.log
File: src/utils.js:13; src/app.js:13
Description: `logAndCache` usa `console.log` como único mecanismo de log operacional (linha 13),
             sem níveis, estrutura ou possibilidade de desativar em produção; o boot da aplicação
             em `src/app.js:13` também loga via `console.log` direto.
Impact: Não há como filtrar/desativar esses logs por ambiente, nem estruturá-los para um agregador
        de log real — em produção eles se misturam com qualquer outra saída de stdout.
Recommendation: Aplicar "Substituir números mágicos/logging via print por constantes e um logger
                de verdade" — introduzir um logger de verdade (ex.: `pino`/`winston`) com níveis, e
                usá-lo tanto no boot quanto em qualquer log operacional restante.

#### [LOW] Código Morto — Cache e Contador de Receita Nunca Lidos
File: src/utils.js:9-15,25; src/AppManager.js:2
Description: `globalCache` (linha 9) só é escrito por `logAndCache` (chamado em
             `src/AppManager.js:59`) e nunca lido em lugar nenhum do projeto. `totalRevenue`
             (linha 10) é exportado e importado em `src/AppManager.js:2`, mas nunca incrementado
             nem lido — o relatório financeiro recalcula a receita do zero em vez de usá-lo.
Impact: Duas peças de estado parecem existir para um propósito (cachear o último checkout,
        acumular receita total) mas nenhuma delas é de fato utilizada — código morto que aumenta a
        superfície da codebase sem entregar nada.
Recommendation: Remover `globalCache`, `logAndCache` e `totalRevenue` por completo se nenhuma
                funcionalidade real depende deles, ou implementar de fato o propósito pretendido
                (ex.: um cache com TTL real) se a intenção era mantê-los.

```text
================================
Total: 17 findings
================================
```

```text
================================
PHASE 3: REFACTORING OUTCOME
================================
```
Applied: concluído nesta sessão

## Findings resolvidos
- [CRITICAL] Credenciais e Segredos Hardcoded — resolvido (movidos para `process.env` via `dotenv`, `config/settings.js` falha no boot se faltar alguma variável, `.env.example` adicionado)
- [CRITICAL] Chave de Gateway de Pagamento e Número de Cartão Logados em Texto Puro — resolvido (log removido; `checkoutController.js` loga apenas curso/usuário, nunca cartão ou chave)
- [CRITICAL] God Class / God File — resolvido (`AppManager.js` eliminado; dividido em `config/db.js`, `models/*`, `controllers/*`, `routes/*`)
- [CRITICAL] Hashing de Senha Caseiro (Fraco) — resolvido (`badCrypto` removido, `bcrypt` em uso; usuário seed 'Leonan' precisará resetar senha em um cenário real, já que o hash antigo não é convertível)
- [HIGH] Lógica de Negócio Presa em Route Handler — Checkout — resolvido (`checkoutController.checkout()`)
- [HIGH] Lógica de Negócio Presa em Route Handler — Relatório Financeiro — resolvido (`reportController.buildFinancialReport()`)
- [HIGH] Endpoint Administrativo Sem Autenticação — resolvido (`GET /api/admin/financial-report` agora exige `requireAuth({ adminOnly: true })`; endpoint novo `POST /api/login` adicionado para emitir o JWT — mudança de contrato necessária, documentada)
- [HIGH] Endpoint Destrutivo Sem Autenticação — resolvido (`DELETE /api/users/:id` exige `requireAuth()`, permite apenas o próprio usuário ou um admin — mudança de contrato necessária, documentada)
- [HIGH] Forte Acoplamento / Ausência de Injeção de Dependência — resolvido (conexão criada uma vez em `app.js` e injetada nos models; `globalCache` removido)
- [HIGH] Fluxo Assíncrono Desestruturado — Checkout — resolvido (driver promisificado em `config/db.js`, controller em `async/await`)
- [HIGH] Fluxo Assíncrono Desestruturado — Relatório Financeiro — resolvido (contadores manuais removidos, substituídos por `Promise.all` + busca em lote)
- [MEDIUM] Queries N+1 no Relatório Financeiro — resolvido (`enrollmentModel.findByCourseIds`, `userModel.findByIds`, `paymentModel.findByEnrollmentIds` em lote; validado manualmente contra os dados semeados)
- [MEDIUM] API Deprecated — Driver sqlite3 em Estilo Callback — resolvido (wrapper promisificado em `config/db.js`; nenhum callback restante)
- [MEDIUM] Validação/Tratamento de Erro Inconsistente Entre Rotas — resolvido (`AppError` + `middlewares/errorHandler.js` centralizado; toda resposta de erro agora é `{ "error": "..." }` — mudança de formato necessária, documentada; `DELETE /api/users/:id` agora checa erro e apaga `enrollments`/`payments` em cascata, sem deixar dados órfãos)
- [LOW] Nomenclatura Ruim / Números Mágicos — resolvido (variáveis renomeadas nos controllers; `badCrypto` e seus números mágicos removidos junto com o finding CRITICAL correspondente)
- [LOW] Logging Orientado a Debug via console.log — resolvido (`utils/logger.js` com níveis, controlado por `LOG_LEVEL`)
- [LOW] Código Morto — Cache e Contador de Receita Nunca Lidos — resolvido (`globalCache`, `logAndCache`, `totalRevenue` removidos por completo junto com `utils.js`)

## Findings parcialmente resolvidos ou adiados
Nenhum — todos os 17 findings da Fase 2 foram resolvidos.

```text
================================
17/17 findings resolved
================================
```
