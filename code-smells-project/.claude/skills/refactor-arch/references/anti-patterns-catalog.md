# Catálogo de Anti-Patterns

A severidade segue a escala abaixo (também resumida no template de relatório de auditoria).
Classifique por **impacto**, não pela facilidade do fix:

- **CRITICAL** — quebra o funcionamento correto, expõe dados sensíveis (credenciais hardcoded,
  SQL injection), ou viola completamente a separação de responsabilidades (uma "God Class"
  misturando banco de dados, lógica complexa e roteamento no mesmo lugar).
- **HIGH** — violações fortes de MVC/SOLID que prejudicam seriamente manutenibilidade e
  testabilidade (lógica de negócio pesada presa em controllers, forte acoplamento sem injeção de
  dependência, estado global mutável usado pela aplicação inteira).
- **MEDIUM** — problemas de padronização, duplicação, ou gargalos de performance moderados
  (queries N+1, middleware inadequado, validação ausente nas rotas).
- **LOW** — problemas de legibilidade, nomenclatura, ou números mágicos.

Para cada finding, cite o **arquivo e linha(s) exatos** que você leu — não parafraseie de memória.
Quando o mesmo anti-pattern aparecer em múltiplas funções, liste cada ocorrência (veja no SKILL.md,
Fase 2 passo 2, como evitar duplicação excessiva quando um padrão se repete muitas vezes).

Este catálogo é escrito para ser agnóstico de stack: cada item descreve a *forma* do problema mais
sinais concretos em alguns ecossistemas comuns. Se você estiver olhando para uma stack não listada
explicitamente, aplique a mesma forma — o sinal é o padrão, não a sintaxe exata.

---

## 1. [CRITICAL] Credenciais e Segredos Hardcoded

**Forma**: Segredos — API keys, senhas de banco, chaves de assinatura/sessão, credenciais SMTP —
commitados como strings literais no código-fonte em vez de carregados de variáveis de
ambiente/config em runtime.

**Sinais de detecção**:
- Atribuição de uma string literal a uma variável/chave cujo nome sugere um segredo: `SECRET_KEY`,
  `password`, `db_pass`, `api_key`, `token`, `smtp_password`, etc.
- Objetos/dicts de config construídos a partir de literais em vez de `os.environ`/`process.env`.
- Um segredo ecoado de volta em uma resposta de API (agravando a severidade — agora ele está
  vazando ativamente, não só parado no controle de versão).

**Exemplo de sinal**: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` — um literal
atribuído diretamente, sem nenhuma leitura de variável de ambiente em lugar algum.

---

## 2. [CRITICAL] Injeção de SQL / Query

**Forma**: Input controlado pelo usuário concatenado diretamente em uma string de query (SQL, ou
qualquer linguagem de consulta) em vez de usar queries parametrizadas/prepared statements/query
builders de ORM.

**Sinais de detecção**:
- Concatenação de string (`+`, f-strings, template literals) montando uma query que depois é
  passada para `.execute()`, `.query()`, `db.run()`, `db.get()`, `db.all()`, etc.
- Um endpoint que aceita uma query crua (texto SQL) vinda do corpo/parâmetros da requisição e a
  executa diretamente — isso é injection por design e costuma ser o pior finding sozinho de toda a
  codebase; sinalize como um finding próprio mesmo que o arquivo também tenha injection por
  concatenação comum em outros pontos.

**Exemplo de sinal**: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` —
concatenação de string indo direto para a execução, sem nenhum placeholder à vista.

---

## 3. [CRITICAL] God Class / God File

**Forma**: Um único arquivo ou classe é dono de roteamento, lógica de negócio, acesso a dados e
formatação para múltiplos domínios não relacionados, sem separação nenhuma.

**Sinais de detecção**:
- Um arquivo define a conexão/schema do banco, contém lógica de query para várias entidades não
  relacionadas (ex.: produtos E usuários E pedidos), e é importado diretamente pelos handlers de
  rota — ou seja, está atuando como model, repository e às vezes camada de lógica de negócio ao
  mesmo tempo.
- Uma classe que tanto monta a infraestrutura (conexões de banco, criação de schema) *quanto*
  registra rotas HTTP *quanto* contém a lógica de tratamento dessas rotas, tudo como métodos dela
  mesma.
- Heurística aproximada de tamanho: se um único arquivo mistura ≥2 preocupações de domínio não
  relacionadas e abrange uma fração grande da lógica total do projeto, já é um God File mesmo
  antes de contar linhas — mas um arquivo passando de ~250–300 linhas fazendo isso é um bom sinal
  secundário para citar junto da descrição qualitativa.

**Observação**: um projeto dividido em vários arquivos ainda pode ter uma God Class — ex.: uma
classe "AppManager" ou "Service" que sozinha faz tudo, só que movida para fora de `app.js`. A
quantidade de arquivos não é o mesmo que separação de responsabilidades — verifique qual é a
*responsabilidade* real de cada arquivo.

---

## 4. [CRITICAL] Hashing de Senha Fraco ou Ausente

**Forma**: Senhas armazenadas ou comparadas sem um hash forte de mão única, feito para esse fim
(bcrypt, scrypt, argon2, ou o `generate_password_hash` de algum framework).

**Sinais de detecção**:
- Comparação em texto puro: colunas de senha comparadas com `==`/`===` contra o input do usuário.
- Um hash genérico rápido usado para senhas: MD5, SHA-1, SHA-256 sozinho (sem salt, sem work
  factor) — esses são feitos para velocidade, que é exatamente o oposto do que se quer em
  armazenamento de senha.
- Uma função "cripto" caseira (loop manual montando uma string a partir de `base64`, `substring`,
  etc.) no lugar de uma biblioteca de hashing de verdade — trate qualquer primitiva criptográfica
  caseira como CRITICAL independente de como ela funciona por dentro; o ponto não é auditar o
  algoritmo, é que inventar sua própria criptografia para armazenar credenciais já é o próprio
  defeito.

---

## 5. [HIGH] Lógica de Negócio Presa em Controllers/Routes

**Forma**: Regras de validação, cálculos, orquestração entre múltiplas operações de dados, e
lógica de formatação vivem diretamente dentro da função que trata a requisição HTTP em vez de uma
camada de controller/service/model que poderia ser testada independentemente do HTTP.

**Sinais de detecção**:
- Uma função de route handler cujo corpo faz parsing de requisição E validação em múltiplos
  passos E chamadas diretas ao banco E formatação de resposta, tudo inline, tipicamente 20+ linhas
  sem delegar nada.
- Cálculos de domínio (faixas de desconto, taxa de conclusão, totais) computados inline em um
  route handler em vez de em um método de model/service que pudesse ser testado sem uma
  requisição HTTP.
- Isso se aplica mesmo em projetos "parcialmente em camadas": ter um diretório `routes/` não
  significa que a lógica dentro desses arquivos de rota não está fazendo tudo que um controller e
  um service deveriam fazer — verifique o *conteúdo*, não só o nome do diretório.

---

## 6. [HIGH] Autenticação/Autorização Ausente ou Falsa

**Forma**: Operações sensíveis (ações de admin, exclusões, dados financeiros, execução de
código/query arbitrária) são alcançáveis sem nenhuma checagem de auth, ou a auth existe mas não
verifica nada de fato.

**Sinais de detecção**:
- Endpoints admin/destrutivos (`/admin/*`, endpoints de delete/reset) sem decorator de auth,
  middleware, ou checagem de sessão/token antes de executar.
- Um endpoint de "login" que retorna um token que nunca é de fato validado nas requisições
  seguintes, ou que nem é um token assinado de verdade (ex.: uma string montada concatenando um
  prefixo com o ID do usuário) — isso é pior do que não ter login nenhum, porque parece seguro
  sem ser.

---

## 7. [HIGH] Forte Acoplamento / Sem Injeção de Dependência

**Forma**: Módulos acessam estado global mutável compartilhado (uma conexão de banco, um cache,
um objeto de config) diretamente por import/referência em vez de receber o que precisam como
parâmetro ou via construtor — tornando o código impossível de testar isoladamente ou de trocar
implementações.

**Sinais de detecção**:
- Um global em nível de módulo (`db_connection = None` mutado por uma função getter;
  `globalCache = {}` exportado e mutado a partir de múltiplos lugares) que muitas funções não
  relacionadas acessam diretamente.
- Classes de negócio/service que instanciam suas próprias dependências internamente
  (`new Database()` dentro do construtor) em vez de aceitá-las como argumentos.

---

## 8. [HIGH] Fluxo Assíncrono Desestruturado ("Callback Hell")

**Forma**: Operações assíncronas aninhadas em muitos níveis via callbacks, muitas vezes
coordenadas com contadores manuais em vez de promises/async-await (ou o equivalente estruturado de
concorrência em outros ecossistemas), tornando o tratamento de erro inconsistente e o fluxo de
controle difícil de acompanhar.

**Sinais de detecção**:
- 3+ níveis de callbacks aninhados em uma única função.
- Variáveis "contador pendente" manuais (ex.: `coursesPending--`, `enrPending--`) usadas para
  detectar quando um conjunto de operações assíncronas paralelas terminou, em vez de
  `Promise.all`/`asyncio.gather`/etc.
- Tratamento de erro inconsistente entre os callbacks aninhados — alguns branches checam `err`,
  outros ignoram silenciosamente.

---

## 9. [MEDIUM] Queries N+1

**Forma**: Uma query é executada uma vez por item em um loop em vez de buscar os dados
relacionados em uma única query em lote (`JOIN`, `WHERE id IN (...)`, uma opção de eager-loading
de ORM).

**Sinais de detecção**:
- Uma chamada de banco (`.execute()`, `.query()`, `Model.query.get()`, `db.get()`) dentro de um
  loop `for` ou `.forEach()`/`.map()` sobre uma lista já buscada antes.
- Loops aninhados, cada um disparando sua própria query por iteração (ex.: loop sobre pedidos →
  loop sobre os itens de cada pedido → query separada por item para buscar o nome do produto) —
  sinalize isso como um único finding de N+1 descrevendo a cadeia inteira, citando tanto a
  localização externa quanto a interna.

---

## 10. [MEDIUM] Lógica/Validação Duplicada

**Forma**: A mesma regra de validação ou cálculo é copiada e colada em múltiplas
funções/arquivos em vez de definida uma vez e reutilizada.

**Sinais de detecção**:
- Blocos quase idênticos de lógica condicional (ex.: a mesma checagem aninhada de if/else "isso
  está atrasado", ou a mesma validação de tamanho de campo) aparecendo em 2+ lugares em vez de
  chamar uma função/método compartilhado que já existe para exatamente esse propósito (ou
  deveria).
- Especialmente notável quando uma classe de model já define a lógica como método (ex.:
  `Task.is_overdue()`), mas quem chama reimplementa inline mesmo assim, em vez de chamar o método.

---

## 11. [MEDIUM] APIs Deprecated / Obsoletas

**Forma**: O código depende de uma API, método ou pacote que o próprio ecossistema já
deprecou ou removeu, em favor de um substituto moderno documentado. Esta categoria é obrigatória
de checar mesmo quando nada mais chama atenção.

**Sinais de detecção por stack** (verifique os que se aplicam à stack detectada; esta lista é um
ponto de partida, não é exaustiva — se você souber de outras depreciações para a versão de
framework detectada, inclua-as também):

- **Python/Flask**: `@app.before_first_request` (removido no Flask 2.3+ — use setup no contexto
  da aplicação no startup em vez disso); `datetime.utcnow()` (deprecated desde o Python 3.12 — use
  `datetime.now(timezone.utc)`); `hashlib.md5`/`sha1` usado para qualquer coisa sensível à
  segurança (não é deprecated como função, mas seu uso para senhas/segurança é uma prática
  obsoleta — trate como deprecated-para-este-propósito e faça referência cruzada com o finding
  #4); servidor de debug implícito do `Flask(__name__)` usado como se fosse pronto para produção
  (`app.run(debug=True)` no que é apresentado como o ponto de entrada normal da aplicação).
- **Node.js/Express**: o pacote standalone `body-parser` quando o `express.json()` /
  `express.urlencoded()` embutido já cobre essa necessidade desde o Express 4.16 (uma dependência
  no pacote standalone junto com middleware embutido não usado é o sinal); APIs de estilo callback
  de `sqlite3`/`fs` quando o mesmo pacote/módulo stdlib oferece uma variante baseada em promise
  (`sqlite`, `fs/promises`) que hoje é o estilo recomendado; `new Buffer()` (deprecated em favor de
  `Buffer.from()`/`Buffer.alloc()`).
- **Geral**: qualquer dependência fixada em uma major version cujo changelog/docs a marca como
  EOL ou substituída — registre isso mesmo que você não consiga testar o caminho de upgrade
  sozinho, e recomende o equivalente moderno no campo Recommendation do finding.

---

## 12. [MEDIUM] Validação Ausente no Nível de Rota / Middleware Inadequado

**Forma**: Não existe validação de input centralizada nem middleware de tratamento de erro; cada
handler reinventa seu próprio `try/except`/`try/catch` ad hoc e lógica de status code, com formas
e cobertura inconsistentes entre endpoints.

**Sinais de detecção**:
- Alguns endpoints validam entradas a fundo, outros quase nada, sem nenhuma camada de validação
  compartilhada explicando a inconsistência.
- Respostas de erro com formas diferentes entre endpoints (nomes de chave diferentes para a
  mensagem de erro, status codes diferentes para a mesma categoria de falha) porque cada handler
  construiu a sua própria.

---

## 13. [LOW] Nomenclatura Ruim / Números Mágicos

**Forma**: Identificadores que não comunicam intenção (letras únicas fora de contadores de loop
triviais, abreviações que só o autor original reconheceria), e literais numéricos/de string com
significado de negócio que não está nomeado em lugar nenhum.

**Sinais de detecção**:
- Nomes de parâmetro/variável como `u`, `e`, `p`, `cc` representando `user`, `email`, `password`,
  `creditCard` em corpos de função não triviais.
- Valores de limite (faixas de desconto, limites de tamanho, timeouts) escritos como literais
  soltos em lógica condicional em vez de constantes nomeadas.

---

## 14. [LOW] Logging Orientado a Debug / Config Deixada em "Modo Dev"

**Forma**: `print()`/`console.log()` usados como única forma de logging (sem níveis, sem
estrutura, sem forma de desativar em produção), e/ou flags de debug deixadas ativas no que é
apresentado como o caminho de execução normal da aplicação.

**Sinais de detecção**:
- Chamadas de `print(...)`/`console.log(...)` espalhadas pela lógica de negócio para o que
  claramente deveria ser logging operacional (erros, mudanças de estado) em vez de um módulo de
  logging de verdade.
- `debug=True`/`DEBUG = True` fixado incondicionalmente no ponto de entrada.

---

## 15. [LOW] Código Morto / Imports Não Usados / Funcionalidades Não Conectadas

**Forma**: Imports que nunca são referenciados, ou módulos/classes inteiros construídos mas nunca
chamados de nenhum lugar alcançável — funcionalidade que parece existir mas não roda de verdade.

**Sinais de detecção**:
- Statements de import para módulos cujo nome nunca mais aparece no arquivo.
- Uma classe/service com lógica de verdade (ex.: um service de notificação que envia e-mail) que
  nenhum controller ou rota nunca instancia ou chama — confirme com uma busca no repositório
  inteiro pelo nome antes de sinalizar, já que ela pode estar conectada em um arquivo que você
  ainda não leu.

---

## 16. [CRITICAL] Autorização Insuficiente / Mass Assignment de Campos Sensíveis

**Forma**: Diferente do catálogo #6 (nenhuma autenticação), aqui a autenticação existe e passa —
mas o handler nunca verifica se o usuário autenticado é o **dono** do recurso que está mutando
(ou um admin), e/ou aceita qualquer campo do corpo da requisição — incluindo campos que deveriam
ser exclusivos de admin (`role`, `is_admin`, `active`, saldo, preço em um contexto de
review/pedido) — e os aplica direto no model sem checar quem está pedindo a mudança. Um guard
`@require_auth()` sem parâmetro de role, ou um decorator de "está logado" genérico, cria a falsa
sensação de que a rota está protegida quando na verdade qualquer usuário autenticado pode agir
sobre o recurso de **qualquer outro** usuário.

**Sinais de detecção**:
- Um handler `PUT`/`PATCH` em uma rota com um ID de recurso na URL (`/users/<id>`,
  `/accounts/<id>`) protegido só por um guard de "autenticado" (sem checar role nem posse), onde o
  `id` da URL nunca é comparado ao id do usuário autenticado (`g.current_user.id`,
  `req.user.id`, etc.).
- Atribuição direta de campos do corpo da requisição para o model
  (`if 'role' in data: user.role = data['role']`, ou um loop genérico `for key, value in
  data.items(): setattr(model, key, value)`) sem uma lista explícita de quais campos um usuário
  comum pode alterar em si mesmo versus quais só um admin pode alterar em qualquer registro.
- Testar manualmente: logar como um usuário comum e tentar `PUT` no próprio registro incluindo um
  campo administrativo (`role`, `is_admin`, `verified`) — se funcionar, é este anti-pattern.

**Exemplo real** (encontrado durante a validação da Fase 3, não na auditoria original — prova de
por que vale reexecutar a Fase 2 depois de qualquer mudança em rotas de auth): uma rota
`PUT /users/<id>` protegida com `@require_auth()` (qualquer usuário logado, sem checar role) cujo
controller aplicava `if 'role' in data: user.role = data['role']` sem nunca comparar `user_id`
com o id do usuário autenticado — qualquer usuário conseguia se promover a admin ou trocar a senha
de outra conta.

---

## Usando este catálogo com eficiência

Leia cada arquivo-fonte pelo menos uma vez procurando especificamente por essas dezesseis formas.
É normal um projeto legado pequeno disparar a maioria delas — esse é o ponto do exercício. Resista
à tentação de parar assim que tiver "findings suficientes" para o mínimo exigido — uma auditoria
completa que acaba passando do mínimo é mais útil do que uma que para exatamente nele.

Um cuidado especial vale para o item #16: ele é fácil de não aparecer numa primeira leitura porque
o código *parece* protegido (tem um decorator de auth ali). Para toda rota que edita um recurso
identificado por ID, pergunte explicitamente "o que impede o usuário X de editar o recurso do
usuário Y, ou de setar um campo que só um admin deveria poder setar?" — se a resposta não estiver
escrita em código, é um finding.
