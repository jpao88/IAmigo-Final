import random
import time
import os
from services.usuario_service import UsuarioService
from ui.menus import criar_usuario_menu, painel_principal_menu
from ui.utils import exibir_cabecalho


def exibir_logo():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║   ██╗ █████╗ ███╗   ███╗██╗ ██████╗  ██████╗     ║
    ║   ██║██╔══██╗████╗ ████║██║██╔════╝ ██╔═══██╗    ║
    ║   ██║███████║██╔████╔██║██║██║  ███╗██║   ██║    ║
    ║   ██║██╔══██║██║╚██╔╝██║██║██║   ██║██║   ██║    ║
    ║   ██║██║  ██║██║ ╚═╝ ██║██║╚██████╔╝╚██████╔╝    ║
    ║   ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═════╝  ╚═════╝     ║
    ║                                                  ║
    ║   Seu amigo para organizar tarefas e estudos     ║
    ║                                                  ║
    ║       Desenvolvido para auxiliar pessoas         ║
    ║            com dificuldades de foco              ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)


def exibir_frase():
    frases = [
        "😊 Que bom te ver por aqui!",
        "🚀 Vamos organizar o dia juntos?",
        "📚 Um passo de cada vez.",
        "✨ Pequenos avanços também são conquistas.",
        "🎯 Vamos focar no que importa hoje.",
        "🌟 Você está indo muito bem!",
        "🤖 Estou pronto para ajudar.",
        "💡 Toda tarefa começa com um primeiro passo.",
        "📝 Vamos colocar as ideias em ordem?",
        "😄 Pronto para mais um dia produtivo?"
    ]

    print(f"\n{random.choice(frases)}\n")
    
import time

def tela_carregamento():
        etapas = [
            "█░░░░░░░░░░ 10%",
            "███░░░░░░░░ 30%",
            "██████░░░░░ 60%",
            "███████████ 100%"
        ]

        print(""" 
        ╔══════════════════════════════════════╗
        ║          INICIANDO IAMIGO            ║
        ╚══════════════════════════════════════╝
        """)

        for etapa in etapas:
            print(etapa)
            time.sleep(0.4)

        print("\n✅ Sistema pronto!\n")
        time.sleep(1)

def executar_sistema():
    usuario_service = UsuarioService()

    while True:
        usuarios = usuario_service.listar_usuarios()

        exibir_logo()
        print("Olá! 👋 Eu sou o IAmigo.")
        exibir_frase()

        print("""
        ╔════════════════════════════════════╗
        ║         O QUE VAMOS FAZER?         ║
        ╠════════════════════════════════════╣
        ║ 1. Continuar com meu perfil        ║
        ║ 2. Criar um novo perfil            ║
        ║ 3. Encerrar por agora              ║
        ╚════════════════════════════════════╝
        """)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            if not usuarios:
                input("\nNenhum perfil salvo. Crie um primeiro! (Enter)")
                continue

            print("        ╔════════════════════════════════════╗")
            print("        ║         PERFIS ENCONTRADOS         ║")
            print("        ╠════════════════════════════════════╣")

            for u in usuarios:
                # 32 espaços para o nome + 4 espaços do ' 👤 ' = 36 espaços internos (igual ao menu)
                nome_formatado = u.nome.ljust(32)
                print(f"        ║ 👤 {nome_formatado}║")

            print("        ╚════════════════════════════════════╝")
            nome = input("\n✨ Qual perfil deseja acessar? ").strip()
                
            usuario = next((u for u in usuarios if u.nome == nome), None)

            if usuario is not None:
                painel_principal_menu(usuario)
            else:
                input("\n🤖🔍 Opa! Não encontrei esse perfil na minha lista. Pressione ENTER para tentar novamente.")
        
        elif opcao == "2":
            criar_usuario_menu()
            
        elif opcao == "3":
            print("\nAté logo 👋, não esqueça de realizar suas tarefas diárias📝!")
            break  # Agora o break está alinhado corretamente dentro da opção 3


if __name__ == "__main__":
    tela_carregamento()
    executar_sistema()