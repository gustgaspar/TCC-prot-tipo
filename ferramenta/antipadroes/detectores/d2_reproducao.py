"""D2 – Reprodução automática (AR02, AR10). Experimental.

Regras (Quadro 3-8):
  (a) AR02: durante uma espera sem ação do usuário (ação "espera" com duração ≥ ESPERA_MINIMA),
      o conteúdo da tela muda de forma substancial (similaridade de Jaccard dos rótulos, sem
      números, abaixo de LIMIAR) — outro conteúdo começou sem solicitação;
  (b) AR10: na primeira vez em que aparece, o controle de reprodução automática está marcado.
"""
from __future__ import annotations

import re

from ..modelo import Sessao
from ..xmlutil import assinatura_de_conteudo, jaccard, normalizar, nos
from .base import Achado, Detector, unidade_tela

CONTROLE_AUTOPLAY = re.compile(r"(reproducao automatica|reproduzir automaticamente|autoplay|reproduzir o proximo)")
ESPERA_MINIMA = 5.0
LIMIAR = 0.5


class ReproducaoAutomatica(Detector):
    codigo = "D2"
    nome = "Reprodução automática"
    antipadroes = ("AR02", "AR10")
    experimental = True

    def detectar(self, sessao: Sessao) -> list[Achado]:
        achados = []
        acoes = sessao.acoes
        for i, a in enumerate(acoes):
            if a.acao == "espera" and a.segundos >= ESPERA_MINIMA and i > 0:
                antes, depois = sessao.hierarquia(acoes[i - 1]), sessao.hierarquia(a)
                if antes and depois:
                    sim = jaccard(assinatura_de_conteudo(antes), assinatura_de_conteudo(depois))
                    if sim < LIMIAR:
                        achados.append(Achado(
                            detector=self.codigo, antipadrao="AR02", app=sessao.app, unidade=unidade_tela(a),
                            descricao=f"o conteúdo mudou sem ação do usuário durante {a.segundos:.0f} s "
                                      f"(similaridade {sim:.2f})",
                            passo=a.passo, tela=a.tela, hierarquia=a.hierarquia, evidencia={"similaridade": round(sim, 2)}))
        for a in acoes:
            for n in nos(sessao.hierarquia(a)):
                if n.marcavel and CONTROLE_AUTOPLAY.search(normalizar(n.rotulo)):
                    if n.marcado:
                        achados.append(Achado(
                            detector=self.codigo, antipadrao="AR10", app=sessao.app, unidade=unidade_tela(a),
                            descricao=f"controle “{n.rotulo}” ativado por padrão", passo=a.passo, tela=a.tela,
                            hierarquia=a.hierarquia, evidencia={"controle": n.rotulo}))
                    return achados  # só a primeira ocorrência do controle indica o estado padrão
        return achados
