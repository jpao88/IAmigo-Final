from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from api.dependencias import exigir_dono_ou_admin
from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

controller = UsuarioController()


class NovoUsuario(BaseModel):
    nome: str
    estilo_instrucao: str = "direto"
    senha: Optional[str] = None


class AtualizarUsuario(BaseModel):
    nome: str
    estilo_instrucao: str


class Mensagem(BaseModel):
    texto: str


class Pergunta(BaseModel):
    texto: str


class MensagemConversa(BaseModel):
    mensagem: str
    estado: Optional[str] = None
    tarefa_parcial: Optional[dict] = None


def usuario_publico(usuario):
    """Lista branca dos campos que podem sair da API. O senha_hash nunca sai."""
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "estilo_instrucao": usuario.estilo_instrucao,
        "criado_em": usuario.criado_em
    }


@router.get("")
def listar_usuarios():
    return {
        "dados": [
            usuario_publico(usuario)
            for usuario in controller.listar_perfis()
        ]
    }


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: int):
    return {
        "dados": usuario_publico(controller.buscar_perfil(usuario_id))
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: NovoUsuario):
    usuario = controller.criar_perfil(
        dados.nome,
        dados.estilo_instrucao,
        dados.senha
    )

    return {
        "dados": usuario_publico(usuario)
    }


@router.put("/{usuario_id}")
def atualizar_usuario(
    usuario_id: int,
    dados: AtualizarUsuario,
    usuario_autenticado=Depends(exigir_dono_ou_admin)
):
    usuario = controller.atualizar_perfil(
        usuario_id, dados.nome, dados.estilo_instrucao
    )

    return {
        "dados": usuario_publico(usuario)
    }


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_usuario(
    usuario_id: int,
    usuario_autenticado=Depends(exigir_dono_ou_admin)
):
    controller.excluir_perfil(usuario_id)


@router.post("/{usuario_id}/mensagens")
def interpretar_mensagem(
    usuario_id: int,
    dados: Mensagem,
    usuario_autenticado=Depends(exigir_dono_ou_admin)
):
    return {
        "dados": controller.interpretar_mensagem(usuario_id, dados.texto)
    }


@router.post("/{usuario_id}/perguntas")
def responder_pergunta(
    usuario_id: int,
    dados: Pergunta,
    usuario_autenticado=Depends(exigir_dono_ou_admin)
):
    return {
        "dados": controller.responder_pergunta(usuario_id, dados.texto)
    }


@router.post("/{usuario_id}/conversa")
def avancar_conversa(
    usuario_id: int,
    dados: MensagemConversa,
    usuario_autenticado=Depends(exigir_dono_ou_admin)
):
    resultado = controller.avancar_conversa(
        usuario_id, dados.mensagem, dados.estado, dados.tarefa_parcial
    )

    return {
        "dados": resultado
    }
