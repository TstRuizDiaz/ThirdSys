

from __future__ import annotations

from datetime import datetime
from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox,
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QScrollArea,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

# ─────────────────────────────────────────────────────────────────────────────
# Paleta (alinhada com sidebar.py)
# ─────────────────────────────────────────────────────────────────────────────
_BG        = "#F2F5F8"
_CARD      = "#FFFFFF"
_BORDA     = "#DDE3EA"
_TITULO    = "#1C2B3A"
_SUB       = "#5A7A96"
_LABEL     = "#8AA5BC"
_AZUL      = "#2563EB"
_AZUL_BG   = "#EFF6FF"
_AZUL_BD   = "#93C5FD"
_VERDE     = "#16A34A"
_VERDE_BG  = "#F0FAF4"
_VERDE_BD  = "#86EFAC"
_VERM      = "#991B1B"
_VERM_BG   = "#FEF2F2"
_VERM_BD   = "#FCA5A5"
_AMAR      = "#92400E"
_AMAR_BG   = "#FFFBEB"
_AMAR_BD   = "#FCD34D"
_SIDEBAR   = "#253B50"
_SIDEBAR_DK= "#1F3248"
_ACENTO    = "#3B7DD8"

_NIVEL_META = {
    "Admin":    {"cor": _AZUL,  "bg": _AZUL_BG,  "bd": _AZUL_BD,  "icone": "fa5s.crown"},
    "User":     {"cor": _VERDE, "bg": _VERDE_BG, "bd": _VERDE_BD, "icone": "fa5s.user"},
    "Portaria": {"cor": _AMAR,  "bg": _AMAR_BG,  "bd": _AMAR_BD,  "icone": "fa5s.door-open"},
}

_NIVEL_DESCRICAO = {
    "Admin":    "Acesso total · Gerencia usuários",
    "User":     "Acesso total · Sem gerência de usuários",
    "Portaria": "Portaria · Consulta empresas e colaboradores",
}


# ─────────────────────────────────────────────────────────────────────────────
# Modelo de usuário (temporário — sem banco)
# ─────────────────────────────────────────────────────────────────────────────

class UsuarioLocal:
    def __init__(self, nome: str, nivel: str, ativo: bool = True,
                 criado_em: Optional[str] = None):
        self.nome      = nome
        self.nivel     = nivel   # "Admin" | "User" | "Portaria"
        self.ativo     = ativo
        self.criado_em = criado_em or datetime.now().strftime("%d/%m/%Y")

    def iniciais(self) -> str:
        partes = self.nome.strip().split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nome[:2].upper()


# ─────────────────────────────────────────────────────────────────────────────
# Repositório em memória (substituir por SQLAlchemy futuramente)
# ─────────────────────────────────────────────────────────────────────────────

class RepositorioUsuarios:
    _instancia: Optional["RepositorioUsuarios"] = None

    def __init__(self):
        self._usuarios: list[UsuarioLocal] = [
            UsuarioLocal("Administrador", "Admin",    True,  "01/01/2024"),
            UsuarioLocal("Portaria",      "Portaria", True,  "01/01/2024"),
        ]

    @classmethod
    def instancia(cls) -> "RepositorioUsuarios":
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def listar(self) -> list[UsuarioLocal]:
        return list(self._usuarios)

    def adicionar(self, u: UsuarioLocal):
        self._usuarios.append(u)

    def remover(self, nome: str):
        self._usuarios = [u for u in self._usuarios if u.nome != nome]

    def promover_admin(self, nome: str):
        for u in self._usuarios:
            if u.nome == nome:
                u.nivel = "Admin"

    def alterar_nivel(self, nome: str, novo_nivel: str):
        for u in self._usuarios:
            if u.nome == nome:
                u.nivel = novo_nivel

    def toggle_ativo(self, nome: str):
        for u in self._usuarios:
            if u.nome == nome:
                u.ativo = not u.ativo

    def nome_existe(self, nome: str) -> bool:
        return any(u.nome.lower() == nome.lower() for u in self._usuarios)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers visuais
# ─────────────────────────────────────────────────────────────────────────────

def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {_BORDA}; border: none;")
    return f


def _label_secao(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setStyleSheet(
        f"font-size: 9px; font-weight: bold; color: {_LABEL};"
        " letter-spacing: 1.4px; background: transparent;"
    )
    return lbl


def _badge_nivel(nivel: str) -> QLabel:
    m   = _NIVEL_META.get(nivel, _NIVEL_META["User"])
    lbl = QLabel(nivel)
    lbl.setStyleSheet(f"""
        background: {m['bg']}; color: {m['cor']};
        border: 1px solid {m['bd']};
        border-radius: 4px; padding: 1px 8px;
        font-size: 10px; font-weight: bold;
    """)
    return lbl


def _avatar(iniciais: str, nivel: str, tamanho: int = 34) -> QLabel:
    m   = _NIVEL_META.get(nivel, _NIVEL_META["User"])
    lbl = QLabel(iniciais)
    lbl.setFixedSize(tamanho, tamanho)
    lbl.setAlignment(Qt.AlignCenter)
    r   = tamanho // 2
    lbl.setStyleSheet(f"""
        background: {m['bg']}; color: {m['cor']};
        border: 1.5px solid {m['bd']};
        border-radius: {r}px;
        font-size: {tamanho // 3}px; font-weight: bold;
    """)
    return lbl


def _btn_icon(icone: str, cor: str, tooltip: str,
              tamanho: int = 28) -> QToolButton:
    b = QToolButton()
    b.setIcon(qta.icon(icone, color=cor))
    b.setIconSize(QSize(13, 13))
    b.setFixedSize(tamanho, tamanho)
    b.setToolTip(tooltip)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QToolButton {{
            background: transparent; border: 1px solid {_BORDA};
            border-radius: 6px;
        }}
        QToolButton:hover {{ background: {_BG}; border-color: {_LABEL}; }}
    """)
    return b


# ─────────────────────────────────────────────────────────────────────────────
# Dialog: Adicionar / Editar Usuário
# ─────────────────────────────────────────────────────────────────────────────

class DialogFormUsuario(QDialog):
    """Formulário para criar ou editar um usuário."""

    def __init__(self, usuario: Optional[UsuarioLocal] = None, parent=None):
        super().__init__(parent)
        self._usuario = usuario
        self._editando = usuario is not None
        self.setWindowTitle("Editar usuário" if self._editando else "Novo usuário")
        self.setFixedWidth(380)
        self.setModal(True)
        self.setStyleSheet(f"background: {_BG};")
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 24)
        lay.setSpacing(0)

        # Cabeçalho
        hdr = QHBoxLayout()
        ic  = QLabel()
        ic.setPixmap(
            qta.icon("fa5s.user-edit" if self._editando else "fa5s.user-plus",
                     color=_AZUL).pixmap(20, 20)
        )
        ic.setStyleSheet("background: transparent;")
        hdr.addWidget(ic)
        titulo = QLabel("Editar usuário" if self._editando else "Novo usuário")
        titulo.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {_TITULO};"
            " background: transparent; padding-left: 8px;"
        )
        hdr.addWidget(titulo)
        hdr.addStretch()
        lay.addLayout(hdr)

        lay.addSpacing(20)

        # Campo nome
        lay.addWidget(_label_secao("NOME DO USUÁRIO"))
        lay.addSpacing(6)
        self._inp_nome = QLineEdit()
        self._inp_nome.setPlaceholderText("Ex: João Silva")
        self._inp_nome.setFixedHeight(36)
        if self._editando:
            self._inp_nome.setText(self._usuario.nome)
            self._inp_nome.setReadOnly(True)
            self._inp_nome.setStyleSheet(f"""
                QLineEdit {{
                    background: {_BG}; color: {_LABEL};
                    border: 1.5px solid {_BORDA}; border-radius: 7px;
                    padding: 0 12px; font-size: 13px;
                }}
            """)
        else:
            self._inp_nome.setStyleSheet(f"""
                QLineEdit {{
                    background: {_CARD}; color: {_TITULO};
                    border: 1.5px solid #CBD5E1; border-radius: 7px;
                    padding: 0 12px; font-size: 13px;
                }}
                QLineEdit:focus {{ border-color: {_AZUL}; background: {_AZUL_BG}; }}
            """)
        lay.addWidget(self._inp_nome)

        lay.addSpacing(16)

        # Nível de acesso
        lay.addWidget(_label_secao("NÍVEL DE ACESSO"))
        lay.addSpacing(6)
        self._combo_nivel = QComboBox()
        self._combo_nivel.addItems(["Admin", "User", "Portaria"])
        if self._editando:
            self._combo_nivel.setCurrentText(self._usuario.nivel)
        self._combo_nivel.setFixedHeight(36)
        self._combo_nivel.setStyleSheet(f"""
            QComboBox {{
                background: {_CARD}; color: {_TITULO};
                border: 1.5px solid #CBD5E1; border-radius: 7px;
                padding: 0 12px; font-size: 13px;
            }}
            QComboBox:focus {{ border-color: {_AZUL}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: {_CARD}; color: {_TITULO};
                border: 1px solid {_BORDA};
                selection-background-color: {_AZUL_BG};
            }}
        """)
        lay.addWidget(self._combo_nivel)

        lay.addSpacing(8)

        # Descrição dinâmica do nível
        self._lbl_desc = QLabel()
        self._lbl_desc.setWordWrap(True)
        self._lbl_desc.setStyleSheet(
            f"font-size: 11px; color: {_SUB}; background: transparent;"
        )
        self._atualizar_desc(self._combo_nivel.currentText())
        self._combo_nivel.currentTextChanged.connect(self._atualizar_desc)
        lay.addWidget(self._lbl_desc)

        lay.addSpacing(24)

        # Botões
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

        lbl_salvar = "Salvar alterações" if self._editando else "Adicionar usuário"
        btn_salvar = QPushButton(lbl_salvar)
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

    def _atualizar_desc(self, nivel: str):
        self._lbl_desc.setText(f"↳  {_NIVEL_DESCRICAO.get(nivel, '')}")

    def _salvar(self):
        nome  = self._inp_nome.text().strip()
        nivel = self._combo_nivel.currentText()

        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do usuário.")
            return

        repo = RepositorioUsuarios.instancia()

        if not self._editando:
            if repo.nome_existe(nome):
                QMessageBox.warning(self, "Nome duplicado",
                                    f"Já existe um usuário com o nome '{nome}'.")
                return
            repo.adicionar(UsuarioLocal(nome, nivel))
        else:
            repo.alterar_nivel(self._usuario.nome, nivel)

        self.accept()


# ─────────────────────────────────────────────────────────────────────────────
# Card de usuário individual
# ─────────────────────────────────────────────────────────────────────────────

class CardUsuario(QFrame):
    sinal_editar   = Signal(str)   # nome
    sinal_remover  = Signal(str)
    sinal_toggle   = Signal(str)

    def __init__(self, usuario: UsuarioLocal, eh_admin_logado: bool, parent=None):
        super().__init__(parent)
        self._usuario       = usuario
        self._eh_admin_logado = eh_admin_logado
        self._setup_ui()

    def _setup_ui(self):
        u   = self._usuario
        m   = _NIVEL_META.get(u.nivel, _NIVEL_META["User"])
        opacidade = "1.0" if u.ativo else "0.5"

        self.setStyleSheet(f"""
            QFrame {{
                background: {_CARD};
                border: 1px solid {_BORDA};
                border-left: 3px solid {m['cor']};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 12, 12)
        root.setSpacing(12)

        # Avatar
        av = _avatar(u.iniciais(), u.nivel, 36)
        av.setStyleSheet(av.styleSheet() + f" opacity: {opacidade};")
        root.addWidget(av)

        # Info
        info = QVBoxLayout()
        info.setSpacing(2)

        nome_row = QHBoxLayout()
        nome_row.setSpacing(8)
        lbl_nome = QLabel(u.nome)
        lbl_nome.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {_TITULO};"
        )
        nome_row.addWidget(lbl_nome)
        nome_row.addWidget(_badge_nivel(u.nivel))
        if not u.ativo:
            lbl_inativo = QLabel("INATIVO")
            lbl_inativo.setStyleSheet(f"""
                background: {_VERM_BG}; color: {_VERM};
                border: 1px solid {_VERM_BD};
                border-radius: 4px; padding: 1px 8px;
                font-size: 9px; font-weight: bold;
            """)
            nome_row.addWidget(lbl_inativo)
        nome_row.addStretch()
        info.addLayout(nome_row)

        lbl_desc = QLabel(_NIVEL_DESCRICAO.get(u.nivel, ""))
        lbl_desc.setStyleSheet(f"font-size: 10px; color: {_LABEL};")
        info.addWidget(lbl_desc)

        lbl_data = QLabel(f"Criado em {u.criado_em}")
        lbl_data.setStyleSheet(f"font-size: 10px; color: {_LABEL};")
        info.addWidget(lbl_data)

        root.addLayout(info, 1)

        # Ações (somente para admin logado)
        if self._eh_admin_logado:
            acoes = QHBoxLayout()
            acoes.setSpacing(4)

            # Editar
            btn_edit = _btn_icon("fa5s.pen", _AZUL, "Editar nível")
            btn_edit.clicked.connect(lambda: self.sinal_editar.emit(u.nome))
            acoes.addWidget(btn_edit)

            # Ativar / Desativar
            if u.ativo:
                btn_tog = _btn_icon("fa5s.toggle-on", _VERDE, "Desativar usuário")
            else:
                btn_tog = _btn_icon("fa5s.toggle-off", _LABEL, "Ativar usuário")
            btn_tog.clicked.connect(lambda: self.sinal_toggle.emit(u.nome))
            acoes.addWidget(btn_tog)

            # Remover (não pode remover o próprio admin primário)
            btn_del = _btn_icon("fa5s.trash-alt", _VERM, "Remover usuário")
            btn_del.clicked.connect(lambda: self.sinal_remover.emit(u.nome))
            acoes.addWidget(btn_del)

            root.addLayout(acoes)


# ─────────────────────────────────────────────────────────────────────────────
# Painel de usuários
# ─────────────────────────────────────────────────────────────────────────────

class PainelUsuarios(QWidget):
    """Lista rolável de usuários com barra de filtro e botão adicionar."""

    def __init__(self, eh_admin: bool, parent=None):
        super().__init__(parent)
        self._eh_admin   = eh_admin
        self._filtro_nivel = "Todos"
        self.setStyleSheet(f"background: transparent;")
        self._setup_ui()
        self.recarregar()

    def _setup_ui(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(10)

        # Barra de ações
        barra = QHBoxLayout()
        barra.setSpacing(8)

        # Filtro rápido por nível
        self._combo_filtro = QComboBox()
        self._combo_filtro.addItems(["Todos", "Admin", "User", "Portaria"])
        self._combo_filtro.setFixedHeight(32)
        self._combo_filtro.setStyleSheet(f"""
            QComboBox {{
                background: {_CARD}; color: {_TITULO};
                border: 1px solid {_BORDA}; border-radius: 7px;
                padding: 0 10px; font-size: 11px;
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {_CARD}; color: {_TITULO};
                border: 1px solid {_BORDA};
                selection-background-color: {_AZUL_BG};
            }}
        """)
        self._combo_filtro.currentTextChanged.connect(self._on_filtro)
        barra.addWidget(self._combo_filtro)

        # Contagem
        self._lbl_contagem = QLabel()
        self._lbl_contagem.setStyleSheet(
            f"font-size: 11px; color: {_LABEL}; background: transparent;"
        )
        barra.addWidget(self._lbl_contagem)
        barra.addStretch()

        if self._eh_admin:
            btn_add = QPushButton("  Adicionar usuário")
            btn_add.setIcon(qta.icon("fa5s.user-plus", color="white"))
            btn_add.setIconSize(QSize(12, 12))
            btn_add.setFixedHeight(32)
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.setStyleSheet(f"""
                QPushButton {{
                    background: {_AZUL}; color: white;
                    border: none; border-radius: 7px;
                    font-size: 11px; font-weight: bold; padding: 0 14px;
                }}
                QPushButton:hover {{ background: #1D4ED8; }}
            """)
            btn_add.clicked.connect(self._adicionar)
            barra.addWidget(btn_add)

        self._root.addLayout(barra)

        # Área rolável
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._lista_widget = QWidget()
        self._lista_widget.setStyleSheet("background: transparent;")
        self._lista_layout = QVBoxLayout(self._lista_widget)
        self._lista_layout.setContentsMargins(0, 0, 0, 0)
        self._lista_layout.setSpacing(8)
        self._lista_layout.addStretch()

        scroll.setWidget(self._lista_widget)
        scroll.setMinimumHeight(260)
        self._root.addWidget(scroll, 1)

    def _on_filtro(self, nivel: str):
        self._filtro_nivel = nivel
        self.recarregar()

    def recarregar(self):
        # Limpa cards existentes (preserva o stretch)
        while self._lista_layout.count() > 1:
            item = self._lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        repo     = RepositorioUsuarios.instancia()
        usuarios = repo.listar()

        if self._filtro_nivel != "Todos":
            usuarios = [u for u in usuarios if u.nivel == self._filtro_nivel]

        ativos   = sum(1 for u in usuarios if u.ativo)
        total    = len(usuarios)
        self._lbl_contagem.setText(
            f"{ativos} ativo{'s' if ativos != 1 else ''} · {total} total"
        )

        if not usuarios:
            lbl = QLabel("Nenhum usuário encontrado.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {_LABEL}; font-size: 12px; padding: 20px;")
            self._lista_layout.insertWidget(0, lbl)
            return

        for u in usuarios:
            card = CardUsuario(u, self._eh_admin)
            card.sinal_editar.connect(self._editar)
            card.sinal_remover.connect(self._remover)
            card.sinal_toggle.connect(self._toggle)
            self._lista_layout.insertWidget(
                self._lista_layout.count() - 1, card
            )

    def _adicionar(self):
        dlg = DialogFormUsuario(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.recarregar()

    def _editar(self, nome: str):
        repo = RepositorioUsuarios.instancia()
        u    = next((x for x in repo.listar() if x.nome == nome), None)
        if not u:
            return
        dlg = DialogFormUsuario(usuario=u, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.recarregar()

    def _remover(self, nome: str):
        repo   = RepositorioUsuarios.instancia()
        admins = [u for u in repo.listar() if u.nivel == "Admin"]
        if len(admins) == 1 and admins[0].nome == nome:
            QMessageBox.warning(
                self, "Operação negada",
                "Não é possível remover o único administrador do sistema."
            )
            return
        resp = QMessageBox.question(
            self, "Remover usuário",
            f"Deseja remover '{nome}' permanentemente?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            repo.remover(nome)
            self.recarregar()

    def _toggle(self, nome: str):
        repo   = RepositorioUsuarios.instancia()
        u      = next((x for x in repo.listar() if x.nome == nome), None)
        admins = [x for x in repo.listar() if x.nivel == "Admin" and x.ativo]
        if u and u.ativo and u.nivel == "Admin" and len(admins) == 1:
            QMessageBox.warning(
                self, "Operação negada",
                "Não é possível desativar o único administrador ativo."
            )
            return
        repo.toggle_ativo(nome)
        self.recarregar()


# ─────────────────────────────────────────────────────────────────────────────
# Dialog principal
# ─────────────────────────────────────────────────────────────────────────────

class DialogLicenca(QDialog):
    """
    Abre ao clicar no avatar da Sidebar.
    Passe o usuário logado para controlar permissões de edição.

    Uso:
        dlg = DialogLicenca(usuario_logado=self.usuario, parent=self)
        dlg.exec()
    """

    def __init__(self, usuario_logado=None, parent=None):
        super().__init__(parent)
        self._usuario_logado = usuario_logado
        self._eh_admin = (
            usuario_logado is None or
            getattr(usuario_logado, "nivel", "Admin") == "Admin"
        )
        self.setWindowTitle("Sistema · Licença e Usuários")
        self.setFixedWidth(520)
        self.setModal(True)
        self.setStyleSheet(f"background: {_BG};")
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Cabeçalho colorido ────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background: {_SIDEBAR};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)
        h_lay.setSpacing(14)

        ic_hdr = QLabel()
        ic_hdr.setPixmap(qta.icon("fa5s.shield-alt", color=_ACENTO).pixmap(28, 28))
        ic_hdr.setStyleSheet("background: transparent;")
        h_lay.addWidget(ic_hdr)

        txt_hdr = QVBoxLayout()
        txt_hdr.setSpacing(2)
        lbl_hdr = QLabel("ThirdSys — Gestão de Terceiros")
        lbl_hdr.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #E8F0F8;"
            " background: transparent;"
        )
        lbl_sub = QLabel("Licença e controle de usuários")
        lbl_sub.setStyleSheet(
            f"font-size: 11px; color: {_LABEL}; background: transparent;"
        )
        txt_hdr.addWidget(lbl_hdr)
        txt_hdr.addWidget(lbl_sub)
        h_lay.addLayout(txt_hdr)
        h_lay.addStretch()

        # Botão fechar no header
        btn_x = QToolButton()
        btn_x.setIcon(qta.icon("fa5s.times", color="#6B8FAD"))
        btn_x.setIconSize(QSize(14, 14))
        btn_x.setFixedSize(30, 30)
        btn_x.setCursor(Qt.PointingHandCursor)
        btn_x.setStyleSheet(f"""
            QToolButton {{ background: transparent; border: none; border-radius: 6px; }}
            QToolButton:hover {{ background: {_SIDEBAR_DK}; }}
        """)
        btn_x.clicked.connect(self.accept)
        h_lay.addWidget(btn_x)

        lay.addWidget(header)

        # ── Corpo ─────────────────────────────────────────────────────────────
        corpo = QWidget()
        corpo.setStyleSheet(f"background: {_BG};")
        c_lay = QVBoxLayout(corpo)
        c_lay.setContentsMargins(24, 20, 24, 20)
        c_lay.setSpacing(20)

        # ── Seção: Cliente ────────────────────────────────────────────────────
        c_lay.addWidget(_label_secao("CLIENTE"))
        card_cliente = self._card_cliente()
        c_lay.addWidget(card_cliente)

        # ── Seção: Licença ────────────────────────────────────────────────────
        c_lay.addWidget(_label_secao("LICENÇA"))
        card_licenca = self._card_licenca()
        c_lay.addWidget(card_licenca)

        # ── Seção: Usuários ───────────────────────────────────────────────────
        hdr_usr = QHBoxLayout()
        hdr_usr.addWidget(_label_secao("USUÁRIOS DO SISTEMA"))
        hdr_usr.addStretch()
        if not self._eh_admin:
            lbl_aviso = QLabel("Somente Admin pode gerenciar usuários")
            lbl_aviso.setStyleSheet(
                f"font-size: 10px; color: {_AMAR}; background: transparent;"
            )
            hdr_usr.addWidget(lbl_aviso)
        c_lay.addLayout(hdr_usr)

        self._painel = PainelUsuarios(eh_admin=self._eh_admin)
        c_lay.addWidget(self._painel, 1)

        # ── Rodapé ────────────────────────────────────────────────────────────
        c_lay.addWidget(_sep())
        rod = QHBoxLayout()
        lbl_rod = QLabel(
            f"Desenvolvido por Santiago Ruiz  ·  v1.0.0  ·  "
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        lbl_rod.setStyleSheet(
            f"font-size: 10px; color: {_LABEL}; background: transparent;"
        )
        rod.addWidget(lbl_rod)
        rod.addStretch()

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setFixedSize(90, 34)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background: {_SIDEBAR}; color: white;
                border: none; border-radius: 7px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {_SIDEBAR_DK}; }}
        """)
        btn_fechar.clicked.connect(self.accept)
        rod.addWidget(btn_fechar)
        c_lay.addLayout(rod)

        lay.addWidget(corpo, 1)

    # ── Cards ─────────────────────────────────────────────────────────────────

    def _card_cliente(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {_CARD}; border: 1px solid {_BORDA};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(20)

        def _info(icone, rotulo, valor):
            col = QVBoxLayout()
            col.setSpacing(3)
            topo = QHBoxLayout()
            topo.setSpacing(6)
            ic = QLabel()
            ic.setPixmap(qta.icon(icone, color=_LABEL).pixmap(11, 11))
            lbl_r = QLabel(rotulo)
            lbl_r.setStyleSheet(f"font-size: 9px; color: {_LABEL}; font-weight: bold; letter-spacing: 1px;")
            topo.addWidget(ic)
            topo.addWidget(lbl_r)
            topo.addStretch()
            col.addLayout(topo)
            lbl_v = QLabel(valor)
            lbl_v.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {_TITULO};")
            col.addWidget(lbl_v)
            return col

        lay.addLayout(_info("fa5s.building",       "EMPRESA",  "Lactalis Brasil"))
        self._v_sep(lay)
        lay.addLayout(_info("fa5s.map-marker-alt", "UNIDADE",  "Goiânia — GO"))
        self._v_sep(lay)
        lay.addLayout(_info("fa5s.calendar-alt",   "CLIENTE DESDE", "Jun 2026"))
        lay.addStretch()
        return frame

    def _card_licenca(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {_AZUL_BG};
                border: 1px solid {_AZUL_BD};
                border-left: 3px solid {_AZUL};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(16)

        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.infinity", color=_AZUL).pixmap(22, 22))
        lay.addWidget(ic)

        info = QVBoxLayout()
        info.setSpacing(3)
        lbl_plano = QLabel("Plano Vitalício")
        lbl_plano.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {_AZUL};"
        )
        lbl_det = QLabel("Licença perpétua · Sem data de expiração · Atualizações incluídas")
        lbl_det.setStyleSheet(f"font-size: 11px; color: {_SUB};")
        info.addWidget(lbl_plano)
        info.addWidget(lbl_det)
        lay.addLayout(info, 1)

        badge = QLabel("● ATIVO")
        badge.setStyleSheet(f"""
            background: {_VERDE_BG}; color: {_VERDE};
            border: 1px solid {_VERDE_BD};
            border-radius: 5px; padding: 4px 12px;
            font-size: 11px; font-weight: bold;
        """)
        lay.addWidget(badge)
        return frame

    @staticmethod
    def _v_sep(lay: QHBoxLayout):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet(f"background: {_BORDA}; border: none;")
        lay.addWidget(line)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    class _UsuarioFake:
        nome  = "Administrador"
        nivel = "Admin"

    dlg = DialogLicenca(usuario_logado=_UsuarioFake())
    dlg.exec()
    sys.exit(0)