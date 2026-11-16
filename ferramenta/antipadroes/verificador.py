"""Verificador de requisitos (módulo 3 da Figura 3-2): executa a biblioteca Gherkin com behave.

Cada cenário termina em um de três vereditos:
  aprovado     — o requisito foi atendido;
  reprovado    — o requisito foi violado (o teste falha, como qualquer teste de aceitação);
  indecidível  — a sessão não tem evidência suficiente (par não aplicável, não observável ou
                 cenário marcado @manual); o motivo é registrado.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REQUISITOS = RAIZ / "requisitos"


def verificar(pasta_sessao: str | Path, tags: str | None = None, saida: str | Path | None = None) -> dict:
    pasta = Path(pasta_sessao).resolve()
    resultado = Path(saida) if saida else pasta / "requisitos.jsonl"
    if resultado.exists():
        resultado.unlink()
    cmd = [sys.executable, "-m", "behave", str(REQUISITOS), "-D", f"sessao={pasta}", "-D", f"saida={resultado}",
           "--no-capture", "--format", "progress", "--no-summary"]
    if tags:
        cmd += ["--tags", tags]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ)
    linhas = [json.loads(l) for l in resultado.read_text(encoding="utf-8").splitlines() if l.strip()] if resultado.exists() else []
    resumo = {"aprovado": 0, "reprovado": 0, "indecidivel": 0}
    for l in linhas:
        resumo[l["veredito"]] = resumo.get(l["veredito"], 0) + 1
    decidiveis = resumo["aprovado"] + resumo["reprovado"]
    total = decidiveis + resumo["indecidivel"]
    return {"app": pasta.name, "cenarios": linhas, "resumo": resumo,
            "proporcao_decidivel": round(decidiveis / total, 3) if total else None,
            "codigo_saida_behave": proc.returncode, "log": proc.stdout[-4000:] + proc.stderr[-4000:]}
