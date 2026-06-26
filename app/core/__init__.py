from app.core.database import criar_tabelas, get_session
from app.core.security import hash_senha
from app.models.user import Usuario

def inicializar_banco():
    # Cria as tabelas
    criar_tabelas()

    session = get_session()

    # Verifica se já existe um admin
    admin_existe = session.query(Usuario).filter_by(username="admin").first()

    if not admin_existe:
        admin = Usuario(
            nome="Administrador",
            username="admin",
            senha_hash=hash_senha("admin123"),
            perfil="admin",
            ativo=True
        )
        session.add(admin)
        session.commit()
        print("Usuário admin criado com sucesso!")
    else:
        print("Admin já existe.")

    session.close()