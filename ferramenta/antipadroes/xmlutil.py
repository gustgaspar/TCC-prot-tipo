"""Leitura de hierarquias de views do Android (dump do UI Automator ou page source do Appium)."""
from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

_BOUNDS = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")


@dataclass
class No:
    classe: str
    texto: str
    descricao: str
    rid: str
    pacote: str
    clicavel: bool
    rolavel: bool
    marcavel: bool
    marcado: bool
    bounds: Optional[tuple[int, int, int, int]]

    @property
    def rotulo(self) -> str:
        return (self.texto or self.descricao or "").strip()

    @property
    def area(self) -> int:
        if not self.bounds:
            return 0
        x1, y1, x2, y2 = self.bounds
        return max(0, x2 - x1) * max(0, y2 - y1)


def _bool(v: Optional[str]) -> bool:
    return str(v).lower() == "true"


def nos(xml: Optional[str]) -> list[No]:
    if not xml:
        return []
    try:
        raiz = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
    except ET.ParseError:
        return []
    out = []
    for el in raiz.iter():
        if el.tag == "hierarchy":
            continue
        b = _BOUNDS.match(el.get("bounds", ""))
        out.append(No(
            classe=el.get("class") or el.tag,
            texto=el.get("text") or "",
            descricao=el.get("content-desc") or "",
            rid=el.get("resource-id") or "",
            pacote=el.get("package") or "",
            clicavel=_bool(el.get("clickable")),
            rolavel=_bool(el.get("scrollable")),
            marcavel=_bool(el.get("checkable")),
            marcado=_bool(el.get("checked")),
            bounds=tuple(int(g) for g in b.groups()) if b else None,
        ))
    return out


def textos(xml: Optional[str]) -> list[str]:
    return [n.rotulo for n in nos(xml) if n.rotulo]


def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para casar padrões textuais com tolerância."""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.lower()).strip()


def assinatura_de_conteudo(xml: Optional[str]) -> set[str]:
    """Conjunto de rótulos sem números (descarta cronômetros e contadores)."""
    out = set()
    for t in textos(xml):
        t = re.sub(r"\d+", "", normalizar(t)).strip(" :/.-")
        if len(t) >= 3:
            out.add(t)
    return out


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)
