"""Converte a ficha de inspeção manual (CSV, Apêndice A) em uma sessão.

Colunas esperadas (ver protocolo/ficha_modelo.csv):
    id_evidencia,app,categoria,versao_app,dispositivo,data_hora,pesquisador,par,fluxo,passo,
    acao,operador_klm,caracteres,descricao_elemento,codigo_candidato,arquivo_tela,trecho_video,
    canal_externo,gatilho,observacoes
"""
from __future__ import annotations

import csv
from pathlib import Path

from .modelo import Acao, Sessao

VERDADEIRO = {"1", "sim", "s", "true", "verdadeiro", "x"}


def converter(ficha: str | Path, destino: str | Path, nao_aplicaveis: list[str] | None = None,
              nao_observaveis: list[str] | None = None) -> Sessao:
    with Path(ficha).open(encoding="utf-8") as f:
        linhas = [l for l in csv.DictReader(f) if any((v or "").strip() for v in l.values())]
    if not linhas:
        raise ValueError("ficha vazia")
    p = linhas[0]
    sessao = Sessao(pasta=Path(destino), meta={
        "app": p["app"], "categoria": p.get("categoria", ""), "versao_app": p.get("versao_app", ""),
        "dispositivo": p.get("dispositivo", ""), "data": p.get("data_hora", ""),
        "pesquisador": p.get("pesquisador", ""), "modo": "manual",
        "pares_nao_aplicaveis": nao_aplicaveis or [], "pares_nao_observaveis": nao_observaveis or [],
    })
    for i, l in enumerate(linhas, start=1):
        sessao.acoes.append(Acao(
            passo=int(l.get("passo") or i), par=(l.get("par") or "-").strip(), fluxo=(l.get("fluxo") or "transversal").strip(),
            acao=(l.get("acao") or "observacao").strip(), descricao=(l.get("descricao_elemento") or "").strip(),
            operador_klm=(l.get("operador_klm") or "").strip(), caracteres=int(l.get("caracteres") or 0),
            tela=(l.get("arquivo_tela") or "").strip(), canal_externo=(l.get("canal_externo") or "").strip().lower() in VERDADEIRO,
            gatilho=(l.get("gatilho") or "").strip(), codigo_candidato=(l.get("codigo_candidato") or "").strip(),
            observacoes=(l.get("observacoes") or "").strip(),
        ))
    sessao.salvar()
    return sessao
