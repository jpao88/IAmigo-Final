"""Erros de domínio do sistema.

Os services lançam estes erros e cada camada decide como mostrá-los:
a API transforma em status HTTP (api_app.py) e o console imprime a mensagem.

Herdam de ValueError/RuntimeError para que o código que já captura
essas exceções (console, testes) continue funcionando.
"""


class NaoEncontrado(ValueError):
    """O registro pedido não existe ou não pertence ao usuário."""


class DadosInvalidos(ValueError):
    """Os dados recebidos não respeitam uma regra de negócio."""


class CredenciaisInvalidas(ValueError):
    """Nome ou senha não conferem."""


class FalhaIA(RuntimeError):
    """O serviço de IA não está configurado ou não respondeu."""
