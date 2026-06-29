"""
app/server/api_server.py
─────────────────────────────────────────────────────────────────────────────
Servidor central do ThirdSys — roda em UMA máquina (ex.: a da portaria,
24h ligada) e é o único processo que acessa o arquivo SQLite diretamente.

As outras máquinas da rede (clientes ThirdSys) NÃO acessam o banco direto.
Elas conversam com este servidor via HTTP (rede local), o que evita o
problema de SQLite sendo escrito por vários processos ao mesmo tempo via
pasta de rede (lock/corrupção).

COMO RODAR (modo desenvolvimento, no seu notebook):
    pip install fastapi uvicorn
    python -m app.server.api_server

COMO RODAR EM PRODUÇÃO (máquina da portaria, sem precisar instalar nada):
    1. Gerar um .exe único com PyInstaller (feito no seu notebook):
         pyinstaller --onefile --name ThirdSysServer app/server/api_server.py
    2. Copiar o .exe gerado (dist/ThirdSysServer.exe) + a pasta "data/"
       (com o thirdsys.db) para uma pasta na máquina da portaria.
    3. Dar duplo clique no .exe — ele abre uma janela de console e fica
       escutando na rede. Não precisa de instalação nem de admin.
    4. (Opcional) Para iniciar automaticamente com o Windows, sem precisar
       de permissão de administrador: criar um atalho do .exe dentro de
         %AppData%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
       (essa pasta é por usuário, não exige admin).

As outras máquinas só precisam saber o IP local da máquina da portaria
(ex.: 192.168.0.50) e a porta (8000), configurados em app/core/api_client.py.
─────────────────────────────────────────────────────────────────────────────
"""

import secrets
from datetime import datetime, timedelta

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from app.core.database import get_session, criar_tabelas
from app.core.security import verificar_senha
from app.models.user import Usuario

app = FastAPI(title="ThirdSys API")

# ─────────────────────────────────────────────────────────────────────────────
# Sessões em memória (token -> dados). Simples e suficiente para uma rede
# local pequena. Se o servidor for reiniciado, todo mundo precisa logar de
# novo — o que é aceitável para esse cenário.
# ─────────────────────────────────────────────────────────────────────────────
_SESSOES: dict[str, dict] = {}
TOKEN_VALIDADE_HORAS = 12


class LoginRequest(BaseModel):
    username: str
    senha: str


class LoginResponse(BaseModel):
    success: bool
    token: str | None = None
    usuario: dict | None = None
    erro: str | None = None


def _limpar_sessoes_expiradas():
    agora = datetime.utcnow()
    expiradas = [t for t, s in _SESSOES.items() if s["expira_em"] < agora]
    for t in expiradas:
        _SESSOES.pop(t, None)


@app.on_event("startup")
def _startup():
    # Garante que as tabelas existem (idempotente — não apaga dados).
    criar_tabelas()


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    _limpar_sessoes_expiradas()

    session = get_session()
    try:
        usuario = (
            session.query(Usuario)
            .filter_by(username=payload.username.strip())
            .first()
        )

        if not usuario:
            return LoginResponse(success=False, erro="Usuário não encontrado.")

        if not usuario.ativo:
            return LoginResponse(success=False, erro="Usuário inativo. Contate o administrador.")

        if not verificar_senha(payload.senha, usuario.senha_hash):
            return LoginResponse(success=False, erro="Senha incorreta.")

        token = secrets.token_hex(32)
        _SESSOES[token] = {
            "usuario_id": usuario.id,
            "expira_em": datetime.utcnow() + timedelta(hours=TOKEN_VALIDADE_HORAS),
        }

        return LoginResponse(
            success=True,
            token=token,
            usuario={
                "id": usuario.id,
                "nome": usuario.nome,
                "username": usuario.username,
                "perfil": usuario.perfil,
            },
        )
    finally:
        session.close()


@app.get("/api/health")
def health():
    """Usado pelos clientes para checar se o servidor está acessível."""
    return {"status": "ok"}


def main():
    # host="0.0.0.0" -> escuta em todos os IPs da máquina, ou seja,
    # aceita conexões vindas de outros computadores da rede local.
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
