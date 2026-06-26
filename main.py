import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtCore import Qt

from app.core.settings import garantir_pasta_base
from app.core.session_manager import carregar_sessao, salvar_sessao
from app.ui.splash_screen import SplashScreen
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        icon_path = resource_path("assets/icons/logo_t.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # ── Pasta-base de documentos ────────────────────────────────────────
        # Na 1ª execução, abre o explorador de arquivos para o usuário
        # escolher onde o ThirdSys vai guardar tudo (empresas, colaboradores,
        # documentos e treinamentos). Nas execuções seguintes é transparente.
        # Chamado ANTES de splash/login: se o usuário cancelar, o app encerra
        # limpo sem nem mostrar essas telas.
        garantir_pasta_base()

        palette = QPalette()
        palette.setColor(QPalette.Window,          QColor("#F0F4F8"))
        palette.setColor(QPalette.WindowText,      QColor("#1A2B4A"))
        palette.setColor(QPalette.Base,            QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase,   QColor("#F8FAFC"))
        palette.setColor(QPalette.Text,            QColor("#1A2B4A"))
        palette.setColor(QPalette.Button,          QColor("#2563EB"))
        palette.setColor(QPalette.ButtonText,      QColor("#FFFFFF"))
        palette.setColor(QPalette.Highlight,       QColor("#2563EB"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        app.setPalette(palette)

        qss_path = resource_path("app/ui/styles/stylesheet.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())

        _refs = {}

        def apos_splash():
            try:
                splash.hide()
                sessao = carregar_sessao()

                if sessao and sessao.get("token") and sessao.get("cnpj"):
                    _abrir_main(
                        usuario=sessao,
                        token=sessao["token"],
                        cnpj=sessao["cnpj"],
                    )
                else:
                    _abrir_login()

            except Exception as e:
                print(f"ERRO em apos_splash: {e}")
                import traceback
                traceback.print_exc()

        def _abrir_login():
            login = LoginWindow()
            _refs["login"] = login

            def on_aceito():
                usuario = login.usuario_logado  # dict
                token   = login.token
                cnpj    = login.cnpj_logado

                salvar_sessao(
                    usuario_id=usuario.get("id"),
                    email=usuario.get("email", ""),
                    token=token,
                    cnpj=cnpj,
                )
                login.hide()
                _abrir_main(usuario=usuario, token=token, cnpj=cnpj)

            def on_rejeitado():
                sys.exit(0)

            login.accepted.connect(on_aceito)
            login.rejected.connect(on_rejeitado)
            login.show()
            login.raise_()
            login.activateWindow()

        def _abrir_main(usuario, token, cnpj):
            window = MainWindow(usuario=usuario, token=token, cnpj=cnpj)
            _refs["main"] = window
            window.show()
            window.raise_()
            window.activateWindow()
            if "splash" in _refs:
                _refs["splash"].deleteLater()
                del _refs["splash"]

        splash = SplashScreen(on_finalizado=apos_splash)
        _refs["splash"] = splash
        splash.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()