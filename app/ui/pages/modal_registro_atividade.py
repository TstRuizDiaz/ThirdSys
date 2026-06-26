"""
app/ui/pages/modal_registro_atividade.py
────────────────────────────────────────────────────────────────────────────────
Modal exibido ao clicar em "Liberar Entrada".

Comportamento por tipo de empresa (Empresa.tipo_empresa):
- "flutuante": exige descrição da atividade, permite adicionar várias
  pessoas à mesma atividade, e GRAVA um registro de Atividade no banco
  (é esse registro que alimenta o card/contador "Atividades hoje").
- "fixa": não exige descrição, não mostra a opção de adicionar mais
  pessoas (entrada é individual) e NÃO grava Atividade — por isso não
  aparece em "Atividades hoje".

Também inclui o toggle "Possui veículo?" — se marcado "Sim", abre o
ModalVeiculo (definido em portaria_page.py) ao confirmar, para cadastrar
a entrada do veículo junto com a liberação do colaborador.
"""
from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QScrollArea, QTextEdit,
    QVBoxLayout, QWidget,
)

import qtawesome as qta

COR_BG             = "#F2F5F8"
COR_CARD_BG        = "#FFFFFF"
COR_CARD_BORDA     = "#DDE3EA"
COR_TITULO         = "#1C2B3A"
COR_SUBTITULO      = "#5A7A96"
COR_SEPARADOR      = "#DDE3EA"
COR_SECAO_LABEL    = "#8AA5BC"
COR_TEXTO_NORMAL   = "#374151"
COR_SB_ACENTO      = "#3B7DD8"
COR_SB_SUBTEXTO    = "#6B8FAD"
COR_VERDE_BG       = "#F0FAF4"
COR_VERDE_BORDA    = "#86EFAC"
COR_VERDE_TEXTO    = "#166634"
COR_VERMELHO_BG    = "#FEF2F2"
COR_VERMELHO_BORDA = "#FCA5A5"
COR_VERMELHO_TEXTO = "#991B1B"
COR_AZUL_BG        = "#EFF6FF"
COR_AZUL_BORDA     = "#93C5FD"
COR_AZUL_TEXTO     = "#1E40AF"
COR_AMARELO_BG     = "#FFFBEB"
COR_AMARELO_BORDA  = "#FCD34D"
COR_AMARELO_TEXTO  = "#92400E"
COR_CIANO          = "#0891B2"


def _sep() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
    return f

def _secao(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setStyleSheet(
        f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL};"
        " background: transparent; border: none; letter-spacing: 1.4px;"
    )
    return lbl


# ── Chip ──────────────────────────────────────────────────────────────────────

class ChipColab(QFrame):
    removido = Signal(int)

    def __init__(self, trabalhador_id: int, nome: str, empresa: str,
                 principal: bool = False, parent=None):
        super().__init__(parent)
        self.trabalhador_id = trabalhador_id
        cor_bg    = COR_VERDE_BG    if principal else COR_AZUL_BG
        cor_borda = COR_VERDE_BORDA if principal else COR_AZUL_BORDA
        cor_txt   = COR_VERDE_TEXTO if principal else COR_AZUL_TEXTO
        self.setStyleSheet(f"""
            QFrame {{ background: {cor_bg}; border: 1px solid {cor_borda}; border-radius: 14px; }}
            QLabel {{ border: none; background: transparent; color: {cor_txt}; }}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(8,4,6,4); lay.setSpacing(5)
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user", color=cor_txt).pixmap(11,11))
        ic.setStyleSheet("background: transparent; border: none;"); lay.addWidget(ic, alignment=Qt.AlignVCenter)
        vl = QVBoxLayout(); vl.setSpacing(0); vl.setContentsMargins(0,0,0,0)
        lbl_n = QLabel(nome); lbl_n.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {cor_txt};")
        lbl_e = QLabel(empresa); lbl_e.setStyleSheet(f"font-size: 9px; color: {cor_txt};")
        vl.addWidget(lbl_n); vl.addWidget(lbl_e); lay.addLayout(vl)
        if principal:
            b = QLabel("Principal")
            b.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COR_VERDE_TEXTO};"
                            f" background: {COR_VERDE_BORDA}; border-radius: 3px; padding: 1px 5px;")
            lay.addWidget(b, alignment=Qt.AlignVCenter)
        else:
            btn = QPushButton(); btn.setIcon(qta.icon("fa5s.times", color=cor_txt))
            btn.setIconSize(QSize(9,9)); btn.setFixedSize(20,20); btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 10px; }}"
                              f"QPushButton:hover {{ background: {cor_borda}; }}")
            btn.clicked.connect(lambda: self.removido.emit(self.trabalhador_id))
            lay.addWidget(btn, alignment=Qt.AlignVCenter)


# ── Item resultado ────────────────────────────────────────────────────────────

class ItemResultado(QFrame):
    selecionado = Signal(dict)

    def __init__(self, dados: dict, parent=None):
        super().__init__(parent)
        self._dados = dados
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border-bottom: 1px solid {COR_CARD_BORDA}; }}
            QFrame:hover {{ background: {COR_AZUL_BG}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(12,8,12,8); lay.setSpacing(10)
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user-circle", color=COR_SB_SUBTEXTO).pixmap(20,20))
        ic.setStyleSheet("background: transparent; border: none;"); lay.addWidget(ic, alignment=Qt.AlignVCenter)
        vl = QVBoxLayout(); vl.setSpacing(1); vl.setContentsMargins(0,0,0,0)
        lbl_n = QLabel(dados["nome"]); lbl_n.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {COR_TITULO};")
        info = f"{dados['empresa']}  •  {dados['funcao']}"
        cor_i = COR_AMARELO_TEXTO
        if dados.get("dentro"):
            info += "  ⚠ já dentro da planta"
        else:
            cor_i = COR_SUBTITULO
        lbl_i = QLabel(info); lbl_i.setStyleSheet(f"font-size: 10px; color: {cor_i};")
        vl.addWidget(lbl_n); vl.addWidget(lbl_i); lay.addLayout(vl, 1)
        ic2 = QLabel(); ic2.setPixmap(qta.icon("fa5s.plus-circle", color=COR_SB_ACENTO).pixmap(14,14))
        ic2.setStyleSheet("background: transparent; border: none;"); lay.addWidget(ic2, alignment=Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.selecionado.emit(self._dados)
        super().mousePressEvent(event)


# ── Toggle Sim/Não genérico (usado para "Possui veículo?") ───────────────────

class _ToggleSimNao:
    """Dois QPushButton como seleção exclusiva, sem setCheckable (evita loops)."""

    _ESTILO_BASE   = "QPushButton {{ border-radius: 7px; font-size: 12px; font-weight: bold; padding: 6px 16px; border: none; background-color: {bg}; color: {cor}; }}"

    def __init__(self, label_sim="Sim", label_nao="Não", cor_ativo=COR_CIANO):
        self._valor = False  # False = Não
        self._cor_ativo = cor_ativo

        self.btn_sim = QPushButton(f"  {label_sim}")
        self.btn_sim.setIcon(qta.icon("fa5s.check", color="#94A3B8"))
        self.btn_sim.setIconSize(QSize(11, 11))
        self.btn_sim.setCursor(Qt.PointingHandCursor)

        self.btn_nao = QPushButton(f"  {label_nao}")
        self.btn_nao.setIcon(qta.icon("fa5s.times", color="white"))
        self.btn_nao.setIconSize(QSize(11, 11))
        self.btn_nao.setCursor(Qt.PointingHandCursor)

        self.btn_sim.clicked.connect(lambda: self.selecionar(True))
        self.btn_nao.clicked.connect(lambda: self.selecionar(False))
        self.selecionar(False)

    def selecionar(self, valor: bool):
        self._valor = valor
        ativo   = self._ESTILO_BASE.format(bg=self._cor_ativo, cor="white")
        inativo = self._ESTILO_BASE.format(bg="transparent",   cor="#94A3B8")
        if valor:
            self.btn_sim.setStyleSheet(ativo)
            self.btn_sim.setIcon(qta.icon("fa5s.check", color="white"))
            self.btn_nao.setStyleSheet(inativo)
            self.btn_nao.setIcon(qta.icon("fa5s.times", color="#94A3B8"))
        else:
            self.btn_nao.setStyleSheet(self._ESTILO_BASE.format(bg="#DC2626", cor="white"))
            self.btn_nao.setIcon(qta.icon("fa5s.times", color="white"))
            self.btn_sim.setStyleSheet(inativo)
            self.btn_sim.setIcon(qta.icon("fa5s.check", color="#94A3B8"))

    def valor(self) -> bool:
        return self._valor

    def widget(self) -> QFrame:
        container = QFrame()
        container.setFixedHeight(44)
        container.setStyleSheet(
            "QFrame { background-color: #F1F5F9; border-radius: 10px; border: 1px solid #E2E8F0; }"
        )
        inner = QHBoxLayout(container)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(4)
        inner.addWidget(self.btn_sim)
        inner.addWidget(self.btn_nao)
        return container


# ── Modal ─────────────────────────────────────────────────────────────────────

class ModalRegistroAtividade(QDialog):
    confirmado = Signal(list, str)   # (lista de trabalhador_ids, descricao)

    def __init__(self, colab_principal: dict, parent=None):
        super().__init__(parent)
        self._principal = colab_principal
        self._selecionados: dict[int, dict] = {colab_principal["id"]: colab_principal}

        self.setWindowTitle("Registrar Entrada / Atividade")
        self.setWindowFlag(Qt.Window)
        self.setModal(True)
        self.setMinimumSize(580, 640)
        self.resize(620, 680)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
            QWidget {{ border: none; }}
        """)

        self._principal_ja_dentro = self._verificar_dentro(colab_principal["id"])
        # "fixa" ou "flutuante" — definida na Ficha da Empresa.
        # Empresa flutuante = exige descrição + permite multi-seleção +
        # gera Atividade (conta em "Atividades hoje"). Empresa fixa não.
        self._tipo_empresa = self._buscar_tipo_empresa(colab_principal["id"])
        self._setup_ui()

    # ── Verificações ──────────────────────────────────────────────────────────

    def _verificar_dentro(self, trabalhador_id: int) -> bool:
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from sqlalchemy import func
            hoje   = date.today()
            inicio = datetime.combine(hoje, datetime.min.time())
            session = get_session()
            ultima = (session.query(func.max(Acesso.horario))
                      .filter(Acesso.trabalhador_id == trabalhador_id,
                              Acesso.horario >= inicio).scalar())
            if not ultima: session.close(); return False
            ult = session.query(Acesso).filter(
                Acesso.trabalhador_id == trabalhador_id,
                Acesso.horario == ultima).first()
            session.close()
            return ult is not None and ult.tipo == "entrada"
        except Exception:
            return False

    def _buscar_tipo_empresa(self, trabalhador_id: int) -> str:
        """Lê Empresa.tipo_empresa do colaborador principal. 'fixa' por padrão
        (inclusive se a empresa não tiver essa coluna preenchida ainda)."""
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            session = get_session()
            t = session.get(Trabalhador, trabalhador_id)
            tipo = "fixa"
            if t and t.empresa and getattr(t.empresa, "tipo_empresa", None):
                tipo = t.empresa.tipo_empresa
            session.close()
            return tipo
        except Exception:
            return "fixa"

    # ── UI ────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        eh_flutuante = self._tipo_empresa == "flutuante"

        raiz = QVBoxLayout(self); raiz.setContentsMargins(28,24,28,24); raiz.setSpacing(16)

        # Cabeçalho
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.clipboard-check", color=COR_SB_ACENTO).pixmap(20,20))
        ic.setStyleSheet("background: transparent; border: none;"); topo.addWidget(ic)
        vl = QVBoxLayout(); vl.setSpacing(2)
        lbl_t = QLabel("Registrar Entrada / Atividade")
        lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        lbl_s = QLabel(
            "Descreva a atividade e confirme quem está entrando na planta"
            if eh_flutuante else
            "Confirme a liberação de entrada"
        )
        lbl_s.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(lbl_t); vl.addWidget(lbl_s); topo.addLayout(vl); topo.addStretch()

        # Badge do tipo de empresa, só pra deixar visualmente claro
        badge = QLabel("  Empresa Flutuante" if eh_flutuante else "  Empresa Fixa")
        badge.setStyleSheet(f"""
            font-size: 10px; font-weight: bold;
            color: {'#7C3AED' if eh_flutuante else '#2563EB'};
            background: {'#F5F3FF' if eh_flutuante else '#EFF6FF'};
            border: 1px solid {'#DDD6FE' if eh_flutuante else '#BFDBFE'};
            border-radius: 10px; padding: 4px 10px;
        """)
        topo.addWidget(badge, alignment=Qt.AlignVCenter)

        btn_x = QPushButton(); btn_x.setIcon(qta.icon("fa5s.times", color=COR_SUBTITULO))
        btn_x.setIconSize(QSize(12,12)); btn_x.setFixedSize(30,30); btn_x.setCursor(Qt.PointingHandCursor)
        btn_x.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_x.clicked.connect(self.reject); topo.addWidget(btn_x, alignment=Qt.AlignTop)
        raiz.addLayout(topo)

        # Aviso principal já dentro
        if self._principal_ja_dentro:
            fa = QFrame(); fa.setStyleSheet(f"""
                QFrame {{ background: {COR_VERMELHO_BG}; border: 1px solid {COR_VERMELHO_BORDA};
                          border-left: 4px solid {COR_VERMELHO_TEXTO}; border-radius: 4px; }}
                QLabel {{ border: none; background: transparent; }}
            """)
            al = QHBoxLayout(fa); al.setContentsMargins(12,10,12,10); al.setSpacing(8)
            ia = QLabel(); ia.setPixmap(qta.icon("fa5s.exclamation-circle", color=COR_VERMELHO_TEXTO).pixmap(16,16))
            ia.setStyleSheet("background: transparent; border: none;")
            la = QLabel(f"<b>{self._principal['nome']}</b> já está dentro da planta. "
                        "Registrar nova entrada pode gerar duplicidade.")
            la.setWordWrap(True); la.setStyleSheet(f"font-size: 11px; color: {COR_VERMELHO_TEXTO};")
            al.addWidget(ia, alignment=Qt.AlignTop); al.addWidget(la, 1)
            raiz.addWidget(fa)

        raiz.addWidget(_sep())

        # ── Descrição da atividade — SÓ para empresa flutuante ──────────────
        self._secao_descricao = _secao("DESCRIÇÃO DA ATIVIDADE")
        raiz.addWidget(self._secao_descricao)
        self._campo_atividade = QTextEdit()
        self._campo_atividade.setFixedHeight(78)
        self._campo_atividade.setPlaceholderText("Ex.: Manutenção preventiva nas caldeiras do setor B...")
        self._campo_atividade.setStyleSheet(f"""
            QTextEdit {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL};
                         border: 1.5px solid {COR_CARD_BORDA}; border-radius: 6px;
                         padding: 8px 10px; font-size: 12px; }}
            QTextEdit:focus {{ border-color: {COR_SB_ACENTO}; }}
        """)
        raiz.addWidget(self._campo_atividade)
        self._secao_descricao.setVisible(eh_flutuante)
        self._campo_atividade.setVisible(eh_flutuante)

        # Chips
        raiz.addWidget(_secao("PESSOAS NA ATIVIDADE"))
        self._area_chips = QScrollArea(); self._area_chips.setWidgetResizable(True)
        self._area_chips.setFixedHeight(90); self._area_chips.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._area_chips.setStyleSheet(f"""
            QScrollArea {{ background: {COR_CARD_BG}; border: 1.5px solid {COR_CARD_BORDA}; border-radius: 6px; }}
            QScrollBar:vertical {{ background: {COR_BG}; width: 5px; border-radius: 2px; }}
            QScrollBar::handle:vertical {{ background: {COR_CARD_BORDA}; border-radius: 2px; }}
        """)
        self._chips_widget = QWidget(); self._chips_widget.setStyleSheet("background: transparent; border: none;")
        self._chips_layout = QHBoxLayout(self._chips_widget)
        self._chips_layout.setContentsMargins(8,8,8,8); self._chips_layout.setSpacing(6)
        self._chips_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._chips_layout.addStretch()
        self._area_chips.setWidget(self._chips_widget)
        raiz.addWidget(self._area_chips)

        # ── Adicionar pessoas — SÓ para empresa flutuante ────────────────────
        # Empresa fixa = entrada individual, sem multi-seleção.
        self._frame_add = QFrame(); self._frame_add.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border: 1.5px solid {COR_CARD_BORDA}; border-radius: 8px; }}
            QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }}
        """)
        fl = QVBoxLayout(self._frame_add); fl.setContentsMargins(14,12,14,12); fl.setSpacing(8)
        topo_add = QHBoxLayout()
        ia2 = QLabel(); ia2.setPixmap(qta.icon("fa5s.user-plus", color=COR_SB_ACENTO).pixmap(13,13))
        ia2.setStyleSheet("background: transparent; border: none;")
        la2 = QLabel("Adicionar mais pessoas à atividade")
        la2.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {COR_TITULO};")
        topo_add.addWidget(ia2); topo_add.addWidget(la2); topo_add.addStretch()
        self._lbl_contador = QLabel("1 pessoa")
        self._lbl_contador.setStyleSheet(f"""
            font-size: 10px; font-weight: bold; color: {COR_SB_ACENTO};
            background: {COR_AZUL_BG}; border: 1px solid {COR_AZUL_BORDA};
            border-radius: 10px; padding: 2px 8px;
        """)
        topo_add.addWidget(self._lbl_contador); fl.addLayout(topo_add)

        br = QHBoxLayout(); br.setSpacing(6)
        is2 = QLabel(); is2.setPixmap(qta.icon("fa5s.search", color=COR_SB_SUBTEXTO).pixmap(12,12))
        is2.setStyleSheet("background: transparent; border: none;"); br.addWidget(is2)
        self._campo_busca = QLineEdit(); self._campo_busca.setPlaceholderText("Pesquisar por nome ou CPF…")
        self._campo_busca.setFixedHeight(34)
        self._campo_busca.setStyleSheet(f"""
            QLineEdit {{ background: {COR_BG}; color: {COR_TITULO}; border: 1px solid {COR_CARD_BORDA};
                         border-radius: 5px; padding: 0 10px; font-size: 12px; }}
            QLineEdit:focus {{ border-color: {COR_SB_ACENTO}; background: white; }}
        """)
        br.addWidget(self._campo_busca, 1); fl.addLayout(br)

        self._lista_resultados = QFrame(); self._lista_resultados.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 5px; }}
        """)
        self._lista_resultados.setVisible(False)
        self._layout_resultados = QVBoxLayout(self._lista_resultados)
        self._layout_resultados.setContentsMargins(0,0,0,0); self._layout_resultados.setSpacing(0)
        fl.addWidget(self._lista_resultados)
        raiz.addWidget(self._frame_add)
        self._frame_add.setVisible(eh_flutuante)

        # ── Possui veículo? — sempre visível, fixa ou flutuante ─────────────
        raiz.addWidget(_secao("VEÍCULO"))
        frame_veic = QFrame(); frame_veic.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border: 1.5px solid {COR_CARD_BORDA}; border-radius: 8px; }}
            QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }}
        """)
        fv = QHBoxLayout(frame_veic); fv.setContentsMargins(14, 10, 14, 10); fv.setSpacing(10)
        icv = QLabel(); icv.setPixmap(qta.icon("fa5s.car", color=COR_CIANO).pixmap(16, 16))
        icv.setStyleSheet("background: transparent; border: none;")
        lblv = QLabel("Possui veículo?")
        lblv.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COR_TITULO};")
        fv.addWidget(icv); fv.addWidget(lblv); fv.addStretch()
        self._toggle_veiculo = _ToggleSimNao(cor_ativo=COR_CIANO)
        fv.addWidget(self._toggle_veiculo.widget())
        raiz.addWidget(frame_veic)

        raiz.addStretch()

        self._timer_busca = QTimer(self); self._timer_busca.setSingleShot(True)
        self._timer_busca.setInterval(300); self._timer_busca.timeout.connect(self._executar_busca)
        self._campo_busca.textChanged.connect(self._on_texto_alterado)

        # Botões
        raiz.addWidget(_sep())
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = QPushButton("  Cancelar"); btn_c.setIcon(qta.icon("fa5s.times", color=COR_SUBTITULO))
        btn_c.setIconSize(QSize(11,11)); btn_c.setFixedHeight(40); btn_c.setCursor(Qt.PointingHandCursor)
        btn_c.setAutoDefault(False); btn_c.setDefault(False)
        btn_c.setStyleSheet(f"""
            QPushButton {{ background: {COR_CARD_BG}; color: {COR_SUBTITULO};
                           border: 1px solid {COR_CARD_BORDA}; border-radius: 5px; padding: 0 20px; font-size: 13px; }}
            QPushButton:hover {{ background: #EBF0F6; }}
        """)
        btn_c.clicked.connect(self.reject)
        self._btn_confirmar = QPushButton("  Confirmar Entrada")
        self._btn_confirmar.setIcon(qta.icon("fa5s.check", color="white"))
        self._btn_confirmar.setIconSize(QSize(13,13)); self._btn_confirmar.setFixedHeight(40)
        self._btn_confirmar.setCursor(Qt.PointingHandCursor)
        self._btn_confirmar.setAutoDefault(False); self._btn_confirmar.setDefault(False)
        self._btn_confirmar.setStyleSheet(f"""
            QPushButton {{ background: {COR_VERDE_TEXTO}; color: white; border: none; border-radius: 5px;
                           padding: 0 24px; font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background: #14532D; }}
            QPushButton:disabled {{ background: {COR_CARD_BORDA}; color: {COR_SECAO_LABEL}; }}
        """)
        self._btn_confirmar.clicked.connect(self._on_confirmar)
        btns.addWidget(btn_c); btns.addStretch(); btns.addWidget(self._btn_confirmar)
        raiz.addLayout(btns)

        # Chip principal — APÓS todos os widgets criados
        self._adicionar_chip(self._principal, principal=True)

    # ── Chips ─────────────────────────────────────────────────────────────────

    def _adicionar_chip(self, dados: dict, principal: bool = False):
        chip = ChipColab(dados["id"], dados["nome"], dados["empresa"], principal=principal)
        if not principal:
            chip.removido.connect(self._remover_colab)
        count = self._chips_layout.count()
        self._chips_layout.insertWidget(count - 1, chip)
        self._atualizar_contador()

    def _remover_colab(self, tid: int):
        if tid == self._principal["id"]: return
        self._selecionados.pop(tid, None)
        for i in range(self._chips_layout.count()):
            item = self._chips_layout.itemAt(i)
            if item and isinstance(item.widget(), ChipColab):
                chip: ChipColab = item.widget()
                if chip.trabalhador_id == tid:
                    chip.deleteLater(); break
        self._atualizar_contador()

    def _atualizar_contador(self):
        n = len(self._selecionados)
        self._lbl_contador.setText(f"{n} pessoa{'s' if n > 1 else ''}")

    # ── Busca ─────────────────────────────────────────────────────────────────

    def _on_texto_alterado(self, texto: str):
        if len(texto.strip()) < 2: self._lista_resultados.setVisible(False); return
        self._timer_busca.start()

    def _executar_busca(self):
        termo = self._campo_busca.text().strip()
        if len(termo) < 2: self._lista_resultados.setVisible(False); return
        resultados = self._buscar_colaboradores(termo)
        while self._layout_resultados.count():
            item = self._layout_resultados.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if not resultados:
            lbl = QLabel("Nenhum colaborador encontrado"); lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {COR_SECAO_LABEL}; font-size: 11px; padding: 12px;")
            self._layout_resultados.addWidget(lbl)
        else:
            for d in resultados[:8]:
                w = ItemResultado(d); w.selecionado.connect(self._on_selecionar_resultado)
                self._layout_resultados.addWidget(w)
        self._lista_resultados.setVisible(True)

    def _buscar_colaboradores(self, termo: str) -> list[dict]:
        result = []
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            session = get_session()
            q = (session.query(Trabalhador).filter(Trabalhador.ativo == True)
                 .filter(Trabalhador.nome.ilike(f"%{termo}%") | Trabalhador.cpf.contains(termo))
                 .limit(10).all())
            for t in q:
                if t.id == self._principal["id"]: continue
                emp = t.empresa.razao_social if t.empresa else "—"
                result.append({"id": t.id, "nome": t.nome, "empresa": emp,
                                "funcao": t.funcao or "—", "cpf": t.cpf or "—",
                                "dentro": self._verificar_dentro(t.id)})
            session.close()
        except Exception as e:
            print(f"[ModalRegistroAtividade] busca: {e}")
        return result

    def _on_selecionar_resultado(self, dados: dict):
        tid = dados["id"]
        if dados.get("dentro") and tid not in self._selecionados:
            QMessageBox.warning(self, "Colaborador já dentro",
                                f"<b>{dados['nome']}</b> já possui entrada registrada hoje.\n"
                                "Registre a saída antes de liberar nova entrada.")
            return
        if tid in self._selecionados:
            self._lista_resultados.setVisible(False); self._campo_busca.clear(); return
        self._selecionados[tid] = dados
        self._adicionar_chip(dados)
        self._lista_resultados.setVisible(False); self._campo_busca.clear()

    # ── Confirmação + salvar Atividade ────────────────────────────────────────

    def _on_confirmar(self):
        if self._principal_ja_dentro:
            r = QMessageBox.warning(self, "Colaborador já dentro",
                                    f"<b>{self._principal['nome']}</b> já está dentro da planta.\n"
                                    "Deseja registrar mesmo assim?",
                                    QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if r != QMessageBox.Yes: return

        eh_flutuante = self._tipo_empresa == "flutuante"

        descricao = ""
        if eh_flutuante:
            descricao = self._campo_atividade.toPlainText().strip()
            if not descricao:
                QMessageBox.warning(self, "Campo obrigatório",
                                    "Por favor, descreva a atividade antes de confirmar.")
                return
            ids = list(self._selecionados.keys())
        else:
            # Empresa fixa: entrada individual, sem atividade registrada.
            ids = [self._principal["id"]]

        # CORREÇÃO: o cadastro do veículo (quando "Possui veículo? = Sim")
        # agora é resolvido ANTES de qualquer gravação no banco (Atividade)
        # e antes de confirmar/aceitar este modal. Antes, a Atividade já
        # era salva e a entrada já era liberada (confirmado.emit + accept())
        # independentemente do usuário ter cancelado o ModalVeiculo — ou
        # seja, "Cancelar" no veículo não cancelava a liberação. Agora, se
        # o usuário marcou "Sim" e cancela o cadastro do veículo, a
        # liberação inteira é abortada (nada é salvo, nada é emitido).
        if self._toggle_veiculo.valor():
            if not self._abrir_modal_veiculo():
                return  # veículo cancelado/não cadastrado -> cancela tudo

        if eh_flutuante:
            # Só empresa flutuante gera Atividade -> só ela conta em
            # "Atividades hoje" no dashboard da portaria. Salva só agora,
            # depois do veículo confirmado (ou de não ser necessário).
            self._salvar_atividade(descricao)

        self.confirmado.emit(ids, descricao)
        self.accept()

    def _abrir_modal_veiculo(self) -> bool:
        """Abre o ModalVeiculo (definido em portaria_page.py) pré-preenchido
        com o nome/empresa do colaborador principal, pra cadastrar a entrada
        do veículo junto da liberação de acesso.

        Retorna True se o veículo foi cadastrado com sucesso (usuário
        confirmou o ModalVeiculo), e False se o usuário cancelou — nesse
        caso, quem chamou esta função deve abortar toda a liberação."""
        try:
            from app.ui.pages.portaria_page import ModalVeiculo, VeiculoDTO
            dto = VeiculoDTO(
                motorista=self._principal.get("nome", ""),
                empresa=self._principal.get("empresa", ""),
            )
            modal = ModalVeiculo(dto=dto, parent=self.parent() or self)
            # dto criado aqui não tem id -> ModalVeiculo trata como nova entrada
            modal._is_new = True
            resultado = modal.exec()
            return resultado == QDialog.Accepted
        except Exception as e:
            print(f"[ModalRegistroAtividade] abrir modal veiculo: {e}")
            r = QMessageBox.question(
                self, "Veículo",
                "Não foi possível abrir o cadastro de veículo agora.\n"
                "Deseja continuar a liberação de entrada SEM cadastrar o veículo?",
                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
            )
            return r == QMessageBox.Yes

    def _salvar_atividade(self, descricao: str):
        """Persiste Atividade + AtividadeParticipante no banco.
        Chamado apenas para empresas flutuantes (ver _on_confirmar)."""
        try:
            from app.core.database import get_session
            from app.models.atividade import Atividade, AtividadeParticipante
            from app.core.session_manager import carregar_sessao

            sessao   = carregar_sessao()
            # CORREÇÃO: era sessao["username"] -> KeyError, pois a sessão
            # salva no login só tem usuario_id/email/token/cnpj.
            operador = (sessao.get("username") or sessao.get("email") or "portaria") if sessao else "portaria"
            setor    = self._principal.get("empresa", "—")

            session = get_session()
            ativ = Atividade(
                descricao=descricao,
                setor=setor,
                operador=operador,
                data_inicio=datetime.now(),
            )
            session.add(ativ)
            session.flush()   # gera ativ.id antes do commit

            for tid in self._selecionados:
                session.add(AtividadeParticipante(
                    atividade_id=ativ.id,
                    trabalhador_id=tid,
                ))

            session.commit()
            session.close()
        except Exception as e:
            print(f"[ModalRegistroAtividade] salvar atividade: {e}")