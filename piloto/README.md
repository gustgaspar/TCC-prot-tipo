# Piloto do TCC 1 – 2 aplicativos

O piloto testa o protocolo de inspeção, a contagem de ações (IAF) e a codificação antes da
inspeção completa do TCC 2 (Seção 3.2.4 e Quadro 5-2 do projeto, sprints S16–S18).

## Aplicativos
Configurados em [`apps.csv`](apps.csv) (código, categoria, pares não aplicáveis / não observáveis,
dias de notificações observados). Pares previstos: A01 (vídeo curto) P1, P2, P3; A02 (gamificado de
estudo) P1, P2, P5 — P4 exige pagamento e fica como não observável.

> Critérios de escolha: Android, gratuitos, entre os mais baixados no Brasil, sem bloqueio de
> captura de tela e sem pagamento nos fluxos. A identificação real dos apps **não** vai para o
> repositório (só os códigos).

## Passo a passo
Um único comando faz todo o processamento; ele pode ser rodado a qualquer momento e só preenche
o que já tem dado (o restante fica “—”):

```bash
python -m antipadroes piloto --codificadores gustavo icaro joao
```

1. **Inspeção** – cada inspetor percorre os pares seguindo o [protocolo](../protocolo/protocolo_inspecao.md)
   e registra uma linha por ação em `fichas/<APP>_<inspetor>.csv` (modelo em `../protocolo/ficha_modelo.csv`;
   exemplo em `../protocolo/ficha_exemplo.csv`). Ex.: `fichas/A01_gustavo.csv`.
2. **Processar** – rode o comando acima. Ele converte as fichas em `sessoes/<APP>_<inspetor>/`, grava
   `iaf.csv` e cria uma planilha de codificação por pessoa em `codificacao/rodada1/<nome>.csv`, já com
   as unidades a codificar (pares P1/P4 e cada tela marcada com código candidato nas fichas).
   Rode **depois** que todas as fichas estiverem prontas: planilhas já existentes nunca são sobrescritas
   (para regenerar, apague a pasta da rodada).
3. **Codificar** – cada um abre **só a própria** planilha e marca `1` (presente) ou `0` (ausente) na
   coluna `codificador_<nome>`, consultando o [livro de códigos](../protocolo/livro_de_codigos.md).
4. **Kappa** – rode o comando de novo: ele junta as planilhas em `codificacao/codificacao_rodada1.csv`,
   calcula o kappa de Fleiss e lista as divergências. Abaixo de 0,61: discutir as divergências, ajustar
   o livro de códigos, registrar em `mudancas_protocolo.md`, copiar as planilhas para
   `codificacao/rodada2/`, recodificar e rodar de novo.
5. **Coleta automatizada** (opcional no piloto) – com o ambiente de [`../docs/ambiente.md`](../docs/ambiente.md),
   grave em `sessoes/<APP>_auto/` com `python -m antipadroes coletar`; o comando do piloto inclui essa
   sessão no IAF e na linha “fluxos automatizados”. Relatório: `python -m antipadroes analisar sessoes/A01_auto`.
6. **Resultados** – a tabela fica em [`resultados.md`](resultados.md), gerada pelo comando (não edite à mão).

## Limitações conhecidas
- Observação de notificações: 14 dias completos ficam para o TCC 2 (no piloto: dias cobertos = ___).
- Apps com bloqueio de captura ou de automação são registrados como resultado (risco R02).
