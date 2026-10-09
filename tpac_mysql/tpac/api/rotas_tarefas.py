from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.dependencias import exigir_dono_ou_admin
from controllers.tarefa_controller import TarefaController

router = APIRouter(
    prefix="/usuarios/{usuario_id}/tarefas",
    tags=["tarefas"],
    dependencies=[Depends(exigir_dono_ou_admin)]
)

controller = TarefaController()


class NovaTarefa(BaseModel):
    tipo: str
    titulo: str
    descricao: Optional[str] = None
    prioridade: str = "media"
    prazo: Optional[date] = None


@router.get("")
def listar_tarefas(usuario_id: int):
    resposta = controller.listar_tarefas(usuario_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_tarefa(usuario_id: int, dados: NovaTarefa):
    resposta = controller.criar_tarefa(
        usuario_id,
        dados.tipo,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    if not resposta["sucesso"]:
        status_code = 404 if resposta["mensagem"] == "Usuário não encontrado." else 422
        raise HTTPException(
            status_code=status_code,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.patch("/{tarefa_id}")
def alternar_status(usuario_id: int, tarefa_id: int):
    resposta = controller.alternar_status(usuario_id, tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }

@router.get("/{tarefa_id}")
def buscar_tarefa(usuario_id: int, tarefa_id: int):
    resposta = controller.buscar_tarefa(usuario_id, tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.put("/{tarefa_id}")
def atualizar_tarefa(usuario_id: int, tarefa_id: int, dados: NovaTarefa):
    resposta = controller.atualizar_tarefa(
        usuario_id,
        tarefa_id,
        dados.tipo,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    if not resposta["sucesso"]:
        nao_encontrado = resposta["mensagem"] in {
            "Usuário não encontrado.",
            "Tarefa não encontrada."
        }
        raise HTTPException(
            status_code=404 if nao_encontrado else 422,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }

@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_tarefa(usuario_id: int, tarefa_id: int):
    resposta = controller.excluir_tarefa(usuario_id, tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )


@router.get("/{tarefa_id}/passos")
def listar_passos(usuario_id: int, tarefa_id: int):
    resposta = controller.listar_passos(usuario_id, tarefa_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.post("/{tarefa_id}/passos/gerar", status_code=status.HTTP_201_CREATED)
def gerar_passos(usuario_id: int, tarefa_id: int):
    resposta = controller.gerar_passos(usuario_id, tarefa_id)

    if not resposta["sucesso"]:
        status_code = 503 if resposta["tipo"] == "FALHA_IA" else 404
        raise HTTPException(
            status_code=status_code,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.patch("/{tarefa_id}/passos/{passo_id}")
def alternar_status_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    resposta = controller.alternar_status_passo(usuario_id, tarefa_id, passo_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )

    return {
        "dados": resposta["dados"]
    }


@router.delete("/{tarefa_id}/passos/{passo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    resposta = controller.excluir_passo(usuario_id, tarefa_id, passo_id)

    if not resposta["sucesso"]:
        raise HTTPException(
            status_code=404,
            detail=resposta["mensagem"]
        )