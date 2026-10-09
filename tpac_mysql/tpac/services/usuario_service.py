from repositories.usuario_repository import UsuarioRepository
from core.interpretador import interpretar_mensagem as interpretar_texto
from core.ia_service import obter_resposta_ia
from core.erros import CredenciaisInvalidas, DadosInvalidos, NaoEncontrado
from core.conversa import ConversaTarefa, ESPERANDO_PRAZO, ESPERANDO_PRIORIDADE
from core.seguranca import gerar_hash_senha, verificar_senha
from services.tarefa_service import TarefaService


class UsuarioService:
    def __init__(self, repository=None):
        self.repository = repository or UsuarioRepository()

    def _validar_perfil(self, nome, estilo_instrucao):
        nome = nome.strip()

        if not nome:
            raise DadosInvalidos("O nome não pode ficar vazio.")

        if len(nome) < 3:
            raise DadosInvalidos("O nome precisa ter pelo menos 3 caracteres.")

        if estilo_instrucao not in {"direto", "detalhado"}:
            raise DadosInvalidos(
                "O estilo deve ser 'direto' ou 'detalhado'."
            )

        return nome

    def listar_usuarios(self):
        return self.repository.listar()

    def buscar_usuario(self, usuario_id):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        return usuario

    def criar_usuario(self, nome, estilo_instrucao, senha=None):
        nome = self._validar_perfil(nome, estilo_instrucao)

        existente = self.repository.buscar_por_nome(nome)
        if existente is not None:
            raise DadosInvalidos("Já existe um perfil com esse nome.")

        senha_hash = None

        if senha is not None:
            if len(senha) < 6:
                raise DadosInvalidos("A senha precisa ter pelo menos 6 caracteres.")

            senha_hash = gerar_hash_senha(senha)

        return self.repository.criar(nome, estilo_instrucao, senha_hash)

    def atualizar_usuario(self, usuario_id, nome, estilo_instrucao):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        nome = self._validar_perfil(nome, estilo_instrucao)

        existente = self.repository.buscar_por_nome(nome)
        if existente is not None and existente.id != usuario_id:
            raise DadosInvalidos("Já existe um perfil com esse nome.")

        return self.repository.atualizar(usuario_id, nome, estilo_instrucao)

    def excluir_usuario(self, usuario_id):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        self.repository.excluir(usuario_id)

    def autenticar(self, nome, senha):
        usuario = self.repository.buscar_por_nome(nome.strip())

        if (
            usuario is None
            or not usuario.senha_hash
            or not verificar_senha(senha, usuario.senha_hash)
        ):
            raise CredenciaisInvalidas("Nome ou senha inválidos.")

        return usuario

    def interpretar_mensagem(self, usuario_id, texto):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        return interpretar_texto(texto)

    def responder_pergunta(self, usuario_id, pergunta):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        return obter_resposta_ia(pergunta, usuario.estilo_instrucao)

    def avancar_conversa(self, usuario_id, mensagem, estado=None, tarefa_parcial=None):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        estados_validos = {None, ESPERANDO_PRAZO, ESPERANDO_PRIORIDADE}

        if estado not in estados_validos:
            raise DadosInvalidos("Estado de conversa inválido.")

        tarefa_service = TarefaService()

        def persistir_na_api(categoria, titulo, prioridade, prazo):
            tarefa_service.criar_tarefa(
                usuario_id, categoria, titulo,
                prioridade=prioridade, prazo=prazo
            )

        conversa = ConversaTarefa(
            estado=estado,
            tarefa=tarefa_parcial,
            persistir_tarefa=persistir_na_api
        )

        if estado is None:
            interpretacao = interpretar_texto(mensagem)

            if interpretacao["intencao"] != "registrar_tarefa":
                raise DadosInvalidos(
                    "Não consegui identificar uma tarefa nessa mensagem."
                )

            respostas = conversa.iniciar(
                interpretacao["titulo"], interpretacao["categoria"]
            )
        else:
            respostas = conversa.processar(mensagem)

        return {
            "respostas": respostas,
            "estado": conversa.estado,
            "tarefa": conversa.tarefa
        }