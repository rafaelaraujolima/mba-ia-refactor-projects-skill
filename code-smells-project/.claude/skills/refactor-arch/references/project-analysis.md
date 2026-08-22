# Heurísticas de Análise de Projeto

Objetivo deste arquivo: dar sinais rápidos e confiáveis para identificar linguagem, framework,
dependências, domínio e forma arquitetural atual — sem precisar ler cada linha de cada arquivo
primeiro. Use manifestos e pontos de entrada como seu mapa, e depois leia os arquivos-fonte para
preencher os detalhes.

## 1. Detectando a linguagem

Olhe as extensões de arquivo em toda a árvore (ignorando diretórios de dependência):

| Extensão(ões) | Linguagem |
|---|---|
| `.py` | Python |
| `.js`, `.mjs`, `.cjs` | JavaScript (Node.js se houver `package.json` sem config de bundler de browser) |
| `.ts` | TypeScript |
| `.rb` | Ruby |
| `.go` | Go |
| `.java` | Java |
| `.php` | PHP |
| `.cs` | C# |

Se mais de uma linguagem aparecer, a dominante (por contagem de arquivos e onde fica o ponto de
entrada) é a linguagem principal — mencione as outras como secundárias/de tooling se for relevante.

## 2. Detectando framework e versão

Confira primeiro o manifesto da linguagem detectada — ele é a fonte confiável quando existe:

- **Python**: `requirements.txt`, `pyproject.toml` ou `Pipfile`. Procure por `flask`, `django`,
  `fastapi`, `bottle`, etc. A versão fixada (ex.: `flask==3.1.1` ou `Flask>=3.0`) é a versão do
  framework. Se não houver versão fixada, registre o framework sem uma versão em vez de chutar
  uma.
- **Node.js**: `package.json` → `dependencies`/`devDependencies`. Procure por `express`,
  `fastify`, `koa`, `nestjs`, etc. O `package.json` também dá o ponto de entrada (`main`) e
  qualquer comando `scripts.start`, que diz como subir a aplicação mais tarde na Fase 3.
- **Outras stacks**: `Gemfile` (Ruby/Rails/Sinatra), `go.mod` (Go, verifique `gin`, `echo`,
  stdlib `net/http`), `pom.xml`/`build.gradle` (Java/Spring), `composer.json` (PHP/Laravel).

Se não houver manifesto nenhum, infira o framework a partir dos imports no ponto de entrada
(ex.: `from flask import Flask` ou `require('express')`).

## 3. Detectando a camada de banco de dados

Sinais, mais ou menos em ordem de quão diretamente eles informam:

- Uma dependência no manifesto nomeando um driver de banco ou ORM: `sqlite3`, `psycopg2`,
  `pymysql`, `sqlalchemy`, `flask-sqlalchemy`, `mongoose`, `sequelize`, `prisma`, `typeorm`, `pg`.
  ORMs (SQLAlchemy, Sequelize, Prisma, TypeORM) significam que o projeto já tem o schema definido
  como **classes de model** em algum lugar — isso é um sinal forte de quão preparado o projeto já
  está para uma camada de Models, e algo que vale registrar na linha de arquitetura.
- Strings de conexão cruas ou statements `CREATE TABLE` no código-fonte (comum nos projetos com
  estilo mais legado que você vai encontrar) — leia-as diretamente para pegar nomes exatos de
  tabelas e colunas; isso costuma ser mais confiável do que ler um arquivo de model parcialmente
  desatualizado.
- Um arquivo `.db`/`.sqlite` sentado na raiz do projeto — confirma SQLite e dá um caminho para
  referenciar (e alertar — um arquivo de banco commitado é em si um pequeno code smell que vale um
  finding LOW se parecer conter dados semeados/reais).

Liste os **nomes de tabela ou model** que você encontrar, não só "usa SQLite" — o resumo da Fase 1
precisa da especificidade do estilo `DB tables: produtos, usuarios, pedidos, itens_pedido`.

## 4. Detectando o domínio de negócio

Não descreva o domínio de forma genérica ("uma API CRUD"). Leia os paths de rota, os nomes de
campo de model/tabela, e qualquer docstring ou README no projeto para nomear o que o negócio
realmente faz:

- Os paths de rota entregam os substantivos: `/produtos`, `/pedidos`, `/usuarios` → e-commerce
  (produtos, pedidos, usuários). `/courses`, `/enrollments`, `/payments` → uma plataforma de
  cursos/LMS com fluxo de checkout. `/tasks`, `/categories`, `/reports` → uma ferramenta de gestão
  de tarefas.
- Um README no projeto alvo (se existir) costuma declarar o domínio diretamente — leia-o antes de
  inferir só a partir do código.
- Procure um fluxo distintivo, não só a lista de entidades: existe um fluxo de
  checkout/pagamento? Uma superfície de relatórios/analytics? Uma superfície só-de-admin?
  Mencione isso — "API de E-commerce (produtos, pedidos, usuários)" é bom; "API de E-commerce com
  um painel admin que pode executar SQL arbitrário" é melhor se for verdade, porque já antecipa um
  finding que você vai detalhar na Fase 2.

## 5. Mapeando a arquitetura atual

Classifique o que você vê em uma destas formas, aproximadamente — diga qual, em uma linha, mais
detalhes suficientes para justificar:

- **Monolítica / arquivo único**: um ou dois arquivos contêm roteamento, lógica de negócio e
  acesso a dados juntos. Diga isso claramente: "Monolítica — tudo em 4 arquivos, sem separação de
  camadas."
- **Multi-arquivo ad hoc, sem camadas**: existem múltiplos arquivos (ex.: `app.js`,
  `AppManager.js`, `utils.js`), mas a divisão não é por responsabilidade MVC — uma classe ainda
  faz roteamento + persistência + lógica de negócio junto, só que movida para o próprio arquivo.
  Não confunda "mais de um arquivo" com "em camadas" — verifique se cada arquivo tem uma
  responsabilidade única e coerente.
- **Parcialmente em camadas**: existem diretórios `models/`, `routes/`, `services/`, `utils/` (ou
  similares), então *alguma* separação existe pelo nome — mas verifique se as *rotas* ainda
  contêm lógica de negócio e manipulação direta de dados em vez de delegar para um
  controller/service, e se lógica de validação/formatação está duplicada entre arquivos em vez de
  centralizada. Camadas parciais não são o mesmo que MVC correto — diga isso, e seja específico
  sobre o que ainda está no lugar errado.

## 6. Contando arquivos-fonte

Conte apenas os arquivos que você de fato analisou para arquitetura/qualidade (código-fonte da
aplicação) — exclua `node_modules/`, `venv/`/`.venv/`, `__pycache__/`, `.git/`, lockfiles, e o
diretório `.claude/` da própria skill. Essa contagem precisa bater com a realidade; não estime,
conte de verdade.

## 7. Preenchendo o resumo da Fase 1

Depois de reunir tudo acima, preencha cada campo do bloco de saída da Fase 1 no SKILL.md. Mantenha
cada campo em uma linha. Se um campo genuinamente não se aplicar (ex.: nenhuma dependência
relevante além do próprio framework), diga isso brevemente em vez de omitir a linha.
