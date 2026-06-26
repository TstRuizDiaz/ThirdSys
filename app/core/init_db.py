from app.core.database import criar_tabelas, get_session
from app.core.security import hash_senha
from app.models.user import Usuario
from app.models.documento import TipoDocumento

TIPOS_DOCUMENTO = [
    # DOCUMENTOS EMPRESA
    {"nome": "CCMEI (MEI)",                     "categoria": "empresa", "tem_validade": False, "ordem": 1},
    {"nome": "Contrato Social",                  "categoria": "empresa", "tem_validade": False, "ordem": 2},
    {"nome": "Contrato Quarteirização",          "categoria": "empresa", "tem_validade": False, "ordem": 3},
    {"nome": "Cartão CNPJ",                      "categoria": "empresa", "tem_validade": False, "ordem": 4},
    {"nome": "Apólice de Seguro de Vida",        "categoria": "empresa", "tem_validade": True,  "ordem": 5},
    {"nome": "PGR",                              "categoria": "empresa", "tem_validade": True,  "ordem": 6},
    {"nome": "ART CREA",                         "categoria": "empresa", "tem_validade": True,  "ordem": 7},
    {"nome": "PCMSO",                            "categoria": "empresa", "tem_validade": True,  "ordem": 8},
    {"nome": "Manual QSMA",                      "categoria": "empresa", "tem_validade": False, "ordem": 9},
    {"nome": "Comunicação Prévia MTPS",          "categoria": "empresa", "tem_validade": False, "ordem": 10},

    # DOCUMENTOS COLABORADOR
    {"nome": "ASO",                              "categoria": "colaborador", "tem_validade": True,  "ordem": 1},
    {"nome": "Crachá / RG",                      "categoria": "colaborador", "tem_validade": False, "ordem": 2},
    {"nome": "Ficha de Registro",                "categoria": "colaborador", "tem_validade": False, "ordem": 3},
    {"nome": "Ficha de EPI",                     "categoria": "colaborador", "tem_validade": False, "ordem": 4},
    {"nome": "Ordem de Serviço (NR-01)",         "categoria": "colaborador", "tem_validade": False, "ordem": 5},
    {"nome": "Certificado/Diploma (PLH)",        "categoria": "colaborador", "tem_validade": True,  "ordem": 6},
    {"nome": "Certificados Normativos",          "categoria": "colaborador", "tem_validade": True,  "ordem": 7},
]

def inicializar_banco():
    criar_tabelas()
    session = get_session()

    # Admin
    if not session.query(Usuario).filter_by(username="admin").first():
        admin = Usuario(
            nome="Administrador",
            username="admin",
            senha_hash=hash_senha("admin123"),
            perfil="admin",
            ativo=True
        )
        session.add(admin)
        print("Usuário admin criado!")
    else:
        print("Admin já existe.")

    # Tipos de documento
    for tipo in TIPOS_DOCUMENTO:
        existe = session.query(TipoDocumento).filter_by(
            nome=tipo["nome"], categoria=tipo["categoria"]
        ).first()
        if not existe:
            session.add(TipoDocumento(**tipo))

    session.commit()
    session.close()
    print("Banco inicializado.")