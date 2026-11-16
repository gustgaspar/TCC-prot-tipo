"""Testa o coletor com um driver falso (sem Appium nem emulador)."""
from antipadroes.coletor import Coletor
from antipadroes.modelo import Sessao


class Elemento:
    def __init__(self, drv, chave):
        self.drv, self.chave = drv, chave

    def click(self):
        self.drv.eventos.append(("click", self.chave))
        if self.chave == "Abrir no site":
            self.drv.current_package = "com.android.chrome"

    def send_keys(self, t):
        self.drv.eventos.append(("keys", t))


class DriverFalso:
    def __init__(self):
        self.eventos, self.current_package, self.n = [], "com.exemplo.app", 0

    def find_element(self, by, valor):
        chave = valor.split('"')[1] if "textContains" in valor else valor
        return Elemento(self, chave)

    def get_window_size(self):
        return {"width": 1080, "height": 2400}

    def swipe(self, *a):
        self.eventos.append(("swipe",) + a)

    def back(self):
        self.eventos.append(("back",))

    def get_screenshot_as_file(self, caminho):
        open(caminho, "wb").write(b"\x89PNG")

    @property
    def page_source(self):
        self.n += 1
        return f'<hierarchy><node text="tela {self.n}" package="{self.current_package}" bounds="[0,0][10,10]"/></hierarchy>'


def test_coletor_registra_passos(tmp_path, monkeypatch):
    monkeypatch.setenv("SENHA_TESTE", "segredo")
    s = Sessao(pasta=tmp_path / "A99", meta={"app": "A99"})
    s.salvar()
    drv = DriverFalso()
    roteiro = {"par": "P1", "fluxo": "saida", "passos": [
        {"acao": "toque", "alvo": {"texto": "Perfil"}},
        {"acao": "digitacao", "alvo": {"id": "senha"}, "texto": "${ENV:SENHA_TESTE}"},
        {"acao": "gesto", "direcao": "cima", "repeticoes": 2, "descricao": "rolar"},
        {"acao": "toque", "alvo": {"texto": "Abrir no site"}},
    ]}
    Coletor(drv, s, "com.exemplo.app", pausa=0).executar(roteiro)
    s2 = Sessao.carregar(tmp_path / "A99")
    assert [a.acao for a in s2.acoes] == ["toque", "digitacao", "gesto", "gesto", "toque"]
    assert s2.acoes[1].caracteres == len("segredo") and ("keys", "segredo") in drv.eventos
    assert s2.acoes[-1].canal_externo and not s2.acoes[0].canal_externo
    assert (tmp_path / "A99" / "telas" / "tela_0005.xml").exists()
    assert "segredo" not in (tmp_path / "A99" / "acoes.jsonl").read_text()   # credencial não é gravada
