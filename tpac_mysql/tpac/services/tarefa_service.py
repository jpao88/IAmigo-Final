from repositories.tarefa_repository import TarefaRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.passo_repository import PassoRepository
from core.ia_service import gerar_passos_tarefa


class TarefaService:
    def __init__(self, tarefa_repository=None, usuario_repository=None, passo_repository=None):
        self.tarefa_repository = tarefa_repository or TarefaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.passo_repository = passo_repository or PassoRepository()

    def listar_tarefas(self, usuario_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        return self.tarefa_repository.listar_por_usuario(usuario_id)

    def criar_tarefa(self, usuario_id, tipo, titulo, descricao=None, prioridade="media", prazo=None):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        titulo = titulo.strip()

        if not titulo:
            raise ValueError("O título não pode ficar vazio.")

        if tipo not in {"tarefas_diarias", "tarefas_educacionais"}:
            raise ValueError(
                "O tipo deve ser 'tarefas_diarias' ou 'tarefas_educacionais'."
            )

        if prioridade not in {"baixa", "media", "alta"}:
            raise ValueError(
                "A prioridade deve ser 'baixa', 'media' ou 'alta'."
            )

        return self.tarefa_repository.criar(
            usuario_id, tipo, titulo, descricao, prioridade, prazo
        )

    def alternar_status(self, usuario_id, tarefa_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")

        if tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        return self.tarefa_repository.alternar_concluida(tarefa_id)

    def listar_passos(self, usuario_id, tarefa_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")

        if tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        return self.passo_repository.listar_por_tarefa(tarefa_id)

    def gerar_passos(self, usuario_id, tarefa_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")

        if tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        textos = gerar_passos_tarefa(tarefa.titulo)

        falha_ia = (
            not textos
            or (
                len(textos) == 1
                and (
                    textos[0].startswith("Configure")
                    or textos[0].startswith("Não foi possível gerar os passos")
                    or textos[0].startswith("Erro")
                )
            )
        )

        if falha_ia:
            mensagem = textos[0] if textos else "Não foi possível gerar os passos."
            raise RuntimeError(mensagem)

        return self.passo_repository.criar_varios(tarefa_id, textos)

    def adicionar_passo(self, usuario_id, tarefa_id, texto):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        texto = texto.strip()

        if not texto:
            raise ValueError("O texto do passo não pode ficar vazio.")

        return self.passo_repository.criar(tarefa_id, texto)

    def alternar_status_passo(self, usuario_id, tarefa_id, passo_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")

        if tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        passo = self.passo_repository.buscar_por_id(passo_id)

        if passo is None:
            raise ValueError("Passo não encontrado.")

        if passo.tarefa_id != tarefa_id:
            raise ValueError("Passo não encontrado.")

        return self.passo_repository.alternar_concluido(passo_id)

    def excluir_passo(self, usuario_id, tarefa_id, passo_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise ValueError("Tarefa não encontrada.")

        if tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        passo = self.passo_repository.buscar_por_id(passo_id)

        if passo is None:
            raise ValueError("Passo não encontrado.")

        if passo.tarefa_id != tarefa_id:
            raise ValueError("Passo não encontrado.")

        self.passo_repository.excluir(passo_id)
    
    def _obter_tarefa_do_usuario(self, usuario_id, tarefa_id):
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise ValueError("Usuário não encontrado.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None or tarefa.usuario_id != usuario_id:
            raise ValueError("Tarefa não encontrada.")

        return tarefa

    def buscar_tarefa(self, usuario_id, tarefa_id):
        return self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

    def _validar_dados_tarefa(self, tipo, titulo, prioridade):
        titulo = titulo.strip()

        if not titulo:
            raise ValueError("O título não pode ficar vazio.")

        if tipo not in {"tarefas_diarias", "tarefas_educacionais"}:
            raise ValueError(
                "O tipo deve ser 'tarefas_diarias' ou 'tarefas_educacionais'."
            )

        if prioridade not in {"baixa", "media", "alta"}:
            raise ValueError(
                "A prioridade deve ser 'baixa', 'media' ou 'alta'."
            )

        return titulo

    def atualizar_tarefa(self, usuario_id, tarefa_id, tipo, titulo, descricao=None, prioridade="media", prazo=None):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        titulo = self._validar_dados_tarefa(tipo, titulo, prioridade)

        return self.tarefa_repository.atualizar(
            tarefa_id, tipo, titulo, descricao, prioridade, prazo
        )

    def excluir_tarefa(self, usuario_id, tarefa_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        self.tarefa_repository.excluir(tarefa_id)