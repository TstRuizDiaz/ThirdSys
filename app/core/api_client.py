"""
app/core/api_client.py
─────────────────────────────────────────────────────────────────────────────
Cliente HTTP que fala com o ThirdSys Server (app/server/api_server.py),
que roda numa única máquina da rede local (ex.: a da portaria, 24h ligada).

IMPORTANTE: troque API_BASE_URL pelo IP local da máquina que está rodando
o ThirdSysServer. Para descobrir esse IP, na máquina-servidor execute no
cmd: ipconfig  (procure por "Endereço IPv4" da rede local).
─────────────────────────────────────────────────────────────────────────────
"""

import requests
from dataclasses import dataclass
from typing import Optional

# ── Endereço do servidor central na rede local da empresa ──────────────────
# Trocar pelo IP fixo da máquina-servidor (ex.: a da portaria) quando for
# para produção. Em desenvolvimento, pode apontar para 127.0.0.1 se o
# servidor estiver rodando no próprio notebook.
API_BASE_URL = "http://127.0.0.1:8000"


@dataclass
class LoginResult:
    success: bool
    token: Optional[str] = None
    usuario: Optional[dict] = None
    erro: Optional[str] = None


def login_api(username: str, senha: str) -> LoginResult:
    """Autentica contra o ThirdSys Server (rede local)."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": username, "senha": senha},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            return LoginResult(
                success=data.get("success", False),
                token=data.get("token"),
                usuario=data.get("usuario"),
                erro=data.get("erro"),
            )
        else:
            return LoginResult(success=False, erro=f"Erro no servidor ({response.status_code}).")

    except requests.ConnectionError:
        return LoginResult(
            success=False,
            erro=(
                "Não foi possível conectar ao servidor do ThirdSys.\n"
                "Verifique se o computador-servidor está ligado e conectado "
                "à rede da empresa."
            ),
        )
    except requests.Timeout:
        return LoginResult(success=False, erro="Servidor demorou para responder. Tente novamente.")
    except Exception as e:
        return LoginResult(success=False, erro=f"Erro inesperado: {e}")


def checar_servidor_online() -> bool:
    """Pode ser usado na splash screen para avisar se o servidor está offline."""
    try:
        r = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False
