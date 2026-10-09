"""Formatos de entrada e saída da API.

Os tipos Literal fazem o Swagger mostrar os valores aceitos e o FastAPI
recusar valores inválidos (422) antes de chegar ao service.

Os modelos de saída são a lista branca do que pode sair da API:
campos que não estão aqui (como senha_hash e papel) nunca são enviados.
"""
from datetime import date, datetime
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

TipoTarefa = Literal["tarefas_diarias", "tarefas_educacionais"]
Prioridade = Literal["baixa", "media", "alta"]
EstiloInstrucao = Literal["direto", "detalhado"]
EstadoConversa = Literal["esperando_prazo", "esperando_prioridade"]

T = TypeVar("T")


class Resposta(BaseModel, Generic[T]):
    dados: T


# ---------- Entrada ----------

class Login(BaseModel):
    nome: str
    senha: str


class NovoUsuario(BaseModel):
    nome: str = Field(max_length=100)
    estilo_instrucao: EstiloInstrucao = "direto"
    senha: Optional[str] = None


class AtualizarUsuario(BaseModel):
    nome: str = Field(max_length=100)
    estilo_instrucao: EstiloInstrucao


class NovaTarefa(BaseModel):
    tipo: TipoTarefa
    titulo: str = Field(max_length=200)
    descricao: Optional[str] = None
    prioridade: Prioridade = "media"
    prazo: Optional[date] = None


class Mensagem(BaseModel):
    texto: str


class Pergunta(BaseModel):
    texto: str


class MensagemConversa(BaseModel):
    mensagem: str
    estado: Optional[EstadoConversa] = None
    tarefa_parcial: Optional[dict] = None


# ---------- Saída ----------

class SaidaORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UsuarioPublico(SaidaORM):
    id: int
    nome: str
    estilo_instrucao: EstiloInstrucao
    criado_em: Optional[datetime] = None


class TarefaSaida(SaidaORM):
    id: int
    usuario_id: int
    tipo: TipoTarefa
    titulo: str
    descricao: Optional[str] = None
    prioridade: Prioridade
    prazo: Optional[date] = None
    concluida: bool
    criado_em: Optional[datetime] = None


class PassoSaida(SaidaORM):
    id: int
    tarefa_id: int
    texto: str
    concluido: bool
    ordem: int


class Sessao(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    usuario: UsuarioPublico


class Interpretacao(BaseModel):
    intencao: Literal["registrar_tarefa", "pergunta"]
    titulo: Optional[str] = None
    categoria: Optional[TipoTarefa] = None


class PassoConversa(BaseModel):
    respostas: List[str]
    estado: str
    tarefa: dict
