from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QScrollArea, QSizePolicy,
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
COR_SB_BG          = "#1C2B3A"
COR_SB_BORDA       = "#243447"
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


def _sep() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background-color: {COR_SEPARADOR}; border: none;")
    return f


# ── Card de uma atividade ─────────────────────────────────────────────────────

class CardAtividade(QFrame):
    """
    Exibe uma atividade com:
      • cabeçalho colorido com setor, horário de início e status
      • descrição
      • lista de participantes em chips
      • botão "Encerrar" (encerra a atividade — define data_fim)
    """
    encerrada = Signal(int)   # emite atividade_id

    def __init__(self, ativ: dict, parent=None):
        """
        ativ = {
            id, descricao, setor, data_inicio (datetime), encerrada (bool),
            participantes: [{"nome": str, "funcao": str}, ...]
        }
        """
        super().__init__(parent)
        self._ativ = ativ
        self._setup_ui()

    def _setup_ui(self):
        encerrada = self._ativ["encerrada"]

        # Cor do status
        cor_status_bg    = COR_VERDE_BG    if not encerrada else "#F4F7FA"
        cor_status_borda = COR_VERDE_BORDA if not encerrada else COR_CARD_BORDA
        cor_status_txt   = COR_VERDE_TEXTO if not encerrada else COR_SECAO_LABEL
        cor_borda_esq    = COR_VERDE_TEXTO if not encerrada else COR_SECAO_LABEL

        self.setStyleSheet(f"""
            QFrame#CardAtiv {{
                background: {COR_CARD_BG};
                border: 1px solid {COR_CARD_BORDA};
                border-left: 4px solid {cor_borda_esq};
                border-radius: 6px;
            }}
            QLabel {{ border: none; background: transparent; }}
            QWidget {{ border: none; }}
        """)
        self.setObjectName("CardAtiv")

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(16, 14, 16, 14)
        raiz.setSpacing(10)

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        header = QHBoxLayout(); header.setSpacing(10)

        # ícone setor
        ic_setor = QLabel()
        ic_setor.setPixmap(qta.icon("fa5s.industry", color=COR_SB_ACENTO).pixmap(14,14))
        ic_setor.setStyleSheet("background: transparent; border: none;")
        header.addWidget(ic_setor, alignment=Qt.AlignVCenter)

        # setor
        lbl_setor = QLabel(self._ativ["setor"] or "Setor não informado")
        lbl_setor.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COR_TITULO};")
        header.addWidget(lbl_setor, 1)

        # horário de início
        hora_str = ""
        if self._ativ["data_inicio"]:
            hora_str = self._ativ["data_inicio"].strftime("Início: %H:%M")
        lbl_hora = QLabel(hora_str)
        lbl_hora.setStyleSheet(f"font-size: 10px; color: {COR_SECAO_LABEL};")
        header.addWidget(lbl_hora, alignment=Qt.AlignVCenter)

        # badge status
        badge = QLabel("● Em andamento" if not encerrada else "● Encerrada")
        badge.setStyleSheet(f"""
            font-size: 10px; font-weight: bold; color: {cor_status_txt};
            background: {cor_status_bg}; border: 1px solid {cor_status_borda};
            border-radius: 10px; padding: 2px 8px;
        """)
        header.addWidget(badge, alignment=Qt.AlignVCenter)

        raiz.addLayout(header)
        raiz.addWidget(_sep())

        # ── Descrição ──────────────────────────────────────────────────────────
        lbl_desc_label = QLabel("ATIVIDADE")
        lbl_desc_label.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1.2px;")
        lbl_desc = QLabel(self._ativ["descricao"])
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"font-size: 12px; color: {COR_TEXTO_NORMAL};")
        raiz.addWidget(lbl_desc_label)
        raiz.addWidget(lbl_desc)

        # ── Participantes ──────────────────────────────────────────────────────
        participantes = self._ativ.get("participantes", [])
        if participantes:
            lbl_p = QLabel("PARTICIPANTES")
            lbl_p.setStyleSheet(
                f"font-size: 9px; font-weight: bold; color: {COR_SECAO_LABEL}; letter-spacing: 1.2px;")
            raiz.addWidget(lbl_p)

            chips_row = QHBoxLayout(); chips_row.setSpacing(6); chips_row.setContentsMargins(0,0,0,0)
            chips_row.setAlignment(Qt.AlignLeft)
            for p in participantes:
                chip = QFrame()
                chip.setStyleSheet(f"""
                    QFrame {{ background: {COR_AZUL_BG}; border: 1px solid {COR_AZUL_BORDA};
                              border-radius: 12px; }}
                    QLabel {{ border: none; background: transparent; color: {COR_AZUL_TEXTO}; }}
                """)
                cl = QHBoxLayout(chip); cl.setContentsMargins(8,3,8,3); cl.setSpacing(5)
                ic_u = QLabel()
                ic_u.setPixmap(qta.icon("fa5s.user", color=COR_AZUL_TEXTO).pixmap(10,10))
                ic_u.setStyleSheet("background: transparent; border: none;")
                lbl_pn = QLabel(p["nome"])
                lbl_pn.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COR_AZUL_TEXTO};")
                lbl_pf = QLabel(f"· {p['funcao']}")
                lbl_pf.setStyleSheet(f"font-size: 10px; color: {COR_AZUL_TEXTO};")
                cl.addWidget(ic_u); cl.addWidget(lbl_pn); cl.addWidget(lbl_pf)
                chips_row.addWidget(chip)
            chips_row.addStretch()

            chips_container = QWidget()
            chips_container.setStyleSheet("background: transparent; border: none;")
            chips_container.setLayout(chips_row)
            raiz.addWidget(chips_container)

        # ── Botão encerrar ─────────────────────────────────────────────────────
        if not encerrada:
            rodape = QHBoxLayout(); rodape.setContentsMargins(0,4,0,0)
            rodape.addStretch()
            btn_enc = QPushButton("  Encerrar atividade")
            btn_enc.setIcon(qta.icon("fa5s.check-double", color=COR_VERDE_TEXTO))
            btn_enc.setIconSize(QSize(12,12)); btn_enc.setFixedHeight(32)
            btn_enc.setCursor(Qt.PointingHandCursor)
            btn_enc.setStyleSheet(f"""
                QPushButton {{
                    background: {COR_VERDE_BG}; color: {COR_VERDE_TEXTO};
                    border: 1px solid {COR_VERDE_BORDA}; border-radius: 4px;
                    padding: 0 14px; font-size: 11px; font-weight: bold;
                }}
                QPushButton:hover {{ background: {COR_VERDE_BORDA}; }}
            """)
            btn_enc.clicked.connect(lambda: self.encerrada.emit(self._ativ["id"]))
            rodape.addWidget(btn_enc)
            raiz.addLayout(rodape)


# ── Janela principal ──────────────────────────────────────────────────────────

class JanelaAtividades(QDialog):
    """
    Lista todos os serviços em andamento no dia de hoje,
    agrupados por setor (empresa da turma principal).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serviços em Andamento")
        self.setWindowFlag(Qt.Window)
        self.setMinimumSize(780, 560)
        self.resize(860, 660)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COR_BG}; }}
            QLabel  {{ border: none; background: transparent; }}
            QWidget {{ border: none; }}
        """)
        self._setup_ui()
        self._carregar()

    # ── Estrutura ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(28,24,28,24); raiz.setSpacing(16)

        # Cabeçalho
        header = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon("fa5s.hard-hat", color=COR_SB_ACENTO).pixmap(22,22))
        ic.setStyleSheet("background: transparent; border: none;"); header.addWidget(ic)
        vl = QVBoxLayout(); vl.setSpacing(2)
        lbl_t = QLabel("Serviços em Andamento")
        lbl_t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COR_TITULO};")
        self._lbl_sub = QLabel("Carregando…")
        self._lbl_sub.setStyleSheet(f"font-size: 11px; color: {COR_SUBTITULO};")
        vl.addWidget(lbl_t); vl.addWidget(self._lbl_sub)
        header.addLayout(vl); header.addStretch()

        # Botão atualizar
        btn_ref = QPushButton()
        btn_ref.setIcon(qta.icon("fa5s.sync-alt", color=COR_SB_ACENTO))
        btn_ref.setIconSize(QSize(13,13)); btn_ref.setFixedSize(34,34)
        btn_ref.setCursor(Qt.PointingHandCursor); btn_ref.setToolTip("Atualizar")
        btn_ref.setStyleSheet(f"""
            QPushButton {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA}; border-radius: 4px; }}
            QPushButton:hover {{ background: #EBF0F6; }}
        """)
        btn_ref.clicked.connect(self._carregar); header.addWidget(btn_ref)

        btn_x = QPushButton("  Fechar")
        btn_x.setIcon(qta.icon("fa5s.times", color="white"))
        btn_x.setIconSize(QSize(11,11)); btn_x.setFixedHeight(34)
        btn_x.setCursor(Qt.PointingHandCursor)
        btn_x.setStyleSheet(f"""
            QPushButton {{ background: {COR_SUBTITULO}; color: white; border: none;
                           border-radius: 4px; padding: 0 16px; font-size: 12px; }}
            QPushButton:hover {{ background: {COR_TITULO}; }}
        """)
        btn_x.clicked.connect(self.close); header.addWidget(btn_x)
        raiz.addLayout(header)

        # Cards de resumo
        self._resumo_row = QHBoxLayout(); self._resumo_row.setSpacing(12)
        raiz.addLayout(self._resumo_row)

        raiz.addWidget(_sep())

        # Área de conteúdo com scroll
        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: {COR_BG}; width: 6px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: {COR_CARD_BORDA}; border-radius: 3px; }}
        """)
        self._conteudo = QWidget(); self._conteudo.setStyleSheet("background: transparent; border: none;")
        self._layout_conteudo = QVBoxLayout(self._conteudo)
        self._layout_conteudo.setContentsMargins(0,0,8,0); self._layout_conteudo.setSpacing(12)
        self._scroll.setWidget(self._conteudo)
        raiz.addWidget(self._scroll, 1)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def _carregar(self):
        """Busca todas as atividades do dia e monta os cards."""
        atividades = self._buscar_atividades()

        # Limpa resumo
        while self._resumo_row.count():
            item = self._resumo_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Limpa conteúdo
        while self._layout_conteudo.count():
            item = self._layout_conteudo.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        em_andamento = [a for a in atividades if not a["encerrada"]]
        encerradas   = [a for a in atividades if a["encerrada"]]

        # Cards de resumo
        self._card_resumo("fa5s.hard-hat",     COR_SB_ACENTO,    "Em andamento",  str(len(em_andamento)))
        self._card_resumo("fa5s.check-circle", COR_VERDE_TEXTO,  "Encerradas hoje", str(len(encerradas)))
        self._card_resumo("fa5s.users",        COR_AMARELO_TEXTO, "Participantes",
                          str(sum(len(a["participantes"]) for a in em_andamento)))

        self._lbl_sub.setText(
            f"{len(atividades)} atividade(s) registrada(s) hoje  •  "
            f"Atualizado: {datetime.now().strftime('%H:%M:%S')}"
        )

        if not atividades:
            lbl_v = QLabel("Nenhuma atividade registrada hoje")
            lbl_v.setAlignment(Qt.AlignCenter)
            lbl_v.setStyleSheet(f"font-size: 14px; color: {COR_SECAO_LABEL}; padding: 40px;")
            self._layout_conteudo.addWidget(lbl_v)
            self._layout_conteudo.addStretch()
            return

        # Agrupa por setor
        setores: dict[str, list] = {}
        for a in atividades:
            s = a["setor"] or "Setor não informado"
            setores.setdefault(s, []).append(a)

        # Em andamento primeiro, depois encerradas
        for setor, lista in sorted(setores.items()):
            lista_ordenada = sorted(lista, key=lambda x: (x["encerrada"], -(x["data_inicio"].timestamp() if x["data_inicio"] else 0)))
            self._bloco_setor(setor, lista_ordenada)

        self._layout_conteudo.addStretch()

    def _card_resumo(self, icone, cor, titulo, valor):
        frame = QFrame(); frame.setStyleSheet(f"""
            QFrame {{ background: {COR_CARD_BG}; border: 1px solid {COR_CARD_BORDA};
                      border-top: 3px solid {cor}; border-radius: 6px; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        fl = QVBoxLayout(frame); fl.setContentsMargins(14,10,14,10); fl.setSpacing(3)
        row = QHBoxLayout()
        ic = QLabel(); ic.setPixmap(qta.icon(icone, color=cor).pixmap(12,12))
        ic.setStyleSheet("border: none; background: transparent;")
        lt = QLabel(titulo); lt.setStyleSheet(f"font-size: 10px; color: {COR_SECAO_LABEL}; font-weight: bold;")
        row.addWidget(ic); row.addWidget(lt); row.addStretch()
        lv = QLabel(valor); lv.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {cor};")
        fl.addLayout(row); fl.addWidget(lv)
        self._resumo_row.addWidget(frame, 1)

    def _bloco_setor(self, setor: str, atividades: list):
        """Cria um bloco colapsável com o nome do setor e os cards."""
        # Label do setor
        lbl_setor = QLabel(f"  {setor.upper()}")
        lbl_setor.setStyleSheet(f"""
            font-size: 10px; font-weight: bold; color: {COR_SB_ACENTO};
            background: {COR_AZUL_BG}; border: 1px solid {COR_AZUL_BORDA};
            border-radius: 4px; padding: 4px 10px; letter-spacing: 1px;
        """)
        self._layout_conteudo.addWidget(lbl_setor)

        for ativ in atividades:
            card = CardAtividade(ativ)
            card.encerrada.connect(self._on_encerrar_atividade)
            self._layout_conteudo.addWidget(card)

    # ── Consulta banco ────────────────────────────────────────────────────────

    def _buscar_atividades(self) -> list[dict]:
        result = []
        try:
            from app.core.database import get_session
            from app.models.atividade import Atividade, AtividadeParticipante
            from app.models.trabalhador import Trabalhador

            hoje   = date.today()
            inicio = datetime.combine(hoje, datetime.min.time())
            session = get_session()

            ativs = (session.query(Atividade)
                     .filter(Atividade.data_inicio >= inicio)
                     .order_by(Atividade.data_inicio.desc())
                     .all())

            for a in ativs:
                participantes = []
                for p in a.participantes:
                    t = p.trabalhador
                    participantes.append({
                        "nome":   t.nome if t else "—",
                        "funcao": t.funcao or "—" if t else "—",
                    })
                result.append({
                    "id":           a.id,
                    "descricao":    a.descricao,
                    "setor":        a.setor or "—",
                    "data_inicio":  a.data_inicio,
                    "data_fim":     a.data_fim,
                    "encerrada":    a.encerrada,
                    "operador":     a.operador or "—",
                    "participantes": participantes,
                })
            session.close()
        except Exception as e:
            print(f"[JanelaAtividades] buscar: {e}")
        return result

    # ── Encerrar atividade ────────────────────────────────────────────────────

    def _on_encerrar_atividade(self, atividade_id: int):
        r = QMessageBox.question(
            self, "Encerrar atividade",
            "Deseja encerrar esta atividade?\nIsso indica que o grupo saiu da planta.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        )
        if r != QMessageBox.Yes: return
        try:
            from app.core.database import get_session
            from app.models.atividade import Atividade
            session = get_session()
            a = session.query(Atividade).filter_by(id=atividade_id).first()
            if a:
                a.encerrada = True
                a.data_fim  = datetime.now()
                session.commit()
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível encerrar:\n{e}")
            return
        self._carregar()   # recarrega a lista