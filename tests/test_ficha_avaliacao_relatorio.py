import csv
import shutil
from pathlib import Path

from antipadroes import avaliacao, detectores, ficha, iaf, notificacoes, relatorio
from antipadroes.modelo import Sessao

RAIZ = Path(__file__).resolve().parents[1]


def test_ficha_exemplo_vira_sessao(tmp_path):
    s = ficha.converter(RAIZ / "protocolo" / "ficha_exemplo.csv", tmp_path / "A00", nao_aplicaveis=["P3", "P4", "P5"])
    r = iaf.calcular(Sessao.carregar(s.pasta), "P1")
    assert r.situacao == "calculado" and r.iaf_acoes == 2.0 and r.canal_externo


def test_avaliacao_contra_oraculo(f01):
    oraculo = {("F01", "P1", "AR07"): True, ("F01", "P4", "AR08"): True,          # FN em AR08 (não detectado)
               ("F01", "passo:1", "AR06"): True, ("F01", "passo:33", "AR09"): False}  # FP em AR09
    r = avaliacao.avaliar(detectores.detectar(f01), oraculo, {"F01"})
    d4, d5 = r["por_detector"]["D4"], r["por_detector"]["D5"]
    assert (d4["vp"], d4["fn"], d4["revocacao"]) == (1, 1, 0.5)
    assert d5["fp"] == 1 and d5["precisao"] == 0.0
    assert "F01/notificacao:5/AR03" in r["nao_codificados"]


def test_relatorio_html(tmp_path, f01):
    destino = tmp_path / "F01"
    shutil.copytree(f01.pasta, destino)
    s = Sessao.carregar(destino)
    h, j = relatorio.gerar(s, detectores.detectar(s))
    texto = h.read_text(encoding="utf-8")
    assert "Índice de assimetria de fricção" in texto and "AR07" in texto and j.exists()


def test_dumpsys_parser():
    saida = """  NotificationRecord(0x1 pkg=com.exemplo.app user=UserHandle{0} id=1)
      android.title=String (Não perca!)
      android.text=String (Sua ofensiva vai acabar)
  NotificationRecord(0x2 pkg=com.outro.app user=UserHandle{0} id=2)
      android.title=String (Outro)"""
    regs = notificacoes.analisar_dumpsys(saida, "com.exemplo.app")
    assert regs == [{"pkg": "com.exemplo.app", "titulo": "Não perca!", "texto": "Sua ofensiva vai acabar"}]
