"""Concordância entre codificadores: kappa de Fleiss (FLEISS, 1971) e de Cohen (COHEN, 1960).

Formato do CSV de codificação (piloto/codificacao/):
    app,unidade,antipadrao,codificador_1,codificador_2,codificador_3
    A01,P1-S,AR07,1,1,0
Cada linha é uma decisão de presença (1) ou ausência (0) de um antipadrão numa unidade
(tela, fluxo ou par). Colunas cujo nome começa por "codificador" são os avaliadores.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def ler_codificacao(caminho: str | Path) -> tuple[list[str], list[list[str]], list[dict]]:
    with Path(caminho).open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    if not linhas:
        raise ValueError("arquivo de codificação vazio")
    cods = [c for c in linhas[0].keys() if c.lower().startswith("codificador")]
    if len(cods) < 2:
        raise ValueError("são necessários ao menos dois codificadores")
    # linhas com algum valor em branco são ignoradas
    completas = [l for l in linhas if all(str(l[c]).strip() != "" for c in cods)]
    return cods, [[str(l[c]).strip() for c in cods] for l in completas], completas


def fleiss(avaliacoes: list[list[str]]) -> float:
    """avaliacoes: uma lista por item, com a categoria atribuída por cada avaliador."""
    n_itens = len(avaliacoes)
    if n_itens == 0:
        raise ValueError("sem itens")
    n = len(avaliacoes[0])
    if any(len(a) != n for a in avaliacoes):
        raise ValueError("todos os itens precisam do mesmo número de avaliadores")
    categorias = sorted({c for a in avaliacoes for c in a})
    contagens = [Counter(a) for a in avaliacoes]
    p_j = {c: sum(cnt[c] for cnt in contagens) / (n_itens * n) for c in categorias}
    p_i = [(sum(v * v for v in cnt.values()) - n) / (n * (n - 1)) for cnt in contagens]
    p_bar = sum(p_i) / n_itens
    p_e = sum(v * v for v in p_j.values())
    if p_e == 1:
        return 1.0
    return (p_bar - p_e) / (1 - p_e)


def cohen(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("listas de tamanhos diferentes ou vazias")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / (n * n)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def interpretar(k: float) -> str:
    """Faixas de Landis e Koch (1977)."""
    if k < 0:
        return "pobre"
    for limite, rotulo in [(0.20, "leve"), (0.40, "razoável"), (0.60, "moderada"), (0.80, "substancial")]:
        if k <= limite:
            return rotulo
    return "quase perfeita"


def resumo(caminho: str | Path) -> dict:
    cods, avaliacoes, linhas = ler_codificacao(caminho)
    out = {"codificadores": cods, "itens": len(avaliacoes)}
    if len(cods) >= 3:
        k = fleiss(avaliacoes)
        out.update(metodo="Fleiss", kappa=round(k, 3), interpretacao=interpretar(k))
    else:
        k = cohen([a[0] for a in avaliacoes], [a[1] for a in avaliacoes])
        out.update(metodo="Cohen", kappa=round(k, 3), interpretacao=interpretar(k))
    out["meta_atingida"] = out["kappa"] >= 0.61
    divergentes = [f"{l['app']}/{l['unidade']}/{l['antipadrao']}" for l, a in zip(linhas, avaliacoes) if len(set(a)) > 1]
    out["divergencias"] = divergentes
    return out
