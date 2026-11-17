import csv
from pathlib import Path

from antipadroes import cli, piloto

RAIZ = Path(__file__).resolve().parents[1]
EXEMPLO = RAIZ / "protocolo" / "ficha_exemplo.csv"


def _montar(tmp_path: Path) -> Path:
    p = tmp_path / "piloto"
    (p / "fichas").mkdir(parents=True)
    (p / "apps.csv").write_text("codigo,categoria,nao_aplicaveis,nao_observaveis,dias_notificacoes\n"
                                "A00,Exemplo,P2 P3 P4 P5,,3\n", encoding="utf-8")
    linhas = EXEMPLO.read_text(encoding="utf-8").splitlines()
    (p / "fichas" / "A00_ana.csv").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    # o segundo inspetor não registrou o passo "Selecionar motivo" (diverge na contagem da saída)
    (p / "fichas" / "A00_bia.csv").write_text("\n".join(l for l in linhas if "Selecionar motivo" not in l) + "\n", encoding="utf-8")
    (p / "fichas" / "A01_ninguem.csv").write_text(linhas[0] + "\n", encoding="utf-8")   # ficha só com cabeçalho
    return p


def _marcar(arq: Path, valores: list[str]):
    with arq.open(encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        campos, linhas = leitor.fieldnames, list(leitor)
    col = next(c for c in campos if c.startswith("codificador"))
    for l, v in zip(linhas, valores):
        l[col] = v
    with arq.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def test_sem_dados_nao_inventa_nada(tmp_path):
    p = tmp_path / "piloto"
    p.mkdir()
    r = piloto.executar(p, ["x", "y", "z"])
    assert r["sessoes_manuais"] == [] and r["planilhas_criadas"] == []
    texto = (p / "resultados.md").read_text(encoding="utf-8")
    assert "Ainda não há planilhas" in texto


def test_piloto_de_ponta_a_ponta(tmp_path):
    p = _montar(tmp_path)
    r = piloto.executar(p, ["ana", "bia", "caio"])
    assert r["sessoes_manuais"] == ["A00_ana", "A00_bia"]          # ficha vazia é ignorada
    assert (p / "iaf.csv").exists()
    planilhas = sorted((p / "codificacao" / "rodada1").glob("*.csv"))
    assert [x.stem for x in planilhas] == ["ana", "bia", "caio"]

    unidades = piloto.unidades([__import__("antipadroes").modelo.Sessao.carregar(p / "sessoes" / "A00_ana")])
    assert ("A00", "P1", "AR07") == unidades[0][:3]
    assert any(u[1] == "tela:A00_015.png" and u[2] == "AR09" for u in unidades)
    n = len(unidades)

    # rodada 1 ainda em branco: kappa indisponível, sem erro
    assert piloto.executar(p, ["ana", "bia", "caio"])["kappas"] == {1: None}

    _marcar(planilhas[0], ["1"] * n)
    _marcar(planilhas[1], ["1"] * n)
    _marcar(planilhas[2], ["1"] * (n - 1) + ["0"])
    r = piloto.executar(p, ["ana", "bia", "caio"])
    k = r["kappas"][1]
    assert k["metodo"] == "Fleiss" and k["itens"] == n and len(k["divergencias"]) == 1

    texto = (p / "resultados.md").read_text(encoding="utf-8")
    assert "| Inspetores com ficha | ana, bia |" in texto
    assert "2,00" in texto and "–" in texto                       # IAF diverge entre inspetores (intervalo)
    assert "P1 sair: ana 12, bia 11" in texto
    assert "P1" in texto.split("Saída por canal externo?")[1].split("\n")[0]
    assert "| Antipadrões codificados (maioria) | AR07 (3), AR09 (1) |" in texto   # P1 + telas 016 e 018
    assert "não aplicável" in texto


def test_planilhas_existentes_nao_sao_sobrescritas(tmp_path):
    p = _montar(tmp_path)
    piloto.executar(p, ["ana"])
    arq = p / "codificacao" / "rodada1" / "ana.csv"
    _marcar(arq, ["1"])
    piloto.executar(p, ["ana"])
    assert ",1," in arq.read_text(encoding="utf-8")


def test_cli_piloto(tmp_path, capsys):
    p = _montar(tmp_path)
    assert cli.main(["piloto", str(p), "--codificadores", "ana", "bia"]) == 0
    saida = capsys.readouterr().out
    assert "A00_ana" in saida and "resultados →" in saida
