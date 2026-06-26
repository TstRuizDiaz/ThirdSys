from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout,
    QLineEdit, QDateEdit, QFileDialog, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QProgressBar, QSizePolicy, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QSize, QDate, QPoint
from PySide6.QtGui import QFont, QAction, QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
import qtawesome as qta
from datetime import date, timedelta


class CNPJLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("99.999.999/9999-99;_")
        self.setMaxLength(18)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                background-color: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 10px;
                padding: 4px 14px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background-color: #EFF6FF; }
            QLineEdit[invalid="true"] { border-color: #DC2626; background-color: #FEF2F2; }
            QLineEdit[valid="true"] { border-color: #16A34A; background-color: #F0FDF4; }
        """)
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        digits = self._extract_digits(text)
        if len(digits) == 14:
            if self._validar_cnpj(digits):
                self.setProperty("valid", "true")
                self.setProperty("invalid", "false")
            else:
                self.setProperty("valid", "false")
                self.setProperty("invalid", "true")
        else:
            self.setProperty("valid", "false")
            self.setProperty("invalid", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def _extract_digits(self, text: str) -> str:
        return ''.join(c for c in text if c.isdigit())

    def text_clean(self) -> str:
        return self._extract_digits(self.text())

    def is_valid(self) -> bool:
        digits = self.text_clean()
        if len(digits) != 14:
            return False
        return self._validar_cnpj(digits)

    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        if len(cnpj) != 14 or not cnpj.isdigit():
            return False
        if cnpj == cnpj[0] * 14:
            return False

        def calcular_dv(cnpj_parte, pesos):
            soma = sum(int(d) * p for d, p in zip(cnpj_parte, pesos))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        if calcular_dv(cnpj[:12], pesos1) != int(cnpj[12]):
            return False
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        if calcular_dv(cnpj[:13], pesos2) != int(cnpj[13]):
            return False
        return True


PERIODICIDADES = [
    ("Anual (1 ano)",    365),
    ("Bienal (2 anos)",  730),
    ("3 anos",          1095),
    ("4 anos",          1460),
    ("5 anos",          1825),
]

PERIODICIDADES_PGR = [
    ("Anual (1 ano)",   365),
    ("Bienal (2 anos)", 730),
]


def _qdate_to_date(qdate: QDate) -> date:
    return date(qdate.year(), qdate.month(), qdate.day())


def _date_to_qdate(d: date) -> QDate:
    return QDate(d.year, d.month, d.day)


# ─────────────────────────────────────────────────────────────────────────────
# Toggle simples sem setCheckable — evita loops de sinais
# ─────────────────────────────────────────────────────────────────────────────

class ToggleTipo:
    """
    Gerencia dois QPushButton como seleção exclusiva (radio),
    sem usar setCheckable para evitar loops de toggled.
    """

    _ESTILO_FIXA_ATIVO = """
        QPushButton {
            border-radius: 7px; font-size: 12px; font-weight: bold;
            padding: 6px 18px; border: none;
            background-color: #2563EB; color: white;
        }
    """
    _ESTILO_FLUTUANTE_ATIVO = """
        QPushButton {
            border-radius: 7px; font-size: 12px; font-weight: bold;
            padding: 6px 18px; border: none;
            background-color: #7C3AED; color: white;
        }
    """
    _ESTILO_INATIVO = """
        QPushButton {
            border-radius: 7px; font-size: 12px; font-weight: bold;
            padding: 6px 18px; border: none;
            background-color: transparent; color: #94A3B8;
        }
    """

    def __init__(self):
        self._valor = "fixa"  # estado interno

        self.btn_fixa = QPushButton("  Fixa")
        self.btn_fixa.setIcon(qta.icon("fa5s.building", color="white"))
        self.btn_fixa.setIconSize(QSize(13, 13))
        self.btn_fixa.setCursor(Qt.PointingHandCursor)

        self.btn_flutuante = QPushButton("  Flutuante")
        self.btn_flutuante.setIcon(qta.icon("fa5s.exchange-alt", color="#94A3B8"))
        self.btn_flutuante.setIconSize(QSize(13, 13))
        self.btn_flutuante.setCursor(Qt.PointingHandCursor)

        self.btn_fixa.clicked.connect(lambda: self.selecionar("fixa"))
        self.btn_flutuante.clicked.connect(lambda: self.selecionar("flutuante"))

        self.selecionar("fixa")

    def selecionar(self, valor: str):
        self._valor = valor
        if valor == "fixa":
            self.btn_fixa.setStyleSheet(self._ESTILO_FIXA_ATIVO)
            self.btn_fixa.setIcon(qta.icon("fa5s.building", color="white"))
            self.btn_flutuante.setStyleSheet(self._ESTILO_INATIVO)
            self.btn_flutuante.setIcon(qta.icon("fa5s.exchange-alt", color="#94A3B8"))
        else:
            self.btn_flutuante.setStyleSheet(self._ESTILO_FLUTUANTE_ATIVO)
            self.btn_flutuante.setIcon(qta.icon("fa5s.exchange-alt", color="white"))
            self.btn_fixa.setStyleSheet(self._ESTILO_INATIVO)
            self.btn_fixa.setIcon(qta.icon("fa5s.building", color="#94A3B8"))

    def valor(self) -> str:
        return self._valor

    def widget(self) -> QFrame:
        """Retorna o container com os dois botões."""
        container = QFrame()
        container.setFixedHeight(44)
        container.setStyleSheet(
            "QFrame { background-color: #F1F5F9; border-radius: 10px; border: 1px solid #E2E8F0; }"
        )
        inner = QHBoxLayout(container)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(4)
        inner.addWidget(self.btn_fixa)
        inner.addWidget(self.btn_flutuante)
        return container


# ─────────────────────────────────────────────────────────────────────────────
# FichaEmpresaPage
# ─────────────────────────────────────────────────────────────────────────────

class FichaEmpresaPage(QWidget):
    voltar = Signal()

    def __init__(self, empresa=None, setor_nome: str = ""):
        super().__init__()
        self._arquivos = {}
        self._cards_validade = {}
        self._cards_checkbox = {}
        self.setor_nome = setor_nome

        self._empresa_id    = empresa.id           if empresa else None
        self.empresa_nome   = empresa.razao_social if empresa else ""
        self._empresa_dados = {}

        if empresa:
            self._empresa_dados = self._ler_empresa(empresa.id)

        self.setStyleSheet("background-color: #F0F4F8;")
        self._setup_ui()
        if empresa:
            self._preencher_dados()
            self._verificar_alertas()

    def _ler_empresa(self, empresa_id: int) -> dict:
        try:
            from app.core.database import get_session
            from app.models.empresa import Empresa
            session = get_session()
            e = session.get(Empresa, empresa_id)
            if not e:
                session.close()
                return {}
            d = dict(
                id=e.id,
                razao_social=e.razao_social or "",
                cnpj=e.cnpj or "",
                email=e.email or "",
                telefone=e.telefone or "",
                responsavel=e.responsavel or "",
                setor=e.setor or "",
                tipo_empresa=e.tipo_empresa if hasattr(e, "tipo_empresa") and e.tipo_empresa else "fixa",
                tem_contrato_social=bool(e.tem_contrato_social),
                tem_manual_qsma=bool(e.tem_manual_qsma),
                pgr_data_inicial=e.pgr_data_inicial,
                pgr_validade=e.pgr_validade,
                pgr_periodo_dias=int(e.pgr_periodo_dias) if hasattr(e, 'pgr_periodo_dias') and e.pgr_periodo_dias else (
                    730 if (hasattr(e, 'pgr_bienal') and e.pgr_bienal) else 365
                ),
                pcmso_data_inicial=e.pcmso_data_inicial,
                pcmso_validade=e.pcmso_validade,
                pcmso_periodo_dias=int(e.pcmso_periodo_dias) if hasattr(e, 'pcmso_periodo_dias') and e.pcmso_periodo_dias else 365,
                apolice_data_inicial=e.apolice_data_inicial,
                apolice_validade=e.apolice_validade,
                apolice_periodo_dias=int(e.apolice_periodo_dias) if hasattr(e, 'apolice_periodo_dias') and e.apolice_periodo_dias else 365,
            )
            session.close()
            return d
        except Exception as ex:
            print(f"[ERRO _ler_empresa] {ex}")
            return {}

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        btn_voltar = self._btn_acao("  Voltar", "fa5s.arrow-left", "#F1F5F9", "#64748B", "#64748B")
        btn_voltar.clicked.connect(self.voltar.emit)
        header.addWidget(btn_voltar)
        header.addStretch()

        titulo = QLabel(f"Ficha da Empresa — {self.setor_nome.title()}")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; background: transparent;")
        header.addWidget(titulo)
        header.addStretch()

        btn_salvar = self._btn_acao("  Salvar", "fa5s.save", "#16A34A", "white", "white")
        btn_salvar.clicked.connect(self._on_salvar)
        btn_colab = self._btn_acao("  Colaborador", "fa5s.user-plus", "#2563EB", "white", "white")
        btn_colab.clicked.connect(self._on_novo_colaborador)
        header.addWidget(btn_colab)
        header.addWidget(btn_salvar)
        layout.addLayout(header)

        self._banner_alertas = QFrame()
        self._banner_alertas.setVisible(False)
        self._banner_alertas.setStyleSheet("""
            QFrame {
                background-color: #FEF2F2;
                border: 1px solid #FCA5A5;
                border-left: 4px solid #DC2626;
                border-radius: 8px;
            }
            QLabel { border: none; background: transparent; }
        """)
        self._banner_layout = QVBoxLayout(self._banner_alertas)
        self._banner_layout.setContentsMargins(16, 10, 16, 10)
        self._banner_layout.setSpacing(4)

        lbl_banner_titulo = QLabel("Documentos vencidos")
        lbl_banner_titulo.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #991B1B; border: none; background: transparent;"
        )
        self._banner_layout.addWidget(lbl_banner_titulo)
        self._lbl_banner_itens = QLabel("")
        self._lbl_banner_itens.setWordWrap(True)
        self._lbl_banner_itens.setStyleSheet(
            "font-size: 12px; color: #DC2626; border: none; background: transparent;"
        )
        self._banner_layout.addWidget(self._lbl_banner_itens)
        layout.addWidget(self._banner_alertas)

        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFixedHeight(1)
        linha.setStyleSheet("background-color: #E2E8F0; border: none;")
        layout.addWidget(linha)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 0 12px 12px 12px;
            }
            QTabBar::tab {
                background: #F1F5F9; color: #64748B;
                border: 1px solid #E2E8F0;
                border-radius: 8px 8px 0 0;
                padding: 8px 20px; font-weight: bold;
                font-size: 13px; margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: white; color: #2563EB;
                border-bottom: 2px solid #2563EB;
            }
        """)
        self.tabs.addTab(self._aba_dados(),        "  Dados da Empresa")
        self.tabs.addTab(self._aba_colaboradores(), "  Colaboradores")
        layout.addWidget(self.tabs)

    def _verificar_alertas(self):
        hoje = date.today()
        d = self._empresa_dados
        nome = d.get("razao_social", "Esta empresa")
        alertas = []
        for doc, val in [
            ("PGR",               d.get("pgr_validade")),
            ("PCMSO",             d.get("pcmso_validade")),
            ("Apolice de Seguro", d.get("apolice_validade")),
        ]:
            if val and val < hoje:
                dias = (hoje - val).days
                alertas.append(f"• {nome}: {doc} vencido ha {dias} dia(s) ({val.strftime('%d/%m/%Y')})")
            elif val and val <= hoje + timedelta(days=30):
                dias = (val - hoje).days
                alertas.append(f"• {nome}: {doc} vence em {dias} dia(s) ({val.strftime('%d/%m/%Y')})")

        if alertas:
            self._lbl_banner_itens.setText("\n".join(alertas))
            self._banner_alertas.setVisible(True)
            tem_vencido = any("vencido" in a for a in alertas)
            if tem_vencido:
                self._banner_alertas.setStyleSheet("""
                    QFrame { background-color: #FEF2F2; border: 1px solid #FCA5A5; border-left: 4px solid #DC2626; border-radius: 8px; }
                    QLabel { border: none; background: transparent; }
                """)
                self._lbl_banner_itens.setStyleSheet("font-size: 12px; color: #DC2626; border: none; background: transparent;")
            else:
                self._banner_alertas.setStyleSheet("""
                    QFrame { background-color: #FFFBEB; border: 1px solid #FCD34D; border-left: 4px solid #D97706; border-radius: 8px; }
                    QLabel { border: none; background: transparent; }
                """)
                self._lbl_banner_itens.setStyleSheet("font-size: 12px; color: #92400E; border: none; background: transparent;")
        else:
            self._banner_alertas.setVisible(False)

    def _aba_dados(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        vlayout = QVBoxLayout(container)
        vlayout.setSpacing(20)
        vlayout.addWidget(self._titulo_secao("Dados da Empresa"))
        vlayout.addWidget(self._secao_dados())
        vlayout.addWidget(self._titulo_secao("Documentos da Empresa"))
        vlayout.addWidget(self._secao_documentos())
        scroll.setWidget(container)
        return scroll

    def _aba_colaboradores(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        busca = QLineEdit()
        busca.setPlaceholderText("Buscar colaborador...")
        busca.setFixedHeight(36)
        busca.setStyleSheet("""
            QLineEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; }
        """)
        header.addWidget(busca)
        header.addStretch()

        btn_novo = QPushButton("  Novo Colaborador")
        btn_novo.setIcon(qta.icon("fa5s.user-plus", color="white"))
        btn_novo.setIconSize(QSize(13, 13))
        btn_novo.setCursor(Qt.PointingHandCursor)
        btn_novo.setStyleSheet("""
            QPushButton { background: #2563EB; color: white; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background: #1D4ED8; }
        """)
        btn_novo.clicked.connect(self._on_novo_colaborador)
        header.addWidget(btn_novo)
        layout.addLayout(header)

        self.tabela_colabs = QTableWidget()
        self.tabela_colabs.setColumnCount(5)
        self.tabela_colabs.setHorizontalHeaderLabels(["Nome", "CPF", "Funcao", "ASO", "Situacao"])
        self.tabela_colabs.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_colabs.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela_colabs.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_colabs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_colabs.verticalHeader().setVisible(False)
        self.tabela_colabs.setAlternatingRowColors(True)
        self.tabela_colabs.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E2E8F0; border-radius: 10px; gridline-color: #F1F5F9; }
            QTableWidget::item { padding: 10px; color: #1A2B4A; }
            QTableWidget::item:selected { background: #EFF6FF; }
            QHeaderView::section { background: #F8FAFC; color: #64748B; border: none; border-bottom: 2px solid #E2E8F0; padding: 10px; font-weight: bold; font-size: 12px; }
        """)
        self.tabela_colabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabela_colabs.customContextMenuRequested.connect(self._menu_contexto_colab)
        self.tabela_colabs.doubleClicked.connect(self._on_colab_duplo_clique)
        layout.addWidget(self.tabela_colabs)

        busca.textChanged.connect(self._filtrar_colabs)
        self._busca_colab = busca
        self._carregar_colaboradores()
        return widget

    def _menu_contexto_colab(self, pos: QPoint):
        index = self.tabela_colabs.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        item = self.tabela_colabs.item(row, 0)
        if not item:
            return
        colab_id = item.data(Qt.UserRole)
        nome = item.text()

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 6px; }
            QMenu::item { padding: 8px 20px 8px 12px; border-radius: 6px; font-size: 13px; color: #1A2B4A; }
            QMenu::item:selected { background: #EFF6FF; color: #2563EB; }
            QMenu::separator { height: 1px; background: #F1F5F9; margin: 4px 8px; }
        """)
        acao_editar   = QAction(qta.icon("fa5s.edit",       color="#2563EB"), "  Editar",   self)
        acao_inativar = QAction(qta.icon("fa5s.user-slash", color="#D97706"), "  Inativar", self)
        acao_excluir  = QAction(qta.icon("fa5s.trash-alt",  color="#DC2626"), "  Excluir",  self)
        acao_editar.triggered.connect(lambda: self._editar_colab(colab_id))
        acao_inativar.triggered.connect(lambda: self._inativar_colab(colab_id, nome))
        acao_excluir.triggered.connect(lambda: self._excluir_colab(colab_id, nome))
        menu.addAction(acao_editar)
        menu.addSeparator()
        menu.addAction(acao_inativar)
        menu.addSeparator()
        menu.addAction(acao_excluir)
        menu.exec(self.tabela_colabs.viewport().mapToGlobal(pos))

    def _editar_colab(self, colab_id: int):
        self.window().navegar_para(f"colaborador:{colab_id}|{self._empresa_id or 0}")

    def _inativar_colab(self, colab_id: int, nome: str):
        resp = QMessageBox.question(self, "Inativar colaborador", f"Deseja inativar <b>{nome}</b>?", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        session = get_session()
        try:
            colab = session.get(Trabalhador, colab_id)
            if colab:
                colab.ativo = False
                session.commit()
            self._carregar_colaboradores()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao inativar: {e}")
        finally:
            session.close()

    def _excluir_colab(self, colab_id: int, nome: str):
        resp = QMessageBox.warning(self, "Excluir colaborador", f"Tem certeza que deseja excluir <b>{nome}</b>?<br><span style='color:#DC2626'>Esta acao nao pode ser desfeita.</span>", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        session = get_session()
        try:
            colab = session.get(Trabalhador, colab_id)
            if colab:
                session.delete(colab)
                session.commit()
            self._carregar_colaboradores()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")
        finally:
            session.close()

    def _carregar_colaboradores(self):
        if not hasattr(self, "tabela_colabs") or not self._empresa_id:
            return
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        from app.models.empresa import Empresa
        session = get_session()
        empresa = session.get(Empresa, self._empresa_id)
        if empresa and hasattr(empresa, 'pgr_periodo_dias') and empresa.pgr_periodo_dias:
            dias_periodo = int(empresa.pgr_periodo_dias)
        elif empresa and hasattr(empresa, 'pgr_bienal') and empresa.pgr_bienal:
            dias_periodo = 730
        else:
            dias_periodo = 365
        colabs = session.query(Trabalhador).filter_by(empresa_id=self._empresa_id, ativo=True).all()
        dados = []
        for c in colabs:
            aso_validade     = c.aso_validade
            aso_data_inicial = c.aso_data_inicial if hasattr(c, 'aso_data_inicial') else None
            if not aso_data_inicial and aso_validade:
                aso_data_inicial = aso_validade - timedelta(days=dias_periodo)
            elif not aso_data_inicial:
                aso_data_inicial = date.today()
            nova_aso_validade = aso_data_inicial + timedelta(days=dias_periodo)
            dados.append(dict(id=c.id, nome=c.nome, cpf=c.cpf or "", funcao=c.funcao or "",
                              aso_validade=aso_validade, aso_validade_calculada=nova_aso_validade,
                              aso_data_inicial=aso_data_inicial))
        session.close()
        self._colabs_cache = dados
        self._popular_tabela(dados)

    def _popular_tabela(self, colabs):
        from PySide6.QtGui import QColor
        hoje = date.today()
        self.tabela_colabs.setRowCount(len(colabs))
        for row, c in enumerate(colabs):
            self.tabela_colabs.setItem(row, 0, QTableWidgetItem(c["nome"]))
            self.tabela_colabs.setItem(row, 1, QTableWidgetItem(c["cpf"]))
            self.tabela_colabs.setItem(row, 2, QTableWidgetItem(c["funcao"]))
            aso_val = c.get("aso_validade_calculada") or c.get("aso_validade")
            aso_txt = aso_val.strftime("%d/%m/%Y") if aso_val else "—"
            aso_item = QTableWidgetItem(aso_txt)
            if aso_val and aso_val < hoje:
                aso_item.setForeground(QColor("#DC2626"))
            self.tabela_colabs.setItem(row, 3, aso_item)
            bloqueado = bool(aso_val and aso_val < hoje)
            sit = QTableWidgetItem("BLOQUEADO" if bloqueado else "LIBERADO")
            if bloqueado:
                sit.setForeground(QColor("#DC2626")); sit.setBackground(QColor("#FEE2E2"))
            else:
                sit.setForeground(QColor("#16A34A")); sit.setBackground(QColor("#DCFCE7"))
            self.tabela_colabs.setItem(row, 4, sit)
            self.tabela_colabs.item(row, 0).setData(Qt.UserRole, c["id"])

    def _filtrar_colabs(self, termo: str):
        if not hasattr(self, "_colabs_cache"):
            return
        termo = termo.lower()
        filtrados = [c for c in self._colabs_cache
                     if termo in c["nome"].lower() or termo in c["cpf"].lower() or termo in c["funcao"].lower()]
        self._popular_tabela(filtrados)

    def _on_colab_duplo_clique(self, index):
        item = self.tabela_colabs.item(index.row(), 0)
        if item:
            self._editar_colab(item.data(Qt.UserRole))

    def _on_novo_colaborador(self):
        if not self._empresa_id:
            QMessageBox.warning(self, "Atencao", "Salve a empresa primeiro.")
            return
        self.window().navegar_para(f"novo_colaborador:{self._empresa_id}")

    # ── Seção de dados ────────────────────────────────────────────────────────
    def _secao_dados(self) -> QFrame:
        frame = self._frame()
        grid = QGridLayout(frame)
        grid.setSpacing(16)
        grid.setContentsMargins(24, 24, 24, 24)
        grid.setColumnStretch(1, 1)

        campos = [
            ("Empresa *",   "campo_nome",        None),
            ("CNPJ *",      "campo_cnpj",        CNPJLineEdit),
            ("E-mail",      "campo_email",       None),
            ("Telefone",    "campo_telefone",    None),
            ("Responsavel", "campo_responsavel", None),
        ]

        _estilo_linha = """
            QLineEdit {
                background-color: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 10px;
                padding: 4px 14px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background-color: #EFF6FF; }
        """

        for i, (label_txt, attr, factory) in enumerate(campos):
            lbl = QLabel(label_txt)
            lbl.setStyleSheet("color: #64748B; font-size: 12px; font-weight: bold; background: transparent; padding-left: 12px;")
            lbl.setFixedWidth(100)
            lbl.setAlignment(Qt.AlignVCenter)
            campo = factory() if factory else QLineEdit()
            if not factory:
                campo.setFixedHeight(40)
                campo.setStyleSheet(_estilo_linha)
            setattr(self, attr, campo)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(campo, i, 1)

        # ── Tipo de Empresa — usando ToggleTipo ───────────────────────────────
        lbl_tipo = QLabel("Tipo *")
        lbl_tipo.setStyleSheet("color: #64748B; font-size: 12px; font-weight: bold; background: transparent; padding-left: 12px;")
        lbl_tipo.setFixedWidth(100)
        lbl_tipo.setAlignment(Qt.AlignVCenter)

        self._toggle_tipo = ToggleTipo()

        row_tipo = len(campos)
        grid.addWidget(lbl_tipo, row_tipo, 0)
        grid.addWidget(self._toggle_tipo.widget(), row_tipo, 1)

        return frame

    def _secao_documentos(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        docs_validade = [
            ("PGR",               "fa5s.file-medical-alt", "Programa de Gerenciamento de Riscos",             PERIODICIDADES_PGR),
            ("PCMSO",             "fa5s.user-shield",      "Programa de Controle Medico de Saude Ocupacional", PERIODICIDADES),
            ("Apolice de Seguro", "fa5s.shield-alt",       "Cobertura seguradora da empresa",                  PERIODICIDADES),
        ]
        for col, (nome_doc, icone, descricao, opcoes_periodo) in enumerate(docs_validade):
            card_dict = self._card_validade(nome_doc, icone, descricao, opcoes_periodo)
            self._cards_validade[nome_doc] = card_dict
            grid.addWidget(card_dict["widget"], 0, col)

        docs_check = [
            ("Contrato Social", "fa5s.file-contract", "Documento constitutivo da empresa"),
            ("Manual QSMA",     "fa5s.book",           "Manual de Qualidade, Seguranca e Meio Ambiente"),
        ]
        for col, (nome_doc, icone, descricao) in enumerate(docs_check):
            card_dict = self._card_checkbox(nome_doc, icone, descricao)
            self._cards_checkbox[nome_doc] = card_dict
            grid.addWidget(card_dict["widget"], 1, col)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(spacer, 1, 2)
        return container

    def _card_validade(self, nome_doc, icone, descricao, opcoes_periodo) -> dict:
        card = QFrame()
        card.setFixedWidth(320)
        card.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(16, 14, 16, 14)
        header.setSpacing(10)

        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("QFrame { background-color: #EFF6FF; border-radius: 10px; border: none; }")
        icon_lay = QVBoxLayout(icon_container)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icone, color="#2563EB").pixmap(18, 18))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        icon_lay.addWidget(icon_lbl)
        header.addWidget(icon_container)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        lbl_nome = QLabel(nome_doc)
        lbl_nome.setStyleSheet("color: #1A2B4A; font-size: 14px; font-weight: bold; background: transparent;")
        lbl_desc = QLabel(descricao)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
        lbl_desc.setWordWrap(True)
        text_layout.addWidget(lbl_nome)
        text_layout.addWidget(lbl_desc)
        header.addLayout(text_layout, 1)

        lbl_status = QLabel("DENTRO DO PRAZO")
        lbl_status.setAlignment(Qt.AlignCenter)
        lbl_status.setStyleSheet("background-color: #DCFCE7; color: #16A34A; border-radius: 16px; padding: 5px 10px; font-size: 9px; font-weight: bold;")
        header.addWidget(lbl_status)
        layout.addLayout(header)

        progress = QProgressBar()
        progress.setFixedHeight(4)
        progress.setTextVisible(False)
        progress.setMaximum(opcoes_periodo[0][1])
        progress.setValue(opcoes_periodo[0][1])
        progress.setStyleSheet("QProgressBar { background-color: #F1F5F9; border-radius: 2px; border: none; margin: 0 16px; } QProgressBar::chunk { background-color: #16A34A; border-radius: 2px; }")
        layout.addWidget(progress)

        periodo_layout = QHBoxLayout()
        periodo_layout.setContentsMargins(16, 10, 16, 0)
        periodo_layout.setSpacing(8)
        lbl_periodo = QLabel("Periodicidade:")
        lbl_periodo.setStyleSheet("color: #64748B; font-size: 11px; font-weight: bold; background: transparent;")
        periodo_layout.addWidget(lbl_periodo)
        combo_periodo = QComboBox()
        combo_periodo.setFixedHeight(30)
        for label, _ in opcoes_periodo:
            combo_periodo.addItem(label)
        combo_periodo.setStyleSheet("""
            QComboBox { background: white; color: #1A2B4A; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 2px 10px; font-size: 11px; font-weight: bold; }
            QComboBox:focus { border-color: #2563EB; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView { background: white; color: #1A2B4A; border: 1px solid #E2E8F0; border-radius: 8px; selection-background-color: #EFF6FF; selection-color: #2563EB; }
        """)
        periodo_layout.addWidget(combo_periodo, 1)
        layout.addLayout(periodo_layout)

        datas_layout = QHBoxLayout()
        datas_layout.setContentsMargins(16, 10, 16, 0)
        datas_layout.setSpacing(10)

        ini_layout = QVBoxLayout()
        ini_layout.setSpacing(2)
        lbl_ini_titulo = QLabel("Data Inicial")
        lbl_ini_titulo.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: bold; background: transparent;")
        dt_ini = QDateEdit()
        dt_ini.setButtonSymbols(QDateEdit.NoButtons)
        dt_ini.setCalendarPopup(True)
        dt_ini.setDate(QDate.currentDate())
        dt_ini.setMaximumDate(QDate.currentDate())
        dt_ini.setStyleSheet("QDateEdit { background: white; color: #1A2B4A; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 5px 8px; font-size: 12px; } QDateEdit:focus { border-color: #2563EB; }")
        ini_layout.addWidget(lbl_ini_titulo)
        ini_layout.addWidget(dt_ini)
        datas_layout.addLayout(ini_layout)

        val_layout = QVBoxLayout()
        val_layout.setSpacing(2)
        lbl_val_titulo = QLabel("Validade (automatica)")
        lbl_val_titulo.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: bold; background: transparent;")
        dt_val = QDateEdit()
        dt_val.setButtonSymbols(QDateEdit.NoButtons)
        dt_val.setCalendarPopup(False)
        dt_val.setReadOnly(True)
        dt_val.setStyleSheet("QDateEdit { background: #F8FAFC; color: #64748B; border: 1.5px solid #E2E8F0; border-radius: 8px; padding: 5px 8px; font-size: 12px; }")
        val_layout.addWidget(lbl_val_titulo)
        val_layout.addWidget(dt_val)
        datas_layout.addLayout(val_layout)
        layout.addLayout(datas_layout)

        footer = QHBoxLayout()
        footer.setContentsMargins(16, 10, 16, 14)
        footer.setSpacing(10)

        dias_container = QFrame()
        dias_container.setStyleSheet("QFrame { background-color: #F8FAFC; border-radius: 8px; }")
        dias_lay = QHBoxLayout(dias_container)
        dias_lay.setContentsMargins(10, 6, 10, 6)
        dias_lay.setSpacing(4)
        lbl_dias_num = QLabel("365")
        lbl_dias_num.setStyleSheet("color: #16A34A; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        lbl_dias_txt = QLabel("dias restantes")
        lbl_dias_txt.setStyleSheet("color: #94A3B8; font-size: 11px; background: transparent;")
        dias_lay.addWidget(lbl_dias_num)
        dias_lay.addWidget(lbl_dias_txt)
        dias_lay.addStretch()
        footer.addWidget(dias_container, 1)

        btn_upload = QPushButton()
        btn_upload.setIcon(qta.icon("fa5s.paperclip", color="#64748B"))
        btn_upload.setIconSize(QSize(14, 14))
        btn_upload.setFixedSize(36, 36)
        btn_upload.setToolTip(f"Anexar PDF — {nome_doc}")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet("QPushButton { background-color: #F1F5F9; border-radius: 8px; } QPushButton:hover { background-color: #E2E8F0; }")
        btn_upload.clicked.connect(lambda _, n=nome_doc, b=btn_upload: self._on_upload_pdf(n, b))
        footer.addWidget(btn_upload)
        layout.addLayout(footer)

        def atualizar():
            ini = _qdate_to_date(dt_ini.date())
            idx = combo_periodo.currentIndex()
            dias_periodo = opcoes_periodo[idx][1]
            venc = ini + timedelta(days=dias_periodo)
            dt_val.blockSignals(True)
            dt_val.setDate(_date_to_qdate(venc))
            dt_val.blockSignals(False)
            hoje = date.today()
            dias = (venc - hoje).days
            progress.setMaximum(dias_periodo)
            progress.setValue(max(0, min(dias, dias_periodo)))
            if dias < 0:
                lbl_dias_num.setText(str(abs(dias))); lbl_dias_txt.setText("dias vencido")
                lbl_status.setText("VENCIDO"); lbl_status.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border-radius: 16px; padding: 3px 10px; font-size: 9px; font-weight: bold;")
                lbl_dias_num.setStyleSheet("color: #DC2626; font-size: 18px; font-weight: bold; background: transparent; border: none;")
                lbl_dias_txt.setStyleSheet("color: #DC2626; font-size: 11px; background: transparent;")
                dias_container.setStyleSheet("QFrame { background-color: #FEF2F2; border-radius: 8px; }")
                progress.setStyleSheet("QProgressBar { background-color: #FEE2E2; border-radius: 2px; border: none; margin: 0 16px; } QProgressBar::chunk { background-color: #DC2626; border-radius: 2px; }")
            elif dias <= 30:
                lbl_dias_num.setText(str(dias)); lbl_dias_txt.setText("dias restantes")
                lbl_status.setText("A VENCER"); lbl_status.setStyleSheet("background-color: #FEF3C7; color: #D97706; border-radius: 16px; padding: 3px 10px; font-size: 9px; font-weight: bold;")
                lbl_dias_num.setStyleSheet("color: #D97706; font-size: 18px; font-weight: bold; background: transparent; border: none;")
                lbl_dias_txt.setStyleSheet("color: #D97706; font-size: 11px; background: transparent;")
                dias_container.setStyleSheet("QFrame { background-color: #FFFBEB; border-radius: 8px; }")
                progress.setStyleSheet("QProgressBar { background-color: #F1F5F9; border-radius: 2px; border: none; margin: 0 16px; } QProgressBar::chunk { background-color: #D97706; border-radius: 2px; }")
            else:
                lbl_dias_num.setText(str(dias)); lbl_dias_txt.setText("dias restantes")
                lbl_status.setText("DENTRO DO PRAZO"); lbl_status.setStyleSheet("background-color: #DCFCE7; color: #16A34A; border-radius: 16px; padding: 5px 10px; font-size: 9px; font-weight: bold;")
                lbl_dias_num.setStyleSheet("color: #16A34A; font-size: 18px; font-weight: bold; background: transparent; border: none;")
                lbl_dias_txt.setStyleSheet("color: #94A3B8; font-size: 11px; background: transparent;")
                dias_container.setStyleSheet("QFrame { background-color: #F8FAFC; border-radius: 8px; }")
                progress.setStyleSheet("QProgressBar { background-color: #F1F5F9; border-radius: 2px; border: none; margin: 0 16px; } QProgressBar::chunk { background-color: #16A34A; border-radius: 2px; }")

        def on_ini_changed(qdate: QDate):
            if qdate > QDate.currentDate():
                QMessageBox.warning(None, "Data invalida", "A data inicial nao pode ser uma data futura.")
                dt_ini.blockSignals(True)
                dt_ini.setDate(QDate.currentDate())
                dt_ini.blockSignals(False)
            atualizar()

        dt_ini.dateChanged.connect(on_ini_changed)
        combo_periodo.currentIndexChanged.connect(lambda _: atualizar())
        atualizar()

        return {
            "widget": card, "data_inicial": dt_ini, "data_validade": dt_val,
            "combo_periodo": combo_periodo, "opcoes_periodo": opcoes_periodo,
            "status": lbl_status, "dias_num": lbl_dias_num,
            "progress": progress, "btn_upload": btn_upload, "atualizar": atualizar,
        }

    def _card_checkbox(self, nome_doc: str, icone: str, descricao: str) -> dict:
        card = QFrame()
        card.setFixedWidth(320)
        card.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(16, 14, 16, 14)
        header.setSpacing(10)

        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("QFrame { background-color: #F0FDF4; border-radius: 10px; border: none; }")
        icon_lay = QVBoxLayout(icon_container)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icone, color="#16A34A").pixmap(18, 18))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        icon_lay.addWidget(icon_lbl)
        header.addWidget(icon_container)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        lbl_nome = QLabel(nome_doc)
        lbl_nome.setStyleSheet("color: #1A2B4A; font-size: 14px; font-weight: bold; background: transparent;")
        lbl_desc = QLabel(descricao)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
        lbl_desc.setWordWrap(True)
        text_layout.addWidget(lbl_nome)
        text_layout.addWidget(lbl_desc)
        header.addLayout(text_layout, 1)
        layout.addLayout(header)

        toggle_layout = QHBoxLayout()
        toggle_layout.setContentsMargins(16, 0, 16, 12)
        toggle_layout.setAlignment(Qt.AlignCenter)

        toggle_container = QFrame()
        toggle_container.setFixedSize(180, 40)
        toggle_container.setStyleSheet("QFrame { background-color: #F1F5F9; border-radius: 10px; border: 1px solid #E2E8F0; }")
        toggle_inner = QHBoxLayout(toggle_container)
        toggle_inner.setContentsMargins(3, 3, 3, 3)
        toggle_inner.setSpacing(3)

        estilo_base        = "QPushButton { border-radius: 8px; font-size: 11px; font-weight: bold; padding: 6px 12px; border: none; }"
        estilo_sim_ativo   = estilo_base + "QPushButton { background-color: #16A34A; color: white; }"
        estilo_sim_inativo = estilo_base + "QPushButton { background-color: transparent; color: #94A3B8; }"
        estilo_nao_ativo   = estilo_base + "QPushButton { background-color: #DC2626; color: white; }"
        estilo_nao_inativo = estilo_base + "QPushButton { background-color: transparent; color: #94A3B8; }"

        btn_sim = QPushButton("Possui")
        btn_sim.setIcon(qta.icon("fa5s.check", color="white"))
        btn_sim.setIconSize(QSize(11, 11))
        btn_sim.setCursor(Qt.PointingHandCursor)
        btn_sim.setStyleSheet(estilo_sim_inativo)

        btn_nao = QPushButton("Nao possui")
        btn_nao.setIcon(qta.icon("fa5s.times", color="white"))
        btn_nao.setIconSize(QSize(11, 11))
        btn_nao.setCursor(Qt.PointingHandCursor)
        btn_nao.setStyleSheet(estilo_nao_ativo)

        # Estado interno — sem setCheckable para evitar loops
        _estado = {"valor": False}  # False = nao possui

        def _selecionar_sim():
            _estado["valor"] = True
            btn_sim.setStyleSheet(estilo_sim_ativo)
            btn_sim.setIcon(qta.icon("fa5s.check", color="white"))
            btn_nao.setStyleSheet(estilo_nao_inativo)
            btn_nao.setIcon(qta.icon("fa5s.times", color="#94A3B8"))

        def _selecionar_nao():
            _estado["valor"] = False
            btn_nao.setStyleSheet(estilo_nao_ativo)
            btn_nao.setIcon(qta.icon("fa5s.times", color="white"))
            btn_sim.setStyleSheet(estilo_sim_inativo)
            btn_sim.setIcon(qta.icon("fa5s.check", color="#94A3B8"))

        btn_sim.clicked.connect(_selecionar_sim)
        btn_nao.clicked.connect(_selecionar_nao)
        _selecionar_nao()  # padrão

        # Expõe isChecked via monkey-patch para compatibilidade com _on_salvar
        btn_sim.isChecked = lambda: _estado["valor"]
        btn_nao.isChecked = lambda: not _estado["valor"]

        toggle_inner.addWidget(btn_sim)
        toggle_inner.addWidget(btn_nao)
        toggle_layout.addWidget(toggle_container)
        layout.addLayout(toggle_layout)

        upload_layout = QHBoxLayout()
        upload_layout.setContentsMargins(16, 0, 16, 14)
        btn_upload = QPushButton("  Anexar PDF")
        btn_upload.setIcon(qta.icon("fa5s.paperclip", color="#64748B"))
        btn_upload.setIconSize(QSize(14, 14))
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet("""
            QPushButton { background-color: #F8FAFC; color: #64748B; border: 1.5px dashed #CBD5E1; border-radius: 8px; padding: 8px 14px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: #F1F5F9; }
        """)
        btn_upload.clicked.connect(lambda _, n=nome_doc, b=btn_upload: self._on_upload_pdf(n, b))
        upload_layout.addStretch()
        upload_layout.addWidget(btn_upload)
        upload_layout.addStretch()
        layout.addLayout(upload_layout)

        return {
            "widget": card, "btn_sim": btn_sim, "btn_nao": btn_nao,
            "selecionar_sim": _selecionar_sim, "selecionar_nao": _selecionar_nao,
            "btn_upload": btn_upload, "icon_container": icon_container, "icon_lbl": icon_lbl,
        }

    def _on_upload_pdf(self, nome_doc: str, btn: QPushButton):
        caminho, _ = QFileDialog.getOpenFileName(self, f"Selecionar PDF — {nome_doc}", "", "Documentos PDF (*.pdf)")
        if not caminho:
            return
        from pathlib import Path
        path = Path(caminho)
        if path.suffix.lower() != ".pdf":
            QMessageBox.warning(self, "Arquivo invalido", f"Extensao encontrada: {path.suffix or 'nenhuma'}"); return
        if not path.exists():
            QMessageBox.warning(self, "Erro", "Arquivo nao encontrado."); return
        if path.stat().st_size == 0:
            QMessageBox.warning(self, "Arquivo vazio", "O PDF esta vazio."); return
        try:
            with open(caminho, "rb") as f:
                if f.read(5) != b"%PDF-":
                    QMessageBox.warning(self, "PDF invalido", "O arquivo nao e um PDF valido."); return
        except Exception as e:
            QMessageBox.warning(self, "Erro de leitura", f"Nao foi possivel ler o arquivo:\n{e}"); return
        tamanho_mb = path.stat().st_size / (1024 * 1024)
        if tamanho_mb > 50:
            QMessageBox.warning(self, "Arquivo muito grande", f"O arquivo excede 50MB.\nTamanho atual: {tamanho_mb:.1f}MB"); return
        self._arquivos[nome_doc] = caminho
        btn.setIcon(qta.icon("fa5s.check", color="#16A34A"))
        btn.setStyleSheet("QPushButton { background-color: #DCFCE7; color: #16A34A; border: 1.5px solid #16A34A; border-radius: 8px; padding: 8px 14px; font-size: 11px; font-weight: bold; }")
        if btn.text(): btn.setText("  PDF Anexado")
        btn.setToolTip(f"PDF anexado: {path.name}\nTamanho: {tamanho_mb:.1f}MB")

    def _preencher_dados(self):
        d = self._empresa_dados
        self.campo_nome.setText(d.get("razao_social", ""))
        cnpj = d.get("cnpj", "")
        if cnpj:
            self.campo_cnpj.setText(cnpj)
        self.campo_email.setText(d.get("email", ""))
        self.campo_telefone.setText(d.get("telefone", ""))
        self.campo_responsavel.setText(d.get("responsavel", ""))

        # Tipo de empresa
        self._toggle_tipo.selecionar(d.get("tipo_empresa", "fixa"))

        # Documentos checkbox
        if d.get("tem_contrato_social"):
            self._cards_checkbox["Contrato Social"]["selecionar_sim"]()
        else:
            self._cards_checkbox["Contrato Social"]["selecionar_nao"]()

        if d.get("tem_manual_qsma"):
            self._cards_checkbox["Manual QSMA"]["selecionar_sim"]()
        else:
            self._cards_checkbox["Manual QSMA"]["selecionar_nao"]()

        # Documentos com validade
        config = [
            ("PGR",               "pgr_data_inicial",     "pgr_periodo_dias"),
            ("PCMSO",             "pcmso_data_inicial",   "pcmso_periodo_dias"),
            ("Apolice de Seguro", "apolice_data_inicial", "apolice_periodo_dias"),
        ]
        for nome_doc, chave_ini, chave_periodo in config:
            di      = d.get(chave_ini)
            periodo = d.get(chave_periodo, 365)
            w       = self._cards_validade[nome_doc]
            combo   = w["combo_periodo"]
            opcoes  = w["opcoes_periodo"]
            combo.blockSignals(True)
            w["data_inicial"].blockSignals(True)
            idx_match = next((i for i, (_, dias) in enumerate(opcoes) if dias == periodo), 0)
            combo.setCurrentIndex(idx_match)
            if di:
                w["data_inicial"].setDate(_date_to_qdate(di))
            combo.blockSignals(False)
            w["data_inicial"].blockSignals(False)
            w["atualizar"]()

    def _on_salvar(self):
        from app.core.database import get_session
        from app.models.empresa import Empresa
        import shutil
        from app.core.settings import docs_empresa, _sanitizar
        from pathlib import Path

        nome = self.campo_nome.text().strip()
        cnpj = self.campo_cnpj.text_clean()

        if not nome or not cnpj:
            QMessageBox.warning(self, "Atencao", "Empresa e CNPJ sao obrigatorios."); return
        if not self.campo_cnpj.is_valid():
            QMessageBox.warning(self, "CNPJ invalido", "O CNPJ informado nao e valido.")
            self.campo_cnpj.setFocus(); return

        session = get_session()
        try:
            emp = session.get(Empresa, self._empresa_id) if self._empresa_id else Empresa()
            if not self._empresa_id:
                session.add(emp)

            emp.razao_social        = nome
            emp.cnpj                = cnpj
            emp.email               = self.campo_email.text().strip()
            emp.telefone            = self.campo_telefone.text().strip()
            emp.responsavel         = self.campo_responsavel.text().strip()
            emp.setor               = self.setor_nome
            emp.tem_contrato_social = self._cards_checkbox["Contrato Social"]["btn_sim"].isChecked()
            emp.tem_manual_qsma     = self._cards_checkbox["Manual QSMA"]["btn_sim"].isChecked()

            if hasattr(emp, "tipo_empresa"):
                emp.tipo_empresa = self._toggle_tipo.valor()

            config = [
                ("PGR",               ("pgr_data_inicial",     "pgr_validade",     "pgr_periodo_dias")),
                ("PCMSO",             ("pcmso_data_inicial",   "pcmso_validade",   "pcmso_periodo_dias")),
                ("Apolice de Seguro", ("apolice_data_inicial", "apolice_validade", "apolice_periodo_dias")),
            ]
            for nome_doc, (attr_ini, attr_val, attr_periodo) in config:
                w     = self._cards_validade[nome_doc]
                combo = w["combo_periodo"]
                opcoes= w["opcoes_periodo"]
                idx   = combo.currentIndex()
                dias  = opcoes[idx][1]
                ini   = _qdate_to_date(w["data_inicial"].date())
                val   = _qdate_to_date(w["data_validade"].date())
                setattr(emp, attr_ini, ini)
                setattr(emp, attr_val, val)
                if hasattr(emp, attr_periodo):
                    setattr(emp, attr_periodo, dias)
                if nome_doc == "PGR" and hasattr(emp, 'pgr_bienal'):
                    emp.pgr_bienal = (dias == 730)

            session.flush()

            for nome_doc, caminho in self._arquivos.items():
                origem = Path(caminho)
                if not origem.exists():
                    continue
                pasta_dest   = docs_empresa(emp.razao_social)
                nome_arquivo = _sanitizar(nome_doc) + origem.suffix.lower()
                destino      = pasta_dest / nome_arquivo
                shutil.copy2(origem, destino)
                self._arquivos[nome_doc] = str(destino)

            session.commit()
            self._empresa_id    = emp.id
            self._empresa_dados = self._ler_empresa(emp.id)
            self._verificar_alertas()
            QMessageBox.information(self, "Sucesso", "Empresa salva com sucesso!")

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")
        finally:
            session.close()

    def _titulo_secao(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet("color: #000000; font-size: 15px; font-weight: bold; background: transparent;")
        return lbl

    def _frame(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        return frame

    def _btn_acao(self, texto, icone, bg, cor_icone, cor_txt) -> QPushButton:
        btn = QPushButton(texto)
        btn.setIcon(qta.icon(icone, color=cor_icone))
        btn.setIconSize(QSize(13, 13))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg}; color: {cor_txt};
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 8px 16px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        return btn