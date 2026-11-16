"""Modelo de dados de uma sessão de inspeção.

Uma *sessão* é a inspeção de um aplicativo (manual ou automatizada) e fica em uma pasta:

    sessoes/A01/
        meta.json            metadados (app, categoria, versão, dispositivo, data, modo)
        acoes.jsonl          uma ação por linha, na ordem em que foi executada
        telas/               capturas (PNG) e hierarquias de views (XML) de cada passo
        notificacoes.csv     opcional: notificações recebidas no período de observação

A inspeção manual (ficha CSV do Apêndice A) e o coletor automatizado produzem o mesmo
formato, de modo que IAF, detectores, requisitos e relatório funcionam para ambos.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Optional

# Tipos de ação reconhecidos. "espera" e "observacao" não contam como ação do usuário.
ACOES_DO_USUARIO = {"toque", "gesto", "digitacao", "voltar"}
FLUXOS = {"engajamento", "saida", "transversal"}
PARES = {"P1", "P2", "P3", "P4", "P5"}


@dataclass
class Acao:
    passo: int
    par: str                      # P1..P5 ou "-" para observações transversais
    fluxo: str                    # engajamento | saida | transversal
    acao: str                     # toque | gesto | digitacao | voltar | espera | observacao
    descricao: str = ""
    operador_klm: str = ""        # ex.: "M P" (preenchido automaticamente se vazio)
    caracteres: int = 0           # caracteres digitados (digitação)
    segundos: float = 0.0         # duração (esperas)
    tela: str = ""                # arquivo da captura, relativo a telas/
    hierarquia: str = ""          # arquivo XML da hierarquia, relativo a telas/
    canal_externo: bool = False   # o passo levou para fora do aplicativo (navegador, e-mail...)
    pacote: str = ""              # pacote Android em primeiro plano após o passo
    gatilho: str = ""             # intenção do usuário relacionada (ex.: "notificacoes")
    codigo_candidato: str = ""    # código do catálogo anotado pelo pesquisador (ARxx)
    observacoes: str = ""

    @property
    def do_usuario(self) -> bool:
        return self.acao in ACOES_DO_USUARIO


@dataclass
class Sessao:
    pasta: Path
    meta: dict = field(default_factory=dict)
    acoes: list[Acao] = field(default_factory=list)

    # ---------- leitura e escrita ----------
    @classmethod
    def carregar(cls, pasta: str | Path) -> "Sessao":
        pasta = Path(pasta)
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
        acoes = []
        arq = pasta / "acoes.jsonl"
        if arq.exists():
            for linha in arq.read_text(encoding="utf-8").splitlines():
                if linha.strip():
                    acoes.append(Acao(**json.loads(linha)))
        return cls(pasta=pasta, meta=meta, acoes=acoes)

    def salvar(self) -> None:
        self.pasta.mkdir(parents=True, exist_ok=True)
        (self.pasta / "telas").mkdir(exist_ok=True)
        (self.pasta / "meta.json").write_text(json.dumps(self.meta, ensure_ascii=False, indent=2), encoding="utf-8")
        with (self.pasta / "acoes.jsonl").open("w", encoding="utf-8") as f:
            for a in self.acoes:
                f.write(json.dumps(asdict(a), ensure_ascii=False) + "\n")

    def registrar(self, acao: Acao) -> None:
        self.acoes.append(acao)
        with (self.pasta / "acoes.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(acao), ensure_ascii=False) + "\n")

    # ---------- consultas ----------
    @property
    def app(self) -> str:
        return self.meta.get("app", self.pasta.name)

    def fluxo(self, par: str, fluxo: str) -> list[Acao]:
        return [a for a in self.acoes if a.par == par and a.fluxo == fluxo]

    def tem_fluxo(self, par: str, fluxo: str) -> bool:
        return any(a.do_usuario for a in self.fluxo(par, fluxo))

    def nao_observavel(self, par: str) -> bool:
        return par in set(self.meta.get("pares_nao_observaveis", []))

    def nao_aplicavel(self, par: str) -> bool:
        return par in set(self.meta.get("pares_nao_aplicaveis", []))

    def caminho_tela(self, nome: str) -> Path:
        return self.pasta / "telas" / nome

    def hierarquia(self, acao: Acao) -> Optional[str]:
        if not acao.hierarquia:
            return None
        p = self.caminho_tela(acao.hierarquia)
        return p.read_text(encoding="utf-8") if p.exists() else None

    def notificacoes(self) -> list[dict]:
        arq = self.pasta / "notificacoes.csv"
        if not arq.exists():
            return []
        with arq.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))


def carregar_sessoes(pastas: Iterable[str | Path]) -> list[Sessao]:
    return [Sessao.carregar(p) for p in pastas]
