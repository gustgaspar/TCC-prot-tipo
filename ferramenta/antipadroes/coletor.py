"""Coletor (módulo 1 da Figura 3-2): executa roteiros de fluxo com Appium + UiAutomator2.

A cada passo registra: captura de tela (PNG), hierarquia de views (XML), ação executada com o
operador KLM, pacote em primeiro plano e indicação de canal externo. O resultado é uma sessão
no mesmo formato da inspeção manual (ver modelo.py).

Formato do roteiro (YAML) — ver ferramenta/roteiros/exemplo_A01_P1.yaml:
    app: A01
    pacote: com.exemplo.app          # pacote Android do aplicativo
    atividade: .MainActivity         # opcional
    par: P1
    fluxo: saida                     # engajamento | saida | transversal
    passos:
      - {acao: toque, alvo: {id: "com.exemplo:id/perfil"}, descricao: "Abrir perfil"}
      - {acao: toque, alvo: {texto: "Configurações"}}
      - {acao: digitacao, alvo: {id: "...:id/senha"}, texto: "${ENV:SENHA_A01}"}
      - {acao: gesto, direcao: cima, repeticoes: 5, descricao: "rolar feed"}
      - {acao: espera, segundos: 10, descricao: "aguardar fim do vídeo"}
      - {acao: voltar}
      - {acao: observacao, descricao: "capturar estado atual"}
Campos opcionais por passo: gatilho (ex.: "notificacoes"), canal_externo (força o valor),
operador_klm (sobrepõe o padrão), codigo_candidato.
Credenciais nunca são escritas no roteiro: use ${ENV:NOME_DA_VARIAVEL}.
"""
from __future__ import annotations

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .modelo import Acao, Sessao

PACOTES_SISTEMA = {
    "com.android.permissioncontroller", "com.google.android.permissioncontroller",
    "com.android.packageinstaller", "com.google.android.inputmethod.latin", "com.android.systemui",
    "com.google.android.gms",
}
_ENV = re.compile(r"\$\{ENV:([A-Z0-9_]+)\}")


def _appium_by():
    try:
        from appium.webdriver.common.appiumby import AppiumBy
        return AppiumBy
    except ImportError:  # permite testar o coletor com um driver falso, sem o Appium instalado
        class AppiumBy:
            ID, ACCESSIBILITY_ID, XPATH, ANDROID_UIAUTOMATOR = "id", "accessibility id", "xpath", "-android uiautomator"
        return AppiumBy


def _expandir(texto: str) -> str:
    def troca(m):
        v = os.environ.get(m.group(1))
        if v is None:
            raise KeyError(f"variável de ambiente {m.group(1)} não definida")
        return v
    return _ENV.sub(troca, texto)


class Coletor:
    def __init__(self, driver: Any, sessao: Sessao, pacote_app: str, pausa: float = 1.0):
        self.driver = driver
        self.sessao = sessao
        self.pacote_app = pacote_app
        self.pausa = pausa
        self.sessao.pasta.mkdir(parents=True, exist_ok=True)
        (self.sessao.pasta / "telas").mkdir(exist_ok=True)
        self.passo = max((a.passo for a in sessao.acoes), default=0)

    # ---------- localização de elementos ----------
    def _encontrar(self, alvo: dict):
        AppiumBy = _appium_by()
        if "id" in alvo:
            return self.driver.find_element(AppiumBy.ID, alvo["id"])
        if "desc" in alvo:
            return self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, alvo["desc"])
        if "texto" in alvo:
            t = alvo["texto"].replace('"', '\\"')
            return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{t}")')
        if "xpath" in alvo:
            return self.driver.find_element(AppiumBy.XPATH, alvo["xpath"])
        if "uiautomator" in alvo:
            return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, alvo["uiautomator"])
        raise ValueError(f"alvo sem localizador reconhecido: {alvo}")

    # ---------- execução ----------
    def _capturar(self) -> tuple[str, str]:
        base = f"tela_{self.passo:04d}"
        self.driver.get_screenshot_as_file(str(self.sessao.caminho_tela(base + ".png")))
        self.sessao.caminho_tela(base + ".xml").write_text(self.driver.page_source, encoding="utf-8")
        return base + ".png", base + ".xml"

    def _gesto(self, direcao: str, duracao_ms: int = 400):
        tam = self.driver.get_window_size()
        w, h = tam["width"], tam["height"]
        cx, cy = w // 2, h // 2
        d = {"cima": (cx, int(h * 0.75), cx, int(h * 0.25)), "baixo": (cx, int(h * 0.25), cx, int(h * 0.75)),
             "esquerda": (int(w * 0.8), cy, int(w * 0.2), cy), "direita": (int(w * 0.2), cy, int(w * 0.8), cy)}[direcao]
        self.driver.swipe(*d, duracao_ms)

    def executar_passo(self, p: dict, par: str, fluxo: str) -> list[Acao]:
        tipo = p["acao"]
        repeticoes = int(p.get("repeticoes", 1)) if tipo == "gesto" else 1
        registradas = []
        for _ in range(repeticoes):
            caracteres, segundos = 0, 0.0
            if tipo == "toque":
                self._encontrar(p["alvo"]).click()
            elif tipo == "digitacao":
                texto = _expandir(str(p.get("texto", "")))
                el = self._encontrar(p["alvo"])
                el.click()
                el.send_keys(texto)
                caracteres = len(texto)
            elif tipo == "gesto":
                self._gesto(p.get("direcao", "cima"), int(p.get("duracao_ms", 400)))
            elif tipo == "voltar":
                self.driver.back()
            elif tipo == "espera":
                segundos = float(p.get("segundos", 5))
                time.sleep(segundos)
            elif tipo == "abrir_app":
                self.driver.activate_app(self.pacote_app)
            elif tipo == "observacao":
                pass
            else:
                raise ValueError(f"ação desconhecida: {tipo}")
            if tipo not in {"espera", "observacao"}:
                time.sleep(self.pausa)
            self.passo += 1
            tela, hier = self._capturar()
            pacote = getattr(self.driver, "current_package", "") or ""
            externo = p.get("canal_externo")
            if externo is None:
                externo = bool(pacote) and pacote != self.pacote_app and pacote not in PACOTES_SISTEMA
            acao = Acao(passo=self.passo, par=par, fluxo=fluxo, acao="toque" if tipo == "abrir_app" else tipo,
                        descricao=p.get("descricao", ""), operador_klm=p.get("operador_klm", ""),
                        caracteres=caracteres, segundos=segundos, tela=tela, hierarquia=hier,
                        canal_externo=bool(externo), pacote=pacote, gatilho=p.get("gatilho", ""),
                        codigo_candidato=p.get("codigo_candidato", ""))
            self.sessao.registrar(acao)
            registradas.append(acao)
        return registradas

    def executar(self, roteiro: dict) -> list[Acao]:
        par, fluxo = roteiro.get("par", "-"), roteiro.get("fluxo", "transversal")
        out = []
        for p in roteiro["passos"]:
            out.extend(self.executar_passo(p, par, fluxo))
        return out


def ler_roteiro(caminho: str | Path) -> dict:
    import yaml
    return yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))


def criar_driver(roteiro: dict, servidor: str = "http://127.0.0.1:4723", dispositivo: str | None = None):
    """Cria a sessão Appium (UiAutomator2) sem reinstalar nem limpar o aplicativo."""
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    op = UiAutomator2Options()  # já define platformName=Android e automationName=UiAutomator2
    op.app_package = roteiro["pacote"]
    if roteiro.get("atividade"):
        op.app_activity = roteiro["atividade"]
    op.no_reset = True
    op.new_command_timeout = 300
    if dispositivo:
        op.udid = dispositivo
    return webdriver.Remote(servidor, options=op)


def coletar(roteiros: list[str | Path], pasta_sessao: str | Path, servidor: str, meta_extra: dict | None = None) -> Sessao:
    pasta = Path(pasta_sessao)
    sessao = Sessao.carregar(pasta) if (pasta / "meta.json").exists() else Sessao(pasta=pasta)
    primeiro = ler_roteiro(roteiros[0])
    if not sessao.meta:
        sessao.meta = {"app": primeiro["app"], "categoria": primeiro.get("categoria", ""), "modo": "automatico",
                       "data": datetime.now().isoformat(timespec="seconds"), "pares_nao_aplicaveis": [],
                       "pares_nao_observaveis": [], **(meta_extra or {})}
        sessao.salvar()
    driver = criar_driver(primeiro, servidor)
    try:
        caps = getattr(driver, "capabilities", {}) or {}
        sessao.meta.setdefault("dispositivo", caps.get("deviceName", ""))
        sessao.meta.setdefault("versao_android", caps.get("platformVersion", ""))
        try:
            info = driver.execute_script("mobile: shell", {"command": "dumpsys", "args": ["package", primeiro["pacote"]]})
            m = re.search(r"versionName=(\S+)", str(info))
            if m:
                sessao.meta["versao_app"] = m.group(1)
        except Exception:  # requer appium --allow-insecure adb_shell; versão pode ser anotada à mão
            pass
        (sessao.pasta / "meta.json").write_text(__import__("json").dumps(sessao.meta, ensure_ascii=False, indent=2), encoding="utf-8")
        col = Coletor(driver, sessao, primeiro["pacote"])
        for r in roteiros:
            col.executar(ler_roteiro(r))
    finally:
        driver.quit()
    return sessao
