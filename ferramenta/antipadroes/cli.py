"""Interface de linha de comando:  python -m antipadroes <comando> ...

Comandos
  coletar       executa roteiros YAML no emulador/dispositivo (Appium) e grava a sessão
  ficha         converte uma ficha de inspeção manual (CSV) em sessão
  notificacoes  acrescenta as notificações ativas do app (adb dumpsys) a <sessao>/notificacoes.csv
  iaf           calcula o IAF de uma ou mais sessões (tela e CSV)
  detectar      roda os detectores e grava <sessao>/achados.json
  verificar     executa a biblioteca Gherkin sobre a sessão
  relatorio     gera <sessao>/relatorio.html e relatorio.json
  analisar      detectar + verificar + relatorio, em sequência
  kappa         concordância entre codificadores (Fleiss ou Cohen)
  avaliar       precisão, revocação e F1 dos detectores contra o oráculo
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import avaliacao, concordancia, detectores, ficha, iaf, notificacoes, relatorio, verificador
from .modelo import Sessao


def _imprimir_iaf(res):
    print(f"{'app':6} {'par':4} {'situação':15} {'entrar':>6} {'sair':>5} {'IAF':>6} {'IAF-t':>6} externo")
    for r in res:
        print(f"{r.app:6} {r.par:4} {r.situacao:15} {r.acoes_engajamento:6} {r.acoes_saida:5} "
              f"{(r.iaf_acoes if r.iaf_acoes is not None else '-'):>6} {(r.iaf_tempo if r.iaf_tempo is not None else '-'):>6} "
              f"{'sim' if r.canal_externo else 'não'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="antipadroes", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("coletar"); c.add_argument("sessao"); c.add_argument("roteiros", nargs="+")
    c.add_argument("--servidor", default="http://127.0.0.1:4723")
    c = sub.add_parser("ficha"); c.add_argument("csv"); c.add_argument("sessao")
    c.add_argument("--nao-aplicaveis", nargs="*", default=[]); c.add_argument("--nao-observaveis", nargs="*", default=[])
    c = sub.add_parser("notificacoes"); c.add_argument("sessao"); c.add_argument("--pacote", required=True)
    c = sub.add_parser("iaf"); c.add_argument("sessoes", nargs="+"); c.add_argument("--csv")
    c = sub.add_parser("detectar"); c.add_argument("sessao"); c.add_argument("--detectores", nargs="*")
    c = sub.add_parser("verificar"); c.add_argument("sessao"); c.add_argument("--tags")
    c = sub.add_parser("relatorio"); c.add_argument("sessao")
    c = sub.add_parser("analisar"); c.add_argument("sessoes", nargs="+")
    c = sub.add_parser("kappa"); c.add_argument("csv")
    c = sub.add_parser("avaliar"); c.add_argument("oraculo"); c.add_argument("sessoes", nargs="+"); c.add_argument("--saida")
    a = ap.parse_args(argv)

    if a.cmd == "coletar":
        from .coletor import coletar
        s = coletar(a.roteiros, a.sessao, a.servidor)
        print(f"sessão {s.app}: {len(s.acoes)} passos em {s.pasta}")
    elif a.cmd == "ficha":
        s = ficha.converter(a.csv, a.sessao, a.nao_aplicaveis, a.nao_observaveis)
        print(f"sessão {s.app}: {len(s.acoes)} passos convertidos para {s.pasta}")
    elif a.cmd == "notificacoes":
        s = Sessao.carregar(a.sessao)
        n = notificacoes.registrar(a.sessao, s.app, a.pacote)
        print(f"{n} notificações registradas")
    elif a.cmd == "iaf":
        res = iaf.calcular_todos([Sessao.carregar(p) for p in a.sessoes])
        _imprimir_iaf(res)
        if a.csv:
            iaf.exportar_csv(res, a.csv)
            print(f"CSV salvo em {a.csv}")
    elif a.cmd == "detectar":
        s = Sessao.carregar(a.sessao)
        ach = detectores.detectar(s, a.detectores)
        (s.pasta / "achados.json").write_text(json.dumps([asdict(x) for x in ach], ensure_ascii=False, indent=2), encoding="utf-8")
        for x in ach:
            print(f"[{x.detector}] {x.antipadrao} {x.unidade}: {x.descricao}")
        print(f"{len(ach)} achados → {s.pasta / 'achados.json'}")
    elif a.cmd == "verificar":
        r = verificador.verificar(a.sessao, a.tags)
        for c_ in r["cenarios"]:
            print(f"{c_['veredito']:12} {c_['funcionalidade']} :: {c_['cenario']}" + (f"  ({c_['motivo']})" if c_.get("motivo") else ""))
        print(r["resumo"], "proporção decidível:", r["proporcao_decidivel"])
        return 1 if r["resumo"]["reprovado"] else 0
    elif a.cmd in {"relatorio", "analisar"}:
        pastas = [a.sessao] if a.cmd == "relatorio" else a.sessoes
        for p in pastas:
            s = Sessao.carregar(p)
            ach = detectores.detectar(s)
            (s.pasta / "achados.json").write_text(json.dumps([asdict(x) for x in ach], ensure_ascii=False, indent=2), encoding="utf-8")
            req = verificador.verificar(p) if a.cmd == "analisar" else _ler_requisitos(s)
            h, _ = relatorio.gerar(s, ach, req)
            print(f"{s.app}: {len(ach)} achados; requisitos {req.get('resumo') if req else '-'} → {h}")
    elif a.cmd == "kappa":
        print(json.dumps(concordancia.resumo(a.csv), ensure_ascii=False, indent=2))
    elif a.cmd == "avaliar":
        sess = [Sessao.carregar(p) for p in a.sessoes]
        ach = [x for s in sess for x in detectores.detectar(s)]
        r = avaliacao.avaliar(ach, avaliacao.ler_oraculo(a.oraculo), {s.app for s in sess})
        txt = json.dumps(r, ensure_ascii=False, indent=2)
        print(txt)
        if a.saida:
            Path(a.saida).write_text(txt, encoding="utf-8")
    return 0


def _ler_requisitos(s: Sessao) -> dict:
    arq = s.pasta / "requisitos.jsonl"
    if not arq.exists():
        return {}
    cen = [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines() if l.strip()]
    res = {"aprovado": 0, "reprovado": 0, "indecidivel": 0}
    for c in cen:
        res[c["veredito"]] += 1
    dec = res["aprovado"] + res["reprovado"]
    return {"cenarios": cen, "resumo": res, "proporcao_decidivel": round(dec / len(cen), 3) if cen else None}


if __name__ == "__main__":
    sys.exit(main())
