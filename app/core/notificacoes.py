"""
app/core/notificacoes.py
─────────────────────────────────────────────────────────────────────────────
Agrega tudo que está vencido ou a vencer (PGR, PCMSO, Apólice, ASO,
Treinamentos NR) num único lugar — usado pelo sino de notificações na
sidebar e pelo e-mail diário de alertas.

Reaproveita os mesmos "loaders" já usados pela tela de Vencimentos
(app/ui/pages/vencimentos_page.py via _carregar_vencimentos_* do
relatorios-style), recalculando o status (vencido/a_vencer) aqui mesmo
pra não depender de importar widgets Qt num módulo que pode ser chamado
fora da UI (ex.: pelo envio de e-mail agendado).
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from datetime import date, timedelta

DIAS_AVISO_VENCIMENTO = 30


def _status(data_validade) -> str:
    if not data_validade:
        return "sem_data"
    hoje = date.today()
    if data_validade < hoje:
        return "vencido"
    elif data_validade <= hoje + timedelta(days=DIAS_AVISO_VENCIMENTO):
        return "a_vencer"
    return "valido"


def _carregar_empresas() -> list[tuple[str, str, date]]:
    from app.core.database import get_session
    from app.models.empresa import Empresa
    from app.models.documento import Documento, TipoDocumento

    session = get_session()
    try:
        registros = []
        for emp in session.query(Empresa).all():
            if emp.pgr_validade:
                registros.append((emp.razao_social, "PGR", emp.pgr_validade))
            if emp.pcmso_validade:
                registros.append((emp.razao_social, "PCMSO", emp.pcmso_validade))
            if emp.apolice_validade:
                registros.append((emp.razao_social, "Apólice de Seguro", emp.apolice_validade))

        docs = (
            session.query(Documento, TipoDocumento, Empresa)
            .join(TipoDocumento, Documento.tipo_documento_id == TipoDocumento.id)
            .join(Empresa, Documento.empresa_id == Empresa.id)
            .filter(TipoDocumento.categoria == "empresa")
            .filter(Documento.data_validade.isnot(None))
            .all()
        )
        for doc, tipo, emp in docs:
            registros.append((emp.razao_social, tipo.nome, doc.data_validade))
        return registros
    finally:
        session.close()


def _carregar_colaboradores() -> list[tuple[str, str, date]]:
    from app.core.database import get_session
    from app.models.trabalhador import Trabalhador
    from app.models.documento import Documento, TipoDocumento

    session = get_session()
    try:
        registros = []
        for t in session.query(Trabalhador).filter_by(ativo=True).all():
            if t.aso_validade:
                registros.append((t.nome, "ASO", t.aso_validade))

        docs = (
            session.query(Documento, TipoDocumento, Trabalhador)
            .join(TipoDocumento, Documento.tipo_documento_id == TipoDocumento.id)
            .join(Trabalhador, Documento.trabalhador_id == Trabalhador.id)
            .filter(TipoDocumento.categoria == "colaborador")
            .filter(Documento.data_validade.isnot(None))
            .all()
        )
        for doc, tipo, t in docs:
            registros.append((t.nome, tipo.nome, doc.data_validade))
        return registros
    finally:
        session.close()


def _carregar_treinamentos() -> list[tuple[str, str, date]]:
    from app.core.database import get_session
    from app.models.treinamento import Treinamento
    from app.models.trabalhador import Trabalhador

    session = get_session()
    try:
        rows = (
            session.query(Treinamento, Trabalhador)
            .join(Trabalhador, Treinamento.trabalhador_id == Trabalhador.id)
            .filter(Treinamento.data_validade.isnot(None))
            .all()
        )
        return [(t.nome, tr.nr_nome, tr.data_validade) for tr, t in rows]
    finally:
        session.close()


def obter_alertas() -> dict:
    """
    Retorna:
        {
          "vencidos":  [(referencia, tipo, data_validade, origem), ...],
          "a_vencer":  [(referencia, tipo, data_validade, origem), ...],
          "total_vencidos": int,
          "total_a_vencer": int,
        }
    `origem` é "Empresa" | "Colaborador" | "Treinamento" — só pra dar
    contexto na lista do sino/e-mail.
    """
    fontes = [
        (_carregar_empresas(),      "Empresa"),
        (_carregar_colaboradores(), "Colaborador"),
        (_carregar_treinamentos(),  "Treinamento"),
    ]

    vencidos, a_vencer = [], []
    for registros, origem in fontes:
        for ref, tipo, venc in registros:
            st = _status(venc)
            if st == "vencido":
                vencidos.append((ref, tipo, venc, origem))
            elif st == "a_vencer":
                a_vencer.append((ref, tipo, venc, origem))

    vencidos.sort(key=lambda x: x[2])
    a_vencer.sort(key=lambda x: x[2])

    return {
        "vencidos": vencidos,
        "a_vencer": a_vencer,
        "total_vencidos": len(vencidos),
        "total_a_vencer": len(a_vencer),
    }
