# language: pt
@AR02
Funcionalidade: Controle da reprodução automática
  Para poder interromper o uso quando eu quiser
  Como usuário de um aplicativo de vídeo
  Quero desativar a reprodução automática com poucas ações

  @RQ-AR02-01
  Esquema do Cenário: Desativar a reprodução automática a partir do player
    Dado o fluxo de saída do par "P3"
    Quando eu desativo pelo caminho mais curto registrado
    Então devo concluir em no máximo <max_acoes> ações

    Exemplos:
      | max_acoes |
      | 3         |

  @RQ-AR02-02 @ECA-Digital @D2
  Cenário: Nenhum conteúdo inicia sem solicitação
    Dadas as telas registradas na sessão
    Quando aplico o detector "D2"
    Então não deve haver achados do antipadrão "AR02"
