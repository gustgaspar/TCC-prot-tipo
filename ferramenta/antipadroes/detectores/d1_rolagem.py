"""D1 – Rolagem sem ponto de parada (AR01). Experimental.

Regra (Quadro 3-8): em uma sequência de pelo menos K gestos de rolagem consecutivos, verifica
se cada gesto continua trazendo itens novos e se nenhuma tela exibe marcador de fim ou pausa.
"""
from __future__ import annotations

import re

from ..modelo import Sessao
from ..xmlutil import assinatura_de_conteudo, normalizar, textos
from .base import Achado, Detector

MARCADORES_FIM = re.compile(r"(voce (esta|ja esta) em dia|nao ha mais|fim do feed|tudo visto|voce viu tudo|"
                            r"you.?re all caught up|no more posts|fim das novidades|pausa)")
ROLAGEM = re.compile(r"(rol|scroll|desliz|swipe)")


class RolagemSemParada(Detector):
    codigo = "D1"
    nome = "Rolagem sem ponto de parada"
    antipadroes = ("AR01",)
    experimental = True

    def __init__(self, k: int = 5):
        self.k = k

    def _sequencias(self, sessao: Sessao):
        atual = []
        for a in sessao.acoes:
            if a.acao == "gesto" and a.hierarquia and ROLAGEM.search(normalizar(a.descricao or "rolar")):
                atual.append(a)
            else:
                if len(atual) >= self.k:
                    yield atual
                atual = []
        if len(atual) >= self.k:
            yield atual

    def detectar(self, sessao: Sessao) -> list[Achado]:
        achados = []
        for seq in self._sequencias(sessao):
            vistos: set[str] = set()
            novos_por_gesto = []
            marcador = False
            for a in seq:
                xml = sessao.hierarquia(a)
                if any(MARCADORES_FIM.search(normalizar(t)) for t in textos(xml)):
                    marcador = True
                itens = assinatura_de_conteudo(xml)
                novos_por_gesto.append(len(itens - vistos))
                vistos |= itens
            if not marcador and all(n > 0 for n in novos_por_gesto[1:]):
                achados.append(Achado(
                    detector=self.codigo, antipadrao="AR01", app=sessao.app, unidade=f"feed:passo-{seq[0].passo}",
                    descricao=f"{len(seq)} rolagens seguidas trouxeram itens novos sem marcador de fim ou pausa",
                    passo=seq[-1].passo, tela=seq[-1].tela, hierarquia=seq[-1].hierarquia,
                    evidencia={"rolagens": len(seq), "itens_novos_por_rolagem": novos_por_gesto}))
        return achados
