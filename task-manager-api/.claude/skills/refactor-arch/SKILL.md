---
name: refactor-arch
description: Audita qualquer codebase em busca de problemas de arquitetura, segurança e qualidade de código, e depois a refatora para uma estrutura MVC (Model-View-Controller) limpa. Use sempre que o usuário invocar "/refactor-arch", ou pedir para auditar, revisar ou refatorar a arquitetura de um projeto, encontrar anti-patterns ou code smells, ou migrar uma codebase para MVC — independente da linguagem, framework ou tipo de aplicação (Python/Flask, Node/Express, ou outros). Executa em três fases sequenciais (análise, auditoria, refatoração) e sempre pausa para confirmação humana antes de alterar qualquer arquivo.
---

# Refactor Arch — Auditoria Arquitetural & Refatoração para MVC

Você está atuando como um auditor de arquitetura sênior. Seu trabalho é entender uma codebase
desconhecida a ponto de conseguir (1) descrever com precisão sua stack e domínio, (2) apontar todo
problema real de arquitetura, segurança e qualidade com evidência exata de arquivo:linha, e (3)
transformá-la em uma codebase MVC limpa sem quebrar nenhum comportamento.

Esta skill é deliberadamente **agnóstica de tecnologia**: nada abaixo assume Python, Flask ou
Node.js especificamente. Os arquivos de referência trazem heurísticas de detecção e padrões de
transformação para as stacks que você provavelmente vai encontrar, mas o método — ler o código,
classificar o que está errado com base em evidência (não em impressão), propor um plano, esperar
um humano dizer "pode ir," e só então refatorar e validar — é o que realmente generaliza. Ao
encontrar uma stack que os arquivos de referência não cobrem, aplique o mesmo método e raciocine a
partir dos princípios subjacentes (separação de responsabilidades do MVC, SOLID) em vez de forçar
um padrão que não se encaixa.

Execute as três fases abaixo **em ordem, em uma única invocação**, pausando apenas onde indicado.

## Arquivos de referência

Leia cada um deles quando chegar na fase que precisa dele — não carregue todos antes da Fase 1,
já que ela só precisa do primeiro.

| Arquivo | Ler na | Conteúdo |
|---|---|---|
| `references/project-analysis.md` | Fase 1 | Heurísticas para detectar linguagem, framework, banco de dados, dependências, domínio e arquitetura atual a partir da árvore de arquivos e manifestos |
| `references/anti-patterns-catalog.md` | Fase 2 | 15 anti-patterns com severidade, sinais de detecção e orientação de evidência arquivo/linha, incluindo detecção de APIs deprecated |
| `references/audit-report-template.md` | Fase 2 | A estrutura exata que o relatório de auditoria deve seguir |
| `references/mvc-guidelines.md` | Fase 3 | O que significa "MVC correto" para a stack alvo, e como escalar a refatoração conforme a maturidade inicial do projeto |
| `references/refactoring-playbook.md` | Fase 3 | 13 padrões de transformação antes/depois, um para cada família de anti-pattern |

---

## Fase 1 — Análise do Projeto

Objetivo: entender o que você está vendo antes de julgar.

1. Leia `references/project-analysis.md` para as heurísticas de detecção.
2. Percorra a árvore de arquivos do projeto (excluindo diretórios de dependência/build como
   `node_modules`, `venv`, `__pycache__`, `.git`). Liste todo arquivo-fonte que você vai analisar —
   você precisa de uma contagem exata para o resumo.
3. Determine: linguagem principal, framework (+ versão, se descobrível em algum manifesto),
   dependências relevantes, o domínio de negócio (infira isso a partir de nomes de rotas, campos
   de model e nomes de tabela — não chute algo genérico), a forma arquitetural atual (monolito em
   um arquivo só, multi-arquivo sem camadas, ou já organizado em camadas mas com falhas), e
   qualquer tabela/model de banco de dados que você encontrar.
4. Imprima um resumo exatamente neste formato (adapte os valores dos campos, mantendo os nomes dos
   campos e a estrutura):

```
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

Não pule direto para a saída da Fase 2 imediatamente — o usuário deve ver esse resumo como um
bloco distinto. Mas não pare e espere aqui; siga direto para a Fase 2, a menos que algo no projeto
seja ambíguo demais para analisar (ex.: nenhum ponto de entrada reconhecível), caso em que você
deve pedir orientação ao usuário antes de continuar.

---

## Fase 2 — Auditoria de Arquitetura

Objetivo: transformar o que você agora entende em uma lista completa de findings com evidência —
e então parar.

1. Leia `references/anti-patterns-catalog.md` e `references/audit-report-template.md`.
2. Percorra a codebase arquivo por arquivo e confira cada um contra todo anti-pattern do
   catálogo. Não pare na primeira ocorrência de um padrão — o mesmo anti-pattern costuma se repetir
   dentro de um arquivo (ex.: SQL injection em cinco funções diferentes); liste cada ocorrência com
   seu próprio arquivo:linha, porque a credibilidade do relatório vem de precisão, não de nomear a
   categoria uma única vez. Dito isso, não infle o relatório com duplicatas triviais — se o mesmo
   problema de uma linha se repetir 10+ vezes em algo parecido com um loop, cite algumas linhas
   representativas mais uma nota "(e mais N, ver também...)" em vez de 10 findings quase idênticos.
3. Verifique explicitamente APIs deprecated conforme a seção dedicada do catálogo — essa é uma
   categoria obrigatória de checar, não opcional, e deve ser verificada mesmo que o resto do código
   pareça limpo.
4. Classifique a severidade de cada finding usando a escala CRITICAL/HIGH/MEDIUM/LOW definida no
   catálogo. Severidade é sobre impacto, não sobre a facilidade do fix — um segredo hardcoded de
   uma linha continua sendo CRITICAL.
5. Escreva o relatório completo seguindo `references/audit-report-template.md` à risca, com os
   findings ordenados CRITICAL → HIGH → MEDIUM → LOW (empates desempatados por caminho de
   arquivo). Salve em `reports/audit-report.md` dentro do projeto auditado (crie o diretório
   `reports/` se não existir) — uma revisão posterior pode querer mover ou renomear esse arquivo,
   mas o trabalho da skill termina em escrevê-lo em um local previsível e autocontido.
6. Imprima o relatório na conversa. O arquivo salvo termina em `Total: <N> findings` — **não**
   inclua a pergunta de confirmação do passo 7 dentro do arquivo (veja "O que vai para o arquivo
   vs. o que vai só para a conversa" em `references/audit-report-template.md`): ela é um prompt
   para a interação ao vivo, e deixá-la congelada dentro de um artefato salvo faz o relatório
   parecer uma pergunta em aberto para sempre, mesmo muito depois da Fase 3 já ter rodado.
7. **Pare aqui e peça explicitamente ao usuário para confirmar antes de tocar em qualquer
   arquivo**, por exemplo: "Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]". Essa
   confirmação não é opcional nem uma formalidade — não refatore nada, nem mesmo um fix "trivial"
   de uma linha, até que o usuário tenha confirmado afirmativamente. Se ele recusar ou quiser mudar
   o plano antes, pare e trabalhe com ele em vez de seguir em frente.

---

## Fase 3 — Refatoração para MVC

Só comece esta fase após confirmação humana explícita vinda da Fase 2.

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. Antes de escrever qualquer código, monte um plano concreto: quais findings mapeiam para qual
   padrão de transformação, como vai ficar a nova estrutura de diretórios, e o quanto de
   reestruturação realmente se justifica dada a maturidade *inicial* do projeto (veja a seção
   "escalando a refatoração" de `mvc-guidelines.md` — um projeto que já separa
   models/routes/services precisa de correções cirúrgicas, não de um trator). Compartilhe esse
   plano brevemente antes de executá-lo se ele desviar significativamente do que o relatório da
   Fase 2 sugeria.
3. Aplique as transformações do playbook, resolvendo todo finding CRITICAL e HIGH da auditoria, e
   o máximo possível de findings MEDIUM/LOW que se encaixem naturalmente na reestruturação.
   Preserve o comportamento externo: todo path de rota, método, formato de requisição e formato de
   resposta que existiam antes devem continuar funcionando da mesma forma depois, a menos que um
   finding especificamente exigisse mudar o contrato (ex.: um endpoint que permitia ao cliente
   executar SQL arbitrário não deve sobreviver com o mesmo contrato — removê-lo ou protegê-lo é o
   fix correto, e você deve deixar isso explícito em vez de simplesmente derrubar a funcionalidade
   em silêncio).
4. Não deixe o projeto parcialmente migrado — remova os arquivos/módulos antigos que a nova
   estrutura substitui, de forma que cada responsabilidade viva em exatamente um lugar. Atualize
   os manifestos de dependência se você adicionou ou removeu pacotes (ex.: trocar um hashing fraco
   por um de verdade, ou adicionar `python-dotenv`/`dotenv`).
5. Valide o resultado:
   - Suba a aplicação (instalando dependências antes, se necessário) e confirme que ela inicia sem
     erros ou exceções não tratadas nos logs.
   - Exercite uma amostra representativa dos endpoints originais (no mínimo: um endpoint de
     listagem/leitura, um endpoint de escrita/criação, e qualquer endpoint ligado a um finding
     CRITICAL/HIGH que você corrigiu) e confirme que retornam os status codes e formatos
     esperados.
   - Se algo falhar ao subir ou um endpoint regredir, corrija antes de declarar sucesso — não
     reporte a Fase 3 como completa com a aplicação quebrada.
   - Encerre o processo de servidor que você iniciou para validação assim que terminar de usá-lo.
6. Imprima um resumo de conclusão na conversa neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore da nova estrutura>

Validation
  <check ou x> Application boots without errors
  <check ou x> Endpoints respond correctly (<liste o que você testou>)
  <check ou x> <N>/<M> findings from the audit resolved
================================
```

Seja honesto nesse resumo — se um finding foi deliberadamente adiado (ex.: exige uma mudança de
infraestrutura fora do escopo de uma refatoração de código, como rotacionar uma credencial vazada
em um gerenciador de segredos real), diga isso explicitamente em vez de afirmar "zero anti-patterns
remaining" quando isso não for exatamente verdade.
7. Além de imprimir na conversa, **anexe** esse resultado ao mesmo `reports/audit-report.md` da
   Fase 2 (não crie um segundo arquivo), seguindo o formato "REFACTORING OUTCOME" descrito em
   `references/audit-report-template.md`. Isso completa o arquivo: ele passa a registrar tanto o
   que foi encontrado quanto o que de fato foi resolvido, em vez de terminar congelado numa
   pergunta de confirmação que já foi respondida há muito tempo.

---

## Regras gerais para todas as fases

- **Evidência acima de afirmação.** Toda alegação no relatório de auditoria deve apontar para um
  intervalo real de arquivo:linha que você de fato leu, não um palpite plausível.
- **Adapte, não aplique como template fixo.** Esses arquivos de referência ensinam o que procurar
  e como corrigir; não são um checklist para aplicar mecanicamente sem considerar o contexto. Um
  projeto sem nenhuma separação MVC minimamente adequada precisa de uma reestruturação completa;
  um projeto que já tem uma só precisa ter suas violações corrigidas no lugar.
- **Nunca modifique arquivos antes do gate de confirmação da Fase 2.** Isso inclui não "adiantar"
  correções óbvias enquanto ainda está escrevendo o relatório de auditoria.
- **A skill precisa continuar copiável.** Não assuma nada específico sobre este repositório em
  particular (nomes de outros projetos, diretórios irmãos, um caminho fixo de `reports/` fora do
  projeto atual). Tudo que você precisa saber sobre o projeto alvo deve vir de analisá-lo do zero
  na Fase 1.
