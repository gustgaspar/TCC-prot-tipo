"""D3 – Permissão oportunista (AR06).

Regras (Quadro 3-8):
  (a) identifica o diálogo de permissão do sistema e o passo em que surge; sinaliza quando
      nenhuma ação anterior do usuário estava relacionada a notificações ou permissões
      (campo "gatilho" do registro de ações);
  (b) em telas que antecedem o pedido, compara a área das opções de aceitar e recusar e
      sinaliza destaque assimétrico (aceitar com área ≥ RAZAO_DESTAQUE vezes a de recusar).
"""
from __future__ import annotations

import re

from ..modelo import Sessao
from ..xmlutil import No, normalizar, nos
from .base import Achado, Detector, unidade_tela

PACOTES_PERMISSAO = {"com.android.permissioncontroller", "com.google.android.permissioncontroller",
                     "com.android.packageinstaller"}
ACEITAR = re.compile(r"^(permitir|ativar|sim|aceitar|quero|continuar|ok|allow|turn on|enable)\b")
RECUSAR = re.compile(r"^(agora nao|nao permitir|nao|depois|mais tarde|pular|recusar|dispensar|not now|don.?t allow|skip|later)\b")
GATILHOS = ("notific", "permiss", "alerta", "lembrete")
RAZAO_DESTAQUE = 2.0


def _eh_dialogo_permissao(lista: list[No]) -> bool:
    return any(n.pacote in PACOTES_PERMISSAO or "permission_allow" in n.rid for n in lista)


class PermissaoOportunista(Detector):
    codigo = "D3"
    nome = "Permissão oportunista"
    antipadroes = ("AR06",)

    def detectar(self, sessao: Sessao) -> list[Achado]:
        achados: list[Achado] = []
        acoes = sessao.acoes
        for i, a in enumerate(acoes):
            lista = nos(sessao.hierarquia(a))
            if not lista:
                continue
            if _eh_dialogo_permissao(lista):
                anteriores = [x for x in acoes[: i + 1] if x.do_usuario]
                relacionado = any(any(g in (x.gatilho or "").lower() for g in GATILHOS) for x in anteriores[-3:])
                if not relacionado:
                    achados.append(Achado(
                        detector=self.codigo, antipadrao="AR06", app=sessao.app, unidade=unidade_tela(a),
                        descricao=f"pedido de permissão no passo {a.passo} sem ação anterior relacionada "
                                  f"({len(anteriores)} ações do usuário até aqui)",
                        passo=a.passo, tela=a.tela, hierarquia=a.hierarquia,
                        evidencia={"acoes_anteriores": len(anteriores)}))
                continue
            # (b) tela de pré-pedido com destaque assimétrico
            botoes = [n for n in lista if n.clicavel and n.rotulo and n.area]
            aceitar = [n for n in botoes if ACEITAR.match(normalizar(n.rotulo))]
            recusar = [n for n in botoes if RECUSAR.match(normalizar(n.rotulo))]
            proximo_pedido = any(_eh_dialogo_permissao(nos(sessao.hierarquia(x))) for x in acoes[i + 1: i + 3])
            if aceitar and recusar and proximo_pedido:
                aa, ar = max(n.area for n in aceitar), max(n.area for n in recusar)
                if ar and aa / ar >= RAZAO_DESTAQUE:
                    achados.append(Achado(
                        detector=self.codigo, antipadrao="AR06", app=sessao.app, unidade=unidade_tela(a),
                        descricao=f"tela antes do pedido destaca a opção de aceitar ({aa / ar:.1f}× a área da opção de recusar)",
                        passo=a.passo, tela=a.tela, hierarquia=a.hierarquia,
                        evidencia={"razao_area": round(aa / ar, 2)}))
        return achados
