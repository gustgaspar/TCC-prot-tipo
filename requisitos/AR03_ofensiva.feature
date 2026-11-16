# language: pt
@AR03
Funcionalidade: Ofensivas sem ameaça de perda
  Para manter um hábito sem me sentir pressionado
  Como usuário de um aplicativo gamificado
  Quero pausar a ofensiva com facilidade e não receber ameaças de perda

  @RQ-AR03-01
  Esquema do Cenário: Pausar a ofensiva ou os seus lembretes
    Dado o fluxo de saída do par "P5"
    Quando eu desativo pelo caminho mais curto registrado
    Então devo concluir em no máximo <max_acoes> ações

    Exemplos:
      | max_acoes |
      | 3         |

  @RQ-AR03-02 @D5
  Cenário: Telas e notificações não ameaçam a perda da ofensiva
    Dadas as telas registradas na sessão
    Quando aplico o detector "D5"
    Então não deve haver achados do antipadrão "AR03"
