"""Custo de fluxos segundo o Keystroke-Level Model (CARD; MORAN; NEWELL, 1980).

Valores dos operadores (segundos), conforme Card, Moran e Newell (1980):
    K = 0,28  pressionar tecla (digitador médio)
    P = 1,10  apontar um alvo
    H = 0,40  mover a mão entre dispositivos
    M = 1,35  preparação mental
A adaptação para toque — um toque ou gesto equivale a apontar (P) precedido de
preparação mental (M) — é uma hipótese de trabalho a calibrar no piloto e pode ser
alterada em OPERADORES/MAPA_ACOES sem mudar o restante da ferramenta.
"""
from __future__ import annotations

from .modelo import Acao

OPERADORES = {"K": 0.28, "P": 1.10, "H": 0.40, "M": 1.35}

# Operadores padrão por tipo de ação (usados quando a ação não informa operador_klm).
MAPA_ACOES = {
    "toque": "M P",
    "gesto": "M P",
    "voltar": "P",
    "digitacao": "M K*",   # K* = um K por caractere digitado
}


def operadores(acao: Acao) -> list[str]:
    texto = acao.operador_klm.strip() or MAPA_ACOES.get(acao.acao, "")
    ops: list[str] = []
    for tok in texto.split():
        if tok == "K*":
            ops.extend(["K"] * max(1, acao.caracteres))
        elif tok in OPERADORES:
            ops.append(tok)
        else:
            raise ValueError(f"operador KLM desconhecido: {tok!r} (passo {acao.passo})")
    return ops


def tempo(acoes: list[Acao]) -> float:
    """Tempo estimado (s) para executar as ações do usuário de um fluxo."""
    return round(sum(OPERADORES[o] for a in acoes if a.do_usuario for o in operadores(a)), 2)


def numero_de_acoes(acoes: list[Acao]) -> int:
    """Número de ações do usuário (cada campo de texto conta como uma ação)."""
    return sum(1 for a in acoes if a.do_usuario)


def numero_de_telas(acoes: list[Acao]) -> int:
    return len({a.tela for a in acoes if a.tela})
