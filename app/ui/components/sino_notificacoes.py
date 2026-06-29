"""
app/ui/components/sino_notificacoes.py
─────────────────────────────────────────────────────────────────────────────
Sino de notificações: mostra quantos documentos estão vencidos/a vencer,
com um menu rápido ao clicar, e um diálogo pra configurar o envio
automático de e-mail (SMTP) com esse mesmo resumo.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import threading

import qtawesome as qta
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QMenu,
    QMessageBox, QPushButton, QSpinBox, QTextEdit, QToolButton,
    QVBoxLayout, QWidgetAction,
)

from app.core.notificacoes import obter_alertas
from app.core.settings import (
    obter_smtp_config, salvar_smtp_config,
    obter_ultimo_envio_email, marcar_envio_email_hoje,
)
from app.core.email_service import (
    enviar_alerta_vencimentos, testar_conexao_smtp, EmailNaoConfiguradoError,
)

_BG      = "#F2F5F8"
_CARD    = "#FFFFFF"
_BORDA   = "#DDE3EA"
_TITULO  = "#1C2B3A"
_SUB     = "#5A7A96"
_LABEL   = "#8AA5BC"
_AZUL    = "#2563EB"
_VERM    = "#991B1B"
_AMAR    = "#92400E"
_VERDE   = "#16A34A"


# ─────────────────────────────────────────────────────────────────────────────
# Diálogo de configuração de e-mail
# ─────────────────────────────────────────────────────────────────────────────
class DialogConfigEmail(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar alertas por e-mail")
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet(f"background: {_BG};")
        self._setup_ui()

    @staticmethod
    def _campo() -> str:
        return f"""
            QLineEdit, QSpinBox {{
                background: {_CARD}; color: {_TITULO};
                border: 1.5px solid #CBD5E1; border-radius: 7px;
                padding: 0 10px; font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus {{ border-color: {_AZUL}; }}
        """

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 20)
        lay.setSpacing(10)

        titulo = QLabel("Alertas de vencimento por e-mail")
        titulo.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {_TITULO}; background: transparent;"
        )
        lay.addWidget(titulo)
        sub = QLabel(
            "Quando ativado, o sistema envia um e-mail diário (uma vez por "
            "dia, ao abrir o sistema) com tudo que está vencido ou a "
            "vencer em até 30 dias."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"font-size: 11px; color: {_SUB}; background: transparent;")
        lay.addWidget(sub)
        lay.addSpacing(10)

        cfg = obter_smtp_config()

        self._chk_ativo = QCheckBox("Ativar envio automático de e-mail")
        self._chk_ativo.setChecked(cfg.get("ativo", False))
        self._chk_ativo.setStyleSheet(f"color: {_TITULO}; font-size: 12px;")
        lay.addWidget(self._chk_ativo)
        lay.addSpacing(6)

        lay.addWidget(self._lbl("SERVIDOR SMTP (ex: smtp.gmail.com)"))
        self._inp_host = QLineEdit(cfg.get("host", ""))
        self._inp_host.setFixedHeight(34)
        self._inp_host.setStyleSheet(self._campo())
        lay.addWidget(self._inp_host)

        lay.addWidget(self._lbl("PORTA (geralmente 587)"))
        self._inp_porta = QSpinBox()
        self._inp_porta.setRange(1, 65535)
        self._inp_porta.setValue(int(cfg.get("porta", 587)))
        self._inp_porta.setFixedHeight(34)
        self._inp_porta.setStyleSheet(self._campo())
        lay.addWidget(self._inp_porta)

        lay.addWidget(self._lbl("USUÁRIO / E-MAIL DE ENVIO"))
        self._inp_usuario = QLineEdit(cfg.get("usuario", ""))
        self._inp_usuario.setFixedHeight(34)
        self._inp_usuario.setStyleSheet(self._campo())
        lay.addWidget(self._inp_usuario)

        lay.addWidget(self._lbl("SENHA (ou senha de app, no caso do Gmail)"))
        self._inp_senha = QLineEdit(cfg.get("senha", ""))
        self._inp_senha.setEchoMode(QLineEdit.Password)
        self._inp_senha.setFixedHeight(34)
        self._inp_senha.setStyleSheet(self._campo())
        lay.addWidget(self._inp_senha)

        lay.addWidget(self._lbl("NOME DO REMETENTE"))
        self._inp_remetente = QLineEdit(cfg.get("remetente_nome", "ThirdSys — Vencimentos"))
        self._inp_remetente.setFixedHeight(34)
        self._inp_remetente.setStyleSheet(self._campo())
        lay.addWidget(self._inp_remetente)

        lay.addWidget(self._lbl("DESTINATÁRIOS (um e-mail por linha)"))
        self._txt_destinatarios = QTextEdit()
        self._txt_destinatarios.setPlainText("\n".join(cfg.get("destinatarios", [])))
        self._txt_destinatarios.setFixedHeight(70)
        self._txt_destinatarios.setStyleSheet(f"""
            QTextEdit {{
                background: {_CARD}; color: {_TITULO};
                border: 1.5px solid #CBD5E1; border-radius: 7px;
                padding: 6px 10px; font-size: 12px;
            }}
        """)
        lay.addWidget(self._txt_destinatarios)

        lay.addSpacing(8)
        btn_testar = QPushButton("  Testar conexão")
        btn_testar.setIcon(qta.icon("fa5s.plug", color=_AZUL))
        btn_testar.setFixedHeight(34)
        btn_testar.setCursor(Qt.PointingHandCursor)
        btn_testar.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD}; color: {_AZUL};
                border: 1px solid {_AZUL}; border-radius: 7px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #EFF6FF; }}
        """)
        btn_testar.clicked.connect(self._testar)
        lay.addWidget(btn_testar)

        lay.addSpacing(12)
        btn_row = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD}; color: {_SUB};
                border: 1px solid {_BORDA}; border-radius: 7px;
                font-size: 12px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {_BG}; }}
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar configuração")
        btn_salvar.setFixedHeight(36)
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setStyleSheet(f"""
            QPushButton {{
                background: {_AZUL}; color: white;
                border: none; border-radius: 7px;
                font-size: 12px; font-weight: bold; padding: 0 20px;
            }}
            QPushButton:hover {{ background: #1D4ED8; }}
        """)
        btn_salvar.clicked.connect(self._salvar)

        btn_row.addWidget(btn_cancelar)
        btn_row.addStretch()
        btn_row.addWidget(btn_salvar)
        lay.addLayout(btn_row)

    @staticmethod
    def _lbl(texto: str) -> QLabel:
        l = QLabel(texto)
        l.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {_LABEL};"
            " letter-spacing: 1px; background: transparent; margin-top: 4px;"
        )
        return l

    def _destinatarios(self) -> list[str]:
        return [
            e.strip() for e in self._txt_destinatarios.toPlainText().splitlines()
            if e.strip()
        ]

    def _testar(self):
        try:
            testar_conexao_smtp(
                self._inp_host.text().strip(),
                self._inp_porta.value(),
                self._inp_usuario.text().strip(),
                self._inp_senha.text(),
            )
            QMessageBox.information(self, "Conexão OK",
                                     "Conectado e autenticado com sucesso no servidor SMTP.")
        except Exception as e:
            QMessageBox.critical(self, "Falha na conexão", str(e))

    def _salvar(self):
        salvar_smtp_config(
            host=self._inp_host.text().strip(),
            porta=self._inp_porta.value(),
            usuario=self._inp_usuario.text().strip(),
            senha=self._inp_senha.text(),
            remetente_nome=self._inp_remetente.text().strip(),
            destinatarios=self._destinatarios(),
            ativo=self._chk_ativo.isChecked(),
        )
        QMessageBox.information(self, "Salvo", "Configuração de e-mail salva.")
        self.accept()


# ─────────────────────────────────────────────────────────────────────────────
# Sino de notificações
# ─────────────────────────────────────────────────────────────────────────────
class SinoNotificacoes(QToolButton):
    """Botão de sino com badge de contagem. Clique abre um menu com os
    itens vencidos/a vencer, botão pra ver tudo na tela de Vencimentos, e
    botão pra configurar o e-mail."""

    navegar = Signal(str)  # emite "vencimentos" quando clica em "Ver tudo"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(32, 32)
        self.setStyleSheet("""
            QToolButton { background: transparent; border: none; border-radius: 16px; }
            QToolButton:hover { background: #1F3248; }
        """)
        self._alertas = {"vencidos": [], "a_vencer": [], "total_vencidos": 0, "total_a_vencer": 0}
        self.clicked.connect(self._abrir_menu)
        self._atualizar_icone()

        # Atualiza sozinho a cada 5 minutos, sem precisar que o usuário
        # navegue pra tela de Vencimentos pra "descobrir" que algo venceu.
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.atualizar)
        self._timer.start(5 * 60 * 1000)
        self.atualizar()

    def atualizar(self):
        try:
            self._alertas = obter_alertas()
        except Exception:
            # Não deixa um erro de consulta ao banco travar a sidebar —
            # o sino simplesmente fica sem badge até a próxima tentativa.
            return
        self._atualizar_icone()

    def _atualizar_icone(self):
        total = self._alertas["total_vencidos"] + self._alertas["total_a_vencer"]
        cor = "#6B8FAD" if total == 0 else ("#DC2626" if self._alertas["total_vencidos"] else "#D97706")
        self.setIcon(qta.icon("fa5s.bell", color=cor))
        self.setIconSize(QSize(16, 16))
        self.setToolTip(
            f"{self._alertas['total_vencidos']} vencido(s), "
            f"{self._alertas['total_a_vencer']} a vencer"
        )

    def _abrir_menu(self):
        self.atualizar()
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background: {_CARD}; border: 1px solid {_BORDA}; border-radius: 8px; padding: 6px; }}
            QMenu::item {{ padding: 6px 10px; border-radius: 6px; font-size: 12px; color: {_TITULO}; }}
            QMenu::item:selected {{ background: #F4F7FA; }}
            QMenu::separator {{ height: 1px; background: {_BORDA}; margin: 6px 4px; }}
        """)

        v, a = self._alertas["total_vencidos"], self._alertas["total_a_vencer"]
        if v == 0 and a == 0:
            menu.addAction("Nenhum vencimento pendente ✓").setEnabled(False)
        else:
            if v:
                menu.addAction(f"🔴 {v} vencido(s)").setEnabled(False)
                for ref, tipo, venc, origem in self._alertas["vencidos"][:5]:
                    menu.addAction(f"   {ref} — {tipo} ({venc.strftime('%d/%m/%Y')})").setEnabled(False)
            if a:
                menu.addAction(f"🟡 {a} a vencer (30 dias)").setEnabled(False)
                for ref, tipo, venc, origem in self._alertas["a_vencer"][:5]:
                    menu.addAction(f"   {ref} — {tipo} ({venc.strftime('%d/%m/%Y')})").setEnabled(False)

        menu.addSeparator()
        act_ver = menu.addAction("Ver tudo em Vencimentos")
        act_ver.triggered.connect(lambda: self.navegar.emit("vencimentos"))

        act_cfg = menu.addAction("Configurar alertas por e-mail")
        act_cfg.triggered.connect(self._abrir_config_email)

        act_enviar = menu.addAction("Enviar e-mail de teste agora")
        act_enviar.triggered.connect(self._enviar_agora)

        menu.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def _abrir_config_email(self):
        dlg = DialogConfigEmail(parent=self)
        dlg.exec()

    def _enviar_agora(self):
        try:
            enviar_alerta_vencimentos(self._alertas)
            QMessageBox.information(
                self, "E-mail enviado",
                "O e-mail de alerta foi enviado para os destinatários configurados."
            )
        except EmailNaoConfiguradoError as e:
            QMessageBox.warning(self, "E-mail não configurado", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Falha ao enviar", str(e))


def verificar_envio_diario_em_background():
    """Chamado uma vez ao abrir o app (MainWindow). Se o e-mail estiver
    ativado e ainda não foi enviado hoje, envia em uma thread separada —
    não trava a abertura do sistema esperando a resposta do servidor SMTP."""
    from datetime import date

    def _job():
        try:
            cfg = obter_smtp_config()
            if not cfg.get("ativo"):
                return
            if obter_ultimo_envio_email() == date.today().isoformat():
                return  # já enviado hoje
            alertas = obter_alertas()
            enviar_alerta_vencimentos(alertas, config=cfg)
            marcar_envio_email_hoje()
        except Exception:
            # Falha de e-mail (sem internet, SMTP fora, etc.) nunca deve
            # impedir o uso do sistema — só não envia e tenta de novo no
            # próximo dia/abertura.
            pass

    threading.Thread(target=_job, daemon=True).start()
