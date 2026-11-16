# language: pt
@AR01 @ECA-Digital
Funcionalidade: Pontos naturais de parada no feed
  Para conseguir parar de rolar quando eu quiser
  Como usuário de um aplicativo com feed
  Quero encontrar um marcador de fim ou uma pausa depois de alguns itens

  @RQ-AR01-01 @D1
  Cenário: O feed oferece um ponto de parada
    Dado o feed rolado pelo menos 5 vezes
    Quando aplico o detector "D1"
    Então não deve haver achados do antipadrão "AR01"
