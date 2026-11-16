"""Gerador de relatório (módulo 4 da Figura 3-2): HTML e JSON por sessão."""
from __future__ import annotations

import html
import json
from dataclasses import asdict
from pathlib import Path

from . import iaf
from .catalogo import NOMES
from .detectores import Achado
from .iaf import NOMES_PARES
from .modelo import Sessao

CSS = """
body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;background:#f6f7f9;color:#1d2433}
header{background:#1f3a5f;color:#fff;padding:20px 32px}header h1{margin:0;font-size:22px}
header p{margin:4px 0 0;opacity:.85}main{padding:24px 32px;max-width:1200px}
h2{font-size:18px;margin:28px 0 10px;color:#1f3a5f}
.cards{display:flex;gap:12px;flex-wrap:wrap}.card{background:#fff;border:1px solid #dde2ea;border-radius:8px;padding:12px 16px;min-width:150px}
.card b{display:block;font-size:24px}.card span{font-size:13px;color:#5a6576}
table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}
th,td{border:1px solid #dde2ea;padding:6px 8px;text-align:left;vertical-align:top}th{background:#eef1f5}
.ruim{color:#b3261e;font-weight:600}.bom{color:#1e7b34;font-weight:600}.neutro{color:#5a6576}
img.ev{max-width:160px;border:1px solid #ccd;border-radius:4px}
small{color:#5a6576}
"""


SITUACOES = {"nao_aplicavel": "não se aplica a este aplicativo", "nao_observavel": "não observável (ex.: exige pagamento)",
             "incompleto": "registro incompleto"}


def _fmt(v):
    return "—" if v is None else (f"{v:.2f}" if isinstance(v, float) else str(v))


def gerar(sessao: Sessao, achados: list[Achado], requisitos: dict | None = None) -> tuple[Path, Path]:
    pasta = sessao.pasta
    resultados = [iaf.calcular(sessao, p) for p in sorted(NOMES_PARES)]
    dados = {
        "meta": sessao.meta,
        "iaf": [{**asdict(r), "obstrucao": r.obstrucao} for r in resultados],
        "achados": [asdict(a) for a in achados],
        "requisitos": requisitos or {},
    }
    pj = pasta / "relatorio.json"
    pj.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    e = html.escape
    m = sessao.meta
    linhas_iaf = []
    for r in resultados:
        if r.situacao != "calculado":
            linhas_iaf.append(f"<tr><td>{r.par}</td><td>{e(NOMES_PARES[r.par])}</td><td colspan=5 class=neutro>{SITUACOES.get(r.situacao, r.situacao)}</td></tr>")
            continue
        cls = "ruim" if r.obstrucao else "bom"
        linhas_iaf.append(f"<tr><td>{r.par}</td><td>{e(NOMES_PARES[r.par])}</td><td>{r.acoes_engajamento}</td>"
                          f"<td>{r.acoes_saida}</td><td class={cls}>{_fmt(r.iaf_acoes)}</td><td>{_fmt(r.iaf_tempo)}</td>"
                          f"<td>{'sim' if r.canal_externo else 'não'}</td></tr>")
    linhas_ach = []
    for a in achados:
        img = f'<img class=ev src="telas/{e(a.tela)}" alt="evidência">' if a.tela else ""
        linhas_ach.append(f"<tr><td>{a.detector}</td><td><b>{a.antipadrao}</b><br><small>{e(NOMES.get(a.antipadrao, ''))}</small></td>"
                          f"<td>{e(a.unidade)}</td><td>{e(a.descricao)}</td><td>{_fmt(a.passo)}</td><td>{img}</td></tr>")
    reqs_html = ""
    if requisitos and requisitos.get("cenarios"):
        lin = []
        for c in requisitos["cenarios"]:
            cls = {"aprovado": "bom", "reprovado": "ruim"}.get(c["veredito"], "neutro")
            lin.append(f"<tr><td>{e(' '.join(c.get('tags', [])))}</td><td>{e(c['funcionalidade'])}</td><td>{e(c['cenario'])}</td>"
                       f"<td class={cls}>{c['veredito']}</td><td>{e(c.get('motivo', ''))}</td></tr>")
        r = requisitos["resumo"]
        reqs_html = (f"<h2>Requisitos de aceitação (Gherkin)</h2><div class=cards>"
                     f"<div class=card><b>{r['aprovado']}</b><span>aprovados</span></div>"
                     f"<div class=card><b class=ruim>{r['reprovado']}</b><span>reprovados</span></div>"
                     f"<div class=card><b>{r['indecidivel']}</b><span>indecidíveis</span></div>"
                     f"<div class=card><b>{_fmt(requisitos.get('proporcao_decidivel'))}</b><span>proporção decidível</span></div></div>"
                     f"<table><tr><th>Etiquetas</th><th>Funcionalidade</th><th>Cenário</th><th>Veredito</th><th>Motivo</th></tr>{''.join(lin)}</table>")
    doc = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório {e(sessao.app)}</title><style>{CSS}</style></head>
<body><header><h1>Relatório de antipadrões de retenção – {e(sessao.app)}</h1>
<p>Categoria: {e(m.get('categoria', '—'))} · versão do app: {e(m.get('versao_app', '—'))} · dispositivo: {e(m.get('dispositivo', '—'))} · data: {e(m.get('data', '—'))} · modo: {e(m.get('modo', '—'))}</p></header>
<main>
<div class=cards><div class=card><b>{len(sessao.acoes)}</b><span>passos registrados</span></div>
<div class=card><b class="{'ruim' if achados else 'bom'}">{len(achados)}</b><span>achados</span></div>
<div class=card><b>{sum(1 for r in resultados if r.obstrucao)}</b><span>pares em que sair custa mais (IAF &gt; 1) ou exige canal externo</span></div></div>
<h2>Índice de assimetria de fricção</h2>
<table><tr><th>Par</th><th>Fluxos</th><th>Ações para entrar</th><th>Ações para sair</th><th>IAF (ações)</th><th>IAF (tempo KLM)</th><th>Canal externo</th></tr>{''.join(linhas_iaf)}</table>
<p><small>IAF &gt; 1: sair custa mais do que entrar. Tempo estimado pelo Keystroke-Level Model (Card; Moran; Newell, 1980).</small></p>
<h2>Achados dos detectores</h2>
{'<p class=bom>Nenhum achado.</p>' if not achados else f"<table><tr><th>Detector</th><th>Antipadrão</th><th>Unidade</th><th>Descrição</th><th>Passo</th><th>Evidência</th></tr>{''.join(linhas_ach)}</table>"}
{reqs_html}
<p><small>Gerado pela ferramenta do TCC “Antipadrões de retenção em aplicativos móveis” (PUCPR). Os achados são indícios a confirmar pelo oráculo, não pareceres jurídicos.</small></p>
</main></body></html>"""
    ph = pasta / "relatorio.html"
    ph.write_text(doc, encoding="utf-8")
    return ph, pj
