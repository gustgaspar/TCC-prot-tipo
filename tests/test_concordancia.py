import pytest

from antipadroes import concordancia


def test_fleiss_exemplo_classico():
    # Exemplo de Fleiss (1971) reproduzido em várias referências: 10 itens, 14 avaliadores, 5 categorias.
    tabela = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
              [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]
    avaliacoes = [[str(c) for c, n in enumerate(linha) for _ in range(n)] for linha in tabela]
    assert concordancia.fleiss(avaliacoes) == pytest.approx(0.210, abs=0.001)


def test_cohen():
    a = ["1", "1", "0", "0", "1", "0", "1", "1"]
    b = ["1", "0", "0", "0", "1", "0", "1", "1"]
    assert concordancia.cohen(a, b) == pytest.approx(0.75)


def test_resumo_csv(tmp_path):
    arq = tmp_path / "cod.csv"
    arq.write_text("app,unidade,antipadrao,codificador_1,codificador_2,codificador_3\n"
                   "A01,P1,AR07,1,1,1\nA01,P2,AR05,0,0,0\nA01,tela:t1.png,AR06,1,1,0\nA02,P1,AR07,0,0,0\n", encoding="utf-8")
    r = concordancia.resumo(arq)
    assert r["metodo"] == "Fleiss" and r["itens"] == 4 and r["divergencias"] == ["A01/tela:t1.png/AR06"]


def test_interpretacao():
    assert concordancia.interpretar(0.65) == "substancial"
