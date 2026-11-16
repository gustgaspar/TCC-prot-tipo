# Roteiro da demonstração (apresentação do TCC 1, ~3 min)

1. **Problema em uma frase:** “Não estimular o uso compulsivo” não é testável. Mostre `requisitos/AR07_saida_obstruida.feature`.
2. **Rodar a suíte num app que viola** (sessão sintética ou do piloto):
   `python -m antipadroes verificar tests/fixtures/sessoes/F01` → cenários **reprovados** com o motivo
   (ex.: “IAF = 2,00: sair exige 12 ações e entrar 6”).
3. **Mesmo requisito num app conforme:** `python -m antipadroes verificar tests/fixtures/sessoes/F02` → aprovado.
4. **Relatório com evidência:** abrir `relatorio.html` (IAF por par, achados, vereditos).
5. **Piloto real:** tabela de resultados do `piloto/README.md` (IAF de A01/A02, kappa).
6. **Fechamento:** o que o TCC 2 faz (20 apps, oráculo completo, precisão/revocação/F1, estudo com desenvolvedores).
