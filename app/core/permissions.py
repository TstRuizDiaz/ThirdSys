"""
app/core/permissions.py
─────────────────────────────────────────────────────────────────────────────
Regra de negócio (definida pelo cliente):

  - admin    → acesso total: cria/edita/exclui setores, empresas,
               colaboradores, treinamentos, documentos, e gerencia outros
               usuários. Vê todo o menu.
  - tecnico  → "usuário normal": vê praticamente todo o menu do admin
               (Dashboard, Empresas, Trabalhadores, Vencimentos,
               Relatórios) mas NÃO pode editar/excluir setores, nem
               criar/editar/excluir empresa ou colaborador, nem gerenciar
               usuários — só consulta + libera/bloqueia.
  - operador → "portaria": menu mais restrito — só Dashboard, Empresas,
               Trabalhadores e Portaria (sem Vencimentos/Relatórios).
               Mesmas restrições de edição do tecnico.

Ou seja, existem duas dimensões independentes:
  1) QUAIS TELAS aparecem no menu (varia por perfil — ver menu_permitido).
  2) SE PODE EDITAR/CRIAR/EXCLUIR dentro das telas que vê (só admin).
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from typing import Union

UsuarioLike = Union[dict, object, None]

# Itens de menu por perfil. "portaria" não entra aqui porque fica numa
# seção separada ("SISTEMA") e é sempre visível pra todo mundo.
_MENU_POR_PERFIL = {
    "admin":    {"dashboard", "empresas", "trabalhadores", "vencimentos", "relatorios"},
    "tecnico":  {"dashboard", "empresas", "trabalhadores", "vencimentos", "relatorios"},
    "operador": {"dashboard", "empresas", "trabalhadores"},
}


def obter_perfil(usuario: UsuarioLike) -> str:
    if usuario is None:
        return "admin"  # sem usuário logado (ex: modo dev) = sem restrição
    if isinstance(usuario, dict):
        return usuario.get("perfil", "operador")
    return getattr(usuario, "perfil", "operador")


def eh_admin(usuario: UsuarioLike) -> bool:
    return obter_perfil(usuario) == "admin"


def role_label(usuario: UsuarioLike) -> str:
    """Compatibilidade com SetoresPage, que já esperava
    'ADMINISTRATIVO' / 'TECNICO' como string de papel."""
    return "ADMINISTRATIVO" if eh_admin(usuario) else "TECNICO"


def menu_permitido(usuario: UsuarioLike) -> set[str]:
    """Conjunto de chaves de menu (dashboard/empresas/trabalhadores/
    vencimentos/relatorios) que esse usuário pode ver/acessar."""
    perfil = obter_perfil(usuario)
    return set(_MENU_POR_PERFIL.get(perfil, _MENU_POR_PERFIL["operador"]))


def pode_acessar(usuario: UsuarioLike, chave: str) -> bool:
    return chave in menu_permitido(usuario)
