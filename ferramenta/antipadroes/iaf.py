"""Índice de assimetria de fricção (IAF) — Seção 3.2.4 e Apêndice A do projeto.

IAF(ações) = C(saída) / C(engajamento)
IAF(tempo) = T(saída) / T(engajamento)
Valores > 1 indicam que sair custa mais do que entrar. Um fluxo de saída que exige canal
externo ao aplicativo é registrado como obstrução independentemente do valor do índice.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from . import klm
from .modelo import PARES, Sessao

NOMES_PARES = {
    "P1": "Criar conta ↔ excluir conta",
    "P2": "Ativar notificações ↔ desativar notificações",
    "P3": "Iniciar reprodução ↔ desativar reprodução automática",
    "P4": "Assinar ↔ cancelar assinatura",
    "P5": "Iniciar ofensiva ↔ pausar ofensiva ou lembretes",
}


@dataclass
class ResultadoIAF:
    app: str
    par: str
    situacao: str                 # calculado | nao_aplicavel | nao_observavel | incompleto
    acoes_engajamento: int = 0
    acoes_saida: int = 0
    telas_engajamento: int = 0
    telas_saida: int = 0
    tempo_engajamento: float = 0.0
    tempo_saida: float = 0.0
    iaf_acoes: Optional[float] = None
    iaf_tempo: Optional[float] = None
    canal_externo: bool = False

    @property
    def obstrucao(self) -> bool:
        return self.canal_externo or (self.iaf_acoes is not None and self.iaf_acoes > 1)


def calcular(sessao: Sessao, par: str) -> ResultadoIAF:
    if par not in PARES:
        raise ValueError(f"par desconhecido: {par}")
    r = ResultadoIAF(app=sessao.app, par=par, situacao="incompleto")
    if sessao.nao_aplicavel(par):
        r.situacao = "nao_aplicavel"
        return r
    if sessao.nao_observavel(par):
        r.situacao = "nao_observavel"
        return r
    eng, sai = sessao.fluxo(par, "engajamento"), sessao.fluxo(par, "saida")
    r.acoes_engajamento, r.acoes_saida = klm.numero_de_acoes(eng), klm.numero_de_acoes(sai)
    r.telas_engajamento, r.telas_saida = klm.numero_de_telas(eng), klm.numero_de_telas(sai)
    r.tempo_engajamento, r.tempo_saida = klm.tempo(eng), klm.tempo(sai)
    r.canal_externo = any(a.canal_externo for a in sai)
    if r.acoes_engajamento and r.acoes_saida:
        r.situacao = "calculado"
        r.iaf_acoes = round(r.acoes_saida / r.acoes_engajamento, 2)
        r.iaf_tempo = round(r.tempo_saida / r.tempo_engajamento, 2) if r.tempo_engajamento else None
    return r


def calcular_todos(sessoes: list[Sessao]) -> list[ResultadoIAF]:
    return [calcular(s, p) for s in sessoes for p in sorted(PARES)]


def exportar_csv(resultados: list[ResultadoIAF], destino: str | Path) -> None:
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    campos = list(asdict(resultados[0]).keys()) + ["obstrucao"] if resultados else []
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in resultados:
            w.writerow({**asdict(r), "obstrucao": r.obstrucao})
