# language: pt
@AR07 @CDC
Funcionalidade: Simetria entre entrar e sair
  Para poder sair do serviço com a mesma facilidade com que entrei
  Como usuário
  Quero excluir a minha conta sem mais esforço do que tive para criá-la

  @RQ-AR07-01 @D4
  Cenário: Excluir a conta não custa mais do que criá-la
    Dado o fluxo de engajamento do par "P1"
    Quando eu percorro o fluxo de saída do par "P1"
    Então o índice de assimetria de fricção deve ser no máximo 1,0
    E a saída não deve exigir canal externo ao aplicativo
