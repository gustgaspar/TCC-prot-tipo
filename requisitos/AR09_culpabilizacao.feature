# language: pt
@AR09 @CDC
Funcionalidade: Opções de saída com rótulos neutros
  Para recusar ou sair sem constrangimento
  Como usuário
  Quero que as opções de saída não tentem me fazer sentir culpado

  @RQ-AR09-01 @D5
  Cenário: Nenhum texto culpabiliza quem quer sair ou recusar
    Dadas as telas registradas na sessão
    Quando aplico o detector "D5"
    Então não deve haver achados do antipadrão "AR09"
