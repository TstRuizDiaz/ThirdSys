import requests
from dataclasses import dataclass
from typing import Optional

API_BASE_URL = "https://sua-api.com"  # ← trocar pela URL real quando a API estiver pronta

# ─── MOCK LOCAL (remover quando a API estiver pronta) ───────────────────────
MOCK_USUARIOS = {
    "14049467008387": {
        "email": "admin@empresa.com",
        "senha": "123456",
        "usuario": {
            "id": 1,
            "nome": "Administrador",
            "email": "admin@empresa.com",
            "cnpj": "14049467008387",
        }
    }
}

def _mock_login(cnpj: str, email: str, senha: str) -> "LoginResult":
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    cadastro = MOCK_USUARIOS.get(cnpj_limpo)

    if not cadastro:
        return LoginResult(success=False, erro="CNPJ não cadastrado no sistema.")
    if cadastro["email"] != email:
        return LoginResult(success=False, erro="E-mail inválido para este CNPJ.")
    if cadastro["senha"] != senha:
        return LoginResult(success=False, erro="Senha incorreta.")

    return LoginResult(
        success=True,
        token="mock-token-dev-123",
        usuario=cadastro["usuario"],
    )

USE_MOCK = True  # ← mudar para False quando a API estiver pronta
# ────────────────────────────────────────────────────────────────────────────


@dataclass
class LoginResult:
    success: bool
    token: Optional[str] = None
    usuario: Optional[dict] = None
    erro: Optional[str] = None


def login_api(cnpj: str, email: str, senha: str) -> LoginResult:
    """Autentica na API remota com CNPJ + e-mail + senha."""

    if USE_MOCK:
        return _mock_login(cnpj, email, senha)

    try:
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))

        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={
                "cnpj": cnpj_limpo,
                "email": email,
                "password": senha,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return LoginResult(
                success=True,
                token=data.get("token"),
                usuario=data.get("user") or data.get("usuario"),
            )
        elif response.status_code == 401:
            return LoginResult(success=False, erro="CNPJ, e-mail ou senha inválidos.")
        else:
            return LoginResult(success=False, erro=f"Erro no servidor ({response.status_code}).")

    except requests.ConnectionError:
        return LoginResult(success=False, erro="Sem conexão com o servidor. Verifique sua internet.")
    except requests.Timeout:
        return LoginResult(success=False, erro="Servidor demorou para responder. Tente novamente.")
    except Exception as e:
        return LoginResult(success=False, erro=f"Erro inesperado: {e}")