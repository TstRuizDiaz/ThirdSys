import sys
import math
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen, QBrush


class GlowProgressBar(QWidget):
    """Barra estilo Windows Update — glow verde deslizando sobre fundo cinza."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(360, 22)
        self._pos = 0.0       # posição do centro do glow (0.0 a 1.0)
        self._dir = 1
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        speed = 0.012
        self._pos += speed * self._dir
        if self._pos >= 1.1:
            self._pos = 1.1
            self._dir = -1
        elif self._pos <= -0.1:
            self._pos = -0.1
            self._dir = 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # --- borda externa (cinza escuro) ---
        p.setPen(QPen(QColor(160, 160, 160), 1))
        p.setBrush(QBrush(QColor(212, 212, 212)))
        p.drawRect(0, 0, w - 1, h - 1)

        # --- fundo interno da barra (cinza claro com leve gradiente) ---
        inner = QRect(2, 2, w - 4, h - 4)
        bg = QLinearGradient(0, 2, 0, h - 2)
        bg.setColorAt(0.0, QColor(228, 228, 228))
        bg.setColorAt(0.4, QColor(215, 215, 215))
        bg.setColorAt(1.0, QColor(200, 200, 200))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bg))
        p.drawRect(inner)

        # --- glow verde deslizante ---
        glow_w = int(w * 0.38)
        cx = int(self._pos * w)

        glow = QLinearGradient(cx - glow_w, 0, cx + glow_w, 0)
        glow.setColorAt(0.0,  QColor(120, 220, 80,   0))
        glow.setColorAt(0.3,  QColor(140, 230, 90,  80))
        glow.setColorAt(0.5,  QColor(160, 255, 100, 200))
        glow.setColorAt(0.7,  QColor(140, 230, 90,  80))
        glow.setColorAt(1.0,  QColor(120, 220, 80,   0))

        p.setClipRect(inner)
        p.setBrush(QBrush(glow))
        p.drawRect(cx - glow_w, 2, glow_w * 2, h - 4)
        p.setClipping(False)

        # --- highlight branco no topo (vidro) ---
        hi = QLinearGradient(0, 2, 0, h // 2)
        hi.setColorAt(0.0, QColor(255, 255, 255, 110))
        hi.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(hi))
        p.drawRect(2, 2, w - 4, (h - 4) // 2)

        p.end()


class SplashScreen(QWidget):

    def __init__(self, on_finalizado):
        super().__init__()
        self.on_finalizado = on_finalizado

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(480, 300)
        self._centralizar()
        self._setup_ui()
        self._iniciar_progresso()

    def _centralizar(self):
        tela = QApplication.primaryScreen().geometry()
        self.move((tela.width() - 480) // 2, (tela.height() - 300) // 2)

    def paintEvent(self, event):
        # Fundo branco puro, sem QSS
        p = QPainter(self)
        p.fillRect(0, 0, self.width(), self.height(), QColor(240, 240, 240))

        # Borda fina cinza
        p.setPen(QPen(QColor(180, 180, 180), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 40)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # Título
        self._label_titulo = QLabel("Checking for updates...")
        font_titulo = QFont("Segoe UI", 13)
        self._label_titulo.setFont(font_titulo)
        self._label_titulo.setAlignment(Qt.AlignLeft)
        layout.addWidget(self._label_titulo)

        layout.addSpacing(18)

        # Barra de progresso desenhada
        self.barra = GlowProgressBar()
        layout.addWidget(self.barra, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        # Status
        self._label_status = QLabel("")
        font_status = QFont("Segoe UI", 9)
        self._label_status.setFont(font_status)
        self._label_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label_status)

        layout.addStretch()

        # Versão
        label_versao = QLabel("v1.0.0")
        font_v = QFont("Segoe UI", 8)
        label_versao.setFont(font_v)
        label_versao.setAlignment(Qt.AlignRight)
        layout.addWidget(label_versao)

    # ── progresso ──────────────────────────────────────────────────────────────

    def _iniciar_progresso(self):
        self._etapa = 0
        self._etapas = [
            (2000,  "Verificando banco de dados..."),
            (4000,  "Carregando configurações..."),
            (6000,  "Inicializando módulos..."),
            (8000,  "Verificando sessão..."),
            (10000, "Pronto!"),
        ]
        self._agendar_proxima()

    def _agendar_proxima(self):
        if self._etapa >= len(self._etapas):
            QTimer.singleShot(800, self._fechar)
            return
        delay, texto = self._etapas[self._etapa]
        # delay acumulado já passou — usar intervalo entre etapas
        intervalo = delay if self._etapa == 0 else (
            self._etapas[self._etapa][0] - self._etapas[self._etapa - 1][0]
        )
        QTimer.singleShot(intervalo, lambda t=texto: self._avancar(t))

    def _avancar(self, texto):
        self._label_status.setText(texto)
        self._etapa += 1
        self._agendar_proxima()

    def _fechar(self):
        self.barra._timer.stop()
        self.hide()
        self.on_finalizado()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    def abrir_login():
        print("→ login_window.py")

    splash = SplashScreen(on_finalizado=abrir_login)
    splash.show()
    sys.exit(app.exec())