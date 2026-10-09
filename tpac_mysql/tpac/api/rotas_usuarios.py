from typing import List

from fastapi import APIRouter, Depends, status

from api.dependencias import exigir_admin, exigir_dono, exigir_dono_ou_admin
from api.schemas import (
    AtualizarUsuario,
    Interpretacao,
    Mensagem,
    MensagemConversa,
    NovoUsuario,
    PassoConversa,
    Pergunta,
    Resposta,
    UsuarioPublico,
)
from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

controller = UsuarioController()


@router.get(
    "",
    response_model=Resposta[List[UsuarioPublico]],
    dependencies=[Depends(exigir_admin)]
)
def listar_usuarios():
    return {
        "dados": controller.listar_perfis()
    }


@router.get(
    "/{usuario_id}",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def buscar_usuario(usuario_id: int):
    return {
        "dados": controller.buscar_perfil(usuario_id)
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Resposta[UsuarioPublico])
def criar_usuario(dados: NovoUsuario):
    usuario = controller.criar_perfil(
        dados.nome,
        dados.estilo_instrucao,
        dados.senha
    )

    return {
        "dados": usuario
    }


@router.put(
    "/{usuario_id}",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def atualizar_usuario(usuario_id: int, dados: AtualizarUsuario):
    usuario = controller.atualizar_perfil(
        usuario_id, dados.nome, dados.estilo_instrucao
    )

    return {
        "dados": usuario
    }


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def excluir_usuario(usuario_id: int):
    controller.excluir_perfil(usuario_id)


@router.post(
    "/{usuario_id}/mensagens",
    response_model=Resposta[Interpretacao],
    dependencies=[Depends(exigir_dono)]
)
def interpretar_mensagem(usuario_id: int, dados: Mensagem):
    return {
        "dados": controller.interpretar_mensagem(usuario_id, dados.texto)
    }


@router.post(
    "/{usuario_id}/perguntas",
    response_model=Resposta[List[str]],
    dependencies=[Depends(exigir_dono)]
)
def responder_pergunta(usuario_id: int, dados: Pergunta):
    return {
        "dados": controller.responder_pergunta(usuario_id, dados.texto)
    }


@router.post(
    "/{usuario_id}/conversa",
    response_model=Resposta[PassoConversa],
    dependencies=[Depends(exigir_dono)]
)
def avancar_conversa(usuario_id: int, dados: MensagemConversa):
    resultado = controller.avancar_conversa(
        usuario_id, dados.mensagem, dados.estado, dados.tarefa_parcial
    )

    return {
        "dados": resultado
    }
