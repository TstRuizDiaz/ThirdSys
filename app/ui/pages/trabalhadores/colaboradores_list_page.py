from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QColor, QAction
import qtawesome as qta
from datetime import date

# Nome exato da NR-01 salvo no banco (igual ao NRS_FIREPOINT do form)
NR01_NOME_BANCO = "NR-01 — Disposições Gerais e Gerenciamento de Riscos (Integração)"

_MENU_STYLE = """
    QMenu {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 6px 4px;
    }
    QMenu::item {
        padding: 8px 20px 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        color: #1A2B4A;
        margin: 1px 4px;
    }
    QMenu::item:selected {
        background: #EFF6FF;
        color: #2563EB;
    }
    QMenu::item:disabled {
        color: #94A3B8;
    }
    QMenu::separator {
        height: 1px;
        background: #F1F5F9;
        margin: 4px 10px;
    }
    QMenu::icon {
        padding-left: 6px;
    }
"""


class ColaboradoresListPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #F0F4F8;")
        self._colabs_cache = []
        self._setup_ui()
        self.carregar_dados()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        titulo = QLabel("Colaboradores")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1A2B4A; background: transparent;"
        )
        layout.addWidget(titulo)

        sub = QLabel("Todos os colaboradores terceirizados cadastrados")
        sub.setStyleSheet("font-size: 13px; color: #64748B; background: transparent;")
        layout.addWidget(sub)

        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFixedHeight(1)
        linha.setStyleSheet("background-color: #E2E8F0; border: none;")
        layout.addWidget(linha)

        # ── Filtros ───────────────────────────────────────────────────────────
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar por nome, CPF ou função...")
        self.campo_busca.setFixedHeight(38)
        self.campo_busca.setStyleSheet("""
            QLineEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background: #EFF6FF; }
        """)
        filtros.addWidget(self.campo_busca)

        self.combo_empresa = QComboBox()
        self.combo_empresa.setFixedHeight(38)
        self.combo_empresa.setFixedWidth(220)
        self.combo_empresa.setStyleSheet("""
            QComboBox {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QComboBox:focus { border-color: #2563EB; }
            QComboBox QAbstractItemView {
                background: white; border: 1px solid #CBD5E1;
                border-radius: 8px; selection-background-color: #EFF6FF;
                color: #1A2B4A;
            }
        """)
        filtros.addWidget(self.combo_empresa)

        self.combo_situacao = QComboBox()
        self.combo_situacao.setFixedHeight(38)
        self.combo_situacao.setFixedWidth(160)
        self.combo_situacao.addItems(["Todos", "Liberados", "Bloqueados"])
        self.combo_situacao.setStyleSheet(self.combo_empresa.styleSheet())
        filtros.addWidget(self.combo_situacao)

        btn_buscar = QPushButton("  Buscar")
        btn_buscar.setIcon(qta.icon("fa5s.search", color="white"))
        btn_buscar.setIconSize(QSize(13, 13))
        btn_buscar.setFixedHeight(38)
        btn_buscar.setCursor(Qt.PointingHandCursor)
        btn_buscar.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white;
                border: none; border-radius: 8px;
                padding: 4px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        btn_buscar.clicked.connect(self._aplicar_filtros)
        filtros.addWidget(btn_buscar)
        layout.addLayout(filtros)

        self.label_contagem = QLabel("0 colaboradores encontrados")
        self.label_contagem.setStyleSheet(
            "font-size: 12px; color: #94A3B8; background: transparent;"
        )
        layout.addWidget(self.label_contagem)

        # ── Tabela ────────────────────────────────────────────────────────────
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Nome", "Empresa", "Função", "ASO", "Integração (NR-01)", "Situação"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #E2E8F0;
                border-radius: 12px; gridline-color: #F1F5F9;
            }
            QTableWidget::item { padding: 10px; color: #1A2B4A; }
            QTableWidget::item:selected { background: #EFF6FF; }
            QTableWidget::item:alternate { background: #F8FAFC; }
            QHeaderView::section {
                background: #F8FAFC; color: #64748B;
                border: none; border-bottom: 2px solid #E2E8F0;
                padding: 10px; font-weight: bold; font-size: 12px;
            }
        """)
        self.tabela.doubleClicked.connect(self._on_duplo_clique)

        # ── Menu de contexto (clique direito) ─────────────────────────────────
        self.tabela.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabela.customContextMenuRequested.connect(self._menu_contexto)

        layout.addWidget(self.tabela)

        self.campo_busca.textChanged.connect(self._aplicar_filtros)
        self.combo_empresa.currentIndexChanged.connect(self._aplicar_filtros)
        self.combo_situacao.currentIndexChanged.connect(self._aplicar_filtros)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def carregar_dados(self):
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        from app.models.empresa import Empresa
        from sqlalchemy.orm import joinedload

        session = get_session()
        self._colabs_cache = session.query(Trabalhador).options(
            joinedload(Trabalhador.empresa)
        ).filter_by(ativo=True).all()

        for c in self._colabs_cache:
            _ = c.empresa.razao_social if c.empresa else ""

        empresas = session.query(Empresa).filter_by(status="ativo").all()
        self._empresas_nomes = {e.id: e.razao_social for e in empresas}
        session.close()

        self.combo_empresa.clear()
        self.combo_empresa.addItem("Todas as empresas", None)
        for eid, enome in self._empresas_nomes.items():
            self.combo_empresa.addItem(enome, eid)

        self._aplicar_filtros()

    def _aplicar_filtros(self):
        from app.models.treinamento import Treinamento
        from app.core.database import get_session

        termo      = self.campo_busca.text().lower()
        empresa_id = self.combo_empresa.currentData()
        situacao   = self.combo_situacao.currentText()
        hoje       = date.today()

        session = get_session()
        nr01_map: dict[int, Treinamento] = {}
        try:
            for tr in session.query(Treinamento).filter(
                Treinamento.nr_nome == NR01_NOME_BANCO
            ).all():
                nr01_map[tr.trabalhador_id] = tr
        except Exception:
            pass

        filtrados = []
        for c in self._colabs_cache:
            if empresa_id and c.empresa_id != empresa_id:
                continue
            if termo and (
                termo not in c.nome.lower()
                and termo not in (c.cpf or "").lower()
                and termo not in (c.funcao or "").lower()
            ):
                continue

            nr01         = nr01_map.get(c.id)
            aso_vencido  = bool(c.aso_validade and c.aso_validade < hoje)
            nr01_vencida = bool(not nr01 or not nr01.data_validade or nr01.data_validade < hoje)
            bloqueado    = aso_vencido or nr01_vencida

            if situacao == "Liberados"  and bloqueado:     continue
            if situacao == "Bloqueados" and not bloqueado: continue

            filtrados.append((c, nr01, bloqueado))

        session.close()
        self._popular_tabela(filtrados)
        self.label_contagem.setText(f"{len(filtrados)} colaborador(es) encontrado(s)")

    def _popular_tabela(self, dados):
        hoje = date.today()
        self.tabela.setRowCount(len(dados))

        for row, (c, nr01, bloqueado) in enumerate(dados):
            self.tabela.setItem(row, 0, QTableWidgetItem(c.nome))
            empresa = c.empresa.razao_social if c.empresa else "—"
            self.tabela.setItem(row, 1, QTableWidgetItem(empresa))
            self.tabela.setItem(row, 2, QTableWidgetItem(c.funcao or "—"))

            # ASO
            aso_txt  = c.aso_validade.strftime("%d/%m/%Y") if c.aso_validade else "—"
            aso_item = QTableWidgetItem(aso_txt)
            if c.aso_validade and c.aso_validade < hoje:
                aso_item.setForeground(QColor("#DC2626"))
            self.tabela.setItem(row, 3, aso_item)

            # NR-01
            if nr01 and nr01.data_validade:
                nr01_item = QTableWidgetItem(nr01.data_validade.strftime("%d/%m/%Y"))
                nr01_item.setForeground(QColor("#DC2626" if nr01.data_validade < hoje else "#16A34A"))
            else:
                nr01_item = QTableWidgetItem("Não cadastrada")
                nr01_item.setForeground(QColor("#DC2626"))
            self.tabela.setItem(row, 4, nr01_item)

            # Situação
            sit_item = QTableWidgetItem("BLOQUEADO" if bloqueado else "LIBERADO")
            if bloqueado:
                sit_item.setForeground(QColor("#DC2626"))
                sit_item.setBackground(QColor("#FEE2E2"))
            else:
                sit_item.setForeground(QColor("#16A34A"))
                sit_item.setBackground(QColor("#DCFCE7"))
            self.tabela.setItem(row, 5, sit_item)

            # Armazena IDs para o menu de contexto
            self.tabela.item(row, 0).setData(Qt.UserRole,     c.id)
            self.tabela.item(row, 0).setData(Qt.UserRole + 1, c.empresa_id)
            self.tabela.item(row, 0).setData(Qt.UserRole + 2, c.nome)
            self.tabela.item(row, 0).setData(Qt.UserRole + 3, bloqueado)

    # ── Menu de contexto ──────────────────────────────────────────────────────

    def _menu_contexto(self, pos: QPoint):
        index = self.tabela.indexAt(pos)
        if not index.isValid():
            return

        row  = index.row()
        item = self.tabela.item(row, 0)
        if not item:
            return

        colab_id   = item.data(Qt.UserRole)
        empresa_id = item.data(Qt.UserRole + 1)
        nome       = item.data(Qt.UserRole + 2)
        bloqueado  = item.data(Qt.UserRole + 3)

        menu = QMenu(self)
        menu.setStyleSheet(_MENU_STYLE)

        # ── Cabeçalho informativo (não clicável) ──────────────────────────────
        header_action = QAction(nome, self)
        header_action.setEnabled(False)
        header_font = header_action.font()
        header_font.setBold(True)
        header_action.setFont(header_font)
        menu.addAction(header_action)
        menu.addSeparator()

        # ── Visualizar / Editar ───────────────────────────────────────────────
        acao_ver = QAction(
            qta.icon("fa5s.eye", color="#2563EB"), "  Ver ficha completa", self
        )
        acao_editar = QAction(
            qta.icon("fa5s.user-edit", color="#2563EB"), "  Editar colaborador", self
        )
        acao_ver.triggered.connect(lambda: self._on_ver(colab_id, empresa_id))
        acao_editar.triggered.connect(lambda: self._on_editar(colab_id, empresa_id))
        menu.addAction(acao_ver)
        menu.addAction(acao_editar)
        menu.addSeparator()

        # ── Documentos ────────────────────────────────────────────────────────
        acao_docs = QAction(
            qta.icon("fa5s.file-alt", color="#64748B"), "  Ver documentos", self
        )
        acao_trein = QAction(
            qta.icon("fa5s.graduation-cap", color="#64748B"), "  Ver treinamentos", self
        )
        acao_docs.triggered.connect(lambda: self._on_editar(colab_id, empresa_id, aba=1))
        acao_trein.triggered.connect(lambda: self._on_editar(colab_id, empresa_id, aba=2))
        menu.addAction(acao_docs)
        menu.addAction(acao_trein)
        menu.addSeparator()

        # ── Status ────────────────────────────────────────────────────────────
        if bloqueado:
            acao_liberar = QAction(
                qta.icon("fa5s.unlock", color="#16A34A"), "  Liberar colaborador", self
            )
            acao_liberar.triggered.connect(lambda: self._on_liberar(colab_id, nome))
            menu.addAction(acao_liberar)
        else:
            acao_bloquear = QAction(
                qta.icon("fa5s.lock", color="#D97706"), "  Bloquear colaborador", self
            )
            acao_bloquear.triggered.connect(lambda: self._on_bloquear(colab_id, nome))
            menu.addAction(acao_bloquear)

        acao_inativar = QAction(
            qta.icon("fa5s.user-slash", color="#D97706"), "  Inativar colaborador", self
        )
        acao_inativar.triggered.connect(lambda: self._on_inativar(colab_id, nome))
        menu.addAction(acao_inativar)
        menu.addSeparator()

        # ── Zona de perigo ────────────────────────────────────────────────────
        acao_excluir = QAction(
            qta.icon("fa5s.trash-alt", color="#DC2626"), "  Excluir permanentemente", self
        )
        acao_excluir.triggered.connect(lambda: self._on_excluir(colab_id, nome))
        menu.addAction(acao_excluir)

        menu.exec(self.tabela.viewport().mapToGlobal(pos))

    # ── Ações CRUD ────────────────────────────────────────────────────────────

    def _on_ver(self, colab_id: int, empresa_id: int):
        self.window().navegar_para(f"colaborador:{colab_id}|{empresa_id or 0}")

    def _on_editar(self, colab_id: int, empresa_id: int, aba: int = 0):
        """Navega para o form de colaborador via main_window, com aba opcional."""
        chave = f"colaborador:{colab_id}|{empresa_id or 0}"
        self.window().navegar_para(chave)
        # Após navegar, seleciona a aba correta se necessário
        if aba > 0:
            mw = self.window()
            if hasattr(mw, "_colab_page") and mw._colab_page:
                mw._colab_page.tabs.setCurrentIndex(aba)

    def _on_liberar(self, colab_id: int, nome: str):
        """Remove bloqueios manuais ativos para o colaborador."""
        resp = QMessageBox.question(
            self, "Liberar colaborador",
            f"Deseja remover os bloqueios manuais de <b>{nome}</b>?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            from app.core.database import get_session
            from app.models.bloqueio import Bloqueio
            session = get_session()
            session.query(Bloqueio).filter_by(
                trabalhador_id=colab_id, tipo="manual", ativo=True
            ).update({"ativo": False})
            session.commit()
            session.close()
            self.carregar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível liberar: {e}")

    def _on_bloquear(self, colab_id: int, nome: str):
        """Abre o modal de bloqueio da portaria."""
        try:
            from app.ui.pages.portaria.portaria_page import ModalBloqueio
            modal = ModalBloqueio(colab_id, nome, parent=self)
            if modal.exec():
                self.carregar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir modal de bloqueio: {e}")

    def _on_inativar(self, colab_id: int, nome: str):
        resp = QMessageBox.question(
            self, "Inativar colaborador",
            f"Deseja inativar <b>{nome}</b>?<br>"
            f"<span style='color:#64748B;font-size:12px'>"
            f"O colaborador não aparecerá mais nas listagens ativas.</span>",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            session = get_session()
            colab = session.get(Trabalhador, colab_id)
            if colab:
                colab.ativo = False
                session.commit()
            session.close()
            self.carregar_dados()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao inativar: {e}")

    def _on_excluir(self, colab_id: int, nome: str):
        resp = QMessageBox.warning(
            self, "Excluir colaborador",
            f"Tem certeza que deseja excluir permanentemente <b>{nome}</b>?<br><br>"
            f"<span style='color:#DC2626'>"
            f"⚠ Esta ação remove todos os dados, documentos e treinamentos "
            f"associados e <b>não pode ser desfeita</b>.</span>",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        # Segunda confirmação para exclusão permanente
        resp2 = QMessageBox.warning(
            self, "Confirmar exclusão",
            f"Digite 'CONFIRMAR' mentalmente — ao clicar em Sim, "
            f"<b>{nome}</b> será removido permanentemente do sistema.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp2 != QMessageBox.Yes:
            return

        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            from app.models.treinamento import Treinamento
            from app.models.bloqueio import Bloqueio
            session = get_session()
            # Remove dependências antes do colaborador
            session.query(Treinamento).filter_by(trabalhador_id=colab_id).delete()
            session.query(Bloqueio).filter_by(trabalhador_id=colab_id).delete()
            colab = session.get(Trabalhador, colab_id)
            if colab:
                session.delete(colab)
            session.commit()
            session.close()
            self.carregar_dados()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")

    # ── Duplo clique → ver ficha ──────────────────────────────────────────────

    def _on_duplo_clique(self, index):
        row  = index.row()
        item = self.tabela.item(row, 0)
        if item:
            colab_id   = item.data(Qt.UserRole)
            empresa_id = item.data(Qt.UserRole + 1)
            self.window().navegar_para(f"colaborador:{colab_id}|{empresa_id or 0}")