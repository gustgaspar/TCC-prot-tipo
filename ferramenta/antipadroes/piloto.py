"""Execução do piloto de ponta a ponta:  python -m antipadroes piloto

Estrutura esperada da pasta do piloto (padrão: piloto/):

    apps.csv                          codigo,categoria,nao_aplicaveis,nao_observaveis,dias_notificacoes
    fichas/<APP>_<inspetor>.csv       uma ficha por inspetor e app (inspeção manual)
    notificacoes/<APP>_<inspetor>.csv opcional: notificações recebidas (data,app,titulo,texto,origem)
    sessoes/<APP>_auto/               opcional: sessão da coleta automatizada (antipadroes coletar)
    codificacao/rodada<N>/<nome>.csv  planilhas de codificação, uma por codificador

O comando:
  1. converte cada ficha em sessoes/<APP>_<inspetor>/ (com os pares não aplicáveis de apps.csv);
  2. calcula o IAF de todas as sessões e grava iaf.csv;
  3. gera as planilhas em branco da rodada 1 (se ainda não existirem) para os codificadores
     informados em --codificadores, com as unidades tiradas das fichas;
  4. junta as planilhas de cada rodada em codificacao/codificacao_rodada<N>.csv e calcula o kappa;
  5. escreve resultados.md com a tabela de resultados do piloto.

Nada é inventado: célula sem dado fica "—" até que a ficha ou a planilha correspondente exista.
"""
from __future__ import annotations

import csv
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import concordancia, ficha, iaf
from .iaf import NOMES_PARES
from .modelo import PARES, Sessao

PAR_PARA_ANTIPADRAO = {"P1": "AR07", "P2": "AR05", "P4": "AR08"}   # livro de códigos: AR05/AR07/AR08 no par
_FICHA = re.compile(r"^(A\d+)_(.+)\.csv$")
_RODADA = re.compile(r"^rodada(\d+)$")


@dataclass
class App:
    codigo: str
    categoria: str = ""
    nao_aplicaveis: list[str] = field(default_factory=list)
    nao_observaveis: list[str] = field(default_factory=list)
    dias_notificacoes: str = ""


def ler_apps(caminho: Path) -> dict[str, App]:
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8") as f:
        return {l["codigo"].strip(): App(
            codigo=l["codigo"].strip(), categoria=(l.get("categoria") or "").strip(),
            nao_aplicaveis=(l.get("nao_aplicaveis") or "").split(),
            nao_observaveis=(l.get("nao_observaveis") or "").split(),
            dias_notificacoes=(l.get("dias_notificacoes") or "").strip(),
        ) for l in csv.DictReader(f) if (l.get("codigo") or "").strip()}


def _ficha_tem_passos(caminho: Path) -> bool:
    with caminho.open(encoding="utf-8") as f:
        return any(any((v or "").strip() for v in l.values()) for l in csv.DictReader(f))


def converter_fichas(pasta: Path, apps: dict[str, App]) -> list[Sessao]:
    sessoes = []
    for arq in sorted((pasta / "fichas").glob("*.csv")):
        m = _FICHA.match(arq.name)
        if not m or not _ficha_tem_passos(arq):
            continue
        app = apps.get(m.group(1), App(m.group(1)))
        s = ficha.converter(arq, pasta / "sessoes" / arq.stem, app.nao_aplicaveis, app.nao_observaveis)
        s.meta["inspetor"] = m.group(2)
        s.salvar()
        notif = pasta / "notificacoes" / arq.name
        if notif.exists():
            shutil.copyfile(notif, s.pasta / "notificacoes.csv")
        sessoes.append(s)
    return sessoes


def sessoes_automaticas(pasta: Path, apps: dict[str, App]) -> list[Sessao]:
    out = []
    for p in sorted((pasta / "sessoes").glob("*_auto")):
        if (p / "meta.json").exists():
            s = Sessao.carregar(p)
            app = apps.get(s.app)
            if app and not s.meta.get("pares_nao_aplicaveis"):
                s.meta["pares_nao_aplicaveis"] = app.nao_aplicaveis
                s.meta["pares_nao_observaveis"] = app.nao_observaveis
            out.append(s)
    return out


# ---------------------------------------------------------------- codificação
def unidades(sessoes: list[Sessao]) -> list[tuple[str, str, str, str]]:
    """(app, unidade, antipadrao, contexto) a codificar, sem repetição, a partir das sessões manuais."""
    vistos: dict[tuple[str, str, str], str] = {}
    for s in sessoes:
        for par, ap in PAR_PARA_ANTIPADRAO.items():
            if iaf.calcular(s, par).situacao == "calculado":
                vistos.setdefault((s.app, par, ap), NOMES_PARES[par])
        insp = s.meta.get("inspetor", s.pasta.name)
        for a in s.acoes:
            for cod in re.split(r"[;,\s]+", a.codigo_candidato.strip()):
                if not re.fullmatch(r"AR\d{2}", cod or ""):
                    continue
                if cod == "AR01":
                    un = f"feed:{insp}-passo-{a.passo}"
                elif a.tela:
                    un = f"tela:{a.tela}"
                else:
                    un = f"passo:{insp}-{a.passo}"
                vistos.setdefault((s.app, un, cod), f"{a.par} {a.fluxo}: {a.descricao}".strip())
        for i, n in enumerate(s.notificacoes(), start=1):
            texto = " – ".join(x for x in ((n.get("titulo") or "").strip(), (n.get("texto") or "").strip()) if x)
            if texto:
                for cod in ("AR03", "AR05"):
                    vistos.setdefault((s.app, f"notificacao:{insp}-{i}", cod), f"{(n.get('data') or '').strip()}: {texto}")
    return sorted((k[0], k[1], k[2], v) for k, v in vistos.items())


def gerar_planilhas(pasta: Path, sessoes: list[Sessao], codificadores: list[str], rodada: int = 1) -> list[Path]:
    """Uma planilha por codificador, todas com as mesmas linhas e a coluna de marcação em branco."""
    destino = pasta / "codificacao" / f"rodada{rodada}"
    destino.mkdir(parents=True, exist_ok=True)
    linhas = unidades(sessoes)
    criadas = []
    for nome in codificadores:
        arq = destino / f"{nome}.csv"
        if arq.exists():
            continue
        with arq.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["app", "unidade", "antipadrao", "contexto", f"codificador_{nome}", "observacoes"])
            for app, un, ap, ctx in linhas:
                w.writerow([app, un, ap, ctx, "", ""])
        criadas.append(arq)
    return criadas


def juntar_planilhas(arquivos: list[Path], destino: Path) -> Path:
    marcas: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    cods = []
    for arq in sorted(arquivos):
        with arq.open(encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            col = next(c for c in leitor.fieldnames if c.startswith("codificador"))
            cods.append(col)
            for l in leitor:
                marcas[(l["app"], l["unidade"], l["antipadrao"])][col] = (l.get(col) or "").strip()
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["app", "unidade", "antipadrao", *cods])
        for chave in sorted(marcas):
            w.writerow([*chave, *(marcas[chave].get(c, "") for c in cods)])
    return destino


def rodadas(pasta: Path) -> dict[int, Path]:
    """Junta as planilhas de cada rodada com ao menos 2 codificadores; devolve {rodada: csv juntado}."""
    out = {}
    base = pasta / "codificacao"
    for d in sorted(base.glob("rodada*")):
        m = _RODADA.match(d.name)
        arqs = sorted(d.glob("*.csv"))
        if m and d.is_dir() and len(arqs) >= 2:
            out[int(m.group(1))] = juntar_planilhas(arqs, base / f"codificacao_{d.name}.csv")
    return out


def _kappa(caminho: Path) -> dict | None:
    try:
        r = concordancia.resumo(caminho)
    except (ValueError, ZeroDivisionError):
        return None
    return r if r["itens"] else None


def presentes(caminho: Path) -> list[tuple[str, str, str]]:
    """Unidades em que a maioria dos codificadores marcou presença (1)."""
    with caminho.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    out = []
    for l in linhas:
        v = [str(l[c]).strip() for c in l if c.startswith("codificador")]
        if v and all(v) and sum(x == "1" for x in v) * 2 > len(v):
            out.append((l["app"], l["unidade"], l["antipadrao"]))
    return out


# ---------------------------------------------------------------- resultados
def _fmt(x: float | None) -> str:
    return "—" if x is None else f"{x:.2f}".replace(".", ",")


def divergencias_contagem(sessoes: list[Sessao]) -> dict[str, list[str]]:
    por_app: dict[str, list[Sessao]] = defaultdict(list)
    for s in sessoes:
        por_app[s.app].append(s)
    out: dict[str, list[str]] = {}
    for app, ss in por_app.items():
        div = []
        for par in sorted(PARES):
            rs = [(s.meta.get("inspetor", s.pasta.name), iaf.calcular(s, par)) for s in ss]
            rs = [(n, r) for n, r in rs if r.situacao == "calculado"]
            for fluxo, attr in (("entrar", "acoes_engajamento"), ("sair", "acoes_saida")):
                vals = {n: getattr(r, attr) for n, r in rs}
                if len(set(vals.values())) > 1:
                    div.append(f"{par} {fluxo}: " + ", ".join(f"{n} {v}" for n, v in vals.items()))
        out[app] = div
    return out


def _celula_iaf(rs: list[iaf.ResultadoIAF], app: App | None = None, par: str = "") -> str:
    if not rs and app:
        if par in app.nao_aplicaveis:
            return "não aplicável"
        if par in app.nao_observaveis:
            return "não observável"
    calc = [r.iaf_acoes for r in rs if r.situacao == "calculado"]
    if calc:
        lo, hi = min(calc), max(calc)
        return _fmt(lo) if lo == hi else f"{_fmt(lo)}–{_fmt(hi)}"
    sit = {r.situacao for r in rs}
    if sit == {"nao_aplicavel"}:
        return "não aplicável"
    if sit == {"nao_observavel"}:
        return "não observável"
    return "—"


def resultados_markdown(apps: dict[str, App], manuais: list[Sessao], auto: list[Sessao],
                        kappas: dict[int, dict | None], codificados: list[tuple[str, str, str]]) -> str:
    codigos = sorted(set(apps) | {s.app for s in manuais} | {s.app for s in auto})
    res = {s.pasta.name: iaf.calcular_todos([s]) for s in manuais}
    div = divergencias_contagem(manuais)

    def por(app, par):
        return [r for s in manuais if s.app == app for r in res[s.pasta.name] if r.par == par]

    linhas = [["Inspetores com ficha"] + [", ".join(sorted(s.meta.get("inspetor", "?") for s in manuais if s.app == a)) or "—" for a in codigos]]
    for par in sorted(PARES):
        linhas.append([f"IAF {par} ({NOMES_PARES[par].lower()})"] + [_celula_iaf(por(a, par), apps.get(a), par) for a in codigos])
    linhas.append(["Saída por canal externo?"] + [
        (", ".join(sorted({r.par for r in (x for p in PARES for x in por(a, p)) if r.canal_externo})) or "não")
        if any(s.app == a for s in manuais) else "—" for a in codigos])
    linhas.append(["Antipadrões codificados (maioria)"] + [
        (", ".join(f"{ap} ({n})" for ap, n in sorted(_contar([c[2] for c in codificados if c[0] == a]).items())) or "nenhum")
        if any(kappas.values()) else "—" for a in codigos])
    linhas.append(["Divergências de contagem entre inspetores"] + [
        ("; ".join(div[a]) or "nenhuma") if len([s for s in manuais if s.app == a]) > 1 else "—" for a in codigos])
    linhas.append(["Fluxos automatizados com sucesso"] + [_auto(a, auto) for a in codigos])
    linhas.append(["Dias de notificações observados"] + [apps[a].dias_notificacoes or "—" if a in apps else "—" for a in codigos])

    cab = ["Métrica"] + [f"{a}" + (f" ({apps[a].categoria})" if a in apps and apps[a].categoria else "") for a in codigos]
    md = ["# Resultados do piloto", "",
          "> Arquivo gerado por `python -m antipadroes piloto`. Não edite à mão: corrija as fichas ou",
          "> as planilhas de codificação e rode o comando de novo. “—” = ainda sem dado.", "",
          "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    md += ["| " + " | ".join(l) + " |" for l in linhas]
    md += ["", "IAF = ações para sair ÷ ações para entrar; intervalo quando os inspetores divergem.", "",
           "## Concordância da codificação", ""]
    if not kappas:
        md.append("Ainda não há planilhas de codificação de dois ou mais codificadores.")
    else:
        md += ["| Rodada | Método | Itens completos | Kappa | Interpretação | Meta (≥ 0,61) | Divergências |",
               "|---|---|---|---|---|---|---|"]
        for n, k in sorted(kappas.items()):
            if k is None:
                md.append(f"| {n} | — | 0 | — | planilhas ainda em branco | — | — |")
            else:
                md.append(f"| {n} | {k['metodo']} | {k['itens']} | {_fmt(k['kappa'])} | {k['interpretacao']} | "
                          f"{'atingida' if k['meta_atingida'] else 'não atingida'} | {len(k['divergencias'])} |")
        ult = kappas[max(kappas)]
        if ult and ult["divergencias"]:
            md += ["", "Unidades com divergência na última rodada (discutir e registrar em `mudancas_protocolo.md`):", ""]
            md += [f"- `{d}`" for d in ult["divergencias"]]
    return "\n".join(md) + "\n"


def _contar(itens):
    c: dict[str, int] = defaultdict(int)
    for i in itens:
        c[i] += 1
    return c


def _auto(app: str, auto: list[Sessao]) -> str:
    ss = [s for s in auto if s.app == app]
    if not ss:
        return "—"
    partes = []
    for s in ss:
        for par in sorted(PARES):
            eng, sai = s.tem_fluxo(par, "engajamento"), s.tem_fluxo(par, "saida")
            if eng or sai:
                partes.append(f"{par} ({int(eng) + int(sai)}/2)")
    return ", ".join(partes) or "nenhum"


def executar(pasta: str | Path = "piloto", codificadores: list[str] | None = None) -> dict:
    pasta = Path(pasta)
    if not pasta.is_dir():
        raise FileNotFoundError(f"pasta do piloto não encontrada: {pasta}")
    apps = ler_apps(pasta / "apps.csv")
    manuais = converter_fichas(pasta, apps)
    auto = sessoes_automaticas(pasta, apps)
    todas = manuais + auto
    if todas:
        iaf.exportar_csv(iaf.calcular_todos(todas), pasta / "iaf.csv")
    planilhas = gerar_planilhas(pasta, manuais, codificadores) if manuais and codificadores else []
    juntadas = rodadas(pasta)
    kappas = {n: _kappa(p) for n, p in juntadas.items()}
    codificados = presentes(juntadas[max(juntadas)]) if juntadas else []
    (pasta / "resultados.md").write_text(resultados_markdown(apps, manuais, auto, kappas, codificados), encoding="utf-8")
    return {"sessoes_manuais": [s.pasta.name for s in manuais], "sessoes_auto": [s.pasta.name for s in auto],
            "planilhas_criadas": [str(p) for p in planilhas], "kappas": kappas,
            "resultados": str(pasta / "resultados.md")}
