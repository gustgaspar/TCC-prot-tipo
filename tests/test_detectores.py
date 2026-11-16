from antipadroes import detectores
from antipadroes.detectores.d5_textos import classificar


def _codigos(achados):
    return sorted((a.detector, a.antipadrao) for a in achados)


def test_f01_todos_os_detectores_disparam(f01):
    assert _codigos(detectores.detectar(f01)) == [
        ("D1", "AR01"), ("D2", "AR02"), ("D2", "AR10"), ("D3", "AR06"), ("D4", "AR07"), ("D5", "AR03"), ("D5", "AR09")]


def test_f02_sem_falsos_positivos(f02):
    assert detectores.detectar(f02) == []


def test_d4_unidade_e_evidencia(f01):
    (a,) = detectores.SaidaObstruida().detectar(f01)
    assert a.unidade == "P1" and a.evidencia["iaf_acoes"] == 2.0 and a.evidencia["canal_externo"]


def test_d4_limite_configuravel(f01):
    assert detectores.SaidaObstruida(limite=3.0).detectar(f01)[0].descricao.startswith("a saída exige canal externo")


def test_d5_padroes_textuais():
    assert classificar("Não perca sua ofensiva!")[0][0] == "AR03"
    assert classificar("Sua sequência vai acabar hoje")[0][0] == "AR03"
    assert classificar("Tem certeza que deseja cancelar?")[0][0] == "AR09"
    assert classificar("Não, prefiro pagar mais")[0][0] == "AR09"
    assert classificar("Sua lição de hoje está pronta") == []


def test_d3_ignora_pedido_apos_acao_relacionada(f02):
    assert detectores.PermissaoOportunista().detectar(f02) == []


def test_d1_marcador_de_fim_evita_achado(f02):
    assert detectores.RolagemSemParada().detectar(f02) == []
