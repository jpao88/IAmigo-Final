from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status
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
    return {
        "dados": controller.listar_tarefas(usuario_id)
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_tarefa(usuario_id: int, dados: NovaTarefa):
    tarefa = controller.criar_tarefa(
        usuario_id,
        dados.tipo,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    return {
        "dados": tarefa
    }


@router.patch("/{tarefa_id}")
def alternar_status(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.alternar_status(usuario_id, tarefa_id)
    }


@router.get("/{tarefa_id}")
def buscar_tarefa(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.buscar_tarefa(usuario_id, tarefa_id)
    }


@router.put("/{tarefa_id}")
def atualizar_tarefa(usuario_id: int, tarefa_id: int, dados: NovaTarefa):
    tarefa = controller.atualizar_tarefa(
        usuario_id,
        tarefa_id,
        dados.tipo,
        dados.titulo,
        dados.descricao,
        dados.prioridade,
        dados.prazo
    )

    return {
        "dados": tarefa
    }


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_tarefa(usuario_id: int, tarefa_id: int):
    controller.excluir_tarefa(usuario_id, tarefa_id)


@router.get("/{tarefa_id}/passos")
def listar_passos(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.listar_passos(usuario_id, tarefa_id)
    }


@router.post("/{tarefa_id}/passos/gerar", status_code=status.HTTP_201_CREATED)
def gerar_passos(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.gerar_passos(usuario_id, tarefa_id)
    }


@router.patch("/{tarefa_id}/passos/{passo_id}")
def alternar_status_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    return {
        "dados": controller.alternar_status_passo(usuario_id, tarefa_id, passo_id)
    }


@router.delete("/{tarefa_id}/passos/{passo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    controller.excluir_passo(usuario_id, tarefa_id, passo_id)
