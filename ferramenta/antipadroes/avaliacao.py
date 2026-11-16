"""Avaliação dos detectores contra o oráculo (Capítulo 4, Seção 4.3.1).

Oráculo (CSV): app,unidade,antipadrao,presente   — presente = 1 ou 0
Cada decisão é classificada como VP, FP, FN ou VN na unidade (app, unidade, antipadrão).
Achados em unidades não codificadas no oráculo são listados à parte ("nao_codificados"),
para revisão, e não entram no cálculo.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from .detectores import TODOS, Achado


def ler_oraculo(caminho: str | Path) -> dict[tuple[str, str, str], bool]:
    with Path(caminho).open(encoding="utf-8") as f:
        return {(l["app"].strip(), l["unidade"].strip(), l["antipadrao"].strip()): l["presente"].strip() in {"1", "sim", "true"}
                for l in csv.DictReader(f)}


def metricas(vp: int, fp: int, fn: int) -> dict:
    p = vp / (vp + fp) if vp + fp else None
    r = vp / (vp + fn) if vp + fn else None
    f1 = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
    rd = lambda x: None if x is None else round(x, 3)
    return {"precisao": rd(p), "revocacao": rd(r), "f1": rd(f1)}


def avaliar(achados: list[Achado], oraculo: dict[tuple[str, str, str], bool], apps: set[str] | None = None) -> dict:
    preditos = {(a.app, a.unidade, a.antipadrao): a.detector for a in achados}
    por_detector = {}
    total = defaultdict(int)
    for cls in TODOS:
        conta = defaultdict(int)
        for chave, presente in oraculo.items():
            app, _, ap = chave
            if ap not in cls.antipadroes or (apps and app not in apps):
                continue
            detectado = chave in preditos
            rot = ("vp" if detectado else "fn") if presente else ("fp" if detectado else "vn")
            conta[rot] += 1
            total[rot] += 1
        por_detector[cls.codigo] = {"antipadroes": list(cls.antipadroes), **dict(conta),
                                    **metricas(conta["vp"], conta["fp"], conta["fn"])}
    nao_codificados = [f"{a.app}/{a.unidade}/{a.antipadrao}" for a in achados
                       if (a.app, a.unidade, a.antipadrao) not in oraculo and (not apps or a.app in apps)]
    return {"por_detector": por_detector, "micro": {**dict(total), **metricas(total["vp"], total["fp"], total["fn"])},
            "nao_codificados": nao_codificados}
