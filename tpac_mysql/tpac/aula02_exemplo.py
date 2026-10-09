from controllers.usuario_controller import UsuarioController

controller = UsuarioController()

while True:
    print("\n=== EXEMPLO AULA 02 ===")
    print("1. Listar perfis")
    print("2. Criar perfil")
    print("3. Sair")

    opcao = input("Escolha: ").strip()

    if opcao == "1":
        print("\nPerfis:")
        for usuario in controller.listar_perfis():
            print("-", usuario.nome)

    elif opcao == "2":
        nome = input("Nome: ").strip()
        print("1. Direto")
        print("2. Detalhado")
        escolha = input("Estilo: ").strip()
        estilo = "detalhado" if escolha == "2" else "direto"
        try:
            usuario = controller.criar_perfil(nome, estilo)
            print(f"Perfil {usuario.nome} criado.")
        except ValueError as erro:
            print(erro)

    elif opcao == "3":
        break
