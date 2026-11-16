from antipadroes import verificador
from conftest import FIXTURES


def _vereditos(r):
    return {c["cenario"].split(" -- ")[0]: c["veredito"] for c in r["cenarios"]}


def test_f01_reprova_requisitos_violados():
    r = verificador.verificar(FIXTURES / "F01")
    v = _vereditos(r)
    assert r["resumo"] == {"aprovado": 0, "reprovado": 10, "indecidivel": 5}
    assert v["Excluir a conta não custa mais do que criá-la"] == "reprovado"
    assert v["Cancelar não custa mais do que assinar"] == "indecidivel"     # P4 não observável


def test_f02_aprova_requisitos_atendidos():
    r = verificador.verificar(FIXTURES / "F02")
    assert r["resumo"]["reprovado"] == 0 and r["resumo"]["aprovado"] == 11
    manuais = [c for c in r["cenarios"] if "manual" in c["tags"]]
    assert manuais and all(c["veredito"] == "indecidivel" for c in manuais)
