from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import sys, os

from app.core.api_client import login_api


def resource_path(relative_path):
    base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
    return os.path.join(base, relative_path)


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(resource_path("assets/icons/logo_t.ico")))
        self.setFixedSize(400, 440)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        self.usuario_logado = None
        self.token = None

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

        # Usuário
        layout.addWidget(QLabel("Usuário"))
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("seu usuário")
        layout.addWidget(self.input_usuario)

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

    def _fazer_login(self):
        usuario = self.input_usuario.text().strip()
        senha = self.input_senha.text()

        if not usuario or not senha:
            self.label_erro.setText("Preencha todos os campos.")
            return

        self.btn_login.setText("Aguarde...")
        self.btn_login.setEnabled(False)
        self.label_erro.setText("")

        resultado = login_api(usuario, senha)

        self.btn_login.setText("Entrar")
        self.btn_login.setEnabled(True)

        if resultado.success:
            self.usuario_logado = resultado.usuario
            self.token = resultado.token
            self.accept()
        else:
            self.label_erro.setText(resultado.erro)
