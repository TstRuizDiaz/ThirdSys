from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QMessageBox, QScrollArea,
    QDialog, QPushButton, QLineEdit, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QColor
import qtawesome as qta
from datetime import date, datetime, timedelta

# ── Paleta corporativa ───────────────────────────────────────────────────────
COR_BG           = "#F2F5F8"
COR_CARD_BG      = "#FFFFFF"
COR_CARD_BORDA   = "#DDE3EA"
COR_TITULO       = "#1C2B3A"
COR_SUBTITULO    = "#5A7A96"
COR_SEPARADOR    = "#DDE3EA"
COR_SECAO_LABEL  = "#8AA5BC"

CARD_VERDE    = ("#14532D", "#16A34A", "#16A34A", "#DCFCE7")
CARD_AZUL     = ("#1C4E8A", "#2563EB", "#2563EB", "#E8F0FB")
CARD_ROXO     = ("#4C2D8A", "#6D3FC0", "#6D3FC0", "#EDE8F8")
CARD_LARANJA  = ("#7A4010", "#C0670A", "#C0670A", "#FBF2E5")


def _verificar_licenca() -> tuple[bool, int]:
    try:
        from app.core.settings import carregar_config
        from datetime import timedelta
        config = carregar_config()
        ativacao_str = config.get("licenca_ativacao", "")
        if not ativacao_str:
            return False, 0
        ativacao = datetime.strptime(ativacao_str, "%Y-%m-%d").date()
        expiracao = ativacao + timedelta(days=180)
        dias_restantes = (expiracao - date.today()).days
        return dias_restantes >= 0, dias_restantes
    except Exception:
        return False, 0


# ══════════════════════════════════════════════════════════════════════════════
# MODAL DE DETALHE DA ENTRADA — aberto ao clicar numa linha de "Últimas Entradas"
# ══════════════════════════════════════════════════════════════════════════════

class ModalDetalheEntrada(QDialog):
    """
    Mini relatório da entrada clicada. Os campos mostrados mudam conforme o
    tipo do registro:
      - colaborador: nome, empresa, função, CPF, horário, operador
      - veiculo: placa, modelo, cor, motorista, empresa, observação, horário, operador
      - visitante: nome, documento, telefone, quem procura, motivo, horário, operador
    """

    def __init__(self, dados: dict, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._tipo = dados.get("tipo", "colaborador")

        self.setWindowTitle("Detalhe da Entrada")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
            QWidget {{ border: none; }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        d = self._dados
        tipo = self._tipo
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(24, 20, 24, 20)
        raiz.setSpacing(14)

        # ── Cabeçalho ─────────────────────────────────────────────────────
        topo = QHBoxLayout()

        ICONES_TIPO = {
            "veiculo":     ("fa5s.truck",     "#6D3FC0", "#EDE8F8"),
            "visitante":   ("fa5s.user-tie",  "#2563EB", "#E8F0FB"),
            "colaborador": ("fa5s.hard-hat",  "#16A34A", "#DCFCE7"),
        }
        icone_nome, cor_ic, bg_ic = ICONES_TIPO.get(tipo, ICONES_TIPO["colaborador"])

        ic_frame = QFrame()
        ic_frame.setFixedSize(40, 40)
        ic_frame.setStyleSheet(f"background: {bg_ic}; border-radius: 20px;")
        ic_lay = QHBoxLayout(ic_frame)
        ic_lay.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel()
        ic_lbl.setPixmap(qta.icon(icone_nome, color=cor_ic).pixmap(18, 18))
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_lay.addWidget(ic_lbl)
        topo.addWidget(ic_frame)

        vl = QVBoxLayout()
        vl.setSpacing(1)
        titulo_txt = d.get("placa", "—") if tipo == "veiculo" else d.get("nome", "—")
        lbl_t = QLabel(titulo_txt)
        lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        lbl_t.setWordWrap(True)

        SUBTITULOS = {
            "veiculo": "Entrada de Veículo",
            "visitante": "Entrada de Visitante",
            "colaborador": "Entrada de Colaborador",
        }
        lbl_s = QLabel(SUBTITULOS.get(tipo, "Entrada"))
        lbl_s.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(lbl_t)
        vl.addWidget(lbl_s)
        topo.addLayout(vl, 1)
        raiz.addLayout(topo)

        raiz.addWidget(self._separador())

        # ── Campos ────────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 8px; }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(10)

        horario = d.get("horario")
        horario_txt = horario.strftime("%d/%m/%Y às %H:%M") if horario else "—"

        if tipo == "veiculo":
            campos = [
                ("Placa",      d.get("placa") or "—"),
                ("Modelo",     d.get("modelo") or "—"),
                ("Tipo",       d.get("veiculo_tipo") or "—"),
                ("Cor",        d.get("cor") or "—"),
                ("Motorista",  d.get("motorista") or "—"),
                ("Empresa",    d.get("empresa") or "—"),
                ("Observação", d.get("observacao") or "—"),
                ("Entrada",    horario_txt),
                ("Operador",   d.get("operador") or "—"),
            ]
        elif tipo == "visitante":
            campos = [
                ("Nome",       d.get("nome") or "—"),
                ("Documento",  d.get("documento") or "—"),
                ("Telefone",   d.get("telefone") or "—"),
                ("Procura",    d.get("pessoa_visitada") or "—"),
                ("Setor",      d.get("empresa") or "—"),
                ("Motivo",     d.get("motivo") or "—"),
                ("Entrada",    horario_txt),
                ("Operador",   d.get("operador") or "—"),
            ]
        else:
            campos = [
                ("Nome",     d.get("nome") or "—"),
                ("Empresa",  d.get("empresa") or "—"),
                ("Função",   d.get("funcao") or "—"),
                ("CPF",      d.get("cpf") or "—"),
                ("Entrada",  horario_txt),
                ("Operador", d.get("operador") or "—"),
            ]

        for label_txt, valor_txt in campos:
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl_l = QLabel(label_txt)
            lbl_l.setFixedWidth(90)
            lbl_l.setStyleSheet(
                f"font-size: 11px; font-weight: bold; color: {COR_SECAO_LABEL};"
            )
            lbl_v = QLabel(str(valor_txt))
            lbl_v.setWordWrap(True)
            lbl_v.setStyleSheet(f"font-size: 13px; color: {COR_TITULO};")
            row.addWidget(lbl_l)
            row.addWidget(lbl_v, 1)
            cl.addLayout(row)

        raiz.addWidget(card)

        # ── Botão fechar ──────────────────────────────────────────────────
        btn_fechar = QPushButton("  Fechar")
        btn_fechar.setIcon(qta.icon("fa5s.times", color="white"))
        btn_fechar.setIconSize(QSize(11, 11))
        btn_fechar.setFixedHeight(38)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background: {COR_SUBTITULO}; color: white; border: none;
                border-radius: 6px; padding: 0 18px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COR_TITULO}; }}
        """)
        btn_fechar.clicked.connect(self.accept)
        raiz.addWidget(btn_fechar)

    def _separador(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
        return sep


# ══════════════════════════════════════════════════════════════════════════════
# MODAL DE RELATÓRIO EM TEMPO REAL — usado pelos cards "Pessoas na Unidade",
# "Veículos no Pátio" e "Empresas no Local"
# ══════════════════════════════════════════════════════════════════════════════

class ModalRelatorioTempoReal(QDialog):
    def __init__(self, titulo: str, icone: str, cor: str, dados: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setFixedSize(440, 520)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
        """)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(22, 20, 22, 20)
        raiz.setSpacing(12)

        cab = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(icone, color=cor).pixmap(18, 18))
        ic.setStyleSheet("background: transparent; border: none;")
        cab.addWidget(ic)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        cab.addWidget(lbl_t)
        cab.addStretch()
        lbl_qtd = QLabel(f"{len(dados)} registro(s)")
        lbl_qtd.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        cab.addWidget(lbl_qtd)
        raiz.addLayout(cab)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
        raiz.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #F2F5F8; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #DDE3EA; border-radius: 3px; }
        """)
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        cl = QVBoxLayout(container)
        cl.setSpacing(0)
        cl.setContentsMargins(0, 0, 4, 0)

        if dados:
            for item in dados:
                cl.addWidget(self._linha(item))
        else:
            vazio = QLabel("Nenhum registro neste momento")
            vazio.setAlignment(Qt.AlignCenter)
            vazio.setStyleSheet(
                f"font-size: 12px; color: {COR_SECAO_LABEL}; background: transparent;"
                " border: none; padding: 30px 0;"
            )
            cl.addWidget(vazio)
        cl.addStretch()

        scroll.setWidget(container)
        raiz.addWidget(scroll, 1)

        btn_fechar = QPushButton("  Fechar")
        btn_fechar.setIcon(qta.icon("fa5s.times", color="white"))
        btn_fechar.setIconSize(QSize(11, 11))
        btn_fechar.setFixedHeight(38)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background: {COR_SUBTITULO}; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COR_TITULO}; }}
        """)
        btn_fechar.clicked.connect(self.accept)
        raiz.addWidget(btn_fechar)

    def _linha(self, item: dict) -> QFrame:
        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; border-bottom: 1px solid {COR_SEPARADOR}; }}"
        )
        v = QVBoxLayout(row)
        v.setContentsMargins(4, 8, 4, 8)
        v.setSpacing(2)

        l1 = QLabel(item.get("linha1", "—"))
        l1.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COR_TITULO}; background: transparent; border: none;")
        l1.setWordWrap(True)
        v.addWidget(l1)

        if item.get("linha2"):
            l2 = QLabel(item["linha2"])
            l2.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO}; background: transparent; border: none;")
            l2.setWordWrap(True)
            v.addWidget(l2)

        if item.get("linha3"):
            l3 = QLabel(item["linha3"])
            l3.setStyleSheet(f"font-size: 10px; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
            v.addWidget(l3)

        return row


# ══════════════════════════════════════════════════════════════════════════════
# CRUD DE VISITANTES — aberto ao clicar no card "Visitantes"
# ══════════════════════════════════════════════════════════════════════════════

class ModalFormVisitante(QDialog):
    """Formulário de cadastro/edição de visitante."""

    def __init__(self, visitante=None, parent=None):
        super().__init__(parent)
        self._visitante_id = visitante.id if visitante else None
        self.setWindowTitle("Editar Visitante" if visitante else "Novo Visitante")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
            QLineEdit {{
                border: 1px solid {COR_CARD_BORDA}; border-radius: 5px;
                padding: 6px 8px; font-size: 13px; background: white;
                color: {COR_TITULO};
            }}
        """)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(22, 20, 22, 20)
        raiz.setSpacing(12)

        titulo = QLabel("Editar Visitante" if visitante else "Cadastrar Visitante")
        titulo.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        raiz.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.in_nome = QLineEdit(visitante.nome if visitante else "")
        self.in_documento = QLineEdit(visitante.documento if visitante and visitante.documento else "")
        self.in_telefone = QLineEdit(visitante.telefone if visitante and visitante.telefone else "")
        self.in_empresa_visitada = QLineEdit(visitante.empresa_visitada if visitante and visitante.empresa_visitada else "")
        self.in_pessoa_visitada = QLineEdit(visitante.pessoa_visitada if visitante and visitante.pessoa_visitada else "")
        self.in_motivo = QLineEdit(visitante.motivo if visitante and visitante.motivo else "")

        form.addRow("Nome*", self.in_nome)
        form.addRow("CPF/RG", self.in_documento)
        form.addRow("Telefone", self.in_telefone)
        form.addRow("Empresa/Setor visitado", self.in_empresa_visitada)
        form.addRow("Procura por", self.in_pessoa_visitada)
        form.addRow("Motivo", self.in_motivo)

        for i in range(form.rowCount()):
            label_item = form.itemAt(i, QFormLayout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setStyleSheet(
                    f"font-size: 12px; font-weight: bold; color: {COR_SECAO_LABEL};"
                )

        raiz.addLayout(form)

        botoes = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background: white; color: {COR_TITULO}; border: 1px solid {COR_CARD_BORDA};
                border-radius: 6px; font-size: 13px; padding: 0 14px;
            }}
            QPushButton:hover {{ background: #F2F5F8; }}
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("  Salvar" if visitante else "  Registrar Entrada")
        btn_salvar.setIcon(qta.icon("fa5s.check", color="white"))
        btn_salvar.setIconSize(QSize(11, 11))
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setFixedHeight(36)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold; padding: 0 14px;
            }
            QPushButton:hover { background: #1C4E8A; }
        """)
        btn_salvar.clicked.connect(self._salvar)

        botoes.addWidget(btn_cancelar)
        botoes.addStretch()
        botoes.addWidget(btn_salvar)
        raiz.addLayout(botoes)

    def _salvar(self):
        nome = self.in_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do visitante.")
            return

        from app.core.database import get_session
        from app.models.visitante import Visitante

        session = get_session()
        try:
            if self._visitante_id:
                v = session.query(Visitante).get(self._visitante_id)
                if not v:
                    QMessageBox.critical(self, "Erro", "Visitante não encontrado.")
                    return
            else:
                v = Visitante(entrada=datetime.now(), status="Dentro")
                session.add(v)

            v.nome = nome
            v.documento = self.in_documento.text().strip()
            v.telefone = self.in_telefone.text().strip()
            v.empresa_visitada = self.in_empresa_visitada.text().strip()
            v.pessoa_visitada = self.in_pessoa_visitada.text().strip()
            v.motivo = self.in_motivo.text().strip()

            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar: {e}")
        finally:
            session.close()


class ModalVisitantes(QDialog):
    """CRUD de visitantes — cadastro, edição, registro de saída e exclusão."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visitantes")
        self.setModal(True)
        self.setFixedSize(720, 520)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
        """)
        self._setup_ui()
        self._carregar()

    def _setup_ui(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(22, 20, 22, 20)
        raiz.setSpacing(12)

        cab = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.user-tie", color="#2563EB").pixmap(18, 18))
        ic.setStyleSheet("background: transparent; border: none;")
        cab.addWidget(ic)
        lbl_t = QLabel("Visitantes")
        lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        cab.addWidget(lbl_t)
        cab.addStretch()

        btn_novo = QPushButton("  Novo Visitante")
        btn_novo.setIcon(qta.icon("fa5s.plus", color="white"))
        btn_novo.setIconSize(QSize(10, 10))
        btn_novo.setCursor(Qt.PointingHandCursor)
        btn_novo.setFixedHeight(34)
        btn_novo.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 6px; font-size: 12px; font-weight: bold; padding: 0 14px;
            }
            QPushButton:hover { background: #1C4E8A; }
        """)
        btn_novo.clicked.connect(self._novo)
        cab.addWidget(btn_novo)
        raiz.addLayout(cab)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
        raiz.addWidget(sep)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Procura por", "Entrada", "Status", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #DDE3EA; border-radius: 6px;
                gridline-color: #EEF1F5;
            }
            QHeaderView::section {
                background: #F2F5F8; color: #5A7A96; font-size: 10px; font-weight: bold;
                border: none; padding: 6px;
            }
        """)
        raiz.addWidget(self.tabela, 1)

        btn_fechar = QPushButton("  Fechar")
        btn_fechar.setIcon(qta.icon("fa5s.times", color="white"))
        btn_fechar.setIconSize(QSize(11, 11))
        btn_fechar.setFixedHeight(38)
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background: {COR_SUBTITULO}; color: white; border: none;
                border-radius: 6px; font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COR_TITULO}; }}
        """)
        btn_fechar.clicked.connect(self.accept)
        raiz.addWidget(btn_fechar)

    def _carregar(self):
        from app.core.database import get_session
        from app.models.visitante import Visitante

        session = get_session()
        try:
            visitantes = session.query(Visitante).order_by(Visitante.entrada.desc()).all()
            self.tabela.setRowCount(0)
            for v in visitantes:
                row = self.tabela.rowCount()
                self.tabela.insertRow(row)
                self.tabela.setItem(row, 0, QTableWidgetItem(v.nome or "—"))
                self.tabela.setItem(row, 1, QTableWidgetItem(v.pessoa_visitada or "—"))
                entrada_txt = v.entrada.strftime("%d/%m %H:%M") if v.entrada else "—"
                self.tabela.setItem(row, 2, QTableWidgetItem(entrada_txt))

                item_status = QTableWidgetItem(v.status or "—")
                if v.status == "Dentro":
                    item_status.setForeground(QColor("#16A34A"))
                else:
                    item_status.setForeground(QColor("#5A7A96"))
                self.tabela.setItem(row, 3, item_status)

                self.tabela.setCellWidget(row, 4, self._criar_acoes(v.id, v.status))

            if not visitantes:
                self.tabela.setRowCount(1)
                vazio = QTableWidgetItem("Nenhum visitante cadastrado")
                vazio.setForeground(QColor(COR_SECAO_LABEL))
                self.tabela.setItem(0, 0, vazio)
                self.tabela.setSpan(0, 0, 1, 5)
        finally:
            session.close()

    def _criar_acoes(self, visitante_id: int, status: str) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        h = QHBoxLayout(wrap)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(6)

        btn_editar = QPushButton()
        btn_editar.setIcon(qta.icon("fa5s.edit", color="#2563EB"))
        btn_editar.setFixedSize(26, 26)
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            " QPushButton:hover { background: #E8F0FB; border-radius: 4px; }"
        )
        btn_editar.clicked.connect(lambda _, vid=visitante_id: self._editar(vid))
        h.addWidget(btn_editar)

        if status == "Dentro":
            btn_saida = QPushButton()
            btn_saida.setIcon(qta.icon("fa5s.sign-out-alt", color="#C0670A"))
            btn_saida.setFixedSize(26, 26)
            btn_saida.setCursor(Qt.PointingHandCursor)
            btn_saida.setStyleSheet(
                "QPushButton { border: none; background: transparent; }"
                " QPushButton:hover { background: #FBF2E5; border-radius: 4px; }"
            )
            btn_saida.clicked.connect(lambda _, vid=visitante_id: self._registrar_saida(vid))
            h.addWidget(btn_saida)

        btn_excluir = QPushButton()
        btn_excluir.setIcon(qta.icon("fa5s.trash", color="#DC2626"))
        btn_excluir.setFixedSize(26, 26)
        btn_excluir.setCursor(Qt.PointingHandCursor)
        btn_excluir.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            " QPushButton:hover { background: #FEF2F2; border-radius: 4px; }"
        )
        btn_excluir.clicked.connect(lambda _, vid=visitante_id: self._excluir(vid))
        h.addWidget(btn_excluir)

        h.addStretch()
        return wrap

    def _novo(self):
        modal = ModalFormVisitante(parent=self)
        if modal.exec() == QDialog.Accepted:
            self._carregar()

    def _editar(self, visitante_id: int):
        from app.core.database import get_session
        from app.models.visitante import Visitante

        session = get_session()
        try:
            v = session.query(Visitante).get(visitante_id)
            if not v:
                return
            modal = ModalFormVisitante(visitante=v, parent=self)
            if modal.exec() == QDialog.Accepted:
                self._carregar()
        finally:
            session.close()

    def _registrar_saida(self, visitante_id: int):
        resposta = QMessageBox.question(
            self, "Registrar Saída",
            "Confirmar a saída deste visitante?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        from app.core.database import get_session
        from app.models.visitante import Visitante

        session = get_session()
        try:
            v = session.query(Visitante).get(visitante_id)
            if v:
                v.saida = datetime.now()
                v.status = "Saiu"
                session.commit()
            self._carregar()
        finally:
            session.close()

    def _excluir(self, visitante_id: int):
        resposta = QMessageBox.question(
            self, "Excluir Visitante",
            "Tem certeza que deseja excluir este registro? Essa ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        from app.core.database import get_session
        from app.models.visitante import Visitante

        session = get_session()
        try:
            v = session.query(Visitante).get(visitante_id)
            if v:
                session.delete(v)
                session.commit()
            self._carregar()
        finally:
            session.close()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    navegar = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COR_BG};")
        self._cards = {}
        self._setup_ui()

        # Auto-refresh a cada 5 segundos.
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.carregar_dados)
        self._timer.start(5_000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 30)
        layout.setSpacing(0)

        # ── Cabeçalho ────────────────────────────────────────────────────────
        cabecalho = QHBoxLayout()
        cabecalho.setContentsMargins(0, 0, 0, 0)

        col_titulo = QVBoxLayout()
        col_titulo.setSpacing(3)

        titulo = QLabel("Painel de Controle")
        titulo.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COR_TITULO};"
            " background: transparent; letter-spacing: 0.3px;"
        )
        col_titulo.addWidget(titulo)

        sub = QLabel("Gestão de Terceiros")
        sub.setStyleSheet(
            f"font-size: 12px; color: {COR_SUBTITULO}; background: transparent;"
        )
        col_titulo.addWidget(sub)
        cabecalho.addLayout(col_titulo)
        cabecalho.addStretch()

        self._lbl_atualizacao = QLabel("")
        self._lbl_atualizacao.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._lbl_atualizacao.setStyleSheet(
            f"font-size: 10px; color: {COR_SECAO_LABEL}; background: transparent;"
        )
        cabecalho.addWidget(self._lbl_atualizacao)

        layout.addLayout(cabecalho)
        layout.addSpacing(20)
        layout.addWidget(self._separador())
        layout.addSpacing(20)

        self._card_cliente = self._criar_card_cliente()
        layout.addWidget(self._card_cliente)

        layout.addSpacing(12)

        self._banner_licenca = self._criar_banner_licenca()
        layout.addWidget(self._banner_licenca)
        self._banner_licenca.setVisible(False)

        layout.addSpacing(20)
        layout.addWidget(self._separador())
        layout.addSpacing(24)

        secao = QLabel("STATUS EM TEMPO REAL")
        secao.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {COR_SECAO_LABEL};"
            " background: transparent; letter-spacing: 1.4px;"
        )
        layout.addWidget(secao)
        layout.addSpacing(12)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        cards = [
            ("pessoas_unidade", "fa5s.users",          "Pessoas na Unidade", CARD_VERDE),
            ("visitantes",      "fa5s.user-tie",        "Visitantes",          CARD_AZUL),
            ("veiculos_patio",  "fa5s.truck",           "Veículos no Pátio",   CARD_ROXO),
            ("empresas_ativas", "fa5s.building",        "Empresas no Local",   CARD_LARANJA),
        ]

        for chave, icone, label, cores in cards:
            card = self._criar_card(chave, icone, label, cores)
            cards_layout.addWidget(card)
            self._cards[chave] = card

        layout.addLayout(cards_layout)
        layout.addSpacing(24)

        linha_inferior = QHBoxLayout()
        linha_inferior.setSpacing(16)
        linha_inferior.setContentsMargins(0, 0, 0, 0)

        self._painel_entradas = self._criar_painel_entradas()
        linha_inferior.addWidget(self._painel_entradas, stretch=2)

        painel_atalhos = self._criar_painel_atalhos()
        linha_inferior.addWidget(painel_atalhos, stretch=1)

        layout.addLayout(linha_inferior)

        layout.addStretch()
        layout.addWidget(self._separador())
        layout.addSpacing(10)

        rodape = QHBoxLayout()
        rodape.setContentsMargins(0, 0, 0, 0)

        self._lbl_rodape = QLabel("ThirdSys — Sistema de Gestão de Terceiros")
        self._lbl_rodape.setStyleSheet(
            f"font-size: 10px; color: {COR_SECAO_LABEL}; background: transparent;"
        )
        rodape.addWidget(self._lbl_rodape)
        rodape.addStretch()

        self._lbl_licenca_rodape = QLabel("")
        self._lbl_licenca_rodape.setStyleSheet(
            "font-size: 10px; color: #16A34A; background: transparent; font-weight: bold;"
        )
        rodape.addWidget(self._lbl_licenca_rodape)

        layout.addLayout(rodape)

        self.carregar_dados()

    def _criar_card_cliente(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF;
                border: 1px solid {COR_CARD_BORDA};
                border-left: 5px solid #2563EB;
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        lay = QHBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(16)

        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.building", color="#2563EB").pixmap(28, 28))
        ic.setStyleSheet("background: transparent; border: none;")
        ic.setAlignment(Qt.AlignTop)
        lay.addWidget(ic)

        txt = QVBoxLayout()
        txt.setSpacing(3)
        txt.setContentsMargins(0, 0, 0, 0)

        lbl_cliente_tag = QLabel("CLIENTE")
        lbl_cliente_tag.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1.4px;"
        )
        txt.addWidget(lbl_cliente_tag)

        self._lbl_empresa_nome = QLabel("—")
        self._lbl_empresa_nome.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {COR_TITULO}; letter-spacing: 0.3px;"
        )
        txt.addWidget(self._lbl_empresa_nome)

        self._lbl_empresa_unidade = QLabel("—")
        self._lbl_empresa_unidade.setStyleSheet(
            f"font-size: 13px; color: {COR_SUBTITULO};"
        )
        txt.addWidget(self._lbl_empresa_unidade)

        lay.addLayout(txt)
        lay.addStretch()

        cnpj_col = QVBoxLayout()
        cnpj_col.setSpacing(3)
        cnpj_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        lbl_cnpj_tag = QLabel("CNPJ")
        lbl_cnpj_tag.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1.4px;"
        )
        lbl_cnpj_tag.setAlignment(Qt.AlignRight)
        cnpj_col.addWidget(lbl_cnpj_tag)

        self._lbl_cnpj = QLabel("—")
        self._lbl_cnpj.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {COR_TITULO};"
        )
        self._lbl_cnpj.setAlignment(Qt.AlignRight)
        cnpj_col.addWidget(self._lbl_cnpj)

        lay.addLayout(cnpj_col)
        return frame

    def _criar_banner_licenca(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #FEF3C7;
                border: 1px solid #FCD34D;
                border-left: 5px solid #D97706;
                border-radius: 8px;
            }
            QLabel { border: none; background: transparent; }
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(12)

        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.exclamation-triangle", color="#D97706").pixmap(16, 16))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        self._lbl_aviso_licenca = QLabel("")
        self._lbl_aviso_licenca.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #92400E;"
        )
        lay.addWidget(self._lbl_aviso_licenca)
        lay.addStretch()
        return frame

    def _criar_card(self, chave, icone_nome, titulo_card, cores) -> QFrame:
        cor_num, cor_ic, cor_borda, bg_ic = cores

        frame = QFrame()
        frame.setFixedHeight(110)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COR_CARD_BG};
                border: 1px solid {COR_CARD_BORDA};
                border-left: 4px solid {cor_borda};
            }}
            QFrame:hover {{
                background-color: #F8FAFC;
            }}
        """)

        outer = QHBoxLayout(frame)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(16)

        ic_frame = QFrame()
        ic_frame.setFixedSize(46, 46)
        ic_frame.setStyleSheet(
            f"background-color: {bg_ic}; border: none; border-radius: 4px;"
        )
        ic_layout = QHBoxLayout(ic_frame)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_label = QLabel()
        ic_label.setPixmap(qta.icon(icone_nome, color=cor_ic).pixmap(20, 20))
        ic_label.setAlignment(Qt.AlignCenter)
        ic_label.setStyleSheet("background: transparent; border: none;")
        ic_layout.addWidget(ic_label)
        outer.addWidget(ic_frame, alignment=Qt.AlignVCenter)

        txt = QVBoxLayout()
        txt.setSpacing(4)
        txt.setContentsMargins(0, 0, 0, 0)

        lbl_titulo = QLabel(titulo_card.upper())
        lbl_titulo.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL};"
            " background: transparent; border: none; letter-spacing: 1px;"
        )
        txt.addWidget(lbl_titulo)

        lbl_num = QLabel("—")
        lbl_num.setStyleSheet(
            f"font-size: 30px; font-weight: bold; color: {cor_num};"
            " background: transparent; border: none;"
        )
        txt.addWidget(lbl_num)

        outer.addLayout(txt)
        outer.addStretch()

        frame._lbl_num = lbl_num
        frame.mousePressEvent = lambda e, k=chave: self._abrir_relatorio_card(k)
        return frame

    def _abrir_relatorio_card(self, chave: str):
        if chave == "visitantes":
            modal = ModalVisitantes(self)
            modal.exec()
            self.carregar_dados()
            return

        TITULOS = {
            "pessoas_unidade": ("Pessoas na Unidade", "fa5s.users", "#16A34A"),
            "veiculos_patio":  ("Veículos no Pátio",  "fa5s.truck", "#6D3FC0"),
            "empresas_ativas": ("Empresas no Local",  "fa5s.building", "#C0670A"),
        }
        titulo, icone, cor = TITULOS.get(chave, ("Relatório", "fa5s.chart-bar", "#5A7A96"))
        dados = self._dados_relatorio_card(chave)
        modal = ModalRelatorioTempoReal(titulo, icone, cor, dados, parent=self)
        modal.exec()

    def _dados_relatorio_card(self, chave: str) -> list:
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from app.models.trabalhador import Trabalhador
            from app.models.veiculo import Veiculo
            from sqlalchemy import func
        except Exception as e:
            print(f"Erro ao importar models para relatório: {e}")
            return []

        session = get_session()
        hoje = date.today()
        inicio = datetime.combine(hoje, datetime.min.time())
        resultado = []

        try:
            if chave == "pessoas_unidade":
                subq = (
                    session.query(Acesso.trabalhador_id, func.max(Acesso.horario).label("ultima"))
                    .filter(Acesso.horario >= inicio)
                    .group_by(Acesso.trabalhador_id)
                    .subquery()
                )
                registros = (
                    session.query(Acesso, Trabalhador)
                    .join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                    .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                    .filter(Acesso.tipo == "entrada")
                    .order_by(Acesso.horario.desc())
                    .all()
                )
                for acesso, trab in registros:
                    resultado.append({
                        "linha1": trab.nome,
                        "linha2": trab.empresa.razao_social if trab.empresa else "—",
                        "linha3": f"Entrou às {acesso.horario.strftime('%H:%M')}" if acesso.horario else "",
                    })

            elif chave == "veiculos_patio":
                veiculos = (
                    session.query(Veiculo)
                    .filter(Veiculo.status == "Dentro")
                    .order_by(Veiculo.entrada.desc())
                    .all()
                )
                for v in veiculos:
                    resultado.append({
                        "linha1": f"{v.placa} — {v.modelo or v.tipo}",
                        "linha2": v.empresa or "—",
                        "linha3": f"Entrou às {v.entrada.strftime('%H:%M')}" if v.entrada else "—",
                    })

            elif chave == "empresas_ativas":
                subq = (
                    session.query(Acesso.trabalhador_id, func.max(Acesso.horario).label("ultima"))
                    .filter(Acesso.horario >= inicio)
                    .group_by(Acesso.trabalhador_id)
                    .subquery()
                )
                ids_dentro = [
                    row[0] for row in (
                        session.query(Acesso.trabalhador_id)
                        .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                        .filter(Acesso.tipo == "entrada")
                        .all()
                    )
                ]
                if ids_dentro:
                    trabalhadores = (
                        session.query(Trabalhador)
                        .filter(Trabalhador.id.in_(ids_dentro), Trabalhador.empresa_id.isnot(None))
                        .all()
                    )
                    contagem = {}
                    for t in trabalhadores:
                        nome_emp = t.empresa.razao_social if t.empresa else "—"
                        contagem[nome_emp] = contagem.get(nome_emp, 0) + 1
                    for nome_emp, qtd in sorted(contagem.items(), key=lambda x: -x[1]):
                        resultado.append({
                            "linha1": nome_emp,
                            "linha2": f"{qtd} pessoa(s) no local",
                            "linha3": "",
                        })
        except Exception as e:
            print(f"Erro ao montar relatório do card '{chave}': {e}")
        finally:
            session.close()

        return resultado

    def _criar_painel_entradas(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame#painelEntradas {{
                background: {COR_CARD_BG};
                border: 1px solid {COR_CARD_BORDA};
                border-radius: 8px;
            }}
        """)
        frame.setObjectName("painelEntradas")

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(0)

        cab = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.history", color="#2563EB").pixmap(14, 14))
        ic.setStyleSheet("background: transparent; border: none;")
        cab.addWidget(ic)
        cab.addSpacing(8)

        lbl_sec = QLabel("ÚLTIMAS ENTRADAS")
        lbl_sec.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {COR_SECAO_LABEL};"
            " background: transparent; letter-spacing: 1.4px; border: none;"
        )
        cab.addWidget(lbl_sec)
        cab.addStretch()

        btn_ver_todos = QLabel("Ver portaria →")
        btn_ver_todos.setCursor(Qt.PointingHandCursor)
        btn_ver_todos.setStyleSheet(
            "font-size: 11px; color: #2563EB; background: transparent;"
            " border: none; text-decoration: underline;"
        )
        btn_ver_todos.mousePressEvent = lambda e: self.navegar.emit("portaria")
        cab.addWidget(btn_ver_todos)

        lay.addLayout(cab)
        lay.addSpacing(14)
        lay.addWidget(self._separador())
        lay.addSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #F2F5F8; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #DDE3EA; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        self._container_entradas = QVBoxLayout(container)
        self._container_entradas.setSpacing(0)
        self._container_entradas.setContentsMargins(0, 0, 4, 0)
        self._container_entradas.addStretch()

        scroll.setWidget(container)
        lay.addWidget(scroll, 1)

        return frame

    def _limpar_entradas(self):
        while self._container_entradas.count():
            item = self._container_entradas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._container_entradas.addStretch()

    def _adicionar_linha_entrada(self, dados: dict):
        tipo = dados.get("tipo", "colaborador")
        nome = dados.get("nome") or "—"
        empresa = dados.get("empresa") or ""
        horario_dt = dados.get("horario")
        horario = horario_dt.strftime("%H:%M") if horario_dt else "—"

        TIPO_CONFIG = {
            "colaborador": ("fa5s.hard-hat",      "#16A34A", "#DCFCE7"),
            "visitante":   ("fa5s.user-tie",       "#2563EB", "#E8F0FB"),
            "veiculo":     ("fa5s.truck",           "#6D3FC0", "#EDE8F8"),
        }
        icone_nome, cor_ic, bg_ic = TIPO_CONFIG.get(tipo, ("fa5s.user", "#5A7A96", "#F2F5F8"))

        row = QFrame()
        row.setFixedHeight(52)
        row.setCursor(Qt.PointingHandCursor)
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {COR_SEPARADOR};
            }}
            QFrame:hover {{ background: #F8FAFC; }}
        """)
        row.mousePressEvent = lambda e, d=dados: self._abrir_detalhe_entrada(d)

        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        ic_frame = QFrame()
        ic_frame.setFixedSize(32, 32)
        ic_frame.setStyleSheet(
            f"background: {bg_ic}; border-radius: 16px; border: none;"
        )
        ic_lay = QHBoxLayout(ic_frame)
        ic_lay.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel()
        ic_lbl.setPixmap(qta.icon(icone_nome, color=cor_ic).pixmap(14, 14))
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_lbl.setStyleSheet("background: transparent; border: none;")
        ic_lay.addWidget(ic_lbl)
        h.addWidget(ic_frame, alignment=Qt.AlignVCenter)

        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        lbl_nome = QLabel(nome)
        lbl_nome.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {COR_TITULO};"
            " background: transparent; border: none;"
        )
        info.addWidget(lbl_nome)

        if empresa:
            lbl_emp = QLabel(empresa)
            lbl_emp.setStyleSheet(
                f"font-size: 11px; color: {COR_SUBTITULO};"
                " background: transparent; border: none;"
            )
            info.addWidget(lbl_emp)

        h.addLayout(info)
        h.addStretch()

        col_dir = QVBoxLayout()
        col_dir.setSpacing(4)
        col_dir.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        lbl_hora = QLabel(horario)
        lbl_hora.setAlignment(Qt.AlignRight)
        lbl_hora.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {COR_TITULO};"
            " background: transparent; border: none;"
        )
        col_dir.addWidget(lbl_hora)

        TIPO_LABEL = {
            "colaborador": ("COLABORADOR", cor_ic, bg_ic),
            "visitante":   ("VISITANTE",   cor_ic, bg_ic),
            "veiculo":     ("VEÍCULO",     cor_ic, bg_ic),
        }
        txt_badge, cor_badge, bg_badge = TIPO_LABEL.get(tipo, ("—", "#5A7A96", "#F2F5F8"))
        badge = QLabel(txt_badge)
        badge.setAlignment(Qt.AlignRight)
        badge.setStyleSheet(
            f"font-size: 8px; font-weight: bold; color: {cor_badge};"
            f" background: {bg_badge}; border: none;"
            " padding: 2px 6px; border-radius: 3px; letter-spacing: 0.8px;"
        )
        col_dir.addWidget(badge)

        h.addLayout(col_dir)

        count = self._container_entradas.count()
        self._container_entradas.insertWidget(max(0, count - 1), row)

    def _abrir_detalhe_entrada(self, dados: dict):
        modal = ModalDetalheEntrada(dados, parent=self)
        modal.exec()

    def _adicionar_linha_vazia(self, mensagem: str = "Sem registros hoje"):
        lbl = QLabel(mensagem)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"font-size: 12px; color: {COR_SECAO_LABEL}; background: transparent;"
            " border: none; padding: 20px 0;"
        )
        count = self._container_entradas.count()
        self._container_entradas.insertWidget(max(0, count - 1), lbl)

    def _criar_painel_atalhos(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame#painelAtalhos {{
                background: {COR_CARD_BG};
                border: 1px solid {COR_CARD_BORDA};
                border-radius: 8px;
            }}
        """)
        frame.setObjectName("painelAtalhos")

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(0)

        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.bolt", color="#2563EB").pixmap(14, 14))
        ic.setStyleSheet("background: transparent; border: none;")

        lbl_sec = QLabel("ACESSO RÁPIDO")
        lbl_sec.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {COR_SECAO_LABEL};"
            " background: transparent; letter-spacing: 1.4px; border: none;"
        )

        cab = QHBoxLayout()
        cab.addWidget(ic)
        cab.addSpacing(8)
        cab.addWidget(lbl_sec)
        cab.addStretch()
        lay.addLayout(cab)

        lay.addSpacing(14)
        lay.addWidget(self._separador())
        lay.addSpacing(12)

        atalhos = [
            ("portaria",      "fa5s.sign-in-alt",    "Registrar Entrada"),
            ("setores",       "fa5s.building",        "Ver Empresas"),
            ("trabalhadores", "fa5s.hard-hat",        "Ver Trabalhadores"),
            ("vencimentos",   "fa5s.calendar-times",  "Ver Vencimentos"),
        ]

        for chave, icone_nome, rotulo in atalhos:
            btn = self._criar_atalho(chave, icone_nome, rotulo)
            lay.addWidget(btn)
            lay.addSpacing(6)

        lay.addStretch()
        return frame

    def _criar_atalho(self, chave: str, icone_nome: str, rotulo: str) -> QFrame:
        frame = QFrame()
        frame.setFixedHeight(44)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COR_BG};
                border: 1px solid {COR_CARD_BORDA};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background-color: #EBF0F6;
                border: 1px solid #BDC8D4;
            }}
        """)

        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(10)

        ic = QLabel()
        ic.setPixmap(qta.icon(icone_nome, color="#3B7DD8").pixmap(13, 13))
        ic.setStyleSheet("background: transparent; border: none;")
        h.addWidget(ic)

        lbl = QLabel(rotulo)
        lbl.setStyleSheet(
            f"font-size: 12px; color: {COR_TITULO}; background: transparent; border: none;"
        )
        h.addWidget(lbl)
        h.addStretch()

        seta = QLabel()
        seta.setPixmap(qta.icon("fa5s.chevron-right", color="#BDC8D4").pixmap(9, 9))
        seta.setStyleSheet("background: transparent; border: none;")
        h.addWidget(seta)

        frame.mousePressEvent = lambda e, k=chave: self.navegar.emit(k)
        return frame

    def _separador(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
        return sep

    def showEvent(self, event):
        super().showEvent(event)
        self.carregar_dados()

    def atualizar_empresa(self, nome: str, cidade: str, cnpj: str, unidade: str = ""):
        self._lbl_empresa_nome.setText(nome.upper() if nome else "—")
        unidade_txt = unidade if unidade else (cidade if cidade else "—")
        self._lbl_empresa_unidade.setText(unidade_txt)
        self._lbl_cnpj.setText(cnpj if cnpj else "—")

    def carregar_dados(self):
        try:
            from app.core.database import get_session
            from app.core.settings import carregar_config
            from app.models.acesso import Acesso
            from app.models.trabalhador import Trabalhador
            from app.models.empresa import Empresa
            from app.models.veiculo import Veiculo
            from app.models.visitante import Visitante
            from sqlalchemy import func

            session = get_session()
            hoje    = date.today()
            inicio  = datetime.combine(hoje, datetime.min.time())

            subq = (
                session.query(Acesso.trabalhador_id, func.max(Acesso.horario).label("ultima"))
                .filter(Acesso.horario >= inicio)
                .group_by(Acesso.trabalhador_id)
                .subquery()
            )
            pessoas_dentro = (
                session.query(Acesso)
                .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                .filter(Acesso.tipo == "entrada")
                .count()
            )

            visitantes = session.query(Visitante).filter(Visitante.status == "Dentro").count()

            veiculos_patio = session.query(Veiculo).filter(Veiculo.status == "Dentro").count()

            ids_dentro = [
                row[0] for row in (
                    session.query(Acesso.trabalhador_id)
                    .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                    .filter(Acesso.tipo == "entrada")
                    .all()
                )
            ]
            empresas_no_local = 0
            if ids_dentro:
                empresas_no_local = (
                    session.query(Trabalhador.empresa_id)
                    .filter(Trabalhador.id.in_(ids_dentro), Trabalhador.empresa_id.isnot(None))
                    .distinct()
                    .count()
                )

            entradas_colab = (
                session.query(Acesso, Trabalhador)
                .join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                .filter(Acesso.tipo == "entrada", Acesso.horario >= inicio)
                .order_by(Acesso.horario.desc())
                .limit(8)
                .all()
            )
            ultimas = []
            for acesso, trab in entradas_colab:
                emp = trab.empresa.razao_social if trab.empresa else ""
                ultimas.append({
                    "tipo": "colaborador",
                    "nome": trab.nome,
                    "empresa": emp,
                    "horario": acesso.horario,
                    "funcao": trab.funcao or "",
                    "cpf": trab.cpf or "",
                    "operador": getattr(acesso, "operador", "") or "",
                })

            entradas_veic = (
                session.query(Veiculo)
                .filter(Veiculo.entrada >= inicio)
                .order_by(Veiculo.entrada.desc())
                .limit(8)
                .all()
            )
            for v in entradas_veic:
                ultimas.append({
                    "tipo": "veiculo",
                    "nome": f"{v.placa} — {v.modelo or v.tipo}",
                    "empresa": v.empresa or "",
                    "horario": v.entrada,
                    "placa": v.placa or "",
                    "modelo": v.modelo or "",
                    "veiculo_tipo": v.tipo or "",
                    "cor": v.cor or "",
                    "motorista": v.motorista or "",
                    "observacao": v.observacao or "",
                    "operador": getattr(v, "operador", "") or "",
                })

            entradas_visit = (
                session.query(Visitante)
                .filter(Visitante.entrada >= inicio)
                .order_by(Visitante.entrada.desc())
                .limit(8)
                .all()
            )
            for vis in entradas_visit:
                ultimas.append({
                    "tipo": "visitante",
                    "nome": vis.nome,
                    "empresa": vis.empresa_visitada or "",
                    "horario": vis.entrada,
                    "documento": vis.documento or "",
                    "telefone": vis.telefone or "",
                    "pessoa_visitada": vis.pessoa_visitada or "",
                    "motivo": vis.motivo or "",
                    "operador": getattr(vis, "operador", "") or "",
                })

            ultimas.sort(key=lambda r: r["horario"] or datetime.min, reverse=True)
            ultimas = ultimas[:8]

            session.close()

            self._cards["pessoas_unidade"]._lbl_num.setText(str(pessoas_dentro))
            self._cards["visitantes"]._lbl_num.setText(str(visitantes))
            self._cards["veiculos_patio"]._lbl_num.setText(str(veiculos_patio))
            self._cards["empresas_ativas"]._lbl_num.setText(str(empresas_no_local))

            self._limpar_entradas()
            if ultimas:
                for reg in ultimas:
                    self._adicionar_linha_entrada(reg)
            else:
                self._adicionar_linha_vazia("Nenhuma entrada registrada hoje")

            config = carregar_config()
            self.atualizar_empresa(
                nome=config.get("empresa_nome", ""),
                cidade=config.get("empresa_cidade", ""),
                cnpj=config.get("empresa_cnpj", ""),
                unidade=config.get("empresa_unidade", ""),
            )

            valida, dias = _verificar_licenca()
            self._atualizar_licenca(valida, dias)

            agora = datetime.now().strftime("%H:%M:%S")
            self._lbl_atualizacao.setText(f"Atualizado às {agora}")

        except Exception as e:
            print(f"Erro ao carregar dashboard: {e}")

    def _atualizar_licenca(self, valida: bool, dias: int):
        if not valida and dias == 0:
            self._banner_licenca.setVisible(False)
            self._lbl_licenca_rodape.setText("")

        elif not valida and dias < 0:
            self._banner_licenca.setVisible(True)
            self._lbl_aviso_licenca.setText(
                f"⚠  Licença expirada há {abs(dias)} dia(s). "
                "Entre em contato para renovar."
            )
            self._banner_licenca.setStyleSheet("""
                QFrame {
                    background: #FEF2F2;
                    border: 1px solid #FCA5A5;
                    border-left: 5px solid #DC2626;
                    border-radius: 8px;
                }
                QLabel { border: none; background: transparent; }
            """)
            self._lbl_aviso_licenca.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #991B1B;"
            )
            self._lbl_licenca_rodape.setText("LICENÇA EXPIRADA")
            self._lbl_licenca_rodape.setStyleSheet(
                "font-size: 10px; color: #DC2626; background: transparent; font-weight: bold;"
            )
            self._bloquear_sistema()

        elif dias <= 30:
            self._banner_licenca.setVisible(True)
            self._lbl_aviso_licenca.setText(
                f"⚠  Licença vence em {dias} dia(s). Entre em contato para renovar."
            )
            self._lbl_licenca_rodape.setText(f"Licença válida por {dias} dia(s)")
            self._lbl_licenca_rodape.setStyleSheet(
                "font-size: 10px; color: #D97706; background: transparent; font-weight: bold;"
            )
        else:
            self._banner_licenca.setVisible(False)
            self._lbl_licenca_rodape.setText(f"Licença válida por {dias} dia(s)")
            self._lbl_licenca_rodape.setStyleSheet(
                "font-size: 10px; color: #16A34A; background: transparent; font-weight: bold;"
            )

    def _bloquear_sistema(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Licença Expirada")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(
            "<b>Licença expirada.</b><br><br>"
            "O período de uso deste sistema encerrou.<br>"
            "Entre em contato para renovar sua licença e continuar utilizando."
        )
        msg.setInformativeText("Contato: santiago@thirdsys.com.br")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()