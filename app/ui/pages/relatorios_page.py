"""
relatorios_page.py
─────────────────────────────────────────────────────────────────────────────
Tela de Relatórios do ThirdSys.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
import subprocess
import sys
import traceback
from collections import defaultdict
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QSize, QTimer, QDate, Signal
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QPen, QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDateEdit,
    QDialog, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QMessageBox, QPushButton, QScrollArea,
    QSizePolicy, QStackedWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

# ─────────────────────────────────────────────────────────────────────────────
# Paleta
# ─────────────────────────────────────────────────────────────────────────────
_BG      = "#F2F5F8"
_CARD    = "#FFFFFF"
_BORDA   = "#DDE3EA"
_TITULO  = "#1C2B3A"
_SUB     = "#5A7A96"
_LABEL   = "#8AA5BC"
_TEXTO   = "#374151"
_AZUL    = "#2563EB"
_AZUL_BG = "#EFF6FF"
_VERDE   = "#16A34A"
_VERDE_BG= "#F0FAF4"
_VERDE_BD= "#86EFAC"
_VERM    = "#991B1B"
_VERM_BG = "#FEF2F2"
_VERM_BD = "#FCA5A5"
_AMAR    = "#92400E"
_AMAR_BG = "#FFFBEB"
_AMAR_BD = "#FCD34D"

_GRAF_CORES = [
    "#2563EB", "#16A34A", "#D97706", "#DC2626",
    "#7C3AED", "#0891B2", "#BE185D", "#65A30D",
]

_LOGO_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "assets", "logo.png"
))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers visuais
# ─────────────────────────────────────────────────────────────────────────────

def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {_BORDA}; border: none;")
    return f


def _card(radius: int = 10) -> QFrame:
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: {_CARD};
            border: 1px solid {_BORDA};
            border-radius: {radius}px;
        }}
        QLabel {{ border: none; background: transparent; }}
        QWidget {{ border: none; }}
    """)
    return f


def _btn(texto: str, icone: str, bg: str, hover: str,
         cor_txt: str = "white", altura: int = 38) -> QPushButton:
    b = QPushButton(texto)
    b.setIcon(qta.icon(icone, color=cor_txt))
    b.setIconSize(QSize(13, 13))
    b.setFixedHeight(altura)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {cor_txt}; border: none;
            border-radius: 7px; padding: 0 16px;
            font-size: 12px; font-weight: bold;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ background: {_BORDA}; color: {_LABEL}; }}
    """)
    return b


def _estilo_date() -> str:
    return f"""
        QDateEdit {{
            background: {_CARD}; color: {_TITULO};
            border: 1.5px solid #CBD5E1; border-radius: 7px;
            padding: 4px 10px; font-size: 12px;
        }}
        QDateEdit:focus {{ border-color: {_AZUL}; background: {_AZUL_BG}; }}
    """


def _estilo_combo() -> str:
    return f"""
        QComboBox {{
            background: {_CARD}; color: {_TITULO};
            border: 1.5px solid #CBD5E1; border-radius: 7px;
            padding: 4px 10px; font-size: 12px;
        }}
        QComboBox:focus {{ border-color: {_AZUL}; }}
        QComboBox::drop-down {{ border: none; width: 20px; }}
        QComboBox QAbstractItemView {{
            background: {_CARD}; color: {_TITULO};
            border: 1px solid {_BORDA}; selection-background-color: {_AZUL_BG};
        }}
    """


def _estilo_tabela() -> str:
    return f"""
        QTableWidget {{
            background: {_CARD}; border: none;
            gridline-color: {_BORDA}; font-size: 12px; color: {_TEXTO};
            outline: none;
        }}
        QTableWidget::item {{ padding: 8px 12px; border-bottom: 1px solid {_BORDA}; }}
        QTableWidget::item:selected {{ background: {_AZUL_BG}; color: {_TITULO}; }}
        QHeaderView::section {{
            background: #F4F7FA; color: {_LABEL};
            border: none; border-bottom: 2px solid {_BORDA};
            padding: 8px 12px; font-size: 11px; font-weight: bold;
        }}
    """
def _pasta_downloads() -> Path:
    """Retorna a pasta Downloads do usuário em qualquer SO."""
    if sys.platform == "win32":
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x001A, None, 0, buf)
        # 0x001A = CSIDL_PERSONAL → Documents; use CSIDL_DOWNLOADS se disponível
        # Mais confiável via env:
        return Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads"
    else:
        return Path.home() / "Downloads"
    

def _nome_relatorio(tipo: str) -> str:
    """Ex: relatorio_bloqueios_19-39.pdf"""
    agora = datetime.now().strftime("%d-%m-%Y_%H-%M")
    return f"relatorio_{tipo}_{agora}.pdf"

# ─────────────────────────────────────────────────────────────────────────────
# Gráfico de barras
# ─────────────────────────────────────────────────────────────────────────────

class GraficoBarras(QWidget):
    def __init__(self, dados: list, titulo: str = "", cor: str = _AZUL, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._titulo = titulo
        self._cor = cor
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def atualizar(self, dados: list, titulo: str = ""):
        self._dados = dados
        if titulo:
            self._titulo = titulo
        self.update()

    def paintEvent(self, _):
        if not self._dados:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        try:
            W, H = self.width(), self.height()
            PAD_L, PAD_R, PAD_T, PAD_B = 48, 16, 30, 44
            area_w = W - PAD_L - PAD_R
            area_h = H - PAD_T - PAD_B

            valores = [max(v, 0) for _, v in self._dados]
            max_v   = max(valores) if valores else 1
            if max_v == 0:
                max_v = 1

            p.fillRect(0, 0, W, H, QColor(_CARD))

            if self._titulo:
                p.setPen(QColor("#000000"))
                p.setFont(QFont("Segoe UI", 10, QFont.Bold))
                p.drawText(PAD_L, 18, self._titulo)

            p.setPen(QPen(QColor(_BORDA), 1, Qt.DashLine))
            grades = 4
            for i in range(grades + 1):
                y = PAD_T + area_h - int(area_h * i / grades)
                p.drawLine(PAD_L, y, PAD_L + area_w, y)
                val_label = int(max_v * i / grades)
                p.setPen(QColor(_LABEL))
                p.setFont(QFont("Segoe UI", 8))
                p.drawText(2, y + 4, str(val_label))
                p.setPen(QPen(QColor(_BORDA), 1, Qt.DashLine))

            n = len(self._dados)
            if n == 0:
                return

            gap   = max(4, int(area_w * 0.08 / (n + 1)))
            bar_w = max(8, int((area_w - gap * (n + 1)) / n))

            for i, (rotulo, valor) in enumerate(self._dados):
                x  = PAD_L + gap + i * (bar_w + gap)
                bh = int(area_h * valor / max_v) if max_v else 0
                y  = PAD_T + area_h - bh

                path = QPainterPath()
                r = min(4, bar_w // 2)
                path.moveTo(x, PAD_T + area_h)
                path.lineTo(x, y + r)
                path.quadTo(x, y, x + r, y)
                path.lineTo(x + bar_w - r, y)
                path.quadTo(x + bar_w, y, x + bar_w, y + r)
                path.lineTo(x + bar_w, PAD_T + area_h)
                path.closeSubpath()

                cor = QColor(self._cor)
                cor.setAlpha(220)
                p.fillPath(path, cor)

                p.setPen(QColor(_TITULO))
                p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                p.drawText(x, y - 14, bar_w, 14, Qt.AlignCenter, str(valor))

                p.setPen(QColor(_SUB))
                p.setFont(QFont("Segoe UI", 8))
                rotulo_curto = rotulo[:10] + "…" if len(rotulo) > 10 else rotulo
                p.drawText(x - gap, PAD_T + area_h + 6, bar_w + gap * 2, 32,
                           Qt.AlignCenter | Qt.TextWordWrap, rotulo_curto)

        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico de pizza
# ─────────────────────────────────────────────────────────────────────────────

class GraficoPizza(QWidget):
    def __init__(self, dados: list, titulo: str = "", parent=None):
        super().__init__(parent)
        self._dados = dados
        self._titulo = titulo
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def atualizar(self, dados: list, titulo: str = ""):
        self._dados = dados
        if titulo:
            self._titulo = titulo
        self.update()

    def paintEvent(self, _):
        if not self._dados:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        try:
            W, H = self.width(), self.height()
            p.fillRect(0, 0, W, H, QColor(_CARD))

            if self._titulo:
                p.setPen(QColor(_TITULO))
                p.setFont(QFont("Segoe UI", 10, QFont.Bold))
                p.drawText(16, 18, self._titulo)

            total = sum(v for _, v in self._dados)
            if total == 0:
                return

            pizza_sz = min(H - 50, W // 2 - 20)
            cx = 16 + pizza_sz // 2
            cy = 28 + (H - 50) // 2
            r  = pizza_sz // 2

            angulo = 0.0
            for i, (rotulo, valor) in enumerate(self._dados):
                span = 360 * 16 * valor / total
                cor  = QColor(_GRAF_CORES[i % len(_GRAF_CORES)])
                p.setBrush(cor)
                p.setPen(QPen(QColor(_CARD), 2))
                p.drawPie(cx - r, cy - r, pizza_sz, pizza_sz,
                          int(angulo), int(span))
                angulo += span

            leg_x = cx + r + 20
            leg_y = cy - r
            p.setFont(QFont("Segoe UI", 9))
            for i, (rotulo, valor) in enumerate(self._dados):
                cor = QColor(_GRAF_CORES[i % len(_GRAF_CORES)])
                p.setBrush(cor)
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(leg_x, leg_y + i * 22, 12, 12, 3, 3)
                p.setPen(QColor(_TITULO))
                pct = f"{100 * valor / total:.0f}%"
                p.drawText(leg_x + 18, leg_y + i * 22 + 10,
                           f"{rotulo[:22]} — {valor} ({pct})")

        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Card KPI
# ─────────────────────────────────────────────────────────────────────────────

class CardKPI(QFrame):
    def __init__(self, icone: str, cor: str, titulo: str, valor: str = "—", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {_CARD}; border: 1px solid {_BORDA};
                border-top: 3px solid {cor}; border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)

        topo = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(icone, color=cor).pixmap(14, 14))
        ic.setStyleSheet("background: transparent; border: none;")
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet(
            f"font-size: 10px; color: {_LABEL}; font-weight: bold; "
            "background: transparent; border: none;"
        )
        topo.addWidget(ic)
        topo.addWidget(lbl_t)
        topo.addStretch()
        lay.addLayout(topo)

        self._lbl_valor = QLabel(valor)
        self._lbl_valor.setStyleSheet(
            f"font-size: 26px; font-weight: bold; color: {cor}; "
            "background: transparent; border: none;"
        )
        lay.addWidget(self._lbl_valor)

    def set_valor(self, v: str):
        self._lbl_valor.setText(v)


# ─────────────────────────────────────────────────────────────────────────────
# Gerador de PDF
# ─────────────────────────────────────────────────────────────────────────────

class GeradorPDF:
    """Gera PDFs corporativos com reportlab."""

    _AZUL_RL   = (0.145, 0.388, 0.922)
    _VERM_RL   = (0.600, 0.106, 0.106)
    _VERDE_RL  = (0.086, 0.639, 0.290)
    _CINZA_RL  = (0.353, 0.474, 0.588)
    _TITULO_RL = (0.110, 0.169, 0.227)

    @staticmethod
    def _cabecalho(canvas, doc, titulo_relatorio: str, periodo: str):
        from reportlab.lib.pagesizes import A4
        w, h = A4
        c = canvas

        c.setFillColorRGB(*GeradorPDF._AZUL_RL)
        c.rect(0, h - 56, w, 56, fill=1, stroke=0)

        logo_w = 120
        logo_h = 44
        if os.path.exists(_LOGO_PATH):
            c.drawImage(_LOGO_PATH,
                        x=(w / 2) - (logo_w / 2),
                        y=h - 54,
                        width=logo_w, height=logo_h,
                        mask="auto")
        else:
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(28, h - 34, "Terceiros")
            c.setFont("Helvetica", 11)
            c.drawString(28, h - 50, "Gestao de Terceiros e Seguranca")

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 13)
        c.drawRightString(w - 28, h - 32, titulo_relatorio)
        c.setFont("Helvetica", 9)
        c.drawRightString(w - 28, h - 46, periodo)

        c.setStrokeColorRGB(*GeradorPDF._CINZA_RL)
        c.setLineWidth(0.5)
        c.line(28, h - 64, w - 28, h - 64)

    @staticmethod
    def _rodape(canvas, doc):
        from reportlab.lib.pagesizes import A4
        w, h = A4
        c = canvas
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.5)
        c.line(28, 36, w - 28, 36)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.setFont("Helvetica", 8)
        c.drawString(28, 22, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawCentredString(w / 2, 22, "Santiago Diaz - Desenvolvedor de Software | TST")
        c.drawRightString(w - 28, 22, f"Pagina {doc.page}")

    @classmethod
    def movimentacao(cls, dados: dict, caminho: str):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics.charts.barcharts import VerticalBarChart

        W_PAGE, _ = A4
        doc = SimpleDocTemplate(
            caminho, pagesize=A4,
            leftMargin=28, rightMargin=28,
            topMargin=72, bottomMargin=56,
        )

        def _on_page(canvas, doc):
            cls._cabecalho(canvas, doc, "Relatorio de Movimentacao", dados["periodo"])
            cls._rodape(canvas, doc)

        story = []
        az  = colors.HexColor("#2563EB")
        vd  = colors.HexColor("#16A34A")
        cin = colors.HexColor("#5A7A96")
        tit = colors.HexColor("#1C2B3A")
        d_w = W_PAGE - 56

        st_sec = ParagraphStyle("sec", fontName="Helvetica-Bold",
                                fontSize=9, textColor=cin, spaceBefore=14, spaceAfter=4)

        kpi_tbl = Table(
            [["Total de Entradas", "Total de Saidas", "Dias no periodo"],
             [str(dados["total_entradas"]), str(dados["total_saidas"]), str(len(dados["por_dia"]))]],
            colWidths=[d_w / 3] * 3
        )
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
            ("BACKGROUND",    (0, 1), (-1, 1), colors.white),
            ("TEXTCOLOR",     (0, 0), (-1, 0), cin),
            ("TEXTCOLOR",     (0, 1), (-1, 1), az),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8),
            ("FONTSIZE",      (0, 1), (-1, 1), 22),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0, 0), (-1, 0), [colors.HexColor("#F4F7FA")]),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("TOPPADDING",    (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING",    (0, 1), (-1, 1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 20),
        ]))
        story.append(kpi_tbl)
        story.append(Spacer(1, 14))

        if dados["por_dia"]:
            story.append(Paragraph("Movimentacao por dia", st_sec))
            dias = [d[0] for d in dados["por_dia"]]
            entr = [d[1] for d in dados["por_dia"]]
            sai  = [d[2] for d in dados["por_dia"]]
            drw = Drawing(d_w, 140)
            bc  = VerticalBarChart()
            bc.x, bc.y = 40, 20
            bc.width  = d_w - 60
            bc.height = 100
            bc.data   = [entr, sai]
            bc.categoryAxis.categoryNames = [d[-5:] for d in dias]
            bc.categoryAxis.labels.fontSize = 7
            bc.categoryAxis.labels.angle    = 30 if len(dias) > 7 else 0
            bc.valueAxis.labels.fontSize    = 7
            bc.bars[0].fillColor = az
            bc.bars[1].fillColor = vd
            bc.groupSpacing = 4
            bc.barSpacing   = 2
            drw.add(Rect(42, 128, 10, 8, fillColor=az, strokeColor=None))
            drw.add(String(56, 129, "Entradas", fontSize=7, fillColor=tit))
            drw.add(Rect(102, 128, 10, 8, fillColor=vd, strokeColor=None))
            drw.add(String(116, 129, "Saidas", fontSize=7, fillColor=tit))
            drw.add(bc)
            story.append(drw)
            story.append(Spacer(1, 8))

        if dados["por_empresa"]:
            story.append(Paragraph("Movimentacao por empresa", st_sec))
            rows = [["Empresa", "Total de acessos", "% do total"]]
            total_geral = sum(v for _, v in dados["por_empresa"]) or 1
            for emp, tot in sorted(dados["por_empresa"], key=lambda x: -x[1]):
                rows.append([emp, str(tot), f"{100 * tot / total_geral:.1f}%"])
            emp_tbl = Table(rows, colWidths=[d_w * 0.6, d_w * 0.2, d_w * 0.2])
            emp_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(emp_tbl)
            story.append(Spacer(1, 14))

        if dados["detalhe"]:
            story.append(Paragraph("Registro detalhado de acessos", st_sec))
            rows = [["Colaborador", "Empresa", "Tipo", "Horario", "Operacao"]]
            for nome, emp, tipo, hora, op in dados["detalhe"]:
                rows.append([nome, emp, tipo.capitalize(), hora, op])
            col_w = [d_w * 0.25, d_w * 0.25, d_w * 0.15, d_w * 0.20, d_w * 0.15]
            det_tbl = Table(rows, colWidths=col_w, repeatRows=1)
            det_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 8),
                ("ALIGN",       (2, 0), (-1, -1), "CENTER"),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(det_tbl)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)

    @classmethod
    def bloqueios(cls, dados: dict, caminho: str):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        )
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics.charts.piecharts import Pie

        W_PAGE, _ = A4
        doc = SimpleDocTemplate(
            caminho, pagesize=A4,
            leftMargin=28, rightMargin=28,
            topMargin=72, bottomMargin=56,
        )

        def _on_page(canvas, doc):
            cls._cabecalho(canvas, doc, "Relatorio de Bloqueios", dados["periodo"])
            cls._rodape(canvas, doc)

        story = []
        verm = colors.HexColor("#991B1B")
        cin  = colors.HexColor("#5A7A96")
        tit  = colors.HexColor("#1C2B3A")
        az   = colors.HexColor("#2563EB")
        graf_cores_rl = [colors.HexColor(c) for c in _GRAF_CORES]
        d_w = W_PAGE - 56

        st_sec = ParagraphStyle("sec", fontName="Helvetica-Bold",
                                fontSize=9, textColor=cin,
                                spaceBefore=14, spaceAfter=4)

        kpi_tbl = Table(
            [["Total de bloqueios", "Empresas afetadas", "Motivos distintos"],
             [str(dados["total_bloqueios"]), str(len(dados["por_empresa"])), str(len(dados["por_motivo"]))]],
            colWidths=[d_w / 3] * 3
        )
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
            ("BACKGROUND",    (0, 1), (-1, 1), colors.white),
            ("TEXTCOLOR",     (0, 0), (-1, 0), cin),
            ("TEXTCOLOR",     (0, 1), (-1, 1), verm),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8),
            ("FONTSIZE",      (0, 1), (-1, 1), 22),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0, 0), (-1, 0), [colors.HexColor("#F4F7FA")]),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("TOPPADDING",    (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING",    (0, 1), (-1, 1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 20),
        ]))
        story.append(kpi_tbl)
        story.append(Spacer(1, 14))

        if dados["por_motivo"]:
            story.append(Paragraph("Bloqueios por motivo", st_sec))
            total_m = sum(v for _, v in dados["por_motivo"]) or 1
            drw = Drawing(d_w, 150)
            pie = Pie()
            pie.x, pie.y = 10, 10
            pie.width = pie.height = 120
            pie.data   = [v for _, v in dados["por_motivo"]]
            pie.labels = [f"{100*v/total_m:.0f}%" for _, v in dados["por_motivo"]]
            pie.sideLabels = 0
            pie.slices.strokeColor = colors.white
            pie.slices.strokeWidth = 1
            for i in range(len(dados["por_motivo"])):
                pie.slices[i].fillColor = graf_cores_rl[i % len(graf_cores_rl)]
            drw.add(pie)
            lx, ly = 145, 130
            for i, (motivo, val) in enumerate(dados["por_motivo"]):
                drw.add(Rect(lx, ly - i * 18, 10, 10,
                             fillColor=graf_cores_rl[i % len(graf_cores_rl)],
                             strokeColor=None))
                drw.add(String(lx + 14, ly - i * 18 + 2,
                               f"{motivo[:30]} — {val}",
                               fontSize=8, fillColor=tit))
            story.append(drw)
            story.append(Spacer(1, 8))

        if dados["por_empresa"]:
            story.append(Paragraph("Bloqueios por empresa", st_sec))
            rows = [["Empresa", "Qtd de bloqueios"]]
            for emp, qtd in sorted(dados["por_empresa"], key=lambda x: -x[1]):
                rows.append([emp, str(qtd)])
            emp_tbl = Table(rows, colWidths=[d_w * 0.75, d_w * 0.25])
            emp_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(emp_tbl)
            story.append(Spacer(1, 14))

        if dados["detalhe"]:
            story.append(Paragraph("Registro detalhado de bloqueios", st_sec))
            rows = [["Colaborador", "Empresa", "Motivos", "Horario", "Operador"]]
            for nome, emp, motivos, hora, op in dados["detalhe"]:
                rows.append([nome, emp, motivos, hora, op])
            cw = [d_w*0.22, d_w*0.22, d_w*0.28, d_w*0.16, d_w*0.12]
            det_tbl = Table(rows, colWidths=cw, repeatRows=1)
            det_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 8),
                ("ALIGN",       (3, 0), (-1, -1), "CENTER"),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#FFF8F8")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(det_tbl)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)


# ─────────────────────────────────────────────────────────────────────────────
# Aba Movimentação
# ─────────────────────────────────────────────────────────────────────────────

class AbaMovimentacao(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: dict = {}
        self._carregando = False
        self.setStyleSheet(f"background: {_BG}; border: none;")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        filtros = _card(8)
        fl = QHBoxLayout(filtros)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        fl.addWidget(QLabel("De:"))
        self._dt_ini = QDateEdit()
        self._dt_ini.setCalendarPopup(True)
        self._dt_ini.setButtonSymbols(QDateEdit.NoButtons)
        self._dt_ini.setDate(QDate.currentDate().addDays(-7))
        self._dt_ini.setMaximumDate(QDate.currentDate())  # ← sem datas futuras
        self._dt_ini.setStyleSheet(_estilo_date())
        self._dt_ini.setFixedHeight(34)
        fl.addWidget(self._dt_ini)

        fl.addWidget(QLabel("Ate:"))
        self._dt_fim = QDateEdit()
        self._dt_fim.setCalendarPopup(True)
        self._dt_fim.setButtonSymbols(QDateEdit.NoButtons)
        self._dt_fim.setDate(QDate.currentDate())
        self._dt_fim.setMaximumDate(QDate.currentDate())  # ← sem datas futuras
        self._dt_fim.setStyleSheet(_estilo_date())
        self._dt_fim.setFixedHeight(34)
        fl.addWidget(self._dt_fim)

        fl.addWidget(QLabel("Periodo rapido:"))
        self._combo_periodo = QComboBox()
        self._combo_periodo.addItems(["Personalizado", "Hoje", "Ultimos 7 dias",
                                      "Ultimos 30 dias", "Este mes"])
        self._combo_periodo.setStyleSheet(_estilo_combo())
        self._combo_periodo.setFixedHeight(34)
        self._combo_periodo.currentIndexChanged.connect(self._on_periodo_rapido)
        fl.addWidget(self._combo_periodo)

        fl.addStretch()

        self._btn_atualizar = _btn("  Atualizar", "fa5s.sync", _AZUL, "#1D4ED8")
        self._btn_atualizar.clicked.connect(self.carregar_dados)
        fl.addWidget(self._btn_atualizar)

        self._btn_pdf = _btn("  Exportar PDF", "fa5s.file-pdf", _VERM, "#7F1D1D")
        self._btn_pdf.clicked.connect(self._exportar_pdf)
        self._btn_pdf.setEnabled(False)
        fl.addWidget(self._btn_pdf)

        root.addWidget(filtros)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_entradas = CardKPI("fa5s.sign-in-alt",  _AZUL,  "Total de entradas")
        self._kpi_saidas   = CardKPI("fa5s.sign-out-alt", _VERDE, "Total de saidas")
        self._kpi_colab    = CardKPI("fa5s.users",        _AMAR,  "Colaboradores distintos")
        self._kpi_empresas = CardKPI("fa5s.building",     _VERM,  "Empresas distintas")
        for k in [self._kpi_entradas, self._kpi_saidas,
                  self._kpi_colab, self._kpi_empresas]:
            kpi_row.addWidget(k, 1)
        root.addLayout(kpi_row)

        graf_row = QHBoxLayout()
        graf_row.setSpacing(12)

        card_bar = _card(8)
        cb_lay = QVBoxLayout(card_bar)
        cb_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_barras = GraficoBarras([], "Entradas por dia", _AZUL)
        cb_lay.addWidget(self._graf_barras)
        graf_row.addWidget(card_bar, 3)

        card_pizza = _card(8)
        cp_lay = QVBoxLayout(card_pizza)
        cp_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_pizza = GraficoPizza([], "Acessos por empresa")
        cp_lay.addWidget(self._graf_pizza)
        graf_row.addWidget(card_pizza, 2)

        root.addLayout(graf_row)

        card_tbl = _card(8)
        tl = QVBoxLayout(card_tbl)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)

        header_tbl = QFrame()
        header_tbl.setStyleSheet(
            f"background: #F4F7FA; border-radius: 8px 8px 0 0; border-bottom: 1px solid {_BORDA};"
        )
        hl = QHBoxLayout(header_tbl)
        hl.setContentsMargins(16, 10, 16, 10)
        lbl_det = QLabel("Registro detalhado")
        lbl_det.setStyleSheet(
            f"font-weight: bold; font-size: 12px; color: {_TITULO}; "
            "background: transparent; border: none;"
        )
        hl.addWidget(lbl_det)
        hl.addStretch()
        tl.addWidget(header_tbl)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(5)
        self._tabela.setHorizontalHeaderLabels(
            ["Colaborador", "Empresa", "Tipo", "Horario", "Operador"]
        )
        self._tabela.setStyleSheet(_estilo_tabela())
        self._tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setShowGrid(False)
        self._tabela.setMinimumHeight(200)
        tl.addWidget(self._tabela)
        root.addWidget(card_tbl, 1)

    def _on_periodo_rapido(self, idx: int):
        hoje = QDate.currentDate()
        if idx == 0:
            return
        elif idx == 1:
            self._dt_ini.setDate(hoje)
            self._dt_fim.setDate(hoje)
        elif idx == 2:
            self._dt_ini.setDate(hoje.addDays(-7))
            self._dt_fim.setDate(hoje)
        elif idx == 3:
            self._dt_ini.setDate(hoje.addDays(-30))
            self._dt_fim.setDate(hoje)
        elif idx == 4:
            self._dt_ini.setDate(QDate(hoje.year(), hoje.month(), 1))
            self._dt_fim.setDate(hoje)
        self.carregar_dados()

    def carregar_dados(self):
        if self._carregando:
            return
        self._carregando = True
        self._btn_atualizar.setEnabled(False)
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from app.models.trabalhador import Trabalhador
            from sqlalchemy.orm import joinedload

            qdi = self._dt_ini.date()
            qdf = self._dt_fim.date()
            ini = datetime(qdi.year(), qdi.month(), qdi.day())
            fim = datetime(qdf.year(), qdf.month(), qdf.day(), 23, 59, 59)

            print(f"[MOV] Carregando: {ini} → {fim}")

            session = get_session()
            try:
                rows = (
                    session.query(Acesso, Trabalhador)
                    .join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                    .options(joinedload(Trabalhador.empresa))
                    .filter(Acesso.horario >= ini, Acesso.horario <= fim)
                    .order_by(Acesso.horario.desc())
                    .all()
                )
            finally:
                session.close()

            print(f"[MOV] {len(rows)} registros encontrados")

            total_e   = sum(1 for a, _ in rows if a.tipo == "entrada")
            total_s   = sum(1 for a, _ in rows if a.tipo == "saida")
            colab_set = {t.id for _, t in rows}
            emp_set   = {(t.empresa.razao_social if t.empresa else "—") for _, t in rows}

            por_dia_dict: dict = defaultdict(lambda: [0, 0])
            for a, _ in rows:
                d = a.horario.strftime("%d/%m")
                if a.tipo == "entrada":
                    por_dia_dict[d][0] += 1
                else:
                    por_dia_dict[d][1] += 1
            por_dia = sorted(
                [(d, v[0], v[1]) for d, v in por_dia_dict.items()],
                key=lambda x: x[0]
            )

            por_emp: dict = defaultdict(int)
            for _, t in rows:
                emp = t.empresa.razao_social if t.empresa else "Sem empresa"
                por_emp[emp] += 1
            por_empresa = sorted(por_emp.items(), key=lambda x: -x[1])

            detalhe = []
            for a, t in rows:
                emp  = t.empresa.razao_social if t.empresa else "—"
                hora = a.horario.strftime("%d/%m %H:%M") if a.horario else "—"
                op   = getattr(a, "operador", "portaria") or "portaria"
                detalhe.append((t.nome, emp, a.tipo, hora, op))

            self._dados = {
                "periodo":        f"{qdi.toString('dd/MM/yyyy')} a {qdf.toString('dd/MM/yyyy')}",
                "total_entradas": total_e,
                "total_saidas":   total_s,
                "por_dia":        por_dia,
                "por_empresa":    por_empresa,
                "detalhe":        detalhe,
            }

            self._kpi_entradas.set_valor(str(total_e))
            self._kpi_saidas.set_valor(str(total_s))
            self._kpi_colab.set_valor(str(len(colab_set)))
            self._kpi_empresas.set_valor(str(len(emp_set)))

            self._graf_barras.atualizar([(d, e) for d, e, _ in por_dia], "Entradas por dia")
            self._graf_pizza.atualizar([(e, v) for e, v in por_empresa[:8]], "Acessos por empresa")

            self._tabela.setRowCount(len(detalhe))
            for row, (nome, emp, tipo, hora, op) in enumerate(detalhe):
                cor_tipo = _AZUL_BG if tipo == "entrada" else _VERDE_BG
                for col, txt in enumerate([nome, emp, tipo.capitalize(), hora, op]):
                    it = QTableWidgetItem(txt)
                    it.setTextAlignment(
                        Qt.AlignCenter if col >= 2 else Qt.AlignLeft | Qt.AlignVCenter
                    )
                    if col == 2:
                        it.setBackground(QColor(cor_tipo))
                    self._tabela.setItem(row, col, it)

            self._btn_pdf.setEnabled(True)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao carregar", str(e))
        finally:
            self._carregando = False
            self._btn_atualizar.setEnabled(True)



    def _exportar_pdf(self):
        if not self._dados:
            return
        pasta   = _pasta_downloads()
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = str(pasta / _nome_relatorio("movimentacao"))
        try:
            GeradorPDF.movimentacao(self._dados, caminho)
            QMessageBox.information(
                self, "PDF gerado",
                f"Salvo em:\n{caminho}"
            )
            self._abrir_arquivo(caminho)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao gerar PDF", str(e))

    @staticmethod
    def _abrir_arquivo(caminho: str):
        try:
            if sys.platform == "win32":
                os.startfile(caminho)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", caminho])
            else:
                subprocess.Popen(["xdg-open", caminho])
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Aba Bloqueios
# ─────────────────────────────────────────────────────────────────────────────

class AbaBloqueios(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: dict = {}
        self._carregando = False
        self.setStyleSheet(f"background: {_BG}; border: none;")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        filtros = _card(8)
        fl = QHBoxLayout(filtros)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        fl.addWidget(QLabel("De:"))
        self._dt_ini = QDateEdit()
        self._dt_ini.setCalendarPopup(True)
        self._dt_ini.setButtonSymbols(QDateEdit.NoButtons)
        self._dt_ini.setDate(QDate.currentDate().addDays(-30))
        self._dt_ini.setMaximumDate(QDate.currentDate())  # ← sem datas futuras
        self._dt_ini.setStyleSheet(_estilo_date())
        self._dt_ini.setFixedHeight(34)
        fl.addWidget(self._dt_ini)

        fl.addWidget(QLabel("Ate:"))
        self._dt_fim = QDateEdit()
        self._dt_fim.setCalendarPopup(True)
        self._dt_fim.setButtonSymbols(QDateEdit.NoButtons)
        self._dt_fim.setDate(QDate.currentDate())
        self._dt_fim.setMaximumDate(QDate.currentDate())  # ← sem datas futuras
        self._dt_fim.setStyleSheet(_estilo_date())
        self._dt_fim.setFixedHeight(34)
        fl.addWidget(self._dt_fim)

        fl.addWidget(QLabel("Periodo rapido:"))
        self._combo_periodo = QComboBox()
        self._combo_periodo.addItems(["Personalizado", "Hoje", "Ultimos 7 dias",
                                      "Ultimos 30 dias", "Este mes"])
        self._combo_periodo.setCurrentIndex(3)
        self._combo_periodo.setStyleSheet(_estilo_combo())
        self._combo_periodo.setFixedHeight(34)
        self._combo_periodo.currentIndexChanged.connect(self._on_periodo_rapido)
        fl.addWidget(self._combo_periodo)

        fl.addStretch()

        self._btn_atualizar = _btn("  Atualizar", "fa5s.sync", _AZUL, "#1D4ED8")
        self._btn_atualizar.clicked.connect(self.carregar_dados)
        fl.addWidget(self._btn_atualizar)

        self._btn_pdf = _btn("  Exportar PDF", "fa5s.file-pdf", _VERM, "#7F1D1D")
        self._btn_pdf.clicked.connect(self._exportar_pdf)
        self._btn_pdf.setEnabled(False)
        fl.addWidget(self._btn_pdf)

        root.addWidget(filtros)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_total    = CardKPI("fa5s.ban",        _VERM,  "Total de bloqueios")
        self._kpi_empresas = CardKPI("fa5s.building",   _AMAR,  "Empresas afetadas")
        self._kpi_motivos  = CardKPI("fa5s.list-ul",    _AZUL,  "Motivos distintos")
        self._kpi_manual   = CardKPI("fa5s.hand-paper", _VERDE, "Bloqueios manuais")
        for k in [self._kpi_total, self._kpi_empresas,
                  self._kpi_motivos, self._kpi_manual]:
            kpi_row.addWidget(k, 1)
        root.addLayout(kpi_row)

        graf_row = QHBoxLayout()
        graf_row.setSpacing(12)

        card_pizza = _card(8)
        cp_lay = QVBoxLayout(card_pizza)
        cp_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_pizza = GraficoPizza([], "Bloqueios por motivo")
        cp_lay.addWidget(self._graf_pizza)
        graf_row.addWidget(card_pizza, 2)

        card_bar = _card(8)
        cb_lay = QVBoxLayout(card_bar)
        cb_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_barras = GraficoBarras([], "Bloqueios por empresa", _VERM)
        cb_lay.addWidget(self._graf_barras)
        graf_row.addWidget(card_bar, 3)

        root.addLayout(graf_row)

        card_tbl = _card(8)
        tl = QVBoxLayout(card_tbl)
        tl.setContentsMargins(0, 0, 0, 0)

        header_tbl = QFrame()
        header_tbl.setStyleSheet(
            f"background: #F4F7FA; border-radius: 8px 8px 0 0; border-bottom: 1px solid {_BORDA};"
        )
        hl = QHBoxLayout(header_tbl)
        hl.setContentsMargins(16, 10, 16, 10)
        lbl_det = QLabel("Registro detalhado de bloqueios")
        lbl_det.setStyleSheet(
            f"font-weight: bold; font-size: 12px; color: {_TITULO}; "
            "background: transparent; border: none;"
        )
        hl.addWidget(lbl_det)
        hl.addStretch()
        tl.addWidget(header_tbl)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(5)
        self._tabela.setHorizontalHeaderLabels(
            ["Colaborador", "Empresa", "Motivos", "Horario", "Operador"]
        )
        self._tabela.setStyleSheet(_estilo_tabela())
        self._tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setShowGrid(False)
        self._tabela.setMinimumHeight(200)
        tl.addWidget(self._tabela)
        root.addWidget(card_tbl, 1)

    def _on_periodo_rapido(self, idx: int):
        hoje = QDate.currentDate()
        if idx == 0:
            return
        elif idx == 1:
            self._dt_ini.setDate(hoje)
            self._dt_fim.setDate(hoje)
        elif idx == 2:
            self._dt_ini.setDate(hoje.addDays(-7))
            self._dt_fim.setDate(hoje)
        elif idx == 3:
            self._dt_ini.setDate(hoje.addDays(-30))
            self._dt_fim.setDate(hoje)
        elif idx == 4:
            self._dt_ini.setDate(QDate(hoje.year(), hoje.month(), 1))
            self._dt_fim.setDate(hoje)
        self.carregar_dados()

    def carregar_dados(self):
        if self._carregando:
            return
        self._carregando = True
        self._btn_atualizar.setEnabled(False)
        try:
            from app.core.database import get_session
            from app.models.bloqueio import Bloqueio
            from app.models.trabalhador import Trabalhador
            from sqlalchemy.orm import joinedload

            qdi = self._dt_ini.date()
            qdf = self._dt_fim.date()
            ini = datetime(qdi.year(), qdi.month(), qdi.day())
            fim = datetime(qdf.year(), qdf.month(), qdf.day(), 23, 59, 59)

            print(f"[BLQ] Carregando: {ini} → {fim}")

            session = get_session()
            try:
                rows = (
                    session.query(Bloqueio, Trabalhador)
                    .join(Trabalhador, Bloqueio.trabalhador_id == Trabalhador.id)
                    .options(joinedload(Trabalhador.empresa))
                    .filter(Bloqueio.criado_em >= ini, Bloqueio.criado_em <= fim)
                    .order_by(Bloqueio.criado_em.desc())
                    .all()
                )
            finally:
                session.close()

            print(f"[BLQ] {len(rows)} registros encontrados")

            def _motivos(b) -> str:
                m = []
                if getattr(b, "doc_incompleta",      False): m.append("Doc. invalida")
                if getattr(b, "determinacao_gestao", False): m.append("Manual")
                if getattr(b, "sem_epi",             False): m.append("Sem EPI")
                if getattr(b, "comportamento",       False): m.append("Comportamento")
                if getattr(b, "outro",               False): m.append("Outro")
                return ", ".join(m) if m else (b.tipo or "—")

            por_motivo: dict = defaultdict(int)
            por_emp:    dict = defaultdict(int)
            manual_count = 0
            detalhe = []

            for b, t in rows:
                mot_str = _motivos(b)
                emp     = t.empresa.razao_social if t.empresa else "Sem empresa"
                hora    = b.criado_em.strftime("%d/%m %H:%M") if b.criado_em else "—"
                op      = getattr(b, "registrado_por", "portaria") or "portaria"
                for mot in mot_str.split(", "):
                    por_motivo[mot.strip()] += 1
                por_emp[emp] += 1
                if getattr(b, "determinacao_gestao", False):
                    manual_count += 1
                detalhe.append((t.nome, emp, mot_str, hora, op))

            por_motivo_lst  = sorted(por_motivo.items(), key=lambda x: -x[1])
            por_empresa_lst = sorted(por_emp.items(),    key=lambda x: -x[1])

            self._dados = {
                "periodo":         f"{qdi.toString('dd/MM/yyyy')} a {qdf.toString('dd/MM/yyyy')}",
                "total_bloqueios": len(rows),
                "por_motivo":      por_motivo_lst,
                "por_empresa":     por_empresa_lst,
                "detalhe":         detalhe,
            }

            self._kpi_total.set_valor(str(len(rows)))
            self._kpi_empresas.set_valor(str(len(por_emp)))
            self._kpi_motivos.set_valor(str(len(por_motivo)))
            self._kpi_manual.set_valor(str(manual_count))

            self._graf_pizza.atualizar(por_motivo_lst[:8], "Bloqueios por motivo")
            self._graf_barras.atualizar(
                [(e, v) for e, v in por_empresa_lst[:10]], "Bloqueios por empresa"
            )

            self._tabela.setRowCount(len(detalhe))
            for row, (nome, emp, mot, hora, op) in enumerate(detalhe):
                for col, txt in enumerate([nome, emp, mot, hora, op]):
                    it = QTableWidgetItem(txt)
                    it.setTextAlignment(
                        Qt.AlignCenter if col >= 3 else Qt.AlignLeft | Qt.AlignVCenter
                    )
                    it.setBackground(QColor(_VERM_BG))
                    self._tabela.setItem(row, col, it)

            self._btn_pdf.setEnabled(True)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao carregar", str(e))
        finally:
            self._carregando = False
            self._btn_atualizar.setEnabled(True)

    def _exportar_pdf(self):
        if not self._dados:
            return
        pasta   = _pasta_downloads()
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = str(pasta / _nome_relatorio("bloqueios"))
        try:
            GeradorPDF.bloqueios(self._dados, caminho)
            QMessageBox.information(
                self, "PDF gerado",
                f"Salvo em:\n{caminho}"
            )
            self._abrir_arquivo(caminho)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao gerar PDF", str(e))

    @staticmethod
    def _abrir_arquivo(caminho: str):
        try:
            if sys.platform == "win32":
                os.startfile(caminho)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", caminho])
            else:
                subprocess.Popen(["xdg-open", caminho])
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Página principal
# ─────────────────────────────────────────────────────────────────────────────

class RelatoriosPage(QWidget):
    """
    Encaixe no stack do MainWindow:

        from app.ui.pages.relatorios_page import RelatoriosPage
        self._relatorios = RelatoriosPage()
        self.stack.addWidget(self._relatorios)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {_BG};")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        ic  = QLabel()
        ic.setPixmap(qta.icon("fa5s.chart-bar", color=_AZUL).pixmap(22, 22))
        ic.setStyleSheet("background: transparent; border: none;")
        hdr.addWidget(ic)
        vl = QVBoxLayout()
        vl.setSpacing(2)
        lbl_t = QLabel("Relatorios")
        lbl_t.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {_TITULO}; "
            "background: transparent; border: none;"
        )
        lbl_s = QLabel("Movimentacao e Bloqueios com graficos e exportacao PDF")
        lbl_s.setStyleSheet(
            f"font-size: 12px; color: {_SUB}; background: transparent; border: none;"
        )
        vl.addWidget(lbl_t)
        vl.addWidget(lbl_s)
        hdr.addLayout(vl)
        hdr.addStretch()
        root.addLayout(hdr)
        root.addWidget(_sep())

        from PySide6.QtWidgets import QTabWidget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {_BORDA};
                background: {_BG};
                border-radius: 0 8px 8px 8px;
            }}
            QTabBar::tab {{
                background: #F4F7FA; color: {_LABEL};
                border: 1px solid {_BORDA}; border-bottom: none;
                padding: 9px 24px; font-size: 12px; font-weight: bold;
                margin-right: 3px; border-radius: 6px 6px 0 0;
            }}
            QTabBar::tab:selected {{
                background: {_CARD}; color: {_AZUL};
                border-top: 2px solid {_AZUL};
            }}
            QTabBar::tab:hover:!selected {{
                background: #EBF0F6; color: {_TITULO};
            }}
        """)

        self._aba_mov = AbaMovimentacao()
        self._aba_blq = AbaBloqueios()

        def _wrap(widget: QWidget) -> QScrollArea:
            sa = QScrollArea()
            sa.setWidgetResizable(True)
            sa.setStyleSheet("border: none; background: transparent;")
            sa.setWidget(widget)
            return sa

        self._tabs.addTab(_wrap(self._aba_mov), "  Movimentacao  ")
        self._tabs.addTab(_wrap(self._aba_blq), "  Bloqueios  ")
        root.addWidget(self._tabs, 1)

    def carregar_dados(self):
        """Chamado pelo MainWindow ao navegar para esta página."""
        self._aba_mov.carregar_dados()
        self._aba_blq.carregar_dados()                              