"""
    page = SetoresPage(user_role="ADMINISTRATIVO")   # admin vê botões CRUD
    page = SetoresPage(user_role="TECNICO")          # outros só navegam
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QDialog, QDialogButtonBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

import qtawesome as qta


# ─────────────────────────────────────────────────────────────────────────────
# Domínio
# ─────────────────────────────────────────────────────────────────────────────

# Catálogo de ícones disponíveis para o usuário escolher
ICONES_DISPONIVEIS: list[tuple[str, str]] = [
    ("fa5s.building",    "Prédio"),
    ("fa5s.truck",       "Caminhão"),
    ("fa5s.wrench",      "Ferramentas"),
    ("fa5s.leaf",        "Folha"),
    ("fa5s.flask",       "Laboratório"),
    ("fa5s.box",         "Caixa"),
    ("fa5s.hard-hat",    "Capacete"),
    ("fa5s.ruler",       "Régua"),
    ("fa5s.fire-extinguisher", "Extintor"),
    ("fa5s.cogs",        "Engrenagens"),
    ("fa5s.users",       "Pessoas"),
    ("fa5s.clipboard",   "Prancheta"),
    ("fa5s.shield-alt",  "Escudo"),
    ("fa5s.chart-bar",   "Gráfico"),
    ("fa5s.laptop",      "Computador"),
]

# Paleta de cores predefinidas
CORES_PREDEFINIDAS: list[tuple[str, str, str]] = [
    # (cor_principal, bg_claro, bg_hover)
    ("#2563EB", "#EFF6FF", "#DBEAFE"),  # Azul
    ("#7C3AED", "#F5F3FF", "#EDE9FE"),  # Roxo
    ("#D97706", "#FFFBEB", "#FEF3C7"),  # Âmbar
    ("#16A34A", "#F0FDF4", "#DCFCE7"),  # Verde
    ("#0891B2", "#ECFEFF", "#CFFAFE"),  # Ciano
    ("#DC2626", "#FEF2F2", "#FEE2E2"),  # Vermelho
    ("#9333EA", "#FAF5FF", "#EDE9FE"),  # Violeta
    ("#059669", "#ECFDF5", "#D1FAE5"),  # Esmeralda
    ("#EA580C", "#FFF7ED", "#FFEDD5"),  # Laranja
    ("#0F172A", "#F8FAFC", "#F1F5F9"),  # Slate escuro
]


@dataclass
class Setor:
    nome: str
    icone: str
    cor: str          # hex principal
    bg: str           # hex fundo claro
    bg2: str          # hex fundo hover/ícone
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ordem: int = 0

    def dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "icone": self.icone,
            "cor": self.cor,
            "bg": self.bg,
            "bg2": self.bg2,
            "ordem": self.ordem,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Repositório (em memória — troque pela chamada ao backend Prisma)
# ─────────────────────────────────────────────────────────────────────────────

class SetorRepository:
    """
    Repositório singleton em memória.
    Para persistência real, substitua os métodos por chamadas REST/Prisma,
    mantendo a mesma interface.
    """

    _instance: Optional["SetorRepository"] = None

    def __new__(cls) -> "SetorRepository":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setores = cls._instance._seed()
        return cls._instance

    # ------------------------------------------------------------------
    # Seed — setores padrão (apenas na primeira instância)
    # ------------------------------------------------------------------
    @staticmethod
    def _seed() -> list[Setor]:
        dados = [
            ("Administração", "fa5s.building",    "#2563EB", "#EFF6FF", "#DBEAFE"),
            ("CD/Logística",  "fa5s.truck",        "#7C3AED", "#F5F3FF", "#EDE9FE"),
            ("Manutenção",    "fa5s.wrench",       "#D97706", "#FFFBEB", "#FEF3C7"),
            ("Meio Ambiente", "fa5s.leaf",         "#16A34A", "#F0FDF4", "#DCFCE7"),
            ("Qualidade",     "fa5s.flask",        "#0891B2", "#ECFEFF", "#CFFAFE"),
            ("Almoxarifado",  "fa5s.box",          "#DC2626", "#FEF2F2", "#FEE2E2"),
            ("SESMT",         "fa5s.hard-hat",     "#9333EA", "#FAF5FF", "#EDE9FE"),
            ("Projeto",       "fa5s.ruler",        "#059669", "#ECFDF5", "#D1FAE5"),
        ]
        return [
            Setor(nome=n, icone=ic, cor=c, bg=bg, bg2=bg2, ordem=i)
            for i, (n, ic, c, bg, bg2) in enumerate(dados)
        ]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def listar(self) -> list[Setor]:
        return sorted(self._setores, key=lambda s: s.ordem)

    def buscar(self, setor_id: str) -> Optional[Setor]:
        return next((s for s in self._setores if s.id == setor_id), None)

    def criar(self, setor: Setor) -> Setor:
        setor.ordem = max((s.ordem for s in self._setores), default=-1) + 1
        self._setores.append(setor)
        return setor

    def atualizar(self, setor_id: str, dados: dict) -> Optional[Setor]:
        setor = self.buscar(setor_id)
        if setor is None:
            return None
        for k, v in dados.items():
            if hasattr(setor, k):
                setattr(setor, k, v)
        return setor

    def excluir(self, setor_id: str) -> bool:
        antes = len(self._setores)
        self._setores = [s for s in self._setores if s.id != setor_id]
        return len(self._setores) < antes

    def mover(self, setor_id: str, nova_ordem: int) -> None:
        setor = self.buscar(setor_id)
        if setor is None:
            return
        setor.ordem = nova_ordem
        # Reindexar para evitar colisões
        for i, s in enumerate(self.listar()):
            s.ordem = i


# ─────────────────────────────────────────────────────────────────────────────
# Diálogo de Criação / Edição
# ─────────────────────────────────────────────────────────────────────────────

class SetorDialog(QDialog):
    """Modal para criar ou editar um setor."""

    def __init__(self, parent: QWidget = None, setor: Optional[Setor] = None):
        super().__init__(parent)
        self.setor = setor  # None → criar, não-None → editar
        self.cor_selecionada = setor.cor if setor else CORES_PREDEFINIDAS[0][0]
        self.bg_selecionado  = setor.bg  if setor else CORES_PREDEFINIDAS[0][1]
        self.bg2_selecionado = setor.bg2 if setor else CORES_PREDEFINIDAS[0][2]

        self.setWindowTitle("Novo Setor" if setor is None else "Editar Setor")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background: #F8FAFC; }
            QLabel  { color: #1A2B4A; font-size: 13px; }
            QLineEdit, QComboBox {
                background: white; border: 1.5px solid #E2E8F0;
                border-radius: 8px; padding: 8px 12px;
                font-size: 13px; color: #1A2B4A;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #2563EB; }
        """)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # ── Nome ──────────────────────────────────────────────────────
        root.addWidget(self._label("Nome do Setor *"))
        self.inp_nome = QLineEdit()
        self.inp_nome.setPlaceholderText("Ex.: Segurança do Trabalho")
        if self.setor:
            self.inp_nome.setText(self.setor.nome)
        root.addWidget(self.inp_nome)

        # ── Ícone ─────────────────────────────────────────────────────
        root.addWidget(self._label("Ícone"))
        self.cmb_icone = QComboBox()
        for icone_id, icone_label in ICONES_DISPONIVEIS:
            self.cmb_icone.addItem(
                qta.icon(icone_id, color="#2563EB"),
                icone_label,
                icone_id,
            )
        if self.setor:
            idx = next(
                (i for i, (id_, _) in enumerate(ICONES_DISPONIVEIS) if id_ == self.setor.icone),
                0,
            )
            self.cmb_icone.setCurrentIndex(idx)
        root.addWidget(self.cmb_icone)

        # ── Cor ───────────────────────────────────────────────────────
        root.addWidget(self._label("Cor do Setor"))
        root.addLayout(self._build_paleta())

        # ── Pré-visualização ──────────────────────────────────────────
        root.addWidget(self._label("Pré-visualização"))
        self.preview = self._build_preview()
        root.addWidget(self.preview)
        self.cmb_icone.currentIndexChanged.connect(self._atualizar_preview)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        root.addWidget(sep)

        # ── Botões ────────────────────────────────────────────────────
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Salvar")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        btns.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background: #16A34A; color: white; border: none;
                border-radius: 8px; padding: 8px 20px; font-weight: bold;
            }
            QPushButton:hover { background: #15803D; }
        """)
        btns.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background: #F1F5F9; color: #64748B;
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 8px 20px; font-weight: bold;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        btns.accepted.connect(self._validar_e_aceitar)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _label(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #64748B; margin-bottom: 0;")
        return lbl

    def _build_paleta(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self._btn_cores: list[QPushButton] = []

        for cor, bg, bg2 in CORES_PREDEFINIDAS:
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {cor}; border-radius: 14px; border: 2px solid transparent;
                }}
                QPushButton:hover {{ border: 2px solid #1A2B4A; }}
            """)
            btn.clicked.connect(lambda _, c=cor, b=bg, b2=bg2: self._selecionar_cor(c, b, b2))
            row.addWidget(btn)
            self._btn_cores.append(btn)

        # Botão cor customizada
        btn_custom = QPushButton("…")
        btn_custom.setFixedSize(28, 28)
        btn_custom.setCursor(Qt.PointingHandCursor)
        btn_custom.setToolTip("Cor personalizada")
        btn_custom.setStyleSheet("""
            QPushButton {
                background: #E2E8F0; border-radius: 14px;
                border: none; font-size: 14px; color: #64748B;
            }
            QPushButton:hover { background: #CBD5E1; }
        """)
        btn_custom.clicked.connect(self._cor_customizada)
        row.addWidget(btn_custom)
        row.addStretch()

        # Marcar cor atual se vier de um setor existente
        if self.setor:
            self._selecionar_cor(self.setor.cor, self.setor.bg, self.setor.bg2)

        return row

    def _selecionar_cor(self, cor: str, bg: str, bg2: str):
        self.cor_selecionada = cor
        self.bg_selecionado  = bg
        self.bg2_selecionado = bg2
        self._atualizar_preview()

    def _cor_customizada(self):
        c = QColorDialog.getColor(QColor(self.cor_selecionada), self, "Escolha a cor")
        if c.isValid():
            hex_cor = c.name()
            # Gerar tons automáticos (clareados)
            r, g, b = c.red(), c.green(), c.blue()
            bg  = f"#{min(r+180,255):02X}{min(g+180,255):02X}{min(b+180,255):02X}"
            bg2 = f"#{min(r+140,255):02X}{min(g+140,255):02X}{min(b+140,255):02X}"
            self._selecionar_cor(hex_cor, bg, bg2)

    def _build_preview(self) -> QWidget:
        container = QWidget()
        container.setFixedHeight(70)
        container.setStyleSheet(f"background: {self.bg_selecionado}; border-radius: 12px;")

        row = QHBoxLayout(container)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(12)

        circulo = QWidget()
        circulo.setFixedSize(40, 40)
        circulo.setStyleSheet(f"background: {self.bg2_selecionado}; border-radius: 20px;")
        cl = QHBoxLayout(circulo)
        cl.setContentsMargins(0, 0, 0, 0)

        self._preview_ic = QLabel()
        icone_atual = self.cmb_icone.currentData() if hasattr(self, "cmb_icone") else "fa5s.building"
        self._preview_ic.setPixmap(qta.icon(icone_atual, color=self.cor_selecionada).pixmap(20, 20))
        self._preview_ic.setAlignment(Qt.AlignCenter)
        self._preview_ic.setStyleSheet("background: transparent;")
        cl.addWidget(self._preview_ic)
        row.addWidget(circulo)

        self._preview_nome = QLabel(
            self.inp_nome.text() if hasattr(self, "inp_nome") and self.inp_nome.text()
            else "Nome do Setor"
        )
        self._preview_nome.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {self.cor_selecionada}; background: transparent;"
        )
        self.inp_nome.textChanged.connect(lambda t: self._preview_nome.setText(t or "Nome do Setor"))
        row.addWidget(self._preview_nome)
        row.addStretch()

        seta = QLabel("›")
        seta.setStyleSheet(f"font-size: 22px; color: {self.cor_selecionada}; background: transparent;")
        row.addWidget(seta)

        return container

    def _atualizar_preview(self):
        """Recria o preview com as cores e ícone atuais."""
        cor = self.cor_selecionada
        bg  = self.bg_selecionado
        bg2 = self.bg2_selecionado
        icone_id = self.cmb_icone.currentData()

        self.preview.setStyleSheet(f"background: {bg}; border-radius: 12px;")

        circulo = self.preview.findChild(QWidget)
        if circulo:
            circulo.setStyleSheet(f"background: {bg2}; border-radius: 20px;")

        self._preview_ic.setPixmap(qta.icon(icone_id, color=cor).pixmap(20, 20))
        self._preview_nome.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {cor}; background: transparent;"
        )

    # ------------------------------------------------------------------
    def _validar_e_aceitar(self):
        nome = self.inp_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do setor.")
            self.inp_nome.setFocus()
            return
        self.accept()

    # ------------------------------------------------------------------
    def resultado(self) -> dict:
        """Retorna os dados preenchidos pelo usuário."""
        return {
            "nome":  self.inp_nome.text().strip(),
            "icone": self.cmb_icone.currentData(),
            "cor":   self.cor_selecionada,
            "bg":    self.bg_selecionado,
            "bg2":   self.bg2_selecionado,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Guard de Role
# ─────────────────────────────────────────────────────────────────────────────

def _is_admin(role: str) -> bool:
    """Retorna True apenas para o perfil ADMINISTRATIVO."""
    return role.strip().upper() == "ADMINISTRATIVO"


# ─────────────────────────────────────────────────────────────────────────────
# SetoresPage
# ─────────────────────────────────────────────────────────────────────────────

class SetoresPage(QWidget):
    """
    Página de setores com CRUD completo.

    Parâmetros
    ----------
    user_role : str
        Role do usuário logado. Apenas "ADMINISTRATIVO" acessa
        as ações de criar, editar e excluir setores.
    """

    navegar = Signal(str)
    voltar  = Signal()

    def __init__(self, user_role: str = "ADMINISTRATIVO"):
        super().__init__()
        self.user_role = user_role
        self.repo = SetorRepository()
        self.setStyleSheet("background-color: #F0F4F8;")
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI principal
    # ------------------------------------------------------------------
    def _setup_ui(self):
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(32, 24, 32, 24)
        self._root_layout.setSpacing(16)

        self._root_layout.addLayout(self._build_header())
        self._root_layout.addWidget(self._separador())

        # Scroll para o grid de cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")
        self._root_layout.addWidget(self._scroll)

        self._renderizar_grid()

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()

        btn_voltar = self._btn_voltar()
        btn_voltar.clicked.connect(self.voltar.emit)
        header.addWidget(btn_voltar)
        header.addStretch()

        titulo = QLabel("Setores")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A2B4A;")
        header.addWidget(titulo)
        header.addStretch()

        # Botão "Novo Setor" — visível APENAS para ADMINISTRATIVO
        if _is_admin(self.user_role):
            btn_novo = QPushButton("  Novo Setor")
            btn_novo.setIcon(qta.icon("fa5s.plus", color="white"))
            btn_novo.setIconSize(QSize(13, 13))
            btn_novo.setCursor(Qt.PointingHandCursor)
            btn_novo.setStyleSheet("""
                QPushButton {
                    background-color: #16A34A; color: white;
                    border: none; border-radius: 8px;
                    padding: 8px 18px; font-weight: bold; font-size: 13px;
                }
                QPushButton:hover { background-color: #15803D; }
            """)
            btn_novo.clicked.connect(self._acao_criar)
            header.addWidget(btn_novo)

        return header

    def _separador(self) -> QWidget:
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #E2E8F0;")
        return sep

    # ------------------------------------------------------------------
    # Renderização do grid de cards
    # ------------------------------------------------------------------
    def _renderizar_grid(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 8, 0, 8)

        setores = self.repo.listar()

        if not setores:
            msg = QLabel("Nenhum setor cadastrado.\nClique em Novo Setor para começar.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #94A3B8; font-size: 15px;")
            grid.addWidget(msg, 0, 0)
        else:
            colunas = 4
            for i, setor in enumerate(setores):
                card = self._criar_card(setor)
                grid.addWidget(card, i // colunas, i % colunas)

        self._scroll.setWidget(container)

    # ------------------------------------------------------------------
    # Card de setor
    # ------------------------------------------------------------------
    def _criar_card(self, setor: Setor) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        # ── Botão principal (navegar) ──────────────────────────────────
        btn = QPushButton()
        btn.setFixedHeight(110)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {setor.bg};
                border-radius: 14px;
                text-align: left;
                border: 1.5px solid transparent;
            }}
            QPushButton:hover {{
                background: white;
                border: 1.5px solid {setor.cor};
            }}
            QPushButton:pressed {{ background: {setor.bg}; }}
        """)

        row = QHBoxLayout(btn)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(14)

        # Círculo ícone
        circulo = QWidget()
        circulo.setFixedSize(48, 48)
        circulo.setStyleSheet(f"background: {setor.bg2}; border-radius: 24px; border: none;")
        circulo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cl = QHBoxLayout(circulo)
        cl.setContentsMargins(0, 0, 0, 0)
        ic = QLabel()
        ic.setPixmap(qta.icon(setor.icone, color=setor.cor).pixmap(22, 22))
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("background: transparent; border: none;")
        cl.addWidget(ic)
        row.addWidget(circulo)

        lbl = QLabel(setor.nome)
        lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {setor.cor};"
            " background: transparent; border: none;"
        )
        row.addWidget(lbl)
        row.addStretch()

        seta = QLabel("›")
        seta.setStyleSheet(f"font-size: 22px; color: {setor.cor}; background: transparent; border: none;")
        row.addWidget(seta)

        btn.clicked.connect(
            lambda _, nome=setor.nome: self.navegar.emit(f"setor:{nome.upper()}")
        )
        vbox.addWidget(btn)

        # ── Ações CRUD (apenas ADMINISTRATIVO) ────────────────────────
        if _is_admin(self.user_role):
            acoes = QHBoxLayout()
            acoes.setSpacing(6)
            acoes.setContentsMargins(4, 0, 4, 0)

            btn_editar  = self._btn_acao("fa5s.pen",        "#2563EB", "Editar")
            btn_excluir = self._btn_acao("fa5s.trash-alt",  "#DC2626", "Excluir")

            btn_editar.clicked.connect(lambda _, s=setor: self._acao_editar(s))
            btn_excluir.clicked.connect(lambda _, s=setor: self._acao_excluir(s))

            acoes.addWidget(btn_editar)
            acoes.addWidget(btn_excluir)
            acoes.addStretch()
            vbox.addLayout(acoes)

        return wrapper

    def _btn_acao(self, icone: str, cor: str, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(qta.icon(icone, color=cor))
        btn.setIconSize(QSize(13, 13))
        btn.setFixedSize(28, 24)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: white; border: 1px solid #E2E8F0;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: #F8FAFC; border-color: {cor}; }}
        """)
        return btn

    # ------------------------------------------------------------------
    # Ações CRUD
    # ------------------------------------------------------------------
    def _acao_criar(self):
        dlg = SetorDialog(self)
        if dlg.exec() == QDialog.Accepted:
            dados = dlg.resultado()
            novo = Setor(**dados)
            self.repo.criar(novo)
            self._renderizar_grid()

    def _acao_editar(self, setor: Setor):
        dlg = SetorDialog(self, setor=setor)
        if dlg.exec() == QDialog.Accepted:
            self.repo.atualizar(setor.id, dlg.resultado())
            self._renderizar_grid()

    def _acao_excluir(self, setor: Setor):
        resp = QMessageBox.question(
            self,
            "Excluir Setor",
            f'Tem certeza que deseja excluir o setor "{setor.nome}"?\n'
            "Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.repo.excluir(setor.id)
            self._renderizar_grid()

    # ------------------------------------------------------------------
    # Componentes utilitários
    # ------------------------------------------------------------------
    def _btn_voltar(self) -> QPushButton:
        btn = QPushButton("  Voltar")
        btn.setIcon(qta.icon("fa5s.arrow-left", color="#64748B"))
        btn.setIconSize(QSize(13, 13))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #F1F5F9; color: #64748B;
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        return btn


# ─────────────────────────────────────────────────────────────────────────────
# EmpresasPage (inalterada, mantida aqui para não quebrar imports existentes)
# ─────────────────────────────────────────────────────────────────────────────

class EmpresasPage(QWidget):
    navegar = Signal(str)
    voltar  = Signal()

    def __init__(self, setor_nome: str = "", empresas: list = None):
        super().__init__()
        self.setor_nome = setor_nome
        self.empresas = empresas or []
        self.setStyleSheet("background-color: #F0F4F8;")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        btn_voltar = self._btn_voltar()
        btn_voltar.clicked.connect(self.voltar.emit)
        header.addWidget(btn_voltar)
        header.addStretch()

        titulo = QLabel(f"Empresas — {self.setor_nome.title()}")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A2B4A;")
        header.addWidget(titulo)
        header.addStretch()

        btn_nova = QPushButton("  Nova Empresa")
        btn_nova.setIcon(qta.icon("fa5s.plus", color="white"))
        btn_nova.setIconSize(QSize(13, 13))
        btn_nova.setCursor(Qt.PointingHandCursor)
        btn_nova.setStyleSheet("""
            QPushButton {
                background-color: #16A34A; color: white;
                border: none; border-radius: 8px;
                padding: 8px 18px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #15803D; }
        """)
        btn_nova.clicked.connect(lambda: self.navegar.emit("nova_empresa"))
        header.addWidget(btn_nova)
        layout.addLayout(header)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #E2E8F0;")
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 8, 0, 8)

        if not self.empresas:
            msg = QLabel("Nenhuma empresa cadastrada.\nClique em Nova Empresa para começar.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #94A3B8; font-size: 15px;")
            grid.addWidget(msg, 0, 0)
        else:
            for i, empresa in enumerate(self.empresas):
                card = self._criar_card_empresa(empresa)
                grid.addWidget(card, i // 3, i % 3)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _criar_card_empresa(self, empresa) -> QPushButton:
        nome      = empresa.razao_social if hasattr(empresa, "razao_social") else str(empresa)
        cnpj      = empresa.cnpj         if hasattr(empresa, "cnpj")         else ""
        empresa_id = empresa.id           if hasattr(empresa, "id")           else 0

        btn = QPushButton()
        btn.setFixedHeight(80)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1.5px solid #E2E8F0;
                border-radius: 12px; text-align: left; padding: 0 16px;
            }
            QPushButton:hover { border: 1.5px solid #2563EB; background: #EFF6FF; }
        """)

        row = QHBoxLayout(btn)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(14)

        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.building", color="#2563EB").pixmap(22, 22))
        ic.setStyleSheet("background: transparent; border: none;")
        row.addWidget(ic)

        txt = QVBoxLayout()
        txt.setSpacing(2)
        lbl_nome = QLabel(nome)
        lbl_nome.setStyleSheet("font-size: 13px; font-weight: bold; color: #1A2B4A; background: transparent; border: none;")
        txt.addWidget(lbl_nome)
        lbl_cnpj = QLabel(cnpj)
        lbl_cnpj.setStyleSheet("font-size: 11px; color: #94A3B8; background: transparent; border: none;")
        txt.addWidget(lbl_cnpj)
        row.addLayout(txt)
        row.addStretch()

        seta = QLabel("›")
        seta.setStyleSheet("font-size: 20px; color: #CBD5E1; background: transparent; border: none;")
        row.addWidget(seta)

        btn.clicked.connect(
            lambda _, eid=empresa_id, sn=self.setor_nome:
            self.navegar.emit(f"empresa_detalhe:{eid}|{sn}")
        )
        return btn

    def _btn_voltar(self) -> QPushButton:
        btn = QPushButton("  Voltar")
        btn.setIcon(qta.icon("fa5s.arrow-left", color="#64748B"))
        btn.setIconSize(QSize(13, 13))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #F1F5F9; color: #64748B;
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        return btn