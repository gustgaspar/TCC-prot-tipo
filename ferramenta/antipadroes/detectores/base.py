from __future__ import annotations

from dataclasses import dataclass, field

from ..modelo import Acao, Sessao


@dataclass
class Achado:
    detector: str            # D1..D5
    antipadrao: str          # AR01..AR10
    app: str
    unidade: str             # unidade de análise: "P1" (par), "tela:<arquivo>" ou "feed:passo-<n>"
    descricao: str
    passo: int | None = None
    tela: str = ""
    hierarquia: str = ""
    evidencia: dict = field(default_factory=dict)


def unidade_tela(acao: Acao) -> str:
    return f"tela:{acao.tela}" if acao.tela else f"passo:{acao.passo}"


class Detector:
    codigo = "D0"
    nome = ""
    antipadroes: tuple[str, ...] = ()
    experimental = False

    def detectar(self, sessao: Sessao) -> list[Achado]:  # pragma: no cover - interface
        raise NotImplementedError
