# language: pt
@AR08 @CDC
Funcionalidade: Cancelamento simétrico à assinatura
  Para cancelar quando eu quiser
  Como assinante
  Quero cancelar com o mesmo esforço com que assinei, sem insistência

  @RQ-AR08-01 @D4
  Cenário: Cancelar não custa mais do que assinar
    Dado o fluxo de engajamento do par "P4"
    Quando eu percorro o fluxo de saída do par "P4"
    Então o índice de assimetria de fricção deve ser no máximo 1,0
    E a saída não deve exigir canal externo ao aplicativo

  @RQ-AR08-02 @manual
  Cenário: No máximo uma oferta de retenção no cancelamento
    Dado que inicio o cancelamento da assinatura
    Quando avanço até a confirmação do cancelamento
    Então devo ver no máximo uma oferta de retenção
