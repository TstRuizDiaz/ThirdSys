"""
app/core/email_service.py
─────────────────────────────────────────────────────────────────────────────
Envio de e-mail com o resumo de vencimentos (vencidos + a vencer).

Usa SMTP simples (smtplib, biblioteca padrão do Python — não precisa
instalar nada extra). A configuração (host, porta, usuário, senha,
destinatários) fica salva em data/config.json via app.core.settings.

Funciona com qualquer provedor SMTP comum:
  - Gmail:    smtp.gmail.com, porta 587 (precisa "senha de app", não a
              senha normal da conta — ver suporte do Gmail)
  - Outlook:  smtp.office365.com, porta 587
  - Outro provedor corporativo: perguntar ao TI host/porta/usuário/senha
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.settings import obter_smtp_config


class EmailNaoConfiguradoError(Exception):
    pass


def _montar_corpo_html(alertas: dict) -> str:
    def _linhas(lista, cor):
        if not lista:
            return f'<p style="color:#6B7280;font-size:13px;">Nenhum item.</p>'
        linhas = "".join(
            f"<tr>"
            f'<td style="padding:6px 10px;border-bottom:1px solid #E5E7EB;">{ref}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #E5E7EB;">{tipo}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #E5E7EB;">{venc.strftime("%d/%m/%Y")}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #E5E7EB;">{origem}</td>'
            f"</tr>"
            for ref, tipo, venc, origem in lista
        )
        return (
            f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
            f'<tr style="background:#F4F7FA;">'
            f'<th style="padding:6px 10px;text-align:left;color:{cor};">Referência</th>'
            f'<th style="padding:6px 10px;text-align:left;color:{cor};">Documento</th>'
            f'<th style="padding:6px 10px;text-align:left;color:{cor};">Vencimento</th>'
            f'<th style="padding:6px 10px;text-align:left;color:{cor};">Origem</th>'
            f"</tr>{linhas}</table>"
        )

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 640px;">
        <div style="background:#2563EB;color:white;padding:16px 20px;border-radius:8px 8px 0 0;">
            <h2 style="margin:0;font-size:18px;">ThirdSys — Alerta de Vencimentos</h2>
        </div>
        <div style="border:1px solid #DDE3EA;border-top:none;padding:20px;border-radius:0 0 8px 8px;">
            <h3 style="color:#991B1B;font-size:14px;">
                Vencidos ({alertas['total_vencidos']})
            </h3>
            {_linhas(alertas['vencidos'], '#991B1B')}
            <br>
            <h3 style="color:#92400E;font-size:14px;">
                A vencer em até 30 dias ({alertas['total_a_vencer']})
            </h3>
            {_linhas(alertas['a_vencer'], '#92400E')}
            <p style="color:#8AA5BC;font-size:11px;margin-top:20px;">
                E-mail automático gerado pelo ThirdSys. Acesse o sistema
                para mais detalhes ou para gerar o relatório em PDF.
            </p>
        </div>
    </div>
    """


def enviar_alerta_vencimentos(alertas: dict, config: dict | None = None) -> None:
    """Envia o e-mail de alerta. Lança EmailNaoConfiguradoError se o SMTP
    não estiver configurado/ativo, ou a exceção original do smtplib se a
    conexão/autenticação falhar (deixa o chamador decidir como avisar o
    usuário — não engolimos o erro aqui)."""
    cfg = config or obter_smtp_config()

    if not cfg.get("ativo"):
        raise EmailNaoConfiguradoError("Envio de e-mail está desativado nas configurações.")
    if not cfg.get("host") or not cfg.get("destinatarios"):
        raise EmailNaoConfiguradoError("Configure o servidor SMTP e ao menos um destinatário.")

    if alertas["total_vencidos"] == 0 and alertas["total_a_vencer"] == 0:
        return  # nada a avisar — não manda e-mail vazio

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"[ThirdSys] {alertas['total_vencidos']} vencido(s) e "
        f"{alertas['total_a_vencer']} a vencer"
    )
    msg["From"] = f"{cfg.get('remetente_nome', 'ThirdSys')} <{cfg['usuario']}>"
    msg["To"] = ", ".join(cfg["destinatarios"])

    msg.attach(MIMEText(_montar_corpo_html(alertas), "html", "utf-8"))

    with smtplib.SMTP(cfg["host"], int(cfg["porta"]), timeout=15) as server:
        server.starttls()
        if cfg.get("usuario"):
            server.login(cfg["usuario"], cfg["senha"])
        server.sendmail(cfg["usuario"], cfg["destinatarios"], msg.as_string())


def testar_conexao_smtp(host: str, porta: int, usuario: str, senha: str) -> None:
    """Usado pelo botão 'Testar conexão' na tela de configuração — lança
    exceção se algo falhar, pra UI mostrar a mensagem de erro real."""
    with smtplib.SMTP(host, int(porta), timeout=10) as server:
        server.starttls()
        if usuario:
            server.login(usuario, senha)
