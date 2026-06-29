from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QLineEdit,
    QDialog, QComboBox, QCheckBox, QTextEdit, QTimeEdit,
    QMessageBox, QGridLayout, QSizePolicy, QApplication,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPainterPath, QPixmap
import qtawesome as qta
_HAS_QTA = True
from datetime import date, datetime, timedelta
from typing import Optional
import unicodedata

from app.ui.pages.foto_facial_widget import _get_foto_path

NR01_NOME_BANCO = "NR-01 — Disposições Gerais e Gerenciamento de Riscos (Integração)"

COR_BG              = "#F2F5F8"
COR_CARD_BG         = "#FFFFFF"
COR_CARD_BORDA      = "#DDE3EA"
COR_TITULO          = "#1C2B3A"
COR_SUBTITULO       = "#5A7A96"
COR_SEPARADOR       = "#DDE3EA"
COR_SECAO_LABEL     = "#8AA5BC"
COR_TEXTO_NORMAL    = "#374151"
COR_TEXTO_FRACO     = "#6B7280"

COR_SB_BG           = "#1C2B3A"
COR_SB_BORDA        = "#243447"
COR_SB_TEXTO        = "#A8BED1"
COR_SB_ACENTO       = "#3B7DD8"
COR_SB_SUBTEXTO     = "#6B8FAD"

COR_VERDE_BG        = "#F0FAF4"
COR_VERDE_BORDA     = "#86EFAC"
COR_VERDE_TEXTO     = "#166534"
COR_VERMELHO_BG     = "#FEF2F2"
COR_VERMELHO_BORDA  = "#FCA5A5"
COR_VERMELHO_TEXTO  = "#991B1B"
COR_AMARELO_BG      = "#FFFBEB"
COR_AMARELO_BORDA   = "#FCD34D"
COR_AMARELO_TEXTO   = "#92400E"
COR_AZUL_BG         = "#EFF6FF"
COR_AZUL_BORDA      = "#93C5FD"
COR_AZUL_TEXTO      = "#1E40AF"
COR_ROXO            = "#7C3AED"
COR_CIANO           = "#0891B2"
COR_CIANO_BG        = "#ECFEFF"
COR_CIANO_BORDA     = "#67E8F9"

# Visitantes — paleta própria (roxo), pra diferenciar visualmente de
# colaboradores (sem cor de destaque) e veículos (ciano) nas tabelas e
# cards que listam todo mundo dentro da planta.
COR_VISITANTE        = "#7C3AED"
COR_VISITANTE_BG     = "#F5F3FF"
COR_VISITANTE_BORDA  = "#C4B5FD"

TIPOS_VEICULO  = ["Carro", "Moto", "Caminhão", "Van/Kombi", "Ônibus", "Bicicleta", "Outro"]
STATUS_DENTRO  = "Dentro"
STATUS_SAIU    = "Saiu"


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _sep() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;"); return f

def _sep_sb() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background-color: {COR_SB_BORDA}; border: none;"); return f

def _secao(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL}; background: transparent; border: none; letter-spacing: 1.4px;")
    return lbl

def _secao_sb(texto: str) -> QLabel:
    lbl = QLabel(texto); lbl.setContentsMargins(0, 6, 0, 2)
    lbl.setStyleSheet("font-size: 9px; font-weight: bold; color: #3A5570; background: transparent; border: none; letter-spacing: 1.2px;")
    return lbl

def _card(borda_esq: str = None) -> QFrame:
    borda = f"border-left: 4px solid {borda_esq};" if borda_esq else ""
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; {borda} }}
        QLabel {{ border: none; background: transparent; }}
        QWidget {{ border: none; }}
    """)
    return f

def _tabela_estilo() -> str:
    return f"""
        QTableWidget {{ background-color: {COR_CARD_BG}; border: none; gridline-color: {COR_CARD_BORDA}; font-size: 12px; color: {COR_TEXTO_NORMAL}; }}
        QTableWidget::item {{ padding: 8px 12px; border-bottom: 1px solid {COR_CARD_BORDA}; }}
        QTableWidget::item:selected {{ background-color: {COR_AZUL_BG}; color: {COR_TITULO}; }}
        QHeaderView::section {{ background-color: #F4F7FA; color: {COR_SECAO_LABEL}; border: none; border-bottom: 2px solid {COR_CARD_BORDA}; padding: 8px 12px; font-size: 11px; font-weight: bold; }}
        QScrollBar:vertical {{ background: {COR_BG}; width: 6px; border-radius: 3px; }}
        QScrollBar::handle:vertical {{ background: {COR_CARD_BORDA}; border-radius: 3px; }}
    """

def _tab_estilo(cor_acento: str) -> str:
    return f"""
        QTabWidget::pane {{ border: 1px solid {COR_CARD_BORDA}; background: {COR_CARD_BG}; border-radius: 0 4px 4px 4px; }}
        QTabBar::tab {{ background: #F4F7FA; color: {COR_SECAO_LABEL}; border: 1px solid {COR_CARD_BORDA}; border-bottom: none; padding: 8px 20px; font-size: 12px; font-weight: bold; margin-right: 2px; border-radius: 4px 4px 0 0; }}
        QTabBar::tab:selected {{ background: {COR_CARD_BG}; color: {cor_acento}; border-top: 2px solid {cor_acento}; }}
        QTabBar::tab:hover:!selected {{ background: #EBF0F6; color: {COR_TITULO}; }}
    """

def _campo_input(placeholder: str = "", altura: int = 38) -> QLineEdit:
    le = QLineEdit(); le.setPlaceholderText(placeholder); le.setFixedHeight(altura)
    le.setStyleSheet(f"""
        QLineEdit {{ background: white; color: {COR_TITULO}; border: 1.5px solid #CBD5E1; border-radius: 6px; padding: 4px 12px; font-size: 13px; }}
        QLineEdit:focus {{ border-color: {COR_SB_ACENTO}; background: #EFF6FF; }}
    """)
    return le

def _campo_combo(opcoes: list, altura: int = 38) -> QComboBox:
    cb = QComboBox()
    for o in opcoes: cb.addItem(o)
    cb.setFixedHeight(altura)
    cb.setStyleSheet(f"""
        QComboBox {{ background: white; color: {COR_TITULO}; border: 1.5px solid #CBD5E1; border-radius: 6px; padding: 4px 12px; font-size: 13px; }}
        QComboBox:focus {{ border-color: {COR_SB_ACENTO}; }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; selection-background-color: {COR_AZUL_BG}; }}
    """)
    return cb

def _label_campo(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 0.8px; background: transparent; border: none;")
    return lbl

def _btn_primario(texto: str, icone: str, bg: str, hover: str, altura: int = 40) -> QPushButton:
    btn = QPushButton(texto); btn.setIcon(qta.icon(icone, color="white")); btn.setIconSize(QSize(13, 13))
    btn.setFixedHeight(altura); btn.setCursor(Qt.PointingHandCursor)
    # CORREÇÃO: autoDefault=True faz com que, ao apertar Enter em QUALQUER
    # QLineEdit da mesma janela (ex.: a barra de busca da portaria), o Qt
    # também "clique" neste botão (comportamento padrão de botão default
    # de QDialog) — mesmo já existindo um returnPressed tratando o Enter.
    # Isso causava, por exemplo, o botão de tela cheia sendo acionado ao
    # pesquisar, minimizando/maximizando a janela sem o usuário clicar nele.
    btn.setAutoDefault(False); btn.setDefault(False)
    btn.setStyleSheet(f"""
        QPushButton {{ background: {bg}; color: white; border: none; border-radius: 6px; padding: 0 20px; font-size: 13px; font-weight: bold; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ background: {COR_CARD_BORDA}; color: {COR_SECAO_LABEL}; }}
    """)
    return btn

def _btn_secundario(texto: str, icone: str, altura: int = 38) -> QPushButton:
    btn = QPushButton(texto); btn.setIcon(qta.icon(icone, color=COR_SUBTITULO)); btn.setIconSize(QSize(12, 12))
    btn.setFixedHeight(altura); btn.setCursor(Qt.PointingHandCursor)
    btn.setAutoDefault(False); btn.setDefault(False)  # ver comentário em _btn_primario
    btn.setStyleSheet(f"""
        QPushButton {{ background: {COR_CARD_BG}; color: {COR_SUBTITULO}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; padding: 0 18px; font-size: 13px; }}
        QPushButton:hover {{ background: #EBF0F6; }}
    """)
    return btn

def _get_operador() -> str:
    """
    Nome do operador logado, usado para auditoria em todos os registros
    (entradas, saídas, bloqueios, veículos). A sessão salva por
    salvar_sessao() no main.py NÃO tem a chave "username" — ela tem
    usuario_id / email / token / cnpj. Por isso este helper tenta
    "username" (se algum dia existir) e cai para "email" antes de
    "portaria". Todo o resto do arquivo deve chamar este helper em vez
    de acessar sessao["username"] direto — fazer isso causa KeyError e
    o registro falha silenciosamente (é a causa do erro reportado).
    """
    try:
        from app.core.session_manager import carregar_sessao
        s = carregar_sessao()
        if not s:
            return "portaria"
        return s.get("username") or s.get("email") or "portaria"
    except Exception:
        return "portaria"

def _get_session():
    try:
        from app.core.database import get_session
        return get_session()
    except Exception: return None

def _normalizar_nome(nome: str) -> str:
    """
    Normaliza um nome para comparação tolerante a acentos, caixa e espaços
    extras. Usado para vincular o motorista de um veículo a um colaborador
    cadastrado apenas pelo nome (sem chave estrangeira entre as tabelas),
    e também para filtrar as tabelas de histórico por nome.
    """
    if not nome:
        return ""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acento.strip().lower().split())

def _registrar_saida_veiculo_por_motorista(nome_colaborador: str) -> bool:
    """
    Quando a saída de um COLABORADOR é registrada, procura um veículo que
    ainda esteja "Dentro" cujo campo motorista bata (por nome normalizado)
    com o colaborador, e registra a saída do veículo também — evitando
    veículo "Dentro" com motorista já fora da planta.
    """
    v = VeiculoRepo.buscar_dentro_por_motorista(nome_colaborador)
    if not v:
        return False
    return VeiculoRepo.registrar_saida(v.id)

def _registrar_saida_colaborador_por_nome(nome_motorista: str) -> bool:
    """
    Quando a saída de um VEÍCULO é registrada, procura um colaborador
    cadastrado com esse mesmo nome (normalizado) que tenha entrada hoje e
    ainda não tenha saída registrada, e registra a saída dele também —
    evitando colaborador "dentro da planta" com o veículo já fora.
    """
    s = _get_session()
    if not s:
        return False
    try:
        from app.models.acesso import Acesso
        from app.models.trabalhador import Trabalhador
        nome_norm = _normalizar_nome(nome_motorista)
        if not nome_norm:
            return False
        hoje_inicio = datetime.combine(date.today(), datetime.min.time())
        trab = None
        for t in s.query(Trabalhador).filter(Trabalhador.ativo == True).all():
            if _normalizar_nome(t.nome) == nome_norm:
                trab = t; break
        if not trab:
            return False
        tem_entrada = (s.query(Acesso)
                       .filter(Acesso.trabalhador_id == trab.id, Acesso.tipo == "entrada",
                               Acesso.horario >= hoje_inicio).first())
        if not tem_entrada:
            return False
        tem_saida = (s.query(Acesso)
                     .filter(Acesso.trabalhador_id == trab.id, Acesso.tipo == "saida",
                             Acesso.horario >= hoje_inicio).first())
        if tem_saida:
            return False
        op = _get_operador()
        s.add(Acesso(trabalhador_id=trab.id, tipo="saida", horario=datetime.now(), operador=op))
        s.commit()
        return True
    except Exception as e:
        print(f"[_registrar_saida_colaborador_por_nome] {e}"); s.rollback(); return False
    finally:
        s.close()

def _aplicar_foto_avatar(lbl_avatar: QLabel, nome_empresa: str, nome_colab: str):
    size = lbl_avatar.width()
    foto_path = _get_foto_path(nome_empresa, nome_colab)
    if foto_path:
        pixmap = QPixmap(str(foto_path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            result = QPixmap(size, size); result.fill(Qt.transparent)
            painter = QPainter(result); painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath(); path.addEllipse(0, 0, size, size); painter.setClipPath(path)
            x_off = (scaled.width()-size)//2; y_off = (scaled.height()-size)//2
            painter.drawPixmap(-x_off, -y_off, scaled); painter.end()
            lbl_avatar.setPixmap(result)
            lbl_avatar.setStyleSheet(f"border: 2px solid {COR_VERDE_BORDA}; border-radius: 28px; background: transparent;")
            return
    lbl_avatar.setPixmap(qta.icon("fa5s.user-circle", color=COR_SB_SUBTEXTO).pixmap(40, 40))
    lbl_avatar.setStyleSheet(f"background-color: {COR_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 28px;")


def _barra_busca_nome(placeholder: str = "Filtrar por nome do colaborador…") -> tuple:
    """
    Cria uma barra de busca padrão (ícone + QLineEdit) para filtrar tabelas
    de histórico por nome. Retorna (frame, campo_busca).
    """
    frame = QFrame(); frame.setFixedHeight(40)
    frame.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; }} QLineEdit {{ border: none; background: transparent; }} QLabel {{ border: none; background: transparent; }}")
    bl = QHBoxLayout(frame); bl.setContentsMargins(12, 0, 12, 0); bl.setSpacing(8)
    ic = QLabel(); ic.setPixmap(qta.icon("fa5s.search", color=COR_SECAO_LABEL).pixmap(13, 13)); ic.setStyleSheet("background: transparent; border: none;")
    campo = QLineEdit(); campo.setPlaceholderText(placeholder)
    campo.setStyleSheet(f"color: {COR_TITULO}; font-size: 12px;")
    bl.addWidget(ic); bl.addWidget(campo, 1)
    return frame, campo


def _filtrar_tabelas_por_texto(tabelas: list, texto: str, coluna: int = 0):
    """
    Esconde/exibe linhas das tabelas informadas conforme o texto digitado
    bata (de forma normalizada/tolerante a acento) com o conteúdo da
    coluna indicada (por padrão, a primeira coluna — nome do colaborador
    ou placa, dependendo da tabela).
    """
    termo = _normalizar_nome(texto)
    for tbl in tabelas:
        for row in range(tbl.rowCount()):
            if tbl.columnSpan(row, 0) > 1:
                continue  # linha de "nenhum registro encontrado"
            item = tbl.item(row, coluna)
            visivel = True
            if termo:
                visivel = bool(item) and termo in _normalizar_nome(item.text())
            tbl.setRowHidden(row, not visivel)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO DE VEÍCULOS
# ══════════════════════════════════════════════════════════════════════════════

class VeiculoDTO:
    def __init__(self, id=None, placa="", modelo="", tipo="Carro", cor="",
                 motorista="", empresa="", observacao="", status=STATUS_DENTRO,
                 entrada=None, saida=None, operador="portaria"):
        self.id = id; self.placa = placa.upper().strip(); self.modelo = modelo.strip()
        self.tipo = tipo; self.cor = cor.strip(); self.motorista = motorista.strip()
        self.empresa = empresa.strip(); self.observacao = observacao.strip()
        self.status = status; self.entrada = entrada or datetime.now()
        self.saida = saida; self.operador = operador


class VeiculoRepo:
    @staticmethod
    def listar(inicio: datetime) -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.veiculo import Veiculo
            rows = s.query(Veiculo).filter(Veiculo.entrada >= inicio).order_by(Veiculo.entrada.desc()).all()
            return [VeiculoDTO(id=v.id, placa=v.placa, modelo=v.modelo, tipo=v.tipo, cor=v.cor,
                               motorista=v.motorista, empresa=v.empresa, observacao=v.observacao,
                               status=v.status, entrada=v.entrada, saida=v.saida, operador=v.operador) for v in rows]
        except Exception as e: print(f"[VeiculoRepo.listar] {e}"); return []
        finally: s.close()

    @staticmethod
    def dentro() -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.veiculo import Veiculo
            rows = s.query(Veiculo).filter(Veiculo.status == STATUS_DENTRO).order_by(Veiculo.entrada.desc()).all()
            return [VeiculoDTO(id=v.id, placa=v.placa, modelo=v.modelo, tipo=v.tipo, cor=v.cor,
                               motorista=v.motorista, empresa=v.empresa, observacao=v.observacao,
                               status=v.status, entrada=v.entrada, saida=v.saida, operador=v.operador) for v in rows]
        except Exception as e: print(f"[VeiculoRepo.dentro] {e}"); return []
        finally: s.close()

    @staticmethod
    def contar_dentro() -> int:
        s = _get_session()
        if not s: return 0
        try:
            from app.models.veiculo import Veiculo
            return s.query(Veiculo).filter(Veiculo.status == STATUS_DENTRO).count()
        except Exception: return 0
        finally: s.close()

    @staticmethod
    def buscar_dentro_por_motorista(nome: str) -> Optional["VeiculoDTO"]:
        """
        Procura, entre os veículos atualmente "Dentro", um cujo campo
        motorista bata (nome normalizado) com o nome informado. Usado para
        vincular a saída automática do veículo quando o colaborador
        correspondente registra a própria saída.
        """
        s = _get_session()
        if not s: return None
        try:
            from app.models.veiculo import Veiculo
            nome_norm = _normalizar_nome(nome)
            if not nome_norm: return None
            rows = s.query(Veiculo).filter(Veiculo.status == STATUS_DENTRO).all()
            for v in rows:
                if _normalizar_nome(v.motorista) == nome_norm:
                    return VeiculoDTO(id=v.id, placa=v.placa, modelo=v.modelo, tipo=v.tipo, cor=v.cor,
                                       motorista=v.motorista, empresa=v.empresa, observacao=v.observacao,
                                       status=v.status, entrada=v.entrada, saida=v.saida, operador=v.operador)
            return None
        except Exception as e: print(f"[VeiculoRepo.buscar_dentro_por_motorista] {e}"); return None
        finally: s.close()

    @staticmethod
    def registrar_entrada(dto: "VeiculoDTO"):
        s = _get_session()
        if not s: return None
        try:
            from app.models.veiculo import Veiculo
            v = Veiculo(placa=dto.placa, modelo=dto.modelo, tipo=dto.tipo, cor=dto.cor,
                        motorista=dto.motorista, empresa=dto.empresa, observacao=dto.observacao,
                        status=STATUS_DENTRO, entrada=dto.entrada, saida=None, operador=dto.operador)
            s.add(v); s.commit(); return v.id
        except Exception as e: print(f"[VeiculoRepo.entrada] {e}"); s.rollback(); return None
        finally: s.close()

    @staticmethod
    def registrar_saida(vid: int) -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.veiculo import Veiculo
            v = s.get(Veiculo, vid)
            if not v: return False
            v.status = STATUS_SAIU; v.saida = datetime.now(); s.commit(); return True
        except Exception as e: print(f"[VeiculoRepo.saida] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def atualizar(dto: "VeiculoDTO") -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.veiculo import Veiculo
            v = s.get(Veiculo, dto.id)
            if not v: return False
            v.placa = dto.placa; v.modelo = dto.modelo; v.tipo = dto.tipo
            v.cor = dto.cor; v.motorista = dto.motorista; v.empresa = dto.empresa; v.observacao = dto.observacao
            s.commit(); return True
        except Exception as e: print(f"[VeiculoRepo.atualizar] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def excluir(vid: int) -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.veiculo import Veiculo
            v = s.get(Veiculo, vid)
            if not v: return False
            s.delete(v); s.commit(); return True
        except Exception as e: print(f"[VeiculoRepo.excluir] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def buscar(termo: str) -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.veiculo import Veiculo
            rows = (s.query(Veiculo)
                    .filter(Veiculo.placa.ilike(f"%{termo}%") | Veiculo.motorista.ilike(f"%{termo}%") |
                            Veiculo.empresa.ilike(f"%{termo}%") | Veiculo.modelo.ilike(f"%{termo}%"))
                    .order_by(Veiculo.entrada.desc()).limit(50).all())
            return [VeiculoDTO(id=v.id, placa=v.placa, modelo=v.modelo, tipo=v.tipo, cor=v.cor,
                               motorista=v.motorista, empresa=v.empresa, observacao=v.observacao,
                               status=v.status, entrada=v.entrada, saida=v.saida, operador=v.operador) for v in rows]
        except Exception as e: print(f"[VeiculoRepo.buscar] {e}"); return []
        finally: s.close()


class ModalVeiculo(QDialog):
    salvo = Signal(object)

    def __init__(self, dto: VeiculoDTO = None, parent=None):
        super().__init__(parent)
        self._dto = dto; self._is_new = dto is None
        titulo = "Registrar Entrada de Veículo" if self._is_new else "Editar Veículo"
        self.setWindowTitle(titulo); self.setFixedSize(520, 540); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._build_ui(titulo)
        if dto: self._preencher(dto)

    def _build_ui(self, titulo):
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(16)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.car" if self._is_new else "fa5s.edit", color=COR_CIANO).pixmap(20, 20))
        lbl_t = QLabel(titulo); lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        topo.addWidget(ic); topo.addWidget(lbl_t); topo.addStretch()
        lay.addLayout(topo); lay.addWidget(_sep())
        grid = QGridLayout(); grid.setSpacing(12); grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(_label_campo("PLACA *"), 0, 0)
        self._placa = _campo_input("Ex: ABC-1234"); self._placa.setMaxLength(10)
        grid.addWidget(self._placa, 1, 0)
        grid.addWidget(_label_campo("TIPO *"), 0, 1)
        self._tipo = _campo_combo(TIPOS_VEICULO); grid.addWidget(self._tipo, 1, 1)
        grid.addWidget(_label_campo("MODELO"), 2, 0)
        self._modelo = _campo_input("Ex: Gol, Sprinter…"); grid.addWidget(self._modelo, 3, 0)
        grid.addWidget(_label_campo("COR"), 2, 1)
        self._cor = _campo_input("Ex: Branco, Prata…"); grid.addWidget(self._cor, 3, 1)
        grid.addWidget(_label_campo("MOTORISTA / CONDUTOR"), 4, 0, 1, 2)
        self._motorista = _campo_input("Nome completo (igual ao cadastro do colaborador, se houver)"); grid.addWidget(self._motorista, 5, 0, 1, 2)
        grid.addWidget(_label_campo("EMPRESA / ORIGEM"), 6, 0, 1, 2)
        self._empresa = _campo_input("Razão social ou departamento"); grid.addWidget(self._empresa, 7, 0, 1, 2)
        grid.addWidget(_label_campo("OBSERVAÇÃO"), 8, 0, 1, 2)
        self._obs = QTextEdit(); self._obs.setFixedHeight(60); self._obs.setPlaceholderText("Carga, finalidade da visita…")
        self._obs.setStyleSheet(f"QTextEdit {{ background: white; color: {COR_TITULO}; border: 1.5px solid #CBD5E1; border-radius: 6px; padding: 6px 12px; font-size: 13px; }} QTextEdit:focus {{ border-color: {COR_SB_ACENTO}; }}")
        grid.addWidget(self._obs, 9, 0, 1, 2)
        lay.addLayout(grid); lay.addStretch()
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = _btn_secundario("  Cancelar", "fa5s.times"); btn_c.clicked.connect(self.reject)
        lbl_s = "  Registrar Entrada" if self._is_new else "  Salvar Alterações"
        ic_s  = "fa5s.sign-in-alt"    if self._is_new else "fa5s.save"
        self._btn_s = _btn_primario(lbl_s, ic_s, COR_CIANO, "#0E7490")
        self._btn_s.clicked.connect(self._on_salvar)
        btns.addWidget(btn_c); btns.addWidget(self._btn_s); lay.addLayout(btns)

    def _preencher(self, dto):
        self._placa.setText(dto.placa)
        idx = self._tipo.findText(dto.tipo)
        if idx >= 0: self._tipo.setCurrentIndex(idx)
        self._modelo.setText(dto.modelo); self._cor.setText(dto.cor)
        self._motorista.setText(dto.motorista); self._empresa.setText(dto.empresa)
        self._obs.setPlainText(dto.observacao)

    def _on_salvar(self):
        placa = self._placa.text().strip().upper()
        if not placa:
            QMessageBox.warning(self, "Campo obrigatório", "Informe a placa do veículo."); self._placa.setFocus(); return
        dto = VeiculoDTO(id=self._dto.id if self._dto else None, placa=placa,
                         tipo=self._tipo.currentText(), modelo=self._modelo.text().strip(),
                         cor=self._cor.text().strip(), motorista=self._motorista.text().strip(),
                         empresa=self._empresa.text().strip(), observacao=self._obs.toPlainText().strip(),
                         operador=_get_operador())
        if self._is_new:
            vid = VeiculoRepo.registrar_entrada(dto)
            if vid is None: QMessageBox.critical(self, "Erro", "Não foi possível registrar no banco."); return
            dto.id = vid
        else:
            if not VeiculoRepo.atualizar(dto): QMessageBox.critical(self, "Erro", "Não foi possível atualizar."); return
        self.salvo.emit(dto); self.accept()


class ModalSaidaVeiculo(QDialog):
    confirmado = Signal(int)

    def __init__(self, dto: VeiculoDTO, parent=None):
        super().__init__(parent)
        self._dto = dto; self.setWindowTitle("Registrar Saída de Veículo")
        self.setFixedSize(420, 280); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(16)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.sign-out-alt", color=COR_AMARELO_TEXTO).pixmap(22, 22))
        vl = QVBoxLayout(); vl.setSpacing(2)
        vl.addWidget(QLabel("Registrar Saída de Veículo").__class__(parent=None) if False else self._lbl("Registrar Saída de Veículo", f"font-size: 15px; font-weight: bold; color: {COR_TITULO};"))
        vl.addWidget(self._lbl("Confirme os dados antes de registrar a saída:", f"font-size: 11px; color: {COR_SUBTITULO};"))
        topo.addWidget(ic); topo.addLayout(vl); topo.addStretch(); lay.addLayout(topo); lay.addWidget(_sep())
        frame_info = _card(); fl = QVBoxLayout(frame_info); fl.setContentsMargins(16, 12, 16, 12); fl.setSpacing(6)
        for label, valor in [("Placa:", self._dto.placa), ("Modelo:", self._dto.modelo or "—"),
                              ("Motorista:", self._dto.motorista or "—"),
                              ("Entrada:", self._dto.entrada.strftime("%d/%m/%Y %H:%M") if self._dto.entrada else "—")]:
            row = QHBoxLayout()
            ll = QLabel(label); ll.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold;")
            lv = QLabel(valor); lv.setStyleSheet(f"font-size: 12px; color: {COR_TITULO}; font-weight: bold;")
            row.addWidget(ll); row.addStretch(); row.addWidget(lv); fl.addLayout(row)
        lay.addWidget(frame_info)
        self._lbl_aviso = self._lbl("", f"font-size: 11px; color: {COR_SB_ACENTO}; font-style: italic;")
        self._lbl_aviso.setWordWrap(True); self._lbl_aviso.setVisible(False)
        lay.addWidget(self._lbl_aviso)
        lay.addStretch()
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = _btn_secundario("  Cancelar", "fa5s.times"); btn_c.clicked.connect(self.reject)
        btn_ok = _btn_primario("  Confirmar Saída", "fa5s.sign-out-alt", COR_AMARELO_TEXTO, "#78350F")
        btn_ok.clicked.connect(self._on_confirmar)
        btns.addWidget(btn_c); btns.addWidget(btn_ok); lay.addLayout(btns)

    def _lbl(self, texto, estilo):
        l = QLabel(texto); l.setStyleSheet(estilo); return l

    def _on_confirmar(self):
        if not VeiculoRepo.registrar_saida(self._dto.id):
            QMessageBox.critical(self, "Erro", "Não foi possível registrar a saída."); return
        # Vínculo automático: se o motorista deste veículo corresponder a um
        # colaborador cadastrado que ainda esteja "dentro" hoje, registra a
        # saída dele também (saída combinada veículo + colaborador).
        if self._dto.motorista and _registrar_saida_colaborador_por_nome(self._dto.motorista):
            self._lbl_aviso.setText(f"Saída do colaborador “{self._dto.motorista}” também foi registrada automaticamente.")
            self._lbl_aviso.setVisible(True)
        self.confirmado.emit(self._dto.id); self.accept()


class JanelaVeiculos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabelas_filtraveis = []
        self.setWindowTitle("Histórico de Veículos"); self.setWindowFlag(Qt.Window)
        self.setMinimumSize(860, 540); self.resize(1000, 640)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QDialog {{ background-color: {COR_BG}; }}")
        self._build_ui(); self._carregar_todos()

    def _build_ui(self):
        raiz = QVBoxLayout(self); raiz.setContentsMargins(28, 24, 28, 24); raiz.setSpacing(16)
        hdr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.car", color=COR_CIANO).pixmap(22, 22)); ic.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel("Histórico de Veículos"); lt.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_TITULO};")
        ls = QLabel("Registros de entrada e saída de veículos na unidade"); ls.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(lt); vl.addWidget(ls)
        hdr.addWidget(ic); hdr.addLayout(vl); hdr.addStretch()
        btn_f = _btn_primario("  Fechar", "fa5s.times", COR_SUBTITULO, COR_TITULO, 34); btn_f.clicked.connect(self.close)
        hdr.addWidget(btn_f); raiz.addLayout(hdr); raiz.addWidget(_sep())
        res = QHBoxLayout(); res.setSpacing(12)
        self._lbl_hoje   = self._rc(res, "fa5s.sun",           COR_CIANO,        "Hoje")
        self._lbl_semana = self._rc(res, "fa5s.calendar-week", COR_SB_ACENTO,    "Esta semana")
        self._lbl_mes    = self._rc(res, "fa5s.calendar-alt",  COR_AMARELO_TEXTO,"Este mês")
        self._lbl_dentro = self._rc(res, "fa5s.parking",       COR_VERDE_TEXTO,  "Agora na unidade")
        raiz.addLayout(res)
        barra_busca, self._campo_busca_nome = _barra_busca_nome("Filtrar por nome do motorista/colaborador…")
        self._campo_busca_nome.textChanged.connect(self._filtrar_por_nome)
        raiz.addWidget(barra_busca)
        self._tabs = QTabWidget(); self._tabs.setStyleSheet(_tab_estilo(COR_CIANO)); raiz.addWidget(self._tabs, 1)
        cols = ["Placa", "Tipo", "Modelo/Cor", "Motorista", "Empresa", "Entrada", "Saída", "Status"]
        self._tbl_hoje   = self._add_tab("  Hoje  ",        cols)
        self._tbl_semana = self._add_tab("  Esta Semana  ", cols)
        self._tbl_mes    = self._add_tab("  Este Mês  ",    cols)

    def _filtrar_por_nome(self, texto: str):
        # Coluna 3 = "Motorista" nesta tabela
        _filtrar_tabelas_por_texto(self._tabelas_filtraveis, texto, coluna=3)

    def _rc(self, lay, icone, cor, titulo):
        f = QFrame(); f.setStyleSheet(f"QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-top: 3px solid {cor}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        fl = QVBoxLayout(f); fl.setContentsMargins(16, 12, 16, 12); fl.setSpacing(4)
        topo = QHBoxLayout(); ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(14, 14)); ic.setStyleSheet("border: none; background: transparent;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch()
        lv = QLabel("—"); lv.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {cor};")
        fl.addLayout(topo); fl.addWidget(lv); lay.addWidget(f, 1); return lv

    def _add_tab(self, label, cols):
        w = QWidget(); w.setStyleSheet(f"background: {COR_CARD_BG}; border: none;")
        lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0)
        tbl = QTableWidget(); tbl.setColumnCount(len(cols)); tbl.setHorizontalHeaderLabels(cols)
        tbl.setStyleSheet(_tabela_estilo()); tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False); tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers); tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False); tbl.setFocusPolicy(Qt.NoFocus)
        lay.addWidget(tbl); self._tabs.addTab(w, label); self._tabelas_filtraveis.append(tbl); return tbl

    def _fill(self, tbl, veiculos):
        tbl.setRowCount(len(veiculos))
        for row, v in enumerate(veiculos):
            mc = f"{v.modelo}" + (f" / {v.cor}" if v.cor else "")
            e_str = v.entrada.strftime("%d/%m/%Y %H:%M") if v.entrada else "—"
            s_str = v.saida.strftime("%d/%m/%Y %H:%M")   if v.saida   else "—"
            for col, (txt, ctr, bld) in enumerate([
                (v.placa, False, True), (v.tipo, False, False), (mc, False, False),
                (v.motorista or "—", False, False), (v.empresa or "—", False, False),
                (e_str, True, False), (s_str, True, False)]):
                it = QTableWidgetItem(str(txt)); it.setTextAlignment((Qt.AlignCenter if ctr else Qt.AlignLeft)|Qt.AlignVCenter)
                if bld: f = it.font(); f.setBold(True); it.setFont(f)
                tbl.setItem(row, col, it)
            it_st = QTableWidgetItem(v.status); it_st.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_st.setForeground(QColor(COR_CIANO)); it_st.setBackground(QColor(COR_CIANO_BG))
            else: it_st.setForeground(QColor(COR_SECAO_LABEL))
            tbl.setItem(row, 7, it_st)
        if not veiculos:
            tbl.setRowCount(1); it = QTableWidgetItem("Nenhum veículo registrado neste período")
            it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter); it.setForeground(QColor(COR_SECAO_LABEL))
            tbl.setItem(0, 0, it); tbl.setSpan(0, 0, 1, 8)

    def _carregar_todos(self):
        hoje = date.today()
        i_h  = datetime.combine(hoje, datetime.min.time())
        i_s  = datetime.combine(hoje - timedelta(days=hoje.weekday()), datetime.min.time())
        i_m  = datetime.combine(hoje.replace(day=1), datetime.min.time())
        v_h  = VeiculoRepo.listar(i_h); v_s = VeiculoRepo.listar(i_s); v_m = VeiculoRepo.listar(i_m)
        v_d  = VeiculoRepo.dentro()
        self._fill(self._tbl_hoje, v_h); self._fill(self._tbl_semana, v_s); self._fill(self._tbl_mes, v_m)
        self._lbl_hoje.setText(str(len(v_h))); self._lbl_semana.setText(str(len(v_s)))
        self._lbl_mes.setText(str(len(v_m))); self._lbl_dentro.setText(str(len(v_d)))
        if self._campo_busca_nome.text():
            self._filtrar_por_nome(self._campo_busca_nome.text())


class PainelVeiculos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ThirdSys — Controle de Veículos"); self.setWindowFlag(Qt.Window)
        self.setMinimumSize(1080, 640)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1280, screen.width()-80), min(760, screen.height()-80))
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QDialog {{ background-color: {COR_BG}; }}")
        self._lista: list = []
        self._build_ui(); self._carregar()

    def _build_ui(self):
        raiz = QVBoxLayout(self); raiz.setContentsMargins(28, 24, 28, 24); raiz.setSpacing(16)
        # Header
        hdr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.car", color=COR_CIANO).pixmap(26, 26)); ic.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel("Controle de Veículos"); lt.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COR_TITULO};")
        ls = QLabel("Entrada e saída de veículos — portaria"); ls.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO};")
        vl.addWidget(lt); vl.addWidget(ls); hdr.addWidget(ic); hdr.addLayout(vl); hdr.addStretch()
        btn_hist = _btn_secundario("  Histórico", "fa5s.history"); btn_hist.clicked.connect(lambda: JanelaVeiculos(self).exec())
        btn_f = _btn_primario("  Fechar", "fa5s.times", COR_SUBTITULO, COR_TITULO, 36); btn_f.clicked.connect(self.close)
        hdr.addWidget(btn_hist); hdr.addWidget(btn_f); raiz.addLayout(hdr)
        # Cards resumo
        res = QHBoxLayout(); res.setSpacing(12)
        self._rc_dentro = self._rc(res, "fa5s.parking",  COR_CIANO,        "Veículos na unidade")
        self._rc_hoje   = self._rc(res, "fa5s.sun",       COR_SB_ACENTO,   "Entradas hoje")
        self._rc_cars   = self._rc(res, "fa5s.car",       COR_VERDE_TEXTO, "Carros dentro")
        self._rc_cam    = self._rc(res, "fa5s.truck",     COR_AMARELO_TEXTO,"Caminhões/Vans")
        raiz.addLayout(res)
        # Barra de ações
        barra = QFrame(); barra.setFixedHeight(52)
        barra.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; }} QLineEdit {{ border: none; background: transparent; }} QLabel {{ border: none; background: transparent; }}")
        bl = QHBoxLayout(barra); bl.setContentsMargins(14, 0, 10, 0); bl.setSpacing(10)
        ic_s = QLabel(); ic_s.setPixmap(qta.icon("fa5s.search", color=COR_SB_SUBTEXTO).pixmap(14, 14)); ic_s.setStyleSheet("background: transparent; border: none;")
        self._busca = QLineEdit(); self._busca.setPlaceholderText("Placa, motorista, empresa ou modelo…"); self._busca.setStyleSheet(f"color: {COR_TITULO}; font-size: 13px;")
        self._busca.returnPressed.connect(self._carregar)
        bl.addWidget(ic_s); bl.addWidget(self._busca, 1)
        self._filtro = QComboBox()
        for o in ["Todos", "Dentro", "Saíram"]: self._filtro.addItem(o)
        self._filtro.setFixedHeight(34)
        self._filtro.setStyleSheet(f"QComboBox {{ background: {COR_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; padding: 0 8px; font-size: 12px; min-width: 90px; }} QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; selection-background-color: {COR_AZUL_BG}; }}")
        self._filtro.currentIndexChanged.connect(self._carregar); bl.addWidget(self._filtro)
        sv = QFrame(); sv.setFrameShape(QFrame.VLine); sv.setFixedWidth(1); sv.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;"); bl.addWidget(sv)
        self._btn_entrada = _btn_primario("  Nova Entrada", "fa5s.sign-in-alt", COR_CIANO, "#0E7490", 36)
        self._btn_entrada.clicked.connect(self._on_nova_entrada)
        self._btn_saida = _btn_primario("  Registrar Saída", "fa5s.sign-out-alt", COR_AMARELO_TEXTO, "#78350F", 36)
        self._btn_saida.setEnabled(False); self._btn_saida.clicked.connect(self._on_saida)
        self._btn_editar = _btn_secundario("  Editar", "fa5s.edit", 36)
        self._btn_editar.setEnabled(False); self._btn_editar.clicked.connect(self._on_editar)
        self._btn_excluir = _btn_primario("  Excluir", "fa5s.trash", COR_VERMELHO_TEXTO, "#7F1D1D", 36)
        self._btn_excluir.setEnabled(False); self._btn_excluir.clicked.connect(self._on_excluir)
        btn_lp = QPushButton(); btn_lp.setIcon(qta.icon("fa5s.times", color=COR_SB_SUBTEXTO)); btn_lp.setIconSize(QSize(12, 12))
        btn_lp.setFixedSize(36, 36); btn_lp.setCursor(Qt.PointingHandCursor); btn_lp.setToolTip("Limpar busca")
        btn_lp.setAutoDefault(False); btn_lp.setDefault(False)
        btn_lp.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_lp.clicked.connect(lambda: (self._busca.clear(), self._filtro.setCurrentIndex(0), self._carregar()))
        for w in [self._btn_entrada, self._btn_saida, self._btn_editar, self._btn_excluir, btn_lp]: bl.addWidget(w)
        raiz.addWidget(barra)
        # Tabela
        tbl_frame = _card(); tl = QVBoxLayout(tbl_frame); tl.setContentsMargins(0, 0, 0, 0); tl.setSpacing(0)
        cols = ["Placa", "Tipo", "Modelo / Cor", "Motorista", "Empresa", "Entrada", "Saída", "Tempo", "Status", "Operador"]
        self._tbl = QTableWidget(); self._tbl.setColumnCount(len(cols)); self._tbl.setHorizontalHeaderLabels(cols)
        self._tbl.setStyleSheet(_tabela_estilo())
        hh = self._tbl.horizontalHeader(); hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents); hh.setSectionResizeMode(1, QHeaderView.ResizeToContents); hh.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self._tbl.verticalHeader().setVisible(False); self._tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tbl.setEditTriggers(QAbstractItemView.NoEditTriggers); self._tbl.setAlternatingRowColors(True)
        self._tbl.setShowGrid(False); self._tbl.setFocusPolicy(Qt.NoFocus)
        self._tbl.selectionModel().selectionChanged.connect(self._on_sel); self._tbl.doubleClicked.connect(self._on_editar)
        tl.addWidget(self._tbl); raiz.addWidget(tbl_frame, 1)
        # Rodapé
        rod = QHBoxLayout()
        self._lbl_total = QLabel("0 registros"); self._lbl_total.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL};")
        self._lbl_upd = QLabel(""); self._lbl_upd.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL};")
        btn_r = QPushButton(); btn_r.setIcon(qta.icon("fa5s.sync-alt", color=COR_SB_SUBTEXTO)); btn_r.setIconSize(QSize(12, 12))
        btn_r.setFixedSize(30, 30); btn_r.setCursor(Qt.PointingHandCursor); btn_r.setToolTip("Atualizar")
        btn_r.setAutoDefault(False); btn_r.setDefault(False)
        btn_r.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QPushButton:hover {{ background: {COR_CARD_BG}; }}")
        btn_r.clicked.connect(self._carregar)
        rod.addWidget(self._lbl_total); rod.addStretch(); rod.addWidget(self._lbl_upd); rod.addWidget(btn_r)
        raiz.addLayout(rod)

    def _rc(self, lay, icone, cor, titulo):
        f = QFrame(); f.setStyleSheet(f"QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-top: 3px solid {cor}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        fl = QVBoxLayout(f); fl.setContentsMargins(14, 10, 14, 10); fl.setSpacing(2)
        topo = QHBoxLayout(); ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(13, 13)); ic.setStyleSheet("background: transparent; border: none;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 10px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch()
        lv = QLabel("—"); lv.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {cor};")
        fl.addLayout(topo); fl.addWidget(lv); lay.addWidget(f, 1); return lv

    def _carregar(self):
        filtro = self._filtro.currentText(); termo = self._busca.text().strip()
        if termo: todos = VeiculoRepo.buscar(termo)
        else:
            inicio = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
            todos  = VeiculoRepo.listar(inicio)
        if filtro == "Dentro":  todos = [v for v in todos if v.status == STATUS_DENTRO]
        elif filtro == "Saíram": todos = [v for v in todos if v.status == STATUS_SAIU]
        self._lista = todos; self._fill(); self._upd_cards()
        self._lbl_upd.setText(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

    def _fill(self):
        agora = datetime.now(); self._tbl.setRowCount(len(self._lista))
        for row, v in enumerate(self._lista):
            mc = v.modelo + (f" / {v.cor}" if v.cor else "")
            e_s = v.entrada.strftime("%d/%m %H:%M") if v.entrada else "—"
            sa_s = v.saida.strftime("%d/%m %H:%M")  if v.saida   else "—"
            if v.status == STATUS_DENTRO and v.entrada:
                d = agora - v.entrada; h, m = divmod(int(d.total_seconds())//60, 60); t_s = f"{h}h {m:02d}min"
            elif v.saida and v.entrada:
                d = v.saida - v.entrada; h, m = divmod(int(d.total_seconds())//60, 60); t_s = f"{h}h {m:02d}min"
            else: t_s = "—"
            dados = [(v.placa, False, True), (v.tipo, False, False), (mc or "—", False, False),
                     (v.motorista or "—", False, False), (v.empresa or "—", False, False),
                     (e_s, True, False), (sa_s, True, False), (t_s, True, False)]
            for col, (txt, ctr, bld) in enumerate(dados):
                it = QTableWidgetItem(str(txt)); it.setTextAlignment((Qt.AlignCenter if ctr else Qt.AlignLeft)|Qt.AlignVCenter)
                if bld: f = it.font(); f.setBold(True); it.setFont(f)
                if v.status == STATUS_DENTRO: it.setBackground(QColor("#F0FEFF"))
                self._tbl.setItem(row, col, it)
            it_st = QTableWidgetItem(v.status); it_st.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_st.setForeground(QColor(COR_CIANO)); it_st.setBackground(QColor(COR_CIANO_BG))
            else: it_st.setForeground(QColor(COR_SECAO_LABEL))
            self._tbl.setItem(row, 8, it_st)
            it_op = QTableWidgetItem(v.operador or "—"); it_op.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_op.setBackground(QColor("#F0FEFF"))
            self._tbl.setItem(row, 9, it_op)
        if not self._lista:
            self._tbl.setRowCount(1); it = QTableWidgetItem("Nenhum veículo encontrado")
            it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter); it.setForeground(QColor(COR_SECAO_LABEL))
            self._tbl.setItem(0, 0, it); self._tbl.setSpan(0, 0, 1, 10)
        self._lbl_total.setText(f"{len(self._lista)} registro(s)")

    def _upd_cards(self):
        dentro = [v for v in self._lista if v.status == STATUS_DENTRO]
        ini_h  = datetime.combine(date.today(), datetime.min.time())
        hoje_v = [v for v in self._lista if v.entrada and v.entrada >= ini_h]
        cars   = [v for v in dentro if v.tipo == "Carro"]
        cam    = [v for v in dentro if v.tipo in ("Caminhão", "Van/Kombi", "Ônibus")]
        self._rc_dentro.setText(str(len(dentro))); self._rc_hoje.setText(str(len(hoje_v)))
        self._rc_cars.setText(str(len(cars))); self._rc_cam.setText(str(len(cam)))

    def _sel(self):
        rows = self._tbl.selectionModel().selectedRows()
        if not rows: return None
        row = rows[0].row()
        return self._lista[row] if row < len(self._lista) else None

    def _on_sel(self):
        v = self._sel(); tem = v is not None; dentro = tem and v.status == STATUS_DENTRO
        self._btn_saida.setEnabled(dentro); self._btn_editar.setEnabled(tem); self._btn_excluir.setEnabled(tem)

    def _on_nova_entrada(self):
        m = ModalVeiculo(parent=self); m.salvo.connect(lambda _: self._carregar()); m.exec()

    def _on_saida(self):
        v = self._sel()
        if not v or v.status != STATUS_DENTRO: return
        m = ModalSaidaVeiculo(v, parent=self); m.confirmado.connect(lambda _: self._carregar()); m.exec()

    def _on_editar(self):
        v = self._sel()
        if not v: return
        m = ModalVeiculo(dto=v, parent=self); m.salvo.connect(lambda _: self._carregar()); m.exec()

    def _on_excluir(self):
        v = self._sel()
        if not v: return
        r = QMessageBox.warning(self, "Confirmar exclusão", f"Excluir permanentemente o veículo <b>{v.placa}</b>?",
                                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if r != QMessageBox.Yes: return
        if VeiculoRepo.excluir(v.id): self._carregar()
        else: QMessageBox.critical(self, "Erro", "Não foi possível excluir o registro.")


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO DE VISITANTES
# ══════════════════════════════════════════════════════════════════════════════
# Espelha o módulo de Veículos acima — mesma estrutura DTO/Repo/Modais —
# pra manter consistência visual e de comportamento na portaria.

class VisitanteDTO:
    def __init__(self, id=None, nome="", documento="", telefone="", empresa_visitada="",
                 pessoa_visitada="", motivo="", status=STATUS_DENTRO,
                 entrada=None, saida=None, operador="portaria"):
        self.id = id; self.nome = nome.strip(); self.documento = documento.strip()
        self.telefone = telefone.strip(); self.empresa_visitada = empresa_visitada.strip()
        self.pessoa_visitada = pessoa_visitada.strip(); self.motivo = motivo.strip()
        self.status = status; self.entrada = entrada or datetime.now()
        self.saida = saida; self.operador = operador


class VisitanteRepo:
    @staticmethod
    def listar(inicio: datetime) -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.visitante import Visitante
            rows = s.query(Visitante).filter(Visitante.entrada >= inicio).order_by(Visitante.entrada.desc()).all()
            return [VisitanteDTO(id=v.id, nome=v.nome, documento=v.documento or "", telefone=v.telefone or "",
                                 empresa_visitada=v.empresa_visitada or "", pessoa_visitada=v.pessoa_visitada or "",
                                 motivo=v.motivo or "", status=v.status, entrada=v.entrada, saida=v.saida,
                                 operador=v.operador or "portaria") for v in rows]
        except Exception as e: print(f"[VisitanteRepo.listar] {e}"); return []
        finally: s.close()

    @staticmethod
    def dentro() -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.visitante import Visitante
            rows = s.query(Visitante).filter(Visitante.status == STATUS_DENTRO).order_by(Visitante.entrada.desc()).all()
            return [VisitanteDTO(id=v.id, nome=v.nome, documento=v.documento or "", telefone=v.telefone or "",
                                 empresa_visitada=v.empresa_visitada or "", pessoa_visitada=v.pessoa_visitada or "",
                                 motivo=v.motivo or "", status=v.status, entrada=v.entrada, saida=v.saida,
                                 operador=v.operador or "portaria") for v in rows]
        except Exception as e: print(f"[VisitanteRepo.dentro] {e}"); return []
        finally: s.close()

    @staticmethod
    def contar_dentro() -> int:
        s = _get_session()
        if not s: return 0
        try:
            from app.models.visitante import Visitante
            return s.query(Visitante).filter(Visitante.status == STATUS_DENTRO).count()
        except Exception: return 0
        finally: s.close()

    @staticmethod
    def registrar_entrada(dto: "VisitanteDTO"):
        s = _get_session()
        if not s: return None
        try:
            from app.models.visitante import Visitante
            v = Visitante(nome=dto.nome, documento=dto.documento, telefone=dto.telefone,
                          empresa_visitada=dto.empresa_visitada, pessoa_visitada=dto.pessoa_visitada,
                          motivo=dto.motivo, status=STATUS_DENTRO, entrada=dto.entrada, saida=None,
                          operador=dto.operador)
            s.add(v); s.commit(); return v.id
        except Exception as e: print(f"[VisitanteRepo.entrada] {e}"); s.rollback(); return None
        finally: s.close()

    @staticmethod
    def registrar_saida(vid: int) -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.visitante import Visitante
            v = s.get(Visitante, vid)
            if not v: return False
            v.status = STATUS_SAIU; v.saida = datetime.now(); s.commit(); return True
        except Exception as e: print(f"[VisitanteRepo.saida] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def atualizar(dto: "VisitanteDTO") -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.visitante import Visitante
            v = s.get(Visitante, dto.id)
            if not v: return False
            v.nome = dto.nome; v.documento = dto.documento; v.telefone = dto.telefone
            v.empresa_visitada = dto.empresa_visitada; v.pessoa_visitada = dto.pessoa_visitada
            v.motivo = dto.motivo
            s.commit(); return True
        except Exception as e: print(f"[VisitanteRepo.atualizar] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def excluir(vid: int) -> bool:
        s = _get_session()
        if not s: return False
        try:
            from app.models.visitante import Visitante
            v = s.get(Visitante, vid)
            if not v: return False
            s.delete(v); s.commit(); return True
        except Exception as e: print(f"[VisitanteRepo.excluir] {e}"); s.rollback(); return False
        finally: s.close()

    @staticmethod
    def buscar(termo: str) -> list:
        s = _get_session()
        if not s: return []
        try:
            from app.models.visitante import Visitante
            rows = (s.query(Visitante)
                    .filter(Visitante.nome.ilike(f"%{termo}%") | Visitante.documento.ilike(f"%{termo}%") |
                            Visitante.empresa_visitada.ilike(f"%{termo}%") | Visitante.pessoa_visitada.ilike(f"%{termo}%"))
                    .order_by(Visitante.entrada.desc()).limit(50).all())
            return [VisitanteDTO(id=v.id, nome=v.nome, documento=v.documento or "", telefone=v.telefone or "",
                                 empresa_visitada=v.empresa_visitada or "", pessoa_visitada=v.pessoa_visitada or "",
                                 motivo=v.motivo or "", status=v.status, entrada=v.entrada, saida=v.saida,
                                 operador=v.operador or "portaria") for v in rows]
        except Exception as e: print(f"[VisitanteRepo.buscar] {e}"); return []
        finally: s.close()


class ModalVisitante(QDialog):
    salvo = Signal(object)

    def __init__(self, dto: VisitanteDTO = None, parent=None):
        super().__init__(parent)
        self._dto = dto; self._is_new = dto is None
        titulo = "Registrar Entrada de Visitante" if self._is_new else "Editar Visitante"
        self.setWindowTitle(titulo); self.setFixedSize(520, 540); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._build_ui(titulo)
        if dto: self._preencher(dto)

    def _build_ui(self, titulo):
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(16)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user-tie" if self._is_new else "fa5s.edit", color=COR_VISITANTE).pixmap(20, 20))
        lbl_t = QLabel(titulo); lbl_t.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO};")
        topo.addWidget(ic); topo.addWidget(lbl_t); topo.addStretch()
        lay.addLayout(topo); lay.addWidget(_sep())
        grid = QGridLayout(); grid.setSpacing(12); grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(_label_campo("NOME *"), 0, 0, 1, 2)
        self._nome = _campo_input("Nome completo do visitante"); grid.addWidget(self._nome, 1, 0, 1, 2)
        grid.addWidget(_label_campo("CPF / RG"), 2, 0)
        self._documento = _campo_input("Documento de identificação"); grid.addWidget(self._documento, 3, 0)
        grid.addWidget(_label_campo("TELEFONE"), 2, 1)
        self._telefone = _campo_input("Ex: (00) 00000-0000"); grid.addWidget(self._telefone, 3, 1)
        grid.addWidget(_label_campo("PROCURA POR"), 4, 0, 1, 2)
        self._pessoa_visitada = _campo_input("Nome do colaborador/setor que está visitando"); grid.addWidget(self._pessoa_visitada, 5, 0, 1, 2)
        grid.addWidget(_label_campo("EMPRESA / SETOR VISITADO"), 6, 0, 1, 2)
        self._empresa_visitada = _campo_input("Razão social ou departamento"); grid.addWidget(self._empresa_visitada, 7, 0, 1, 2)
        grid.addWidget(_label_campo("MOTIVO DA VISITA"), 8, 0, 1, 2)
        self._motivo = QTextEdit(); self._motivo.setFixedHeight(60); self._motivo.setPlaceholderText("Reunião, entrega, manutenção…")
        self._motivo.setStyleSheet(f"QTextEdit {{ background: white; color: {COR_TITULO}; border: 1.5px solid #CBD5E1; border-radius: 6px; padding: 6px 12px; font-size: 13px; }} QTextEdit:focus {{ border-color: {COR_SB_ACENTO}; }}")
        grid.addWidget(self._motivo, 9, 0, 1, 2)
        lay.addLayout(grid); lay.addStretch()
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = _btn_secundario("  Cancelar", "fa5s.times"); btn_c.clicked.connect(self.reject)
        lbl_s = "  Registrar Entrada" if self._is_new else "  Salvar Alterações"
        ic_s  = "fa5s.sign-in-alt"    if self._is_new else "fa5s.save"
        self._btn_s = _btn_primario(lbl_s, ic_s, COR_VISITANTE, "#5B21B6")
        self._btn_s.clicked.connect(self._on_salvar)
        btns.addWidget(btn_c); btns.addWidget(self._btn_s); lay.addLayout(btns)

    def _preencher(self, dto):
        self._nome.setText(dto.nome); self._documento.setText(dto.documento)
        self._telefone.setText(dto.telefone); self._pessoa_visitada.setText(dto.pessoa_visitada)
        self._empresa_visitada.setText(dto.empresa_visitada); self._motivo.setPlainText(dto.motivo)

    def _on_salvar(self):
        nome = self._nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do visitante."); self._nome.setFocus(); return
        dto = VisitanteDTO(id=self._dto.id if self._dto else None, nome=nome,
                           documento=self._documento.text().strip(), telefone=self._telefone.text().strip(),
                           pessoa_visitada=self._pessoa_visitada.text().strip(),
                           empresa_visitada=self._empresa_visitada.text().strip(),
                           motivo=self._motivo.toPlainText().strip(), operador=_get_operador())
        if self._is_new:
            vid = VisitanteRepo.registrar_entrada(dto)
            if vid is None: QMessageBox.critical(self, "Erro", "Não foi possível registrar no banco."); return
            dto.id = vid
        else:
            if not VisitanteRepo.atualizar(dto): QMessageBox.critical(self, "Erro", "Não foi possível atualizar."); return
        self.salvo.emit(dto); self.accept()


class ModalSaidaVisitante(QDialog):
    confirmado = Signal(int)

    def __init__(self, dto: VisitanteDTO, parent=None):
        super().__init__(parent)
        self._dto = dto; self.setWindowTitle("Registrar Saída de Visitante")
        self.setFixedSize(420, 280); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(16)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.sign-out-alt", color=COR_AMARELO_TEXTO).pixmap(22, 22))
        vl = QVBoxLayout(); vl.setSpacing(2)
        vl.addWidget(self._lbl("Registrar Saída de Visitante", f"font-size: 15px; font-weight: bold; color: {COR_TITULO};"))
        vl.addWidget(self._lbl("Confirme os dados antes de registrar a saída:", f"font-size: 11px; color: {COR_SUBTITULO};"))
        topo.addWidget(ic); topo.addLayout(vl); topo.addStretch(); lay.addLayout(topo); lay.addWidget(_sep())
        frame_info = _card(); fl = QVBoxLayout(frame_info); fl.setContentsMargins(16, 12, 16, 12); fl.setSpacing(6)
        for label, valor in [("Nome:", self._dto.nome), ("Procura por:", self._dto.pessoa_visitada or "—"),
                              ("Setor:", self._dto.empresa_visitada or "—"),
                              ("Entrada:", self._dto.entrada.strftime("%d/%m/%Y %H:%M") if self._dto.entrada else "—")]:
            row = QHBoxLayout()
            ll = QLabel(label); ll.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold;")
            lv = QLabel(valor); lv.setStyleSheet(f"font-size: 12px; color: {COR_TITULO}; font-weight: bold;")
            row.addWidget(ll); row.addStretch(); row.addWidget(lv); fl.addLayout(row)
        lay.addWidget(frame_info); lay.addStretch()
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = _btn_secundario("  Cancelar", "fa5s.times"); btn_c.clicked.connect(self.reject)
        btn_ok = _btn_primario("  Confirmar Saída", "fa5s.sign-out-alt", COR_AMARELO_TEXTO, "#78350F")
        btn_ok.clicked.connect(self._on_confirmar)
        btns.addWidget(btn_c); btns.addWidget(btn_ok); lay.addLayout(btns)

    def _lbl(self, texto, estilo):
        l = QLabel(texto); l.setStyleSheet(estilo); return l

    def _on_confirmar(self):
        if not VisitanteRepo.registrar_saida(self._dto.id):
            QMessageBox.critical(self, "Erro", "Não foi possível registrar a saída."); return
        self.confirmado.emit(self._dto.id); self.accept()


class JanelaVisitantes(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabelas_filtraveis = []
        self.setWindowTitle("Histórico de Visitantes"); self.setWindowFlag(Qt.Window)
        self.setMinimumSize(860, 540); self.resize(1000, 640)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QDialog {{ background-color: {COR_BG}; }}")
        self._build_ui(); self._carregar_todos()

    def _build_ui(self):
        raiz = QVBoxLayout(self); raiz.setContentsMargins(28, 24, 28, 24); raiz.setSpacing(16)
        hdr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user-tie", color=COR_VISITANTE).pixmap(22, 22)); ic.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel("Histórico de Visitantes"); lt.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_TITULO};")
        ls = QLabel("Registros de entrada e saída de visitantes na unidade"); ls.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(lt); vl.addWidget(ls)
        hdr.addWidget(ic); hdr.addLayout(vl); hdr.addStretch()
        btn_f = _btn_primario("  Fechar", "fa5s.times", COR_SUBTITULO, COR_TITULO, 34); btn_f.clicked.connect(self.close)
        hdr.addWidget(btn_f); raiz.addLayout(hdr); raiz.addWidget(_sep())
        res = QHBoxLayout(); res.setSpacing(12)
        self._lbl_hoje   = self._rc(res, "fa5s.sun",           COR_VISITANTE,     "Hoje")
        self._lbl_semana = self._rc(res, "fa5s.calendar-week", COR_SB_ACENTO,     "Esta semana")
        self._lbl_mes    = self._rc(res, "fa5s.calendar-alt",  COR_AMARELO_TEXTO, "Este mês")
        self._lbl_dentro = self._rc(res, "fa5s.building",      COR_VERDE_TEXTO,   "Agora na unidade")
        raiz.addLayout(res)
        barra_busca, self._campo_busca_nome = _barra_busca_nome("Filtrar por nome do visitante…")
        self._campo_busca_nome.textChanged.connect(self._filtrar_por_nome)
        raiz.addWidget(barra_busca)
        self._tabs = QTabWidget(); self._tabs.setStyleSheet(_tab_estilo(COR_VISITANTE)); raiz.addWidget(self._tabs, 1)
        cols = ["Nome", "Documento", "Procura por", "Setor", "Entrada", "Saída", "Status"]
        self._tbl_hoje   = self._add_tab("  Hoje  ",        cols)
        self._tbl_semana = self._add_tab("  Esta Semana  ", cols)
        self._tbl_mes    = self._add_tab("  Este Mês  ",    cols)

    def _filtrar_por_nome(self, texto: str):
        _filtrar_tabelas_por_texto(self._tabelas_filtraveis, texto, coluna=0)

    def _rc(self, lay, icone, cor, titulo):
        f = QFrame(); f.setStyleSheet(f"QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-top: 3px solid {cor}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        fl = QVBoxLayout(f); fl.setContentsMargins(16, 12, 16, 12); fl.setSpacing(4)
        topo = QHBoxLayout(); ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(14, 14)); ic.setStyleSheet("border: none; background: transparent;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch()
        lv = QLabel("—"); lv.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {cor};")
        fl.addLayout(topo); fl.addWidget(lv); lay.addWidget(f, 1); return lv

    def _add_tab(self, label, cols):
        w = QWidget(); w.setStyleSheet(f"background: {COR_CARD_BG}; border: none;")
        lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0)
        tbl = QTableWidget(); tbl.setColumnCount(len(cols)); tbl.setHorizontalHeaderLabels(cols)
        tbl.setStyleSheet(_tabela_estilo()); tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False); tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers); tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False); tbl.setFocusPolicy(Qt.NoFocus)
        lay.addWidget(tbl); self._tabs.addTab(w, label); self._tabelas_filtraveis.append(tbl); return tbl

    def _fill(self, tbl, visitantes):
        tbl.setRowCount(len(visitantes))
        for row, v in enumerate(visitantes):
            e_str = v.entrada.strftime("%d/%m/%Y %H:%M") if v.entrada else "—"
            s_str = v.saida.strftime("%d/%m/%Y %H:%M")   if v.saida   else "—"
            for col, (txt, ctr, bld) in enumerate([
                (v.nome, False, True), (v.documento or "—", False, False), (v.pessoa_visitada or "—", False, False),
                (v.empresa_visitada or "—", False, False), (e_str, True, False), (s_str, True, False)]):
                it = QTableWidgetItem(str(txt)); it.setTextAlignment((Qt.AlignCenter if ctr else Qt.AlignLeft)|Qt.AlignVCenter)
                if bld: f = it.font(); f.setBold(True); it.setFont(f)
                tbl.setItem(row, col, it)
            it_st = QTableWidgetItem(v.status); it_st.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_st.setForeground(QColor(COR_VISITANTE)); it_st.setBackground(QColor(COR_VISITANTE_BG))
            else: it_st.setForeground(QColor(COR_SECAO_LABEL))
            tbl.setItem(row, 6, it_st)
        if not visitantes:
            tbl.setRowCount(1); it = QTableWidgetItem("Nenhum visitante registrado neste período")
            it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter); it.setForeground(QColor(COR_SECAO_LABEL))
            tbl.setItem(0, 0, it); tbl.setSpan(0, 0, 1, 7)

    def _carregar_todos(self):
        hoje = date.today()
        i_h  = datetime.combine(hoje, datetime.min.time())
        i_s  = datetime.combine(hoje - timedelta(days=hoje.weekday()), datetime.min.time())
        i_m  = datetime.combine(hoje.replace(day=1), datetime.min.time())
        v_h  = VisitanteRepo.listar(i_h); v_s = VisitanteRepo.listar(i_s); v_m = VisitanteRepo.listar(i_m)
        v_d  = VisitanteRepo.dentro()
        self._fill(self._tbl_hoje, v_h); self._fill(self._tbl_semana, v_s); self._fill(self._tbl_mes, v_m)
        self._lbl_hoje.setText(str(len(v_h))); self._lbl_semana.setText(str(len(v_s)))
        self._lbl_mes.setText(str(len(v_m))); self._lbl_dentro.setText(str(len(v_d)))
        if self._campo_busca_nome.text():
            self._filtrar_por_nome(self._campo_busca_nome.text())


class PainelVisitantes(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ThirdSys — Controle de Visitantes"); self.setWindowFlag(Qt.Window)
        self.setMinimumSize(1080, 640)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1280, screen.width()-80), min(760, screen.height()-80))
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QDialog {{ background-color: {COR_BG}; }}")
        self._lista: list = []
        self._build_ui(); self._carregar()

    def _build_ui(self):
        raiz = QVBoxLayout(self); raiz.setContentsMargins(28, 24, 28, 24); raiz.setSpacing(16)
        # Header
        hdr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user-tie", color=COR_VISITANTE).pixmap(26, 26)); ic.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel("Controle de Visitantes"); lt.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COR_TITULO};")
        ls = QLabel("Entrada e saída de visitantes — portaria"); ls.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO};")
        vl.addWidget(lt); vl.addWidget(ls); hdr.addWidget(ic); hdr.addLayout(vl); hdr.addStretch()
        btn_hist = _btn_secundario("  Histórico", "fa5s.history"); btn_hist.clicked.connect(lambda: JanelaVisitantes(self).exec())
        btn_f = _btn_primario("  Fechar", "fa5s.times", COR_SUBTITULO, COR_TITULO, 36); btn_f.clicked.connect(self.close)
        hdr.addWidget(btn_hist); hdr.addWidget(btn_f); raiz.addLayout(hdr)
        # Cards resumo
        res = QHBoxLayout(); res.setSpacing(12)
        self._rc_dentro = self._rc(res, "fa5s.building",  COR_VISITANTE,    "Visitantes na unidade")
        self._rc_hoje   = self._rc(res, "fa5s.sun",       COR_SB_ACENTO,    "Entradas hoje")
        raiz.addLayout(res)
        # Barra de ações
        barra = QFrame(); barra.setFixedHeight(52)
        barra.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; }} QLineEdit {{ border: none; background: transparent; }} QLabel {{ border: none; background: transparent; }}")
        bl = QHBoxLayout(barra); bl.setContentsMargins(14, 0, 10, 0); bl.setSpacing(10)
        ic_s = QLabel(); ic_s.setPixmap(qta.icon("fa5s.search", color=COR_SB_SUBTEXTO).pixmap(14, 14)); ic_s.setStyleSheet("background: transparent; border: none;")
        self._busca = QLineEdit(); self._busca.setPlaceholderText("Nome, documento, setor ou quem procura…"); self._busca.setStyleSheet(f"color: {COR_TITULO}; font-size: 13px;")
        self._busca.returnPressed.connect(self._carregar)
        bl.addWidget(ic_s); bl.addWidget(self._busca, 1)
        self._filtro = QComboBox()
        for o in ["Todos", "Dentro", "Saíram"]: self._filtro.addItem(o)
        self._filtro.setFixedHeight(34)
        self._filtro.setStyleSheet(f"QComboBox {{ background: {COR_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; padding: 0 8px; font-size: 12px; min-width: 90px; }} QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; selection-background-color: {COR_AZUL_BG}; }}")
        self._filtro.currentIndexChanged.connect(self._carregar); bl.addWidget(self._filtro)
        sv = QFrame(); sv.setFrameShape(QFrame.VLine); sv.setFixedWidth(1); sv.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;"); bl.addWidget(sv)
        self._btn_entrada = _btn_primario("  Nova Entrada", "fa5s.sign-in-alt", COR_VISITANTE, "#5B21B6", 36)
        self._btn_entrada.clicked.connect(self._on_nova_entrada)
        self._btn_saida = _btn_primario("  Registrar Saída", "fa5s.sign-out-alt", COR_AMARELO_TEXTO, "#78350F", 36)
        self._btn_saida.setEnabled(False); self._btn_saida.clicked.connect(self._on_saida)
        self._btn_editar = _btn_secundario("  Editar", "fa5s.edit", 36)
        self._btn_editar.setEnabled(False); self._btn_editar.clicked.connect(self._on_editar)
        self._btn_excluir = _btn_primario("  Excluir", "fa5s.trash", COR_VERMELHO_TEXTO, "#7F1D1D", 36)
        self._btn_excluir.setEnabled(False); self._btn_excluir.clicked.connect(self._on_excluir)
        btn_lp = QPushButton(); btn_lp.setIcon(qta.icon("fa5s.times", color=COR_SB_SUBTEXTO)); btn_lp.setIconSize(QSize(12, 12))
        btn_lp.setFixedSize(36, 36); btn_lp.setCursor(Qt.PointingHandCursor); btn_lp.setToolTip("Limpar busca")
        btn_lp.setAutoDefault(False); btn_lp.setDefault(False)
        btn_lp.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_lp.clicked.connect(lambda: (self._busca.clear(), self._filtro.setCurrentIndex(0), self._carregar()))
        for w in [self._btn_entrada, self._btn_saida, self._btn_editar, self._btn_excluir, btn_lp]: bl.addWidget(w)
        raiz.addWidget(barra)
        # Tabela
        tbl_frame = _card(); tl = QVBoxLayout(tbl_frame); tl.setContentsMargins(0, 0, 0, 0); tl.setSpacing(0)
        cols = ["Nome", "Documento", "Telefone", "Procura por", "Setor", "Entrada", "Saída", "Status", "Operador"]
        self._tbl = QTableWidget(); self._tbl.setColumnCount(len(cols)); self._tbl.setHorizontalHeaderLabels(cols)
        self._tbl.setStyleSheet(_tabela_estilo())
        hh = self._tbl.horizontalHeader(); hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self._tbl.verticalHeader().setVisible(False); self._tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tbl.setEditTriggers(QAbstractItemView.NoEditTriggers); self._tbl.setAlternatingRowColors(True)
        self._tbl.setShowGrid(False); self._tbl.setFocusPolicy(Qt.NoFocus)
        self._tbl.selectionModel().selectionChanged.connect(self._on_sel); self._tbl.doubleClicked.connect(self._on_editar)
        tl.addWidget(self._tbl); raiz.addWidget(tbl_frame, 1)
        # Rodapé
        rod = QHBoxLayout()
        self._lbl_total = QLabel("0 registros"); self._lbl_total.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL};")
        self._lbl_upd = QLabel(""); self._lbl_upd.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL};")
        btn_r = QPushButton(); btn_r.setIcon(qta.icon("fa5s.sync-alt", color=COR_SB_SUBTEXTO)); btn_r.setIconSize(QSize(12, 12))
        btn_r.setFixedSize(30, 30); btn_r.setCursor(Qt.PointingHandCursor); btn_r.setToolTip("Atualizar")
        btn_r.setAutoDefault(False); btn_r.setDefault(False)
        btn_r.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QPushButton:hover {{ background: {COR_CARD_BG}; }}")
        btn_r.clicked.connect(self._carregar)
        rod.addWidget(self._lbl_total); rod.addStretch(); rod.addWidget(self._lbl_upd); rod.addWidget(btn_r)
        raiz.addLayout(rod)

    def _rc(self, lay, icone, cor, titulo):
        f = QFrame(); f.setStyleSheet(f"QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-top: 3px solid {cor}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        fl = QVBoxLayout(f); fl.setContentsMargins(14, 10, 14, 10); fl.setSpacing(2)
        topo = QHBoxLayout(); ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(13, 13)); ic.setStyleSheet("background: transparent; border: none;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 10px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch()
        lv = QLabel("—"); lv.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {cor};")
        fl.addLayout(topo); fl.addWidget(lv); lay.addWidget(f, 1); return lv

    def _carregar(self):
        filtro = self._filtro.currentText(); termo = self._busca.text().strip()
        if termo: todos = VisitanteRepo.buscar(termo)
        else:
            inicio = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
            todos  = VisitanteRepo.listar(inicio)
        if filtro == "Dentro":  todos = [v for v in todos if v.status == STATUS_DENTRO]
        elif filtro == "Saíram": todos = [v for v in todos if v.status == STATUS_SAIU]
        self._lista = todos; self._fill(); self._upd_cards()
        self._lbl_upd.setText(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")

    def _fill(self):
        self._tbl.setRowCount(len(self._lista))
        for row, v in enumerate(self._lista):
            e_s = v.entrada.strftime("%d/%m %H:%M") if v.entrada else "—"
            sa_s = v.saida.strftime("%d/%m %H:%M")  if v.saida   else "—"
            dados = [(v.nome, False, True), (v.documento or "—", False, False), (v.telefone or "—", False, False),
                     (v.pessoa_visitada or "—", False, False), (v.empresa_visitada or "—", False, False),
                     (e_s, True, False), (sa_s, True, False)]
            for col, (txt, ctr, bld) in enumerate(dados):
                it = QTableWidgetItem(str(txt)); it.setTextAlignment((Qt.AlignCenter if ctr else Qt.AlignLeft)|Qt.AlignVCenter)
                if bld: f = it.font(); f.setBold(True); it.setFont(f)
                if v.status == STATUS_DENTRO: it.setBackground(QColor(COR_VISITANTE_BG))
                self._tbl.setItem(row, col, it)
            it_st = QTableWidgetItem(v.status); it_st.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_st.setForeground(QColor(COR_VISITANTE)); it_st.setBackground(QColor(COR_VISITANTE_BG))
            else: it_st.setForeground(QColor(COR_SECAO_LABEL))
            self._tbl.setItem(row, 7, it_st)
            it_op = QTableWidgetItem(v.operador or "—"); it_op.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            if v.status == STATUS_DENTRO: it_op.setBackground(QColor(COR_VISITANTE_BG))
            self._tbl.setItem(row, 8, it_op)
        if not self._lista:
            self._tbl.setRowCount(1); it = QTableWidgetItem("Nenhum visitante encontrado")
            it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter); it.setForeground(QColor(COR_SECAO_LABEL))
            self._tbl.setItem(0, 0, it); self._tbl.setSpan(0, 0, 1, 9)
        self._lbl_total.setText(f"{len(self._lista)} registro(s)")

    def _upd_cards(self):
        dentro = [v for v in self._lista if v.status == STATUS_DENTRO]
        ini_h  = datetime.combine(date.today(), datetime.min.time())
        hoje_v = [v for v in self._lista if v.entrada and v.entrada >= ini_h]
        self._rc_dentro.setText(str(len(dentro))); self._rc_hoje.setText(str(len(hoje_v)))

    def _sel(self):
        rows = self._tbl.selectionModel().selectedRows()
        if not rows: return None
        row = rows[0].row()
        return self._lista[row] if row < len(self._lista) else None

    def _on_sel(self):
        v = self._sel(); tem = v is not None; dentro = tem and v.status == STATUS_DENTRO
        self._btn_saida.setEnabled(dentro); self._btn_editar.setEnabled(tem); self._btn_excluir.setEnabled(tem)

    def _on_nova_entrada(self):
        m = ModalVisitante(parent=self); m.salvo.connect(lambda _: self._carregar()); m.exec()

    def _on_saida(self):
        v = self._sel()
        if not v or v.status != STATUS_DENTRO: return
        m = ModalSaidaVisitante(v, parent=self); m.confirmado.connect(lambda _: self._carregar()); m.exec()

    def _on_editar(self):
        v = self._sel()
        if not v: return
        m = ModalVisitante(dto=v, parent=self); m.salvo.connect(lambda _: self._carregar()); m.exec()

    def _on_excluir(self):
        v = self._sel()
        if not v: return
        r = QMessageBox.warning(self, "Confirmar exclusão", f"Excluir permanentemente o visitante <b>{v.nome}</b>?",
                                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if r != QMessageBox.Yes: return
        if VisitanteRepo.excluir(v.id): self._carregar()
        else: QMessageBox.critical(self, "Erro", "Não foi possível excluir o registro.")


# ══════════════════════════════════════════════════════════════════════════════
# COMPONENTES ORIGINAIS DA PORTARIA
# ══════════════════════════════════════════════════════════════════════════════

class JanelaDetalhe(QDialog):
    def __init__(self, titulo, subtitulo, icone, cor_icone, cor_acento, parent=None):
        super().__init__(parent)
        self._cor_acento = cor_acento
        self._tabelas_filtraveis = []
        self.setWindowTitle(titulo); self.setWindowFlag(Qt.Window)
        self.setMinimumSize(860, 580); self.resize(980, 660)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QDialog {{ background-color: {COR_BG}; }}")
        raiz = QVBoxLayout(self); raiz.setContentsMargins(28, 24, 28, 24); raiz.setSpacing(16)
        hdr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor_icone).pixmap(24, 24)); ic.setStyleSheet("background: transparent; border: none;")
        hdr.addWidget(ic)
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_TITULO}; border: none; background: transparent;")
        ls = QLabel(subtitulo); ls.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO}; border: none; background: transparent;")
        vl.addWidget(lt); vl.addWidget(ls); hdr.addLayout(vl); hdr.addStretch()
        btn_f = QPushButton("  Fechar"); btn_f.setIcon(qta.icon("fa5s.times", color="white")); btn_f.setIconSize(QSize(11, 11))
        btn_f.setFixedHeight(34); btn_f.setCursor(Qt.PointingHandCursor)
        btn_f.setStyleSheet(f"QPushButton {{ background: {COR_SUBTITULO}; color: white; border: none; border-radius: 4px; padding: 0 16px; font-size: 12px; }} QPushButton:hover {{ background: {COR_TITULO}; }}")
        btn_f.clicked.connect(self.close); hdr.addWidget(btn_f)
        raiz.addLayout(hdr); raiz.addWidget(_sep())
        self._resumo_layout = QHBoxLayout(); self._resumo_layout.setSpacing(12); raiz.addLayout(self._resumo_layout)
        barra_busca, self._campo_busca_nome = _barra_busca_nome("Filtrar por nome do colaborador…")
        self._campo_busca_nome.textChanged.connect(self._filtrar_por_nome)
        raiz.addWidget(barra_busca)
        self._tabs = QTabWidget(); self._tabs.setStyleSheet(_tab_estilo(cor_acento)); raiz.addWidget(self._tabs, 1)
        self._tab_hoje   = self._new_tab_widget()
        self._tab_semana = self._new_tab_widget()
        self._tab_mes    = self._new_tab_widget()
        self._tabs.addTab(self._tab_hoje,   "  Hoje  ")
        self._tabs.addTab(self._tab_semana, "  Esta Semana  ")
        self._tabs.addTab(self._tab_mes,    "  Este Mês  ")
        self._popular_dados()

    def _filtrar_por_nome(self, texto: str):
        # Coluna 0 = "Colaborador" em todas as tabelas desta janela
        _filtrar_tabelas_por_texto(self._tabelas_filtraveis, texto, coluna=0)

    def _new_tab_widget(self):
        w = QWidget(); w.setStyleSheet(f"background: {COR_CARD_BG}; border: none;"); return w

    def _add_card_resumo(self, icone, cor, titulo, valor="—") -> QLabel:
        f = QFrame(); f.setStyleSheet(f"QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-top: 3px solid {cor}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        fl = QVBoxLayout(f); fl.setContentsMargins(16, 12, 16, 12); fl.setSpacing(4)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(14, 14)); ic.setStyleSheet("border: none; background: transparent;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold; border: none; background: transparent;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch()
        lv = QLabel(valor); lv.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {cor}; border: none; background: transparent;")
        fl.addLayout(topo); fl.addWidget(lv); self._resumo_layout.addWidget(f, 1); return lv

    def _criar_tabela(self, colunas, layout_pai) -> QTableWidget:
        tbl = QTableWidget(); tbl.setColumnCount(len(colunas)); tbl.setHorizontalHeaderLabels(colunas)
        tbl.setStyleSheet(_tabela_estilo()); tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False); tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers); tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False); tbl.setFocusPolicy(Qt.NoFocus)
        layout_pai.addWidget(tbl); self._tabelas_filtraveis.append(tbl); return tbl

    def _item(self, texto, align=Qt.AlignLeft | Qt.AlignVCenter):
        it = QTableWidgetItem(str(texto)); it.setTextAlignment(align); return it

    def _linha_vazia(self, tbl, ncols, msg):
        tbl.setRowCount(1)
        it = QTableWidgetItem(msg); it.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter); it.setForeground(QColor(COR_SECAO_LABEL))
        tbl.setItem(0, 0, it); tbl.setSpan(0, 0, 1, ncols)

    def _popular_dados(self): pass


class JanelaLiberados(JanelaDetalhe):
    def __init__(self, parent=None):
        super().__init__("Colaboradores Liberados", "Histórico de entradas autorizadas",
                         "fa5s.user-check", COR_VERDE_TEXTO, COR_VERDE_TEXTO, parent)

    def _popular_dados(self):
        self._lv_h = self._add_card_resumo("fa5s.sun",           COR_VERDE_TEXTO,  "Hoje")
        self._lv_s = self._add_card_resumo("fa5s.calendar-week", COR_SB_ACENTO,    "Esta semana")
        self._lv_m = self._add_card_resumo("fa5s.calendar-alt",  COR_AMARELO_TEXTO,"Este mês")
        cols = ["Colaborador", "Empresa", "Horário de Entrada", "Operador"]
        for tab, attr in [(self._tab_hoje, "_tbl_h"), (self._tab_semana, "_tbl_s"), (self._tab_mes, "_tbl_m")]:
            lay = QVBoxLayout(tab); lay.setContentsMargins(0, 0, 0, 0)
            setattr(self, attr, self._criar_tabela(cols, lay))
        for p in ("h", "s", "m"): self._carregar(p)

    def _carregar(self, p):
        hoje = date.today()
        inicio = {"h": datetime.combine(hoje, datetime.min.time()),
                  "s": datetime.combine(hoje - timedelta(days=hoje.weekday()), datetime.min.time()),
                  "m": datetime.combine(hoje.replace(day=1), datetime.min.time())}[p]
        linhas = []
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from app.models.trabalhador import Trabalhador
            session = get_session()
            rows = (session.query(Acesso, Trabalhador).join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                    .filter(Acesso.tipo == "entrada", Acesso.horario >= inicio).order_by(Acesso.horario.desc()).all())
            for acesso, trab in rows:
                emp  = trab.empresa.razao_social if trab.empresa else "—"
                hora = acesso.horario.strftime("%d/%m/%Y %H:%M") if acesso.horario else "—"
                op   = getattr(acesso, "operador", "portaria") or "portaria"
                linhas.append((trab.nome, emp, hora, op))
            session.close()
        except Exception: pass
        tbl = {"h": self._tbl_h, "s": self._tbl_s, "m": self._tbl_m}[p]
        tbl.setRowCount(len(linhas))
        for row, (nome, emp, hora, op) in enumerate(linhas):
            tbl.setItem(row, 0, self._item(nome)); tbl.setItem(row, 1, self._item(emp))
            tbl.setItem(row, 2, self._item(hora, Qt.AlignCenter | Qt.AlignVCenter))
            tbl.setItem(row, 3, self._item(op,   Qt.AlignCenter | Qt.AlignVCenter))
        {"h": self._lv_h, "s": self._lv_s, "m": self._lv_m}[p].setText(str(len(linhas)))
        if not linhas: self._linha_vazia(tbl, 4, "Nenhuma entrada registrada neste período")
        if self._campo_busca_nome.text(): self._filtrar_por_nome(self._campo_busca_nome.text())


class JanelaBloqueados(JanelaDetalhe):
    def __init__(self, parent=None):
        super().__init__("Colaboradores Bloqueados", "Histórico de acessos negados e bloqueios registrados",
                         "fa5s.user-slash", COR_VERMELHO_TEXTO, COR_VERMELHO_TEXTO, parent)

    def _popular_dados(self):
        self._lv_h = self._add_card_resumo("fa5s.sun",           COR_VERMELHO_TEXTO, "Hoje")
        self._lv_s = self._add_card_resumo("fa5s.calendar-week", COR_SB_ACENTO,      "Esta semana")
        self._lv_m = self._add_card_resumo("fa5s.calendar-alt",  COR_AMARELO_TEXTO,  "Este mês")
        cols = ["Colaborador", "Empresa", "Motivos", "Horário", "Operador"]
        for tab, attr in [(self._tab_hoje, "_tbl_h"), (self._tab_semana, "_tbl_s"), (self._tab_mes, "_tbl_m")]:
            lay = QVBoxLayout(tab); lay.setContentsMargins(0, 0, 0, 0)
            setattr(self, attr, self._criar_tabela(cols, lay))
        for p in ("h", "s", "m"): self._carregar(p)

    def _carregar(self, p):
        hoje = date.today()
        inicio = {"h": datetime.combine(hoje, datetime.min.time()),
                  "s": datetime.combine(hoje - timedelta(days=hoje.weekday()), datetime.min.time()),
                  "m": datetime.combine(hoje.replace(day=1), datetime.min.time())}[p]
        linhas = []
        try:
            from app.core.database import get_session
            from app.models.bloqueio import Bloqueio
            from app.models.trabalhador import Trabalhador
            session = get_session()
            rows = (session.query(Bloqueio, Trabalhador).join(Trabalhador, Bloqueio.trabalhador_id == Trabalhador.id)
                    .filter(Bloqueio.criado_em >= inicio).order_by(Bloqueio.criado_em.desc()).all())
            for bloqueio, trab in rows:
                emp = trab.empresa.razao_social if trab.empresa else "—"
                motivos = []
                if getattr(bloqueio, "doc_incompleta",      False): motivos.append("Doc. inválida")
                if getattr(bloqueio, "determinacao_gestao", False): motivos.append("Bloqueio manual")
                motivos_str = ", ".join(motivos) if motivos else (bloqueio.tipo or "—")
                hora = bloqueio.criado_em.strftime("%d/%m/%Y %H:%M") if bloqueio.criado_em else "—"
                op   = getattr(bloqueio, "registrado_por", "portaria") or "portaria"
                linhas.append((trab.nome, emp, motivos_str, hora, op))
            session.close()
        except Exception: pass
        tbl = {"h": self._tbl_h, "s": self._tbl_s, "m": self._tbl_m}[p]
        tbl.setRowCount(len(linhas))
        for row, (nome, emp, mot, hora, op) in enumerate(linhas):
            tbl.setItem(row, 0, self._item(nome)); tbl.setItem(row, 1, self._item(emp))
            tbl.setItem(row, 2, self._item(mot))
            tbl.setItem(row, 3, self._item(hora, Qt.AlignCenter | Qt.AlignVCenter))
            tbl.setItem(row, 4, self._item(op,   Qt.AlignCenter | Qt.AlignVCenter))
            for col in range(5):
                it = tbl.item(row, col)
                if it: it.setBackground(QColor("#FFF8F8"))
        {"h": self._lv_h, "s": self._lv_s, "m": self._lv_m}[p].setText(str(len(linhas)))
        if not linhas: self._linha_vazia(tbl, 5, "Nenhum bloqueio registrado neste período")
        if self._campo_busca_nome.text(): self._filtrar_por_nome(self._campo_busca_nome.text())


class JanelaDentro(JanelaDetalhe):
    def __init__(self, parent=None):
        super().__init__("Dentro da Planta", "Colaboradores e visitantes que entraram e ainda não registraram saída",
                         "fa5s.building", COR_SB_ACENTO, COR_SB_ACENTO, parent)

    def _popular_dados(self):
        self._lv_h = self._add_card_resumo("fa5s.user-friends",  COR_SB_ACENTO,    "Atualmente dentro")
        self._lv_s = self._add_card_resumo("fa5s.calendar-week", COR_VERDE_TEXTO,   "Pico esta semana")
        self._lv_m = self._add_card_resumo("fa5s.chart-bar",     COR_AMARELO_TEXTO, "Total este mês")
        # CORREÇÃO: coluna nova "Tipo" — antes esta janela só listava
        # colaboradores (via Acesso/Trabalhador). Agora ela também traz os
        # visitantes com status "Dentro" (aba Hoje) ou que entraram no
        # período (Semana/Mês), destacados com cor própria (roxo) tanto na
        # coluna Tipo quanto no fundo da linha inteira, pra diferenciar
        # rapidamente de colaboradores numa lista combinada.
        cols = ["Colaborador", "Tipo", "Empresa", "Função", "Entrada", "Tempo dentro"]
        lay_h = QVBoxLayout(self._tab_hoje); lay_h.setContentsMargins(0, 0, 0, 0)
        self._tbl_h = self._criar_tabela(cols, lay_h)
        # Menu de contexto (botão direito) — só na aba "Hoje", que reflete
        # quem está de fato dentro da planta agora. Permite, entre outras
        # ações dinâmicas, registrar a entrada do veículo de quem já está
        # dentro (ex.: colaboradora que entrou a pé e depois trouxe o carro).
        # Só se aplica a linhas de colaborador — visitantes não têm veículo
        # vinculado por nome neste fluxo.
        self._tbl_h.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tbl_h.customContextMenuRequested.connect(self._abrir_menu_contexto)
        for tab, attr, aviso in [(self._tab_semana, "_tbl_s", True), (self._tab_mes, "_tbl_m", True)]:
            lay = QVBoxLayout(tab); lay.setContentsMargins(0, 0, 0, 0)
            if aviso:
                lbl = QLabel("⚠  Exibe todos que entraram no período (com ou sem saída registrada)")
                lbl.setStyleSheet(f"color: {COR_AMARELO_TEXTO}; font-size: 11px; padding: 6px 12px; background: {COR_AMARELO_BG}; border-bottom: 1px solid {COR_AMARELO_BORDA};")
                lay.addWidget(lbl)
            setattr(self, attr, self._criar_tabela(cols, lay))
        for p in ("h", "s", "m"): self._carregar(p)

    def _carregar(self, p):
        hoje = date.today(); agora = datetime.now()
        inicio = {"h": datetime.combine(hoje, datetime.min.time()),
                  "s": datetime.combine(hoje - timedelta(days=hoje.weekday()), datetime.min.time()),
                  "m": datetime.combine(hoje.replace(day=1), datetime.min.time())}[p]
        linhas = []  # cada item: (tid_ou_None, tipo, nome, emp, fn, hora, tempo)
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from app.models.trabalhador import Trabalhador
            from sqlalchemy import func
            session = get_session()
            if p == "h":
                subq = (session.query(Acesso.trabalhador_id, func.max(Acesso.horario).label("ultima"))
                        .filter(Acesso.horario >= inicio).group_by(Acesso.trabalhador_id).subquery())
                rows = (session.query(Acesso, Trabalhador)
                        .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                        .join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                        .filter(Acesso.tipo == "entrada").order_by(Acesso.horario).all())
            else:
                rows = (session.query(Acesso, Trabalhador)
                        .join(Trabalhador, Acesso.trabalhador_id == Trabalhador.id)
                        .filter(Acesso.tipo == "entrada", Acesso.horario >= inicio)
                        .order_by(Acesso.horario.desc()).all())
            for acesso, trab in rows:
                emp = trab.empresa.razao_social if trab.empresa else "—"
                fn  = trab.funcao or "—"; hora = acesso.horario.strftime("%H:%M") if acesso.horario else "—"
                if p == "h" and acesso.horario:
                    d = agora - acesso.horario; hh, mm = divmod(int(d.total_seconds())//60, 60); tempo = f"{hh}h {mm:02d}min"
                else:
                    tempo = acesso.horario.strftime("%d/%m %H:%M") if acesso.horario else "—"
                linhas.append((trab.id, "colaborador", trab.nome, emp, fn, hora, tempo))
            session.close()
        except Exception: pass

        # ── Visitantes — somados à mesma lista, destacados por cor própria ──
        try:
            if p == "h":
                visitantes = VisitanteRepo.dentro()
            else:
                visitantes = VisitanteRepo.listar(inicio)
            for v in visitantes:
                emp = v.empresa_visitada or "—"
                fn  = f"Visita: {v.pessoa_visitada}" if v.pessoa_visitada else "Visitante"
                hora = v.entrada.strftime("%H:%M") if v.entrada else "—"
                if p == "h" and v.entrada:
                    d = agora - v.entrada; hh, mm = divmod(int(d.total_seconds())//60, 60); tempo = f"{hh}h {mm:02d}min"
                else:
                    tempo = v.entrada.strftime("%d/%m %H:%M") if v.entrada else "—"
                linhas.append((None, "visitante", v.nome, emp, fn, hora, tempo))
        except Exception as e:
            print(f"[JanelaDentro._carregar visitantes] {e}")

        # Mantém ordenação por horário de entrada (mais antigos primeiro na
        # aba "Hoje", mais recentes primeiro nas demais) — igual ao
        # comportamento original de antes dos visitantes serem somados.
        def _chave_ordenacao(item):
            hora_str = item[5]
            return hora_str or ""
        if p == "h":
            linhas.sort(key=_chave_ordenacao)
        else:
            linhas.sort(key=_chave_ordenacao, reverse=True)

        tbl = {"h": self._tbl_h, "s": self._tbl_s, "m": self._tbl_m}[p]
        tbl.setRowCount(len(linhas))
        for row, (tid, tipo, nome, emp, fn, hora, tempo) in enumerate(linhas):
            eh_visitante = tipo == "visitante"
            it_nome = self._item(nome); it_nome.setData(Qt.UserRole, tid); it_nome.setData(Qt.UserRole + 1, tipo)
            it_tipo = self._item("Visitante" if eh_visitante else "Colaborador", Qt.AlignCenter | Qt.AlignVCenter)
            tbl.setItem(row, 0, it_nome); tbl.setItem(row, 1, it_tipo)
            tbl.setItem(row, 2, self._item(emp)); tbl.setItem(row, 3, self._item(fn))
            tbl.setItem(row, 4, self._item(hora,  Qt.AlignCenter | Qt.AlignVCenter))
            tbl.setItem(row, 5, self._item(tempo, Qt.AlignCenter | Qt.AlignVCenter))
            if eh_visitante:
                # Destaque visual: fundo roxo claro + texto roxo na coluna
                # "Tipo", pra identificar visitantes de imediato na lista
                # combinada com colaboradores.
                it_tipo.setForeground(QColor(COR_VISITANTE))
                for col in range(6):
                    it = tbl.item(row, col)
                    if it: it.setBackground(QColor(COR_VISITANTE_BG))
                f_bold = it_tipo.font(); f_bold.setBold(True); it_tipo.setFont(f_bold)
        {"h": self._lv_h, "s": self._lv_s, "m": self._lv_m}[p].setText(str(len(linhas)))
        if not linhas: self._linha_vazia(tbl, 6, "Nenhum colaborador ou visitante dentro da planta neste período")
        if self._campo_busca_nome.text(): self._filtrar_por_nome(self._campo_busca_nome.text())

    # ── Menu de contexto (botão direito) ────────────────────────────────────

    def _abrir_menu_contexto(self, pos):
        item = self._tbl_h.itemAt(pos)
        if not item: return
        row = item.row()
        it0 = self._tbl_h.item(row, 0)
        if not it0: return
        trabalhador_id = it0.data(Qt.UserRole)
        tipo = it0.data(Qt.UserRole + 1)
        nome = it0.text()
        # Menu de veículo só se aplica a colaboradores (visitantes não têm
        # vínculo de veículo por nome neste fluxo).
        if tipo == "visitante" or trabalhador_id is None:
            return

        veic = VeiculoRepo.buscar_dentro_por_motorista(nome)

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 6px 18px; border-radius: 4px; color: {COR_TEXTO_NORMAL}; font-size: 12px; }}
            QMenu::item:selected {{ background: {COR_AZUL_BG}; color: {COR_TITULO}; }}
            QMenu::separator {{ height: 1px; background: {COR_CARD_BORDA}; margin: 4px 8px; }}
        """)
        ac_detalhe = menu.addAction(qta.icon("fa5s.id-badge", color=COR_SB_ACENTO), "Ver detalhe do colaborador")
        menu.addSeparator()
        # Opções dinâmicas: se já existe veículo "Dentro" vinculado a este
        # nome, oferece dar saída nele; senão, oferece registrar a entrada.
        if veic:
            ac_veic = menu.addAction(qta.icon("fa5s.sign-out-alt", color=COR_AMARELO_TEXTO),
                                     f"Registrar saída do veículo ({veic.placa})")
        else:
            ac_veic = menu.addAction(qta.icon("fa5s.car", color=COR_CIANO), "Registrar entrada de veículo")

        acao = menu.exec(self._tbl_h.viewport().mapToGlobal(pos))
        if acao is None:
            return
        if acao == ac_detalhe:
            ModalDetalheAlerta(trabalhador_id, nome, parent=self).exec()
        elif acao == ac_veic:
            if veic:
                if VeiculoRepo.registrar_saida(veic.id):
                    QMessageBox.information(self, "Veículo", f"Saída do veículo {veic.placa} registrada.")
                else:
                    QMessageBox.critical(self, "Erro", "Não foi possível registrar a saída do veículo.")
            else:
                self._registrar_entrada_veiculo(trabalhador_id, nome)
            for p in ("h", "s", "m"): self._carregar(p)

    def _registrar_entrada_veiculo(self, trabalhador_id, nome):
        emp_nome = ""
        s = _get_session()
        if s:
            try:
                from app.models.trabalhador import Trabalhador
                t = s.get(Trabalhador, trabalhador_id)
                if t and t.empresa: emp_nome = t.empresa.razao_social
            except Exception:
                pass
            finally:
                s.close()
        dto = VeiculoDTO(motorista=nome, empresa=emp_nome)
        modal = ModalVeiculo(dto=dto, parent=self)
        modal._is_new = True
        modal.exec()


class JanelaVencimentos(JanelaDetalhe):
    def __init__(self, parent=None):
        super().__init__("Vencimentos Críticos", "Documentos vencidos ou próximos do vencimento",
                         "fa5s.exclamation-triangle", COR_AMARELO_TEXTO, COR_AMARELO_TEXTO, parent)

    def _popular_dados(self):
        self._lv_venc = self._add_card_resumo("fa5s.times-circle",       COR_VERMELHO_TEXTO, "Já vencidos")
        self._lv_7    = self._add_card_resumo("fa5s.exclamation-circle", COR_AMARELO_TEXTO,  "Vencem em 7 dias")
        self._lv_30   = self._add_card_resumo("fa5s.clock",              COR_SB_ACENTO,      "Vencem em 30 dias")
        cols = ["Colaborador", "Empresa", "Documento", "Vencimento", "Status"]
        for tab, attr in [(self._tab_hoje, "_tbl_v"), (self._tab_semana, "_tbl_7"), (self._tab_mes, "_tbl_30")]:
            lay = QVBoxLayout(tab); lay.setContentsMargins(0, 0, 0, 0)
            setattr(self, attr, self._criar_tabela(cols, lay))
        self._tabs.setTabText(0, "  Já Vencidos  "); self._tabs.setTabText(1, "  Vence em 7 dias  "); self._tabs.setTabText(2, "  Vence em 30 dias  ")
        self._carregar_vencimentos()

    def _carregar_vencimentos(self):
        hoje = date.today(); dados_trab = []
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            from app.models.treinamento import Treinamento
            session = get_session()
            nr01_rows = session.query(Treinamento).filter(Treinamento.nr_nome == NR01_NOME_BANCO).all()
            nr01_map  = {tr.trabalhador_id: tr for tr in nr01_rows}
            for t in session.query(Trabalhador).filter_by(ativo=True).all():
                emp = t.empresa; nr01 = nr01_map.get(t.id)
                dados_trab.append({"nome": t.nome, "emp": emp.razao_social if emp else "—",
                                   "aso": t.aso_validade, "nr01": nr01.data_validade if nr01 else None,
                                   "pgr": getattr(emp, "pgr_validade", None) if emp else None,
                                   "pcmso": getattr(emp, "pcmso_validade", None) if emp else None,
                                   "tem_empresa": bool(emp)})
            session.close()
        except Exception: pass
        def _status(venc):
            if not venc: return "Sem data", QColor("#F4F7FA")
            delta = (venc - hoje).days
            if delta < 0:    return f"Vencido há {-delta}d", QColor("#FFF0F0")
            elif delta <= 7: return f"Vence em {delta}d",    QColor("#FFFBEB")
            else:            return f"Vence em {delta}d",    QColor("#F0F7FF")
        lv, l7, l30 = [], [], []
        for d in dados_trab:
            docs = [("ASO", d["aso"]), ("Integração (NR-01)", d["nr01"])]
            if d["tem_empresa"]: docs += [("PGR", d["pgr"]), ("PCMSO", d["pcmso"])]
            for doc_nome, venc in docs:
                if not venc: continue
                delta = (venc - hoje).days; st, cor = _status(venc)
                linha = (d["nome"], d["emp"], doc_nome, venc.strftime("%d/%m/%Y"), st, cor)
                if delta < 0:     lv.append(linha)
                elif delta <= 7:  l7.append(linha)
                elif delta <= 30: l30.append(linha)
        def _fill(tbl, linhas):
            tbl.setRowCount(len(linhas))
            for row, (nome, emp, doc, venc_s, st, cor) in enumerate(linhas):
                tbl.setItem(row, 0, self._item(nome)); tbl.setItem(row, 1, self._item(emp))
                tbl.setItem(row, 2, self._item(doc, Qt.AlignCenter | Qt.AlignVCenter))
                tbl.setItem(row, 3, self._item(venc_s, Qt.AlignCenter | Qt.AlignVCenter))
                tbl.setItem(row, 4, self._item(st, Qt.AlignCenter | Qt.AlignVCenter))
                for col in range(5):
                    if tbl.item(row, col): tbl.item(row, col).setBackground(cor)
            if not linhas: self._linha_vazia(tbl, 5, "Nenhum documento nesta faixa")
        _fill(self._tbl_v, lv); _fill(self._tbl_7, l7); _fill(self._tbl_30, l30)
        self._lv_venc.setText(str(len(lv))); self._lv_7.setText(str(len(l7))); self._lv_30.setText(str(len(l30)))
        if self._campo_busca_nome.text(): self._filtrar_por_nome(self._campo_busca_nome.text())


class StatusBadge(QLabel):
    def __init__(self, texto, ok, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter); self.setFixedHeight(22); self.setMinimumWidth(100)
        self.atualizar(texto, ok)

    def atualizar(self, texto, ok):
        self.setText(texto)
        if ok:
            self.setStyleSheet(f"background-color: {COR_VERDE_BG}; color: {COR_VERDE_TEXTO}; border: 1px solid {COR_VERDE_BORDA}; border-radius: 3px; padding: 0px 8px; font-size: 11px; font-weight: bold;")
        else:
            self.setStyleSheet(f"background-color: {COR_VERMELHO_BG}; color: {COR_VERMELHO_TEXTO}; border: 1px solid {COR_VERMELHO_BORDA}; border-radius: 3px; padding: 0px 8px; font-size: 11px; font-weight: bold;")


class CardContador(QFrame):
    clicado = Signal()

    def __init__(self, icone, cor_icone, titulo, valor, cor_valor, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background-color: transparent; border: 1px solid {COR_SB_BORDA}; border-radius: 4px; }}
            QFrame:hover {{ background-color: #243447; border-color: {cor_valor}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(10, 8, 10, 8); lay.setSpacing(10)
        ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor_icone).pixmap(16, 16)); ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, alignment=Qt.AlignVCenter)
        vl = QVBoxLayout(); vl.setSpacing(0); vl.setContentsMargins(0, 0, 0, 0)
        self._lv = QLabel(valor); self._lv.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {cor_valor}; background: transparent; border: none;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 10px; color: {COR_SB_SUBTEXTO}; background: transparent; border: none;")
        vl.addWidget(self._lv); vl.addWidget(lt); lay.addLayout(vl); lay.addStretch()
        arr = QLabel(); arr.setPixmap(qta.icon("fa5s.chevron-right", color="#3A5570").pixmap(9, 9)); arr.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(arr, alignment=Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicado.emit()
        super().mousePressEvent(event)

    def set_valor(self, v): self._lv.setText(v)


class CardContadorVeiculo(QFrame):
    clicado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background-color: transparent; border: 1px solid {COR_SB_BORDA}; border-radius: 4px; }}
            QFrame:hover {{ background-color: #243447; border-color: {COR_CIANO}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(10, 8, 10, 8); lay.setSpacing(10)
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.car", color=COR_CIANO).pixmap(16, 16)); ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, alignment=Qt.AlignVCenter)
        vl = QVBoxLayout(); vl.setSpacing(0); vl.setContentsMargins(0, 0, 0, 0)
        self._lv = QLabel("0"); self._lv.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_CIANO}; background: transparent; border: none;")
        lt = QLabel("Veículos na unidade"); lt.setStyleSheet(f"font-size: 10px; color: {COR_SB_SUBTEXTO}; background: transparent; border: none;")
        vl.addWidget(self._lv); vl.addWidget(lt); lay.addLayout(vl); lay.addStretch()
        arr = QLabel(); arr.setPixmap(qta.icon("fa5s.chevron-right", color="#3A5570").pixmap(9, 9)); arr.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(arr, alignment=Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicado.emit()
        super().mousePressEvent(event)

    def set_valor(self, v: str): self._lv.setText(v)


class CardContadorVisitante(QFrame):
    """Espelha CardContadorVeiculo, com a cor própria de visitantes (roxo)."""
    clicado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background-color: transparent; border: 1px solid {COR_SB_BORDA}; border-radius: 4px; }}
            QFrame:hover {{ background-color: #243447; border-color: {COR_VISITANTE}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(10, 8, 10, 8); lay.setSpacing(10)
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.user-tie", color=COR_VISITANTE).pixmap(16, 16)); ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic, alignment=Qt.AlignVCenter)
        vl = QVBoxLayout(); vl.setSpacing(0); vl.setContentsMargins(0, 0, 0, 0)
        self._lv = QLabel("0"); self._lv.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_VISITANTE}; background: transparent; border: none;")
        lt = QLabel("Visitantes na unidade"); lt.setStyleSheet(f"font-size: 10px; color: {COR_SB_SUBTEXTO}; background: transparent; border: none;")
        vl.addWidget(self._lv); vl.addWidget(lt); lay.addLayout(vl); lay.addStretch()
        arr = QLabel(); arr.setPixmap(qta.icon("fa5s.chevron-right", color="#3A5570").pixmap(9, 9)); arr.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(arr, alignment=Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicado.emit()
        super().mousePressEvent(event)

    def set_valor(self, v: str): self._lv.setText(v)


class ItemAlerta(QFrame):
    clicado = Signal()

    def __init__(self, texto, nivel="warning", parent=None, clicavel=False):
        super().__init__(parent)
        self._clicavel = clicavel
        cores = {"warning": (COR_AMARELO_TEXTO, COR_AMARELO_BG, COR_AMARELO_BORDA, "#FFF3D6"),
                 "danger":  (COR_VERMELHO_TEXTO, COR_VERMELHO_BG, COR_VERMELHO_BORDA, "#FDE2E2"),
                 "info":    (COR_AZUL_TEXTO, COR_AZUL_BG, COR_AZUL_BORDA, "#DCEBFF")}
        txt, bg, brd, bg_hover = cores.get(nivel, cores["warning"])
        # CORREÇÃO: "filter" não é uma propriedade válida em Qt Style Sheets
        # (gerava spam de "Unknown property filter" no console). Hover válido
        # via mudança de background-color.
        hover_css = f"QFrame:hover {{ background-color: {bg_hover}; }}" if clicavel else ""
        self.setStyleSheet(f"QFrame {{ background-color: {bg}; border-left: 3px solid {brd}; border-top: 1px solid {brd}; border-right: 1px solid {brd}; border-bottom: 1px solid {brd}; border-radius: 3px; }} QLabel {{ border: none; background: transparent; }} {hover_css}")
        if clicavel:
            self.setCursor(Qt.PointingHandCursor)
            self.setToolTip("Clique para ver o detalhe deste registro")
        lay = QHBoxLayout(self); lay.setContentsMargins(8, 6, 8, 6); lay.setSpacing(8)
        ic_map = {"warning": "fa5s.exclamation-triangle", "danger": "fa5s.times-circle", "info": "fa5s.info-circle"}
        ic = QLabel(); ic.setPixmap(qta.icon(ic_map[nivel], color=txt).pixmap(12, 12)); ic.setStyleSheet("background: transparent; border: none;")
        lbl = QLabel(texto); lbl.setWordWrap(True); lbl.setStyleSheet(f"color: {txt}; font-size: 11px; background: transparent; border: none;")
        lay.addWidget(ic, alignment=Qt.AlignTop); lay.addWidget(lbl, 1)
        if clicavel:
            seta = QLabel(); seta.setPixmap(qta.icon("fa5s.chevron-right", color=txt).pixmap(8, 8)); seta.setStyleSheet("background: transparent; border: none;")
            lay.addWidget(seta, alignment=Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if self._clicavel and event.button() == Qt.LeftButton:
            self.clicado.emit()
        super().mousePressEvent(event)


class ModalDetalheAlerta(QDialog):
    """
    Pequeno relatório de movimentação do colaborador, aberto ao clicar em um
    item da lista "Alertas Recentes" da portaria. Mostra entrada/saída de
    hoje, o veículo vinculado (caso o colaborador tenha entrado com um
    veículo cujo motorista bata com o nome dele) e, se a empresa do
    colaborador for do tipo "flutuante" (prestador eventual), a descrição
    do serviço/atividade registrada para ele hoje.
    """

    def __init__(self, trabalhador_id: int = None, nome_fallback: str = "", parent=None, tipo_evento: str = "movimento"):
        super().__init__(parent)
        self._trabalhador_id = trabalhador_id
        self._nome_fallback = nome_fallback
        # CORREÇÃO: antes este modal sempre mostrava o relatório de
        # "Movimentação Hoje" (entrada/saída), mesmo quando o alerta clicado
        # era de um BLOQUEIO — dando a impressão de que o colaborador tinha
        # sido liberado. Agora, para bloqueios, mostramos um relatório
        # próprio com o(s) motivo(s) do bloqueio em vez da movimentação.
        self._tipo_evento = tipo_evento  # "movimento" (entrada/saída/sesmt) ou "bloqueio"
        eh_bloqueio = self._tipo_evento == "bloqueio"
        self.setWindowTitle("Detalhe do Bloqueio" if eh_bloqueio else "Detalhe do Registro")
        self.setFixedSize(440, 560); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._build_ui()
        self._carregar()

    def _build_ui(self):
        eh_bloqueio = self._tipo_evento == "bloqueio"
        lay = QVBoxLayout(self); lay.setContentsMargins(26, 22, 26, 22); lay.setSpacing(14)
        topo = QHBoxLayout()
        ic_nome = "fa5s.ban" if eh_bloqueio else "fa5s.id-badge"
        ic_cor  = COR_VERMELHO_TEXTO if eh_bloqueio else COR_SB_ACENTO
        ic = QLabel(); ic.setPixmap(qta.icon(ic_nome, color=ic_cor).pixmap(22, 22))
        vl = QVBoxLayout(); vl.setSpacing(2)
        self._lbl_nome = QLabel("—"); self._lbl_nome.setWordWrap(True)
        self._lbl_nome.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COR_TITULO};")
        self._lbl_emp = QLabel("—"); self._lbl_emp.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(self._lbl_nome); vl.addWidget(self._lbl_emp)
        topo.addWidget(ic); topo.addLayout(vl); topo.addStretch()
        if eh_bloqueio:
            badge = QLabel("  Acesso Bloqueado")
            badge.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COR_VERMELHO_TEXTO};"
                                f" background: {COR_VERMELHO_BG}; border: 1px solid {COR_VERMELHO_BORDA};"
                                f" border-radius: 10px; padding: 4px 10px;")
            topo.addWidget(badge, alignment=Qt.AlignVCenter)
        lay.addLayout(topo); lay.addWidget(_sep())

        # ── Bloqueio: motivo(s), justificativa, operador, horário ───────────
        self._frame_bloqueio = _card(COR_VERMELHO_TEXTO)
        mb = QVBoxLayout(self._frame_bloqueio); mb.setContentsMargins(14, 10, 14, 10); mb.setSpacing(6)
        mb.addWidget(_secao("MOTIVO DO BLOQUEIO"))
        self._lbl_motivos = QLabel("—"); self._lbl_motivos.setWordWrap(True)
        self._lbl_motivos.setStyleSheet(f"font-size: 12px; color: {COR_VERMELHO_TEXTO}; font-weight: bold;")
        mb.addWidget(self._lbl_motivos)
        self._lbl_bloq_horario = self._linha_dado(mb, "fa5s.clock", "Horário:", "—")
        self._lbl_bloq_operador = self._linha_dado(mb, "fa5s.user-shield", "Registrado por:", "—")
        self._lbl_bloq_justif = QLabel(""); self._lbl_bloq_justif.setWordWrap(True)
        self._lbl_bloq_justif.setStyleSheet(f"font-size: 11px; color: {COR_TEXTO_NORMAL}; font-style: italic;")
        mb.addWidget(self._lbl_bloq_justif)
        lay.addWidget(self._frame_bloqueio)
        self._frame_bloqueio.setVisible(eh_bloqueio)

        # ── Movimentação (entrada/saída) — apenas quando NÃO é bloqueio ─────
        self._secao_mov = _secao("MOVIMENTAÇÃO HOJE")
        lay.addWidget(self._secao_mov)
        self._card_mov = _card(); ml = QVBoxLayout(self._card_mov); ml.setContentsMargins(14, 10, 14, 10); ml.setSpacing(6)
        self._lbl_entrada = self._linha_dado(ml, "fa5s.sign-in-alt", "Entrada:", "—")
        self._lbl_saida   = self._linha_dado(ml, "fa5s.sign-out-alt", "Saída:", "—")
        self._lbl_funcao  = self._linha_dado(ml, "fa5s.id-card", "Função:", "—")
        lay.addWidget(self._card_mov)
        self._secao_mov.setVisible(not eh_bloqueio)
        self._card_mov.setVisible(not eh_bloqueio)

        self._frame_veic = _card(COR_CIANO)
        vlc = QVBoxLayout(self._frame_veic); vlc.setContentsMargins(14, 10, 14, 10); vlc.setSpacing(6)
        vlc.addWidget(_secao("VEÍCULO VINCULADO"))
        self._lbl_placa  = self._linha_dado(vlc, "fa5s.car", "Placa:", "—")
        self._lbl_veic_m = self._linha_dado(vlc, "fa5s.palette", "Modelo/Cor:", "—")
        self._lbl_veic_s = self._linha_dado(vlc, "fa5s.info-circle", "Status:", "—")
        lay.addWidget(self._frame_veic)
        self._frame_veic.setVisible(False)

        self._frame_serv = _card(COR_ROXO)
        vls = QVBoxLayout(self._frame_serv); vls.setContentsMargins(14, 10, 14, 10); vls.setSpacing(6)
        vls.addWidget(_secao("SERVIÇO (EMPRESA FLUTUANTE)"))
        self._lbl_servico = QLabel("—"); self._lbl_servico.setWordWrap(True)
        self._lbl_servico.setStyleSheet(f"font-size: 12px; color: {COR_TEXTO_NORMAL};")
        vls.addWidget(self._lbl_servico)
        lay.addWidget(self._frame_serv)
        self._frame_serv.setVisible(False)

        lay.addStretch()
        btn_f = _btn_primario("  Fechar", "fa5s.times", COR_SUBTITULO, COR_TITULO, 38)
        btn_f.clicked.connect(self.accept)
        lay.addWidget(btn_f)

    def _linha_dado(self, layout_pai, icone, rotulo, valor) -> QLabel:
        row = QHBoxLayout(); row.setSpacing(8)
        ic = QLabel(); ic.setPixmap(qta.icon(icone, color=COR_SECAO_LABEL).pixmap(11, 11))
        rl = QLabel(rotulo); rl.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        vl = QLabel(valor); vl.setStyleSheet(f"font-size: 12px; color: {COR_TITULO}; font-weight: bold;"); vl.setWordWrap(True)
        row.addWidget(ic); row.addWidget(rl); row.addStretch(); row.addWidget(vl)
        layout_pai.addLayout(row)
        return vl

    def _carregar(self):
        s = _get_session()
        if not s:
            self._lbl_nome.setText(self._nome_fallback or "Colaborador"); return
        try:
            from app.models.trabalhador import Trabalhador
            from app.models.acesso import Acesso
            trab = None
            if self._trabalhador_id is not None:
                trab = s.get(Trabalhador, self._trabalhador_id)
            if not trab:
                self._lbl_nome.setText(self._nome_fallback or "Colaborador não encontrado")
                return
            emp = trab.empresa
            self._lbl_nome.setText(trab.nome)
            self._lbl_emp.setText(emp.razao_social if emp else "—")
            hoje_inicio = datetime.combine(date.today(), datetime.min.time())

            if self._tipo_evento == "bloqueio":
                self._carregar_bloqueio(s, trab, hoje_inicio)
                return  # bloqueio não mostra movimentação/veículo/serviço

            self._lbl_funcao.setText(trab.funcao or "—")
            # CORREÇÃO: antes a "Saída" buscava qualquer registro de saída
            # de hoje (a última, por ordem decrescente) — então, se o
            # colaborador já tinha saído e entrado novamente antes hoje, o
            # relatório mostrava aquela saída antiga mesmo ele estando
            # dentro agora ("saída" preenchida sem ter saído de fato).
            # Agora: pega a ENTRADA mais recente (estado/permanência atual)
            # e só considera "saída" se ela ocorreu DEPOIS dessa entrada.
            entrada = (s.query(Acesso).filter(Acesso.trabalhador_id == trab.id, Acesso.tipo == "entrada",
                                               Acesso.horario >= hoje_inicio).order_by(Acesso.horario.desc()).first())
            saida = None
            if entrada and entrada.horario:
                saida = (s.query(Acesso).filter(Acesso.trabalhador_id == trab.id, Acesso.tipo == "saida",
                                                 Acesso.horario > entrada.horario).order_by(Acesso.horario.asc()).first())
            self._lbl_entrada.setText(entrada.horario.strftime("%d/%m/%Y %H:%M") if entrada and entrada.horario else "Não registrada")
            self._lbl_saida.setText(saida.horario.strftime("%d/%m/%Y %H:%M") if saida and saida.horario else "Ainda não saiu")

            # Veículo vinculado por nome (mesma lógica usada na saída automática)
            veic = VeiculoRepo.buscar_dentro_por_motorista(trab.nome)
            if not veic:
                # se já saiu, procura entre os de hoje (qualquer status)
                todos_hoje = VeiculoRepo.listar(hoje_inicio)
                nome_norm = _normalizar_nome(trab.nome)
                veic = next((v for v in todos_hoje if _normalizar_nome(v.motorista) == nome_norm), None)
            if veic:
                self._frame_veic.setVisible(True)
                self._lbl_placa.setText(veic.placa)
                mc = veic.modelo + (f" / {veic.cor}" if veic.cor else "")
                self._lbl_veic_m.setText(mc or "—")
                self._lbl_veic_s.setText(veic.status)

            # Descrição de serviço para empresas "flutuantes" (prestadores eventuais)
            if _empresa_eh_flutuante(emp):
                descricao = _buscar_descricao_servico_hoje(s, trab.id)
                self._frame_serv.setVisible(True)
                self._lbl_servico.setText(descricao or "Sem descrição de serviço registrada para hoje.")
        except Exception as e:
            print(f"[ModalDetalheAlerta._carregar] {e}")
        finally:
            s.close()

    def _carregar_bloqueio(self, s, trab, hoje_inicio):
        """Busca e exibe o bloqueio mais recente de hoje para este colaborador
        — motivos, horário, operador e justificativa — em vez do relatório
        de movimentação (entrada/saída), que não se aplica a um bloqueio."""
        try:
            from app.models.bloqueio import Bloqueio
            bloqueio = (s.query(Bloqueio)
                        .filter(Bloqueio.trabalhador_id == trab.id, Bloqueio.criado_em >= hoje_inicio)
                        .order_by(Bloqueio.criado_em.desc()).first())
            if not bloqueio:
                self._lbl_motivos.setText("Nenhum bloqueio encontrado para hoje.")
                return
            motivos = []
            if getattr(bloqueio, "doc_incompleta", False):      motivos.append("Documento inválido/incompleto")
            if getattr(bloqueio, "sem_epi", False):              motivos.append("Sem EPI")
            if getattr(bloqueio, "comportamento", False):        motivos.append("Comportamento")
            if getattr(bloqueio, "determinacao_gestao", False):  motivos.append("Bloqueio manual")
            if getattr(bloqueio, "outro", False):                motivos.append("Outro")
            if not motivos:
                motivos = [bloqueio.tipo or "Não especificado"]
            self._lbl_motivos.setText(" • ".join(motivos))
            self._lbl_bloq_horario.setText(bloqueio.criado_em.strftime("%d/%m/%Y %H:%M") if bloqueio.criado_em else "—")
            self._lbl_bloq_operador.setText(getattr(bloqueio, "registrado_por", None) or "portaria")
            justificativa = getattr(bloqueio, "justificativa", "") or ""
            self._lbl_bloq_justif.setText(f"Observação: {justificativa}" if justificativa else "")
        except Exception as e:
            print(f"[ModalDetalheAlerta._carregar_bloqueio] {e}")
            self._lbl_motivos.setText("Não foi possível carregar os detalhes do bloqueio.")


def _empresa_eh_flutuante(emp) -> bool:
    """
    Heurística para identificar empresas "flutuantes" (prestadores de
    serviço eventuais, sem vínculo fixo) — ajuste os nomes dos campos
    abaixo conforme o modelo Empresa real do projeto, caso sejam diferentes.
    """
    if not emp:
        return False
    for campo in ("flutuante", "is_flutuante", "eh_flutuante", "empresa_flutuante"):
        valor = getattr(emp, campo, None)
        if isinstance(valor, bool) and valor:
            return True
    tipo = getattr(emp, "tipo", None) or getattr(emp, "tipo_empresa", None) or getattr(emp, "categoria", None) or ""
    return "flutuante" in str(tipo).lower()


def _buscar_descricao_servico_hoje(session, trabalhador_id: int) -> str:
    """
    Busca a descrição da atividade/serviço de hoje vinculada ao
    colaborador. Tenta alguns formatos comuns de relacionamento entre
    Atividade e Trabalhador; ajuste conforme o modelo real do projeto se
    nenhum dos formatos abaixo corresponder.
    """
    try:
        from app.models.atividade import Atividade
        hoje_inicio = datetime.combine(date.today(), datetime.min.time())
        q = session.query(Atividade).filter(Atividade.data_inicio >= hoje_inicio)
        # Tentativa 1: relação direta trabalhador_id na própria Atividade
        if hasattr(Atividade, "trabalhador_id"):
            ativ = q.filter(Atividade.trabalhador_id == trabalhador_id).order_by(Atividade.data_inicio.desc()).first()
            if ativ:
                return getattr(ativ, "descricao", None) or getattr(ativ, "descricao_servico", None) or ""
        # Tentativa 2: relação muitos-para-muitos via atributo "trabalhadores"
        for ativ in q.order_by(Atividade.data_inicio.desc()).all():
            trabs = getattr(ativ, "trabalhadores", None)
            if trabs and any(getattr(t, "id", None) == trabalhador_id for t in trabs):
                return getattr(ativ, "descricao", None) or getattr(ativ, "descricao_servico", None) or ""
    except Exception as e:
        print(f"[_buscar_descricao_servico_hoje] {e}")
    return ""


class ModalBloqueio(QDialog):
    def __init__(self, trabalhador_id, nome, parent=None):
        super().__init__(parent)
        self.trabalhador_id = trabalhador_id; self.nome = nome
        self.setWindowTitle("Registrar Bloqueio"); self.setFixedSize(460, 430)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }}")
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(14)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.ban", color=COR_VERMELHO_TEXTO).pixmap(18, 18)); ic.setStyleSheet("background: transparent; border: none;")
        lt = QLabel("Registrar Bloqueio"); lt.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COR_TITULO}; background: transparent; border: none;")
        topo.addWidget(ic); topo.addWidget(lt); topo.addStretch(); lay.addLayout(topo)
        lbl_n = QLabel(f"Colaborador: {self.nome}"); lbl_n.setStyleSheet(f"font-size: 12px; color: {COR_TEXTO_NORMAL}; border: none; background: transparent;")
        lay.addWidget(lbl_n); lay.addWidget(_sep())
        lbl_m = QLabel("MOTIVO DO BLOQUEIO"); lbl_m.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1px; border: none; background: transparent;")
        lay.addWidget(lbl_m)
        fm = QFrame(); fm.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }} QLabel {{ border: none; background: transparent; }}")
        ml = QVBoxLayout(fm); ml.setContentsMargins(14, 10, 14, 10); ml.setSpacing(6)
        chk_st = f"QCheckBox {{ color: {COR_TEXTO_NORMAL}; font-size: 13px; background: transparent; border: none; }} QCheckBox::indicator {{ width: 15px; height: 15px; border: 1px solid {COR_CARD_BORDA}; border-radius: 2px; background: white; }} QCheckBox::indicator:checked {{ background-color: {COR_SB_ACENTO}; border-color: {COR_SB_ACENTO}; }}"
        self.chk_aso    = QCheckBox("ASO vencido");         self.chk_aso.setStyleSheet(chk_st)
        self.chk_integ  = QCheckBox("Integração vencida");  self.chk_integ.setStyleSheet(chk_st)
        self.chk_pgr    = QCheckBox("Empresa sem PGR");     self.chk_pgr.setStyleSheet(chk_st)
        self.chk_pcmso  = QCheckBox("Empresa sem PCMSO");   self.chk_pcmso.setStyleSheet(chk_st)
        self.chk_doc    = QCheckBox("Documento inválido");  self.chk_doc.setStyleSheet(chk_st)
        self.chk_manual = QCheckBox("Bloqueio manual");     self.chk_manual.setStyleSheet(chk_st)
        for c in [self.chk_aso, self.chk_integ, self.chk_pgr, self.chk_pcmso, self.chk_doc, self.chk_manual]: ml.addWidget(c)
        lay.addWidget(fm)
        lbl_o = QLabel("OBSERVAÇÃO (OPCIONAL)"); lbl_o.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1px; border: none; background: transparent;")
        lay.addWidget(lbl_o)
        self.campo_just = QTextEdit(); self.campo_just.setFixedHeight(68); self.campo_just.setPlaceholderText("Descreva o motivo...")
        self.campo_just.setStyleSheet(f"QTextEdit {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; padding: 6px; font-size: 12px; }} QTextEdit:focus {{ border-color: {COR_SB_ACENTO}; }}")
        lay.addWidget(self.campo_just)
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = QPushButton("Cancelar"); btn_c.setFixedHeight(38); btn_c.setCursor(Qt.PointingHandCursor)
        btn_c.setAutoDefault(False); btn_c.setDefault(False)
        btn_c.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; color: {COR_SUBTITULO}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; padding: 0 20px; font-size: 13px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("  Confirmar Bloqueio"); btn_ok.setIcon(qta.icon("fa5s.ban", color="white")); btn_ok.setIconSize(QSize(13, 13)); btn_ok.setFixedHeight(38); btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setAutoDefault(False); btn_ok.setDefault(False)
        btn_ok.setStyleSheet(f"QPushButton {{ background: {COR_VERMELHO_TEXTO}; color: white; border: none; border-radius: 4px; padding: 0 20px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ background: #7F1D1D; }}")
        btn_ok.clicked.connect(self._on_confirmar)
        btns.addWidget(btn_c); btns.addWidget(btn_ok); lay.addLayout(btns)

    def _on_confirmar(self):
        if not any([self.chk_aso.isChecked(), self.chk_integ.isChecked(), self.chk_pgr.isChecked(),
                    self.chk_pcmso.isChecked(), self.chk_doc.isChecked(), self.chk_manual.isChecked()]):
            QMessageBox.warning(self, "Atenção", "Selecione ao menos um motivo."); return
        try:
            from app.core.database import get_session
            from app.models.bloqueio import Bloqueio
            # CORREÇÃO: era sessao["username"] -> KeyError, pois a sessão
            # salva no login só tem usuario_id/email/token/cnpj. Use o
            # helper _get_operador(), que já trata isso com fallback.
            op = _get_operador()
            session = get_session()
            b = Bloqueio(trabalhador_id=self.trabalhador_id, tipo="manual", ativo=True,
                         doc_incompleta=self.chk_doc.isChecked(), sem_epi=False, comportamento=False,
                         determinacao_gestao=self.chk_manual.isChecked(), outro=False,
                         justificativa=self.campo_just.toPlainText().strip(), registrado_por=op)
            session.add(b); session.commit(); session.close()
        except Exception: pass
        self.accept()


class ModalEntradaRetroativa(QDialog):
    confirmado = Signal(datetime)

    def __init__(self, nome_colab: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entrada não registrada"); self.setFixedSize(420, 280); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COR_BG}; }} QLabel {{ border: none; background: transparent; color: {COR_TITULO}; }} QWidget {{ border: none; }}")
        self._setup_ui(nome_colab)

    def _setup_ui(self, nome_colab):
        from PySide6.QtCore import QTime
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 24); lay.setSpacing(16)
        topo = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.exclamation-triangle", color=COR_AMARELO_TEXTO).pixmap(22, 22))
        vl = QVBoxLayout(); vl.setSpacing(2)
        lt = QLabel("Entrada não registrada"); lt.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COR_TITULO};")
        ls = QLabel("Nenhuma entrada encontrada hoje para:"); ls.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        ln = QLabel(nome_colab); ln.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COR_SB_ACENTO};")
        vl.addWidget(lt); vl.addWidget(ls); vl.addWidget(ln)
        topo.addWidget(ic); topo.addLayout(vl); topo.addStretch()
        lay.addLayout(topo); lay.addWidget(_sep())
        lbl_h = QLabel("Informe o horário de entrada:"); lbl_h.setStyleSheet(f"font-size: 12px; color: {COR_TEXTO_NORMAL};")
        lay.addWidget(lbl_h)
        self._te = QTimeEdit(); self._te.setDisplayFormat("HH:mm"); self._te.setTime(QTime.currentTime()); self._te.setFixedHeight(40)
        self._te.setStyleSheet(f"QTimeEdit {{ background: white; color: {COR_TITULO}; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 4px 12px; font-size: 18px; font-weight: bold; }} QTimeEdit:focus {{ border-color: {COR_SB_ACENTO}; background: #EFF6FF; }}")
        lay.addWidget(self._te)
        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_c = QPushButton("  Cancelar"); btn_c.setFixedHeight(38); btn_c.setCursor(Qt.PointingHandCursor)
        btn_c.setIcon(qta.icon("fa5s.times", color=COR_SUBTITULO)); btn_c.setIconSize(QSize(11, 11))
        btn_c.setAutoDefault(False); btn_c.setDefault(False)
        btn_c.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; color: {COR_SUBTITULO}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; padding: 0 18px; font-size: 13px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("  Registrar e continuar"); btn_ok.setFixedHeight(38); btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setIcon(qta.icon("fa5s.check", color="white")); btn_ok.setIconSize(QSize(11, 11))
        btn_ok.setAutoDefault(False); btn_ok.setDefault(False)
        btn_ok.setStyleSheet(f"QPushButton {{ background: {COR_SB_ACENTO}; color: white; border: none; border-radius: 6px; padding: 0 18px; font-size: 13px; font-weight: bold; }} QPushButton:hover {{ background: #2E6BC4; }}")
        btn_ok.clicked.connect(self._on_confirmar)
        btns.addWidget(btn_c); btns.addWidget(btn_ok); lay.addLayout(btns)

    def _on_confirmar(self):
        t = self._te.time(); hoje = datetime.now().date()
        horario = datetime(hoje.year, hoje.month, hoje.day, t.hour(), t.minute())
        self.confirmado.emit(horario); self.accept()


# ══════════════════════════════════════════════════════════════════════════════
# PORTARIA PAGE — PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class PortariaPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._colab_atual = None; self._status_ok = False
        self.setWindowTitle("ThirdSys — Portaria / Controle de Acesso")
        # Qt.Window: janela independente (própria barra de título, própria
        # entrada na barra de tarefas), em vez de ficar "presa" dentro do
        # layout das outras páginas.
        # WindowMinimizeButtonHint / WindowMaximizeButtonHint: sem essas
        # duas flags, QDialog mostra só o botão de fechar — o usuário não
        # conseguia maximizar a janela manualmente, o que deixava a tela
        # pequena demais para a tabela de movimentação e causava a sensação
        # de "travar" ao usar com a janela no tamanho padrão.
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setMinimumSize(1180, 700)
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(min(1400, screen.width()-80), min(820, screen.height()-80))
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"background-color: {COR_BG}; QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }}")
        self._setup_ui(); self._iniciar_relogio(); self._carregar_dashboard()
        # Abre já maximizada — tela da portaria é usada o dia inteiro,
        # então faz sentido ocupar a tela toda por padrão. F11 alterna
        # para tela cheia de verdade (sem nem a barra de título).
        self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

    def _setup_ui(self):
        raiz = QHBoxLayout(self); raiz.setContentsMargins(0, 0, 0, 0); raiz.setSpacing(0)
        raiz.addWidget(self._build_sidebar())
        cont = QWidget(); cont.setStyleSheet("background: transparent; border: none;")
        cl = QVBoxLayout(cont); cl.setContentsMargins(32, 28, 32, 28); cl.setSpacing(20)
        cl.addLayout(self._build_header())
        cl.addWidget(self._build_busca())
        cl.addWidget(self._build_area_resultado(), 1)
        raiz.addWidget(cont, 1)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = QFrame(); sb.setFixedWidth(230)
        sb.setStyleSheet(f"QFrame {{ background-color: {COR_SB_BG}; border: none; border-right: 1px solid {COR_SB_BORDA}; }} QLabel {{ border: none; background: transparent; }} QWidget {{ border: none; }} QScrollArea {{ border: none; background: transparent; }}")
        lay = QVBoxLayout(sb); lay.setContentsMargins(16, 20, 16, 16); lay.setSpacing(10)
        # Logo
        lr = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.shield-alt", color=COR_SB_ACENTO).pixmap(18, 18)); ic.setStyleSheet("background: transparent; border: none;")
        lr.addWidget(ic)
        vl = QVBoxLayout(); vl.setSpacing(0)
        vl.addWidget(self._sb_lbl("Portaria", "#E8F0F8", 14, True))
        vl.addWidget(self._sb_lbl("Controle de Acesso", COR_SB_SUBTEXTO, 10, False))
        lr.addLayout(vl); lr.addStretch(); lay.addLayout(lr); lay.addWidget(_sep_sb())
        # Relógio
        self._lbl_rel = QLabel("00:00:00"); self._lbl_rel.setAlignment(Qt.AlignCenter)
        self._lbl_rel.setStyleSheet("font-size: 26px; font-weight: bold; color: #E8F0F8; background: transparent; border: none; letter-spacing: 2px;")
        lay.addWidget(self._lbl_rel)
        self._lbl_data = QLabel(datetime.now().strftime("%d/%m/%Y")); self._lbl_data.setAlignment(Qt.AlignCenter)
        self._lbl_data.setStyleSheet(f"font-size: 11px; color: {COR_SB_SUBTEXTO}; background: transparent; border: none;")
        lay.addWidget(self._lbl_data); lay.addSpacing(4); lay.addWidget(_sep_sb())
        # Cards colaboradores
        lay.addWidget(_secao_sb("HOJE — COLABORADORES"))
        self._card_lib  = CardContador("fa5s.user-check",          "#4CAF82",   "Liberados",            "0", "#4CAF82")
        self._card_blo  = CardContador("fa5s.user-slash",           "#E05252",   "Bloqueados",           "0", "#E05252")
        self._card_den  = CardContador("fa5s.building",             COR_SB_ACENTO,"Dentro da planta",    "0", COR_SB_ACENTO)
        self._card_ven  = CardContador("fa5s.exclamation-triangle", "#C0870A",   "Vencimentos críticos", "0", "#C0870A")
        self._card_ativ = CardContador("fa5s.hard-hat",             COR_ROXO,    "Atividades hoje",      "0", COR_ROXO)
        self._card_lib.clicado.connect(lambda: JanelaLiberados(self).exec())
        self._card_blo.clicado.connect(lambda: JanelaBloqueados(self).exec())
        self._card_den.clicado.connect(lambda: JanelaDentro(self).exec())
        self._card_ven.clicado.connect(lambda: JanelaVencimentos(self).exec())
        self._card_ativ.clicado.connect(self._abrir_atividades)
        for c in [self._card_lib, self._card_blo, self._card_den, self._card_ven, self._card_ativ]: lay.addWidget(c)
        # Card veículos
        lay.addSpacing(4); lay.addWidget(_sep_sb()); lay.addWidget(_secao_sb("VEÍCULOS"))
        self._card_veic = CardContadorVeiculo()
        self._card_veic.clicado.connect(self._abrir_veiculos)
        lay.addWidget(self._card_veic)
        # Card visitantes
        lay.addSpacing(4); lay.addWidget(_sep_sb()); lay.addWidget(_secao_sb("VISITANTES"))
        self._card_visit = CardContadorVisitante()
        self._card_visit.clicado.connect(self._abrir_visitantes)
        lay.addWidget(self._card_visit)
        # Alertas
        lay.addSpacing(4); lay.addWidget(_sep_sb()); lay.addWidget(_secao_sb("ALERTAS RECENTES"))
        self._scroll_al = QScrollArea(); self._scroll_al.setWidgetResizable(True)
        self._scroll_al.setStyleSheet("background: transparent; border: none;")
        self._scroll_al.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_al.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._cont_al = QWidget(); self._cont_al.setStyleSheet("background: transparent; border: none;")
        self._lay_al = QVBoxLayout(self._cont_al); self._lay_al.setSpacing(4); self._lay_al.setContentsMargins(0, 0, 0, 0); self._lay_al.addStretch()
        self._scroll_al.setWidget(self._cont_al)
        lay.addWidget(self._scroll_al, 1); lay.addWidget(_sep_sb())
        # Status online
        conn = QHBoxLayout(); conn.setContentsMargins(0, 4, 0, 0)
        dot = QLabel("●"); dot.setStyleSheet("color: #4CAF82; font-size: 10px; background: transparent; border: none;")
        lbl_c = QLabel("Sistema online"); lbl_c.setStyleSheet(f"color: {COR_SB_SUBTEXTO}; font-size: 10px; background: transparent; border: none;")
        conn.addWidget(dot); conn.addWidget(lbl_c); conn.addStretch(); lay.addLayout(conn)
        return sb

    def _sb_lbl(self, texto, cor, size, bold):
        l = QLabel(texto); l.setStyleSheet(f"color: {cor}; font-size: {size}px;{'font-weight: bold;' if bold else ''} background: transparent; border: none;"); return l

    def _abrir_atividades(self):
        try:
            from app.ui.pages.janela_atividades import JanelaAtividades
            JanelaAtividades(self).exec()
        except Exception: pass

    def _abrir_veiculos(self):
        PainelVeiculos(self).exec()
        self._atualizar_contadores()

    def _abrir_visitantes(self):
        PainelVisitantes(self).exec()
        self._atualizar_contadores()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = QHBoxLayout()
        vl = QVBoxLayout(); vl.setSpacing(3)
        lt = QLabel("Controle de Acesso"); lt.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COR_TITULO}; background: transparent; border: none;")
        ls = QLabel("Somente consulta e registro de movimentação"); ls.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO}; background: transparent; border: none;")
        vl.addWidget(lt); vl.addWidget(ls); hdr.addLayout(vl); hdr.addStretch()
        # CORREÇÃO: botão de tela cheia removido — a janela da portaria já
        # abre no tamanho fixo definido em __init__ (resize/move calculados
        # a partir da tela disponível) e não precisa de alternância de modo.
        return hdr

    # ── Busca ─────────────────────────────────────────────────────────────────

    def _build_busca(self):
        f = QFrame(); f.setFixedHeight(56)
        f.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; }} QLabel {{ border: none; background: transparent; }} QLineEdit {{ border: none; background: transparent; }}")
        lay = QHBoxLayout(f); lay.setContentsMargins(14, 0, 10, 0); lay.setSpacing(10)
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.search", color=COR_SB_SUBTEXTO).pixmap(15, 15)); ic.setStyleSheet("background: transparent; border: none;"); lay.addWidget(ic)
        self._campo_busca = QLineEdit(); self._campo_busca.setPlaceholderText("Pesquisar por nome, CPF, empresa ou crachá...")
        self._campo_busca.setStyleSheet(f"color: {COR_TITULO}; font-size: 13px;")
        self._campo_busca.returnPressed.connect(self._on_pesquisar); lay.addWidget(self._campo_busca, 1)
        sv = QFrame(); sv.setFrameShape(QFrame.VLine); sv.setFixedWidth(1); sv.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;"); lay.addWidget(sv)
        self._combo_tipo = QComboBox()
        for item in ["Nome", "CPF", "Empresa", "Crachá"]: self._combo_tipo.addItem(item)
        self._combo_tipo.setFixedHeight(32)
        self._combo_tipo.setStyleSheet(f"QComboBox {{ background: {COR_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; border-radius: 3px; padding: 0 8px; font-size: 12px; min-width: 80px; }} QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background: {COR_CARD_BG}; color: {COR_TEXTO_NORMAL}; border: 1px solid {COR_CARD_BORDA}; selection-background-color: {COR_AZUL_BG}; }}")
        lay.addWidget(self._combo_tipo)
        btn_b = QPushButton("  Pesquisar"); btn_b.setIcon(qta.icon("fa5s.search", color="white")); btn_b.setIconSize(QSize(12, 12)); btn_b.setFixedHeight(36); btn_b.setCursor(Qt.PointingHandCursor)
        btn_b.setStyleSheet(f"QPushButton {{ background: {COR_SB_ACENTO}; color: white; border: none; border-radius: 3px; padding: 0 18px; font-weight: bold; font-size: 12px; }} QPushButton:hover {{ background: #2E6BC4; }}")
        btn_b.clicked.connect(self._on_pesquisar); lay.addWidget(btn_b)
        btn_l = QPushButton(); btn_l.setIcon(qta.icon("fa5s.times", color=COR_SB_SUBTEXTO)); btn_l.setIconSize(QSize(12, 12)); btn_l.setFixedSize(36, 36); btn_l.setCursor(Qt.PointingHandCursor); btn_l.setToolTip("Limpar")
        btn_l.setAutoDefault(False); btn_l.setDefault(False)
        btn_l.setStyleSheet(f"QPushButton {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 3px; }} QPushButton:hover {{ background: #EBF0F6; }}")
        btn_l.clicked.connect(self._on_limpar); lay.addWidget(btn_l)
        return f

    # ── Área resultado ────────────────────────────────────────────────────────

    def _build_area_resultado(self):
        w = QWidget(); w.setStyleSheet("background: transparent; border: none;")
        h = QHBoxLayout(w); h.setSpacing(16); h.setContentsMargins(0, 0, 0, 0)
        col_e = QVBoxLayout(); col_e.setSpacing(14)
        col_e.addWidget(self._build_card_colab())
        col_e.addWidget(self._build_card_docs())
        col_e.addStretch()
        h.addLayout(col_e, 4)
        col_d = QVBoxLayout(); col_d.setSpacing(14)
        col_d.addWidget(self._build_card_resultado(), 1)
        col_d.addWidget(self._build_card_botoes())
        h.addLayout(col_d, 5)
        return w

    def _build_card_colab(self):
        card = _card(); lay = QVBoxLayout(card); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(12)
        lay.addWidget(_secao("COLABORADOR")); lay.addWidget(_sep())
        corpo = QHBoxLayout(); corpo.setSpacing(14)
        self._lbl_avatar = QLabel(); self._lbl_avatar.setFixedSize(56, 56); self._lbl_avatar.setAlignment(Qt.AlignCenter)
        self._lbl_avatar.setPixmap(qta.icon("fa5s.user-circle", color=COR_SB_SUBTEXTO).pixmap(40, 40))
        self._lbl_avatar.setStyleSheet(f"background-color: {COR_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 28px;")
        corpo.addWidget(self._lbl_avatar, alignment=Qt.AlignTop)
        dados = QVBoxLayout(); dados.setSpacing(3)
        self._lbl_nome   = QLabel("Nenhum colaborador selecionado"); self._lbl_nome.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COR_TEXTO_FRACO}; background: transparent; border: none;"); self._lbl_nome.setWordWrap(True)
        self._lbl_emp    = QLabel("—"); self._lbl_emp.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO}; background: transparent; border: none;")
        self._lbl_cargo  = QLabel("—"); self._lbl_cargo.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO}; background: transparent; border: none;")
        self._lbl_cpf    = QLabel("CPF: —"); self._lbl_cpf.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
        for w in [self._lbl_nome, self._lbl_emp, self._lbl_cargo, self._lbl_cpf]: dados.addWidget(w)
        dados.addStretch(); corpo.addLayout(dados, 1); lay.addLayout(corpo)
        rod = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.clock", color=COR_SECAO_LABEL).pixmap(11, 11)); ic.setStyleSheet("background: transparent; border: none;")
        self._lbl_ult = QLabel("Última entrada: —"); self._lbl_ult.setStyleSheet(f"font-size: 11px; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
        rod.addWidget(ic); rod.addWidget(self._lbl_ult); rod.addStretch(); lay.addLayout(rod)
        return card

    def _build_card_docs(self):
        card = _card(); lay = QVBoxLayout(card); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(10)
        lay.addWidget(_secao("STATUS DOCUMENTAL")); lay.addWidget(_sep())
        grid = QGridLayout(); grid.setSpacing(8); grid.setContentsMargins(0, 0, 0, 0)
        docs = [("Integração (NR-01)", "integracao"), ("ASO", "aso"), ("PGR Empresa", "pgr"), ("PCMSO Empresa", "pcmso")]
        self._badges = {}
        for i, (nome, chave) in enumerate(docs):
            lbl = QLabel(nome); lbl.setStyleSheet(f"font-size: 12px; color: {COR_TEXTO_NORMAL}; background: transparent; border: none;")
            badge = StatusBadge("—", True)
            grid.addWidget(lbl, i, 0); grid.addWidget(badge, i, 1, Qt.AlignRight)
            self._badges[chave] = badge
        lay.addLayout(grid); return card

    def _build_card_resultado(self):
        self._card_res = _card(); lay = QVBoxLayout(self._card_res); lay.setContentsMargins(28, 28, 28, 28); lay.setSpacing(10); lay.setAlignment(Qt.AlignCenter)
        self._res_ic = QLabel(); self._res_ic.setAlignment(Qt.AlignCenter); self._res_ic.setPixmap(qta.icon("fa5s.search", color=COR_SECAO_LABEL).pixmap(48, 48)); self._res_ic.setStyleSheet("background: transparent; border: none;")
        self._res_titulo = QLabel("AGUARDANDO PESQUISA"); self._res_titulo.setAlignment(Qt.AlignCenter); self._res_titulo.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
        self._res_sub = QLabel("Pesquise um colaborador para verificar o acesso"); self._res_sub.setAlignment(Qt.AlignCenter); self._res_sub.setWordWrap(True); self._res_sub.setStyleSheet(f"font-size: 12px; color: {COR_SUBTITULO}; background: transparent; border: none;")
        lay.addWidget(self._res_ic); lay.addWidget(self._res_titulo); lay.addWidget(self._res_sub)
        self._frame_mot = QFrame(); self._frame_mot.setStyleSheet(f"QFrame {{ background-color: {COR_VERMELHO_BG}; border: 1px solid {COR_VERMELHO_BORDA}; border-left: 4px solid {COR_VERMELHO_TEXTO}; border-radius: 3px; }} QLabel {{ border: none; background: transparent; }}"); self._frame_mot.setVisible(False)
        ml = QVBoxLayout(self._frame_mot); ml.setContentsMargins(14, 10, 14, 10); ml.setSpacing(4)
        self._mot_titulo = QLabel("Pendências encontradas:"); self._mot_titulo.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COR_VERMELHO_TEXTO}; background: transparent; border: none;")
        self._mot_lista  = QLabel(""); self._mot_lista.setWordWrap(True); self._mot_lista.setStyleSheet(f"font-size: 12px; color: {COR_VERMELHO_TEXTO}; background: transparent; border: none;")
        ml.addWidget(self._mot_titulo); ml.addWidget(self._mot_lista); lay.addWidget(self._frame_mot)
        return self._card_res

    def _build_card_botoes(self):
        card = QFrame(); card.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(card); lay.setSpacing(10); lay.setContentsMargins(0, 0, 0, 0)
        self._btn_lib  = self._btn_acao("fa5s.check",       "#166534", "#14532D", "  Liberar Entrada")
        self._btn_blo  = self._btn_acao("fa5s.ban",          "#991B1B", "#7F1D1D", "  Bloquear")
        self._btn_sai  = self._btn_acao("fa5s.sign-out-alt", "#1E40AF", "#1E3A8A", "  Registrar Saída")
        self._btn_ses  = self._btn_acao("fa5s.bell",         "#92400E", "#78350F", "  Notificar SESMT")
        self._btn_lib.clicked.connect(self._on_liberar); self._btn_blo.clicked.connect(self._on_bloquear)
        self._btn_sai.clicked.connect(self._on_registrar_saida); self._btn_ses.clicked.connect(self._on_notificar_sesmt)
        for btn in [self._btn_lib, self._btn_blo, self._btn_sai, self._btn_ses]:
            btn.setEnabled(False); lay.addWidget(btn)
        return card

    def _btn_acao(self, icone, bg, hover, texto):
        btn = QPushButton(texto); btn.setIcon(qta.icon(icone, color="white")); btn.setIconSize(QSize(13, 13)); btn.setFixedHeight(44); btn.setCursor(Qt.PointingHandCursor)
        btn.setAutoDefault(False); btn.setDefault(False)  # ver comentário em _btn_primario
        btn.setStyleSheet(f"QPushButton {{ background: {bg}; color: white; border: none; border-radius: 4px; font-weight: bold; font-size: 12px; padding: 0 14px; }} QPushButton:hover {{ background: {hover}; }} QPushButton:disabled {{ background: {COR_CARD_BORDA}; color: {COR_SECAO_LABEL}; }}")
        return btn

    # ── Lógica de pesquisa ────────────────────────────────────────────────────

    def _on_pesquisar(self):
        termo = self._campo_busca.text().strip()
        if not termo: return
        dados = self._buscar_no_banco(termo)
        if dados: self._exibir_colaborador(dados)
        else:     self._exibir_nao_encontrado()

    def _buscar_no_banco(self, termo):
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            from app.models.treinamento import Treinamento
            session = get_session(); tipo = self._combo_tipo.currentText()
            q = session.query(Trabalhador).filter_by(ativo=True)
            if tipo == "CPF":     q = q.filter(Trabalhador.cpf.contains(termo))
            elif tipo == "Empresa":
                from app.models.empresa import Empresa
                q = q.join(Empresa).filter(Empresa.razao_social.ilike(f"%{termo}%"))
            else: q = q.filter(Trabalhador.nome.ilike(f"%{termo}%"))
            t = q.first()
            if not t: session.close(); return None
            hoje = date.today(); emp = t.empresa
            nr01 = session.query(Treinamento).filter(Treinamento.trabalhador_id == t.id, Treinamento.nr_nome == NR01_NOME_BANCO).first()
            dados = {"id": t.id, "nome": t.nome, "empresa": emp.razao_social if emp else "—",
                     "funcao": t.funcao or "—", "cpf": t.cpf or "—",
                     "aso_ok":   bool(t.aso_validade and t.aso_validade >= hoje),
                     "integ_ok": bool(nr01 and nr01.data_validade and nr01.data_validade >= hoje),
                     "pgr_ok":   bool(emp and emp.pgr_validade and emp.pgr_validade >= hoje) if emp else False,
                     "pcmso_ok": bool(emp and emp.pcmso_validade and emp.pcmso_validade >= hoje) if emp else False}
            session.close(); return dados
        except Exception: return None

    def _exibir_colaborador(self, dados):
        self._colab_atual = dados
        self._lbl_nome.setText(dados["nome"]); self._lbl_nome.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COR_TITULO}; background: transparent; border: none;")
        self._lbl_emp.setText(dados["empresa"]); self._lbl_cargo.setText(dados["funcao"]); self._lbl_cpf.setText(f"CPF: {dados['cpf']}")
        _aplicar_foto_avatar(self._lbl_avatar, dados["empresa"], dados["nome"])
        self._badges["integracao"].atualizar("Válida"  if dados["integ_ok"] else "Vencida",  dados["integ_ok"])
        self._badges["aso"].atualizar(       "Válido"  if dados["aso_ok"]   else "Vencido",  dados["aso_ok"])
        self._badges["pgr"].atualizar(       "Válido"  if dados["pgr_ok"]   else "Vencido",  dados["pgr_ok"])
        self._badges["pcmso"].atualizar(     "Válido"  if dados["pcmso_ok"] else "Vencido",  dados["pcmso_ok"])
        motivos = []
        if not dados["aso_ok"]:   motivos.append("ASO vencido")
        if not dados["integ_ok"]: motivos.append("Integração (NR-01) vencida ou não cadastrada")
        if not dados["pgr_ok"]:   motivos.append("Empresa sem PGR válido")
        if not dados["pcmso_ok"]: motivos.append("Empresa sem PCMSO válido")
        self._status_ok = len(motivos) == 0
        if self._status_ok:
            self._res_ic.setPixmap(qta.icon("fa5s.check-circle", color=COR_VERDE_TEXTO).pixmap(52, 52))
            self._res_titulo.setText("ACESSO LIBERADO"); self._res_titulo.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COR_VERDE_TEXTO}; background: transparent; border: none;")
            self._res_sub.setText("Documentação em dia — entrada permitida"); self._frame_mot.setVisible(False)
            self._card_res.setStyleSheet(f"QFrame {{ background-color: {COR_VERDE_BG}; border: 1px solid {COR_VERDE_BORDA}; border-left: 4px solid {COR_VERDE_TEXTO}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        else:
            self._res_ic.setPixmap(qta.icon("fa5s.times-circle", color=COR_VERMELHO_TEXTO).pixmap(52, 52))
            self._res_titulo.setText("ACESSO NEGADO"); self._res_titulo.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COR_VERMELHO_TEXTO}; background: transparent; border: none;")
            self._res_sub.setText("Há pendências que impedem a entrada")
            self._mot_lista.setText("\n".join(f"• {m}" for m in motivos)); self._frame_mot.setVisible(True)
            self._card_res.setStyleSheet(f"QFrame {{ background-color: {COR_VERMELHO_BG}; border: 1px solid {COR_VERMELHO_BORDA}; border-left: 4px solid {COR_VERMELHO_TEXTO}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        for btn in [self._btn_lib, self._btn_blo, self._btn_sai, self._btn_ses]: btn.setEnabled(True)

    def _exibir_nao_encontrado(self):
        self._colab_atual = None
        self._lbl_nome.setText("Colaborador não encontrado"); self._lbl_nome.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COR_TEXTO_FRACO}; background: transparent; border: none;")
        self._lbl_avatar.setPixmap(qta.icon("fa5s.user-circle", color=COR_SB_SUBTEXTO).pixmap(40, 40))
        self._lbl_avatar.setStyleSheet(f"background-color: {COR_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 28px;")
        self._res_ic.setPixmap(qta.icon("fa5s.user-slash", color=COR_SECAO_LABEL).pixmap(48, 48))
        self._res_titulo.setText("NÃO ENCONTRADO"); self._res_titulo.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
        self._res_sub.setText("Nenhum colaborador ativo localizado com esse critério"); self._frame_mot.setVisible(False)
        self._card_res.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        for btn in [self._btn_lib, self._btn_blo, self._btn_sai, self._btn_ses]: btn.setEnabled(False)

    def _on_limpar(self):
        self._campo_busca.clear(); self._colab_atual = None
        self._lbl_nome.setText("Nenhum colaborador selecionado"); self._lbl_nome.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COR_TEXTO_FRACO}; background: transparent; border: none;")
        self._lbl_emp.setText("—"); self._lbl_cargo.setText("—"); self._lbl_cpf.setText("CPF: —"); self._lbl_ult.setText("Última entrada: —")
        self._lbl_avatar.setPixmap(qta.icon("fa5s.user-circle", color=COR_SB_SUBTEXTO).pixmap(40, 40))
        self._lbl_avatar.setStyleSheet(f"background-color: {COR_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 28px;")
        for chave in self._badges: self._badges[chave].atualizar("—", True)
        self._res_ic.setPixmap(qta.icon("fa5s.search", color=COR_SECAO_LABEL).pixmap(48, 48))
        self._res_titulo.setText("AGUARDANDO PESQUISA"); self._res_titulo.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COR_SECAO_LABEL}; background: transparent; border: none;")
        self._res_sub.setText("Pesquise um colaborador para verificar o acesso"); self._frame_mot.setVisible(False)
        self._card_res.setStyleSheet(f"QFrame {{ background-color: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 6px; }} QLabel {{ border: none; background: transparent; }}")
        for btn in [self._btn_lib, self._btn_blo, self._btn_sai, self._btn_ses]: btn.setEnabled(False)

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _on_liberar(self):
        if not self._colab_atual: return
        try:
            from app.ui.pages.modal_registro_atividade import ModalRegistroAtividade
            modal = ModalRegistroAtividade(self._colab_atual, parent=self)
            modal.confirmado.connect(self._on_atividade_confirmada); modal.exec()
        except Exception:
            if self._registrar_acesso("entrada"):
                self._adicionar_alerta(f"Entrada: {self._colab_atual['nome']} — {datetime.now().strftime('%H:%M')}", "info",
                                       trabalhador_id=self._colab_atual["id"], nome=self._colab_atual["nome"])
                self._lbl_ult.setText(f"Última entrada: {datetime.now().strftime('%H:%M:%S')}")
                self._atualizar_contadores()

    def _on_atividade_confirmada(self, ids: list, descricao: str):
        erros = []
        for tid in ids:
            if not self._registrar_acesso_por_id(tid): erros.append(tid)
        nome = self._colab_atual["nome"]; n_extra = len(ids) - 1
        msg = f"Entrada: {nome}" + (f" + {n_extra} pessoa(s)" if n_extra > 0 else "") + f" — {datetime.now().strftime('%H:%M')}"
        self._adicionar_alerta(msg, "info", trabalhador_id=self._colab_atual["id"], nome=nome)
        if erros: QMessageBox.warning(self, "Atenção", f"Não foi possível registrar {len(erros)} colaborador(es).")
        self._lbl_ult.setText(f"Última entrada: {datetime.now().strftime('%H:%M:%S')}")
        self._atualizar_contadores()

    def _registrar_acesso_por_id(self, tid: int) -> bool:
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            # CORREÇÃO: era carregar_sessao(); sessao["username"] -> KeyError
            # ('username' não existe na sessão). Usar _get_operador().
            op = _get_operador()
            session = get_session()
            session.add(Acesso(trabalhador_id=tid, tipo="entrada", horario=datetime.now(), operador=op))
            session.commit(); session.close(); return True
        except Exception as e: print(f"[ERRO _registrar_acesso_por_id] {e}"); return False

    def _on_bloquear(self):
        if not self._colab_atual: return
        modal = ModalBloqueio(self._colab_atual["id"], self._colab_atual["nome"], parent=self)
        if modal.exec() == QDialog.Accepted:
            self._adicionar_alerta(f"Bloqueio: {self._colab_atual['nome']} — {datetime.now().strftime('%H:%M')}", "danger",
                                   trabalhador_id=self._colab_atual["id"], nome=self._colab_atual["nome"], tipo_evento="bloqueio")
            self._atualizar_contadores(); self._exibir_colaborador(self._colab_atual)

    def _on_registrar_saida(self):
        if not self._colab_atual: return
        situacao = self._verificar_situacao_hoje(self._colab_atual["id"])
        # CORREÇÃO: antes só se checava "existe entrada hoje?" (booleano),
        # então clicar em "Registrar Saída" de alguém que JÁ tinha saído
        # registrava outra saída duplicada, silenciosamente, sem aviso.
        # Agora distinguimos 3 situações: "dentro" (pode dar saída normal),
        # "fora" (já saiu — erro, não permite repetir) e "sem_registro"
        # (sem nenhum acesso hoje — pergunta se quer registrar entrada
        # retroativa antes de dar saída).
        if situacao == "fora":
            QMessageBox.critical(self, "Saída já registrada",
                f"<b>{self._colab_atual['nome']}</b> já registrou saída hoje e não se encontra "
                "dentro da planta.<br><br>Não é possível registrar a saída novamente.")
            return
        if situacao == "sem_registro":
            r = QMessageBox.warning(self, "Entrada não registrada",
                f"<b>{self._colab_atual['nome']}</b> não possui entrada registrada hoje.<br><br>"
                "Deseja registrar o horário de entrada manualmente antes de continuar?",
                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
            if r == QMessageBox.Cancel: return
            modal = ModalEntradaRetroativa(self._colab_atual["nome"], parent=self)
            modal.confirmado.connect(self._registrar_entrada_e_saida); modal.exec(); return
        self._finalizar_saida()

    def _verificar_entrada_hoje(self, tid: int) -> bool:
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            inicio = datetime.combine(date.today(), datetime.min.time())
            session = get_session()
            existe = session.query(Acesso).filter(Acesso.trabalhador_id == tid, Acesso.tipo == "entrada", Acesso.horario >= inicio).first()
            session.close(); return existe is not None
        except Exception: return False

    def _verificar_situacao_hoje(self, tid: int) -> str:
        """
        Retorna a situação do colaborador hoje, com base no último acesso
        registrado: 'dentro' (último acesso foi entrada — está na planta),
        'fora' (último acesso foi saída — já deixou a planta) ou
        'sem_registro' (nenhum acesso hoje).
        """
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            inicio = datetime.combine(date.today(), datetime.min.time())
            session = get_session()
            ultimo = (session.query(Acesso)
                      .filter(Acesso.trabalhador_id == tid, Acesso.horario >= inicio)
                      .order_by(Acesso.horario.desc()).first())
            session.close()
            if not ultimo: return "sem_registro"
            return "dentro" if ultimo.tipo == "entrada" else "fora"
        except Exception:
            return "sem_registro"

    def _registrar_entrada_e_saida(self, horario_entrada: datetime):
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            # CORREÇÃO: era carregar_sessao(); sessao["username"] -> KeyError.
            op = _get_operador()
            session = get_session()
            session.add(Acesso(trabalhador_id=self._colab_atual["id"], tipo="entrada", horario=horario_entrada, operador=op))
            session.add(Acesso(trabalhador_id=self._colab_atual["id"], tipo="saida",   horario=datetime.now(),  operador=op))
            session.commit(); session.close()
            # Vínculo automático: se este colaborador também tem um veículo
            # "Dentro" com motorista correspondente, registra a saída dele também.
            veic_saida = _registrar_saida_veiculo_por_motorista(self._colab_atual["nome"])
            msg = f"Entrada retroativa + saída: {self._colab_atual['nome']} — {datetime.now().strftime('%H:%M')}"
            if veic_saida: msg += " (+ veículo)"
            self._adicionar_alerta(msg, "warning", trabalhador_id=self._colab_atual["id"], nome=self._colab_atual["nome"])
            self._atualizar_contadores()
        except Exception as e: QMessageBox.critical(self, "Erro", f"Não foi possível registrar:\n{e}")

    def _finalizar_saida(self):
        if self._registrar_acesso("saida"):
            nome = self._colab_atual["nome"]
            # Vínculo automático: se este colaborador também tem um veículo
            # "Dentro" com motorista correspondente (entrou com os dois),
            # registra a saída do veículo automaticamente também.
            veic_saida = _registrar_saida_veiculo_por_motorista(nome)
            msg = f"Saída: {nome} — {datetime.now().strftime('%H:%M')}"
            if veic_saida: msg += " (+ veículo)"
            self._adicionar_alerta(msg, "info", trabalhador_id=self._colab_atual["id"], nome=nome)
            self._atualizar_contadores()
        else: QMessageBox.critical(self, "Erro", "Não foi possível registrar a saída no banco de dados.")

    def _on_notificar_sesmt(self):
        if not self._colab_atual: return
        nome = self._colab_atual["nome"]
        QMessageBox.information(self, "SESMT Notificado", f"Notificação enviada ao SESMT sobre {nome}.\nHorário: {datetime.now().strftime('%H:%M:%S')}")
        self._adicionar_alerta(f"SESMT notificado: {nome}", "warning", trabalhador_id=self._colab_atual["id"], nome=nome)

    def _registrar_acesso(self, tipo):
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            # CORREÇÃO: era carregar_sessao(); sessao["username"] -> KeyError.
            op = _get_operador()
            session = get_session()
            session.add(Acesso(trabalhador_id=self._colab_atual["id"], tipo=tipo, horario=datetime.now(), operador=op))
            session.commit(); session.close(); return True
        except Exception as e: print(f"[ERRO _registrar_acesso] {e}"); return False

    def _adicionar_alerta(self, texto, nivel="warning", trabalhador_id=None, nome=None, tipo_evento="movimento"):
        clicavel = trabalhador_id is not None
        item = ItemAlerta(texto, nivel, clicavel=clicavel)
        if clicavel:
            item.clicado.connect(lambda tid=trabalhador_id, nm=nome, te=tipo_evento: self._abrir_detalhe_alerta(tid, nm, te))
        count = self._lay_al.count()
        self._lay_al.insertWidget(count - 1, item)
        if self._lay_al.count() > 12:
            w = self._lay_al.itemAt(0).widget()
            if w: w.deleteLater()

    def _abrir_detalhe_alerta(self, trabalhador_id, nome, tipo_evento="movimento"):
        ModalDetalheAlerta(trabalhador_id, nome, parent=self, tipo_evento=tipo_evento).exec()

    # ── Contadores ────────────────────────────────────────────────────────────

    def _atualizar_contadores(self):
        try:
            from app.core.database import get_session
            from app.models.acesso import Acesso
            from app.models.bloqueio import Bloqueio
            from app.models.trabalhador import Trabalhador
            from app.models.treinamento import Treinamento
            from app.models.atividade import Atividade
            from sqlalchemy import func
            session = get_session(); hoje = date.today()
            ini = datetime.combine(hoje, datetime.min.time())
            lib  = session.query(Acesso).filter(Acesso.tipo == "entrada", Acesso.horario >= ini).count()
            blo  = session.query(Bloqueio).filter(Bloqueio.criado_em >= ini).count()
            subq = (session.query(Acesso.trabalhador_id, func.max(Acesso.horario).label("ultima"))
                    .filter(Acesso.horario >= ini).group_by(Acesso.trabalhador_id).subquery())
            den  = (session.query(Acesso)
                    .join(subq, (Acesso.trabalhador_id == subq.c.trabalhador_id) & (Acesso.horario == subq.c.ultima))
                    .filter(Acesso.tipo == "entrada").count())
            aso_v = session.query(Trabalhador).filter(Trabalhador.ativo == True, Trabalhador.aso_validade < hoje).count()
            nr_v  = session.query(Treinamento).filter(Treinamento.nr_nome == NR01_NOME_BANCO, Treinamento.data_validade < hoje).count()
            crit  = aso_v + nr_v
            ativ  = session.query(Atividade).filter(Atividade.data_inicio >= ini, Atividade.encerrada == False).count()
            session.close()
            self._card_lib.set_valor(str(lib)); self._card_blo.set_valor(str(blo))
            self._card_den.set_valor(str(den)); self._card_ven.set_valor(str(crit))
            self._card_ativ.set_valor(str(ativ))
            # ── Veículos ──────────────────────────────────────────────────────
            self._card_veic.set_valor(str(VeiculoRepo.contar_dentro()))
            # ── Visitantes ────────────────────────────────────────────────────
            self._card_visit.set_valor(str(VisitanteRepo.contar_dentro()))
        except Exception as e: print(f"[ERRO _atualizar_contadores] {e}")

    def _carregar_dashboard(self):
        self._atualizar_contadores()
        try:
            from app.core.database import get_session
            from app.models.trabalhador import Trabalhador
            from app.models.treinamento import Treinamento
            session = get_session(); hoje = date.today()
            aso30  = session.query(Trabalhador).filter(Trabalhador.ativo == True, Trabalhador.aso_validade >= hoje, Trabalhador.aso_validade <= hoje + timedelta(days=30)).count()
            nr30   = session.query(Treinamento).filter(Treinamento.nr_nome == NR01_NOME_BANCO, Treinamento.data_validade >= hoje, Treinamento.data_validade <= hoje + timedelta(days=30)).count()
            session.close()
            if aso30 > 0: self._adicionar_alerta(f"{aso30} colaborador(es) com ASO vencendo em 30 dias", "warning")
            if nr30  > 0: self._adicionar_alerta(f"{nr30} colaborador(es) com integração (NR-01) vencendo em 30 dias", "warning")
        except Exception as e: print(f"[ERRO _carregar_dashboard] {e}")

    # ── Relógio ───────────────────────────────────────────────────────────────

    def _iniciar_relogio(self):
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(1000); self._tick()

    def _tick(self):
        self._lbl_rel.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))