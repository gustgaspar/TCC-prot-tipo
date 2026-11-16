# Piloto do TCC 1 – 2 aplicativos

O piloto testa o protocolo de inspeção, a contagem de ações (IAF) e a codificação antes da
inspeção completa do TCC 2 (Seção 3.2.4 e Quadro 5-2 do projeto, sprints S16–S18).

## Aplicativos
| Código | Categoria | Pares aplicáveis | Inspetores | Situação |
|---|---|---|---|---|
| A01 | _preencher (ex.: vídeo curto)_ | P1, P2, P3 | _nomes_ | ⬜ a fazer |
| A02 | _preencher (ex.: gamificado de estudo)_ | P1, P2, P5 | _nomes_ | ⬜ a fazer |

> Critérios de escolha: Android, gratuitos, entre os mais baixados no Brasil, sem bloqueio de
> captura de tela e sem pagamento nos fluxos. A identificação real dos apps **não** vai para o
> repositório (só os códigos).

## Passo a passo
1. Cada inspetor preenche sua ficha: `fichas/A01_<inspetor>.csv` (modelo em `../protocolo/ficha_modelo.csv`;
   exemplo preenchido em `../protocolo/ficha_exemplo.csv`).
2. Converter cada ficha em sessão e calcular o IAF:
   ```bash
   python -m antipadroes ficha piloto/fichas/A01_<inspetor>.csv piloto/sessoes/A01_<inspetor> --nao-aplicaveis P4 P5
   python -m antipadroes iaf piloto/sessoes/A01_* piloto/sessoes/A02_* --csv piloto/iaf.csv
   ```
3. Os três codificam as evidências dos dois apps em `codificacao/codificacao.csv` (modelo em
   `codificacao/codificacao_modelo.csv`) sem ver os outros e calculam o kappa:
   ```bash
   python -m antipadroes kappa piloto/codificacao/codificacao.csv
   ```
   Abaixo de 0,61: ajustar o livro de códigos, registrar em `mudancas_protocolo.md` e fazer nova rodada
   (`codificacao_rodada2.csv`).
4. Rodar a ferramenta sobre uma sessão automatizada (ver `../docs/ambiente.md`) e gerar o relatório:
   ```bash
   python -m antipadroes analisar piloto/sessoes/A01_auto
   ```
5. Preencher os resultados abaixo e as mudanças no protocolo.

## Resultados do piloto
| Métrica | A01 | A02 |
|---|---|---|
| IAF P1 (excluir ÷ criar) | | |
| IAF P2 (desativar ÷ ativar notificações) | | |
| IAF P3 / P5 | | |
| Saída por canal externo? | | |
| Antipadrões codificados | | |
| Kappa de Fleiss (rodada 1 → rodada 2) | | |
| Divergências de contagem entre inspetores | | |
| Fluxos automatizados com sucesso | | |

## Limitações conhecidas
- Observação de notificações: 14 dias completos ficam para o TCC 2 (no piloto: dias cobertos = ___).
- Apps com bloqueio de captura ou de automação são registrados como resultado (risco R02).
