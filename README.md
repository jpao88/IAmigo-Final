# IAmigo

Assistente para organizar tarefas e estudos, pensado para pessoas com
TPAC (Transtorno do Processamento Auditivo Central) e dificuldades de foco.
Usa frases curtas, passos pequenos e uma IA (Gemini) que quebra cada tarefa
em micro-ações.

O sistema pode ser usado de duas formas, que compartilham o mesmo banco
e as mesmas regras de negócio:

- **Console** (`python main.py`): menus no terminal.
- **API + front web** (`uvicorn api_app:app`): FastAPI com login JWT e
  páginas HTML em `frontend/`.

## Como executar

Todo o código fica em [`tpac_mysql/tpac/`](tpac_mysql/tpac/). O passo a passo
(banco MySQL, `.env`, console, API e testes) está no
[README do projeto](tpac_mysql/tpac/README.md).

## Arquitetura

```
frontend/ (HTML + JS) ──HTTP + JWT──► api/ (rotas FastAPI, schemas, permissões)
                                          │
ui/ (console) ────────────┐               ▼
                          │         controllers/
                          ▼               │
                       services/  ◄───────┘   regras de negócio, erros de domínio
                          │
                    repositories/              consultas (SQLAlchemy)
                          │
                       models/  ──────────►  MySQL (database.sql)

core/    → IA (Gemini), interpretador de mensagens, conversa, segurança (senhas e JWT)
config/  → configurações lidas do .env e conexão com o banco
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [Contrato da API](tpac_mysql/tpac/docs/contrato_api_iamigo.md) | Todas as rotas, formatos, permissões e códigos de status |
| [Contrato para o front](tpac_mysql/tpac/docs/contrato_front_iamigo.md) | Fluxo login → painel e como o front trata cada status |
| [Autorização (aula 09)](tpac_mysql/tpac/docs/aula09_autorizacao.md) | Perfis e matriz de permissões |

## Tecnologias

Python, FastAPI, SQLAlchemy, MySQL, PyJWT, Google Gemini, HTML/CSS/JavaScript.
