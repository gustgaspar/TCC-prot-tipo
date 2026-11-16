# Protocolo de inspeção sistemática (v0.1 – a revisar após o piloto)

Versão operacional do Apêndice A e da Seção 3.2.4 do projeto. As mudanças feitas depois do
piloto ficam registradas em [`piloto/mudancas_protocolo.md`](../piloto/mudancas_protocolo.md).

## 1. Preparação
- Emulador Android padronizado (registre: modelo, versão do Android, idioma **português**, fuso
  **America/Sao_Paulo**, resolução) ou dispositivo físico dedicado, sem dados pessoais.
- Gravação de tela ativada durante toda a sessão.
- Uma conta de teste **de adulto** e um e-mail exclusivo por aplicativo; **nenhum meio de pagamento**.
- Registre código do app (A01…), versão instalada, data e hora de início.
- Verifique os termos de uso quanto à automação; se vedarem, a inspeção desse app é só manual.

## 2. Execução
1. Abra o app recém-instalado e registre a primeira tela como `observacao` (pedidos de permissão aparecem aqui).
2. Execute os pares de fluxos aplicáveis (Quadro 3-4), sempre **engajamento antes da saída**, pelo
   **caminho mais curto disponível**:

   | Par | Engajamento | Saída |
   |---|---|---|
   | P1 | Criar conta (do 1º lançamento à tela inicial autenticada) | Excluir conta (da tela inicial à confirmação) |
   | P2 | Ativar notificações (aceitar o pedido) | Desativar notificações não essenciais pelo app |
   | P3 | Iniciar a reprodução de um conteúdo | Desativar a reprodução automática |
   | P4 | Assinar plano ou período de teste **sem pagamento** | Cancelar a assinatura |
   | P5 | Iniciar uma ofensiva (1ª atividade do dia) | Pausar a ofensiva ou desativar seus lembretes |

   Par que não existe no app → **não aplicável**. Par que exige pagamento → percorra até a tela de
   pagamento sem concluir e registre como **não observável**.
3. Role os feeds por **pelo menos 20 gestos** e registre se há marcador de fim ou pausa.
4. Espere ~10 s ao fim de um conteúdo (apps de vídeo) e registre se outro começa sozinho (`espera`).
5. Registre **cada passo** na ficha (`ficha_modelo.csv`): uma linha por ação.
6. Observe as notificações por 14 dias (`notificacoes.csv`: data, título, texto). No TCC 1 a
   observação pode ser parcial; registre os dias cobertos.
7. Ao final: desative as notificações e exclua a conta (isso é o fluxo de saída de P1).

## 3. Como preencher a ficha
| Coluna | Como preencher |
|---|---|
| `par`, `fluxo` | P1…P5 e `engajamento`/`saida`; observações gerais: `-` e `transversal` |
| `acao` | `toque`, `digitacao`, `gesto`, `voltar`, `espera` ou `observacao` |
| `caracteres` | só para `digitacao` (cada campo de texto conta como **uma** ação) |
| `operador_klm` | deixe vazio para usar o padrão (toque = M P; digitação = M + K por caractere) |
| `codigo_candidato` | código do catálogo (AR01…AR10) ou `NOVO` |
| `canal_externo` | `sim` quando o passo leva para fora do app (navegador, e-mail, atendimento) |
| `gatilho` | intenção do usuário relacionada, ex.: `notificacoes` quando você mesmo pediu lembretes |
| `arquivo_tela`, `trecho_video` | nome da captura e minuto:segundo no vídeo |

## 4. Contagem de ações e IAF
- Ação = toque, gesto, voltar ou um campo de texto preenchido. `espera` e `observacao` não contam.
- **IAF = ações da saída ÷ ações do engajamento** (e o mesmo com o tempo estimado pelo KLM).
- Os dois inspetores contam de forma independente; divergências são resolvidas revendo a gravação
  e anotadas em `piloto/mudancas_protocolo.md`.
- Calcule com: `python -m antipadroes ficha <ficha.csv> <pasta-da-sessao>` e depois `python -m antipadroes iaf <pasta>`.

## 5. Codificação (oráculo)
- Unidades de análise: **par** (`P1`…`P5`) para AR07/AR08; **tela** (`tela:<arquivo>`) para os demais;
  **feed** (`feed:passo-<n>`) para AR01; **notificação** (`notificacao:<n>`) para textos de notificações.
- Cada codificador marca 1 (presente) ou 0 (ausente) em `piloto/codificacao/codificacao.csv`, sem ver
  as marcações dos outros. Concordância: `python -m antipadroes kappa piloto/codificacao/codificacao.csv`
  (meta: kappa ≥ 0,61). Abaixo da meta: revisar o livro de códigos e repetir.

## 6. Ética e anonimização
- Nenhum pagamento, nenhuma interação com outros usuários, nenhuma publicação de conteúdo.
- Rostos, nomes e fotos de terceiros nas capturas são **ocultados** antes de irem para o repositório.
- No repositório os apps aparecem só pelo código (A01…); a correspondência fica fora do repositório.
- Credenciais nunca são escritas em fichas nem roteiros (use variáveis de ambiente).
