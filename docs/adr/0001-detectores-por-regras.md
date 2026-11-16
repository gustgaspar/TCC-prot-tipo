# ADR 0001 – Detectores baseados em regras

**Situação:** aceita (nov./2026)

**Contexto.** Ferramentas da literatura usam visão computacional e aprendizado de máquina (AidUI,
UIGuard, AppRay) e precisam de grandes conjuntos rotulados. Este trabalho terá cerca de 20 apps e
um oráculo construído pela equipe.

**Decisão.** Implementar detectores específicos e baseados em regras sobre a hierarquia de views,
os textos e a sequência de ações, um por antipadrão do subconjunto escolhido (D1–D5).

**Consequências.** Regras explicáveis e testáveis por testes unitários; precisão favorecida; menor
cobertura de variações visuais (ex.: texto dentro de imagens). As regras só podem ser ajustadas com
o conjunto de desenvolvimento, para não contaminar a avaliação.
