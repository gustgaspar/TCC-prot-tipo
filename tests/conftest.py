import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramenta"))
FIXTURES = RAIZ / "tests" / "fixtures" / "sessoes"


@pytest.fixture(scope="session", autouse=True)
def gerar_fixtures():
    subprocess.run([sys.executable, str(RAIZ / "tests" / "fixtures" / "gerar_fixtures.py")], check=True, capture_output=True)


@pytest.fixture
def f01():
    from antipadroes.modelo import Sessao
    return Sessao.carregar(FIXTURES / "F01")


@pytest.fixture
def f02():
    from antipadroes.modelo import Sessao
    return Sessao.carregar(FIXTURES / "F02")
