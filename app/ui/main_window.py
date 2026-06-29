from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QStackedWidget, QLabel
)
from PySide6.QtCore import Qt
from app.ui.components.sidebar import Sidebar
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.empresas.setores_page import SetoresPage, EmpresasPage
from app.ui.pages.empresas.ficha_empresa_page import FichaEmpresaPage
from app.ui.pages.trabalhadores.colaboradores_list_page import ColaboradoresListPage


class MainWindow(QMainWindow):

    def __init__(self, usuario, token=None, cnpj=None):
        super().__init__()
        self.usuario = usuario
        self.token   = token
        self.cnpj    = cnpj
        self._empresas_page  = None
        self._ficha_page     = None
        self._colab_page     = None
        self._portaria_page  = None
        self._colab_origem   = "lista"

        from app.core.permissions import eh_admin, role_label, menu_permitido
        self._eh_admin   = eh_admin(usuario)
        self._role_label = role_label(usuario)
        self._menu        = menu_permitido(usuario)

        self.setWindowTitle("ThirdSys — Gestão de Terceiros")
        self.setMinimumSize(1280, 720)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(usuario=self.usuario)
        self.sidebar.nav_item_clicked.connect(self.navegar_para)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #F2F5F8;")
        layout.addWidget(self.stack)

        self.dashboard = DashboardPage()
        self.dashboard.navegar.connect(self.navegar_para)

        self.setores = SetoresPage(user_role=self._role_label)
        self.setores.navegar.connect(self.navegar_para)
        self.setores.voltar.connect(lambda: self.navegar_para("dashboard"))

        self._colabs_list = ColaboradoresListPage(somente_leitura=not self._eh_admin)

        self.pages = {
            "dashboard":     self.dashboard,
            "setores":       self.setores,
            "trabalhadores": self._colabs_list,
        }

        # Vencimentos e Relatórios: admin e tecnico têm acesso, operador
        # não (regra do cliente — ver app/core/permissions.py).
        if "vencimentos" in self._menu:
            from app.ui.pages.relatorios_page import RelatoriosPage
            self._relatorios = RelatoriosPage()

            from app.ui.pages.vencimentos_page import VencimentosPage
            self._vencimentos = VencimentosPage()

            self.pages["relatorios"]  = self._relatorios
            self.pages["vencimentos"] = self._vencimentos
        else:
            self._relatorios  = None
            self._vencimentos = None

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.setCentralWidget(central)
        # Landing page: dashboard pra todo mundo agora (admin, tecnico e
        # operador têm Dashboard no menu).
        self.navegar_para("dashboard" if "dashboard" in self._menu else "trabalhadores")

    def navegar_para(self, chave: str):
        print(f"DEBUG navegar_para: {chave}")

        # Defesa extra: mesmo que os botões estejam escondidos pra
        # quem não deveria ver, qualquer rota que crie/edite/exclua é
        # bloqueada aqui também (só admin) — e Vencimentos/Relatórios
        # ficam restritos a quem tem essas chaves no menu permitido
        # (admin e tecnico; operador não). Não depende só da UI ter
        # escondido o botão certo em algum lugar.
        _ROTAS_ADMIN_PREFIXO = ("nova_empresa", "novo_colaborador:")
        if not self._eh_admin and any(chave.startswith(p) for p in _ROTAS_ADMIN_PREFIXO):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Acesso restrito",
                "Essa ação está disponível apenas para administradores."
            )
            return

        if chave in ("vencimentos", "relatorios") and chave not in self._menu:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Acesso restrito",
                "Essa tela não está disponível para o seu perfil."
            )
            return

        if chave == "empresas":
            chave = "setores"

        if chave == "trabalhadores":
            self._colabs_list.carregar_dados()
            self.stack.setCurrentWidget(self.pages["trabalhadores"])
            self.sidebar.set_ativo("trabalhadores")

        elif chave == "relatorios":
            self.stack.setCurrentWidget(self.pages["relatorios"])
            self.sidebar.set_ativo("relatorios")
            self._relatorios.carregar_dados()

        elif chave == "vencimentos":
            self.stack.setCurrentWidget(self.pages["vencimentos"])
            self.sidebar.set_ativo("vencimentos")
            self._vencimentos.carregar_dados()

        elif chave in self.pages:
            self.stack.setCurrentWidget(self.pages[chave])
            self.sidebar.set_ativo(chave if chave != "setores" else "empresas")
            # CORREÇÃO: ao voltar pro dashboard pela sidebar, força refresh
            # imediato em vez de confiar só no timer de 5s — cobre o caso
            # de o usuário ter feito alguma alteração em outra tela
            # (ex: cadastro de empresa) e voltar direto pro Painel.
            if chave == "dashboard":
                self.dashboard.carregar_dados()

        elif chave.startswith("setor:"):
            setor = chave.replace("setor:", "")
            self._abrir_empresas_setor(setor)

        elif chave == "nova_empresa":
            setor_nome = getattr(self, "_setor_atual", "")
            self._abrir_ficha_empresa(None, setor_nome)

        elif chave.startswith("empresa_detalhe:"):
            partes     = chave.replace("empresa_detalhe:", "").split("|")
            empresa_id = int(partes[0]) if partes[0].isdigit() else None
            setor_nome = partes[1] if len(partes) > 1 else ""
            self._abrir_ficha_empresa(empresa_id, setor_nome)

        elif chave.startswith("novo_colaborador:"):
            empresa_id = int(chave.replace("novo_colaborador:", ""))
            self._abrir_form_colaborador(None, empresa_id, origem="ficha")

        elif chave.startswith("colaborador:"):
            partes     = chave.replace("colaborador:", "").split("|")
            colab_id   = int(partes[0])
            empresa_id = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
            origem = "ficha" if (
                self._ficha_page is not None
                and self.stack.currentWidget() == self._ficha_page
            ) else "lista"
            self._abrir_form_colaborador(colab_id, empresa_id, origem=origem)

        elif chave == "portaria":
            self._abrir_portaria()

    def _abrir_portaria(self):
        from app.ui.pages.portaria_page import PortariaPage

        # Verifica se a janela existe E se o objeto Qt por trás dela ainda
        # está vivo. Se a janela foi fechada/destruída, acessar isVisible()
        # nela gera RuntimeError ("wrapped C/C++ object has been deleted") —
        # por isso o try/except: se acontecer, simplesmente cria de novo.
        portaria_valida = False
        if self._portaria_page is not None:
            try:
                portaria_valida = self._portaria_page.isVisible()
            except RuntimeError:
                self._portaria_page = None

        if portaria_valida:
            self._portaria_page.raise_()
            self._portaria_page.activateWindow()
        else:
            self._portaria_page = PortariaPage(parent=self)
            # CORREÇÃO: a Portaria abre como janela separada (não fica
            # dentro do QStackedWidget), então o showEvent() do Dashboard
            # nunca dispara ao fechar essa janela — o Dashboard fica só
            # "atrás" dela, nunca foi escondido de fato. Sem essa conexão,
            # os dados (pessoas na unidade, vencimentos etc.) só
            # atualizavam no timer de 5s do Dashboard.
            # QDialog.finished dispara tanto no accept/reject quanto ao
            # fechar pelo X (closeEvent padrão chama reject()).
            self._portaria_page.finished.connect(lambda _: self.dashboard.carregar_dados())
            self._portaria_page.show()

        self.sidebar.set_ativo("portaria")

    def _abrir_empresas_setor(self, setor: str):
        self._setor_atual = setor

        from app.core.database import get_session
        from app.models.empresa import Empresa

        session = get_session()
        empresas = session.query(Empresa).filter_by(setor=setor).all()
        session.close()

        if self._empresas_page:
            self.stack.removeWidget(self._empresas_page)
            self._empresas_page.deleteLater()

        self._empresas_page = EmpresasPage(setor, empresas, user_role=self._role_label)
        self._empresas_page.voltar.connect(lambda: self.navegar_para("setores"))
        self._empresas_page.navegar.connect(self.navegar_para)
        self.stack.addWidget(self._empresas_page)
        self.stack.setCurrentWidget(self._empresas_page)

    def _abrir_ficha_empresa(self, empresa_id, setor_nome: str):
        from app.core.database import get_session
        from app.models.empresa import Empresa

        empresa = None
        if empresa_id:
            session = get_session()
            empresa = session.get(Empresa, empresa_id)
            session.close()

        if self._ficha_page:
            self.stack.removeWidget(self._ficha_page)
            self._ficha_page.deleteLater()

        self._ficha_page = FichaEmpresaPage(
            empresa=empresa, setor_nome=setor_nome, somente_leitura=not self._eh_admin
        )
        self._ficha_page.voltar.connect(
            lambda: self._abrir_empresas_setor(setor_nome)
        )
        self.stack.addWidget(self._ficha_page)
        self.stack.setCurrentWidget(self._ficha_page)

    def _abrir_form_colaborador(self, colaborador_id, empresa_id, origem: str = "lista"):
        from app.core.database import get_session
        from app.models.trabalhador import Trabalhador
        from app.models.empresa import Empresa
        from app.ui.pages.trabalhadores.trabalhador_form_page import TrabalhadorFormPage

        session = get_session()
        empresa     = session.get(Empresa,     empresa_id)     if empresa_id     else None
        colaborador = session.get(Trabalhador,  colaborador_id) if colaborador_id else None
        session.close()

        if self._colab_page:
            self.stack.removeWidget(self._colab_page)
            self._colab_page.deleteLater()

        self._colab_page = TrabalhadorFormPage(
            empresa=empresa, trabalhador=colaborador, somente_leitura=not self._eh_admin
        )
        self._colab_origem = origem

        def _voltar():
            if self._colab_page:
                self.stack.removeWidget(self._colab_page)
                self._colab_page.deleteLater()
                self._colab_page = None

            if self._colab_origem == "ficha" and self._ficha_page:
                self.stack.setCurrentWidget(self._ficha_page)
                if hasattr(self._ficha_page, "_carregar_colaboradores"):
                    self._ficha_page._carregar_colaboradores()
            else:
                self._colabs_list.carregar_dados()
                self.stack.setCurrentWidget(self.pages["trabalhadores"])
                self.sidebar.set_ativo("trabalhadores")

        self._colab_page.voltar.connect(_voltar)
        self.stack.addWidget(self._colab_page)
        self.stack.setCurrentWidget(self._colab_page)

    def _placeholder(self, texto: str) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        label  = QLabel(texto)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-size: 20px; color: #8AA5BC; background: transparent;"
        )
        layout.addWidget(label)
        return widget