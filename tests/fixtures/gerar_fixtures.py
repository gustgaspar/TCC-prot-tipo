"""Gera duas sessões sintéticas usadas nos testes e na integração contínua.

F01 – aplicativo fictício que VIOLA os requisitos (saída obstruída, permissão antes de qualquer
      ação, reprodução automática ativa, feed sem fim, textos de ameaça e culpabilização,
      excesso de notificações).
F02 – aplicativo fictício CONFORME.
As telas são hierarquias XML no formato do UI Automator; não há capturas PNG.
Uso: python tests/fixtures/gerar_fixtures.py
"""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI / "sessoes"


def node(cls="android.widget.TextView", text="", rid="", pkg="", desc="", clickable=False, scrollable=False,
         checkable=False, checked=False, bounds=(0, 0, 1080, 120), filhos=""):
    b = f"[{bounds[0]},{bounds[1]}][{bounds[2]},{bounds[3]}]"
    return (f'<node index="0" text="{text}" resource-id="{rid}" class="{cls}" package="{pkg}" content-desc="{desc}" '
            f'checkable="{str(checkable).lower()}" checked="{str(checked).lower()}" clickable="{str(clickable).lower()}" '
            f'enabled="true" focusable="false" focused="false" scrollable="{str(scrollable).lower()}" long-clickable="false" '
            f'password="false" selected="false" bounds="{b}">{filhos}</node>')


def tela(pkg, *filhos):
    raiz = node(cls="android.widget.FrameLayout", pkg=pkg, bounds=(0, 0, 1080, 2400), filhos="".join(filhos))
    return f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><hierarchy rotation=\"0\">{raiz}</hierarchy>"


def botao(pkg, texto, y=1800, largura=800, altura=150):
    x = (1080 - largura) // 2
    return node(cls="android.widget.Button", text=texto, pkg=pkg, clickable=True, bounds=(x, y, x + largura, y + altura))


class Fabrica:
    def __init__(self, nome, meta):
        self.pasta = DESTINO / nome
        if self.pasta.exists():
            shutil.rmtree(self.pasta)
        (self.pasta / "telas").mkdir(parents=True)
        self.meta = meta
        self.acoes = []
        self.passo = 0

    def acao(self, par, fluxo, acao, descricao="", xml=None, **extra):
        self.passo += 1
        reg = {"passo": self.passo, "par": par, "fluxo": fluxo, "acao": acao, "descricao": descricao,
               "operador_klm": "", "caracteres": extra.pop("caracteres", 0), "segundos": extra.pop("segundos", 0.0),
               "tela": "", "hierarquia": "", "canal_externo": extra.pop("canal_externo", False),
               "pacote": extra.pop("pacote", self.meta["pacote"]), "gatilho": extra.pop("gatilho", ""),
               "codigo_candidato": "", "observacoes": ""}
        if xml:
            nome = f"tela_{self.passo:04d}.xml"
            (self.pasta / "telas" / nome).write_text(xml, encoding="utf-8")
            reg["hierarquia"] = nome
        self.acoes.append(reg)

    def notificacoes(self, linhas):
        with (self.pasta / "notificacoes.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["data", "app", "titulo", "texto", "origem"])
            w.writeheader()
            for l in linhas:
                w.writerow({"app": self.meta["app"], "origem": "manual", **l})

    def salvar(self):
        (self.pasta / "meta.json").write_text(json.dumps(self.meta, ensure_ascii=False, indent=2), encoding="utf-8")
        with (self.pasta / "acoes.jsonl").open("w", encoding="utf-8") as f:
            for a in self.acoes:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")


def f01():
    pk = "com.exemplo.violadora"
    f = Fabrica("F01", {"app": "F01", "categoria": "Redes sociais e vídeo curto", "versao_app": "1.0-sintetico",
                        "dispositivo": "fixture", "data": "2026-11-20", "modo": "sintetico", "pacote": pk,
                        "pares_nao_aplicaveis": ["P5"], "pares_nao_observaveis": ["P4"]})
    # abertura: pedido de permissão antes de qualquer ação do usuário (D3)
    f.acao("-", "transversal", "observacao", "abrir o aplicativo",
           tela("com.google.android.permissioncontroller",
                node(text="Permitir que o app envie notificações?", pkg="com.google.android.permissioncontroller"),
                node(cls="android.widget.Button", text="Permitir", rid="com.android.permissioncontroller:id/permission_allow_button",
                     pkg="com.google.android.permissioncontroller", clickable=True, bounds=(100, 1500, 980, 1650)),
                node(cls="android.widget.Button", text="Não permitir", pkg="com.google.android.permissioncontroller",
                     clickable=True, bounds=(100, 1700, 980, 1850))))
    # P2 engajamento: aceitar
    f.acao("P2", "engajamento", "toque", "Permitir", tela(pk, node(text="Início", pkg=pk)))
    # P1 engajamento: 6 ações
    for d, extra in [("Criar conta", {}), ("e-mail", {"acao": "digitacao", "caracteres": 20}),
                     ("senha", {"acao": "digitacao", "caracteres": 10}), ("Continuar", {}), ("Aceitar termos", {}),
                     ("Concluir", {})]:
        f.acao("P1", "engajamento", extra.pop("acao", "toque"), d, tela(pk, node(text=d, pkg=pk)), **extra)
    # feed: 5 rolagens, sempre com itens novos e sem marcador de fim (D1)
    for i in range(5):
        itens = "".join(node(text=f"Publicação {chr(65 + i)}{j} sobre {['viagens', 'música', 'esportes', 'culinária', 'moda'][i]}",
                             pkg=pk) for j in range(4))
        f.acao("-", "transversal", "gesto", "rolar feed", tela(pk, node(cls="androidx.recyclerview.widget.RecyclerView",
                                                                        pkg=pk, scrollable=True, filhos=itens)))
    # P3: iniciar vídeo e espera com troca automática de conteúdo (D2)
    f.acao("P3", "engajamento", "toque", "abrir vídeo", tela(pk, node(text="Como fazer pão caseiro", pkg=pk),
                                                              node(text="Canal Cozinha Fácil", pkg=pk)))
    f.acao("-", "transversal", "espera", "aguardar fim do vídeo",
           tela(pk, node(text="Dez truques de fotografia no celular", pkg=pk), node(text="Canal Foto Rápida", pkg=pk)),
           segundos=12)
    # P3 saída: 4 ações; configuração de reprodução automática vem ativada (AR10)
    for d in ["Perfil", "Configurações", "Reprodução"]:
        f.acao("P3", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    f.acao("P3", "saida", "toque", "desativar reprodução automática",
           tela(pk, node(cls="android.widget.Switch", text="Reprodução automática", pkg=pk, checkable=True, checked=True,
                         clickable=True)))
    # P2 saída: 5 ações
    for d in ["Perfil", "Configurações", "Notificações", "Mais opções", "Desativar promoções"]:
        f.acao("P2", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    # P1 saída: 12 ações, texto culpabilizante (D5/AR09) e última etapa no navegador (canal externo)
    for d in ["Perfil", "Configurações", "Conta", "Privacidade", "Gerenciar conta", "Excluir conta", "Motivo", "Continuar"]:
        f.acao("P1", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    f.acao("P1", "saida", "toque", "Continuar",
           tela(pk, node(text="Tem certeza que deseja sair? Sentiremos sua falta.", pkg=pk), botao(pk, "Continuar")))
    f.acao("P1", "saida", "toque", "Confirmar", tela(pk, node(text="Confirmar", pkg=pk)))
    f.acao("P1", "saida", "digitacao", "senha", tela(pk, node(text="Senha", pkg=pk)), caracteres=10)
    f.acao("P1", "saida", "toque", "Concluir exclusão no site",
           tela("com.android.chrome", node(text="Excluir conta – site", pkg="com.android.chrome")),
           canal_externo=True, pacote="com.android.chrome")
    f.notificacoes(
        [{"data": "2026-11-21", "titulo": "Novidades", "texto": f"Veja o que seus amigos postaram ({i})"} for i in range(4)]
        + [{"data": "2026-11-21", "titulo": "Atenção", "texto": "Não perca sua ofensiva de 3 dias!"},
           {"data": "2026-11-22", "titulo": "Sentimos sua falta", "texto": "Volte e veja os destaques"}])
    f.salvar()


def f02():
    pk = "com.exemplo.conforme"
    f = Fabrica("F02", {"app": "F02", "categoria": "Aplicativos gamificados de estudo e de exercício",
                        "versao_app": "1.0-sintetico", "dispositivo": "fixture", "data": "2026-11-20", "modo": "sintetico",
                        "pacote": pk, "pares_nao_aplicaveis": ["P3"], "pares_nao_observaveis": []})
    f.acao("-", "transversal", "observacao", "abrir o aplicativo", tela(pk, node(text="Bem-vindo", pkg=pk)))
    for d, extra in [("Criar conta", {}), ("e-mail", {"acao": "digitacao", "caracteres": 20}),
                     ("senha", {"acao": "digitacao", "caracteres": 10}), ("Continuar", {}), ("Aceitar termos", {}),
                     ("Concluir", {})]:
        f.acao("P1", "engajamento", extra.pop("acao", "toque"), d, tela(pk, node(text=d, pkg=pk)), **extra)
    # pré-pedido com opções de mesmo destaque e pedido após ação relacionada
    f.acao("P2", "engajamento", "toque", "Ativar lembretes de estudo",
           tela(pk, node(text="Quer receber um lembrete por dia?", pkg=pk), botao(pk, "Sim", y=1600, largura=400),
                botao(pk, "Agora não", y=1800, largura=400)), gatilho="notificacoes")
    f.acao("P2", "engajamento", "toque", "Sim",
           tela("com.google.android.permissioncontroller",
                node(cls="android.widget.Button", text="Permitir", rid="com.android.permissioncontroller:id/permission_allow_button",
                     pkg="com.google.android.permissioncontroller", clickable=True)), gatilho="notificacoes")
    f.acao("P5", "engajamento", "toque", "Começar lição do dia", tela(pk, node(text="Lição 1", pkg=pk)))
    f.acao("P5", "engajamento", "toque", "Concluir lição", tela(pk, node(text="Ofensiva: 1 dia", pkg=pk)))
    for i in range(5):
        itens = "".join(node(text=f"Lição {i}{j} de revisão", pkg=pk) for j in range(3))
        fim = node(text="Você está em dia! Volte amanhã.", pkg=pk) if i == 4 else ""
        f.acao("-", "transversal", "gesto", "rolar trilha", tela(pk, node(pkg=pk, scrollable=True, filhos=itens + fim)))
    f.acao("-", "transversal", "espera", "aguardar", tela(pk, node(text=f"Lição 4{2} de revisão", pkg=pk),
                                                          node(text="Você está em dia! Volte amanhã.", pkg=pk)), segundos=10)
    f.acao("P4", "engajamento", "toque", "Planos", tela(pk, node(text="Planos", pkg=pk)))
    f.acao("P4", "engajamento", "toque", "Plano gratuito plus", tela(pk, node(text="Plano gratuito plus", pkg=pk)))
    f.acao("P4", "engajamento", "toque", "Assinar", tela(pk, node(text="Assinar", pkg=pk)))
    f.acao("P4", "engajamento", "toque", "Confirmar", tela(pk, node(text="Assinatura ativa", pkg=pk)))
    for d in ["Perfil", "Assinatura", "Cancelar assinatura"]:
        f.acao("P4", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    for d in ["Perfil", "Lembretes"]:
        f.acao("P5", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    for d in ["Notificações", "Desativar lembretes"]:
        f.acao("P2", "saida", "toque", d, tela(pk, node(text=d, pkg=pk)))
    for d in ["Perfil", "Conta", "Excluir conta", "Confirmar"]:
        f.acao("P1", "saida", "toque", d, tela(pk, node(text=d, pkg=pk), botao(pk, "Excluir conta"), botao(pk, "Voltar", y=2000)))
    f.acao("P1", "saida", "digitacao", "senha", tela(pk, node(text="Conta excluída", pkg=pk)), caracteres=10)
    f.notificacoes([{"data": "2026-11-21", "titulo": "Lembrete", "texto": "Sua lição de hoje está pronta"},
                    {"data": "2026-11-22", "titulo": "Lembrete", "texto": "Sua lição de hoje está pronta"}])
    f.salvar()


if __name__ == "__main__":
    f01()
    f02()
    print("fixtures geradas em", DESTINO)
