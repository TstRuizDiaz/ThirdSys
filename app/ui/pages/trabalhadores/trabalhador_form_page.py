from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout,
    QLineEdit, QDateEdit, QFileDialog, QMessageBox,
    QComboBox, QTabWidget, QDialog
)
from PySide6.QtCore import Qt, Signal, QSize, QDate, QTimer
from PySide6.QtGui import QFont, QPixmap, QImage
import qtawesome as qta
from datetime import date, timedelta

# ── Importação do módulo de foto facial ───────────────────────────────────────
from app.ui.pages.foto_facial_widget import FotoFacialWidget


# ─────────────────────────────────────────────────────────────────────────────
# NRs exibidas no formulário
# CHAVE  = nr_nome exato salvo no banco (igual ao NRS_BRASIL do model)
# VALOR  = label curto exibido na tela
# ─────────────────────────────────────────────────────────────────────────────
NRS_FIREPOINT: list[tuple[str, str]] = [
    (
        "NR-01 — Disposições Gerais e Gerenciamento de Riscos (Integração)",
        "NR-01 – GRO/PGR e ordens de serviço",
    ),
    (
        "NR-05 — Comissão Interna de Prevenção de Acidentes (CIPA)",
        "NR-05 – CIPA",
    ),
    (
        "NR-06 — Equipamentos de Proteção Individual (EPI)",
        "NR-06 – Uso e conservação de EPI",
    ),
    (
        "NR-10 — Segurança em Instalações e Serviços em Eletricidade",
        "NR-10 – Segurança em eletricidade",
    ),
    (
        "NR-11 — Transporte, Movimentação, Armazenagem e Manuseio de Materiais",
        "NR-11 – Operação de empilhadeira/paleteira",
    ),
    (
        "NR-12 — Segurança no Trabalho em Máquinas e Equipamentos",
        "NR-12 – Máquinas e equipamentos",
    ),
    (
        "NR-18 — Segurança e Saúde no Trabalho na Indústria da Construção",
        "NR-18 – Construção civil",
    ),
    (
        "NR-20 — Segurança e Saúde no Trabalho com Inflamáveis e Combustíveis",
        "NR-20 – Inflamáveis e combustíveis",
    ),
    (
        "NR-23 — Proteção Contra Incêndios",
        "NR-23 – Brigada/incêndio",
    ),
    (
        "NR-32 — Segurança e Saúde no Trabalho em Serviços de Saúde",
        "NR-32 – Área da saúde",
    ),
    (
        "NR-33 — Segurança e Saúde nos Trabalhos em Espaços Confinados",
        "NR-33 – Espaço confinado",
    ),
    (
        "NR-35 — Trabalho em Altura",
        "NR-35 – Trabalho em altura",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# CPF LineEdit com máscara e validação
# ─────────────────────────────────────────────────────────────────────────────
class CPFLineEdit(QLineEdit):
    """QLineEdit com máscara xxx.xxx.xxx-xx e validação de CPF."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("999.999.999-99;_")
        self.setMaxLength(14)
        self.setFixedHeight(36)
        self.setStyleSheet("""
            QLineEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background: #EFF6FF; }
            QLineEdit[invalid="true"] { border-color: #DC2626; background: #FEF2F2; }
            QLineEdit[valid="true"]   { border-color: #16A34A; background: #F0FDF4; }
        """)
        self.textChanged.connect(self._on_changed)

    def _on_changed(self, text: str):
        digits = self._digits(text)
        if len(digits) == 11:
            ok = self._validar_cpf(digits)
            self.setProperty("valid",   "true"  if ok else "false")
            self.setProperty("invalid", "false" if ok else "true")
        else:
            self.setProperty("valid",   "false")
            self.setProperty("invalid", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def _digits(self, text: str) -> str:
        return ''.join(c for c in text if c.isdigit())

    def text_clean(self) -> str:
        return self._digits(self.text())

    def is_valid(self) -> bool:
        d = self.text_clean()
        return len(d) == 11 and self._validar_cpf(d)

    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
            return False

        def dv(nums, pesos):
            s = sum(int(n) * p for n, p in zip(nums, pesos))
            r = s % 11
            return 0 if r < 2 else 11 - r

        if dv(cpf[:9],  range(10, 1, -1)) != int(cpf[9]):
            return False
        if dv(cpf[:10], range(11, 1, -1)) != int(cpf[10]):
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZADOR INTERNO DE ARQUIVOS
# ─────────────────────────────────────────────────────────────────────────────

class PaginaPDF(QLabel):
    def __init__(self, pixmap_original: QPixmap, parent=None):
        super().__init__(parent)
        self._pixmap_original = pixmap_original
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setStyleSheet("background: white; border-radius: 4px;")

    def atualizar_escala(self, largura_disponivel: int):
        margem = 48
        largura_alvo = max(200, largura_disponivel - margem)
        if self._pixmap_original.width() > largura_alvo:
            scaled = self._pixmap_original.scaledToWidth(largura_alvo, Qt.SmoothTransformation)
        else:
            scaled = self._pixmap_original
        self.setPixmap(scaled)
        self.setFixedSize(scaled.size())


class VisualizadorArquivo(QDialog):
    def __init__(self, caminho: str, titulo: str, parent=None):
        super().__init__(parent)
        self.caminho = caminho
        self._paginas_pdf: list[PaginaPDF] = []
        self._scroll_pdf = None
        self.setWindowTitle(f"📄 {titulo}")
        self.setMinimumSize(700, 600)
        self.resize(920, 760)
        self.setStyleSheet("background: #1E293B;")
        self._setup_ui()

    def _setup_ui(self):
        from pathlib import Path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QFrame()
        toolbar.setFixedHeight(52)
        toolbar.setStyleSheet("background: #0F172A; border: none;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(16, 0, 16, 0)
        tl.setSpacing(8)

        nome = Path(self.caminho).name
        lbl_nome = QLabel(f"  {nome}")
        lbl_nome.setStyleSheet("color: #CBD5E1; font-size: 13px; font-weight: bold; background: transparent;")
        tl.addWidget(lbl_nome)
        tl.addStretch()

        btn_pasta = QPushButton("  Abrir pasta")
        btn_pasta.setIcon(qta.icon("fa5s.folder-open", color="#94A3B8"))
        btn_pasta.setIconSize(QSize(12, 12))
        btn_pasta.setCursor(Qt.PointingHandCursor)
        btn_pasta.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: #94A3B8;
                border: 1px solid #334155; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #334155; color: #CBD5E1; }
        """)
        btn_pasta.clicked.connect(self._abrir_pasta)
        tl.addWidget(btn_pasta)

        btn_externo = QPushButton("  Abrir no app padrão")
        btn_externo.setIcon(qta.icon("fa5s.external-link-alt", color="#94A3B8"))
        btn_externo.setIconSize(QSize(12, 12))
        btn_externo.setCursor(Qt.PointingHandCursor)
        btn_externo.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: #94A3B8;
                border: 1px solid #334155; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #334155; color: #CBD5E1; }
        """)
        btn_externo.clicked.connect(self._abrir_externo)
        tl.addWidget(btn_externo)

        btn_fechar = QPushButton("  Fechar")
        btn_fechar.setIcon(qta.icon("fa5s.times", color="#94A3B8"))
        btn_fechar.setIconSize(QSize(12, 12))
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: #94A3B8;
                border: 1px solid #334155; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #DC2626; color: white; border-color: #DC2626; }
        """)
        btn_fechar.clicked.connect(self.reject)
        tl.addWidget(btn_fechar)
        layout.addWidget(toolbar)

        ext = Path(self.caminho).suffix.lower()
        if ext == ".pdf":
            self._carregar_pdf(layout)
        elif ext in (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"):
            self._carregar_imagem(layout)
        else:
            lbl = QLabel("Tipo de arquivo não suportado para visualização.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #94A3B8; font-size: 14px;")
            layout.addWidget(lbl)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._paginas_pdf and self._scroll_pdf:
            largura = self._scroll_pdf.viewport().width()
            for pagina in self._paginas_pdf:
                pagina.atualizar_escala(largura)

    def _carregar_pdf(self, layout):
        try:
            import fitz
            self._scroll_pdf = QScrollArea()
            self._scroll_pdf.setWidgetResizable(True)
            self._scroll_pdf.setStyleSheet("background: #1E293B; border: none;")

            container = QWidget()
            container.setStyleSheet("background: #1E293B;")
            vl = QVBoxLayout(container)
            vl.setContentsMargins(24, 24, 24, 24)
            vl.setSpacing(20)
            vl.setAlignment(Qt.AlignHCenter)

            doc = fitz.open(self.caminho)
            total = len(doc)
            for num_pag in range(total):
                pagina = doc[num_pag]
                mat = fitz.Matrix(2.0, 2.0)
                pix = pagina.get_pixmap(matrix=mat, alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap_original = QPixmap.fromImage(img)
                lbl_pagina = PaginaPDF(pixmap_original)
                self._paginas_pdf.append(lbl_pagina)
                vl.addWidget(lbl_pagina, alignment=Qt.AlignHCenter)
                if total > 1:
                    lbl_num = QLabel(f"Página {num_pag + 1} de {total}")
                    lbl_num.setAlignment(Qt.AlignCenter)
                    lbl_num.setStyleSheet("color: #64748B; font-size: 11px; background: transparent;")
                    vl.addWidget(lbl_num)
            doc.close()
            vl.addStretch()
            self._scroll_pdf.setWidget(container)
            layout.addWidget(self._scroll_pdf)
            QTimer.singleShot(50, self._escala_inicial)
        except ImportError:
            self._fallback_sem_pymupdf(layout)

    def _escala_inicial(self):
        if self._scroll_pdf and self._paginas_pdf:
            largura = self._scroll_pdf.viewport().width()
            for pagina in self._paginas_pdf:
                pagina.atualizar_escala(largura)

    def _carregar_imagem(self, layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: #1E293B; border: none;")
        container = QWidget()
        container.setStyleSheet("background: #1E293B;")
        vl = QVBoxLayout(container)
        vl.setAlignment(Qt.AlignCenter)
        vl.setContentsMargins(24, 24, 24, 24)
        pixmap = QPixmap(self.caminho)
        if pixmap.isNull():
            lbl = QLabel("Não foi possível carregar a imagem.")
            lbl.setStyleSheet("color: #94A3B8; font-size: 14px;")
            vl.addWidget(lbl)
        else:
            lbl_img = QLabel()
            lbl_img.setAlignment(Qt.AlignCenter)
            lbl_img.setStyleSheet("background: transparent;")
            lbl_img.setPixmap(
                pixmap.scaledToWidth(860, Qt.SmoothTransformation)
                if pixmap.width() > 860 else pixmap
            )
            vl.addWidget(lbl_img)
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _fallback_sem_pymupdf(self, layout):
        frame = QFrame()
        frame.setStyleSheet("background: #0F172A;")
        vl = QVBoxLayout(frame)
        vl.setAlignment(Qt.AlignCenter)
        vl.setSpacing(12)
        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.file-pdf", color="#DC2626").pixmap(48, 48))
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("background: transparent;")
        vl.addWidget(ic)
        lbl = QLabel("Visualização de PDF requer PyMuPDF.")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #94A3B8; font-size: 14px; background: transparent;")
        vl.addWidget(lbl)
        layout.addWidget(frame)

    def _abrir_pasta(self):
        from pathlib import Path
        from app.core.settings import abrir_pasta
        abrir_pasta(Path(self.caminho).parent)

    def _abrir_externo(self):
        import subprocess, sys
        try:
            if sys.platform == "win32":
                import os
                os.startfile(self.caminho)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.caminho])
            else:
                subprocess.Popen(["xdg-open", self.caminho])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")


# ─────────────────────────────────────────────────────────────────────────────
# FORMULÁRIO DO TRABALHADOR
# ─────────────────────────────────────────────────────────────────────────────

class TrabalhadorFormPage(QWidget):
    voltar = Signal()

    def __init__(self, empresa=None, trabalhador=None, parent=None):
        super().__init__(parent)
        self.empresa = empresa
        self.trabalhador = trabalhador
        self._arquivos = {}
        self._widget_foto = None  # instanciado em _aba_dados()

        self._pgr_dias = self._ler_pgr_dias()

        self.setStyleSheet("background-color: #F0F4F8;")
        self._setup_ui()
        if trabalhador:
            self._preencher_dados()

    def _ler_pgr_dias(self) -> int:
        if not self.empresa:
            return 365
        try:
            from app.core.database import get_session
            from app.models.empresa import Empresa
            session = get_session()
            e = session.get(Empresa, self.empresa.id)
            if e and hasattr(e, 'pgr_periodo_dias') and e.pgr_periodo_dias:
                dias = int(e.pgr_periodo_dias)
            elif e and hasattr(e, 'pgr_bienal') and e.pgr_bienal:
                dias = 730
            else:
                dias = 365
            session.close()
            return dias
        except Exception:
            return 365

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        btn_voltar = self._btn_acao("  Voltar", "fa5s.arrow-left", "#F1F5F9", "#64748B", "#64748B")
        btn_voltar.clicked.connect(self.voltar.emit)
        header.addWidget(btn_voltar)
        header.addStretch()

        nome_empresa = self.empresa.razao_social if self.empresa else "—"
        titulo = QLabel(f"Colaborador — {nome_empresa}")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A2B4A; background: transparent;")
        header.addWidget(titulo)
        header.addStretch()

        btn_pasta = self._btn_acao("  Abrir pasta", "fa5s.folder-open", "#F1F5F9", "#64748B", "#64748B")
        btn_pasta.clicked.connect(self._on_abrir_pasta_colab)
        header.addWidget(btn_pasta)

        btn_salvar = self._btn_acao("  Salvar", "fa5s.save", "#16A34A", "white", "white")
        btn_salvar.clicked.connect(self._on_salvar)
        header.addWidget(btn_salvar)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; }
            QTabBar::tab {
                background: #F1F5F9; color: #64748B;
                border: 1px solid #E2E8F0;
                border-radius: 8px 8px 0 0;
                padding: 8px 20px; font-weight: bold; font-size: 13px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: white; color: #2563EB;
                border-bottom: 2px solid #2563EB;
            }
        """)

        self.tabs.addTab(self._aba_dados(),        "  Dados Pessoais")
        self.tabs.addTab(self._aba_documentos(),   "  Documentos")
        self.tabs.addTab(self._aba_treinamentos(), "  Treinamentos")
        layout.addWidget(self.tabs)

    def _on_abrir_pasta_colab(self):
        try:
            from app.core.settings import docs_colaborador, abrir_pasta
            nome_empresa = self.empresa.razao_social if self.empresa else "Sem Empresa"
            nome_colab   = self.campo_nome.text().strip() or (
                self.trabalhador.nome if self.trabalhador else "Colaborador"
            )
            pasta = docs_colaborador(nome_empresa, nome_colab)
            abrir_pasta(pasta)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir a pasta:\n{e}")

    # ─────────────────────────────────────────────
    # ABA 1 — DADOS PESSOAIS (com foto facial)
    # ─────────────────────────────────────────────
    def _aba_dados(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 16, 0, 16)

        layout.addWidget(self._titulo_secao("Dados Pessoais"))

        # ── Linha principal: foto (esquerda) + campos (direita) ───────────────
        linha_topo = QHBoxLayout()
        linha_topo.setSpacing(20)
        linha_topo.setAlignment(Qt.AlignTop)

        # ── FOTO FACIAL ───────────────────────────────────────────────────────
        nome_empresa = self.empresa.razao_social if self.empresa else ""
        nome_colab   = self.trabalhador.nome if self.trabalhador else ""
        self._widget_foto = FotoFacialWidget(
            nome_empresa=nome_empresa,
            nome_colab=nome_colab,
            parent=self
        )
        linha_topo.addWidget(self._widget_foto, alignment=Qt.AlignTop)

        # ── CAMPOS DE DADOS ───────────────────────────────────────────────────
        frame = self._frame()
        grid = QGridLayout(frame)
        grid.setSpacing(12)
        grid.setContentsMargins(20, 20, 20, 20)

        lbl_nome = self._lbl_campo("Nome Completo *")
        self.campo_nome = QLineEdit()
        self.campo_nome.setFixedHeight(36)
        self.campo_nome.setStyleSheet(self._estilo_line_edit())
        # Atualiza contexto da foto quando o nome é alterado
        self.campo_nome.textChanged.connect(self._on_nome_changed)
        grid.addWidget(lbl_nome, 0, 0)
        grid.addWidget(self.campo_nome, 0, 1)

        lbl_cpf = self._lbl_campo("CPF *")
        self.campo_cpf = CPFLineEdit()
        grid.addWidget(lbl_cpf, 1, 0)
        grid.addWidget(self.campo_cpf, 1, 1)

        lbl_funcao = self._lbl_campo("Função *")
        self.campo_funcao = QLineEdit()
        self.campo_funcao.setFixedHeight(36)
        self.campo_funcao.setStyleSheet(self._estilo_line_edit())
        grid.addWidget(lbl_funcao, 2, 0)
        grid.addWidget(self.campo_funcao, 2, 1)

        lbl_nasc = self._lbl_campo("Nascimento")
        self.campo_nascimento = QDateEdit()
        self.campo_nascimento.setCalendarPopup(True)
        self.campo_nascimento.setButtonSymbols(QDateEdit.NoButtons)
        self.campo_nascimento.setDate(QDate.currentDate().addYears(-18))
        self.campo_nascimento.setFixedHeight(36)
        self.campo_nascimento.setStyleSheet(self._estilo_date_edit())
        self.campo_nascimento.setMaximumDate(QDate.currentDate().addYears(-18))
        self.campo_nascimento.dateChanged.connect(self._validar_nascimento)
        grid.addWidget(lbl_nasc, 3, 0)
        grid.addWidget(self.campo_nascimento, 3, 1)

        lbl_adm = self._lbl_campo("Admissão")
        self.campo_admissao = QDateEdit()
        self.campo_admissao.setCalendarPopup(True)
        self.campo_admissao.setButtonSymbols(QDateEdit.NoButtons)
        self.campo_admissao.setDate(QDate.currentDate())
        self.campo_admissao.setFixedHeight(36)
        self.campo_admissao.setStyleSheet(self._estilo_date_edit())
        self.campo_admissao.setMaximumDate(QDate.currentDate())
        self.campo_admissao.dateChanged.connect(self._validar_admissao)
        grid.addWidget(lbl_adm, 4, 0)
        grid.addWidget(self.campo_admissao, 4, 1)

        linha_topo.addWidget(frame, 1)
        layout.addLayout(linha_topo)

        layout.addWidget(self._titulo_secao(
            f"ASO — Atestado de Saúde Ocupacional "
            f"({'Bienal' if self._pgr_dias == 730 else 'Anual'})"
        ))
        layout.addWidget(self._secao_aso())
        layout.addWidget(self._titulo_secao("Documentos Obrigatórios"))
        layout.addWidget(self._secao_checkboxes())
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _on_nome_changed(self, texto: str):
        """Atualiza o contexto da foto quando o nome do colaborador muda."""
        if self._widget_foto:
            nome_empresa = self.empresa.razao_social if self.empresa else ""
            self._widget_foto.atualizar_contexto(nome_empresa, texto.strip())

    # ── Validações de data ────────────────────────────────────────────────────
    def _validar_nascimento(self, qdate: QDate):
        hoje = date.today()
        d = date(qdate.year(), qdate.month(), qdate.day())
        if d > hoje:
            QMessageBox.warning(self, "Data inválida",
                "A data de nascimento não pode ser uma data futura.")
            self.campo_nascimento.setDate(QDate.currentDate().addYears(-18))
            return
        idade = (hoje - d).days // 365
        if idade < 18:
            QMessageBox.warning(self, "Menor de idade",
                "Colaboradores menores de 18 anos não são permitidos.\n"
                f"Idade calculada: {idade} anos.")
            self.campo_nascimento.setDate(QDate.currentDate().addYears(-18))

    def _validar_admissao(self, qdate: QDate):
        hoje = date.today()
        d = date(qdate.year(), qdate.month(), qdate.day())
        if d > hoje:
            QMessageBox.warning(self, "Data inválida",
                "A data de admissão não pode ser uma data futura.")
            self.campo_admissao.setDate(QDate.currentDate())

    def _validar_data_aso(self, qdate: QDate):
        hoje = date.today()
        d = date(qdate.year(), qdate.month(), qdate.day())
        if d > hoje:
            QMessageBox.warning(self, "Data inválida",
                "A data inicial do ASO não pode ser uma data futura.")
            self.aso_ini.setDate(QDate.currentDate())

    # ─────────────────────────────────────────────
    # SEÇÃO ASO
    # ─────────────────────────────────────────────
    def _secao_aso(self) -> QFrame:
        frame = self._frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        cab = QHBoxLayout()
        for texto, largura in [
            ("Documento", 220), ("Data Inicial", 130),
            ("Vigência", 130), ("Status", 150), ("Dias", 70), ("Arq.", 80)
        ]:
            lbl = QLabel(texto)
            lbl.setFixedWidth(largura)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "color: #64748B; font-size: 11px; font-weight: bold; "
                "background: transparent; border: none;"
            )
            cab.addWidget(lbl)
        cab.addStretch()
        layout.addLayout(cab)
        self._separador(layout)

        row = QHBoxLayout()
        row.setContentsMargins(0, 10, 0, 10)
        row.setSpacing(9)

        periodo_txt = "Bienal (2 anos)" if self._pgr_dias == 730 else "Anual (1 ano)"
        lbl = QLabel(f"ASO — {periodo_txt}")
        lbl.setFixedWidth(220)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #1A2B4A; font-size: 12px; background: transparent;")
        row.addWidget(lbl)

        self.aso_ini = QDateEdit()
        self.aso_ini.setCalendarPopup(True)
        self.aso_ini.setButtonSymbols(QDateEdit.NoButtons)
        self.aso_ini.setFixedWidth(130)
        self.aso_ini.setDate(QDate.currentDate())
        self.aso_ini.setMaximumDate(QDate.currentDate())
        self.aso_ini.setStyleSheet("""
            QDateEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 8px; font-size: 12px;
            }
            QDateEdit:focus { border-color: #2563EB; }
        """)
        row.addWidget(self.aso_ini)

        self.aso_val = QDateEdit()
        self.aso_val.setReadOnly(True)
        self.aso_val.setButtonSymbols(QDateEdit.NoButtons)
        self.aso_val.setFixedWidth(130)
        self.aso_val.setStyleSheet("""
            QDateEdit {
                background: #F1F5F9; color: #64748B;
                border: 1.5px solid #E2E8F0; border-radius: 8px;
                padding: 4px 8px; font-size: 12px;
            }
        """)
        row.addWidget(self.aso_val)

        self.aso_status = QLabel("DENTRO DO PRAZO")
        self.aso_status.setFixedWidth(150)
        self.aso_status.setAlignment(Qt.AlignCenter)
        self.aso_status.setStyleSheet(
            "background: #DCFCE7; color: #16A34A; border-radius: 6px; "
            "padding: 4px 8px; font-size: 11px; font-weight: bold;"
        )
        row.addWidget(self.aso_status)

        self.aso_dias = QLabel("—")
        self.aso_dias.setFixedWidth(70)
        self.aso_dias.setAlignment(Qt.AlignCenter)
        self.aso_dias.setStyleSheet(
            "color: #1A2B4A; font-size: 13px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        row.addWidget(self.aso_dias)
        row.addWidget(self._btn_upload("ASO"))
        row.addStretch()
        layout.addLayout(row)

        def atualizar_aso():
            qdi = self.aso_ini.date()
            ini = date(qdi.year(), qdi.month(), qdi.day())
            venc = ini + timedelta(days=self._pgr_dias)
            self.aso_val.setDate(QDate(venc.year, venc.month, venc.day))
            dias = (venc - date.today()).days
            self.aso_dias.setText(str(abs(dias)) if dias < 0 else str(dias))
            if dias < 0:
                self.aso_status.setText("VENCIDO")
                self.aso_status.setStyleSheet(
                    "background: #FEE2E2; color: #DC2626; border-radius: 6px; "
                    "padding: 4px 8px; font-size: 11px; font-weight: bold;"
                )
                self.aso_dias.setStyleSheet(
                    "color: #DC2626; font-size: 13px; font-weight: bold; background: transparent;"
                )
            elif dias <= 30:
                self.aso_status.setText("A VENCER")
                self.aso_status.setStyleSheet(
                    "background: #FEF3C7; color: #D97706; border-radius: 6px; "
                    "padding: 4px 8px; font-size: 11px; font-weight: bold;"
                )
                self.aso_dias.setStyleSheet(
                    "color: #D97706; font-size: 13px; font-weight: bold; background: transparent;"
                )
            else:
                self.aso_status.setText("DENTRO DO PRAZO")
                self.aso_status.setStyleSheet(
                    "background: #DCFCE7; color: #16A34A; border-radius: 6px; "
                    "padding: 4px 8px; font-size: 11px; font-weight: bold;"
                )
                self.aso_dias.setStyleSheet(
                    "color: #16A34A; font-size: 13px; font-weight: bold; background: transparent;"
                )

        def on_aso_changed(qdate):
            self._validar_data_aso(qdate)
            atualizar_aso()

        self.aso_ini.dateChanged.connect(on_aso_changed)
        atualizar_aso()
        return frame

    # ─────────────────────────────────────────────
    # SEÇÃO CHECKBOXES
    # ─────────────────────────────────────────────
    def _secao_checkboxes(self) -> QFrame:
        frame = self._frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)

        cab = QHBoxLayout()
        for texto, largura in [("Documento", 250), ("SIM", 70), ("NÃO", 70), ("N/A", 70)]:
            lbl = QLabel(texto)
            lbl.setFixedWidth(largura)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "color: #64748B; font-size: 11px; font-weight: bold; "
                "background: transparent; border: none;"
            )
            cab.addWidget(lbl)
        cab.addStretch()
        layout.addLayout(cab)
        self._separador(layout)

        self._chk_widgets = {}
        docs = [
            ("Ordem de Serviço (NR-01)", "ordem_servico"),
            ("Ficha de Registro",         "ficha_registro"),
            ("Ficha de EPI",              "ficha_epi"),
            ("CNH",                       "cnh"),
        ]
        for nome_doc, attr in docs:
            widgets = self._linha_tri_estado(layout, nome_doc, attr)
            self._chk_widgets[attr] = widgets
            self._separador(layout)

        return frame

    def _linha_tri_estado(self, layout, nome_doc: str, attr: str) -> dict:
        row = QHBoxLayout()
        row.setContentsMargins(2, 8, 0, 8)
        row.setSpacing(4)

        lbl = QLabel(nome_doc)
        lbl.setFixedWidth(250)
        lbl.setStyleSheet("color: #1A2B4A; font-size: 13px; background: transparent; border: none;")
        row.addWidget(lbl)

        btns = {}
        opcoes = [
            ("SIM", "sim", "#DCFCE7", "#16A34A"),
            ("NÃO", "nao", "#FEE2E2", "#DC2626"),
            ("N/A", "na",  "#F1F5F9", "#64748B"),
        ]
        grupo = []
        for texto, valor, bg_ativo, cor_ativo in opcoes:
            btn = QPushButton(texto)
            btn.setFixedSize(70, 35)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{ background: #F1F5F9; color: #94A3B8; border-radius: 6px; }}
                QPushButton:checked {{
                    background: {bg_ativo}; color: {cor_ativo};
                    border: 1.5px solid {cor_ativo};
                }}
            """)

            def on_toggle(checked, b=btn, g=grupo):
                if checked:
                    for other in g:
                        if other is not b:
                            other.setChecked(False)

            btn.toggled.connect(on_toggle)
            grupo.append(btn)
            btns[valor] = btn

            c = QWidget()
            c.setFixedWidth(70)
            c.setStyleSheet("background: transparent;")
            cl = QHBoxLayout(c)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.addWidget(btn)
            row.addWidget(c)

        btns["nao"].setChecked(True)
        setattr(self, f"chk_{attr}", btns)
        row.addStretch()
        layout.addLayout(row)
        return btns

    # ─────────────────────────────────────────────
    # ABA 2 — DOCUMENTOS
    # ─────────────────────────────────────────────
    def _aba_documentos(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 16, 0, 16)

        btn_abrir = QPushButton("  Abrir pasta no explorador")
        btn_abrir.setIcon(qta.icon("fa5s.folder-open", color="#2563EB"))
        btn_abrir.setIconSize(QSize(14, 14))
        btn_abrir.setCursor(Qt.PointingHandCursor)
        btn_abrir.setStyleSheet("""
            QPushButton {
                background: #EFF6FF; color: #2563EB;
                border: 1.5px solid #2563EB; border-radius: 8px;
                padding: 8px 16px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background: #DBEAFE; }
        """)
        btn_abrir.clicked.connect(self._on_abrir_pasta_colab)
        layout.addWidget(btn_abrir)

        frame = self._frame()
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        docs_upload = [
            "Crachá / RG",
            "Ficha de Registro",
            "Ficha de EPI",
            "Ordem de Serviço (NR-01)",
            "Certificado/Diploma (PLH)",
            "Certificados Normativos",
        ]

        for doc in docs_upload:
            row = QHBoxLayout()
            lbl = QLabel(doc)
            lbl.setStyleSheet("color: #1A2B4A; font-size: 13px; background: transparent; border: none;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(self._btn_upload(doc))
            fl.addLayout(row)
            self._separador(fl)

        layout.addWidget(frame)
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    # ─────────────────────────────────────────────
    # ABA 3 — TREINAMENTOS
    # ─────────────────────────────────────────────
    def _aba_treinamentos(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 16, 0, 16)

        busca_frame = QFrame()
        busca_frame.setStyleSheet("background: transparent;")
        busca_layout = QHBoxLayout(busca_frame)
        busca_layout.setContentsMargins(0, 0, 0, 0)

        self.busca_nr = QLineEdit()
        self.busca_nr.setPlaceholderText("Buscar NR... ex: NR-35, altura, elétrica")
        self.busca_nr.setFixedHeight(38)
        self.busca_nr.setStyleSheet("""
            QLineEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background: #EFF6FF; }
        """)
        ic = QLabel()
        ic.setPixmap(qta.icon("fa5s.search", color="#94A3B8").pixmap(16, 16))
        ic.setStyleSheet("background: transparent;")
        busca_layout.addWidget(ic)
        busca_layout.addWidget(self.busca_nr)
        layout.addWidget(busca_frame)

        self._frame_nrs = self._frame()
        self._layout_nrs = QVBoxLayout(self._frame_nrs)
        self._layout_nrs.setContentsMargins(20, 16, 20, 16)
        self._layout_nrs.setSpacing(0)

        cab = QHBoxLayout()
        for texto, largura in [
            ("Treinamento", 320), ("Data Inicial", 130),
            ("Validade", 130), ("Status", 150), ("Dias", 60)
        ]:
            lbl = QLabel(texto)
            lbl.setFixedWidth(largura)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "color: #64748B; font-size: 11px; font-weight: bold; "
                "background: transparent; border: none;"
            )
            cab.addWidget(lbl)
        cab.addStretch()
        self._layout_nrs.addLayout(cab)
        self._separador(self._layout_nrs)

        self._linhas_nrs = {}
        self._todas_linhas_nrs = []

        for nr_nome_banco, label_tela in NRS_FIREPOINT:
            widgets = self._linha_nr(nr_nome_banco, label_tela)
            self._linhas_nrs[nr_nome_banco] = widgets
            self._todas_linhas_nrs.append((nr_nome_banco, label_tela, widgets))

        layout.addWidget(self._frame_nrs)
        layout.addStretch()
        scroll.setWidget(container)

        self.busca_nr.textChanged.connect(self._filtrar_nrs)
        return scroll

    def _linha_nr(self, nr_nome_banco: str, label_tela: str) -> dict:
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 8, 0, 8)
        row.setSpacing(7)

        lbl = QLabel(label_tela)
        lbl.setFixedWidth(320)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #1A2B4A; font-size: 12px; background: transparent; border: none;")
        row.addWidget(lbl)

        ESTILO_PLACEHOLDER = """
            QPushButton {
                background: #F8FAFC; color: #94A3B8;
                border: 1.5px dashed #CBD5E1; border-radius: 6px;
                padding: 4px 6px; font-size: 11px;
            }
            QPushButton:hover {
                background: #EFF6FF; color: #2563EB;
                border-color: #2563EB;
            }
        """
        ESTILO_DATE = """
            QDateEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 6px;
                padding: 4px 6px; font-size: 11px;
            }
            QDateEdit:focus { border-color: #2563EB; }
        """

        btn_placeholder = QPushButton("＋ Informar data")
        btn_placeholder.setFixedSize(130, 28)
        btn_placeholder.setCursor(Qt.PointingHandCursor)
        btn_placeholder.setStyleSheet(ESTILO_PLACEHOLDER)
        row.addWidget(btn_placeholder)

        dt_ini = QDateEdit()
        dt_ini.setButtonSymbols(QDateEdit.NoButtons)
        dt_ini.setCalendarPopup(True)
        dt_ini.setFixedWidth(130)
        dt_ini.setMaximumDate(QDate.currentDate())
        dt_ini.setStyleSheet(ESTILO_DATE)
        dt_ini.hide()
        row.addWidget(dt_ini)

        dt_val = QDateEdit()
        dt_val.setReadOnly(True)
        dt_val.setButtonSymbols(QDateEdit.NoButtons)
        dt_val.setFixedWidth(130)
        dt_val.setStyleSheet("""
            QDateEdit {
                background: #F1F5F9; color: #64748B;
                border: 1.5px solid #E2E8F0; border-radius: 6px;
                padding: 4px 6px; font-size: 11px;
            }
        """)
        row.addWidget(dt_val)

        lbl_status = QLabel("—")
        lbl_status.setFixedWidth(150)
        lbl_status.setAlignment(Qt.AlignCenter)
        lbl_status.setStyleSheet(
            "color: #94A3B8; font-size: 11px; background: transparent; border: none;"
        )
        row.addWidget(lbl_status)

        lbl_dias = QLabel("—")
        lbl_dias.setFixedWidth(70)
        lbl_dias.setAlignment(Qt.AlignCenter)
        lbl_dias.setStyleSheet(
            "color: #94A3B8; font-size: 12px; background: transparent; border: none;"
        )
        row.addWidget(lbl_dias)
        row.addWidget(self._btn_upload(nr_nome_banco))
        row.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #F1F5F9; border: none;")

        self._layout_nrs.addWidget(row_widget)
        self._layout_nrs.addWidget(sep)

        resultado = {
            "widget":        row_widget,
            "sep":           sep,
            "data_inicial":  dt_ini,
            "data_validade": dt_val,
            "status":        lbl_status,
            "dias":          lbl_dias,
            "preenchido":    False,
            "atualizar":     None,
        }

        def atualizar_nr():
            if not resultado["preenchido"]:
                return
            qdi  = dt_ini.date()
            ini  = date(qdi.year(), qdi.month(), qdi.day())
            venc = ini + timedelta(days=365)
            dt_val.setDate(QDate(venc.year, venc.month, venc.day))
            dias = (venc - date.today()).days
            lbl_dias.setText(str(abs(dias)) if dias < 0 else str(dias))
            if dias < 0:
                lbl_status.setText("VENCIDO")
                lbl_status.setStyleSheet(
                    "background: #FEE2E2; color: #DC2626; border-radius: 6px; "
                    "padding: 3px 6px; font-size: 11px; font-weight: bold;"
                )
                lbl_dias.setStyleSheet(
                    "color: #DC2626; font-size: 12px; background: transparent; border: none;"
                )
            elif dias <= 30:
                lbl_status.setText("A VENCER")
                lbl_status.setStyleSheet(
                    "background: #FEF3C7; color: #D97706; border-radius: 6px; "
                    "padding: 3px 6px; font-size: 11px; font-weight: bold;"
                )
                lbl_dias.setStyleSheet(
                    "color: #D97706; font-size: 12px; background: transparent; border: none;"
                )
            else:
                lbl_status.setText("VÁLIDO")
                lbl_status.setStyleSheet(
                    "background: #DCFCE7; color: #16A34A; border-radius: 6px; "
                    "padding: 3px 6px; font-size: 11px; font-weight: bold;"
                )
                lbl_dias.setStyleSheet(
                    "color: #16A34A; font-size: 12px; background: transparent; border: none;"
                )

        resultado["atualizar"] = atualizar_nr

        def ativar_date_edit():
            btn_placeholder.hide()
            dt_ini.setDate(QDate.currentDate())
            dt_ini.show()
            dt_ini.setFocus()
            resultado["preenchido"] = True
            atualizar_nr()

        btn_placeholder.clicked.connect(ativar_date_edit)

        def on_date_changed(_):
            resultado["preenchido"] = True
            atualizar_nr()

        dt_ini.dateChanged.connect(on_date_changed)
        return resultado

    def _filtrar_nrs(self, termo: str):
        termo = termo.lower()
        for nr_nome_banco, label_tela, widgets in self._todas_linhas_nrs:
            visivel = termo in nr_nome_banco.lower() or termo in label_tela.lower()
            widgets["widget"].setVisible(visivel)
            widgets["sep"].setVisible(visivel)

    # ─────────────────────────────────────────────
    # SALVAR
    # ─────────────────────────────────────────────
    def _copiar_com_retry(self, origem, destino, tentativas: int = 3, espera_seg: float = 0.35):
        """
        Copia origem -> destino com algumas tentativas em caso de
        PermissionError/WinError 32 (arquivo em uso por outro processo,
        ex: ainda aberto no visualizador padrão de PDF/imagem do Windows).

        Levanta a última exceção se todas as tentativas falharem.
        """
        import shutil
        import time

        ultimo_erro = None
        for tentativa in range(tentativas):
            try:
                shutil.copy2(origem, destino)
                return
            except PermissionError as e:
                ultimo_erro = e
                if tentativa < tentativas - 1:
                    time.sleep(espera_seg)
        raise ultimo_erro

    def _on_salvar(self):
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        from app.models.treinamento import Treinamento
        from app.core.settings import docs_colaborador, docs_treinamentos, _sanitizar
        from pathlib import Path

        nome   = self.campo_nome.text().strip()
        cpf    = self.campo_cpf.text_clean()
        funcao = self.campo_funcao.text().strip()

        if not nome or not cpf:
            QMessageBox.warning(self, "Atenção", "Nome e CPF são obrigatórios.")
            return

        if not self.campo_cpf.is_valid():
            QMessageBox.warning(
                self, "CPF inválido",
                "O CPF informado não é válido.\n"
                "Verifique os 11 dígitos e tente novamente."
            )
            self.campo_cpf.setFocus()
            return

        if not funcao:
            QMessageBox.warning(self, "Atenção", "A função é obrigatória.")
            return

        hoje = date.today()
        qdn  = self.campo_nascimento.date()
        nasc = date(qdn.year(), qdn.month(), qdn.day())
        if nasc > hoje or (hoje - nasc).days // 365 < 18:
            QMessageBox.warning(self, "Data inválida",
                "Verifique a data de nascimento (sem futuro e maior de 18 anos).")
            return

        qda = self.campo_admissao.date()
        adm = date(qda.year(), qda.month(), qda.day())
        if adm > hoje:
            QMessageBox.warning(self, "Data inválida",
                "A data de admissão não pode ser futura.")
            return

        qdi_aso = self.aso_ini.date()
        ini_aso = date(qdi_aso.year(), qdi_aso.month(), qdi_aso.day())
        if ini_aso > hoje:
            QMessageBox.warning(self, "Data inválida",
                "A data inicial do ASO não pode ser futura.")
            return

        session = get_session()
        try:
            # ── Verifica CPF duplicado antes de salvar ────────────────────────
            cpf_existente = session.query(Trabalhador).filter(
                Trabalhador.cpf == cpf
            ).first()
            id_atual = self.trabalhador.id if self.trabalhador else None
            if cpf_existente and cpf_existente.id != id_atual:
                session.close()
                QMessageBox.warning(
                    self, "CPF ja cadastrado",
                    f"O CPF informado ja esta cadastrado para o colaborador:\n"
                    f"{cpf_existente.nome}\n\n"
                    "Verifique o CPF e tente novamente."
                )
                self.campo_cpf.setFocus()
                return

            if self.trabalhador:
                t = session.get(Trabalhador, self.trabalhador.id)
            else:
                t = Trabalhador()
                session.add(t)

            t.nome            = nome
            t.cpf             = cpf
            t.funcao          = funcao
            t.empresa_id      = self.empresa.id if self.empresa else None
            t.data_nascimento = nasc
            t.data_admissao   = adm

            qdv_aso        = self.aso_val.date()
            t.aso_data_inicial = ini_aso
            t.aso_validade     = date(qdv_aso.year(), qdv_aso.month(), qdv_aso.day())

            for attr in ["ordem_servico", "ficha_registro", "ficha_epi", "cnh"]:
                btns  = getattr(self, f"chk_{attr}")
                valor = "sim" if btns["sim"].isChecked() else \
                        "na"  if btns["na"].isChecked()  else "nao"
                setattr(t, attr, valor)

            session.flush()

            # ── Treinamentos ──────────────────────────────────────────────────
            for nr_nome_banco, widgets in self._linhas_nrs.items():
                if not widgets.get("preenchido", False):
                    continue
                qdi = widgets["data_inicial"].date()
                ini = date(qdi.year(), qdi.month(), qdi.day())
                val = ini + timedelta(days=365)
                tr  = session.query(Treinamento).filter_by(
                    trabalhador_id=t.id, nr_nome=nr_nome_banco
                ).first()
                if not tr:
                    tr = Treinamento(trabalhador_id=t.id, nr_nome=nr_nome_banco)
                    session.add(tr)
                tr.data_realizacao = ini
                tr.data_validade   = val

            # ── Arquivos ──────────────────────────────────────────────────────
            # CORREÇÃO (WinError 32): ao editar um colaborador, self._arquivos
            # já vem populado com os caminhos DENTRO da pasta de destino
            # (ver _preencher_dados). Sem essa checagem, o shutil.copy2 abaixo
            # tentava copiar o arquivo para ele mesmo, e travava com
            # "WinError 32: arquivo em uso" se o Windows ainda tivesse um
            # handle aberto (ex: usuário clicou em "Visualizar" antes).
            #
            # Também isolamos o erro por arquivo: se 1 anexo estiver
            # realmente travado por outro processo, o cadastro do
            # colaborador e os outros anexos são salvos normalmente — só
            # avisamos no final quais anexos precisam ser reenviados.
            nome_empresa = self.empresa.razao_social if self.empresa else "Sem Empresa"
            erros_arquivos = []

            for nome_doc, caminho in list(self._arquivos.items()):
                origem = Path(caminho)
                if not origem.exists():
                    continue

                if nome_doc in self._linhas_nrs or nome_doc.startswith("NR-"):
                    pasta_dest = docs_treinamentos(nome_empresa, nome)
                else:
                    pasta_dest = docs_colaborador(nome_empresa, nome)

                nome_arquivo = _sanitizar(nome_doc) + origem.suffix.lower()
                destino = pasta_dest / nome_arquivo

                # Já está no lugar certo -> nada a fazer (evita copiar
                # o arquivo sobre ele mesmo).
                try:
                    if origem.resolve() == destino.resolve():
                        continue
                except OSError:
                    pass

                try:
                    self._copiar_com_retry(origem, destino)
                    self._arquivos[nome_doc] = str(destino)
                except PermissionError as e:
                    motivo = e.strerror or "arquivo em uso por outro processo"
                    erros_arquivos.append(f"{nome_doc} — {motivo}")
                except OSError as e:
                    erros_arquivos.append(f"{nome_doc} — {e}")

            session.commit()
            self.trabalhador = t

            # ── Atualiza contexto do widget de foto após salvar ───────────────
            if self._widget_foto:
                self._widget_foto.atualizar_contexto(nome_empresa, t.nome)

            if erros_arquivos:
                QMessageBox.warning(
                    self, "Colaborador salvo com avisos",
                    "O cadastro foi salvo, mas os arquivos abaixo não puderam "
                    "ser copiados porque estão em uso (feche o programa que "
                    "abriu o arquivo — ex: leitor de PDF/imagem — e anexe de "
                    "novo):\n\n" + "\n".join(erros_arquivos)
                )
            else:
                QMessageBox.information(self, "Sucesso", "Colaborador salvo com sucesso!")

            self.voltar.emit()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")
        finally:
            session.close()

    # ─────────────────────────────────────────────
    # PREENCHER (edição)
    # ─────────────────────────────────────────────
    def _preencher_dados(self):
        t = self.trabalhador
        self.campo_nome.setText(t.nome or "")
        self.campo_cpf.setText(t.cpf or "")
        self.campo_funcao.setText(t.funcao or "")

        if t.data_nascimento:
            self.campo_nascimento.blockSignals(True)
            self.campo_nascimento.setDate(
                QDate(t.data_nascimento.year, t.data_nascimento.month, t.data_nascimento.day)
            )
            self.campo_nascimento.blockSignals(False)

        if t.data_admissao:
            self.campo_admissao.blockSignals(True)
            self.campo_admissao.setDate(
                QDate(t.data_admissao.year, t.data_admissao.month, t.data_admissao.day)
            )
            self.campo_admissao.blockSignals(False)

        if t.aso_data_inicial:
            self.aso_ini.blockSignals(True)
            self.aso_ini.setDate(
                QDate(t.aso_data_inicial.year, t.aso_data_inicial.month, t.aso_data_inicial.day)
            )
            self.aso_ini.blockSignals(False)
            ini  = t.aso_data_inicial
            venc = ini + timedelta(days=self._pgr_dias)
            self.aso_val.setDate(QDate(venc.year, venc.month, venc.day))

        for attr in ["ordem_servico", "ficha_registro", "ficha_epi", "cnh"]:
            valor = getattr(t, attr, "nao")
            btns  = getattr(self, f"chk_{attr}")
            if valor in btns:
                btns[valor].setChecked(True)

        # ── Treinamentos do banco ─────────────────────────────────────────────
        try:
            from app.core.database import get_session as _gs
            from app.models.treinamento import Treinamento as _Tr
            _sess = _gs()
            for tr in _sess.query(_Tr).filter_by(trabalhador_id=t.id).all():
                if tr.nr_nome in self._linhas_nrs and tr.data_realizacao:
                    w = self._linhas_nrs[tr.nr_nome]
                    for child in w["widget"].findChildren(QPushButton):
                        if "Informar data" in child.text():
                            child.hide()
                            break
                    w["data_inicial"].blockSignals(True)
                    w["data_inicial"].setDate(
                        QDate(tr.data_realizacao.year,
                              tr.data_realizacao.month,
                              tr.data_realizacao.day)
                    )
                    w["data_inicial"].blockSignals(False)
                    w["data_inicial"].show()
                    w["preenchido"] = True
                    w["atualizar"]()
            _sess.close()
        except Exception as _e:
            print(f"[WARN] Não carregou treinamentos: {_e}")

        # ── Arquivos salvos no explorador ─────────────────────────────────────
        try:
            from app.core.settings import docs_colaborador, docs_treinamentos
            nome_empresa = self.empresa.razao_social if self.empresa else "Sem Empresa"
            nome_colab   = t.nome

            for pasta in [
                docs_colaborador(nome_empresa, nome_colab),
                docs_treinamentos(nome_empresa, nome_colab),
            ]:
                if pasta.exists():
                    for arquivo in pasta.iterdir():
                        if arquivo.is_file():
                            self._arquivos[arquivo.stem] = str(arquivo)
        except Exception as _e:
            print(f"[WARN] Não carregou arquivos do explorador: {_e}")

        # ── Foto facial — recarrega com nome correto (modo edição) ────────────
        if self._widget_foto and self.empresa:
            self._widget_foto._nome_empresa = self.empresa.razao_social
            self._widget_foto._nome_colab   = t.nome
            self._widget_foto._carregar_foto_existente()

    # ─────────────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────────────
    def _btn_upload(self, nome_doc: str) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setFixedWidth(80)
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(4)

        btn_clip = QPushButton()
        btn_clip.setIcon(qta.icon("fa5s.paperclip", color="#64748B"))
        btn_clip.setIconSize(QSize(13, 13))
        btn_clip.setFixedSize(36, 36)
        btn_clip.setToolTip(f"Anexar — {nome_doc}")
        btn_clip.setCursor(Qt.PointingHandCursor)
        btn_clip.setStyleSheet("""
            QPushButton { background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 8px; }
            QPushButton:hover { background: #E2E8F0; }
        """)

        btn_open = QPushButton()
        btn_open.setIcon(qta.icon("fa5s.eye", color="#2563EB"))
        btn_open.setIconSize(QSize(13, 13))
        btn_open.setFixedSize(36, 36)
        btn_open.setToolTip(f"Visualizar — {nome_doc}")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setVisible(False)
        btn_open.setStyleSheet("""
            QPushButton { background: #EFF6FF; border: 1px solid #2563EB; border-radius: 8px; }
            QPushButton:hover { background: #DBEAFE; }
        """)

        if nome_doc in self._arquivos:
            btn_clip.setIcon(qta.icon("fa5s.paperclip", color="#16A34A"))
            btn_clip.setStyleSheet("""
                QPushButton { background: #DCFCE7; border: 1px solid #16A34A; border-radius: 8px; }
                QPushButton:hover { background: #BBF7D0; }
            """)
            btn_open.setVisible(True)

        btn_clip.clicked.connect(
            lambda _, n=nome_doc, bc=btn_clip, bo=btn_open: self._on_upload(n, bc, bo)
        )
        btn_open.clicked.connect(lambda _, n=nome_doc: self._on_abrir(n))

        hl.addWidget(btn_clip)
        hl.addWidget(btn_open)
        return container

    def _on_upload(self, nome_doc: str, btn_clip: QPushButton, btn_open: QPushButton):
        caminho, _ = QFileDialog.getOpenFileName(
            self, f"Selecionar — {nome_doc}", "",
            "Arquivos (*.pdf *.jpg *.jpeg *.png)"
        )
        if caminho:
            self._arquivos[nome_doc] = caminho
            btn_clip.setIcon(qta.icon("fa5s.paperclip", color="#16A34A"))
            btn_clip.setStyleSheet("""
                QPushButton { background: #DCFCE7; border: 1px solid #16A34A; border-radius: 8px; }
                QPushButton:hover { background: #BBF7D0; }
            """)
            btn_clip.setToolTip(f"Anexado: {caminho.split('/')[-1]}")
            btn_open.setVisible(True)

    def _on_abrir(self, nome_doc: str):
        caminho = self._arquivos.get(nome_doc)
        if not caminho:
            QMessageBox.warning(self, "Atenção", "Nenhum arquivo anexado para este documento.")
            return
        dialogo = VisualizadorArquivo(caminho, nome_doc, parent=self)
        dialogo.exec()

    def _titulo_secao(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "color: #1A2B4A; font-size: 15px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        return lbl

    def _lbl_campo(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setFixedWidth(130)
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl.setStyleSheet(
            "color: #64748B; font-size: 12px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        return lbl

    def _separador(self, layout):
        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFixedHeight(1)
        linha.setStyleSheet("background-color: #F1F5F9; border: none;")
        layout.addWidget(linha)

    def _frame(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        return frame

    @staticmethod
    def _estilo_line_edit() -> str:
        return """
            QLineEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #2563EB; background: #EFF6FF; }
        """

    @staticmethod
    def _estilo_date_edit() -> str:
        return """
            QDateEdit {
                background: white; color: #1A2B4A;
                border: 1.5px solid #CBD5E1; border-radius: 8px;
                padding: 4px 12px; font-size: 13px;
            }
            QDateEdit:focus { border-color: #2563EB; }
        """

    def _btn_acao(self, texto, icone, bg, cor_icone, cor_txt) -> QPushButton:
        btn = QPushButton(texto)
        btn.setIcon(qta.icon(icone, color=cor_icone))
        btn.setIconSize(QSize(13, 13))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: {cor_txt};
                border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 8px 16px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: #E2E8F0; }}
        """)
        return btn