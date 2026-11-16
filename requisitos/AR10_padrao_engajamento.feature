# language: pt
@AR10 @ECA-Digital
Funcionalidade: Configurações padrão protetivas
  Para não começar a usar o aplicativo no modo de máximo engajamento
  Como novo usuário
  Quero que reprodução automática, lembretes e notificações promocionais venham desativados

  @RQ-AR10-01 @D2
  Cenário: Reprodução automática desativada no primeiro uso
    Dadas as telas registradas na sessão
    Quando aplico o detector "D2"
    Então não deve haver achados do antipadrão "AR10"

  @RQ-AR10-02 @manual
  Cenário: Notificações promocionais e lembretes desativados no primeiro uso
    Dado que acabei de criar a minha conta
    Quando abro as configurações de notificação
    Então as notificações promocionais e os lembretes devem estar desativados
