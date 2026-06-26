import hashlib
import secrets

def hash_senha(senha: str) -> str:
    salt = secrets.token_hex(32)
    hash_val = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100_000
    )
    return f"{salt}:{hash_val.hex()}"

def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        salt, hash_original = hash_armazenado.split(":")
        hash_verificacao = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100_000
        )
        return hash_verificacao.hex() == hash_original
    except Exception:
        return False