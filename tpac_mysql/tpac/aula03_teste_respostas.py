from controllers.usuario_controller import UsuarioController

controller = UsuarioController()

casos = [
    ("Rafa03", "direto"),
    ("Al", "direto"),
    ("Rafa03", "direto"),
    ("Bia", "rapido"),
]

for nome, estilo in casos:
    try:
        usuario = controller.criar_perfil(nome, estilo)
        print("SUCESSO:", usuario.nome)
    except ValueError as erro:
        print(f"{type(erro).__name__}:", erro)