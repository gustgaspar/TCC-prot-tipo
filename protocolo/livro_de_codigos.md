# Livro de códigos (v0)

Cada código corresponde a uma entrada do [catálogo](../catalogo/README.md). Marque **presente (1)**
quando **todos** os critérios de inclusão forem observados na unidade; caso contrário, **ausente (0)**.
Dúvidas vão para a coluna `observacoes` e para a reunião de consenso.

| Código | Unidade | Critérios de inclusão | Não codificar quando |
|---|---|---|---|
| AR01 | feed | ≥ 20 rolagens sempre trazem itens novos; nenhum marcador de fim/pausa | há paginação, “você está em dia” ou pausa sugerida |
| AR02 | tela | ao fim de um conteúdo, outro começa sem ação em ≤ 10 s | o próximo só começa após toque do usuário |
| AR03 | tela / notificação | texto associa a interrupção do uso à perda de progresso (“não perca sua ofensiva”) | lembrete neutro (“sua lição está pronta”) |
| AR04 | tela | prêmio aleatório condicionado a retorno ou tempo de uso | recompensa fixa por tarefa concluída |
| AR05 | notificação / par P2 | notificação sobre conteúdo não solicitado ou de “saudade”; desativação > 3 ações | notificação transacional pedida pelo usuário |
| AR06 | tela | pedido de permissão sem ação anterior relacionada **ou** aceitar com ≥ 2× a área de recusar | pedido logo após o usuário ativar lembretes, com opções equivalentes |
| AR07 | par P1 | IAF(P1) > 1 **ou** exclusão exige canal externo | IAF ≤ 1 e exclusão no app |
| AR08 | par P4 | IAF(P4) > 1, canal externo ou ≥ 2 ofertas de retenção | cancelamento simétrico com ≤ 1 oferta |
| AR09 | tela | opção de saída/recusa redigida para constranger | rótulos neutros |
| AR10 | tela | opção de engajamento (autoplay, lembretes, promoções) ativa no primeiro uso | opção desativada até o usuário ativar |
| NOVO | qualquer | técnica de retenção não prevista — descreva em `observacoes` | — |
