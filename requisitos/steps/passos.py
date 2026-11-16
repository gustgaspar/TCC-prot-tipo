"""Definições dos passos da biblioteca de requisitos.

Os passos leem a sessão carregada no environment.py (manual ou automatizada). Quando a
sessão não tem evidência para decidir um requisito, o cenário é marcado como indecidível
(pulado com o motivo), e não como reprovado.
"""
from behave import given, then, when

from antipadroes import detectores, iaf, klm, notificacoes


def indecidivel(context, motivo: str) -> None:
    context.motivo = motivo
    context.scenario.skip(motivo)


def _fluxo(context, par: str, fluxo: str):
    s = context.sessao
    if s.nao_aplicavel(par):
        indecidivel(context, f"par {par} não se aplica a este aplicativo")
        return None
    if s.nao_observavel(par):
        indecidivel(context, f"par {par} não observável (ex.: exige pagamento)")
        return None
    acoes = s.fluxo(par, fluxo)
    if not any(a.do_usuario for a in acoes):
        indecidivel(context, f"sessão sem registro do fluxo de {fluxo} do par {par}")
        return None
    return acoes


# ---------------- Dado ----------------
@given('o fluxo de engajamento do par "{par}"')
def dado_engajamento(context, par):
    context.par = par
    context.engajamento = _fluxo(context, par, "engajamento")


@given('o fluxo de saída do par "{par}"')
def dado_saida(context, par):
    context.par = par
    context.fluxo_atual = _fluxo(context, par, "saida")


@given("as telas registradas na sessão")
def dado_telas(context):
    if not any(a.hierarquia for a in context.sessao.acoes):
        indecidivel(context, "sessão sem hierarquias de views (inspeção manual sem XML)")


@given("o feed rolado pelo menos {k:d} vezes")
def dado_feed(context, k):
    seq, maior = 0, 0
    for a in context.sessao.acoes:
        seq = seq + 1 if (a.acao == "gesto" and a.hierarquia) else 0
        maior = max(maior, seq)
    if maior < k:
        indecidivel(context, f"sessão sem sequência de {k} rolagens com hierarquia registrada")


@given("as notificações registradas no período de observação")
def dado_notificacoes(context):
    context.notificacoes = context.sessao.notificacoes()
    if not context.notificacoes and not context.sessao.meta.get("observacao_notificacoes_concluida"):
        indecidivel(context, "sem registro de notificações (notificacoes.csv)")


# ---------------- Quando ----------------
@when('eu percorro o fluxo de saída do par "{par}"')
def quando_saida(context, par):
    if getattr(context, "engajamento", None) is None:
        return  # cenário já marcado como indecidível
    context.par = par
    context.fluxo_atual = _fluxo(context, par, "saida")
    if context.fluxo_atual is not None:
        context.iaf = iaf.calcular(context.sessao, par)


@when('eu desativo pelo caminho mais curto registrado')
def quando_desativo(context):
    pass  # o caminho mais curto é o fluxo de saída registrado na inspeção


@when('aplico o detector "{codigo}"')
def quando_detector(context, codigo):
    context.achados = [a for a in detectores.detectar(context.sessao, [codigo])]


@when("conto as notificações por dia")
def quando_conto(context):
    context.por_dia = notificacoes.por_dia(context.notificacoes)


# ---------------- Então ----------------
@then("o índice de assimetria de fricção deve ser no máximo {limite}")
def entao_iaf(context, limite):
    lim = float(limite.replace(",", "."))
    r = context.iaf
    assert r.iaf_acoes is not None, "IAF não calculado"
    assert r.iaf_acoes <= lim, (f"IAF = {r.iaf_acoes:.2f} (sair: {r.acoes_saida} ações; "
                                f"entrar: {r.acoes_engajamento} ações) excede {lim}")


@then("a saída não deve exigir canal externo ao aplicativo")
def entao_sem_canal(context):
    externos = [a.passo for a in (context.fluxo_atual or []) if a.canal_externo]
    assert not externos, f"a saída levou para fora do aplicativo nos passos {externos}"


@then("devo concluir em no máximo {n:d} ações")
def entao_max_acoes(context, n):
    total = klm.numero_de_acoes(context.fluxo_atual)
    assert total <= n, f"foram necessárias {total} ações (limite: {n})"


@then('não deve haver achados do antipadrão "{ap}"')
def entao_sem_achados(context, ap):
    achs = [a for a in context.achados if a.antipadrao == ap]
    assert not achs, "; ".join(f"{a.unidade}: {a.descricao}" for a in achs)


@then("nenhum dia deve ter mais de {n:d} notificações")
def entao_por_dia(context, n):
    excessos = {d: q for d, q in context.por_dia.items() if q > n}
    assert not excessos, f"dias acima do limite de {n}: {excessos}"


# ---------------- Passos de cenários @manual (não automatizados) ----------------
@given("que uso o aplicativo por {dias:d} dias")
@when("observo as recompensas oferecidas")
@then("nenhuma recompensa deve ser aleatória nem condicionada ao tempo de uso")
@given("que inicio o cancelamento da assinatura")
@when("avanço até a confirmação do cancelamento")
@then("devo ver no máximo uma oferta de retenção")
@given("que acabei de criar a minha conta")
@when("abro as configurações de notificação")
@then("as notificações promocionais e os lembretes devem estar desativados")
def passo_manual(context, **_):
    indecidivel(context, "requer inspeção humana")
