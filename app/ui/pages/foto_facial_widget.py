"""
foto_facial_widget.py
─────────────────────────────────────────────────────────────────────────────
Modulo de cadastro de foto facial do colaborador.
Compativel com webcam USB ou celular como webcam (DroidCam, OBS Virtual Cam).

Componentes exportados:
    FotoFacialWidget   — widget inline para o formulario do colaborador
    CameraDialog       — modal de captura com preview ao vivo + deteccao de rosto
    _get_foto_path     — helper para resolver o caminho da foto salva

Deteccao inteligente:
    O botao Capturar so e habilitado quando um rosto e detectado e esta
    centralizado dentro do circulo guia. O circulo muda de cor:
      - Cinza   = aguardando rosto
      - Amarelo = rosto detectado, mas fora do centro
      - Verde   = rosto centralizado, pode capturar
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import shutil
import threading
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import QSize, Qt, QTimer, Signal, QThread, QObject
from PySide6.QtGui import (
    QImage, QPixmap, QFont, QPainter, QPen, QColor, QPainterPath
)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget, QComboBox,
)

try:
    import qtawesome as qta
    _HAS_QTA = True
except ImportError:
    _HAS_QTA = False


# Paleta
_BG          = "#F0F4F8"
_CARD_BG     = "#FFFFFF"
_CARD_BORDA  = "#E2E8F0"
_TITULO      = "#1A2B4A"
_SUBTITULO   = "#64748B"
_VERDE_BG    = "#DCFCE7"
_VERDE_COR   = "#16A34A"
_VERDE_BORDA = "#86EFAC"
_AZUL_BG     = "#EFF6FF"
_AZUL_COR    = "#2563EB"
_AZUL_BORDA  = "#93C5FD"
_VERM_BG     = "#FEE2E2"
_VERM_COR    = "#DC2626"
_VERM_BORDA  = "#FCA5A5"
_AMAR_COR    = "#D97706"
_CINZA_COR   = "#94A3B8"

# Cores do circulo guia
_CIRCULO_AGUARDANDO = "#475569"
_CIRCULO_DETECTADO  = "#D97706"
_CIRCULO_OK         = "#16A34A"

# Haar Cascade
_CASCADE_PATH = str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
_face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de caminho
# ─────────────────────────────────────────────────────────────────────────────

def _get_foto_path(nome_empresa: str, nome_colab: str) -> Optional[Path]:
    try:
        from app.core.settings import docs_colaborador
        pasta = docs_colaborador(nome_empresa, nome_colab)
        for ext in ("jpg", "jpeg", "png"):
            p = pasta / f"foto_facial.{ext}"
            if p.exists():
                return p
    except Exception:
        pass
    return None


def _save_foto_path(nome_empresa: str, nome_colab: str) -> Path:
    try:
        from app.core.settings import docs_colaborador
        pasta = docs_colaborador(nome_empresa, nome_colab)
        pasta.mkdir(parents=True, exist_ok=True)
        return pasta / "foto_facial.jpg"
    except Exception:
        pasta = Path("fotos_faciais") / nome_empresa / nome_colab
        pasta.mkdir(parents=True, exist_ok=True)
        return pasta / "foto_facial.jpg"


# ─────────────────────────────────────────────────────────────────────────────
# Thread de captura
# ─────────────────────────────────────────────────────────────────────────────

class _CameraWorker(QObject):
    frame_ready = Signal(QImage)
    error       = Signal(str)

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self._camera_index = camera_index
        self._running      = False
        self._cap: Optional[cv2.VideoCapture] = None

    def start_capture(self):
        self._running = True
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            self.error.emit(f"Camera {self._camera_index} nao encontrada.")
            self._running = False
            return
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch  = frame_rgb.shape
            img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(img.copy())
        if self._cap:
            self._cap.release()

    def stop(self):
        self._running = False

    def capture_frame(self) -> Optional[QImage]:
        if self._cap and self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch  = frame_rgb.shape
                return QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Modal de captura com deteccao de rosto
# ─────────────────────────────────────────────────────────────────────────────

class CameraDialog(QDialog):
    foto_capturada = Signal(QPixmap)

    _TOL_CENTRO = 0.28

    def __init__(self, nome_empresa: str = "", nome_colab: str = "", parent=None):
        super().__init__(parent)
        self._nome_empresa = nome_empresa
        self._nome_colab   = nome_colab
        self._worker: Optional[_CameraWorker] = None
        self._thread: Optional[QThread]       = None
        self._foto_capturada: Optional[QImage] = None
        self._modo_preview  = False
        self._rosto_ok      = False
        self._cor_circulo   = _CIRCULO_AGUARDANDO

        self.setWindowTitle("Cadastrar Foto Facial")
        self.setModal(True)
        self.setFixedSize(740, 600)
        self.setStyleSheet("background: #0F172A;")
        self._setup_ui()
        self._listar_cameras()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(54)
        toolbar.setStyleSheet("background: #020817; border: none;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(20, 0, 16, 0)
        tl.setSpacing(10)

        ic_cam = QLabel()
        if _HAS_QTA:
            ic_cam.setPixmap(qta.icon("fa5s.camera", color=_AZUL_COR).pixmap(18, 18))
        ic_cam.setStyleSheet("background: transparent; border: none;")
        tl.addWidget(ic_cam)

        vl_titulo = QVBoxLayout()
        vl_titulo.setSpacing(1)
        lbl_t = QLabel("Cadastro de Foto Facial")
        lbl_t.setStyleSheet(
            "color: #E2E8F0; font-size: 14px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        lbl_s = QLabel("Posicione o rosto dentro do circulo guia")
        lbl_s.setStyleSheet(
            f"color: {_CINZA_COR}; font-size: 11px; background: transparent; border: none;"
        )
        vl_titulo.addWidget(lbl_t)
        vl_titulo.addWidget(lbl_s)
        tl.addLayout(vl_titulo)
        tl.addStretch()

        lbl_cam = QLabel("Camera:")
        lbl_cam.setStyleSheet(
            f"color: {_CINZA_COR}; font-size: 12px; background: transparent; border: none;"
        )
        tl.addWidget(lbl_cam)

        self._combo_cam = QComboBox()
        self._combo_cam.setFixedSize(170, 30)
        self._combo_cam.setStyleSheet("""
            QComboBox {
                background: #1E293B; color: #CBD5E1;
                border: 1px solid #334155; border-radius: 5px;
                padding: 0 8px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1E293B; color: #CBD5E1;
                border: 1px solid #334155;
                selection-background-color: #334155;
            }
        """)
        self._combo_cam.currentIndexChanged.connect(self._on_camera_changed)
        tl.addWidget(self._combo_cam)

        btn_fechar = QPushButton()
        btn_fechar.setFixedSize(32, 32)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        if _HAS_QTA:
            btn_fechar.setIcon(qta.icon("fa5s.times", color="#94A3B8"))
            btn_fechar.setIconSize(QSize(12, 12))
        btn_fechar.setStyleSheet("""
            QPushButton {
                background: #1E293B; border: 1px solid #334155; border-radius: 6px;
            }
            QPushButton:hover { background: #DC2626; border-color: #DC2626; }
        """)
        btn_fechar.clicked.connect(self._fechar)
        tl.addWidget(btn_fechar)
        root.addWidget(toolbar)

        # Area de video
        self._lbl_video = QLabel()
        self._lbl_video.setAlignment(Qt.AlignCenter)
        self._lbl_video.setMinimumSize(640, 440)
        self._lbl_video.setStyleSheet(
            "color: #475569; background: #020817; border: none; font-size: 14px;"
        )
        self._lbl_video.setText("Iniciando camera...")
        root.addWidget(self._lbl_video, 1)

        # Barra de status
        self._lbl_guia = QLabel("Aguardando rosto...")
        self._lbl_guia.setAlignment(Qt.AlignCenter)
        self._lbl_guia.setFixedHeight(32)
        self._lbl_guia.setStyleSheet(
            f"background: rgba(15,23,42,0.90); color: {_CINZA_COR}; "
            "font-size: 12px; font-weight: bold; border: none;"
        )
        root.addWidget(self._lbl_guia)

        # Botoes
        btn_bar = QFrame()
        btn_bar.setFixedHeight(72)
        btn_bar.setStyleSheet("background: #0F172A; border: none;")
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(24, 12, 24, 12)
        bl.setSpacing(12)

        self._btn_capturar  = self._btn_acao("fa5s.camera", "  Capturar",  _AZUL_COR,  "#1D4ED8", ativo=False)
        self._btn_repetir   = self._btn_acao("fa5s.redo",   "  Repetir",   "#475569",  "#334155", ativo=False)
        self._btn_confirmar = self._btn_acao("fa5s.check",  "  Confirmar", _VERDE_COR, "#15803D", ativo=False)
        self._btn_cancelar  = self._btn_acao("fa5s.times",  "  Cancelar",  _VERM_COR,  "#B91C1C", ativo=True)

        self._btn_capturar.clicked.connect(self._on_capturar)
        self._btn_repetir.clicked.connect(self._on_repetir)
        self._btn_confirmar.clicked.connect(self._on_confirmar)
        self._btn_cancelar.clicked.connect(self._fechar)

        bl.addWidget(self._btn_capturar)
        bl.addWidget(self._btn_repetir)
        bl.addWidget(self._btn_confirmar)
        bl.addStretch()
        bl.addWidget(self._btn_cancelar)
        root.addWidget(btn_bar)

    @staticmethod
    def _btn_acao(fa_icon: str, texto: str, bg: str, hover: str, ativo: bool) -> QPushButton:
        b = QPushButton(texto)
        b.setFixedHeight(44)
        b.setMinimumWidth(130)
        b.setCursor(Qt.PointingHandCursor)
        b.setEnabled(ativo)
        if _HAS_QTA:
            b.setIcon(qta.icon(fa_icon, color="white"))
            b.setIconSize(QSize(13, 13))
        b.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: white; border: none; border-radius: 8px;
                padding: 0 18px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:disabled {{
                background: #1E293B; color: #475569; border: 1px solid #334155;
            }}
        """)
        return b

    # Cameras
    def _listar_cameras(self):
        def _preencher():
            cams = []
            for i in range(6):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cams.append(i)
                    cap.release()
            self._combo_cam.blockSignals(True)
            self._combo_cam.clear()
            if cams:
                for idx in cams:
                    self._combo_cam.addItem(f"Camera {idx}", idx)
            else:
                self._combo_cam.addItem("Nenhuma camera detectada", -1)
            self._combo_cam.blockSignals(False)
            if cams:
                self._iniciar_camera(cams[0])
            else:
                self._lbl_video.setText("Nenhuma camera disponivel")
        QTimer.singleShot(150, _preencher)

    def _iniciar_camera(self, index: int):
        self._parar_camera()
        if index < 0:
            return
        self._thread = QThread()
        self._worker = _CameraWorker(index)
        self._worker.moveToThread(self._thread)
        self._worker.frame_ready.connect(self._on_frame)
        self._worker.error.connect(self._on_camera_error)
        self._thread.started.connect(self._worker.start_capture)
        self._thread.start()

    def _parar_camera(self):
        if self._worker:
            self._worker.stop()
            self._worker = None
        if self._thread:
            self._thread.quit()
            self._thread.wait(1500)
            self._thread = None

    def _on_camera_changed(self, _):
        if not self._modo_preview:
            idx = self._combo_cam.currentData()
            if idx is not None and idx >= 0:
                self._iniciar_camera(idx)

    def _on_camera_error(self, msg: str):
        self._lbl_video.setText(msg)
        self._lbl_video.setStyleSheet(
            f"color: {_VERM_COR}; background: #020817; border: none; font-size: 13px;"
        )

    # Frames + deteccao de rosto
    def _on_frame(self, img: QImage):
        if self._modo_preview:
            return

        img_mirror = img.mirrored(True, False)

        # Converte para numpy para deteccao
        w, h = img_mirror.width(), img_mirror.height()
        ptr  = img_mirror.bits()
        arr  = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 3)).copy()
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        rostos = _face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        lw = self._lbl_video.width()
        lh = self._lbl_video.height()
        scale = min(lw / w, lh / h)
        dw = int(w * scale)
        dh = int(h * scale)
        ox = (lw - dw) // 2
        oy = (lh - dh) // 2

        cx = lw // 2
        cy = lh // 2
        rw = int(dw * 0.32)
        rh = int(dh * 0.60)

        estado = "aguardando"
        if len(rostos) > 0:
            fx, fy, fw, fh = max(rostos, key=lambda r: r[2] * r[3])
            fcx = int((fx + fw / 2) * scale) + ox
            fcy = int((fy + fh / 2) * scale) + oy
            dx_norm = abs(fcx - cx) / rw
            dy_norm = abs(fcy - cy) / rh
            dentro  = (dx_norm ** 2 + dy_norm ** 2) <= 1.0
            central = dx_norm <= self._TOL_CENTRO and dy_norm <= self._TOL_CENTRO
            if dentro and central:
                estado = "ok"
            else:
                estado = "detectado"

        self._atualizar_estado(estado)

        pixmap = QPixmap.fromImage(img_mirror).scaled(
            lw, lh, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._desenhar_guia(pixmap, rostos, scale, ox, oy, estado)
        self._lbl_video.setPixmap(pixmap)
        self._lbl_video.setStyleSheet("background: #020817; border: none;")

    def _atualizar_estado(self, estado: str):
        if estado == "ok":
            self._rosto_ok    = True
            self._cor_circulo = _CIRCULO_OK
            self._btn_capturar.setEnabled(True)
            self._lbl_guia.setText("Rosto centralizado — clique em Capturar")
            self._lbl_guia.setStyleSheet(
                f"background: rgba(22,163,74,0.20); color: {_VERDE_COR}; "
                "font-size: 12px; font-weight: bold; border: none;"
            )
        elif estado == "detectado":
            self._rosto_ok    = False
            self._cor_circulo = _CIRCULO_DETECTADO
            self._btn_capturar.setEnabled(False)
            self._lbl_guia.setText("Rosto detectado — centralize dentro do circulo")
            self._lbl_guia.setStyleSheet(
                f"background: rgba(217,119,6,0.15); color: {_AMAR_COR}; "
                "font-size: 12px; font-weight: bold; border: none;"
            )
        else:
            self._rosto_ok    = False
            self._cor_circulo = _CIRCULO_AGUARDANDO
            self._btn_capturar.setEnabled(False)
            self._lbl_guia.setText("Aguardando rosto — posicione-se em frente a camera")
            self._lbl_guia.setStyleSheet(
                f"background: rgba(15,23,42,0.90); color: {_CINZA_COR}; "
                "font-size: 12px; font-weight: bold; border: none;"
            )

    def _desenhar_guia(self, pixmap, rostos, scale, ox, oy, estado):
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        lw = pixmap.width()
        lh = pixmap.height()
        cx = lw // 2
        cy = lh // 2
        rw = int(lw * 0.32)
        rh = int(lh * 0.60)

        # Sombra fora do circulo
        sombra = QPainterPath()
        sombra.addRect(0, 0, lw, lh)
        elipse = QPainterPath()
        elipse.addEllipse(cx - rw, cy - rh, rw * 2, rh * 2)
        painter.fillPath(sombra.subtracted(elipse), QColor(0, 0, 0, 110))

        # Circulo guia principal
        cor = QColor(self._cor_circulo)
        pen = QPen(cor)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(cx - rw, cy - rh, rw * 2, rh * 2)

        # Arcos de canto decorativos
        pen2 = QPen(cor)
        pen2.setWidth(5)
        painter.setPen(pen2)
        for angulo in (0, 90, 180, 270):
            painter.drawArc(cx - rw, cy - rh, rw * 2, rh * 2, angulo * 16, 30 * 16)

        # Retangulo ao redor do rosto detectado
        if len(rostos) > 0 and estado in ("detectado", "ok"):
            fx, fy, fw, fh = max(rostos, key=lambda r: r[2] * r[3])
            rx  = int(fx * scale) + ox
            ry  = int(fy * scale) + oy
            rfw = int(fw * scale)
            rfh = int(fh * scale)
            pen_r = QPen(QColor(cor))
            pen_r.setWidth(2)
            pen_r.setStyle(Qt.DotLine)
            painter.setPen(pen_r)
            painter.drawRect(rx, ry, rfw, rfh)

        painter.end()

    # Acoes
    def _on_capturar(self):
        if not self._worker or not self._rosto_ok:
            return
        img = self._worker.capture_frame()
        if img is None:
            QMessageBox.warning(self, "Erro", "Nao foi possivel capturar o frame.")
            return
        img = img.mirrored(True, False)
        self._foto_capturada = img
        self._modo_preview   = True
        pixmap = QPixmap.fromImage(img).scaled(
            self._lbl_video.width(), self._lbl_video.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._lbl_video.setPixmap(pixmap)
        self._lbl_guia.setText("Foto capturada — confirme ou repita")
        self._lbl_guia.setStyleSheet(
            f"background: rgba(22,163,74,0.25); color: {_VERDE_COR}; "
            "font-size: 12px; font-weight: bold; border: none;"
        )
        self._btn_capturar.setEnabled(False)
        self._btn_repetir.setEnabled(True)
        self._btn_confirmar.setEnabled(True)

    def _on_repetir(self):
        self._modo_preview   = False
        self._foto_capturada = None
        self._rosto_ok       = False
        self._cor_circulo    = _CIRCULO_AGUARDANDO
        self._btn_capturar.setEnabled(False)
        self._btn_repetir.setEnabled(False)
        self._btn_confirmar.setEnabled(False)
        self._lbl_guia.setText("Aguardando rosto — posicione-se em frente a camera")
        self._lbl_guia.setStyleSheet(
            f"background: rgba(15,23,42,0.90); color: {_CINZA_COR}; "
            "font-size: 12px; font-weight: bold; border: none;"
        )

    def _on_confirmar(self):
        if self._foto_capturada is None:
            return
        pixmap = QPixmap.fromImage(self._foto_capturada)
        try:
            destino = _save_foto_path(self._nome_empresa, self._nome_colab)
            img_np  = self._foto_capturada.convertToFormat(QImage.Format_RGB888)
            ptr     = img_np.bits()
            arr     = np.frombuffer(ptr, dtype=np.uint8).reshape(
                (img_np.height(), img_np.width(), 3)
            ).copy()
            arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(destino), arr_bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])
        except Exception as e:
            QMessageBox.warning(self, "Aviso",
                f"Foto capturada, mas nao foi possivel salvar em disco:\n{e}")
        self.foto_capturada.emit(pixmap)
        self._fechar()

    def _fechar(self):
        self._parar_camera()
        self.reject()

    def closeEvent(self, event):
        self._parar_camera()
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# Widget inline
# ─────────────────────────────────────────────────────────────────────────────

class FotoFacialWidget(QFrame):
    foto_alterada = Signal(QPixmap)
    _THUMB_SIZE = 120

    def __init__(self, nome_empresa: str = "", nome_colab: str = "", parent=None):
        super().__init__(parent)
        self._nome_empresa = nome_empresa
        self._nome_colab   = nome_colab
        self._foto_pixmap: Optional[QPixmap] = None
        self.setFixedSize(160, 210)
        self.setStyleSheet(f"""
            QFrame {{
                background: {_CARD_BG};
                border: 1px solid {_CARD_BORDA};
                border-radius: 12px;
            }}
        """)
        self._setup_ui()
        if nome_empresa and nome_colab:
            self._carregar_foto_existente()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignHCenter)

        self._lbl_foto = QLabel()
        self._lbl_foto.setFixedSize(self._THUMB_SIZE, self._THUMB_SIZE)
        self._lbl_foto.setAlignment(Qt.AlignCenter)
        self._mostrar_placeholder()
        layout.addWidget(self._lbl_foto, alignment=Qt.AlignHCenter)

        lbl_titulo = QLabel("Foto Facial")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet(
            f"color: {_TITULO}; font-size: 11px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        layout.addWidget(lbl_titulo)

        self._btn_camera  = self._mini_btn("fa5s.camera",     "Abrir camera",    _AZUL_BG, _AZUL_COR, _AZUL_BORDA)
        self._btn_arquivo = self._mini_btn("fa5s.folder-open","Importar arquivo", _BG,      _SUBTITULO, _CARD_BORDA)
        self._btn_remover = self._mini_btn("fa5s.trash-alt",  "Remover foto",     _VERM_BG, _VERM_COR,  _VERM_BORDA)
        self._btn_remover.setVisible(False)

        self._btn_camera.clicked.connect(self._on_camera)
        self._btn_arquivo.clicked.connect(self._on_importar)
        self._btn_remover.clicked.connect(self._on_remover)

        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(self._btn_camera)
        row.addWidget(self._btn_arquivo)
        layout.addLayout(row)
        layout.addWidget(self._btn_remover)

    @staticmethod
    def _mini_btn(fa_icone: str, tooltip: str, bg: str, cor: str, borda: str) -> QPushButton:
        b = QPushButton()
        b.setFixedSize(58, 30)
        b.setToolTip(tooltip)
        b.setCursor(Qt.PointingHandCursor)
        if _HAS_QTA:
            b.setIcon(qta.icon(fa_icone, color=cor))
            b.setIconSize(QSize(13, 13))
        b.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 1px solid {borda};
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: {borda}; }}
        """)
        return b

    def _mostrar_placeholder(self):
        size = self._THUMB_SIZE
        if _HAS_QTA:
            px = qta.icon("fa5s.user-circle", color=_CINZA_COR).pixmap(60, 60)
        else:
            px = QPixmap(60, 60)
            px.fill(Qt.transparent)
        self._lbl_foto.setPixmap(px)
        self._lbl_foto.setStyleSheet(f"""
            QLabel {{
                background: {_BG};
                border: 2px dashed {_CARD_BORDA};
                border-radius: {size // 2}px;
            }}
        """)

    def _mostrar_foto(self, pixmap: QPixmap):
        size = self._THUMB_SIZE
        thumb = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        result = QPixmap(size, size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        ox = (thumb.width()  - size) // 2
        oy = (thumb.height() - size) // 2
        painter.drawPixmap(-ox, -oy, thumb)
        painter.end()
        self._lbl_foto.setPixmap(result)
        self._lbl_foto.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: 2px solid {_VERDE_BORDA};
                border-radius: {size // 2}px;
            }}
        """)
        self._btn_remover.setVisible(True)

    def _carregar_foto_existente(self):
        if not self._nome_empresa or not self._nome_colab:
            return
        path = _get_foto_path(self._nome_empresa, self._nome_colab)
        if path:
            px = QPixmap(str(path))
            if not px.isNull():
                self._foto_pixmap = px
                self._mostrar_foto(px)

    def _on_camera(self):
        dlg = CameraDialog(
            nome_empresa=self._nome_empresa,
            nome_colab=self._nome_colab,
            parent=self,
        )
        dlg.foto_capturada.connect(self._on_foto_recebida)
        dlg.exec()

    def _on_importar(self):
        from PySide6.QtWidgets import QFileDialog
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar foto", "", "Imagens (*.jpg *.jpeg *.png *.bmp)"
        )
        if not caminho:
            return
        px = QPixmap(caminho)
        if px.isNull():
            QMessageBox.warning(self, "Erro", "Nao foi possivel carregar a imagem.")
            return
        try:
            destino = _save_foto_path(self._nome_empresa, self._nome_colab)
            shutil.copy2(caminho, str(destino))
        except Exception:
            pass
        self._on_foto_recebida(px)

    def _on_remover(self):
        self._foto_pixmap = None
        self._mostrar_placeholder()
        self._btn_remover.setVisible(False)
        try:
            path = _get_foto_path(self._nome_empresa, self._nome_colab)
            if path and path.exists():
                path.unlink()
        except Exception:
            pass
        self.foto_alterada.emit(QPixmap())

    def _on_foto_recebida(self, pixmap: QPixmap):
        self._foto_pixmap = pixmap
        self._mostrar_foto(pixmap)
        self.foto_alterada.emit(pixmap)

    def atualizar_contexto(self, nome_empresa: str, nome_colab: str):
        changed = nome_empresa != self._nome_empresa or nome_colab != self._nome_colab
        self._nome_empresa = nome_empresa
        self._nome_colab   = nome_colab
        if changed and nome_empresa and nome_colab:
            self._carregar_foto_existente()

    @property
    def foto_pixmap(self) -> Optional[QPixmap]:
        return self._foto_pixmap

    @property
    def caminho_foto(self) -> Optional[Path]:
        return _get_foto_path(self._nome_empresa, self._nome_colab)