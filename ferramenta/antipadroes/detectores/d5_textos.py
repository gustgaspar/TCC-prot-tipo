"""D5 – Ameaça de perda e culpabilização (AR03, AR09).

Regra (Quadro 3-8): busca padrões textuais em português nos textos da hierarquia de views e
nas notificações registradas. A lista inicial abaixo deve ser revisada com o conjunto de
desenvolvimento (Seção 3.2.4) — nunca com o conjunto de teste.
Os padrões são aplicados sobre o texto normalizado (minúsculas, sem acentos).
"""
from __future__ import annotations

import re

from ..modelo import Sessao
from ..xmlutil import normalizar, textos
from .base import Achado, Detector, unidade_tela

PADROES = {
    "AR03": [  # ofensiva com ameaça de perda
        r"\bnao perca (sua|seu|a|o)\b",
        r"\b(sua|seu|a) (ofensiva|sequencia|streak)\b.{0,40}\b(perder|perde|perdera|acabar|acaba|zerar|zera|terminar|termina|em risco|congela)",
        r"\b(vai|ira) perder (sua|seu|a|o)\b",
        r"\b(ofensiva|sequencia) (esta )?em risco\b",
        r"\bproteja (sua|seu|a) (ofensiva|sequencia)\b",
        r"\bultima chance\b",
    ],
    "AR09": [  # saída culpabilizante
        r"\btem certeza (que|de que) (quer|deseja) (sair|desistir|cancelar|excluir|desativar|ir embora)\b",
        r"\b(sentiremos|vamos sentir) (sua|a sua) falta\b",
        r"\bnao, (prefiro|quero) (perder|ficar sem|continuar sem|pagar mais|nao economizar)\b",
        r"\b(abrir mao|desistir) (de|do|da|dos|das) (seu|sua|seus|suas)\b",
        r"\bvoce vai perder tudo\b",
    ],
}
_COMPILADOS = {ap: [re.compile(p) for p in lista] for ap, lista in PADROES.items()}


def classificar(texto: str) -> list[tuple[str, str]]:
    t = normalizar(texto)
    return [(ap, r.pattern) for ap, regs in _COMPILADOS.items() for r in regs if r.search(t)]


class AmeacaECulpabilizacao(Detector):
    codigo = "D5"
    nome = "Ameaça de perda e culpabilização"
    antipadroes = ("AR03", "AR09")

    def detectar(self, sessao: Sessao) -> list[Achado]:
        vistos: set[tuple[str, str]] = set()
        achados: list[Achado] = []
        for a in sessao.acoes:
            for t in textos(sessao.hierarquia(a)):
                for ap, padrao in classificar(t):
                    chave = (ap, unidade_tela(a))
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    achados.append(Achado(detector=self.codigo, antipadrao=ap, app=sessao.app, unidade=chave[1],
                                          descricao=f"texto “{t}”", passo=a.passo, tela=a.tela,
                                          hierarquia=a.hierarquia, evidencia={"texto": t, "padrao": padrao}))
        for i, n in enumerate(sessao.notificacoes(), start=1):
            t = " ".join(filter(None, [n.get("titulo", ""), n.get("texto", "")]))
            for ap, padrao in classificar(t):
                chave = (ap, f"notificacao:{i}")
                if chave not in vistos:
                    vistos.add(chave)
                    achados.append(Achado(detector=self.codigo, antipadrao=ap, app=sessao.app, unidade=chave[1],
                                          descricao=f"notificação “{t}”", evidencia={"texto": t, "padrao": padrao,
                                                                                    "data": n.get("data", "")}))
        return achados
