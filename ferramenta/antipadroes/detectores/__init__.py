from .base import Achado, Detector
from .d1_rolagem import RolagemSemParada
from .d2_reproducao import ReproducaoAutomatica
from .d3_permissao import PermissaoOportunista
from .d4_saida_obstruida import SaidaObstruida
from .d5_textos import AmeacaECulpabilizacao

TODOS = [RolagemSemParada, ReproducaoAutomatica, PermissaoOportunista, SaidaObstruida, AmeacaECulpabilizacao]


def detectar(sessao, codigos=None) -> list[Achado]:
    achados = []
    for cls in TODOS:
        if codigos and cls.codigo not in codigos:
            continue
        achados.extend(cls().detectar(sessao))
    return achados


__all__ = ["Achado", "Detector", "TODOS", "detectar", "RolagemSemParada", "ReproducaoAutomatica",
           "PermissaoOportunista", "SaidaObstruida", "AmeacaECulpabilizacao"]
