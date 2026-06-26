import json
from app.core.settings import DATA_DIR

SESSION_FILE = DATA_DIR / "session.json"

def salvar_sessao(usuario_id: int, email: str, token: str, cnpj: str):
    data = {"usuario_id": usuario_id, "email": email, "token": token, "cnpj": cnpj}
    SESSION_FILE.write_text(json.dumps(data))

def carregar_sessao() -> dict | None:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            return None
    return None

def limpar_sessao():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
