from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import sys, os, re

from app.core.api_client import login_api


def resource_path(relative_path):
    base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
    return os.path.join(base, relative_path)


def _validar_cnpj(cnpj: str) -> bool:
    c = "".join(filter(str.isdigit, cnpj))
    if len(c) != 14 or c == c[0] * 14:
        return False

    def calc(c, pesos):
        s = sum(int(c[i]) * pesos[i] for i in range(len(pesos)))
        r = s % 11
        return 0 if r < 2 else 11 - r

    p1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    p2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]
    return calc(c, p1) == int(c[12]) and calc(c, p2) == int(c[13])


def _formatar_cnpj(texto: str) -> str:
    d = "".join(filter(str.isdigit, texto))[:14]
    if len(d) <= 2:  return d
    if len(d) <= 5:  return f"{d[:2]}.{d[2:]}"
    if len(d) <= 8:  return f"{d[:2]}.{d[2:5]}.{d[5:]}"
    if len(d) <= 12: return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:]}"
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(resource_path("assets/icons/logo_t.ico")))
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        self.usuario_logado = None
        self.token = None
        self.cnpj_logado = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        # Logo
        logo = QLabel()
        pixmap = QPixmap(resource_path("assets/icons/logo_t.ico"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Título
        titulo = QLabel("Acesse sua conta")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(titulo)

        # CNPJ
        layout.addWidget(QLabel("CNPJ"))
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("00.000.000/0000-00")
        self.input_cnpj.setMaxLength(18)
        self.input_cnpj.textChanged.connect(self._mascara_cnpj)
        layout.addWidget(self.input_cnpj)

        # E-mail
        layout.addWidget(QLabel("E-mail"))
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("email@empresa.com")
        layout.addWidget(self.input_email)

        # Senha
        layout.addWidget(QLabel("Senha"))
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setPlaceholderText("••••••••")
        self.input_senha.returnPressed.connect(self._fazer_login)
        layout.addWidget(self.input_senha)

        # Botão login
        self.btn_login = QPushButton("Entrar")
        self.btn_login.setFixedHeight(42)
        self.btn_login.clicked.connect(self._fazer_login)
        layout.addWidget(self.btn_login)

        # Mensagem de erro
        self.label_erro = QLabel("")
        self.label_erro.setAlignment(Qt.AlignCenter)
        self.label_erro.setStyleSheet("color: #DC2626; font-size: 12px;")
        self.label_erro.setWordWrap(True)
        layout.addWidget(self.label_erro)

        layout.addStretch()

    def _mascara_cnpj(self, texto: str):
        cursor = self.input_cnpj.cursorPosition()
        formatado = _formatar_cnpj(texto)
        self.input_cnpj.blockSignals(True)
        self.input_cnpj.setText(formatado)
        self.input_cnpj.setCursorPosition(min(cursor + 1, len(formatado)))
        self.input_cnpj.blockSignals(False)

    def _fazer_login(self):
        cnpj  = self.input_cnpj.text().strip()
        email = self.input_email.text().strip()
        senha = self.input_senha.text()

        if not cnpj or not email or not senha:
            self.label_erro.setText("Preencha todos os campos.")
            return

        if not _validar_cnpj(cnpj):
            self.label_erro.setText("CNPJ inválido. Verifique e tente novamente.")
            return

        self.btn_login.setText("Aguarde...")
        self.btn_login.setEnabled(False)
        self.label_erro.setText("")

        resultado = login_api(cnpj, email, senha)

        self.btn_login.setText("Entrar")
        self.btn_login.setEnabled(True)

        if resultado.success:
            self.usuario_logado = resultado.usuario
            self.token          = resultado.token
            self.cnpj_logado    = "".join(filter(str.isdigit, cnpj))
            self.accept()
        else:
            self.label_erro.setText(resultado.erro)