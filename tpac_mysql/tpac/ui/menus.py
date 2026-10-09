import random
from getpass import getpass

from ui.utils import exibir_cabecalho, exibir_barra_status, exibir_progresso
from services.usuario_service import UsuarioService
from services.tarefa_service import TarefaService

from core.interpretador import interpretar_mensagem
from core.conversa import ConversaTarefa

usuario_service = UsuarioService()
tarefa_service = TarefaService()


def criar_usuario_menu():
    exibir_cabecalho("BEM-VINDO(A)")
    nome = input("Como você gostaria de ser chamado(a)? ").strip()
    if not nome:
        input("\nNão consegui identificar seu nome. Tente novamente. (ENTER)")
        return

    if any(u.nome == nome for u in usuario_service.listar_usuarios()):
        input(f"\nJá encontrei um cadastro com o nome '{nome}'. Tente novamente para seguirmos! (ENTER)")
        return

    print("\nMe conta uma coisa:")
    print("Quando você precisa fazer algo, o que funciona melhor para você?")
    print("1. Instruções curtas e sem enrolação")
    print("2. Um guia mais detalhado, explicando cada etapa")
    pref = input("Opção: ").strip()
    estilo = "direto" if pref == "1" else "detalhado"

    print("\nSe quiser acessar também pelo site, crie uma senha (mínimo 6 caracteres).")
    senha = getpass("Senha (ENTER para pular): ")

    try:
        usuario_service.criar_usuario(nome, estilo, senha or None)
    except ValueError as erro:
        input(f"\n{erro} (ENTER)")
        return

    input(f"\nTudo certo, [{nome}]! Seu perfil foi criado. Pressione Enter para continuar.")

def gerenciar_tarefas_menu(usuario, tipo: str, titulo: str):
    while True:
        exibir_cabecalho(titulo)
        tarefas = [
            t for t in tarefa_service.listar_tarefas(usuario.id)
            if t.tipo == tipo
        ]
        exibir_progresso(tarefas)

        if not tarefas:
            print("""
            ╔════════════════════════════════════╗
            ║        🎉 TUDO EM DIA!             ║
            ╠════════════════════════════════════╣
            ║ Nenhuma tarefa pendente por aqui.  ║
            ╚════════════════════════════════════╝
            """)
        else:
            print("\n📋 SUAS ATIVIDADES:\n")

            for idx, t in enumerate(tarefas, 1):
                status = "✅" if t.concluida else "⏳"

                print(f"{idx}. {status} {t.titulo}")

                for p in tarefa_service.listar_passos(usuario.id, t.id):
                    print(f"    └─ 📌 {p.texto}")

                print()

        print("\n" + "-"*30)
        print("  ╔════════════════════════════════════════════════════════════════════╗")
        print("     ➊ 📝 Adicionar │  ➋ Abrir Tarefa │  ➌ 🤖 IA │  ➍ 🔙 Voltar      ")
        print("  ╚════════════════════════════════════════════════════════════════════╝")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            print("\n🤖 Certo! Vamos criar uma nova atividade.")
            t_nome = input("➜ O que você precisa fazer hoje? ").strip()
            if t_nome:
                try:
                    tarefa_service.criar_tarefa(usuario.id, tipo, t_nome)
                except ValueError as erro:
                    input(f"\n❌ {erro} Pressione ENTER...")
                    continue

                mensagens = [
                    "🌟 Excelente! Já anotei isso.",
                    "🚀 Um passo de cada vez!",
                    "📌 Atividade adicionada com sucesso.",
                    "💙 Pode deixar, está tudo anotado.",
                    "🎯 Agora ficou mais fácil lembrar."
                ]

                print(f"\n{random.choice(mensagens)}")
                print(f"📌 {t_nome}")

                input("\nPressione ENTER para continuar...")

        elif opcao == "2":
            if not tarefas:
                input(
                    "\nNenhuma tarefa disponível. "
                    "Pressione ENTER para continuar..."
                )
                continue

            try:
                indice = int(
                    input("\nQual tarefa deseja abrir? ")
                ) - 1

                if 0 <= indice < len(tarefas):
                    abrir_tarefa_menu(usuario, tarefas[indice].id)
                else:
                    input(
                        "\n❌ Tarefa não encontrada. "
                        "Pressione ENTER..."
                    )

            except ValueError:
                input(
                    "\n❌ Digite apenas um número. "
                    "Pressione ENTER..."
                )

        elif opcao == "3":
            if not tarefas:
                input(
                    "\nNenhuma tarefa disponível. "
                    "Pressione ENTER para continuar..."
                )
                continue

            try:
                indice = int(
                    input(
                        "\nQual tarefa deseja desmembrar com a IA? "
                    )
                ) - 1

                if 0 <= indice < len(tarefas):
                    print("\n🤖 Criando subtarefas...")

                    try:
                        passos = tarefa_service.gerar_passos(
                            usuario.id, tarefas[indice].id
                        )

                        print("\n✅ Subtarefas criadas pela IA!")

                        for numero, passo in enumerate(passos, 1):
                            print(f"{numero}. {passo.texto}")

                    except RuntimeError as erro:
                        print("\n❌ A IA não conseguiu criar os passos.")
                        print(erro)

                else:
                    print("\n❌ Tarefa não encontrada.")

            except ValueError:
                print("\n❌ Digite apenas um número.")

            input("\nPressione ENTER para continuar...")

        elif opcao == "4":
            break

        else:
            input(
                "\n❌ Opção inválida. "
                "Pressione ENTER para tentar novamente..."
            )

def painel_ia_menu(usuario):
    exibir_cabecalho("🤖 IAMIGO")

    print("""
    ╔════════════════════════════════════════════╗
    ║          CONVERSA COM O IAMIGO             ║
    ╠════════════════════════════════════════════╣
    ║ Conte o que precisa fazer ou tire dúvidas. ║
    ╚════════════════════════════════════════════╝
    """)

    print("Exemplos:")
    print("• Preciso fazer um trabalho de inglês.")
    print("• Preciso marcar uma consulta.")
    print("• O que é fotossíntese?")
    print("\nDigite 'cancelar' para cancelar um cadastro.")
    print("Digite 'sair' para retornar.\n")

    def persistir_tarefa(categoria, titulo, prioridade, prazo):
        tarefa_service.criar_tarefa(
            usuario.id, categoria, titulo,
            prioridade=prioridade, prazo=prazo
        )

    conversa_tarefa = ConversaTarefa(persistir_tarefa)

    while True:
        mensagem = input("Você: ").strip()

        if mensagem.lower() == "sair":
            conversa_tarefa.reiniciar()
            print("\n🤖 IAmigo: Até a próxima! 👋")
            break

        if not mensagem:
            continue

        if conversa_tarefa.esta_cadastrando():
            try:
                respostas = conversa_tarefa.processar(
                    mensagem
                )
            except ValueError as erro:
                conversa_tarefa.reiniciar()
                respostas = [f"❌ Não consegui salvar a tarefa: {erro}"]

        else:
            interpretacao = interpretar_mensagem(
                mensagem
            )

            if (
                interpretacao["intencao"]
                == "registrar_tarefa"
            ):
                respostas = conversa_tarefa.iniciar(
                    interpretacao["titulo"],
                    interpretacao["categoria"]
                )

            else:
                frases = [
                    "🤔 Estou pensando...",
                    "🧠 Analisando sua pergunta...",
                    "📚 Organizando a resposta...",
                    "💡 Tenho uma ideia!",
                    "🎯 Vamos simplificar isso..."
                ]

                print(f"\n{random.choice(frases)}")

                try:
                    respostas = usuario_service.responder_pergunta(
                        usuario.id,
                        mensagem
                    )
                except RuntimeError as erro:
                    respostas = [str(erro)]

        print("\n🤖 IAmigo:")

        for resposta in respostas:
            print(f"  {resposta}")

        print("\n" + "═" * 46 + "\n")

def painel_principal_menu(usuario):
    while True:
        exibir_cabecalho("PAINEL DO USUÁRIO:")
        exibir_barra_status(usuario.nome)

        print("""
        ╔════════════════════════════════════╗
        ║      COMO POSSO TE AJUDAR?         ║
        ╠════════════════════════════════════╣
        ║ 1. 📝 Organizar minhas tarefas     ║
        ║ 2. 📚 Planejar meus estudos        ║
        ║ 3. 🤖 Conversar com o IAmigo       ║
        ║ 4. 👋 Encerrar por agora           ║
        ╚════════════════════════════════════╝
        """)
        opcao = input("\nEscolha: ").strip()
        if opcao == "1":
            print("\n🤖 Vamos colocar suas tarefas em ordem!")
            input("\nPressione ENTER para continuar...")
            gerenciar_tarefas_menu(usuario, "tarefas_diarias", "ROTINA DIÁRIA")
        elif opcao == "2":
            print("\n🤖 Ótimo! Vamos focar nos estudos.")
            input("\nPressione ENTER para continuar...")
            gerenciar_tarefas_menu(usuario, "tarefas_educacionais", "ESTUDOS E EDUCAÇÃO")
        elif opcao == "3":
            print("\n🤖 Estou pronto para conversar com você!")
            input("\nPressione ENTER para continuar...")
            painel_ia_menu(usuario)
        elif opcao == "4":
            print("\n🤖 Foi muito bom conversar com você hoje.")
            print("👋 Até a próxima!")
            break

def abrir_tarefa_menu(usuario, tarefa_id):
    while True:
        tarefa = tarefa_service.buscar_tarefa(usuario.id, tarefa_id)
        passos = tarefa_service.listar_passos(usuario.id, tarefa_id)

        exibir_cabecalho("TAREFA")

        print(f"\n📁 {tarefa.titulo}\n")
        print("Subtarefas:\n")

        if not passos:
            print("Nenhuma subtarefa criada.")
        else:
            for indice, passo in enumerate(passos, 1):
                status = "☑" if passo.concluido else "☐"
                print(f"{indice}. {status} {passo.texto}")

        print("\n" + "-" * 35)
        print("1 - Nova subtarefa")
        print("2 - Marcar ou desmarcar")
        print("3 - Excluir subtarefa")
        print("4 - Voltar")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            texto = input("\nNome da subtarefa: ").strip()

            if texto:
                tarefa_service.adicionar_passo(usuario.id, tarefa_id, texto)

                print("\n✅ Subtarefa adicionada!")
                input("\nPressione ENTER para continuar...")

        elif opcao == "2":
            if not passos:
                input(
                    "\nNenhuma subtarefa disponível. "
                    "Pressione ENTER para continuar..."
                )
                continue

            try:
                indice_passo = int(
                    input("\nNúmero da subtarefa: ")
                ) - 1

                if 0 <= indice_passo < len(passos):
                    tarefa_service.alternar_status_passo(
                        usuario.id, tarefa_id, passos[indice_passo].id
                    )

                    print("\n✅ Status atualizado!")
                else:
                    print("\n❌ Subtarefa não encontrada.")

            except ValueError:
                print("\n❌ Digite apenas um número.")

            input("\nPressione ENTER para continuar...")

        elif opcao == "3":
            if not passos:
                input(
                    "\nNenhuma subtarefa disponível. "
                    "Pressione ENTER para continuar..."
                )
                continue

            try:
                indice_passo = int(
                    input("\nNúmero da subtarefa que deseja excluir: ")
                ) - 1

                if 0 <= indice_passo < len(passos):
                    tarefa_service.excluir_passo(
                        usuario.id, tarefa_id, passos[indice_passo].id
                    )

                    print("\n🗑️ Subtarefa excluída!")
                else:
                    print("\n❌ Subtarefa não encontrada.")

            except ValueError:
                print("\n❌ Digite apenas um número.")

            input("\nPressione ENTER para continuar...")

        elif opcao == "4":
            break

        else:
            input(
                "\n❌ Opção inválida. "
                "Pressione ENTER para tentar novamente..."
            )
