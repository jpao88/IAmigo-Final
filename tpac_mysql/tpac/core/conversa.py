from datetime import datetime


ESPERANDO_MENSAGEM = "esperando_mensagem"
ESPERANDO_PRAZO = "esperando_prazo"
ESPERANDO_PRIORIDADE = "esperando_prioridade"


class ConversaTarefa:
    def __init__(
        self,
        persistir_tarefa,
        estado: str = None,
        tarefa: dict = None
    ):
        self.persistir_tarefa = persistir_tarefa
        self.estado = estado or ESPERANDO_MENSAGEM
        self.tarefa = tarefa or {}

    def esta_cadastrando(self) -> bool:
        return self.estado != ESPERANDO_MENSAGEM

    def iniciar(self, titulo: str, categoria: str) -> list:
        self.tarefa = {
            "titulo": titulo,
            "categoria": categoria,
            "prazo": None,
            "prioridade": "media"
        }

        self.estado = ESPERANDO_PRAZO

        return [
            "📝 Entendi o que você precisa fazer!",
            f"📌 {titulo}",
            "Qual é o prazo?",
            "Digite no formato DD/MM/AAAA ou escreva 'sem prazo'."
        ]

    def processar(self, mensagem: str) -> list:
        mensagem = mensagem.strip()

        if mensagem.lower() == "cancelar":
            self.reiniciar()

            return [
                "Cadastro cancelado.",
                "Pode me contar outra coisa quando quiser."
            ]

        if self.estado == ESPERANDO_PRAZO:
            return self._receber_prazo(mensagem)

        if self.estado == ESPERANDO_PRIORIDADE:
            return self._receber_prioridade(mensagem)

        return [
            "Não há nenhuma tarefa sendo cadastrada."
        ]

    def _receber_prazo(self, mensagem: str) -> list:
        respostas_sem_prazo = [
            "sem prazo",
            "não tem prazo",
            "nao tem prazo",
            "pular"
        ]

        if mensagem.lower() in respostas_sem_prazo:
            self.tarefa["prazo"] = None
        else:
            try:
                data = datetime.strptime(
                    mensagem,
                    "%d/%m/%Y"
                )

                self.tarefa["prazo"] = data.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                return [
                    "Não consegui entender essa data.",
                    "Use o formato DD/MM/AAAA.",
                    "Exemplo: 15/08/2026",
                    "Ou escreva 'sem prazo'."
                ]

        self.estado = ESPERANDO_PRIORIDADE

        return [
            "Certo! Agora escolha a prioridade:",
            "1. Baixa",
            "2. Média",
            "3. Alta"
        ]

    def _receber_prioridade(self, mensagem: str) -> list:
        prioridades = {
            "1": "baixa",
            "baixa": "baixa",
            "2": "media",
            "media": "media",
            "média": "media",
            "3": "alta",
            "alta": "alta"
        }

        escolha = mensagem.lower()

        if escolha not in prioridades:
            return [
                "Escolha uma prioridade válida:",
                "1. Baixa",
                "2. Média",
                "3. Alta"
            ]

        self.tarefa["prioridade"] = prioridades[escolha]

        titulo = self.tarefa["titulo"]
        categoria = self.tarefa["categoria"]
        prazo = self.tarefa["prazo"]
        prioridade = self.tarefa["prioridade"]

        self.persistir_tarefa(categoria, titulo, prioridade, prazo)

        categoria_exibida = {
            "tarefas_diarias": "Rotina diária",
            "tarefas_educacionais": "Estudos e educação"
        }.get(categoria, "Tarefas")

        prazo_exibido = self._formatar_prazo(prazo)
        prioridade_exibida = prioridade.capitalize()

        self.reiniciar()

        return [
            "✅ Tudo certo! Sua tarefa foi salva.",
            f"📌 Tarefa: {titulo}",
            f"📁 Categoria: {categoria_exibida}",
            f"📅 Prazo: {prazo_exibido}",
            f"🔥 Prioridade: {prioridade_exibida}"
        ]

    def _formatar_prazo(self, prazo) -> str:
        if not prazo:
            return "Sem prazo"

        return datetime.strptime(
            prazo,
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

    def reiniciar(self):
        self.estado = ESPERANDO_MENSAGEM
        self.tarefa = {}