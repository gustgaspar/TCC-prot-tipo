import pytest

from antipadroes import iaf, klm
from antipadroes.modelo import Acao


def test_klm_toque_e_digitacao():
    a = [Acao(1, "P1", "engajamento", "toque"), Acao(2, "P1", "engajamento", "digitacao", caracteres=4),
         Acao(3, "P1", "engajamento", "espera", segundos=10)]
    assert klm.numero_de_acoes(a) == 2               # espera não conta
    assert klm.tempo(a) == pytest.approx(1.35 + 1.10 + 1.35 + 4 * 0.28)


def test_operador_invalido():
    with pytest.raises(ValueError):
        klm.operadores(Acao(1, "P1", "saida", "toque", operador_klm="Z"))


def test_iaf_f01_saida_obstruida(f01):
    r = iaf.calcular(f01, "P1")
    assert (r.acoes_engajamento, r.acoes_saida, r.iaf_acoes) == (6, 12, 2.0)
    assert r.canal_externo and r.obstrucao


def test_iaf_situacoes(f01):
    assert iaf.calcular(f01, "P4").situacao == "nao_observavel"
    assert iaf.calcular(f01, "P5").situacao == "nao_aplicavel"


def test_iaf_f02_conforme(f02):
    r = iaf.calcular(f02, "P1")
    assert r.iaf_acoes == pytest.approx(0.83) and not r.obstrucao


def test_exportar_csv(tmp_path, f01, f02):
    destino = tmp_path / "iaf.csv"
    iaf.exportar_csv(iaf.calcular_todos([f01, f02]), destino)
    linhas = destino.read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 1 + 10 and "iaf_acoes" in linhas[0]
