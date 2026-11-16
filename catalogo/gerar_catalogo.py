"""Gera as entradas do catálogo v0 (catalogo/ARxx.md) a partir de uma única fonte.

O modelo de entrada segue o Quadro 3-5 do projeto (formato de antipadrões de Gamma et al.,
1994, e Brown et al., 1998). Edite os dados abaixo e rode: python catalogo/gerar_catalogo.py
"""
from pathlib import Path

ENTRADAS = [
    dict(id="AR01", nome="Rolagem sem ponto de parada",
         contexto="Feeds de redes sociais, vídeo curto, notícias e comércio eletrônico; listas de recomendações.",
         forca="Aumentar a duração da sessão e o número de itens vistos — cada item é mais uma oportunidade de anúncio.",
         mecanismo="Reforço de razão variável (FERSTER; SKINNER, 1957) e perda da noção do tempo (*time fog*): sem fim visível, a decisão de parar depende apenas do autocontrole.",
         sintomas=["O feed continua carregando itens a cada rolagem, sem marcador de fim, paginação ou pausa.",
                   "Não há indicação de que o usuário já viu todas as novidades de quem segue."],
         metrica="Número de itens carregados até o primeiro ponto de parada (infinito se não houver).",
         refatoracao="Marcador “você está em dia” após as novidades de quem o usuário segue; paginação; pausa sugerida após N itens, configurável.",
         requisito="RQ-AR01-01", correspondencias="*Infinite Scroll* (MONGE ROFFARELLO; LUKOFF; DE RUSSIS, 2023); “ocultação de pontos naturais de parada” (BRASIL, 2026).",
         detect="Alta — detector D1 (experimental): itens novos a cada rolagem e ausência de marcador de fim."),
    dict(id="AR02", nome="Reprodução automática contínua",
         contexto="Aplicativos de vídeo, vídeo curto, *streaming* e música; telas de *player* e de fim de conteúdo.",
         forca="Aumentar a duração das sessões e o número de conteúdos consumidos por sessão.",
         mecanismo="Inércia e efeito padrão: continuar não exige nenhuma ação, enquanto parar exige uma decisão ativa (THALER; SUNSTEIN, 2019); eliminação de pontos naturais de parada.",
         sintomas=["Ao término de um conteúdo, outro começa sem ação do usuário, muitas vezes após contagem regressiva curta.",
                   "O controle de reprodução automática vem ativado por padrão.",
                   "O controle fica em tela de configurações distante do *player*."],
         metrica="Estado padrão do controle; número de ações para desativá-lo a partir do *player*; segundos até o início do conteúdo seguinte.",
         refatoracao="Reprodução automática desativada por padrão ou ativada apenas por escolha explícita; controle acessível no próprio *player*; ao fim do conteúdo, tela de escolha sem contagem regressiva.",
         requisito="RQ-AR02-01, RQ-AR02-02 (e RQ-AR10-01 para o estado padrão)",
         correspondencias="*Neverending Autoplay* (MONGE ROFFARELLO; LUKOFF; DE RUSSIS, 2023); mecanismo que mais reduz o senso de controle no YouTube (LUKOFF et al., 2021); “acionamento de novos conteúdos sem solicitação” (BRASIL, 2026).",
         detect="Alta — detector D2 (experimental): troca de conteúdo sem ação registrada e estado do controle na hierarquia de views."),
    dict(id="AR03", nome="Ofensiva com ameaça de perda",
         contexto="Aplicativos gamificados de estudo, exercício e hábitos; jogos casuais com sequências diárias.",
         forca="Aumentar a frequência de retorno diário e a retenção de longo prazo.",
         mecanismo="Aversão à perda (KAHNEMAN; TVERSKY, 1979): interromper o uso é apresentado como perder o progresso acumulado.",
         sintomas=["Contador de dias consecutivos em destaque.",
                   "Mensagens e notificações de perda iminente (“não perca sua ofensiva”), sobretudo à noite.",
                   "Pausa da ofensiva paga, escondida ou inexistente."],
         metrica="Mensagens de ameaça por dia; número de ações para pausar a ofensiva ou desativar seus lembretes.",
         refatoracao="Folgas gratuitas e metas flexíveis; mensagens neutras (“sua lição está pronta”); pausa acessível em até três ações.",
         requisito="RQ-AR03-01, RQ-AR03-02", correspondencias="Relacionado a *playing by appointment* em jogos (ZAGAL; BJÖRK; LEWIS, 2013); apelos emocionais no Duolingo (CASTRO; VALENÇA, 2025).",
         detect="Média — detector D5: padrões textuais em telas e notificações."),
    dict(id="AR04", nome="Recompensa variável por retorno",
         contexto="Jogos casuais, aplicativos gamificados e de comércio eletrônico (baús, roletas, cupons-surpresa).",
         forca="Criar o hábito de voltar ao aplicativo e prolongar o uso.",
         mecanismo="Reforço de razão variável (FERSTER; SKINNER, 1957; EYAL, 2014): o resultado imprevisível mantém a resposta.",
         sintomas=["Prêmio aleatório condicionado a voltar em determinado horário ou a permanecer conectado.",
                   "Recompensas que crescem com o tempo de uso, e não com o progresso."],
         metrica="Presença e frequência de recompensas aleatórias ou atreladas ao tempo de uso.",
         refatoracao="Recompensas previsíveis e ligadas ao progresso; sem prêmio por tempo de tela.",
         requisito="RQ-AR04-01 (@manual)", correspondencias="“Oferta de recompensas pelo tempo de uso” (BRASIL, 2026).",
         detect="Baixa — exige observação ao longo de dias; avaliado manualmente."),
    dict(id="AR05", nome="Notificação de reengajamento",
         contexto="Todos os tipos de aplicativo, especialmente redes sociais, jogos e comércio eletrônico.",
         forca="Trazer o usuário de volta e iniciar novas sessões.",
         mecanismo="Gatilho externo (FOGG, 2009); prova social em notificações sobre a atividade de outras pessoas (CIALDINI, 2006).",
         sintomas=["Notificações sobre conteúdo que o usuário não pediu ou de “saudade”.",
                   "Desativação apenas global, ou por categoria em telas profundas."],
         metrica="Notificações por dia nos 14 dias após o cadastro; ações para desativar notificações não essenciais.",
         refatoracao="Notificações não essenciais em *opt-in* por categoria; resumo diário; desativação em até três ações.",
         requisito="RQ-AR05-01, RQ-AR05-02", correspondencias="*Recapture Notifications* (MONGE ROFFARELLO; LUKOFF; DE RUSSIS, 2023); “notificações excessivas” (BRASIL, 2026).",
         detect="Média — contagem das notificações registradas; ações de desativação pelo IAF de P2."),
    dict(id="AR06", nome="Permissão oportunista",
         contexto="Primeiro uso de qualquer aplicativo; telas de boas-vindas e de conquista.",
         forca="Maximizar a taxa de aceite de notificações e rastreamento.",
         mecanismo="Efeito padrão e reciprocidade: o pedido surge antes de qualquer valor entregue ou logo após uma recompensa, com a opção de aceitar em destaque.",
         sintomas=["Diálogo de permissão do sistema antes de qualquer ação relacionada do usuário.",
                   "Tela de pré-pedido com “Permitir” grande e colorido e “Agora não” pequeno ou em texto."],
         metrica="Passo em que o pedido ocorre e ação que o precedeu; razão de área entre as opções.",
         refatoracao="Pedir no contexto da funcionalidade (ex.: ao ativar lembretes); opções de aceitar e recusar com o mesmo destaque.",
         requisito="RQ-AR06-01", correspondencias="Interferência na interface e efeito padrão (GRAY et al., 2018; 2024).",
         detect="Alta — detector D3: pacote do diálogo de permissão e área dos botões na hierarquia."),
    dict(id="AR07", nome="Saída obstruída",
         contexto="Exclusão de conta em aplicativos de qualquer categoria.",
         forca="Reduzir a perda de usuários e manter dados e base ativa.",
         mecanismo="*Sludge* (THALER, 2018): atrito deliberado em escolhas benéficas ao usuário.",
         sintomas=["Excluir a conta exige mais telas e ações do que criá-la.",
                   "A exclusão só pode ser concluída fora do aplicativo (site, e-mail, atendimento).",
                   "Confirmações repetidas e ofertas de retenção no caminho."],
         metrica="IAF do par P1 (exclusão ÷ criação); uso de canal externo.",
         refatoracao="Exclusão no próprio aplicativo, com número de ações igual ou menor que o cadastro e uma única confirmação.",
         requisito="RQ-AR07-01", correspondencias="Obstrução (GRAY et al., 2018); *roach motel* (BRIGNULL, 2023); CDC, direito à informação e proteção contra práticas abusivas (BRASIL, 1990).",
         detect="Alta — detector D4: IAF calculado do registro de ações e mudança de pacote em primeiro plano."),
    dict(id="AR08", nome="Cancelamento labiríntico",
         contexto="Assinaturas e períodos de teste em *streaming*, aplicativos gamificados e de entrega.",
         forca="Reter assinantes e receitas recorrentes.",
         mecanismo="*Sludge* e insistência (*nagging*): ofertas e confirmações repetidas aumentam o custo de sair.",
         sintomas=["Cancelar exige mais ações que assinar.", "Duas ou mais ofertas de retenção antes da confirmação.",
                   "Cancelamento apenas pela loja de aplicativos ou pelo site."],
         metrica="IAF do par P4 (cancelamento ÷ assinatura); número de ofertas de retenção.",
         refatoracao="Cancelamento simétrico à assinatura, no mesmo canal, com no máximo uma oferta claramente recusável.",
         requisito="RQ-AR08-01, RQ-AR08-02 (@manual)", correspondencias="Obstrução e importunação (GRAY et al., 2018); dificuldade de cancelamento (FEDERAL TRADE COMMISSION, 2022).",
         detect="Alta para o IAF (D4); ofertas de retenção avaliadas manualmente."),
    dict(id="AR09", nome="Saída culpabilizante",
         contexto="Telas de saída, cancelamento, recusa de permissões e de ofertas.",
         forca="Reduzir recusas e cancelamentos por constrangimento.",
         mecanismo="Apelo emocional (*confirmshaming*): a opção de recusa é redigida para fazer o usuário se sentir culpado.",
         sintomas=["“Tem certeza que deseja sair? Sentiremos sua falta.”", "“Não, prefiro pagar mais.”"],
         metrica="Presença de textos culpabilizantes nas telas de saída ou recusa.",
         refatoracao="Rótulos neutros e simétricos (“Cancelar assinatura” / “Manter assinatura”).",
         requisito="RQ-AR09-01", correspondencias="*Confirmshaming* (BRIGNULL, 2023); interferência na interface (GRAY et al., 2024).",
         detect="Média — detector D5: padrões textuais em português."),
    dict(id="AR10", nome="Padrão de engajamento máximo",
         contexto="Configurações iniciais de qualquer aplicativo.",
         forca="Garantir o máximo de engajamento para quem não altera as configurações.",
         mecanismo="Efeito padrão (THALER; SUNSTEIN, 2019): a maioria mantém a configuração inicial.",
         sintomas=["Reprodução automática, lembretes e notificações promocionais ativos no primeiro uso."],
         metrica="Proporção de opções de engajamento ativas por padrão.",
         refatoracao="Padrões protetivos: opções de engajamento desativadas até que o usuário as ative.",
         requisito="RQ-AR10-01, RQ-AR10-02 (@manual)", correspondencias="Modelo mais protetivo desde a concepção (BRASIL, 2025).",
         detect="Alta para controles visíveis na hierarquia (D2); demais configurações avaliadas manualmente."),
]

MODELO = """# {id} – {nome}

> Entrada do catálogo de antipadrões de retenção — **versão v0** (derivada da revisão da literatura; será
> confrontada com as evidências do conjunto de desenvolvimento para gerar a v1).

| Campo | Conteúdo |
|---|---|
| **Identificador e nome** | {id} – {nome} |
| **Contexto** | {contexto} |
| **Força (por que é usado)** | {forca} |
| **Mecanismo explorado** | {mecanismo} |
| **Sintomas observáveis** | {sintomas} |
| **Métrica** | {metrica} |
| **Refatoração** | {refatoracao} |
| **Requisito associado** | {requisito} — ver [`requisitos/`](../requisitos/) |
| **Correspondências e normas** | {correspondencias} |
| **Detectabilidade** | {detect} |
| **Exemplos** | A preencher com evidências anonimizadas da inspeção (código do app, versão, tela). |
"""

if __name__ == "__main__":
    aqui = Path(__file__).parent
    for e in ENTRADAS:
        e = dict(e, sintomas="<br>".join(f"• {s}" for s in e["sintomas"]))
        (aqui / f"{e['id']}.md").write_text(MODELO.format(**e), encoding="utf-8")
    linhas = ["# Catálogo de antipadrões de retenção (v0)", "",
              "Formato de antipadrões (GAMMA et al., 1994; BROWN et al., 1998), conforme o Quadro 3-5 do projeto.", "",
              "| Código | Antipadrão | Detecção automática | Requisitos |", "|---|---|---|---|"]
    for e in ENTRADAS:
        linhas.append(f"| [{e['id']}]({e['id']}.md) | {e['nome']} | {e['detect'].split(' — ')[0]} | {e['requisito']} |")
    (aqui / "README.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(len(ENTRADAS), "entradas geradas")
