# Ambiente para a coleta automatizada

A integração contínua não precisa de emulador (roda sobre as sessões sintéticas). Para coletar de
um aplicativo real, cada integrante monta este ambiente uma vez.

## 1. Android
1. Instale o **Android Studio** e, no *Device Manager*, crie um dispositivo virtual (ex.: Pixel 7)
   com imagem **Android 14 com Google Play** (necessária para instalar apps da loja).
2. Configure o emulador em português, fuso America/Sao_Paulo, e faça login com a **conta Google de teste**.
3. Instale pela Play Store os apps do piloto. Anote a versão (Configurações › Apps › <app>).
4. Verifique o `adb`: `adb devices` deve listar `emulator-5554`.

## 2. Appium
```bash
npm install -g appium
appium driver install uiautomator2
appium --allow-insecure adb_shell     # adb_shell permite ler a versão do app e notificações
```
Use o **Appium Inspector** para descobrir os localizadores (`resource-id`, `content-desc`, texto) de
cada botão e montar os roteiros em `ferramenta/roteiros/local/` (não versionado).

## 3. Python
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[coleta,dev]"
pytest                                                  # testes, sem emulador
```

## 4. Coletar e analisar
```bash
export SENHA_A01='***'                                  # Windows: set SENHA_A01=***
python -m antipadroes coletar piloto/sessoes/A01_auto \
    ferramenta/roteiros/local/A01_P1_engajamento.yaml ferramenta/roteiros/local/A01_P1_saida.yaml
python -m antipadroes analisar piloto/sessoes/A01_auto  # detectores + requisitos + relatório
```
Abra `piloto/sessoes/A01_auto/relatorio.html`.

## Problemas comuns
| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Captura de tela preta | app bloqueia captura (proteção de conteúdo) | registrar como resultado (risco R02); inspecionar manualmente |
| App fecha ou recusa abrir no emulador | detecção de emulador | usar o dispositivo físico dedicado |
| `NoSuchElementError` | localizador mudou com a versão | atualizar o roteiro pelo Appium Inspector |
| Versão do app vazia no relatório | Appium sem `--allow-insecure adb_shell` | anotar a versão manualmente em `meta.json` |
