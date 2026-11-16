# language: pt
@AR05
Funcionalidade: Notificações sob controle do usuário
  Para não ser chamado de volta ao aplicativo o tempo todo
  Como usuário
  Quero desativar notificações não essenciais com poucas ações e receber poucas por dia

  @RQ-AR05-01
  Esquema do Cenário: Desativar notificações não essenciais pelo próprio aplicativo
    Dado o fluxo de saída do par "P2"
    Quando eu desativo pelo caminho mais curto registrado
    Então devo concluir em no máximo <max_acoes> ações

    Exemplos:
      | max_acoes |
      | 3         |

  @RQ-AR05-02 @ECA-Digital
  Esquema do Cenário: Limite diário de notificações após o cadastro
    Dadas as notificações registradas no período de observação
    Quando conto as notificações por dia
    Então nenhum dia deve ter mais de <max_dia> notificações

    Exemplos:
      | max_dia |
      | 3       |
