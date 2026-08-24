# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

## Entrega

### Projeto [code-smells-project](/code-smells-project/)

### 1. Análise manual

Linguagem: Python

Arquitetura: monolítica

Problemas **CRITICAL**:

1. Um único arquivo models.py com toda lógica de acesso ao banco de dados, mesmo com contextos diferentes. Isso causa acoplamento e dependência que, caso alguma alteração em um dos contextos quebrar, pode quebrar todos os outros.
2. SQL Injection via concatenação de string no arquivo models.py. Isso pode fazer com que um usuário mal intencionado execute consultas SQL que não deveria.

Problemas **MEDIUM**:

1. Queries consecutivas ao banco, aninhadas, gerando N+1 chamadas ao banco. O correto seria fazer chamadas em lote.
2. Modo debug ativo, expondo dados sensíveis de configuração.

Problemas **LOW**:

1. Mecanismo de log muito simples, imprimindo apenas no console de forma desestruturada. Fica difícil debugar ou avaliar possíveis problemas.
2. Magic numbers nos relatórios de vendas, dificultando o entendimento na geração dos relatórios.

### Projeto [ecommerce-api-legacy](/ecommerce-api-legacy/)

### 1. Análise manual

Linguagem: JavaScript

Arquitetura: multi-arquivos sem camadas

Problemas **CRITICAL**:

1. Credenciais e segredos hardcoded.
2. God Class AppManager contém toda a lógica de banco de dados.

Problemas **MEDIUM**:

1. Relatórios Financeiros com queries aninhadas, gerando N+1 queries.
2. Tratamento de erro inconsistente entre rotas, não existindo um middleware capaz de tratar isso.

Problemas **LOW**:

1. Nomenclatura e números mágicos no código.
2. Logging orientado via console.log, sem nenhuma estrutura de logs.

### Projeto [task-manager-api](/task-manager-api/)

### Análise manual

Linguagem: Python

Arquitetura: dividida em camadas

Problemas **CRITICAL**:

1. Credenciais hardcoded.
2. Autenticação/Autorização ausente nas rotas que precisam disso.

Problemas **MEDIUM**:

1. Queries aninhadas, gerando N+1 queries.
2. Código duplicado que pode ser reaproveitado através de helpers.

Problemas **LOW**:

1. Mecanismo de log muito simples, imprimindo apenas no console de forma desestruturada.
2. Código morto nunca utilizado.

---

## Construção da Skill

A skill completa foi criada em `code-smells-project/.claude/skills/refactor-arch/` e foi copiada sem
alterações para os outros dois projetos (`ecommerce-api-legacy/.claude/skills/refactor-arch/` e
`task-manager-api/.claude/skills/refactor-arch/`).

### Decisões de design

- **SKILL.md como orquestrador, referências como conhecimento**: o `SKILL.md` só descreve o
  método — três fases, nessa ordem, com um gate de confirmação obrigatório entre a Fase 2 e a
  Fase 3 — e diz *quando* ler cada arquivo de referência, nunca duplicando o conteúdo deles. Isso
  segue revelação progressiva: a Fase 1 só carrega `project-analysis.md`; a Fase 2 carrega
  `anti-patterns-catalog.md` e `audit-report-template.md`; a Fase 3 carrega `mvc-guidelines.md` e
  `refactoring-playbook.md`. Nenhuma fase precisa do conhecimento de outra fase para rodar.
- **Cinco arquivos de referência, um por área de conhecimento exigida**: `project-analysis.md`
  (heurísticas de detecção de linguagem/framework/banco/domínio/arquitetura),
  `anti-patterns-catalog.md` (15 anti-patterns), `audit-report-template.md` (formato do
  relatório, incluindo como o arquivo é construído em três momentos — Fase 1 abre, Fase 2
  continua, Fase 3 completa), `mvc-guidelines.md` (o que é Model/View-Route/Controller de verdade,
  e como escalar a refatoração conforme a maturidade inicial do projeto) e
  `refactoring-playbook.md` (13 padrões de transformação com código antes/depois).
- **Catálogo de anti-patterns** (15 itens, acima do mínimo de 8, com severidade distribuída 4
  CRITICAL / 4 HIGH / 4 MEDIUM / 3 LOW): incluí exatamente os padrões que apareceram nos três
  projetos durante a análise manual — segredos hardcoded, SQL injection, God Class, hash de senha
  fraco (CRITICAL); lógica de negócio presa em controllers/routes, autenticação ausente/falsa,
  acoplamento forte sem DI, callback hell (HIGH); N+1, lógica duplicada, **APIs deprecated**
  (obrigatório pelo enunciado — cobre `datetime.utcnow()`, `before_first_request`, driver
  `sqlite3` em estilo callback vs. o pacote `sqlite` baseado em Promise, `body-parser` vs.
  `express.json()` embutido), validação/middleware inadequado (MEDIUM); nomenclatura/números
  mágicos, logging via print/console.log, código morto (LOW). Cada item tem "sinais de detecção"
  concretos (ex.: "query dentro de um loop `for`"), não descrições vagas.
- **Playbook de refatoração** (13 padrões, acima do mínimo de 8): um padrão por família de
  anti-pattern do catálogo, cada um com exemplo antes/depois em Python **e** em Node quando fazia
  sentido (ex.: parametrização de query, conversão de callback para async/await), para que a Fase
  3 sempre tenha um exemplo de código na linguagem certa.

### Como garanti que a skill é agnóstica de tecnologia

- Nada no `SKILL.md` ou nos arquivos de referência assume Python ou Node como stack padrão — a
  descrição da skill foi revisada explicitamente para não fixar em "backend" nem em nenhuma
  linguagem específica (ver histórico de iteração abaixo).
- `project-analysis.md` detecta a stack a partir de manifestos (`requirements.txt`/`package.json`)
  e do ponto de entrada, nunca assumindo qual vai aparecer.
- `anti-patterns-catalog.md` descreve cada anti-pattern pela **forma** do problema (ex.: "query
  dentro de um loop"), com sinais de detecção por stack como exemplos, não como lista exaustiva —
  a instrução explícita é "se você estiver olhando para uma stack não listada, aplique a mesma
  forma".
- `mvc-guidelines.md` tem uma seção dedicada ("Escalando a refatoração conforme o ponto de
  partida") justamente porque um monolito de 4 arquivos (projeto 1), uma God Class Node (projeto
  2) e um projeto já parcialmente em camadas (projeto 3) precisam de quantidades muito diferentes
  de análise e correção — a skill não aplica o mesmo template estrutural nos três, ela decide o escopo pela
  maturidade que a Fase 1 encontrou.
- **Prova empírica**: a mesma cópia da skill (SKILL.md + referências, sem nenhuma alteração de
  conteúdo) rodou com sucesso em Python/Flask 3.1.1 monolítico, Node/Express com callbacks, e
  Python/Flask 3.0.0 parcialmente organizado — ver seção Resultados.

### Desafios encontrados

- **Relatório salvo como bloco de código gigante**: a primeira versão do `audit-report-template.md`
  envolvia o relatório inteiro em um único bloco ` ``` `, o que desativava headings, links e
  anchors — o arquivo `.md` renderizava como texto pré-formatado sem nenhuma navegação. Corrigido
  reescrevendo a regra: só os banners decorativos (`====...====`) ficam em mini blocos de código;
  Summary, Findings e cada severidade usam headings Markdown reais, o que também foi necessário
  para as anchors (`#critical`, `#high` etc.) funcionarem.
- **Linha de `====` virando heading Setext por acidente**: um banner `====` colado direto abaixo
  de uma linha de texto, fora de um bloco de código, é interpretado pelo Markdown como sublinhado
  de heading (sintaxe Setext) — os banners "PHASE 1"/"PHASE 2" viravam H1 duplicados sem eu ter
  pedido isso. Resolvido isolando cada banner em seu próprio mini bloco de código.
- **O relatório de auditoria terminava com uma pergunta em aberto**: a primeira versão salvava a
  pergunta de confirmação ("Proceed with refactoring (Phase 3)? [y/n]") dentro do arquivo — um
  problema porque, revisado semanas depois, o artefato parece uma pergunta nunca respondida mesmo
  que a Fase 3 já tenha rodado. Resolvido tratando essa pergunta como parte da conversa ao vivo,
  nunca do arquivo salvo, e fazendo a Fase 3 **anexar** um resumo real do que foi resolvido ao
  mesmo arquivo.
- **Quanto refatorar em um projeto já parcialmente organizado**: aplicar a mesma reestruturação
  completa do projeto 1 (monolito) no projeto 3 (que já tinha `models/`/`routes/`/`services/`)
  teria sido um trabalho desnecessário. A skill precisou de uma regra explícita para diferenciar
  "criar a estrutura do zero" de "corrigir violações no lugar".
- **Bugs que só apareceram na validação, não na auditoria**: durante a Fase 3 do projeto 3, a
  correção do `datetime.utcnow()` deprecated introduziu uma comparação naive/aware que quebrava
  `GET /reports/summary`, e `request.get_json()` sem `silent=True` lançava exceção em corpo
  ausente. Nenhum dos dois aparecia até de fato subir o servidor e testar os endpoints com
  `curl` — reforçou por que a Fase 3 exige validação real (boot + endpoints), não só "o código
  parece certo".

---

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Arquivos | Findings | CRITICAL | HIGH | MEDIUM | LOW | Resolvidos na Fase 3 |
|---|---|---|---|---|---|---|---|---|
| [code-smells-project](/code-smells-project/reports/audit-report.md) | Python/Flask 3.1.1 | 4 (~784 LOC) | 15 | 5 | 3 | 4 | 3 | 14/15 (1 LOW parcial — nomenclatura pt/en) |
| [ecommerce-api-legacy](/ecommerce-api-legacy/reports/audit-report.md) | Node/Express ^4.18.2 | 3 (~180 LOC) | 17 | 4 | 7 | 3 | 3 | 17/17 |
| [task-manager-api](/task-manager-api/reports/audit-report.md) | Python/Flask 3.0.0 | 15 (~1160 LOC) | 14 | 3 | 2 | 5 | 4 | 14/14 |

Os três projetos batem o critério de aceite (≥5 findings, com pelo menos 1 CRITICAL/HIGH, nos
3/3 projetos) com folga — a auditoria mais "enxuta" (task-manager-api) ainda encontrou 14
findings, quase 3x o mínimo.

### Comparação antes/depois da estrutura

**code-smells-project** (monolito → MVC completo):
```
Antes                          Depois
app.py                         run.py
controllers.py                 src/
models.py                      ├── config/settings.py
database.py                    ├── models/ (produto, usuario, pedido, relatorio)
                                ├── controllers/ (+ auth_controller com JWT)
                                ├── routes/routes.py
                                └── middlewares/error_handler.py
```

**ecommerce-api-legacy** (God Class → MVC completo):
```
Antes                          Depois
src/app.js                     src/app.js (composition root)
src/AppManager.js (God Class)  ├── config/ (settings.js, db.js)
src/utils.js                   ├── models/ (user, course, enrollment, payment, auditLog)
                                ├── controllers/ (auth, checkout, report, user)
                                ├── routes/ (index + 4 arquivos por domínio)
                                ├── middlewares/errorHandler.js
                                └── utils/logger.js
```

**task-manager-api** (parcialmente organizado → camadas corrigidas):
```
Antes                          Depois
app.py, database.py, seed.py   app.py, database.py, seed.py (mantidos)
models/ (já existia)           models/ (mantido, métodos passaram a ser chamados)
routes/ (lógica de negócio     routes/ (agora só parse → controller → resposta)
  inline nos handlers)         controllers/ (NOVO — concentra toda a lógica)
services/ (nunca conectado)    services/ (NotificationService agora é chamada)
utils/ (definido mas não       utils/ (agora efetivamente importado pelos controllers)
  usado)
```

O projeto 3 confirma que a skill se adapta: manteve os diretórios que já faziam sentido e só
adicionou o que faltava (`controllers/`), em vez de reconstruir tudo do zero como fez nos
projetos 1 e 2.

### Checklist de validação

**Projeto 1 — code-smells-project**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce: produtos, usuários, pedidos)
- [x] Número de arquivos analisados condiz com a realidade (4)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (15)
- [x] Detecção de APIs deprecated incluída (verificada explicitamente; nenhuma encontrada nesta stack)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro (run.py)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

**Projeto 2 — ecommerce-api-legacy**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express ^4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS com checkout, matrícula, pagamento)
- [x] Número de arquivos analisados condiz com a realidade (3)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (17)
- [x] Detecção de APIs deprecated incluída (driver sqlite3 em estilo callback)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro (src/app.js)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

**Projeto 3 — task-manager-api**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0)
- [x] Domínio da aplicação descrito corretamente (Task Manager: tasks, categorias, relatórios)
- [x] Número de arquivos analisados condiz com a realidade (15)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (14)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow())
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (models/routes/services já existiam; controllers/ adicionado)
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados (mantidos + métodos passaram a ser usados)
- [x] Views/Routes separadas para roteamento (lógica de negócio removida das rotas)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro (app.py)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

### Logs das aplicações rodando após a refatoração

**code-smells-project:**
```
$ .venv/Scripts/python.exe run.py
2026-08-22 12:19:25 INFO src.models.db: Banco de dados semeado com dados iniciais
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'src.app'
 * Debug mode: off

$ curl http://localhost:5000/health
{"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}

$ curl -X POST http://localhost:5000/admin/reset-db          # sem token
HTTP 401
$ curl -X POST http://localhost:5000/admin/query              # endpoint removido
HTTP 404
```

**ecommerce-api-legacy:**
```
$ node src/app.js
[INFO] Database connected and seeded (in-memory)
[INFO] LMS API rodando na porta 3000

$ curl -X POST http://localhost:3000/api/login -d '{"email":"leonan@fullcycle.com.br","password":"123"}'
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

$ curl -X POST http://localhost:3000/api/checkout -d '{"usr":"Novo Aluno","eml":"novo@teste.com","pwd":"...","c_id":2,"card":"4111111111111111"}'
{"msg":"Sucesso","enrollment_id":2}

$ curl http://localhost:3000/api/admin/financial-report       # sem token
HTTP 401
$ curl http://localhost:3000/api/admin/financial-report -H "Authorization: Bearer <token>"
[{"course":"Clean Architecture","revenue":997,"students":[...]},{"course":"Docker","revenue":497,...}]
```

**task-manager-api:**
```
$ .venv/Scripts/python.exe app.py
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000

$ python seed.py
Seed concluído com sucesso! 3 usuários, 4 categorias, 10 tasks

$ curl -X POST http://localhost:5000/tasks -d '{"title":"Testar refatoracao"}'  # sem token
HTTP 401
$ curl -X POST http://localhost:5000/login -d '{"email":"joao@email.com","password":"1234"}'
{"message":"Login realizado com sucesso","token":"eyJhbGciOiJIUzI1NiIs...","user":{...,"role":"admin"}}
$ curl -X POST http://localhost:5000/tasks -H "Authorization: Bearer <token>" -d '{"title":"Testar refatoracao"}'
{"id":11,"title":"Testar refatoracao","status":"pending","priority":3,...}
```

### Observações sobre como a skill se comportou em stacks diferentes

- **Mesma skill, zero alteração de conteúdo, três stacks**: o `SKILL.md` e os 5 arquivos de
  referência copiados para `ecommerce-api-legacy` e `task-manager-api` são idênticos aos de
  `code-smells-project` — só o caminho da cópia muda. Isso valida na prática o requisito de
  agnosticismo de tecnologia.
- **Node vs. Python muda o vocabulário dos findings, não o método**: no projeto Node, os findings
  específicos da stack foram callback hell e o driver `sqlite3` deprecated (conceitos que não
  existem nos projetos Python); nos projetos Flask, apareceram `datetime.utcnow()` deprecated e
  hashing com `hashlib.md5`. O catálogo cobriu os dois porque descreve a *forma* do problema, não
  a sintaxe exata.
- **Maturidade inicial muda o volume de HIGH vs. a distribuição geral**: `ecommerce-api-legacy`
  (God Class + callback hell) concentrou 7 findings HIGH — mais que os outros dois combinados —
  porque uma única classe fazendo tudo gera muita superfície de violação de responsabilidade única
  de uma vez. `task-manager-api`, já parcialmente organizado, teve a menor contagem total (14) mas
  ainda assim mais MEDIUM (5) que os outros — duplicação e falta de reaproveitamento de código que
  já existia no projeto, não falta de estrutura.
- **A Fase 3 se adaptou de verdade ao ponto de partida**: no projeto 3 a skill preservou
  `models/`, `routes/`, `services/`, `utils/` existentes e só adicionou `controllers/`, em vez de
  reescrever a árvore inteira como fez nos projetos 1 e 2 — confirmando que a regra de "escalar a
  refatoração" em `mvc-guidelines.md` funcionou na prática, não só na teoria.

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado e configurado (`claude
  --version` funcionando).
- Python 3.10+ (projetos 1 e 3).
- Node.js 18+ (projeto 2).

### Rodando a skill em cada projeto

A skill já está copiada dentro de cada um dos três projetos, em
`<projeto>/.claude/skills/refactor-arch/`. Para invocá-la:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Ou, dentro de uma sessão interativa do Claude Code já aberta em um desses diretórios, basta digitar
`/refactor-arch`. A skill roda a Fase 1 (análise) e a Fase 2 (auditoria) automaticamente, salva
`reports/audit-report.md`, e **pausa esperando confirmação explícita** ("Proceed with refactoring
(Phase 3)? [y/n]") antes de tocar em qualquer arquivo do projeto.

### Rodando cada aplicação já refatorada

Instruções detalhadas de setup (venv, `.env`, dependências) estão no `README.md` de cada projeto:
[code-smells-project](/code-smells-project/README.md#como-rodar),
[ecommerce-api-legacy](/ecommerce-api-legacy/README.md),
[task-manager-api](/task-manager-api/README.md). Resumo:

```bash
# Projetos Python (1 e 3)
python -m venv .venv
source .venv/bin/activate        # Linux/macOS — no Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py                    # ou python app.py, conforme o projeto

# Projeto Node (2)
npm install
npm start
```

### Como validar que a refatoração funcionou

1. **Boot sem erros**: suba a aplicação e confirme que não há exceção não tratada no log de
   startup (ver seção "Logs" em Resultados acima para o output esperado de cada projeto).
2. **Endpoint público básico**: `curl http://localhost:<porta>/health` (ou `/`) deve responder
   `200`.
3. **Fluxo de autenticação**: fazer login com uma credencial seedada (ver README de cada projeto)
   deve devolver um JWT real; usar esse token em um endpoint protegido deve funcionar, e omiti-lo
   deve devolver `401`.
4. **Comparar contra o relatório**: cada finding CRITICAL/HIGH do `reports/audit-report.md`
   correspondente tem uma entrada na seção `REFACTORING OUTCOME` do mesmo arquivo, dizendo
   exatamente como foi resolvido — é possível conferir cada um manualmente lendo o código apontado
   ali.

