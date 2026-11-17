"""Gerador de relatório (módulo 4 da Figura 3-2): HTML e JSON por sessão.

Visual: tema monocromático (tokens no estilo shadcn/ui, cores em OKLCH, fonte Geist),
com modo claro e escuro. O HTML é autossuficiente: sem a fonte Geist instalada ou sem
internet, cai para a fonte do sistema.
"""
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

TOKENS_CLARO = """
  --card: oklch(1.00 0 0); --ring: oklch(0 0 0); --input: oklch(0.94 0 0); --muted: oklch(0.97 0 0);
  --accent: oklch(0.94 0 0); --border: oklch(0.92 0 0); --radius: 0.5rem;
  --chart-1: oklch(0.81 0.17 75.35); --chart-2: oklch(0.55 0.22 264.53); --chart-3: oklch(0.72 0 0);
  --chart-4: oklch(0.92 0 0); --chart-5: oklch(0.56 0 0);
  --popover: oklch(0.99 0 0); --primary: oklch(0 0 0); --secondary: oklch(0.94 0 0);
  --background: oklch(0.99 0 0); --foreground: oklch(0 0 0); --destructive: oklch(0.63 0.19 23.03);
  --card-foreground: oklch(0 0 0); --muted-foreground: oklch(0.44 0 0); --accent-foreground: oklch(0 0 0);
  --primary-foreground: oklch(1.00 0 0); --secondary-foreground: oklch(0 0 0); --destructive-foreground: oklch(1.00 0 0);
  --shadow: 0px 1px 2px 0px hsl(0 0% 0% / 0.18);
"""
TOKENS_ESCURO = """
  --card: oklch(0.14 0 0); --ring: oklch(0.72 0 0); --input: oklch(0.32 0 0); --muted: oklch(0.23 0 0);
  --accent: oklch(0.32 0 0); --border: oklch(0.26 0 0);
  --chart-1: oklch(0.81 0.17 75.35); --chart-2: oklch(0.58 0.21 260.84); --chart-3: oklch(0.56 0 0);
  --chart-4: oklch(0.44 0 0); --chart-5: oklch(0.92 0 0);
  --popover: oklch(0.18 0 0); --primary: oklch(1.00 0 0); --secondary: oklch(0.25 0 0);
  --background: oklch(0 0 0); --foreground: oklch(1.00 0 0); --destructive: oklch(0.69 0.20 23.91);
  --card-foreground: oklch(1.00 0 0); --muted-foreground: oklch(0.72 0 0); --accent-foreground: oklch(1.00 0 0);
  --primary-foreground: oklch(0 0 0); --secondary-foreground: oklch(1.00 0 0); --destructive-foreground: oklch(0 0 0);
"""

CSS = f"""
:root{{{TOKENS_CLARO}
  --font-sans: Geist, ui-sans-serif, system-ui, "Segoe UI", Arial, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, "SFMono-Regular", Consolas, monospace;
  --font-serif: Georgia, serif; color-scheme: light}}
@media (prefers-color-scheme: dark){{:root:not(.light){{{TOKENS_ESCURO} color-scheme: dark}}}}
:root.dark{{{TOKENS_ESCURO} color-scheme: dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--background);color:var(--foreground);font-family:var(--font-sans);
  font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 32px}}
header{{border-bottom:1px solid var(--border);padding:28px 0 22px}}
.top{{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}}
.eyebrow{{font-family:var(--font-mono);font-size:12px;color:var(--muted-foreground);letter-spacing:.02em;margin:0 0 6px}}
h1{{font-size:26px;line-height:1.2;font-weight:600;letter-spacing:-.025em;margin:0}}
.meta{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}}
.chip{{font-family:var(--font-mono);font-size:12px;border:1px solid var(--border);background:var(--muted);
  color:var(--muted-foreground);border-radius:calc(var(--radius) - 2px);padding:2px 8px}}
.chip b{{color:var(--foreground);font-weight:500}}
button.tema{{font:inherit;font-size:13px;background:var(--secondary);color:var(--secondary-foreground);border:1px solid var(--border);
  border-radius:calc(var(--radius) - 2px);padding:6px 12px;cursor:pointer}}
button.tema:hover{{background:var(--accent)}}
button.tema:focus-visible{{outline:2px solid var(--ring);outline-offset:2px}}
main.wrap{{padding-top:28px;padding-bottom:48px}}
section{{margin-top:32px}}
h2{{font-size:16px;font-weight:600;letter-spacing:-.01em;margin:0 0 4px}}
.sub{{color:var(--muted-foreground);margin:0 0 14px;font-size:13px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}
.card{{background:var(--card);color:var(--card-foreground);border:1px solid var(--border);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:16px 18px}}
.card .rot{{font-size:13px;color:var(--muted-foreground)}}
.card .val{{display:block;font-size:30px;font-weight:600;letter-spacing:-.03em;line-height:1.15;margin-top:6px;
  font-variant-numeric:tabular-nums}}
.card .val.alerta{{color:var(--destructive)}}
.tabela{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);overflow-x:auto}}
table{{border-collapse:collapse;width:100%}}
th{{text-align:left;font-weight:500;font-size:12px;color:var(--muted-foreground);background:var(--muted);
  padding:10px 12px;border-bottom:1px solid var(--border);white-space:nowrap}}
td{{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
tbody tr:hover td{{background:var(--muted)}}
td.num{{font-family:var(--font-mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
.mono{{font-family:var(--font-mono);font-size:13px}}
.muted{{color:var(--muted-foreground)}}
.alerta{{color:var(--destructive);font-weight:600}}
.badge{{display:inline-flex;align-items:center;font-size:12px;font-weight:500;line-height:1;white-space:nowrap;
  border-radius:calc(var(--radius) - 2px);padding:4px 8px;border:1px solid transparent}}
.b-ok{{background:var(--primary);color:var(--primary-foreground)}}
.b-falha{{background:var(--destructive);color:var(--destructive-foreground)}}
.b-indef{{background:transparent;color:var(--muted-foreground);border-color:var(--border)}}
.b-code{{font-family:var(--font-mono);background:var(--secondary);color:var(--secondary-foreground)}}
.barras{{display:grid;gap:4px;min-width:150px}}
.barra{{display:flex;align-items:center;gap:8px;font-family:var(--font-mono);font-size:12px;color:var(--muted-foreground)}}
.barra i{{display:block;height:8px;border-radius:999px;min-width:2px}}
.barra .e{{background:var(--chart-2)}}.barra .s{{background:var(--chart-1)}}
.legenda{{display:flex;gap:16px;font-size:12px;color:var(--muted-foreground);margin:10px 2px 0}}
.legenda span::before{{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}}
.legenda .e::before{{background:var(--chart-2)}}.legenda .s::before{{background:var(--chart-1)}}
img.ev{{max-width:150px;border:1px solid var(--border);border-radius:calc(var(--radius) - 2px);display:block}}
.vazio{{padding:28px;text-align:center;color:var(--muted-foreground)}}
footer{{border-top:1px solid var(--border);padding:18px 0 32px;color:var(--muted-foreground);font-size:12px}}
small{{color:var(--muted-foreground)}}
"""

JS = """
(function(){var r=document.documentElement,b=document.getElementById('tema');
function escuro(){return r.classList.contains('dark')||(!r.classList.contains('light')&&matchMedia('(prefers-color-scheme: dark)').matches)}
function rot(){b.textContent=escuro()?'Modo claro':'Modo escuro'}
b.addEventListener('click',function(){var d=!escuro();r.classList.toggle('dark',d);r.classList.toggle('light',!d);rot()});rot()})();
"""

SITUACOES = {"nao_aplicavel": "não se aplica a este aplicativo", "nao_observavel": "não observável (ex.: exige pagamento)",
             "incompleto": "registro incompleto"}
VEREDITOS = {"aprovado": "b-ok", "reprovado": "b-falha"}


def _fmt(v):
    return "—" if v is None else (f"{v:.2f}" if isinstance(v, float) else str(v))


def _barras(entrar: int, sair: int, maximo: int) -> str:
    def w(n):
        return f"{max(2, round(110 * n / maximo))}px" if maximo else "2px"
    return (f'<div class=barras><div class=barra><i class=e style="width:{w(entrar)}"></i>{entrar}</div>'
            f'<div class=barra><i class=s style="width:{w(sair)}"></i>{sair}</div></div>')


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
    calculados = [r for r in resultados if r.situacao == "calculado"]
    maximo = max([max(r.acoes_engajamento or 0, r.acoes_saida or 0) for r in calculados] or [0])
    obstrucoes = sum(1 for r in resultados if r.obstrucao)

    linhas_iaf = []
    for r in resultados:
        nome = f"<td><span class='badge b-code'>{r.par}</span></td><td>{e(NOMES_PARES[r.par])}</td>"
        if r.situacao != "calculado":
            linhas_iaf.append(f"<tr>{nome}<td colspan=4 class=muted>{SITUACOES.get(r.situacao, r.situacao)}</td></tr>")
            continue
        cls = "num alerta" if r.obstrucao else "num"
        externo = "<span class='badge b-falha'>sim</span>" if r.canal_externo else "<span class=muted>não</span>"
        linhas_iaf.append(f"<tr>{nome}<td>{_barras(r.acoes_engajamento, r.acoes_saida, maximo)}</td>"
                          f"<td class='{cls}'>{_fmt(r.iaf_acoes)}</td><td class=num>{_fmt(r.iaf_tempo)}</td><td>{externo}</td></tr>")

    linhas_ach = []
    for a in achados:
        img = f'<img class=ev src="telas/{e(a.tela)}" alt="Tela de evidência do achado">' if a.tela else "<span class=muted>—</span>"
        linhas_ach.append(f"<tr><td><span class='badge b-code'>{a.detector}</span></td>"
                          f"<td><b>{a.antipadrao}</b><br><small>{e(NOMES.get(a.antipadrao, ''))}</small></td>"
                          f"<td class=mono>{e(a.unidade)}</td><td>{e(a.descricao)}</td><td class=num>{_fmt(a.passo)}</td><td>{img}</td></tr>")
    tabela_ach = (f"<div class=tabela><table><thead><tr><th>Detector</th><th>Antipadrão</th><th>Unidade</th><th>Descrição</th>"
                  f"<th>Passo</th><th>Evidência</th></tr></thead><tbody>{''.join(linhas_ach)}</tbody></table></div>"
                  if achados else "<div class='tabela vazio'>Nenhum achado nesta sessão.</div>")

    reqs_html = ""
    if requisitos and requisitos.get("cenarios"):
        lin = []
        for c in requisitos["cenarios"]:
            bcls = VEREDITOS.get(c["veredito"], "b-indef")
            tags = " ".join(f"<span class='badge b-code'>{e(t)}</span>" for t in c.get("tags", []))
            lin.append(f"<tr><td>{tags}</td><td>{e(c['funcionalidade'])}</td><td>{e(c['cenario'])}</td>"
                       f"<td><span class='badge {bcls}'>{c['veredito']}</span></td><td class=muted>{e(c.get('motivo', ''))}</td></tr>")
        r = requisitos["resumo"]
        reqs_html = (f"<section><h2>Requisitos de aceitação (Gherkin)</h2>"
                     f"<p class=sub>Cada cenário termina aprovado, reprovado ou indecidível, com o motivo.</p><div class=cards>"
                     f"<div class=card><span class=rot>Aprovados</span><span class=val>{r['aprovado']}</span></div>"
                     f"<div class=card><span class=rot>Reprovados</span><span class='val{' alerta' if r['reprovado'] else ''}'>{r['reprovado']}</span></div>"
                     f"<div class=card><span class=rot>Indecidíveis</span><span class=val>{r['indecidivel']}</span></div>"
                     f"<div class=card><span class=rot>Proporção decidível</span><span class=val>{_fmt(requisitos.get('proporcao_decidivel'))}</span></div></div>"
                     f"<div class=tabela style='margin-top:12px'><table><thead><tr><th>Etiquetas</th><th>Funcionalidade</th><th>Cenário</th>"
                     f"<th>Veredito</th><th>Motivo</th></tr></thead><tbody>{''.join(lin)}</tbody></table></div></section>")

    chips = "".join(f"<span class=chip>{rot} <b>{e(str(m.get(k, '—')))}</b></span>" for rot, k in
                    [("categoria", "categoria"), ("versão", "versao_app"), ("dispositivo", "dispositivo"),
                     ("data", "data"), ("modo", "modo")])
    doc = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório {e(sessao.app)} · antipadrões de retenção</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><header><div class=wrap><div class=top><div>
<p class=eyebrow>relatório de sessão · {e(sessao.app)}</p>
<h1>Antipadrões de retenção</h1></div>
<button class=tema id=tema type=button>Modo escuro</button></div>
<div class=meta>{chips}</div></div></header>
<main class=wrap>
<div class=cards>
<div class=card><span class=rot>Passos registrados</span><span class=val>{len(sessao.acoes)}</span></div>
<div class=card><span class=rot>Achados dos detectores</span><span class='val{' alerta' if achados else ''}'>{len(achados)}</span></div>
<div class=card><span class=rot>Pares com saída obstruída</span><span class='val{' alerta' if obstrucoes else ''}'>{obstrucoes}<small style="font-size:14px;font-weight:400"> / {len(calculados)}</small></span></div>
</div>
<section><h2>Índice de assimetria de fricção</h2>
<p class=sub>IAF &gt; 1: sair custa mais do que entrar. Tempo estimado pelo Keystroke-Level Model (Card; Moran; Newell, 1980).</p>
<div class=tabela><table><thead><tr><th>Par</th><th>Fluxos</th><th>Ações (entrar / sair)</th><th>IAF (ações)</th><th>IAF (tempo KLM)</th><th>Canal externo</th></tr></thead>
<tbody>{''.join(linhas_iaf)}</tbody></table></div>
<div class=legenda><span class=e>entrar (engajamento)</span><span class=s>sair</span></div></section>
<section><h2>Achados dos detectores</h2>
<p class=sub>Indícios a confirmar pelo oráculo; não são pareceres jurídicos.</p>
{tabela_ach}</section>
{reqs_html}
</main>
<footer><div class=wrap>Gerado pela ferramenta do TCC “Antipadrões de retenção em aplicativos móveis” (PUCPR).</div></footer>
<script>{JS}</script></body></html>"""
    ph = pasta / "relatorio.html"
    ph.write_text(doc, encoding="utf-8")
    return ph, pj
