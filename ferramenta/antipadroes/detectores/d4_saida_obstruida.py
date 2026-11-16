"""D4 – Saída obstruída (AR07, AR08).

Regra (Quadro 3-8): calcula o IAF a partir do registro de ações dos pares P1 (criar ↔ excluir
conta) e P4 (assinar ↔ cancelar) e sinaliza quando sair custa mais do que entrar (IAF > 1)
ou quando a saída abre canal externo ao aplicativo (navegador, e-mail, atendimento).
"""
from __future__ import annotations

from .. import iaf
from ..modelo import Sessao
from .base import Achado, Detector

PAR_PARA_ANTIPADRAO = {"P1": "AR07", "P4": "AR08"}


class SaidaObstruida(Detector):
    codigo = "D4"
    nome = "Saída obstruída"
    antipadroes = ("AR07", "AR08")

    def __init__(self, limite: float = 1.0):
        self.limite = limite

    def detectar(self, sessao: Sessao) -> list[Achado]:
        achados = []
        for par, ap in PAR_PARA_ANTIPADRAO.items():
            r = iaf.calcular(sessao, par)
            if r.situacao != "calculado":
                continue
            motivos = []
            if r.iaf_acoes is not None and r.iaf_acoes > self.limite:
                motivos.append(f"sair exige {r.acoes_saida} ações e entrar {r.acoes_engajamento} (IAF = {r.iaf_acoes:.2f})")
            if r.canal_externo:
                motivos.append("a saída exige canal externo ao aplicativo")
            if motivos:
                saida = sessao.fluxo(par, "saida")
                ultimo = next((a for a in reversed(saida) if a.tela), saida[-1])
                achados.append(Achado(
                    detector=self.codigo, antipadrao=ap, app=sessao.app, unidade=par,
                    descricao="; ".join(motivos), passo=ultimo.passo, tela=ultimo.tela,
                    hierarquia=ultimo.hierarquia,
                    evidencia={"iaf_acoes": r.iaf_acoes, "iaf_tempo": r.iaf_tempo,
                               "acoes_engajamento": r.acoes_engajamento, "acoes_saida": r.acoes_saida,
                               "canal_externo": r.canal_externo},
                ))
        return achados
