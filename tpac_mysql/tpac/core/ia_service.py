import logging
import os
from google import genai
from google.genai import types

from core.erros import FalhaIA

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client() if API_KEY else None

MODELO_GEMINI = "gemini-2.5-flash"


def _obter_instrucao_tpac(estilo_usuario: str) -> str:
    """Retorna a persona e as diretrizes de formatação da IA para o contexto de TPAC."""

    base_prompt = (
        "Você é um assistente especializado em acessibilidade para pessoas com TPAC "
        "(Transtorno do Processamento Auditivo Central).\n"
        "Seu papel é reduzir a carga cognitiva, cansaço mental e ambiguidade.\n"
        "Diretrizes obrigatórias:\n"
        "- Nunca use parágrafos longos, blocos densos de texto ou jargões complexos.\n"
        "- Use frases curtas, ordem direta (Sujeito + Verbo + Objeto).\n"
        "- Divida as respostas visualmente usando tópicos/bullets claros.\n"
    )

    if estilo_usuario == "direto":
        base_prompt += (
            "- Seja extremamente conciso. Vá direto ao ponto, "
            "use o mínimo de palavras possível."
        )
    else:
        base_prompt += (
            "- Se precisar explicar um conceito, faça-o em etapas "
            "lógicas e sequenciais simples."
        )

    return base_prompt


def _linhas_da_resposta(response) -> list:
    return [
        linha.strip()
        for linha in (response.text or "").split("\n")
        if linha.strip()
    ]


def obter_resposta_ia(pergunta: str, estilo_usuario: str) -> list:
    """Conecta ao Gemini para responder dúvidas gerais de estudos ou organização."""

    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada. Configure sua chave de API.")

    system_instruction = _obter_instrucao_tpac(estilo_usuario)

    try:
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=pergunta,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            ),
        )
    except Exception as erro:
        logger.exception("Falha ao consultar o Gemini")
        raise FalhaIA("Não foi possível falar com a IA agora. Tente novamente.") from erro

    linhas = _linhas_da_resposta(response)

    if not linhas:
        raise FalhaIA("A IA não retornou uma resposta.")

    return linhas


def gerar_passos_tarefa(titulo_tarefa: str) -> list:
    """Usa o Gemini para quebrar uma tarefa macro em micro-ações sequenciais."""

    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada. Configure sua chave de API.")

    prompt = (
        f"Quebre a seguinte tarefa em exatamente 3 ou 4 passos sequenciais, "
        f"curtos e fáceis de focar: '{titulo_tarefa}'. "
        f"Escreva apenas os passos, um por linha, sem introduções ou numeração manual."
    )

    system_instruction = (
        "Você é um especialista em produtividade para neurodivergentes. "
        "Crie checklists limpos, com verbos de ação claros e livres de poluição textual."
    )

    try:
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
    except Exception as erro:
        logger.exception("Falha ao gerar passos no Gemini")
        raise FalhaIA("Não foi possível gerar os passos agora. Tente novamente.") from erro

    passos = [
        linha.lstrip("0123456789.-* ")
        for linha in _linhas_da_resposta(response)
    ]
    passos = [passo for passo in passos if passo]

    if not passos:
        raise FalhaIA("A IA não retornou nenhum passo.")

    return passos
