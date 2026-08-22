# Template do Relatório de Auditoria

Use exatamente esta estrutura para `reports/audit-report.md`. O arquivo é construído em três
momentos diferentes da execução da skill — a Fase 1 abre o arquivo, a Fase 2 continua nele, e a
Fase 3 o completa — mas é sempre o **mesmo arquivo único**, nunca três arquivos separados. Mantenha
os cabeçalhos de seção e os rótulos de campo ao pé da letra (em inglês, como no exemplo abaixo — é
o padrão adotado por esta skill); preencha o conteúdo em português.

**Importante sobre formatação**: o arquivo salvo é Markdown de verdade, não um bloco de código
gigante. Só os banners decorativos (`====...====`, no estilo saída de CLI, incluindo o prefixo
`PHASE N:` de cada um) ficam dentro de um mini bloco de código — eles são só visuais, ninguém
precisa clicar neles. Todo o resto (campos como `Project:`/`Stack:`/`Files:`, Summary, Findings,
cada severidade, cada finding) usa headings Markdown reais (`##`, `###`, `####`) ou texto solto
fora do bloco de código. Isso importa por dois motivos: (1) uma linha de `====` ou `----` logo
abaixo de uma linha de texto, fora de um bloco de código, é interpretada pelo Markdown como
sublinhado de heading Setext — ou seja, os banners "quebram" e viram headings gigantes e
duplicados se não estiverem dentro de um bloco de código; e (2) headings reais são o que faz as
anchors (`#critical`, `#high`, etc.) funcionarem de verdade em qualquer visualizador de Markdown
(GitHub, VS Code) — link e anchor só funcionam em Markdown ao vivo, nunca dentro de um bloco de
código.

## Fase 1 abre o arquivo

Ao final da Fase 1 (ver SKILL.md), **crie** `reports/audit-report.md` com este bloco — o mesmo
resumo que você imprime na conversa:

````markdown
```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão, se conhecida>
Dependencies:  <dependências relevantes, separadas por vírgula>
Domain:        <uma linha descrevendo o que a aplicação faz, em termos de negócio>
Architecture:  <forma arquitetural atual, uma linha>
Source files:  <N> files analyzed
DB tables:     <nomes de tabelas/models>
================================
```
````

Esse bloco fica inteiro dentro do mini bloco de código (nenhum campo aqui precisa de link/anchor,
então não há necessidade de tirá-lo do bloco de código como acontece na Fase 2).

## Fase 2 continua no mesmo arquivo

Ao final da Fase 2, **acrescente** ao mesmo arquivo (não crie um segundo arquivo) o relatório de
auditoria completo:

````markdown
```text
================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
```

```text
Project: <nome do diretório do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<LOC> lines of code
```

## Summary
[CRITICAL: <n>](#critical) | [HIGH: <n>](#high) | [MEDIUM: <n>](#medium) | [LOW: <n>](#low)

## Findings

### <a id="critical"></a>CRITICAL

#### [CRITICAL] <Nome do anti-pattern>
File: <caminho>:<linha ou intervalo de linhas>
Description: <o que o código de fato faz, em termos concretos — não "má prática", mas o mecanismo
             específico, ex.: "Concatena o parâmetro de rota `id` diretamente em uma string SQL
             passada para cursor.execute()">
Impact: <o que de fato dá errado por causa disso — uma consequência concreta, não um clichê>
Recommendation: <o fix específico, referenciando o padrão correspondente do
                refactoring-playbook.md pelo nome>

#### [CRITICAL] <Próximo finding CRITICAL...>
...

### <a id="high"></a>HIGH

#### [HIGH] <Nome do anti-pattern>
...

### <a id="medium"></a>MEDIUM

#### [MEDIUM] <Nome do anti-pattern>
...

### <a id="low"></a>LOW

#### [LOW] <Nome do anti-pattern>
...

```text
================================
Total: <N> findings
================================
```
````

Note que só a linha do título (`PHASE 2: ARCHITECTURE AUDIT REPORT`) carrega o prefixo de fase; o
banner de fechamento (`Total: <N> findings`) continua sem prefixo, exatamente como no exemplo
acima.

### O que vai para o arquivo vs. o que vai só para a conversa

O que está descrito acima (Fase 1 + Fase 2) é exatamente o que deve estar **salvo** em
`reports/audit-report.md` neste ponto da execução, terminando no mini banner `Total: <N>
findings`. A pergunta de confirmação —

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

— é impressa **depois**, na conversa, mas não faz parte do arquivo salvo. Ela é um prompt para a
interação ao vivo, não conteúdo de um relatório; deixá-la gravada no arquivo faz o artefato parecer
uma pergunta em aberto, mesmo depois que a Fase 3 já rodou e respondeu essa pergunta há muito
tempo. Se o usuário reabrir `audit-report.md` semanas depois, ele deve encontrar um relatório
completo, não uma pergunta congelada no meio do processo.

## Fase 3 completa o arquivo

Quando a Fase 3 terminar (com sucesso ou parcialmente), **anexe** ao final do mesmo
`reports/audit-report.md` — não crie um arquivo separado — uma seção assim (mesma regra de
formatação: banner `====` com prefixo `PHASE 3:` em mini bloco de código, resto em Markdown real):

````markdown
```text
================================
PHASE 3: REFACTORING OUTCOME
================================
```
Applied: <data/hora ou apenas "concluído nesta sessão">

## Findings resolvidos
- [CRITICAL] <nome do finding> — resolvido (<breve nota de como, ex.: "queries parametrizadas">)
- [HIGH] <nome do finding> — resolvido
...

## Findings parcialmente resolvidos ou adiados
- [LOW] <nome do finding> — <o que foi feito e o que ficou de fora, e por quê>

```text
================================
<N>/<M> findings resolved
================================
```
````

Isso transforma `audit-report.md` num registro único e completo, escrito em três momentos: o que
foi analisado (Fase 1), o que foi encontrado (Fase 2), e o que de fato aconteceu com cada finding
(Fase 3) — nunca arquivos separados nem um arquivo que termina em uma pergunta sem resposta
visível.

## Regras para preenchimento

- **O arquivo é construído em três momentos, sempre o mesmo arquivo**: a Fase 1 cria
  `reports/audit-report.md` com o banner `PHASE 1: PROJECT ANALYSIS`; a Fase 2 acrescenta o bloco
  `PHASE 2: ARCHITECTURE AUDIT REPORT`; a Fase 3 acrescenta `PHASE 3: REFACTORING OUTCOME`. Nunca
  pule a Fase 1 — mesmo em uma execução onde tudo parece óbvio, o arquivo salvo precisa registrar
  o que foi analisado, não só o que foi encontrado.
- **Banners decorativos em mini blocos de código, o resto em Markdown real**: ver a seção
  "Importante sobre formatação" acima. Nunca envolva o relatório inteiro (ou qualquer trecho que
  contenha headings, links ou listas) em um único bloco de código — isso desativa headings, links
  e anchors, fazendo o arquivo inteiro renderizar como texto pré-formatado sem nenhuma navegação.
- **Agrupamento por severidade**: com relatórios que costumam passar de 10-15 findings, uma lista
  plana fica difícil de escanear. Agrupe os findings sob um heading `### <a id="..."></a>
  SEVERIDADE` (CRITICAL, HIGH, MEDIUM, LOW, nessa ordem), e só inclua a seção de uma severidade
  que tenha pelo menos um finding — não imprima um heading "MEDIUM" vazio se não houver nenhum
  finding MEDIUM.
- **Anchors por seção**: o heading de cada severidade carrega uma anchor HTML embutida (`<a
  id="critical"></a>`, `<a id="high"></a>`, `<a id="medium"></a>`, `<a id="low"></a>`) logo antes
  do texto da severidade, e a linha de Summary linka cada contagem para a anchor correspondente
  (`[CRITICAL: <n>](#critical)`), para navegar direto para a seção a partir do resumo em
  relatórios longos. Se uma severidade não tem nenhum finding (e portanto não tem seção nem anchor
  no relatório), deixe a contagem dela em texto plano no Summary em vez de um link quebrado — só
  linke severidades que de fato têm uma seção.
- **Ordenação**: os findings devem aparecer CRITICAL primeiro, depois HIGH, depois MEDIUM, depois
  LOW (a ordem das seções já garante isso). Dentro da mesma seção/severidade, ordene por caminho de
  arquivo para facilitar a leitura.
- **Precisão de arquivo:linha**: todo finding precisa de uma localização exata. Uma linha
  defeituosa isolada recebe `arquivo.py:42`. Um problema estrutural que abrange um intervalo
  recebe `arquivo.py:1-350`. Nunca escreva um finding sem localização — se você não consegue
  apontar onde ele está, você não verificou de fato que ele existe.
- **Um finding por ocorrência concreta, com bom senso**: se o mesmo anti-pattern ocorre em cinco
  funções diferentes de um arquivo, isso são cinco findings (ou um finding só listando cinco
  localizações, se forem casos de uma linha trivialmente parecidos — veja no SKILL.md, Fase 2
  passo 2, quando consolidar). Não junte instâncias estruturalmente diferentes em um único finding
  só para encurtar o relatório.
- **Description, Impact e Recommendation têm papéis diferentes**: Description é *o que o código
  faz* (o mecanismo). Impact é *por que isso importa* (a consequência — vazamento de dados, código
  intestável, resposta lenta, manutenção confusa). Recommendation é *o fix concreto*, nomeando qual
  transformação de `refactoring-playbook.md` se aplica. Não colapse os três em uma frase vaga
  cada.
- **As contagens do Summary precisam bater exatamente com a seção Findings** — conte você mesmo
  depois de escrever o relatório, não estime.
- **`Files: N analyzed | ~LOC lines of code`**: N precisa bater com a contagem da Fase 1. LOC é uma
  aproximação honesta (soma da contagem de linhas dos arquivos-fonte analisados) — arredonde para
  uma precisão razoável (~800, não 812.4).
- **A pergunta de confirmação continua obrigatória na conversa** — é ela que torna a Fase 2 uma
  pausa de verdade em vez de uma formalidade. Não avance além dela sem a resposta explícita do
  usuário; ela só não deve ser persistida dentro do arquivo salvo (ver seção acima).
