"""Ambiente do behave: carrega a sessão indicada por -D sessao=<pasta> e registra o veredito
de cada cenário (aprovado, reprovado ou indecidível) em -D saida=<arquivo.jsonl>."""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramenta"))

from antipadroes.modelo import Sessao  # noqa: E402


class Indecidivel(Exception):
    """Levantada por um passo quando a sessão não tem evidência para decidir o requisito."""


def before_all(context):
    ud = context.config.userdata
    pasta = ud.get("sessao")
    if not pasta:
        raise SystemExit("informe a sessão: behave requisitos -D sessao=<pasta da sessão>")
    context.sessao = Sessao.carregar(pasta)
    context.saida = Path(ud.get("saida", Path(pasta) / "requisitos.jsonl"))
    context.saida.parent.mkdir(parents=True, exist_ok=True)
    context._achados = None


def before_scenario(context, scenario):
    context.motivo = ""
    context.fluxo_atual = None
    if "manual" in scenario.effective_tags:
        context.motivo = "cenário marcado @manual: requer inspeção humana"
        scenario.skip(context.motivo)


def after_scenario(context, scenario):
    status = scenario.status.name if hasattr(scenario.status, "name") else str(scenario.status)
    if status == "passed":
        veredito = "aprovado"
    elif status == "failed":
        # um passo que levantou Indecidivel conta como indecidível, não como violação
        exc = next((s.exception for s in scenario.steps if getattr(s, "exception", None)), None)
        if isinstance(exc, Indecidivel):
            veredito, context.motivo = "indecidivel", str(exc)
        else:
            veredito = "reprovado"
            if exc is not None and not context.motivo:
                context.motivo = str(exc).splitlines()[0][:300]
    else:
        veredito = "indecidivel"
        context.motivo = context.motivo or "sem evidência"
    reg = {"app": context.sessao.app, "funcionalidade": scenario.feature.name, "cenario": scenario.name,
           "tags": sorted(scenario.effective_tags), "veredito": veredito, "motivo": context.motivo}
    with context.saida.open("a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
