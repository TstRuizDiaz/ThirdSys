def __init__(self, empresa=None, trabalhador=None, parent=None):
        super().__init__(parent)
        self.empresa = empresa
        self.trabalhador = trabalhador
        self._arquivos = {}
        self.setWindowTitle("Cadastro de Colaborador")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("background-color: #F0F4F8;")
        self._setup_ui()
        if trabalhador:
            self._preencher_dados()