from core.seguranca import gerar_token_acesso
from services.usuario_service import UsuarioService


class UsuarioController:
    """Repassa os pedidos da API para o service.

    Os erros sobem como exceções de core/erros.py e viram
    respostas HTTP nos handlers registrados em api_app.py.
    """

    def __init__(self, service=None):
        self.service = service or UsuarioService()

    def listar_perfis(self):
        return self.service.listar_usuarios()

    def buscar_perfil(self, usuario_id):
        return self.service.buscar_usuario(usuario_id)

    def criar_perfil(self, nome, estilo_instrucao, senha=None):
        return self.service.criar_usuario(nome, estilo_instrucao, senha)

    def atualizar_perfil(self, usuario_id, nome, estilo_instrucao):
        return self.service.atualizar_usuario(usuario_id, nome, estilo_instrucao)

    def excluir_perfil(self, usuario_id):
        self.service.excluir_usuario(usuario_id)

    def interpretar_mensagem(self, usuario_id, texto):
        return self.service.interpretar_mensagem(usuario_id, texto)

    def responder_pergunta(self, usuario_id, pergunta):
        return self.service.responder_pergunta(usuario_id, pergunta)

    def avancar_conversa(self, usuario_id, mensagem, estado=None, tarefa_parcial=None):
        return self.service.avancar_conversa(
            usuario_id, mensagem, estado, tarefa_parcial
        )

    def autenticar(self, nome, senha):
        usuario = self.service.autenticar(nome, senha)
        token, expira_em = gerar_token_acesso(usuario.id, usuario.nome)
        return {
            "usuario": usuario,
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expira_em
        }
