from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
    QDialog, QToolButton, QApplication
)
from PySide6.QtCore import Signal, Qt, QSize, QTimer
from PySide6.QtGui import QFont
import qtawesome as qta

from app.ui.components.dialog_licenca import DialogLicenca

COR_SIDEBAR_BG      = "#253B50"
COR_SIDEBAR_BORDA   = "#243447"
COR_ITEM_TEXTO      = "#A8BED1"
COR_ITEM_ICONE      = "#6B8FAD"
COR_ATIVO_BG        = "#243447"
COR_ATIVO_ACENTO    = "#3B7DD8"
COR_ATIVO_TEXTO     = "#E8F0F8"
COR_HOVER_BG        = "#1F3248"
COR_USUARIO_TEXTO   = "#C5D8EA"
COR_VERSAO          = "#3A5570"
COR_LOGO_TITULO     = "#E8F0F8"
COR_LOGO_SUB        = "#6B8FAD"


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Dialog de Suporte / Contato
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class DialogContato(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Suporte & Contato")
        self.setFixedWidth(360)
        self.setModal(True)
        self.setStyleSheet("background: #F2F5F8;")
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 24)
        lay.setSpacing(0)

        hdr = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.headset", color="#3B7DD8").pixmap(22, 22))
        ic.setStyleSheet("background: transparent;")
        hdr.addWidget(ic)

        titulo = QLabel("Suporte & Contato")
        titulo.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1C2B3A;"
            " background: transparent; padding-left: 8px;"
        )
        hdr.addWidget(titulo)
        hdr.addStretch()
        lay.addLayout(hdr)

        lay.addSpacing(6)

        sub = QLabel("Desenvolvedor: Santiago Ruiz")
        sub.setStyleSheet("font-size: 11px; color: #5A7A96; background: transparent;")
        lay.addWidget(sub)

        lay.addSpacing(20)

        lay.addWidget(self._criar_linha_contato(
            icone="fa5s.phone-alt",
            cor_icone="#16A34A",
            cor_bg="#F0FAF4",
            cor_borda="#86EFAC",
            rotulo="TELEFONE / WHATSAPP",
            valor="(62) 98112-5673",
        ))

        lay.addSpacing(12)

        lay.addWidget(self._criar_linha_contato(
            icone="fa5s.envelope",
            cor_icone="#2563EB",
            cor_bg="#EFF6FF",
            cor_borda="#93C5FD",
            rotulo="E-MAIL",
            valor="Santiagoruiz.job@gmail.com",
        ))

        lay.addSpacing(24)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setFixedHeight(38)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background: #253B50; color: white; border: none;
                border-radius: 7px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #1F3248; }
        """)
        btn_fechar.clicked.connect(self.accept)
        lay.addWidget(btn_fechar)

    def _criar_linha_contato(self, icone, cor_icone, cor_bg,
                              cor_borda, rotulo, valor) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {cor_bg};
                border: 1px solid {cor_borda};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        lbl_rotulo = QLabel(rotulo)
        lbl_rotulo.setStyleSheet(
            "font-size: 9px; font-weight: bold; color: #8AA5BC; letter-spacing: 1.2px;"
        )
        lay.addWidget(lbl_rotulo)

        linha = QHBoxLayout()
        linha.setSpacing(8)
        linha.setContentsMargins(0, 0, 0, 0)

        ic = QLabel()
        ic.setPixmap(qta.icon(icone, color=cor_icone).pixmap(14, 14))
        ic.setStyleSheet("background: transparent;")
        linha.addWidget(ic)

        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("font-size: 14px; font-weight: bold; color: #1C2B3A;")
        linha.addWidget(lbl_valor)
        linha.addStretch()

        btn_copiar = QToolButton()
        btn_copiar.setIcon(qta.icon("fa5s.copy", color="#8AA5BC"))
        btn_copiar.setIconSize(QSize(14, 14))
        btn_copiar.setToolTip("Copiar")
        btn_copiar.setCursor(Qt.PointingHandCursor)
        btn_copiar.setStyleSheet("""
            QToolButton {
                background: transparent; border: none; padding: 4px;
                border-radius: 4px;
            }
            QToolButton:hover { background: rgba(0,0,0,0.08); }
        """)
        btn_copiar.clicked.connect(lambda _, v=valor: self._copiar(v, btn_copiar))
        linha.addWidget(btn_copiar)

        lay.addLayout(linha)
        return frame

    @staticmethod
    def _copiar(texto: str, btn: QToolButton):
        QApplication.clipboard().setText(texto)
        btn.setIcon(qta.icon("fa5s.check", color="#16A34A"))
        QTimer.singleShot(1500, lambda: btn.setIcon(qta.icon("fa5s.copy", color="#8AA5BC")))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Sidebar
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class Sidebar(QWidget):
    nav_item_clicked = Signal(str)

    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self.setFixedWidth(230)
        self.setStyleSheet(f"background-color: {COR_SIDEBAR_BG}; border: none;")
        self._botoes = {}
        self._icones = {}
        self._ativo  = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # â”€â”€ Logo / CabeÃ§alho â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(f"background-color: {COR_SIDEBAR_BG}; border: none;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 16, 0)
        h_layout.setSpacing(10)

        logo_ic = QLabel()
        logo_ic.setPixmap(qta.icon("fa5s.shield-alt", color=COR_ATIVO_ACENTO).pixmap(22, 22))
        logo_ic.setStyleSheet("background: transparent;")
        h_layout.addWidget(logo_ic)

        logo_txt = QVBoxLayout()
        logo_txt.setSpacing(0)
        sub_app = QLabel("GestÃ£o de Terceiros")
        sub_app.setStyleSheet(
            f"color: {COR_LOGO_SUB}; font-size: 10px; background: transparent;"
        )
        logo_txt.addWidget(sub_app)
        h_layout.addLayout(logo_txt)
        h_layout.addStretch()
        layout.addWidget(header)

        # â”€â”€ Separador â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        layout.addWidget(self._separador())

        # â”€â”€ Menu principal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        layout.addWidget(self._secao_label("MENU PRINCIPAL"))

        itens = [
            ("dashboard",     "fa5s.th-large",             "Dashboard"),
            ("empresas",      "fa5s.building",             "Empresas"),
            ("trabalhadores", "fa5s.hard-hat",             "Trabalhadores"),
            ("documentos",    "fa5s.file-alt",             "Documentos"),
            ("vencimentos",   "fa5s.exclamation-triangle", "Vencimentos"),
            ("relatorios",    "fa5s.chart-bar",            "RelatÃ³rios"),
        ]
        for chave, icone, texto in itens:
            layout.addWidget(self._criar_botao(chave, icone, texto))

        layout.addSpacing(8)
        layout.addWidget(self._separador())
        layout.addWidget(self._secao_label("SISTEMA"))

        layout.addWidget(self._criar_botao("portaria", "fa5s.sign-in-alt", "Portaria"))

        layout.addStretch()

        # â”€â”€ RodapÃ© â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        layout.addWidget(self._separador())

        if self.usuario:
            rodape = QWidget()
            rodape.setStyleSheet(f"background-color: {COR_SIDEBAR_BG}; border: none;")
            r_layout = QHBoxLayout(rodape)
            r_layout.setContentsMargins(16, 12, 16, 12)
            r_layout.setSpacing(10)

            avatar = QLabel()
            avatar.setFixedSize(32, 32)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setPixmap(
                qta.icon("fa5s.user-circle", color=COR_ATIVO_ACENTO).pixmap(20, 20)
            )
            avatar.setStyleSheet(
                f"background-color: {COR_ATIVO_BG}; border-radius: 16px; border: none;"
            )
            avatar.setCursor(Qt.PointingHandCursor)
            avatar.setToolTip("Clique para ver licenÃ§a e usuÃ¡rios")
            avatar.mousePressEvent = lambda _: self._abrir_licenca()
            r_layout.addWidget(avatar)

            info = QVBoxLayout()
            info.setSpacing(1)

            nome_label = QLabel(self.usuario.get("nome", "Usuário") if isinstance(self.usuario, dict) else self.usuario.nome)
            nome_label.setStyleSheet(
                f"color: {COR_USUARIO_TEXTO}; font-size: 12px;"
                " font-weight: bold; background: transparent;"
            )
            nome_label.setMaximumWidth(150)
            info.addWidget(nome_label)

            nivel = getattr(self.usuario, "nivel", "UsuÃ¡rio")
            cargo_label = QLabel(nivel)
            cargo_label.setStyleSheet(
                f"color: {COR_LOGO_SUB}; font-size: 10px; background: transparent;"
            )
            info.addWidget(cargo_label)

            r_layout.addLayout(info)
            r_layout.addStretch()
            layout.addWidget(rodape)

        layout.addWidget(self._separador())

        # â”€â”€ BotÃ£o de suporte â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        btn_suporte = QPushButton("   Suporte & Contato")
        btn_suporte.setIcon(qta.icon("fa5s.headset", color="#3B7DD8"))
        btn_suporte.setIconSize(QSize(13, 13))
        btn_suporte.setFixedHeight(38)
        btn_suporte.setCursor(Qt.PointingHandCursor)
        btn_suporte.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COR_ITEM_TEXTO};
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COR_HOVER_BG};
                color: {COR_ITEM_TEXTO};
            }}
        """)
        btn_suporte.clicked.connect(self._abrir_contato)
        layout.addWidget(btn_suporte)

        ver = QLabel("v1.0.0")
        ver.setAlignment(Qt.AlignCenter)
        ver.setFixedHeight(22)
        ver.setStyleSheet(
            f"color: {COR_VERSAO}; font-size: 10px; background: transparent;"
        )
        layout.addWidget(ver)
        layout.addSpacing(6)

    # â”€â”€ AÃ§Ãµes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _abrir_licenca(self):
        dlg = DialogLicenca(usuario_logado=self.usuario, parent=self)
        dlg.exec()

    def _abrir_contato(self):
        dlg = DialogContato(self)
        dlg.exec()

    # â”€â”€ Helpers de layout â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _separador(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COR_SIDEBAR_BORDA}; border: none;")
        return sep

    def _secao_label(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setContentsMargins(20, 10, 0, 4)
        lbl.setStyleSheet(
            f"color: {COR_VERSAO}; font-size: 9px; font-weight: bold;"
            " letter-spacing: 1.2px; background: transparent;"
        )
        return lbl

    def _criar_botao(self, chave: str, icone: str, texto: str) -> QPushButton:
        btn = QPushButton(f"   {texto}")
        btn.setIcon(qta.icon(icone, color=COR_ITEM_ICONE))
        btn.setIconSize(QSize(15, 15))
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._estilo_inativo())
        btn.clicked.connect(lambda _, k=chave: self._on_click(k))
        self._botoes[chave] = btn
        self._icones[chave] = icone
        return btn

    def _estilo_inativo(self) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {COR_ITEM_TEXTO};
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding-left: 17px;
                font-size: 13px;
                border-radius: 0;
            }}
            QPushButton:hover {{
                background-color: {COR_HOVER_BG};
                color: {COR_ATIVO_TEXTO};
                border-left: 3px solid {COR_SIDEBAR_BORDA};
            }}
        """

    def _estilo_ativo(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COR_ATIVO_BG};
                color: {COR_ATIVO_TEXTO};
                border: none;
                border-left: 3px solid {COR_ATIVO_ACENTO};
                text-align: left;
                padding-left: 17px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 0;
            }}
        """

    def _on_click(self, chave: str):
        self.set_ativo(chave)
        self.nav_item_clicked.emit(chave)

    def set_ativo(self, chave: str):
        if self._ativo and self._ativo in self._botoes:
            self._botoes[self._ativo].setStyleSheet(self._estilo_inativo())
            self._botoes[self._ativo].setIcon(
                qta.icon(self._icones[self._ativo], color=COR_ITEM_ICONE)
            )
        self._ativo = chave
        if chave in self._botoes:
            self._botoes[chave].setStyleSheet(self._estilo_ativo())
            self._botoes[chave].setIcon(
                qta.icon(self._icones[chave], color=COR_ATIVO_ACENTO)
            )
