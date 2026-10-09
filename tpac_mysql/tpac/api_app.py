import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.erros import CredenciaisInvalidas, DadosInvalidos, FalhaIA, NaoEncontrado

from api.rotas_usuarios import router as usuarios_router
from api.rotas_tarefas import router as tarefas_router
from api.rotas_auth import router as auth_router

load_dotenv()

ORIGENS_PADRAO = (
    "http://localhost:5500,"
    "http://127.0.0.1:5500,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)

origens_permitidas = [
    origem.strip()
    for origem in os.getenv("CORS_ORIGINS", ORIGENS_PADRAO).split(",")
    if origem.strip()
]

app = FastAPI(
    title="TPaC API",
    description="API criada na Aula 05",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

STATUS_POR_ERRO = {
    NaoEncontrado: 404,
    DadosInvalidos: 422,
    CredenciaisInvalidas: 401,
    FalhaIA: 503,
}


def _responder_erro(status_code):
    def handler(request: Request, erro: Exception):
        return JSONResponse(status_code=status_code, content={"detail": str(erro)})
    return handler


for classe_erro, status_code in STATUS_POR_ERRO.items():
    app.add_exception_handler(classe_erro, _responder_erro(status_code))


@app.exception_handler(Exception)
def falha_tecnica(request: Request, erro: Exception):
    # O uvicorn registra o traceback completo; o cliente recebe só uma mensagem genérica.
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível concluir a operação."}
    )


app.include_router(usuarios_router)
app.include_router(tarefas_router)
app.include_router(auth_router)


@app.get("/")
def inicio():
    return {
        "sistema": "TPaC",
        "api": "funcionando"
    }