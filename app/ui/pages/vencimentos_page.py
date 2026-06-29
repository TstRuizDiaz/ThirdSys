"""
vencimentos_page.py
─────────────────────────────────────────────────────────────────────────────
Tela de Vencimentos do ThirdSys.

Documentos monitorados:
  • Por colaborador : ASO, Integrações, Treinamentos
  • Por empresa     : PGR, PCMSO, Apólice de Seguro de Vida

Status calculados a partir da periodicidade cadastrada na ficha:
  • VENCIDO   — já expirou
  • CRÍTICO   — vence em até 30 dias
  • ATENÇÃO   — vence em 31–90 dias
  • REGULAR   — vence em mais de 90 dias
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
import subprocess
import sys
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QSize, QDate, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QMessageBox,
    QPushButton, QScrollArea, QSizePolicy, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

# ─────────────────────────────────────────────────────────────────────────────
# Paleta — idêntica ao relatorios_page
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
_LARAN    = "#C2410C"
_LARAN_BG = "#FFF7ED"
_LARAN_BD = "#FDBA74"

# Status
_STATUS_CORES = {
    "VENCIDO":  (_VERM,  _VERM_BG,  _VERM_BD),
    "CRÍTICO":  (_LARAN, _LARAN_BG, _LARAN_BD),
    "ATENÇÃO":  (_AMAR,  _AMAR_BG,  _AMAR_BD),
    "REGULAR":  (_VERDE, _VERDE_BG, _VERDE_BD),
}

_GRAF_CORES = ["#DC2626", "#C2410C", "#D97706", "#16A34A"]

_LOGO_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "assets", "logo.png"
))

# Tipos de documento
_DOCS_COLABORADOR = ["ASO", "Integração", "Treinamento"]
_DOCS_EMPRESA     = ["PGR", "PCMSO", "Apólice Seg. Vida"]
_TODOS_DOCS       = _DOCS_COLABORADOR + _DOCS_EMPRESA


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pasta_downloads() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads"
    return Path.home() / "Downloads"


def _nome_relatorio(tipo: str) -> str:
    agora = datetime.now().strftime("%d-%m-%Y_%H-%M")
    return f"relatorio_{tipo}_{agora}.pdf"


def _calcular_status(dias_restantes: int) -> str:
    if dias_restantes < 0:
        return "VENCIDO"
    elif dias_restantes <= 30:
        return "CRÍTICO"
    elif dias_restantes <= 90:
        return "ATENÇÃO"
    return "REGULAR"


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
            border: 1px solid {_BORDA};
            selection-background-color: {_AZUL_BG};
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


# ─────────────────────────────────────────────────────────────────────────────
# Card KPI
# ─────────────────────────────────────────────────────────────────────────────

class CardKPI(QFrame):
    def __init__(self, icone: str, cor: str, titulo: str,
                 valor: str = "—", parent=None):
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
            f"font-size: 10px; color: {_LABEL}; font-weight: bold;"
            " background: transparent; border: none;"
        )
        topo.addWidget(ic)
        topo.addWidget(lbl_t)
        topo.addStretch()
        lay.addLayout(topo)

        self._lbl_valor = QLabel(valor)
        self._lbl_valor.setStyleSheet(
            f"font-size: 26px; font-weight: bold; color: {cor};"
            " background: transparent; border: none;"
        )
        lay.addWidget(self._lbl_valor)

    def set_valor(self, v: str):
        self._lbl_valor.setText(v)


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico de barras horizontais por status
# ─────────────────────────────────────────────────────────────────────────────

class GraficoStatusBarras(QWidget):
    """Barras horizontais agrupadas por status de vencimento."""

    def __init__(self, dados: dict, titulo: str = "", parent=None):
        super().__init__(parent)
        # dados = {"VENCIDO": n, "CRÍTICO": n, "ATENÇÃO": n, "REGULAR": n}
        self._dados  = dados
        self._titulo = titulo
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def atualizar(self, dados: dict, titulo: str = ""):
        self._dados  = dados
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
            PAD_L, PAD_R, PAD_T, PAD_B = 90, 60, 30, 16
            area_w = W - PAD_L - PAD_R
            area_h = H - PAD_T - PAD_B

            p.fillRect(0, 0, W, H, QColor(_CARD))

            if self._titulo:
                p.setPen(QColor(_TITULO))
                p.setFont(QFont("Segoe UI", 10, QFont.Bold))
                p.drawText(PAD_L, 18, self._titulo)

            labels  = ["VENCIDO", "CRÍTICO", "ATENÇÃO", "REGULAR"]
            valores  = [self._dados.get(l, 0) for l in labels]
            max_v    = max(valores) if valores else 1
            if max_v == 0:
                max_v = 1

            n        = len(labels)
            gap      = 10
            bar_h    = max(16, (area_h - gap * (n + 1)) // n)

            for i, (label, valor) in enumerate(zip(labels, valores)):
                cor_txt, cor_bg, _ = _STATUS_CORES[label]
                y = PAD_T + gap + i * (bar_h + gap)

                # rótulo
                p.setPen(QColor(_SUB))
                p.setFont(QFont("Segoe UI", 9))
                p.drawText(0, y, PAD_L - 8, bar_h,
                           Qt.AlignRight | Qt.AlignVCenter, label)

                # trilha
                path_t = QPainterPath()
                path_t.addRoundedRect(PAD_L, y, area_w, bar_h, 4, 4)
                p.fillPath(path_t, QColor("#F1F5F9"))

                # barra preenchida
                bw = int(area_w * valor / max_v) if max_v else 0
                if bw > 0:
                    path_b = QPainterPath()
                    path_b.addRoundedRect(PAD_L, y, bw, bar_h, 4, 4)
                    cor = QColor(cor_txt)
                    cor.setAlpha(210)
                    p.fillPath(path_b, cor)

                # valor
                p.setPen(QColor(_TITULO))
                p.setFont(QFont("Segoe UI", 9, QFont.Bold))
                p.drawText(PAD_L + area_w + 6, y, PAD_R - 6, bar_h,
                           Qt.AlignLeft | Qt.AlignVCenter, str(valor))

        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Gráfico de pizza por tipo de documento
# ─────────────────────────────────────────────────────────────────────────────

class GraficoPizzaTipo(QWidget):
    def __init__(self, dados: list, titulo: str = "", parent=None):
        super().__init__(parent)
        self._dados  = dados   # [(tipo, n), ...]
        self._titulo = titulo
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def atualizar(self, dados: list, titulo: str = ""):
        self._dados  = dados
        if titulo:
            self._titulo = titulo
        self.update()

    def paintEvent(self, _):
        if not self._dados:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        GRAF_CORES = [
            "#2563EB", "#16A34A", "#D97706", "#DC2626",
            "#7C3AED", "#0891B2", "#BE185D", "#65A30D",
        ]
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
            for i, (_, valor) in enumerate(self._dados):
                span = 360 * 16 * valor / total
                cor  = QColor(GRAF_CORES[i % len(GRAF_CORES)])
                p.setBrush(cor)
                p.setPen(QPen(QColor(_CARD), 2))
                p.drawPie(cx - r, cy - r, pizza_sz, pizza_sz,
                          int(angulo), int(span))
                angulo += span

            leg_x = cx + r + 16
            leg_y = cy - r
            p.setFont(QFont("Segoe UI", 9))
            for i, (rotulo, valor) in enumerate(self._dados):
                cor = QColor(GRAF_CORES[i % len(GRAF_CORES)])
                p.setBrush(cor)
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(leg_x, leg_y + i * 22, 12, 12, 3, 3)
                p.setPen(QColor(_TITULO))
                pct = f"{100 * valor / total:.0f}%"
                p.drawText(leg_x + 18, leg_y + i * 22 + 10,
                           f"{rotulo[:20]} — {valor} ({pct})")
        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Badge de status
# ─────────────────────────────────────────────────────────────────────────────

def _badge_status(status: str) -> QLabel:
    cor, bg, bd = _STATUS_CORES.get(status, (_LABEL, _BG, _BORDA))
    lbl = QLabel(status)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(f"""
        background: {bg}; color: {cor};
        border: 1px solid {bd};
        border-radius: 4px; padding: 2px 8px;
        font-size: 10px; font-weight: bold;
    """)
    return lbl


# ─────────────────────────────────────────────────────────────────────────────
# Aba colaboradores (ASO / Integração / Treinamento)
# ─────────────────────────────────────────────────────────────────────────────

class AbaColaboradores(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: list = []
        self._carregando  = False
        self.setStyleSheet(f"background: {_BG}; border: none;")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # ── Filtros ───────────────────────────────────────────────────────────
        filtros = _card(8)
        fl = QHBoxLayout(filtros)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        fl.addWidget(self._lbl("Tipo:"))
        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(["Todos"] + _DOCS_COLABORADOR)
        self._combo_tipo.setStyleSheet(_estilo_combo())
        self._combo_tipo.setFixedHeight(34)
        self._combo_tipo.currentIndexChanged.connect(self._aplicar_filtro)
        fl.addWidget(self._combo_tipo)

        fl.addWidget(self._lbl("Status:"))
        self._combo_status = QComboBox()
        self._combo_status.addItems(["Todos", "VENCIDO", "CRÍTICO", "ATENÇÃO", "REGULAR"])
        self._combo_status.setStyleSheet(_estilo_combo())
        self._combo_status.setFixedHeight(34)
        self._combo_status.currentIndexChanged.connect(self._aplicar_filtro)
        fl.addWidget(self._combo_status)

        fl.addWidget(self._lbl("Empresa:"))
        self._combo_empresa = QComboBox()
        self._combo_empresa.addItems(["Todas"])
        self._combo_empresa.setStyleSheet(_estilo_combo())
        self._combo_empresa.setFixedHeight(34)
        self._combo_empresa.setMinimumWidth(180)
        self._combo_empresa.currentIndexChanged.connect(self._aplicar_filtro)
        fl.addWidget(self._combo_empresa)

        fl.addStretch()

        self._btn_atualizar = _btn("  Atualizar", "fa5s.sync", _AZUL, "#1D4ED8")
        self._btn_atualizar.clicked.connect(self.carregar_dados)
        fl.addWidget(self._btn_atualizar)

        self._btn_pdf = _btn("  Exportar PDF", "fa5s.file-pdf", _VERM, "#7F1D1D")
        self._btn_pdf.clicked.connect(self._exportar_pdf)
        self._btn_pdf.setEnabled(False)
        fl.addWidget(self._btn_pdf)

        root.addWidget(filtros)

        # ── KPIs ──────────────────────────────────────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_vencido  = CardKPI("fa5s.times-circle",    _VERM,  "Vencidos")
        self._kpi_critico  = CardKPI("fa5s.exclamation-circle", _LARAN, "Críticos (≤30d)")
        self._kpi_atencao  = CardKPI("fa5s.clock",           _AMAR,  "Atenção (31–90d)")
        self._kpi_regular  = CardKPI("fa5s.check-circle",    _VERDE, "Regulares")
        for k in [self._kpi_vencido, self._kpi_critico,
                  self._kpi_atencao, self._kpi_regular]:
            kpi_row.addWidget(k, 1)
        root.addLayout(kpi_row)

        # ── Gráficos ──────────────────────────────────────────────────────────
        graf_row = QHBoxLayout()
        graf_row.setSpacing(12)

        card_barras = _card(8)
        cb_lay = QVBoxLayout(card_barras)
        cb_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_status = GraficoStatusBarras({}, "Documentos por status")
        cb_lay.addWidget(self._graf_status)
        graf_row.addWidget(card_barras, 3)

        card_pizza = _card(8)
        cp_lay = QVBoxLayout(card_pizza)
        cp_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_tipo = GraficoPizzaTipo([], "Distribuição por tipo")
        cp_lay.addWidget(self._graf_tipo)
        graf_row.addWidget(card_pizza, 2)

        root.addLayout(graf_row)

        # ── Tabela ────────────────────────────────────────────────────────────
        card_tbl = _card(8)
        tl = QVBoxLayout(card_tbl)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)

        hdr_tbl = QFrame()
        hdr_tbl.setStyleSheet(
            f"background: #F4F7FA; border-radius: 8px 8px 0 0;"
            f" border-bottom: 1px solid {_BORDA};"
        )
        hl = QHBoxLayout(hdr_tbl)
        hl.setContentsMargins(16, 10, 16, 10)
        lbl_det = QLabel("Registro detalhado — Colaboradores")
        lbl_det.setStyleSheet(
            f"font-weight: bold; font-size: 12px; color: {_TITULO};"
            " background: transparent; border: none;"
        )
        hl.addWidget(lbl_det)
        hl.addStretch()
        self._lbl_total = QLabel()
        self._lbl_total.setStyleSheet(
            f"font-size: 11px; color: {_LABEL}; background: transparent; border: none;"
        )
        hl.addWidget(self._lbl_total)
        tl.addWidget(hdr_tbl)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(7)
        self._tabela.setHorizontalHeaderLabels([
            "Colaborador", "Empresa", "Tipo", "Emissão",
            "Vencimento", "Dias restantes", "Status"
        ])
        self._tabela.setStyleSheet(_estilo_tabela())
        self._tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setShowGrid(False)
        self._tabela.setMinimumHeight(220)
        tl.addWidget(self._tabela)
        root.addWidget(card_tbl, 1)

    # ── dados ─────────────────────────────────────────────────────────────────

    def carregar_dados(self):
        if self._carregando:
            return
        self._carregando = True
        self._btn_atualizar.setEnabled(False)
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            from app.models.empresa import Empresa
            from sqlalchemy.orm import joinedload

            session = get_session()
            try:
                trabalhadores = (
                    session.query(Trabalhador)
                    .options(joinedload(Trabalhador.empresa), joinedload(Trabalhador.treinamentos))
                    .filter(Trabalhador.ativo == True)
                    .all()
                )
            finally:
                session.close()

            hoje = date.today()
            self._dados = []
            empresas = set()

            for t in trabalhadores:
                emp_nome = t.empresa.razao_social if t.empresa else "Sem empresa"
                empresas.add(emp_nome)

                # ASO — campos reais do model Trabalhador: aso_data_inicial / aso_validade
                if getattr(t, "aso_validade", None):
                    venc = t.aso_validade if isinstance(t.aso_validade, date) \
                        else t.aso_validade.date()
                    emis = getattr(t, "aso_data_inicial", None)
                    dias = (venc - hoje).days
                    self._dados.append({
                        "nome": t.nome, "empresa": emp_nome,
                        "tipo": "ASO",
                        "emissao":    emis.strftime("%d/%m/%Y") if emis else "—",
                        "vencimento": venc.strftime("%d/%m/%Y"),
                        "dias":       dias,
                        "status":     _calcular_status(dias),
                    })

                # Integração (NR-01) e demais Treinamentos — vêm do model
                # Treinamento (trabalhador_id, nr_nome, data_realizacao,
                # data_validade). NR-01 é tratado como "Integração".
                treinamentos = getattr(t, "treinamentos", None) or []
                for tr in treinamentos:
                    venc_tr = getattr(tr, "data_validade", None)
                    if not venc_tr:
                        continue
                    venc_tr = venc_tr if isinstance(venc_tr, date) else venc_tr.date()
                    emis_tr = getattr(tr, "data_realizacao", None)
                    dias_tr = (venc_tr - hoje).days
                    is_integracao = getattr(tr, "is_integracao", False)
                    tipo_label = "Integração" if is_integracao else f"Treinamento · {getattr(tr, 'nr_nome', '')}"
                    self._dados.append({
                        "nome": t.nome, "empresa": emp_nome,
                        "tipo": tipo_label,
                        "emissao":    emis_tr.strftime("%d/%m/%Y") if emis_tr else "—",
                        "vencimento": venc_tr.strftime("%d/%m/%Y"),
                        "dias":       dias_tr,
                        "status":     _calcular_status(dias_tr),
                    })

            # Atualiza filtro de empresas
            atual = self._combo_empresa.currentText()
            self._combo_empresa.blockSignals(True)
            self._combo_empresa.clear()
            self._combo_empresa.addItem("Todas")
            for e in sorted(empresas):
                self._combo_empresa.addItem(e)
            idx = self._combo_empresa.findText(atual)
            self._combo_empresa.setCurrentIndex(max(0, idx))
            self._combo_empresa.blockSignals(False)

            self._aplicar_filtro()
            self._btn_pdf.setEnabled(True)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao carregar", str(e))
        finally:
            self._carregando = False
            self._btn_atualizar.setEnabled(True)

    def _aplicar_filtro(self):
        tipo_f   = self._combo_tipo.currentText()
        status_f = self._combo_status.currentText()
        emp_f    = self._combo_empresa.currentText()

        filtrado = [
            d for d in self._dados
            if (tipo_f   == "Todos" or d["tipo"].startswith(tipo_f))
            and (status_f == "Todos" or d["status"] == status_f)
            and (emp_f    == "Todas" or d["empresa"] == emp_f)
        ]

        # KPIs
        contagem = {"VENCIDO": 0, "CRÍTICO": 0, "ATENÇÃO": 0, "REGULAR": 0}
        for d in self._dados:  # KPIs sempre sobre total sem filtro de status
            contagem[d["status"]] = contagem.get(d["status"], 0) + 1
        self._kpi_vencido.set_valor(str(contagem["VENCIDO"]))
        self._kpi_critico.set_valor(str(contagem["CRÍTICO"]))
        self._kpi_atencao.set_valor(str(contagem["ATENÇÃO"]))
        self._kpi_regular.set_valor(str(contagem["REGULAR"]))

        # Gráficos
        self._graf_status.atualizar(contagem, "Documentos por status")

        tipo_cont: dict = {}
        for d in self._dados:
            base = d["tipo"].split(" · ")[0]
            tipo_cont[base] = tipo_cont.get(base, 0) + 1
        self._graf_tipo.atualizar(
            sorted(tipo_cont.items(), key=lambda x: -x[1]),
            "Distribuição por tipo"
        )

        # Tabela
        self._lbl_total.setText(f"{len(filtrado)} registros")
        self._tabela.setRowCount(len(filtrado))
        # Ordena: VENCIDO primeiro, depois CRÍTICO, ATENÇÃO, REGULAR
        ordem = {"VENCIDO": 0, "CRÍTICO": 1, "ATENÇÃO": 2, "REGULAR": 3}
        filtrado.sort(key=lambda d: (ordem.get(d["status"], 9), d["dias"]))

        for row, d in enumerate(filtrado):
            cor_txt, cor_bg, _ = _STATUS_CORES.get(d["status"], (_LABEL, _BG, _BORDA))
            dias_str = str(d["dias"]) if d["dias"] >= 0 else f"{abs(d['dias'])}d vencido"

            for col, txt in enumerate([
                d["nome"], d["empresa"], d["tipo"],
                d["emissao"], d["vencimento"], dias_str, d["status"]
            ]):
                it = QTableWidgetItem(txt)
                it.setTextAlignment(
                    Qt.AlignCenter if col >= 3
                    else Qt.AlignLeft | Qt.AlignVCenter
                )
                if col == 6:
                    it.setForeground(QColor(cor_txt))
                    it.setBackground(QColor(cor_bg))
                elif d["status"] in ("VENCIDO", "CRÍTICO"):
                    it.setBackground(QColor(cor_bg))
                self._tabela.setItem(row, col, it)

    def _exportar_pdf(self):
        if not self._dados:
            return
        pasta   = _pasta_downloads()
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = str(pasta / _nome_relatorio("vencimentos_colaboradores"))
        try:
            GeradorPDFVencimentos.colaboradores(self._dados, caminho)
            QMessageBox.information(self, "PDF gerado", f"Salvo em:\n{caminho}")
            _abrir_arquivo(caminho)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao gerar PDF", str(e))

    @staticmethod
    def _lbl(texto: str) -> QLabel:
        l = QLabel(texto)
        l.setStyleSheet(f"color: {_SUB}; font-size: 12px; background: transparent;")
        return l


# ─────────────────────────────────────────────────────────────────────────────
# Aba empresas (PGR / PCMSO / Apólice)
# ─────────────────────────────────────────────────────────────────────────────

class AbaEmpresas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: list = []
        self._carregando  = False
        self.setStyleSheet(f"background: {_BG}; border: none;")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # ── Filtros ───────────────────────────────────────────────────────────
        filtros = _card(8)
        fl = QHBoxLayout(filtros)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(12)

        fl.addWidget(self._lbl("Tipo:"))
        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(["Todos"] + _DOCS_EMPRESA)
        self._combo_tipo.setStyleSheet(_estilo_combo())
        self._combo_tipo.setFixedHeight(34)
        self._combo_tipo.currentIndexChanged.connect(self._aplicar_filtro)
        fl.addWidget(self._combo_tipo)

        fl.addWidget(self._lbl("Status:"))
        self._combo_status = QComboBox()
        self._combo_status.addItems(["Todos", "VENCIDO", "CRÍTICO", "ATENÇÃO", "REGULAR"])
        self._combo_status.setStyleSheet(_estilo_combo())
        self._combo_status.setFixedHeight(34)
        self._combo_status.currentIndexChanged.connect(self._aplicar_filtro)
        fl.addWidget(self._combo_status)

        fl.addStretch()

        self._btn_atualizar = _btn("  Atualizar", "fa5s.sync", _AZUL, "#1D4ED8")
        self._btn_atualizar.clicked.connect(self.carregar_dados)
        fl.addWidget(self._btn_atualizar)

        self._btn_pdf = _btn("  Exportar PDF", "fa5s.file-pdf", _VERM, "#7F1D1D")
        self._btn_pdf.clicked.connect(self._exportar_pdf)
        self._btn_pdf.setEnabled(False)
        fl.addWidget(self._btn_pdf)

        root.addWidget(filtros)

        # ── KPIs ──────────────────────────────────────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_vencido = CardKPI("fa5s.times-circle",       _VERM,  "Vencidos")
        self._kpi_critico = CardKPI("fa5s.exclamation-circle", _LARAN, "Críticos (≤30d)")
        self._kpi_atencao = CardKPI("fa5s.clock",              _AMAR,  "Atenção (31–90d)")
        self._kpi_regular = CardKPI("fa5s.check-circle",       _VERDE, "Regulares")
        for k in [self._kpi_vencido, self._kpi_critico,
                  self._kpi_atencao, self._kpi_regular]:
            kpi_row.addWidget(k, 1)
        root.addLayout(kpi_row)

        # ── Gráficos ──────────────────────────────────────────────────────────
        graf_row = QHBoxLayout()
        graf_row.setSpacing(12)

        card_barras = _card(8)
        cb_lay = QVBoxLayout(card_barras)
        cb_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_status = GraficoStatusBarras({}, "Documentos por status")
        cb_lay.addWidget(self._graf_status)
        graf_row.addWidget(card_barras, 3)

        card_pizza = _card(8)
        cp_lay = QVBoxLayout(card_pizza)
        cp_lay.setContentsMargins(12, 12, 12, 8)
        self._graf_tipo = GraficoPizzaTipo([], "Distribuição por tipo")
        cp_lay.addWidget(self._graf_tipo)
        graf_row.addWidget(card_pizza, 2)

        root.addLayout(graf_row)

        # ── Tabela ────────────────────────────────────────────────────────────
        card_tbl = _card(8)
        tl = QVBoxLayout(card_tbl)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)

        hdr_tbl = QFrame()
        hdr_tbl.setStyleSheet(
            f"background: #F4F7FA; border-radius: 8px 8px 0 0;"
            f" border-bottom: 1px solid {_BORDA};"
        )
        hl = QHBoxLayout(hdr_tbl)
        hl.setContentsMargins(16, 10, 16, 10)
        lbl_det = QLabel("Registro detalhado — Empresas")
        lbl_det.setStyleSheet(
            f"font-weight: bold; font-size: 12px; color: {_TITULO};"
            " background: transparent; border: none;"
        )
        hl.addWidget(lbl_det)
        hl.addStretch()
        self._lbl_total = QLabel()
        self._lbl_total.setStyleSheet(
            f"font-size: 11px; color: {_LABEL}; background: transparent; border: none;"
        )
        hl.addWidget(self._lbl_total)
        tl.addWidget(hdr_tbl)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(6)
        self._tabela.setHorizontalHeaderLabels([
            "Empresa", "Tipo", "Emissão",
            "Vencimento", "Dias restantes", "Status"
        ])
        self._tabela.setStyleSheet(_estilo_tabela())
        self._tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setShowGrid(False)
        self._tabela.setMinimumHeight(220)
        tl.addWidget(self._tabela)
        root.addWidget(card_tbl, 1)

    # ── dados ─────────────────────────────────────────────────────────────────

    def carregar_dados(self):
        if self._carregando:
            return
        self._carregando = True
        self._btn_atualizar.setEnabled(False)
        try:
            from app.core.database import get_session
            from app.models.empresa import Empresa

            session = get_session()
            try:
                # Empresa não tem campo "ativa" — usa o campo real "status"
                # (default "ativo"), conforme o model app/models/empresa.py.
                empresas = session.query(Empresa).filter(Empresa.status == "ativo").all()
            finally:
                session.close()

            hoje = date.today()
            self._dados = []

            # Campos reais do model Empresa: <prefixo>_data_inicial /
            # <prefixo>_validade (não "_emissao"/"_vencimento").
            _campos = [
                ("pgr_validade",     "pgr_data_inicial",     "PGR"),
                ("pcmso_validade",   "pcmso_data_inicial",   "PCMSO"),
                ("apolice_validade", "apolice_data_inicial", "Apólice Seg. Vida"),
            ]

            for emp in empresas:
                for campo_venc, campo_emis, tipo in _campos:
                    venc = getattr(emp, campo_venc, None)
                    if not venc:
                        continue
                    venc = venc if isinstance(venc, date) else venc.date()
                    emis = getattr(emp, campo_emis, None)
                    dias = (venc - hoje).days
                    self._dados.append({
                        "empresa":    emp.razao_social,
                        "tipo":       tipo,
                        "emissao":    emis.strftime("%d/%m/%Y") if emis else "—",
                        "vencimento": venc.strftime("%d/%m/%Y"),
                        "dias":       dias,
                        "status":     _calcular_status(dias),
                    })

            self._aplicar_filtro()
            self._btn_pdf.setEnabled(True)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao carregar", str(e))
        finally:
            self._carregando = False
            self._btn_atualizar.setEnabled(True)

    def _aplicar_filtro(self):
        tipo_f   = self._combo_tipo.currentText()
        status_f = self._combo_status.currentText()

        filtrado = [
            d for d in self._dados
            if (tipo_f   == "Todos" or d["tipo"] == tipo_f)
            and (status_f == "Todos" or d["status"] == status_f)
        ]

        contagem = {"VENCIDO": 0, "CRÍTICO": 0, "ATENÇÃO": 0, "REGULAR": 0}
        for d in self._dados:
            contagem[d["status"]] = contagem.get(d["status"], 0) + 1
        self._kpi_vencido.set_valor(str(contagem["VENCIDO"]))
        self._kpi_critico.set_valor(str(contagem["CRÍTICO"]))
        self._kpi_atencao.set_valor(str(contagem["ATENÇÃO"]))
        self._kpi_regular.set_valor(str(contagem["REGULAR"]))

        self._graf_status.atualizar(contagem, "Documentos por status")

        tipo_cont: dict = {}
        for d in self._dados:
            tipo_cont[d["tipo"]] = tipo_cont.get(d["tipo"], 0) + 1
        self._graf_tipo.atualizar(
            sorted(tipo_cont.items(), key=lambda x: -x[1]),
            "Distribuição por tipo"
        )

        self._lbl_total.setText(f"{len(filtrado)} registros")
        self._tabela.setRowCount(len(filtrado))
        ordem = {"VENCIDO": 0, "CRÍTICO": 1, "ATENÇÃO": 2, "REGULAR": 3}
        filtrado.sort(key=lambda d: (ordem.get(d["status"], 9), d["dias"]))

        for row, d in enumerate(filtrado):
            cor_txt, cor_bg, _ = _STATUS_CORES.get(d["status"], (_LABEL, _BG, _BORDA))
            dias_str = str(d["dias"]) if d["dias"] >= 0 else f"{abs(d['dias'])}d vencido"

            for col, txt in enumerate([
                d["empresa"], d["tipo"],
                d["emissao"], d["vencimento"], dias_str, d["status"]
            ]):
                it = QTableWidgetItem(txt)
                it.setTextAlignment(
                    Qt.AlignCenter if col >= 2
                    else Qt.AlignLeft | Qt.AlignVCenter
                )
                if col == 5:
                    it.setForeground(QColor(cor_txt))
                    it.setBackground(QColor(cor_bg))
                elif d["status"] in ("VENCIDO", "CRÍTICO"):
                    it.setBackground(QColor(cor_bg))
                self._tabela.setItem(row, col, it)

    def _exportar_pdf(self):
        if not self._dados:
            return
        pasta   = _pasta_downloads()
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = str(pasta / _nome_relatorio("vencimentos_empresas"))
        try:
            GeradorPDFVencimentos.empresas(self._dados, caminho)
            QMessageBox.information(self, "PDF gerado", f"Salvo em:\n{caminho}")
            _abrir_arquivo(caminho)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Erro ao gerar PDF", str(e))

    @staticmethod
    def _lbl(texto: str) -> QLabel:
        l = QLabel(texto)
        l.setStyleSheet(f"color: {_SUB}; font-size: 12px; background: transparent;")
        return l


# ─────────────────────────────────────────────────────────────────────────────
# Gerador de PDF
# ─────────────────────────────────────────────────────────────────────────────

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


class GeradorPDFVencimentos:

    _AZUL_RL  = (0.145, 0.388, 0.922)
    _CINZA_RL = (0.353, 0.474, 0.588)

    _COR_STATUS = {
        "VENCIDO":  (0.60, 0.11, 0.11),
        "CRÍTICO":  (0.76, 0.25, 0.05),
        "ATENÇÃO":  (0.57, 0.25, 0.05),
        "REGULAR":  (0.09, 0.64, 0.29),
    }

    @classmethod
    def _cabecalho(cls, canvas, doc, titulo: str):
        from reportlab.lib.pagesizes import A4
        w, h = A4
        c = canvas
        c.setFillColorRGB(*cls._AZUL_RL)
        c.rect(0, h - 56, w, 56, fill=1, stroke=0)
        if os.path.exists(_LOGO_PATH):
            c.drawImage(_LOGO_PATH, x=(w/2)-60, y=h-54,
                        width=120, height=44, mask="auto")
        else:
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(28, h - 34, "ThirdSys")
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(w - 28, h - 32, titulo)
        c.setFont("Helvetica", 9)
        c.drawRightString(w - 28, h - 46,
                          f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.setStrokeColorRGB(*cls._CINZA_RL)
        c.setLineWidth(0.5)
        c.line(28, h - 64, w - 28, h - 64)

    @classmethod
    def _rodape(cls, canvas, doc):
        from reportlab.lib.pagesizes import A4
        w, h = A4
        c = canvas
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.5)
        c.line(28, 36, w - 28, 36)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.setFont("Helvetica", 8)
        c.drawString(28, 22, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawCentredString(w / 2, 22, "Santiago Ruiz — ThirdSys")
        c.drawRightString(w - 28, 22, f"Página {doc.page}")

    @classmethod
    def colaboradores(cls, dados: list, caminho: str):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle

        W_PAGE, _ = A4
        doc = SimpleDocTemplate(caminho, pagesize=A4,
                                leftMargin=28, rightMargin=28,
                                topMargin=72, bottomMargin=56)

        def _on_page(canvas, doc):
            cls._cabecalho(canvas, doc, "Vencimentos — Colaboradores")
            cls._rodape(canvas, doc)

        cin  = colors.HexColor("#5A7A96")
        d_w  = W_PAGE - 56
        st_sec = ParagraphStyle("sec", fontName="Helvetica-Bold",
                                fontSize=9, textColor=cin,
                                spaceBefore=14, spaceAfter=4)
        story = []

        # KPI resumo
        contagem = {"VENCIDO": 0, "CRÍTICO": 0, "ATENÇÃO": 0, "REGULAR": 0}
        for d in dados:
            contagem[d["status"]] = contagem.get(d["status"], 0) + 1

        kpi = Table(
            [list(contagem.keys()), [str(v) for v in contagem.values()]],
            colWidths=[d_w / 4] * 4
        )
        _cores_kpi = {
            "VENCIDO": "#FEF2F2", "CRÍTICO": "#FFF7ED",
            "ATENÇÃO": "#FFFBEB", "REGULAR": "#F0FAF4"
        }
        _cores_txt = {
            "VENCIDO": "#991B1B", "CRÍTICO": "#C2410C",
            "ATENÇÃO": "#92400E", "REGULAR": "#16A34A"
        }
        kpi.setStyle(TableStyle([
            *[("BACKGROUND",  (i, 0), (i, 0), colors.HexColor(_cores_kpi[s]))
              for i, s in enumerate(contagem.keys())],
            *[("TEXTCOLOR",   (i, 1), (i, 1), colors.HexColor(_cores_txt[s]))
              for i, s in enumerate(contagem.keys())],
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8),
            ("FONTSIZE",      (0, 1), (-1, 1), 20),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi)
        story.append(Spacer(1, 14))

        # Tabela detalhada
        story.append(Paragraph("Registro detalhado", st_sec))
        rows = [["Colaborador", "Empresa", "Tipo", "Emissão", "Vencimento", "Dias", "Status"]]
        ordem = {"VENCIDO": 0, "CRÍTICO": 1, "ATENÇÃO": 2, "REGULAR": 3}
        for d in sorted(dados, key=lambda x: (ordem.get(x["status"], 9), x["dias"])):
            dias_str = str(d["dias"]) if d["dias"] >= 0 else f"{abs(d['dias'])}d vencido"
            rows.append([d["nome"], d["empresa"], d["tipo"],
                         d["emissao"], d["vencimento"], dias_str, d["status"]])

        cw = [d_w*0.20, d_w*0.20, d_w*0.15, d_w*0.12, d_w*0.12, d_w*0.09, d_w*0.12]
        tbl = Table(rows, colWidths=cw, repeatRows=1)
        tbl_style = [
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ALIGN",       (3, 0), (-1, -1), "CENTER"),
            ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]
        for i, d in enumerate(dados, start=1):
            bg_hex = {"VENCIDO": "#FEF2F2", "CRÍTICO": "#FFF7ED",
                      "ATENÇÃO": "#FFFBEB", "REGULAR": "#FFFFFF"}.get(d["status"], "#FFFFFF")
            tbl_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg_hex)))
            txt_hex = _cores_txt.get(d["status"], "#374151")
            tbl_style.append(("TEXTCOLOR", (6, i), (6, i), colors.HexColor(txt_hex)))
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)

    @classmethod
    def empresas(cls, dados: list, caminho: str):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle

        W_PAGE, _ = A4
        doc = SimpleDocTemplate(caminho, pagesize=A4,
                                leftMargin=28, rightMargin=28,
                                topMargin=72, bottomMargin=56)

        def _on_page(canvas, doc):
            cls._cabecalho(canvas, doc, "Vencimentos — Empresas")
            cls._rodape(canvas, doc)

        cin  = colors.HexColor("#5A7A96")
        d_w  = W_PAGE - 56
        st_sec = ParagraphStyle("sec", fontName="Helvetica-Bold",
                                fontSize=9, textColor=cin,
                                spaceBefore=14, spaceAfter=4)
        _cores_kpi = {
            "VENCIDO": "#FEF2F2", "CRÍTICO": "#FFF7ED",
            "ATENÇÃO": "#FFFBEB", "REGULAR": "#F0FAF4"
        }
        _cores_txt = {
            "VENCIDO": "#991B1B", "CRÍTICO": "#C2410C",
            "ATENÇÃO": "#92400E", "REGULAR": "#16A34A"
        }
        story = []
        contagem = {"VENCIDO": 0, "CRÍTICO": 0, "ATENÇÃO": 0, "REGULAR": 0}
        for d in dados:
            contagem[d["status"]] = contagem.get(d["status"], 0) + 1

        kpi = Table(
            [list(contagem.keys()), [str(v) for v in contagem.values()]],
            colWidths=[d_w / 4] * 4
        )
        kpi.setStyle(TableStyle([
            *[("BACKGROUND", (i, 0), (i, 0), colors.HexColor(_cores_kpi[s]))
              for i, s in enumerate(contagem.keys())],
            *[("TEXTCOLOR",  (i, 1), (i, 1), colors.HexColor(_cores_txt[s]))
              for i, s in enumerate(contagem.keys())],
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8),
            ("FONTSIZE",      (0, 1), (-1, 1), 20),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Registro detalhado", st_sec))
        rows = [["Empresa", "Tipo", "Emissão", "Vencimento", "Dias", "Status"]]
        ordem = {"VENCIDO": 0, "CRÍTICO": 1, "ATENÇÃO": 2, "REGULAR": 3}
        for d in sorted(dados, key=lambda x: (ordem.get(x["status"], 9), x["dias"])):
            dias_str = str(d["dias"]) if d["dias"] >= 0 else f"{abs(d['dias'])}d vencido"
            rows.append([d["empresa"], d["tipo"],
                         d["emissao"], d["vencimento"], dias_str, d["status"]])

        cw = [d_w*0.30, d_w*0.18, d_w*0.13, d_w*0.13, d_w*0.10, d_w*0.16]
        tbl = Table(rows, colWidths=cw, repeatRows=1)
        tbl_style = [
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#F4F7FA")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), cin),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ALIGN",       (2, 0), (-1, -1), "CENTER"),
            ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EA")),
            ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]
        for i, d in enumerate(dados, start=1):
            bg_hex = {"VENCIDO": "#FEF2F2", "CRÍTICO": "#FFF7ED",
                      "ATENÇÃO": "#FFFBEB", "REGULAR": "#FFFFFF"}.get(d["status"], "#FFFFFF")
            tbl_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg_hex)))
            txt_hex = _cores_txt.get(d["status"], "#374151")
            tbl_style.append(("TEXTCOLOR", (5, i), (5, i), colors.HexColor(txt_hex)))
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)


# ─────────────────────────────────────────────────────────────────────────────
# Página principal
# ─────────────────────────────────────────────────────────────────────────────

class VencimentosPage(QWidget):
    """
    Encaixe no stack do MainWindow:

        from app.ui.pages.vencimentos_page import VencimentosPage
        self._vencimentos = VencimentosPage()
        self.stack.addWidget(self._vencimentos)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {_BG};")
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        ic  = QLabel()
        ic.setPixmap(
            qta.icon("fa5s.exclamation-triangle", color=_AMAR).pixmap(22, 22)
        )
        ic.setStyleSheet("background: transparent; border: none;")
        hdr.addWidget(ic)

        vl = QVBoxLayout()
        vl.setSpacing(2)
        lbl_t = QLabel("Vencimentos")
        lbl_t.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {_TITULO};"
            " background: transparent; border: none;"
        )
        lbl_s = QLabel(
            "ASO · Integração · Treinamento · PGR · PCMSO · Apólice de Seguro de Vida"
        )
        lbl_s.setStyleSheet(
            f"font-size: 12px; color: {_SUB}; background: transparent; border: none;"
        )
        vl.addWidget(lbl_t)
        vl.addWidget(lbl_s)
        hdr.addLayout(vl)
        hdr.addStretch()

        # Legenda de status
        for label, cor in [("Vencido", _VERM), ("Crítico", _LARAN),
                            ("Atenção", _AMAR), ("Regular", _VERDE)]:
            dot = QLabel(f"● {label}")
            dot.setStyleSheet(
                f"color: {cor}; font-size: 11px; font-weight: bold;"
                " background: transparent; border: none;"
            )
            hdr.addWidget(dot)

        root.addLayout(hdr)
        root.addWidget(_sep())

        # ── Abas ──────────────────────────────────────────────────────────────
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

        self._aba_colab = AbaColaboradores()
        self._aba_emp   = AbaEmpresas()

        def _wrap(widget: QWidget) -> QScrollArea:
            sa = QScrollArea()
            sa.setWidgetResizable(True)
            sa.setStyleSheet("border: none; background: transparent;")
            sa.setWidget(widget)
            return sa

        self._tabs.addTab(_wrap(self._aba_colab), "  Colaboradores  ")
        self._tabs.addTab(_wrap(self._aba_emp),   "  Empresas  ")
        root.addWidget(self._tabs, 1)

    def carregar_dados(self):
        """Chamado pelo MainWindow ao navegar para esta página."""
        self._aba_colab.carregar_dados()
        self._aba_emp.carregar_dados()