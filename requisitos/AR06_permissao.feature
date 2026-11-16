# language: pt
@AR06
Funcionalidade: Pedidos de permissão transparentes
  Para decidir sobre permissões quando faz sentido
  Como usuário
  Quero que o pedido só apareça depois de uma ação minha relacionada, com opções de igual destaque

  @RQ-AR06-01 @D3
  Cenário: Permissão pedida no contexto e sem destaque assimétrico
    Dadas as telas registradas na sessão
    Quando aplico o detector "D3"
    Então não deve haver achados do antipadrão "AR06"
