# Guidelines de Arquitetura MVC (Arquitetura Alvo)

Isso define o que "correto" significa para a Fase 3, independente de linguagem. Adapte a
nomenclatura de diretórios/arquivos às convenções da stack, mas as responsabilidades abaixo não
mudam.

## As três camadas

### Models
**Donos de**: forma dos dados e acesso a dados. Um model representa uma entidade de domínio (um
produto, um usuário, uma tarefa) e é o único lugar que sabe como aquela entidade é armazenada e
recuperada.

- Contém: definições de schema/campo, queries restritas àquela entidade (parametrizadas — nunca
  concatenadas em string), e regras de validação intrínsecas à própria entidade (ex.: "priority
  deve ser entre 1 e 5" pertence ao model Task, não espalhado por toda rota que toca priority).
- NÃO contém: conceitos de HTTP (sem objetos `request`/`response`), roteamento, ou conhecimento
  sobre detalhes de armazenamento de outras entidades (um model Product não deveria acessar
  diretamente a tabela de Orders — orquestração entre entidades é trabalho de um Controller).
- Um model por entidade/conceito de domínio, em seu próprio arquivo/módulo
  (`produto_model.py`, `Product.js`), não um arquivo só com uma função por tabela.

### Views / Routes
**Donos de**: mapear uma requisição HTTP (método + path) para uma action de Controller, e moldar
a resposta em nível de transporte (status code, content type). Em uma API (ao contrário de uma
aplicação renderizada no servidor), "View" tipicamente colapsa em "Routes" — isso é esperado e
está tudo bem; chame a camada de `routes/` e não invente um conceito de renderização de HTML que o
projeto não precisa.

- Contém: declarações de rota/path, a ligação requisição → controller, e qualquer preocupação
  puramente de nível de transporte (CORS, negociação de conteúdo).
- NÃO contém: lógica de validação, cálculos de negócio, ou chamadas diretas ao banco de dados. Um
  route handler que faz mais do que "parsear a requisição, chamar o controller, devolver o que ele
  retornar" tem lógica de negócio vazando para dentro dele — esse é o anti-pattern #5 do catálogo,
  e a Fase 3 deveria ter corrigido isso, não preservado em um arquivo com nome diferente.

### Controllers
**Donos de**: orquestrar a lógica de negócio de uma única requisição — chamar um ou mais models,
aplicar regras de negócio que abrangem mais de uma entidade, tratar erros, e decidir o que a
resposta deve conter.

- Contém: a lógica real de "o que acontece quando alguém chama este endpoint": validar input
  (delegando validação intrínseca da entidade ao model), chamar métodos do model, coordenar
  operações de múltiplos passos (como o fluxo de criação de pedido que verifica estoque, cria o
  pedido e atualiza o inventário), e montar o payload da resposta.
- NÃO contém: SQL bruto/construção de query (isso é trabalho do model) ou definição de path de
  rota (isso é trabalho do router).
- Agrupe controllers por domínio, espelhando os models (`produto_controller.py`,
  `pedido_controller.py`), não por verbo HTTP ou por acaso do histórico do arquivo.

## Peças de apoio (presentes no exemplo de estrutura, esperadas de um projeto MVC de verdade)

- **Módulo de config** (`config/settings.py`, `config.js` lendo `process.env`): o *único* lugar de
  onde segredos e valores dependentes de ambiente são lidos. Nada mais deveria ler uma variável de
  ambiente ou guardar um segredo literal diretamente — tudo mais importa do config.
- **Middlewares / tratamento de erro centralizado** (`middlewares/error_handler.py`, middleware de
  erro do Express): um único lugar que captura erros não tratados e molda uma resposta de erro
  consistente, em vez de cada controller reimplementar seu próprio try/except.
- **Composition root / ponto de entrada** (`app.py`, `src/app.js`): conecta tudo — cria a instância
  da aplicação, registra config, monta as rotas, inicia o servidor. Deve ser curto e
  majoritariamente declarativo; se contém lógica de negócio, essa lógica escapou do seu lugar
  correto.

## Escalando a refatoração conforme o ponto de partida do projeto

Nem todo projeto precisa da mesma quantidade de cirurgia. Decida o escopo certo usando o que a
Fase 1 disse sobre a arquitetura atual:

- **Monolítica / arquivo único** (ex.: toda a lógica em 2-4 arquivos sem nenhuma camada): faça uma
  reestruturação completa para o layout abaixo. Não existe estrutura prévia para preservar, então
  construa do zero.
- **Multi-arquivo ad hoc, sem camadas de verdade** (ex.: uma classe "manager" fazendo roteamento +
  lógica + persistência, só dividida em alguns arquivos): ainda é uma reestruturação completa — a
  contagem de arquivos não é o problema, a falta de separação por responsabilidade é. Não se deixe
  enganar pensando "já tem 3 arquivos, então já está parcialmente pronto."
- **Parcialmente em camadas** (diretórios `models/`, `routes/`, `services/` já existentes que na
  maior parte guardam o *tipo* certo de arquivo, mas com lógica ainda vazando entre as fronteiras):
  uma refatoração cirúrgica — mantenha o layout de diretórios existente onde ele já está correto, e
  mova a lógica que está no lugar errado (ex.: lógica de negócio hoje dentro de
  `routes/task_routes.py`) para uma camada de Controller de verdade, sem renomear/mover o que não
  precisa. Introduza uma camada `controllers/` se ainda não existir uma, já que "routes" e
  "services" sozinhos geralmente não são a mesma coisa que uma camada de Controller de verdade —
  verifique se o `services/` existente já cumpre esse papel (orquestração entre models) ou se é só
  um módulo utilitário genérico, e só renomeie para `controllers/` se isso realmente clarear em vez
  de só gerar churn.

Em todo caso, o teste para "isso já é MVC" é o teste de responsabilidade acima, não se os nomes de
diretório batem com algum exemplo ao pé da letra. Um projeto que termina com nomes de pasta
ligeiramente diferentes mas separação de responsabilidades limpa teve sucesso; um com pastas
`models/`, `views/`, `controllers/` que ainda se contaminam entre si não.

## Estrutura alvo de exemplo (adapte os nomes às convenções da stack)

```
src/
├── config/
│   └── settings.py           # toda config derivada de ambiente vive aqui, em nenhum outro lugar
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/                    # ou routes/ — o que soar mais natural para a stack
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/
│   └── error_handler.py
└── app.py                    # composition root
```
