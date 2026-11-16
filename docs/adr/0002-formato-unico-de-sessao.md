# ADR 0002 – Formato único de sessão

**Situação:** aceita (nov./2026)

**Contexto.** O piloto e parte da inspeção serão manuais; outros fluxos serão automatizados.

**Decisão.** Ficha manual e coletor produzem o mesmo formato (`meta.json`, `acoes.jsonl`, `telas/`).

**Consequências.** IAF, detectores, requisitos e relatório funcionam igual para os dois modos;
inspeções manuais sem XML deixam os cenários que dependem de hierarquia como **indecidíveis**, o que
é medido (proporção de cenários decidíveis, Capítulo 4).
