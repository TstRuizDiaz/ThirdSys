"""
app/core/settings.py
─────────────────────────────────────────────────────────────────────────────
Configurações persistidas do ThirdSys + escolha da pasta-base de documentos.

Na 1ª execução, garantir_pasta_base() abre o explorador de arquivos para o
usuário escolher onde tudo será guardado. Nas próximas execuções, o caminho
salvo em data/config.json é reaproveitado automaticamente.

Estrutura criada:
    <pasta escolhida>\ThirdSys\Empresas\<EMPRESA>\Colaboradores\<COLABORADOR>\Documentos\
    <pasta escolhida>\ThirdSys\Empresas\<EMPRESA>\Colaboradores\<COLABORADOR>\Treinamentos\
─────────────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
import json
import os
import sys

from PySide6.QtWidgets import QFileDialog, QMessageBox

# ─────────────────────────────────────────────────────────────────────────────
# Caminhos fixos da aplicação (não dependem de escolha do usuário)
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "thirdsys.db"

BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

APP_NAME = "ThirdSys"
APP_VERSION = "1.0.0"
DIAS_AVISO_VENCIMENTO = 30

# ─────────────────────────────────────────────────────────────────────────────
# Configurações persistidas (data/config.json)
# ─────────────────────────────────────────────────────────────────────────────
CONFIG_PATH = DATA_DIR / "config.json"

_CONFIG_PADRAO = {
    "empresa_nome": "Lactalis Brasil",
    "empresa_cidade": "Goiânia",
    "empresa_cnpj": "14.049.467/0093-59",
    # Só recebe valor real depois que o usuário escolhe a pasta
    # (ver garantir_pasta_base). Enquanto for None, é sinal de 1ª execução.
    "docs_base_dir": None,
}


def carregar_config() -> dict:
    if not CONFIG_PATH.exists():
        return _CONFIG_PADRAO.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)
    # Garante que chaves novas do padrão existam mesmo em configs antigas
    for k, v in _CONFIG_PADRAO.items():
        dados.setdefault(k, v)
    return dados


def salvar_config(dados: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# 1ª EXECUÇÃO — escolher a pasta-base no explorador de arquivos
# ─────────────────────────────────────────────────────────────────────────────
def garantir_pasta_base(parent=None) -> Path:
    """
    Garante que existe uma pasta-base configurada para guardar os documentos.

    - Se já existe um caminho salvo em config.json E a pasta ainda existe
      no disco -> retorna direto, sem perguntar nada.
    - Se é a 1ª execução (ou a pasta salva foi apagada / pendrive removido
      / HD trocado) -> abre QFileDialog.getExistingDirectory pedindo para
      o usuário escolher onde guardar tudo.
    - Se o usuário cancelar o diálogo -> encerra o app (sem pasta-base o
      sistema não tem onde salvar nada).

    Deve ser chamada UMA ÚNICA VEZ, logo após criar o QApplication, antes
    de abrir splash/login/main window.
    """
    cfg = carregar_config()
    salvo = cfg.get("docs_base_dir")

    if salvo and Path(salvo).exists():
        return Path(salvo)

    QMessageBox.information(
        parent,
        "Configuração inicial — ThirdSys",
        "Bem-vindo ao ThirdSys!\n\n"
        "Selecione a pasta onde o sistema vai guardar os documentos de "
        "empresas e colaboradores (Ordem de Serviço, Ficha de Registro, "
        "Ficha de EPI, CNH, RG, Diploma e Treinamentos Normativos).\n\n"
        "Essa escolha só será pedida uma vez."
    )

    escolhida = QFileDialog.getExistingDirectory(
        parent, "Selecione a pasta para guardar os documentos do ThirdSys"
    )

    if not escolhida:
        QMessageBox.critical(
            parent,
            "Pasta obrigatória",
            "É necessário escolher uma pasta para continuar.\n"
            "O ThirdSys será encerrado."
        )
        sys.exit(1)

    base = Path(escolhida) / "ThirdSys" / "Empresas"
    base.mkdir(parents=True, exist_ok=True)

    cfg["docs_base_dir"] = str(base)
    salvar_config(cfg)
    return base


def trocar_pasta_base(parent=None) -> Path | None:
    """
    Permite trocar a pasta-base depois (ex: botão em uma tela de
    Configurações). Retorna None se o usuário cancelar.
    """
    nova = QFileDialog.getExistingDirectory(
        parent, "Selecione a nova pasta para o ThirdSys"
    )
    if not nova:
        return None

    base = Path(nova) / "ThirdSys" / "Empresas"
    base.mkdir(parents=True, exist_ok=True)

    cfg = carregar_config()
    cfg["docs_base_dir"] = str(base)
    salvar_config(cfg)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# Sanitização de nomes (empresa, colaborador, arquivo)
# ─────────────────────────────────────────────────────────────────────────────
def _sanitizar(nome: str) -> str:
    """Remove/substitui caracteres inválidos em nomes de pasta no Windows."""
    invalidos = r'\/:*?"<>|'
    for ch in invalidos:
        nome = nome.replace(ch, "_")
    return nome.strip(". ")  # Windows não permite ponto ou espaço no fim


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de caminho de documentos
# ─────────────────────────────────────────────────────────────────────────────
def docs_empresa(razao_social: str) -> Path:
    """
    Retorna (e cria) a pasta da empresa:
        <docs_base_dir>/<Razao Social>/
    """
    cfg = carregar_config()
    base_dir = cfg.get("docs_base_dir")
    if not base_dir:
        # Salvaguarda: se algo chamar isso antes de garantir_pasta_base
        # ter rodado, força a escolha agora.
        base_dir = str(garantir_pasta_base())
    base = Path(base_dir) / _sanitizar(razao_social)
    base.mkdir(parents=True, exist_ok=True)
    return base


def docs_colaborador(razao_social: str, nome_colab: str) -> Path:
    """
    Retorna (e cria) a pasta RAIZ do colaborador:
        <docs_base_dir>/<Razao Social>/Colaboradores/<Nome Colaborador>/
    """
    pasta = docs_empresa(razao_social) / "Colaboradores" / _sanitizar(nome_colab)
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def docs_documentos(razao_social: str, nome_colab: str) -> Path:
    """
    Retorna (e cria) a pasta de Documentos do colaborador:
        .../Colaboradores/<Nome>/Documentos/

    Usar para: Ordem de Serviço (NR1), Ficha de Registro, Ficha de EPI,
    CNH, RG, Diploma.
    """
    pasta = docs_colaborador(razao_social, nome_colab) / "Documentos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def docs_treinamentos(razao_social: str, nome_colab: str) -> Path:
    """
    Retorna (e cria) a pasta de Treinamentos do colaborador:
        .../Colaboradores/<Nome>/Treinamentos/

    Usar para: Treinamentos Normativos (NRs).
    """
    pasta = docs_colaborador(razao_social, nome_colab) / "Treinamentos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def abrir_pasta(caminho: Path):
    """Abre a pasta no explorador de arquivos do sistema operacional."""
    import subprocess

    caminho = Path(caminho)
    caminho.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(caminho)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(caminho)])
    else:
        subprocess.Popen(["xdg-open", str(caminho)])


# ─────────────────────────────────────────────────────────────────────────────
# DOCS_DIR — mantido por compatibilidade, mas NÃO calculado no import.
#
# IMPORTANTE: removi o cálculo automático que existia no arquivo original
# (`DOCS_DIR = Path(carregar_config()["docs_base_dir"])` executado direto
# no corpo do módulo). Isso rodava no momento do `import app.core.settings`,
# ou seja, ANTES de existir um QApplication — e antes da pasta-base ter
# sido escolhida na 1ª execução. Se algum código antigo usa DOCS_DIR como
# constante, troque para chamar docs_empresa(...)/docs_colaborador(...)
# no momento do uso.
# ─────────────────────────────────────────────────────────────────────────────
DOCS_DIR = None