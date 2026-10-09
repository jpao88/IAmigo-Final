from fastapi import APIRouter
from pydantic import BaseModel

from api.rotas_usuarios import usuario_publico
from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"]
)

controller = UsuarioController()


class Login(BaseModel):
    nome: str
    senha: str


@router.post("/login")
def login(dados: Login):
    sessao = controller.autenticar(dados.nome, dados.senha)

    return {
        "dados": {
            "access_token": sessao["access_token"],
            "token_type": sessao["token_type"],
            "expires_in": sessao["expires_in"],
            "usuario": usuario_publico(sessao["usuario"])
        }
    }