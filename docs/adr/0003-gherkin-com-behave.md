# ADR 0003 – Requisitos em Gherkin executados com behave

**Situação:** aceita (nov./2026)

**Decisão.** A biblioteca de requisitos é escrita em Gherkin em português (`# language: pt`) e
executada com **behave** (Python), com valores-limite em Esquemas do Cenário e etiquetas que ligam
cada cenário ao catálogo (`@AR07`), ao requisito (`@RQ-AR07-01`), ao detector (`@D4`) e à norma
(`@CDC`, `@ECA-Digital`). Cenários que exigem julgamento humano levam `@manual`.

**Consequências.** Cada cenário termina como aprovado, reprovado ou indecidível (com motivo). Um
requisito reprovado faz o `behave` retornar erro, o que permite usá-lo na integração contínua de
um projeto real e interromper o *build*.
