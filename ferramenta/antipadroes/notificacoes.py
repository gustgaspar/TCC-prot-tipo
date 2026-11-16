"""Registro das notificações recebidas no período de observação (14 dias após o cadastro).

Duas formas de alimentar <sessao>/notificacoes.csv (colunas: data,app,titulo,texto,origem):
  1. manual: o pesquisador anota cada notificação recebida (recomendado no piloto);
  2. automática (experimental): `python -m antipadroes notificacoes <sessao> --pacote <pkg>` lê
     `adb shell dumpsys notification --noredact` e acrescenta as notificações ativas do pacote.
     Rode uma vez por dia, antes de abrir o aplicativo; notificações dispensadas não aparecem.
"""
from __future__ import annotations

import csv
import re
import subprocess
from datetime import date
from pathlib import Path

CAMPOS = ["data", "app", "titulo", "texto", "origem"]


def _ler_dumpsys(pacote: str, adb: str = "adb") -> list[dict]:
    saida = subprocess.run([adb, "shell", "dumpsys", "notification", "--noredact"],
                           capture_output=True, text=True, check=True).stdout
    return analisar_dumpsys(saida, pacote)


def analisar_dumpsys(saida: str, pacote: str) -> list[dict]:
    registros, atual = [], None
    for linha in saida.splitlines():
        if "NotificationRecord(" in linha:
            if atual and atual["pkg"] == pacote:
                registros.append(atual)
            m = re.search(r"pkg=(\S+)", linha)
            atual = {"pkg": m.group(1) if m else "", "titulo": "", "texto": ""}
        elif atual is not None:
            m = re.search(r"android\.title=\w+ \((.*)\)\s*$", linha)
            if m and not atual["titulo"]:
                atual["titulo"] = m.group(1)
            m = re.search(r"android\.text=\w+ \((.*)\)\s*$", linha)
            if m and not atual["texto"]:
                atual["texto"] = m.group(1)
    if atual and atual["pkg"] == pacote:
        registros.append(atual)
    return registros


def registrar(pasta_sessao: str | Path, app: str, pacote: str) -> int:
    arq = Path(pasta_sessao) / "notificacoes.csv"
    novo = not arq.exists()
    regs = _ler_dumpsys(pacote)
    with arq.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for r in regs:
            w.writerow({"data": date.today().isoformat(), "app": app, "titulo": r["titulo"], "texto": r["texto"],
                        "origem": "dumpsys"})
    return len(regs)


def por_dia(linhas: list[dict]) -> dict[str, int]:
    cont: dict[str, int] = {}
    for l in linhas:
        cont[l.get("data", "")] = cont.get(l.get("data", ""), 0) + 1
    return cont
